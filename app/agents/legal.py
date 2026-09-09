import os
import json
import logging
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from app.models import Prompt
from app.agents.llm_helper import (
    call_gemini_with_retry,
    extract_clean_json,
    extract_clean_text,
    extract_smart_diff_context
)

logger = logging.getLogger(__name__)


class LegalAgent:
    """
    LegalAgent uses Gemini to perform compliance analysis on document changes.
    It takes the old and new markdown content and determines the legal impact, 
    risks, consequences, and deadlines.
    """

    @classmethod
    def get_client(cls) -> genai.Client | None:
        """Initializes the Google GenAI client using the API key from environment."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize genai.Client: {e}")
            return None


    @classmethod
    def analyze_changes(cls, old_text: str, new_text: str, db: Session) -> dict:
        """
        Invokes Gemini to analyze the difference between old and new text.
        Loads prompts from Prompt Zone (database) to allow customization.
        Extracts only the modified/added sections to maintain token efficiency and prevent 429 errors.
        """
        # Extract token-efficient smart diff delta
        diff_old, diff_new = extract_smart_diff_context(old_text, new_text, max_chars=12000)

        # Load system and legal analysis prompts from DB
        system_prompt_record = db.query(Prompt).filter(Prompt.key == "system_prompt").first()
        legal_prompt_record = db.query(Prompt).filter(Prompt.key == "legal_prompt").first()
        
        system_prompt = system_prompt_record.content if system_prompt_record else (
            "Вы — Старший методолог и комплаенс-офицер страховой компании Республики Казахстан. "
            "Вы анализируете изменения законодательства, оцениваете комплаенс-риски и последствия."
        )
        
        legal_prompt_template = legal_prompt_record.content if legal_prompt_record else (
            "Проанализируй изменения между предыдущей и новой редакцией нормативного акта.\n\n"
            "Предыдущая редакция:\n```markdown\n{old_text}\n```\n\n"
            "Новая редакция:\n```markdown\n{new_text}\n```\n\n"
            "Подготовь подробный юридический анализ. Ответ верни в строгом формате JSON со следующими ключами:\n"
            "- what_changed (что конкретно изменилось в статьях/нормах)\n"
            "- requirements (новые регуляторные требования, которые компания обязана исполнять)\n"
            "- deadlines (сроки и даты вступления в силу, переходные периоды)\n"
            "- risks (риски несоблюдения для страховой компании, штрафы, предписания АРРФР)\n"
            "- consequences (последствия для бизнес-процессов страховой компании)\n"
            "- affected_departments (список объектов: [{'department': 'Название департамента', 'reason': 'Почему затронут'}])\n"
            "Не используй markdown разметку вокруг JSON в ответе, верни чистый JSON-объект."
        )

        prompt_content = legal_prompt_template.format(
            old_text=diff_old,
            new_text=diff_new
        )
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        # Call Gemini API
        client = cls.get_client()
        if not client:
            raise RuntimeError("GEMINI_API_KEY не задан в .env. Для выполнения юридического анализа требуется подключение к Gemini API.")
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.1
        )
        
        response = call_gemini_with_retry(
            client=client,
            model_name=model_name,
            contents=prompt_content,
            config=config,
            max_retries=3,
            initial_delay=3.0
        )
        
        raw_text = extract_clean_text(response)
        return extract_clean_json(raw_text)

    @classmethod
    def audit_compliance(cls, current_text: str, db: Session) -> dict:
        """
        Runs a general compliance assessment of the current (unchanged since last
        check) redaction of a monitored act, rather than a diff-based analysis.
        Used when a source check finds no textual changes, so the company still
        gets a periodic read on whether it complies with the act as it stands.
        Returns the same dict shape as analyze_changes so it flows through the
        existing DocumentAgent draft/review pipeline and task detail UI unchanged.
        """
        bounded_text = current_text
        if len(current_text) > 15000:
            bounded_text = current_text[:15000] + "\n\n[... Документ сокращен для комплаенс-аудита ...]"

        audit_prompt_record = db.query(Prompt).filter(Prompt.key == "audit_prompt").first()
        audit_prompt_template = audit_prompt_record.content if audit_prompt_record else (
            "Проанализируй действующую редакцию нормативного акта ниже и оцени, насколько деятельность "
            "страховой компании потенциально соответствует ему в целом (плановая проверка — изменений "
            "текста закона с прошлой проверки не обнаружено).\n\n"
            "Действующая редакция:\n```markdown\n{current_text}\n```\n\n"
            "Подготовь подробный комплаенс-анализ. Ответ верни в строгом формате JSON со следующими ключами:\n"
            "- what_changed (кратко: что именно проверялось и что изменений в тексте закона нет)\n"
            "- requirements (ключевые регуляторные требования данного акта, которые компания обязана соблюдать)\n"
            "- deadlines (периодические или регулярные сроки/дедлайны, связанные с исполнением требований)\n"
            "- risks (риски несоблюдения для страховой компании, если требования не выполняются)\n"
            "- consequences (последствия для бизнес-процессов и рекомендации по проверке соответствия)\n"
            "Не используй markdown разметку вокруг JSON в ответе, верни чистый JSON-объект."
        )

        system_prompt_record = db.query(Prompt).filter(Prompt.key == "system_prompt").first()
        system_prompt = system_prompt_record.content if system_prompt_record else (
            "Вы — Старший методолог и комплаенс-офицер страховой компании Республики Казахстан. "
            "Вы анализируете изменения законодательства, оцениваете комплаенс-риски и последствия."
        )

        prompt_content = audit_prompt_template.format(current_text=bounded_text)
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        client = cls.get_client()
        if not client:
            raise RuntimeError("GEMINI_API_KEY не задан в .env. Для проведения планового аудита требуется подключение к Gemini API.")

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.1
        )

        response = call_gemini_with_retry(
            client=client,
            model_name=model_name,
            contents=prompt_content,
            config=config,
            max_retries=3,
            initial_delay=3.0
        )

        raw_text = extract_clean_text(response)
        return extract_clean_json(raw_text)


    @classmethod
    def _grounded_json_call(cls, prompt_content: str, log_label: str) -> tuple[str | None, str | None]:
        """
        Calls Gemini with Google Search grounding first (GEMINI_GROUNDING_MODEL),
        falling back to an ungrounded call (GEMINI_MODEL) if grounding fails or
        is unavailable (e.g. 429 on free-tier keys - grounding quota/pricing is
        tracked per-model, separately from plain generation). Returns
        (raw_json_text, error) - raw_json_text has markdown code fences already
        stripped; error is None on success.
        """
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        grounding_model_name = os.getenv("GEMINI_GROUNDING_MODEL", "gemini-2.5-flash")
        client = cls.get_client()
        if not client:
            return None, "GEMINI_API_KEY is not configured in environment"


        # Grounding and forced JSON response_mime_type are not combinable in the
        # Gemini API, so JSON is enforced via the prompt for the grounded
        # attempt and parsed leniently; the ungrounded fallback can use
        # response_mime_type directly for a more reliable JSON contract.
        attempts = [
            (grounding_model_name, types.GenerateContentConfig(
                temperature=0.1,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )),
            (model_name, types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )),
        ]

        last_error = None
        for attempt_num, (attempt_model, config) in enumerate(attempts):
            try:
                response = client.models.generate_content(
                    model=attempt_model,
                    contents=prompt_content,
                    config=config
                )

                raw_text = response.text.strip()
                if raw_text.startswith("```"):
                    lines = raw_text.splitlines()
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        raw_text = "\n".join(lines[1:-1]).strip()

                if attempt_num > 0:
                    logger.warning(f"{log_label}: grounding unavailable, used ungrounded fallback (URLs are unverified)")
                return raw_text, None

            except Exception as e:
                last_error = e
                logger.warning(f"{log_label} attempt {attempt_num} failed: {e}")

        logger.error(f"{log_label}: all attempts failed: {last_error}")
        return None, str(last_error)

    @classmethod
    def suggest_monitoring_sources(cls, content: str, db: Session) -> tuple[list[dict], str | None]:
        """
        Analyzes internal document content and proposes external legislation that
        should be monitored, attempting to resolve real URLs via Google Search
        grounding. Returns (suggestions, error_message) — nothing is created
        automatically, the caller must present these for human review before
        creating a Source. error_message is None on success; when set, the
        caller should surface it distinctly from "AI found nothing".
        """
        prompt_record = db.query(Prompt).filter(Prompt.key == "source_suggestion_prompt").first()
        prompt_template = prompt_record.content if prompt_record else (
            "Ты — старший методолог и комплаенс-офицер страховой компании Республики Казахстан.\n"
            "Изучи текст внутреннего документа компании ниже и определи, какие законы, постановления "
            "АРРФР и иные нормативно-правовые акты РК регулируют описанную деятельность и должны "
            "отслеживаться на предмет изменений.\n\n"
            "ТЕКСТ ДОКУМЕНТА:\n```markdown\n{content}\n```\n\n"
            "Для каждого найденного НПА укажи точное официальное название, официальную ссылку на "
            "актуальную редакцию (используй поиск, чтобы найти реальную страницу на adilet.zan.kz "
            "или официальном портале АРРФР/egov.kz — не придумывай ссылку, если не уверен, оставь "
            "url пустой строкой) и краткое обоснование, почему документ на него ссылается.\n\n"
            "Верни строго JSON-массив (без markdown разметки вокруг) вида:\n"
            "[{{\"title\": \"...\", \"url\": \"...\", \"reason\": \"...\", \"confidence\": \"high|medium|low\"}}]"
        )
        prompt_content = prompt_template.format(content=content[:8000])

        raw_text, error = cls._grounded_json_call(prompt_content, "suggest_monitoring_sources")
        if error:
            return [], error

        try:
            suggestions = json.loads(raw_text)
            if not isinstance(suggestions, list):
                return [], None
            return [s for s in suggestions if isinstance(s, dict) and s.get("title")], None
        except Exception as e:
            logger.error(f"suggest_monitoring_sources: failed to parse JSON response: {e}")
            return [], str(e)

    @classmethod
    def find_source_url(cls, title: str) -> dict:
        """
        Uses Google Search grounding to find the current, official URL for a
        specific piece of legislation by title - e.g. to fix a monitored Source
        whose stored URL has gone stale (404) or was inaccurate to begin with.
        Returns {"url", "confidence", "note", "error"} - url is None/empty if
        not found with confidence; the caller must present it for human
        confirmation before overwriting the Source's URL.
        """
        prompt_content = (
            "Ты — старший методолог страховой компании Республики Казахстан.\n"
            f"Найди официальную ссылку на актуальную редакцию следующего нормативно-правового "
            f"акта Республики Казахстан: \"{title}\".\n"
            "Используй поиск, чтобы найти реальную рабочую страницу на adilet.zan.kz или "
            "официальном портале АРРФР/egov.kz. Не придумывай ссылку — если не уверен на 100%, "
            "верни пустую строку в поле url.\n\n"
            "Верни строго JSON-объект (без markdown разметки вокруг) вида:\n"
            "{\"url\": \"...\", \"confidence\": \"high|medium|low\", \"note\": \"...\"}"
        )

        raw_text, error = cls._grounded_json_call(prompt_content, "find_source_url")
        if error:
            return {"url": None, "confidence": None, "note": None, "error": error}

        try:
            result = json.loads(raw_text)
            if not isinstance(result, dict):
                return {"url": None, "confidence": None, "note": None, "error": None}
            return {
                "url": result.get("url") or None,
                "confidence": result.get("confidence"),
                "note": result.get("note"),
                "error": None
            }
        except Exception as e:
            logger.error(f"find_source_url: failed to parse JSON response: {e}")
            return {"url": None, "confidence": None, "note": None, "error": str(e)}
