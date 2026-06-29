"""
Shared LLM setup và JSON parser cho tất cả agents
Tự động chọn: OpenAI nếu có key, ngược lại dùng Ollama
"""

import re
import json
from langchain_openai import ChatOpenAI
from config.config import settings


def extract_json(text: str, expect_array: bool = True):
    """
    Trích xuất JSON từ output AI — hoạt động dù AI có thêm text thừa.

    Thứ tự thử:
    1. Parse trực tiếp (AI trả đúng JSON)
    2. Tìm trong code block ```json ... ```
    3. Tìm [...] hoặc {...} đầu tiên trong text (regex)

    Returns: list hoặc dict đã parse, hoặc None nếu không tìm được.
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # 1. Thử parse trực tiếp
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Tìm trong ```json ... ``` hoặc ``` ... ```
    block = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if block:
        try:
            return json.loads(block.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Tìm JSON array [...] hoặc object {...} trong text hỗn hợp
    #    Lấy đoạn từ [ hoặc { đầu tiên đến ] hoặc } cuối cùng tương ứng
    if expect_array:
        start, end, opener, closer = cleaned.find("["), cleaned.rfind("]"), "[", "]"
    else:
        start, end, opener, closer = cleaned.find("{"), cleaned.rfind("}"), "{", "}"

    # Thử cả hai nếu cái kia không tìm thấy
    if start == -1 or end == -1:
        alt_start = cleaned.find("{") if expect_array else cleaned.find("[")
        alt_end = cleaned.rfind("}") if expect_array else cleaned.rfind("]")
        if alt_start != -1 and alt_end != -1 and alt_start < alt_end:
            start, end = alt_start, alt_end

    if start != -1 and end != -1 and start < end:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

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
