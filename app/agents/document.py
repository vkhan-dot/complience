import os
import json
import logging
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from app.models import Task, Prompt, Memory
from app.agents.knowledge import KnowledgeAgent
from app.agents.llm_helper import (
    call_gemini_with_retry,
    extract_clean_text,
    extract_clean_json
)

logger = logging.getLogger(__name__)

class DocumentAgent:
    """
    DocumentAgent coordinates the Impact Agent (business impact assessment), 
    Draft Agent (generating modification files), and Review Agent (verification and quality gates).
    """

    @classmethod
    def get_client(cls) -> genai.Client | None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize genai.Client in DocumentAgent: {e}")
            return None


    @classmethod
    def _normalize_departments(cls, raw_departments) -> list[dict]:
        """Ensures affected_departments is always a list of {department, reason} dicts."""
        if not raw_departments:
            return []
        if isinstance(raw_departments, dict):
            return [{"department": str(k), "reason": str(v)} for k, v in raw_departments.items()]
        
        normalized = []
        if isinstance(raw_departments, list):
            for item in raw_departments:
                if isinstance(item, dict):
                    dept = item.get("department") or item.get("name") or "Не указан"
                    reason = item.get("reason") or item.get("justification") or "Требуется актуализация процессов"
                    normalized.append({"department": str(dept), "reason": str(reason)})
                elif isinstance(item, str) and item.strip():
                    normalized.append({"department": item.strip(), "reason": "Затронуто изменениями законодательства"})
        return normalized

    @classmethod
    def _normalize_plan(cls, raw_plan) -> list[dict]:
        """Ensures implementation_plan is always a list of {step, deadline, owner} dicts."""
        if not raw_plan:
            return []
        normalized = []
        if isinstance(raw_plan, list):
            for item in raw_plan:
                if isinstance(item, dict):
                    normalized.append({
                        "step": str(item.get("step") or item.get("task") or "Этап внедрения"),
                        "deadline": str(item.get("deadline") or item.get("terms") or "В течение 14 дней"),
                        "owner": str(item.get("owner") or item.get("responsible") or "Департамент методологии")
                    })
                elif isinstance(item, str) and item.strip():
                    normalized.append({
                        "step": item.strip(),
                        "deadline": "В течение 14 дней",
                        "owner": "Департамент методологии"
                    })
        elif isinstance(raw_plan, str) and raw_plan.strip():
            normalized.append({
                "step": raw_plan.strip(),
                "deadline": "По графику",
                "owner": "Департамент методологии"
            })
        return normalized

    @classmethod
    def _normalize_checklist(cls, raw_checklist) -> list[dict]:
        """Ensures checklist is always a list of {item} dicts."""
        if not raw_checklist:
            return []
        normalized = []
        if isinstance(raw_checklist, list):
            for item in raw_checklist:
                if isinstance(item, dict):
                    text = item.get("item") or item.get("text") or item.get("check") or ""
                    if text:
                        normalized.append({"item": str(text)})
                elif isinstance(item, str) and item.strip():
                    clean = item.strip().lstrip("- [ ]").lstrip("* [ ]").strip()
                    if clean:
                        normalized.append({"item": clean})
        elif isinstance(raw_checklist, str) and raw_checklist.strip():
            for line in raw_checklist.splitlines():
                clean = line.strip().lstrip("- [ ]").lstrip("* [ ]").strip()
                if clean:
                    normalized.append({"item": clean})
        return normalized

    @classmethod
    def _normalize_review(cls, raw_review) -> dict:
        """Ensures review report matches standard schema with score, issues, recommendations, is_approved."""
        if not isinstance(raw_review, dict):
            return {
                "score": 50,
                "issues": ["Не удалось разобрать структурированный отчет ревью"],
                "recommendations": ["Проверить проект вручную"],
                "is_approved": False
            }
        score = raw_review.get("score")
        try:
            score = int(score) if score is not None else 50
        except (ValueError, TypeError):
            score = 50
        score = max(0, min(100, score))

        issues = raw_review.get("issues", [])
        if not isinstance(issues, list):
            issues = [str(issues)] if issues else []

        recommendations = raw_review.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = [str(recommendations)] if recommendations else []

        is_approved = raw_review.get("is_approved")
        if is_approved is None:
            is_approved = score >= 80

        return {
            "score": score,
            "issues": [str(i) for i in issues],
            "recommendations": [str(r) for r in recommendations],
            "is_approved": bool(is_approved)
        }

    @classmethod
    def generate_impact_and_drafts(cls, task_id: int, db: Session) -> dict:
        """
        Coordinates the whole draft generation pipeline:
        1. Query semantic memory for relevant internal policies.
        2. Impact Agent: Identify affected departments and severity.
        3. Draft Agent: Produce the document updates, board memos, and plans.
        4. Review Agent: Formulate compliance checks and validation reports.
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or not task.analysis_json:
            return {"status": "error", "message": "Task or analysis not found"}

        analysis = task.analysis_json
        
        # 1. Fetch relevant internal documents using KnowledgeAgent
        query_text = f"{analysis.get('what_changed', '')} {analysis.get('requirements', '')}"
        similar_docs = KnowledgeAgent.search_similar_docs(query_text, db, limit=3)
        
        related_docs_str = ""
        for i, (doc, sim) in enumerate(similar_docs):
            related_docs_str += f"\nДокумент #{i+1}: {doc.title} (Категория: {doc.category})\nСодержание:\n{doc.content_markdown[:1500]}\n---\n"

        # Load style and decision memories for Context-Aware Generation
        memories = db.query(Memory).filter(Memory.type.in_(["style", "decision"])).all()
        style_memories = [m for m in memories if m.type == "style"]
        decision_memories = [m for m in memories if m.type == "decision"]
        
        style_guidelines = "\n".join([m.content_text for m in style_memories]) if style_memories else (
            "- Использовать строгий деловой стиль.\n- Ссылаться на законодательные акты РК.\n"
            "- Вводные служебные записки адресовать Правлению от имени Департамента методологии."
        )
        
        past_mistakes = "\n".join([m.content_text for m in decision_memories]) if decision_memories else "Ошибок не зафиксировано."

        # Retrieve prompts from DB or use standard fallbacks
        draft_prompt_record = db.query(Prompt).filter(Prompt.key == "draft_prompt").first()
        draft_prompt_template = draft_prompt_record.content if draft_prompt_record else (
            "Вы — Ведущий методолог страховой компании Республики Казахстан. "
            "На основе анализа изменений в законодательстве РК и предоставленных внутренних документов компании, подготовьте проекты необходимых изменений.\n\n"
            "АНАЛИЗ ИЗМЕНЕНИЙ ЗАКОНА:\n{analysis_str}\n\n"
            "СВЯЗАННЫЕ ВНУТРЕННИЕ РЕГЛАМЕНТЫ КОМПАНИИ:\n{related_docs}\n\n"
            "СТИЛИСТИЧЕСКИЕ И КОРПОРАТИВНЫЕ ПРАВИЛА:\n{style_guidelines}\n\n"
            "ИСТОРИЯ ОШИБОК И ОТКЛОНЕННЫХ ПРОЕКТОВ (НЕ ПОВТОРЯТЬ ЭТИ ОШИБКИ!):\n{past_mistakes}\n\n"
            "Пожалуйста, сформируйте ответ строго в JSON формате с ключами:\n"
            "- affected_departments: список затронутых департаментов (например, Методология, Юристы, Продажи, IT, Андеррайтинг, Урегулирование) с кратким обоснованием для каждого.\n"
            "- rules_changes: проект конкретных правок во внутренние правила (предыдущая редакция -> новая редакция).\n"
            "- memo: служебная записка о необходимости изменений.\n"
            "- board_letter: сопроводительное письмо для Правления компании.\n"
            "- board_directors_letter: письмо для Совета директоров.\n"
            "- implementation_plan: пошаговый план внедрения изменений (этап, сроки, ответственный).\n"
            "- checklist: комплаенс чек-лист для проверки внедрения.\n"
            "Возвращайте чистый JSON-объект без markdown разметки."
        )

        prompt_content = draft_prompt_template.format(
            analysis_str=json.dumps(analysis, ensure_ascii=False, indent=2),
            related_docs=related_docs_str,
            style_guidelines=style_guidelines,
            past_mistakes=past_mistakes
        )

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        client = cls.get_client()
        if not client:
            raise RuntimeError("GEMINI_API_KEY не задан в .env. Для генерации проектов регламентов требуется подключение к Gemini API.")

        # 2 & 3. Run Draft & Impact Agents
        response = call_gemini_with_retry(
            client=client,
            model_name=model_name,
            contents=prompt_content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            ),
            max_retries=3,
            initial_delay=3.0
        )

        raw_draft = extract_clean_text(response)
        draft_data = extract_clean_json(raw_draft)
        
        # 4. Run Review Agent (Compliance, structure and quality check)
        review_prompt_record = db.query(Prompt).filter(Prompt.key == "review_prompt").first()
        review_prompt_template = review_prompt_record.content if review_prompt_record else (
            "Вы — Независимый комплаенс-контролер. "
            "Проверьте подготовленные методологические проекты на корректность, полноту ссылок на законы и отсутствие логических ошибок.\n\n"
            "АНАЛИЗ ИЗМЕНЕНИЙ:\n{analysis_str}\n\n"
            "СГЕНЕРИРОВАННЫЕ ПРОЕКТЫ И ВЛИЯНИЕ:\n{draft_str}\n\n"
            "Сформируйте отчет проверки качества в формате JSON с ключами:\n"
            "- score: оценка от 1 до 100.\n"
            "- issues: список выявленных неточностей, пропущенных ссылок или несоответствий.\n"
            "- recommendations: предложения по доработке текста.\n"
            "- is_approved: логическое значение (true, если оценка >= 80, иначе false).\n"
            "Возвращайте только JSON-объект без markdown разметки."
        )

        review_content = review_prompt_template.format(
            analysis_str=json.dumps(analysis, ensure_ascii=False, indent=2),
            draft_str=json.dumps(draft_data, ensure_ascii=False, indent=2)
        )

        review_response = call_gemini_with_retry(
            client=client,
            model_name=model_name,
            contents=review_content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            ),
            max_retries=3,
            initial_delay=3.0
        )

        raw_review = extract_clean_text(review_response)
        review_data = extract_clean_json(raw_review)
        
        # Normalize and combine results
        norm_departments = cls._normalize_departments(draft_data.get("affected_departments"))
        norm_plan = cls._normalize_plan(draft_data.get("implementation_plan"))
        norm_checklist = cls._normalize_checklist(draft_data.get("checklist"))
        norm_review = cls._normalize_review(review_data)

        # Save impact and drafts to task
        task.analysis_json = {
            **analysis,
            "affected_departments": norm_departments,
            "review_report": norm_review
        }
        task.draft_json = {
            "rules_changes": str(draft_data.get("rules_changes", "")),
            "memo": str(draft_data.get("memo", "")),
            "board_letter": str(draft_data.get("board_letter", "")),
            "board_directors_letter": str(draft_data.get("board_directors_letter", "")),
            "implementation_plan": norm_plan,
            "checklist": norm_checklist
        }
        db.commit()

        return {
            "status": "success",
            "score": norm_review.get("score", 0),
            "is_approved": norm_review.get("is_approved", False)
        }

