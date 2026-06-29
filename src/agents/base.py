"""
Shared LLM setup và JSON parser cho tất cả agents
Tự động chọn: OpenAI nếu có key, ngược lại dùng Ollama
"""

import re
import json
import logging
from langchain_openai import ChatOpenAI
from config.config import settings

logger = logging.getLogger(__name__)


def _find_balanced_end(text: str, start: int, opener: str, closer: str) -> int:
    """
    Walk forward from `start` (which must be the opener character) and return
    the index of the matching closer, respecting nesting and quoted strings.
    Returns -1 if no balanced closer is found.
    """
    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == "\"":
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return i
    return -1


def extract_json(text: str, expect_array: bool = True):
    """
    Trích xuất JSON từ output AI — hoạt động dù AI có thêm text thừa.

    Thứ tự thử:
    1. Parse trực tiếp (AI trả đúng JSON)
    2. Tìm trong code block ```json ... ```
    3. Tìm [...] hoặc {...} đầu tiên trong text, dùng bracket-balancing
       để xác định đúng điểm kết thúc (tránh cắt nhầm ở } nội tuyến)

    Returns: list hoặc dict đã parse, hoặc None nếu không tìm được.
    """
    if not text or not text.strip():
        logger.debug("extract_json: received empty text")
        return None

    cleaned = text.strip()
    logger.debug(f"extract_json: parsing text (len={len(cleaned)}, expect_array={expect_array}): {cleaned[:200]!r}")

    # 1. Thử parse trực tiếp
    try:
        result = json.loads(cleaned)
        logger.debug("extract_json: direct parse succeeded")
        return result
    except json.JSONDecodeError:
        pass

    # 2. Tìm trong ```json ... ``` hoặc ``` ... ```
    block = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if block:
        try:
            result = json.loads(block.group(1).strip())
            logger.debug("extract_json: code-block parse succeeded")
            return result
        except json.JSONDecodeError:
            pass

    # 3. Tìm JSON array [...] hoặc object {...} dùng bracket-balancing
    #    để xử lý đúng các object lồng nhau (nested objects/arrays).
    primary_opener  = "[" if expect_array else "{"
    primary_closer  = "]" if expect_array else "}"
    fallback_opener = "{" if expect_array else "["
    fallback_closer = "}" if expect_array else "]"

    for opener, closer in [(primary_opener, primary_closer), (fallback_opener, fallback_closer)]:
        start = cleaned.find(opener)
        if start == -1:
            continue
        end = _find_balanced_end(cleaned, start, opener, closer)
        if end == -1:
            continue
        candidate = cleaned[start:end + 1]
        try:
            result = json.loads(candidate)
            logger.debug(f"extract_json: bracket-balanced parse succeeded (opener={opener!r})")
            return result
        except json.JSONDecodeError as exc:
            logger.debug(f"extract_json: bracket-balanced parse failed (opener={opener!r}): {exc}")

    logger.warning(f"extract_json: all strategies failed for text: {cleaned[:300]!r}")
    return None


def get_llm(use_large: bool = False) -> ChatOpenAI:
    """
    Thứ tự ưu tiên:
      1. Groq  (cloud free, nhanh x10) — nếu có GROQ_API_KEY
      2. OpenAI (cloud paid)            — nếu có OPENAI_API_KEY
      3. Ollama (local)                 — fallback khi chạy local
    """
    """
    Trả về LLM instance.
    - use_large=True  → dùng GPT-4 Turbo (writer agent)
    - use_large=False → dùng GPT-4o-mini hoặc Ollama (các agent còn lại)
    """
    # 1. Groq — nhanh nhất, miễn phí
    if settings.groq_api_key:
        model = "llama-3.3-70b-versatile" if use_large else "llama-3.1-8b-instant"
        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
            model_name=model,
            temperature=0.7,
            max_tokens=2000,
        )

    # 2. OpenAI — paid
    if settings.openai_api_key:
        model = settings.openai_model if use_large else settings.openai_model_mini
        return ChatOpenAI(
            model_name=model,
            api_key=settings.openai_api_key,
            temperature=0.7,
            max_tokens=2000,
        )

    # 3. Ollama — local fallback
    return ChatOpenAI(
        base_url=settings.ollama_host + "/v1",
        api_key="ollama",
        model_name=settings.ollama_model,
        temperature=0.7,
        max_tokens=2000,
    )
