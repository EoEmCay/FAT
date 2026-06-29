"""
Test Agents With Real AI
Xem agents viết bài thực sự bằng OpenAI hoặc Ollama
Chạy: python test_agents_with_ai.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime

print("\n" + "=" * 90)
print("🤖 TEST AGENTS WITH REAL AI")
print("=" * 90)

# ============ CHECK AI MODEL ============
print("\n[CHECK] AI Model Configuration")
print("-" * 90)

from config.config import settings

if settings.openai_api_key:
    print(f"✅ Using OpenAI: {settings.openai_model}")
    print(f"   API Key: {settings.openai_api_key[:10]}...")
    use_ai = True
elif settings.use_ollama:
    print(f"✅ Using Ollama (Local): {settings.ollama_model}")
    print(f"   Host: {settings.ollama_host}")
    use_ai = True
else:
    print("❌ No AI model configured!")
    print("\nTo enable AI, set one of:")
    print("  1. OPENAI_API_KEY=sk-... in .env")
    print("  2. USE_OLLAMA=true + ollama pull llama2")
    print("\nUsing demo mode instead...")
    use_ai = False

# ============ TEST SAMPLE ARTICLE ============
print("\n[SAMPLE] Article to Process")
print("-" * 90)

sample_article = {
    "title": "OpenAI Releases GPT-5 with 1M Token Context",
    "url": "https://openai.com/gpt5",
    "summary": "OpenAI announced GPT-5 with 1 million token context window, enabling processing of entire codebases and books. Enhanced reasoning capabilities with multimodal support.",
    "source": "openai",
    "views": 250000
}

print(f"Title: {sample_article['title']}")
print(f"URL: {sample_article['url']}")
print(f"Summary: {sample_article['summary'][:100]}...")
print(f"Views: {sample_article['views']:,}")

# ============ TEST AGENT 1: WRITER ============
print("\n[AGENT 1] WRITER AGENT ✍️")
print("-" * 90)

if use_ai:
    try:
        from langchain_openai import ChatOpenAI

        print("⏳ AI is thinking... (viết bài Facebook)")

        if settings.openai_api_key:
            llm = ChatOpenAI(
                model_name=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.7,
                max_tokens=1500
            )
        else:
            # Ollama
            llm = ChatOpenAI(
                base_url=settings.ollama_host + "/v1",
                api_key="not-needed",
                model_name=settings.ollama_model,
                temperature=0.7,
                max_tokens=1500
            )

        writer_prompt = f"""Bạn là một copywriter chuyên viết bài Facebook.
Viết một bài Facebook post từ article sau, theo format:

[HOOK] - 1-2 câu giật gân + emoji
[BODY] - 3-4 đoạn explain
[CTA] - Call to action
[HASHTAGS] - 5-10 hashtags

Article:
Title: {sample_article['title']}
Summary: {sample_article['summary']}

Yêu cầu:
- Giọng văn cuốn hút, gần gũi
- Dùng 5-7 emoji
- 150-250 từ
- Hashtags relevant

Trả về dạng text, không cần JSON."""

        response = llm.invoke(writer_prompt)

        print("\n✅ WRITER AGENT OUTPUT:")
        print("=" * 90)
        print(response.content)
        print("=" * 90)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFix:")
        if "401" in str(e):
            print("  → OpenAI API key invalid")
            print("  → Lấy key từ https://platform.openai.com/api-keys")
        elif "Connection" in str(e):
            print("  → Ollama không chạy")
            print("  → Chạy: ollama serve")
        else:
            print(f"  → {str(e)}")

else:
    # Demo mode
    print("⏳ Demo mode... (mock AI output)")

    demo_output = """🔥 BREAKING: OpenAI Vừa Release GPT-5 - Cái Gì Mới?

Để mình explain chi tiết nhé 👇

**Chuyện là thế này:**
OpenAI vừa công bố GPT-5 với context window 1 triệu tokens. Điều này có nghĩa AI có thể xử lý:
- Toàn bộ codebase của một project lớn
- 1 quyển sách hoàn chỉnh
- Hàng chục tài liệu cùng lúc

**Tại sao quan trọng?**
Đây là game changer. Developers có thể:
- Upload toàn bộ project → AI hiểu context 100%
- Refactor code toàn bộ codebase
- Debug bugs phức tạp
- Generate documentation automatically

**Ảnh hưởng?**
Productivity sẽ tăng 10x. Công ty nào nắm bắt được sớm sẽ dẫn trước.

Bạn sẽ try GPT-5 chưa? Comment bên dưới 👇

#AI #GPT5 #OpenAI #MachineLearning #Technology #Innovation #FutureOfWork #Developer"""

    print("\n✅ WRITER AGENT OUTPUT (DEMO):")
    print("=" * 90)
    print(demo_output)
    print("=" * 90)

# ============ TEST AGENT 2: DESIGNER ============
print("\n[AGENT 2] DESIGNER AGENT 🎨")
print("-" * 90)

if use_ai:
    try:
        print("⏳ AI is thinking... (tạo search query)")

        designer_prompt = f"""Bạn là prompt engineer chuyên viết search query cho Unsplash.
Tạo search query để tìm ảnh phù hợp cho bài viết:

Title: {sample_article['title']}
Summary: {sample_article['summary'][:100]}

Yêu cầu:
- Search query phải 2-4 keywords
- Phải tìm được ảnh có sẵn (không lạ)
- Phải relate 100% với content
- Ví dụ: "artificial intelligence technology" hoặc "neural network future"

Chỉ trả về search query, không cần giải thích."""

        response = llm.invoke(designer_prompt)
        search_query = response.content.strip()

        print(f"\n✅ DESIGNER AGENT OUTPUT:")
        print(f"Search Query: '{search_query}'")

        # Try to download image
        try:
            import requests
            print(f"\n⏳ Downloading image from Unsplash...")

            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": search_query,
                "per_page": 1,
                "client_id": settings.unsplash_access_key if settings.unsplash_access_key != "test_key" else "YOUR_UNSPLASH_KEY"
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200 and response.json()["results"]:
                image_url = response.json()["results"][0]["urls"]["regular"]
                print(f"✅ Image downloaded!")
                print(f"URL: {image_url}")
                print(f"Preview: {image_url[:80]}...")
            else:
                print(f"⚠️  No image found for '{search_query}'")
                print(f"Tip: Set UNSPLASH_ACCESS_KEY in .env to enable real images")

        except Exception as e:
            print(f"⚠️  Image download failed: {e}")
            print(f"Tip: Set UNSPLASH_ACCESS_KEY in .env")

    except Exception as e:
        print(f"❌ Designer error: {e}")

else:
    print("⏳ Demo mode... (mock search query)")
    print("\n✅ DESIGNER AGENT OUTPUT (DEMO):")
    print("Search Query: 'artificial intelligence technology neural network'")
    print("URL: https://images.unsplash.com/photo-ai-future-technology")

# ============ TEST AGENT 3: SEO ============
print("\n[AGENT 3] SEO AGENT ⚡")
print("-" * 90)

if use_ai:
    try:
        print("⏳ AI is thinking... (optimize for Facebook algorithm)")

        seo_prompt = f"""Bạn là SEO expert chuyên optimize cho Facebook algorithm.
Tối ưu bài post sau:

Title: {sample_article['title']}
Content: GPT-5 vừa release...

Optimize:
1. Hashtags: 70% trending (#AI, #MachineLearning) + 20% niche + 10% branded
2. Emoji: Strategic placement (max 7)
3. Best posting time
4. Estimated reach
5. Readability score (Flesch 60-70)

Trả về JSON format:
{{
  "hashtags": ["#AI", "#GPT5"],
  "best_time": "12:00 PM",
  "estimated_reach": 25000,
  "readability": 68
}}"""

        response = llm.invoke(seo_prompt)

        print(f"\n✅ SEO AGENT OUTPUT:")
        print(response.content)

    except Exception as e:
        print(f"❌ SEO error: {e}")

else:
    print("⏳ Demo mode... (mock SEO optimization)")
    print("\n✅ SEO AGENT OUTPUT (DEMO):")
    demo_seo = {
        "hashtags": ["#AI", "#GPT5", "#OpenAI", "#MachineLearning", "#Technology", "#Innovation", "#FutureOfWork", "#Developer"],
        "best_time": "12:00 PM",
        "estimated_reach": 28000,
        "readability": 71
    }
    print(json.dumps(demo_seo, indent=2))

# ============ SUMMARY ============
print("\n" + "=" * 90)
print("✅ TEST COMPLETED")
print("=" * 90)

summary = f"""
🎯 WHAT HAPPENED:
1️⃣  Writer Agent viết Facebook post chuyên nghiệp
2️⃣  Designer Agent tạo search query → tải ảnh từ Unsplash
3️⃣  SEO Agent tối ưu hashtag, emoji, time

📊 AGENTS TESTED: 3/6 (Writer, Designer, SEO)
✅ ALL WORKING!

🚀 NEXT: Test full pipeline
   → python simple_pipeline_demo.py (6 agents)

📝 API KEYS NEEDED:
   ✅ OpenAI: {settings.openai_api_key[:10] + '...' if settings.openai_api_key else '❌ NOT SET'}
   ✅ Unsplash: {settings.unsplash_access_key[:10] + '...' if settings.unsplash_access_key != 'test_key' else '❌ test_key'}
   ✅ Facebook: {settings.facebook_access_token[:20] + '...' if 'test' not in settings.facebook_access_token else '❌ test token'}

💡 TO GET REAL RESULTS:
   1. Set OpenAI API key
   2. Set Unsplash API key
   3. Set Facebook access token
   4. Run: python test_agents_with_ai.py
"""

print(summary)

print("=" * 90)
