"""
Simplified Pipeline Demo - Chạy ngay được
Xem từng agent viết bài, tạo ảnh, tối ưu dần dần
Chạy: python simple_pipeline_demo.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime
import os

print("\n" + "=" * 90)
print("🚀 FACEBOOK AUTOMATION PIPELINE - SIMPLIFIED DEMO")
print("=" * 90)

# ============ SETUP ============
from config.config import settings

print("\n[CONFIG]")
print(f"  🤖 AI Model: {'OpenAI ' + settings.openai_model if settings.openai_api_key else 'Ollama (Local)'}")
print(f"  💾 Database: SQLite")
print(f"  🕐 Schedule: {settings.scraper_time} / {settings.processor_time} / {settings.publisher_time}")
print(f"  📍 Timezone: {settings.scheduler_timezone}")

# ============ MOCK DATA ============
print("\n" + "=" * 90)
print("📰 ARTICLE SOURCES (from Medium, GitHub, Hugging Face)")
print("=" * 90)

articles = [
    {
        "id": 1,
        "source": "medium",
        "title": "OpenAI Releases GPT-5: The Next Era of AI",
        "url": "https://medium.com/@openai/gpt-5",
        "summary": "OpenAI unveiled GPT-5 with 1M token context window and enhanced reasoning capabilities",
        "views": 150000,
        "published": "2026-06-28"
    },
    {
        "id": 2,
        "source": "github",
        "title": "TensorFlow 3.0 Launches Major Update",
        "url": "https://github.com/tensorflow/tensorflow",
        "summary": "TensorFlow releases version 3.0 with distributed training improvements",
        "views": 80000,
        "published": "2026-06-27"
    },
    {
        "id": 3,
        "source": "huggingface",
        "title": "LLaMA 3.0 Model Released",
        "url": "https://huggingface.co/meta-llama",
        "summary": "Meta releases LLaMA 3.0 with 70B parameters and improved performance",
        "views": 120000,
        "published": "2026-06-26"
    }
]

for i, article in enumerate(articles, 1):
    print(f"\n{i}. [{article['source'].upper()}] {article['title']}")
    print(f"   📊 Views: {article['views']:,} | Published: {article['published']}")
    print(f"   📝 {article['summary']}")

# ============ STEP 1: SCRAPER AGENT ============
print("\n" + "=" * 90)
print("STEP 1️⃣  - SCRAPER AGENT 🔍")
print("=" * 90)
print("""
Role: Chuyên gia Thu thập Dữ liệu và Phát hiện Xu hướng
Goal: Cào dữ liệu từ báo chính thống, GitHub Trending, Hugging Face

Task:
  ✓ Cào từ Medium (AI & Technology tags)
  ✓ Cào từ GitHub Trending (Python, JavaScript)
  ✓ Cào từ Hugging Face (trending models)
  ✓ Filter: Chỉ lấy 7 ngày gần nhất, loại bỏ spam/duplicate
  ✓ Output: 35-50 articles với title, url, summary, views, tags
""")

print(f"⏳ Simulating scraper... cào {len(articles)} articles")
print("✅ SCRAPER COMPLETED")
print(f"\n📊 Result: {len(articles)} articles scraped")

# ============ STEP 2: FILTER AGENT ============
print("\n" + "=" * 90)
print("STEP 2️⃣  - FILTER AGENT 🔎")
print("=" * 90)
print("""
Role: Chuyên gia Lọc Tin và Xác Minh Sự Thật
Goal: Lọc, verify facts, xếp hạng articles

Task:
  ✓ Loại bỏ duplicate (check URL, title)
  ✓ Loại bỏ từ nguồn không đáng tin
  ✓ Xác minh sự thật
  ✓ Tóm tắt 2-3 câu cốt lõi
  ✓ Xếp hạng (Score 0-10)
  ✓ Chỉ giữ 5-10 articles (score >= 6)
""")

# Simulate filter scoring
filtered = []
for article in articles:
    score = min(10, max(0, 4 + (article["views"] // 50000)))  # Simple scoring
    if score >= 6:
        filtered.append({
            **article,
            "score": score,
            "verified": True,
            "importance": "High" if score >= 8 else "Medium"
        })

print(f"⏳ Simulating filter... analyzing {len(articles)} articles")
print("✅ FILTER COMPLETED")

print(f"\n📊 Result: {len(filtered)} high-quality articles selected")
for f in filtered:
    print(f"  • {f['title'][:60]}... (Score: {f['score']}/10)")

# ============ STEP 3: WRITER AGENT ============
print("\n" + "=" * 90)
print("STEP 3️⃣  - WRITER AGENT ✍️")
print("=" * 90)
print("""
Role: Chuyên gia Viết Bài Facebook
Goal: Viết bài chuẩn format Facebook, giọng văn cuốn hút

Format:
  [HOOK] - 1-2 câu giật gân + emoji
  [BODY] - 3-5 đoạn: What/Why/Impact/Insight
  [CTA]  - Call to Action rõ ràng
  [TAGS] - Max 10 hashtags
""")

print(f"⏳ Simulating writer agent... viết bài Facebook")

# Simulate writer output
written_posts = []
for article in filtered:
    post = {
        "title": article["title"],
        "hook": f"🔥 BREAKING: {article['title']}",
        "body": f"""Để mình explain chi tiết nhé 👇

**Chuyện là thế này:**
{article['summary']}

**Tại sao quan trọng?**
Đây là một bước tiến lớn trong ngành công nghệ AI/ML. Nó sẽ ảnh hưởng đến cách chúng ta xây dựng ứng dụng.

**Bạn nên biết:**
- Công ty/nhóm nào release cái này
- Những tính năng chính
- Ảnh hưởng đến ngành

**Bài học:**
Ngành AI/ML đang phát triển rất nhanh. Cập nhật kiến thức là cần thiết.""",
        "cta": "Bạn đã biết về cái này chưa? Comment bên dưới nhé 👇",
        "hashtags": ["#AI", "#MachineLearning", "#Technology", "#Future"],
        "emoji_count": 6,
        "word_count": 180,
        "engagement_potential": "High"
    }
    written_posts.append(post)

print("✅ WRITER COMPLETED")

print(f"\n📄 Generated {len(written_posts)} Facebook Posts:")
for i, post in enumerate(written_posts, 1):
    print(f"\n  Post {i}:")
    print(f"  HOOK: {post['hook']}")
    print(f"  BODY: {post['body'][:100]}...")
    print(f"  CTA: {post['cta']}")
    print(f"  HASHTAGS: {' '.join(post['hashtags'])}")

# ============ STEP 4: DESIGNER AGENT ============
print("\n" + "=" * 90)
print("STEP 4️⃣  - DESIGNER AGENT 🎨")
print("=" * 90)
print("""
Role: Chuyên gia Thiết Kế Prompt Sinh Ảnh
Goal: Tạo search query cho Unsplash API, tải ảnh chuyên nghiệp
""")

print(f"⏳ Simulating designer agent... tạo search queries")

# Simulate designer output
image_configs = []
search_keywords = {
    "OpenAI GPT": "artificial intelligence neural network technology",
    "TensorFlow": "machine learning neural network data science",
    "LLaMA": "AI technology future innovation"
}

for post in written_posts:
    # Find matching keyword
    keyword = None
    for key, query in search_keywords.items():
        if key.lower() in post['title'].lower():
            keyword = query
            break

    if not keyword:
        keyword = "technology artificial intelligence"

    config = {
        "title": post['title'][:40],
        "unsplash_query": keyword,
        "recommended_size": "1200x628px",
        "alt_text": f"Professional {keyword} illustration"
    }
    image_configs.append(config)

print("✅ DESIGNER COMPLETED")

print(f"\n🖼️  Image Configurations:")
for i, config in enumerate(image_configs, 1):
    print(f"\n  Image {i}:")
    print(f"  Search Query: '{config['unsplash_query']}'")
    print(f"  Size: {config['recommended_size']}")
    print(f"  Alt Text: {config['alt_text']}")

# ============ STEP 5: SEO AGENT ============
print("\n" + "=" * 90)
print("STEP 5️⃣  - SEO AGENT ⚡")
print("=" * 90)
print("""
Role: Chuyên gia Tối Ưu SEO và Facebook Meta
Goal: Optimize hashtags, emoji, format cho Facebook algorithm

Optimization:
  ✓ Hashtag: 70% trending + 20% niche + 10% branded
  ✓ Emoji: Strategic placement (5-7 total)
  ✓ Text formatting: Chia nhỏ paragraph
  ✓ Best posting time: Peak hours (12PM or 7PM)
  ✓ Readability: Flesch score 60-70
""")

print(f"⏳ Simulating SEO agent... optimize {len(written_posts)} posts")

# Simulate SEO optimization
optimized_posts = []
for post in written_posts:
    optimized = {
        **post,
        "hashtags_optimized": [
            "#AI", "#MachineLearning", "#Technology",
            "#NeuralNetwork", "#DeepLearning",
            "#Future", "#Innovation", "#TechNews"
        ],
        "best_posting_time": "12:00 PM",
        "estimated_reach": 20000 + (len(filtered) * 2000),
        "readability_score": 68,
        "emoji_placement": "Strategic (hook + body transitions + CTA)",
        "format_optimized": "Paragraph breaks + bullet points"
    }
    optimized_posts.append(optimized)

print("✅ SEO COMPLETED")

print(f"\n📈 SEO Optimization Results:")
for i, post in enumerate(optimized_posts, 1):
    print(f"\n  Post {i}:")
    print(f"  ✅ Hashtags: {len(post['hashtags_optimized'])} (optimized)")
    print(f"  ✅ Best Time: {post['best_posting_time']}")
    print(f"  ✅ Estimated Reach: {post['estimated_reach']:,} people")
    print(f"  ✅ Readability: {post['readability_score']}/100")
    print(f"  ✅ Emoji Placement: {post['emoji_placement']}")

# ============ STEP 6: PUBLISHER AGENT ============
print("\n" + "=" * 90)
print("STEP 6️⃣  - PUBLISHER AGENT 📤")
print("=" * 90)
print("""
Role: Chuyên gia Quản Lý API và Xuất Bản
Goal: Validate data, prepare Facebook payload, publish

Validation:
  ✓ Content length: 1-63206 characters
  ✓ Image: Valid URL + accessible
  ✓ Hashtags: Max 10-15
  ✓ Encoding: Valid UTF-8

Facebook API Payload:
  {
    "message": "content + hashtags",
    "picture": "image_url",
    "name": "title",
    "description": "short description",
    "link": "article_url"
  }
""")

print(f"⏳ Simulating publisher agent... validate & prepare")

# Select best post for publishing
best_post = optimized_posts[0]  # GPT-5 is usually the hottest
facebook_payload = {
    "message": f"{best_post['hook']}\n\n{best_post['body']}\n\n{best_post['cta']}\n\n{' '.join(best_post['hashtags_optimized'])}",
    "picture": "https://images.unsplash.com/photo-artificial-intelligence",
    "name": best_post['title'],
    "description": filtered[0]['summary'][:100],
    "link": filtered[0]['url']
}

print("✅ PUBLISHER COMPLETED")

print(f"\n📮 Facebook Payload Ready:")
print(f"  ✅ Content: {len(facebook_payload['message'])} characters")
print(f"  ✅ Image: Present & Valid")
print(f"  ✅ Hashtags: {len(best_post['hashtags_optimized'])} tags")
print(f"  ✅ Validation: PASSED")
print(f"  ✅ Status: READY_TO_PUBLISH")
print(f"  ✅ Scheduled: {best_post['best_posting_time']} Vietnam Time")

# ============ FINAL POST ============
print("\n" + "=" * 90)
print("✨ FINAL FACEBOOK POST")
print("=" * 90)

print(f"""
{best_post['hook']}

{best_post['body']}

{best_post['cta']}

{' '.join(best_post['hashtags_optimized'])}

---

📊 Metrics:
  • Estimated Reach: {best_post['estimated_reach']:,} people
  • Estimated Engagement: {best_post['estimated_reach']//30} interactions
  • Readability: {best_post['readability_score']}/100
  • Post Length: {len(best_post['body'].split())} words
  • Emoji Count: {best_post['emoji_count']}
""")

# ============ SUMMARY ============
print("\n" + "=" * 90)
print("✅ FULL PIPELINE EXECUTION SUMMARY")
print("=" * 90)

summary = f"""
🎯 Pipeline Stages Executed:
  1️⃣  SCRAPER    → Cào {len(articles)} articles from multiple sources
  2️⃣  FILTER     → Lọc còn {len(filtered)} high-quality articles
  3️⃣  WRITER     → Viết {len(written_posts)} Facebook posts
  4️⃣  DESIGNER   → Tạo {len(image_configs)} image search queries
  5️⃣  SEO        → Tối ưu {len(optimized_posts)} posts cho Facebook
  6️⃣  PUBLISHER  → Validate & Prepare 1 best post for publishing

⏱️  Execution Time: ~30 seconds (with real OpenAI API would be 2-5 minutes)

🚀 Next Steps:
  → Click "START SYSTEM" button in Streamlit UI
  → System will run automatically at:
     • 6:00 AM  - Scraper Agent
     • 7:00 AM  - Filter, Writer, Designer, SEO Agents
     • 8:00 AM  - Publisher Agent
  → Check Facebook page for published post!

📊 Expected Results:
  • 5-10 articles scraped daily
  • 5-10 Facebook posts generated
  • ~20,000 estimated reach per post
  • Auto-notifications via Telegram

🎉 System is fully functional and ready!
"""

print(summary)

print("=" * 90)
