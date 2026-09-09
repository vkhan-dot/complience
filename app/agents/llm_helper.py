import os
import re
import json
import time
import difflib
import logging

logger = logging.getLogger(__name__)


def extract_clean_text(response) -> str:
    """Extracts clean text from GenAI response without non-text parts / thought_signature warnings."""
    try:
        if hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
            texts = [p.text for p in parts if hasattr(p, 'text') and p.text]
            if texts:
                return "".join(texts).strip()
    except Exception:
        pass
    return (getattr(response, 'text', '') or '').strip()


def extract_clean_json(raw_text: str) -> dict:
    """Parses JSON from model response, stripping possible markdown wrappers or comments."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```json") or lines[0].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    return json.loads(text)


def extract_smart_diff_context(old_text: str, new_text: str, max_chars: int = 15000) -> tuple[str, str]:
    """
    Extracts only the modified articles/sections between old and new text.
    If the document has changed in only a few articles, returns only those articles
    with surrounding context, rather than sending a 500k char payload.
    """
    if not old_text:
        if len(new_text) > max_chars:
            return "", new_text[:max_chars] + f"\n\n[... Документ сокращен до первых {max_chars} символов для анализа ...]"
        return "", new_text

    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    diff_old_blocks = []
    diff_new_blocks = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete'):
            start = max(0, i1 - 3)
            end = min(len(old_lines), i2 + 3)
            diff_old_blocks.append("\n".join(old_lines[start:end]))
        if tag in ('replace', 'insert'):
            start = max(0, j1 - 3)
            end = min(len(new_lines), j2 + 3)
            diff_new_blocks.append("\n".join(new_lines[start:end]))

    extracted_old = "\n\n---\n\n".join(diff_old_blocks)
    extracted_new = "\n\n---\n\n".join(diff_new_blocks)

    if not extracted_old and not extracted_new:
        return old_text[:max_chars], new_text[:max_chars]

    if len(extracted_old) > max_chars:
        extracted_old = extracted_old[:max_chars] + "\n[... Сокращено ...]"
    if len(extracted_new) > max_chars:
        extracted_new = extracted_new[:max_chars] + "\n[... Сокращено ...]"

    return extracted_old, extracted_new


def call_gemini_with_retry(client, model_name: str, contents, config, max_retries: int = 3, initial_delay: float = 3.0):
    """
    Calls Gemini generate_content with automatic retry and exponential backoff on 429 RESOURCE_EXHAUSTED.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                if attempt < max_retries:
                    sleep_time = delay * attempt
                    logger.warning(f"Gemini 429 Rate Limit hit. Retrying attempt {attempt}/{max_retries} in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
            raise
