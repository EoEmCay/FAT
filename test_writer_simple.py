"""
Simple Writer Test - Xem AI viết bài Facebook
Bạn có thể chạy: python test_writer_simple.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import settings
from langchain_openai import ChatOpenAI
import json

# Sample article
SAMPLE_ARTICLE = """
Title: OpenAI Releases GPT-5 Model
URL: https://openai.com/news/gpt5
Content: OpenAI vừa công bố mô hình GPT-5 với khả năng xử lý 1 triệu tokens,
cải thiện reasoning capabilities, và hỗ trợ multimodal input bao gồm video.
Đây là bước tiến lớn so với GPT-4 Turbo.
"""

PROMPT = """
Bạn là một copywriter chuyên viết bài Facebook cho công nghệ.
Viết một bài Facebook post từ article dưới đây.

Format bài viết:
1. HOOK (1-2 câu, dùng emoji)
2. BODY (3-4 đoạn, explain tại sao quan trọng)
3. CTA (call to action)
4. HASHTAGS (max 10 hashtags)

Yêu cầu:
- Chuyên nghiệp nhưng gần gũi
- Dùng 5-7 emoji
- 150-250 từ
- Giọng văn tự nhiên, không formal quá

Article:
{article}

Trả về dưới dạng JSON:
{{
    "hook": "...",
    "body": "...",
    "cta": "...",
    "hashtags": ["#...", "#..."],
    "word_count": 0
}}
""".format(article=SAMPLE_ARTICLE)

def test_with_openai():
    """Test với OpenAI"""
    if not settings.openai_api_key:
        print("❌ OPENAI_API_KEY chưa được set")
        return False

    try:
        print("\n🔌 Connecting to OpenAI...")
        llm = ChatOpenAI(
            model_name=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.7,
            max_tokens=1500
        )

        print(f"✅ Connected to {settings.openai_model}")
        print("\n🚀 Generating Facebook post...\n")

        response = llm.invoke(PROMPT)

        print("="*70)
        print("📝 AI GENERATED POST:")
        print("="*70)
        print(response.content)
        print("="*70)

        return True

    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
        return False

def test_with_ollama():
    """Test với Ollama (Local)"""
    if not settings.use_ollama:
        return False

    try:
        print("\n🔌 Connecting to Ollama...")
        llm = ChatOpenAI(
            base_url=settings.ollama_host + "/v1",
            api_key="not-needed",
            model_name=settings.ollama_model,
            temperature=0.7,
            max_tokens=1500
        )

        print(f"✅ Connected to Ollama ({settings.ollama_model})")
        print("\n🚀 Generating Facebook post...\n")
        print("⏳ This may take a minute with local model...\n")

        response = llm.invoke(PROMPT)

        print("="*70)
        print("📝 AI GENERATED POST:")
        print("="*70)
        print(response.content)
        print("="*70)

        return True

    except Exception as e:
        print(f"❌ Ollama Error: {str(e)}")
        return False

def main():
    print("="*70)
    print("🤖 FACEBOOK AI WRITER - TEST")
    print("="*70)

    print("\n📄 Sample Article:")
    print(SAMPLE_ARTICLE)

    print("\n" + "-"*70)
    print("🔍 Checking AI Models...")
    print("-"*70)

    # Try OpenAI first
    if settings.openai_api_key:
        print(f"OpenAI API Key: ✅ Set")
        if test_with_openai():
            return
    else:
        print(f"OpenAI API Key: ❌ Not set")

    # Try Ollama
    if settings.use_ollama:
        print(f"Ollama: ✅ Enabled ({settings.ollama_host})")
        if test_with_ollama():
            return
    else:
        print(f"Ollama: ❌ Disabled")

    print("\n" + "="*70)
    print("⚠️  CÁCH FIX:")
    print("="*70)
    print("\n1️⃣  Dùng OpenAI (Recommended):")
    print("   - Lấy API key: https://platform.openai.com/api-keys")
    print("   - Thêm vào .env: OPENAI_API_KEY=sk-...")
    print("   - Run lại: python test_writer_simple.py")

    print("\n2️⃣  Dùng Ollama (Free, Local):")
    print("   - Cài Ollama: https://ollama.ai")
    print("   - Chạy: ollama pull llama2")
    print("   - Set .env: USE_OLLAMA=true")
    print("   - Run lại: python test_writer_simple.py")

if __name__ == "__main__":
    main()
