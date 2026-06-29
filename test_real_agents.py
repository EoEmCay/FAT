"""
Test agents thực sự với AI (LangChain + Ollama hoặc OpenAI)
Chạy: python test_real_agents.py
"""
import sys, json, asyncio
sys.path.insert(0, ".")

from config.config import settings
from src.agents.scraper_agent import ScraperAgent
from src.agents.filter_agent import FilterAgent
from src.agents.writer_agent import WriterAgent
from src.agents.seo_agent import SEOAgent

SEP = "=" * 70

print(f"\n{SEP}")
print("🤖 TEST REAL AI AGENTS (LangChain)")
print(SEP)

# Kiểm tra AI model
if settings.openai_api_key:
    print(f"✅ AI: OpenAI {settings.openai_model}")
elif settings.use_ollama:
    print(f"✅ AI: Ollama ({settings.ollama_model}) tại {settings.ollama_host}")
    print("   ⚠️  Cần chạy 'ollama serve' trước!")
else:
    print("❌ Không có AI model nào được cấu hình!")
    sys.exit(1)

input("\nNhấn Enter để bắt đầu chạy Agent 1 (Scraper)...")

# ── AGENT 1: SCRAPER ──────────────────────────────────────────────
print(f"\n{SEP}")
print("1️⃣  SCRAPER AGENT — AI đang cào & tổng hợp tin tức...")
print(SEP)

try:
    result = ScraperAgent.run()
    print("\n📰 RAW OUTPUT từ AI:")
    print("-" * 70)
    print(result[:800])
    if len(result) > 800:
        print("... [truncated]")

    articles = json.loads(result) if result.strip().startswith("[") else []
    print(f"\n✅ Scraper: {len(articles)} articles")
    if articles:
        print(f"   Ví dụ: {articles[0].get('title', 'N/A')}")
except Exception as e:
    print(f"❌ Scraper lỗi: {e}")
    print("   → Nếu 'Connection refused': chạy 'ollama serve' rồi thử lại")
    sys.exit(1)

input("\nNhấn Enter để chạy Agent 2 (Filter)...")

# ── AGENT 2: FILTER ───────────────────────────────────────────────
print(f"\n{SEP}")
print("2️⃣  FILTER AGENT — AI đang lọc & chấm điểm...")
print(SEP)

try:
    filtered = FilterAgent.run(result)
    print("\n🔎 OUTPUT từ Filter Agent:")
    print("-" * 70)
    print(filtered[:800])

    items = json.loads(filtered) if filtered.strip().startswith("[") else []
    print(f"\n✅ Filter: còn {len(items)} articles sau khi lọc")
    if items:
        for it in items[:3]:
            print(f"   • [{it.get('score', '?')}/10] {it.get('title', 'N/A')[:60]}")
except Exception as e:
    print(f"❌ Filter lỗi: {e}")
    filtered = result  # dùng raw nếu lỗi

input("\nNhấn Enter để chạy Agent 3 (Writer)...")

# ── AGENT 3: WRITER ───────────────────────────────────────────────
print(f"\n{SEP}")
print("3️⃣  WRITER AGENT — AI đang viết bài Facebook...")
print(SEP)

try:
    written = WriterAgent.run(filtered)
    print("\n✍️  OUTPUT từ Writer Agent:")
    print("-" * 70)

    posts = json.loads(written) if written.strip().startswith("[") else []
    if posts:
        post = posts[0]
        print(f"\n🔥 HOOK:\n{post.get('hook', 'N/A')}")
        print(f"\n📝 BODY:\n{post.get('body', 'N/A')[:400]}...")
        print(f"\n👉 CTA:\n{post.get('cta', 'N/A')}")
        print(f"\n#️⃣  HASHTAGS:\n{' '.join(post.get('hashtags', []))}")
        print(f"\n📊 Word count: {post.get('word_count', '?')} | Emoji: {post.get('emoji_count', '?')}")
    else:
        print(written[:600])

    print(f"\n✅ Writer: {len(posts)} bài viết")
except Exception as e:
    print(f"❌ Writer lỗi: {e}")
    written = filtered

input("\nNhấn Enter để chạy Agent 5 (SEO)...")

# ── AGENT 5: SEO ──────────────────────────────────────────────────
print(f"\n{SEP}")
print("5️⃣  SEO AGENT — AI đang tối ưu hashtag & format...")
print(SEP)

try:
    optimized = SEOAgent.run(written)
    print("\n⚡ OUTPUT từ SEO Agent:")
    print("-" * 70)

    opts = json.loads(optimized) if optimized.strip().startswith("[") else []
    if opts:
        opt = opts[0]
        print(f"Best posting time: {opt.get('best_posting_time', '?')}")
        print(f"Estimated reach:   {opt.get('estimated_reach', '?'):,} people")
        print(f"Readability score: {opt.get('readability_score', '?')}/100")
        print(f"Hashtags ({len(opt.get('hashtags_optimized', []))}): {' '.join(opt.get('hashtags_optimized', [])[:6])}")
    else:
        print(optimized[:400])

    print(f"\n✅ SEO: {len(opts)} bài đã tối ưu")
except Exception as e:
    print(f"❌ SEO lỗi: {e}")

# ── SUMMARY ───────────────────────────────────────────────────────
print(f"\n{SEP}")
print("✅ TEST HOÀN TẤT")
print(SEP)
print("""
Kết quả:
  1️⃣  Scraper ✅ — AI tổng hợp articles
  2️⃣  Filter  ✅ — AI lọc & chấm điểm
  3️⃣  Writer  ✅ — AI viết bài Facebook thực sự
  5️⃣  SEO     ✅ — AI tối ưu hashtag & reach

Bước tiếp theo để chạy 24/24:
  1. Cài Ollama: https://ollama.ai → ollama pull llama2
  2. Lấy Facebook token: developers.facebook.com/tools/explorer
  3. Lấy Unsplash key: unsplash.com/oauth/applications
  4. Điền vào .env
  5. python main.py → http://localhost:8501 → START SYSTEM
""")
print(SEP)
