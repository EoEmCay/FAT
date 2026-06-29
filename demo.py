import sqlite3
import uuid
from datetime import datetime

print("="*60)
print("FACEBOOK AUTOMATION - DEMO")
print("="*60)

# Simulate pipeline
print("\n1. SCRAPER: Cào 50 articles...")
print("   ✅ Found 50 articles from Medium, GitHub, Hugging Face")

print("\n2. FILTER: Lọc tốt nhất...")
print("   ✅ Selected 8 best articles (score >= 6)")

print("\n3. WRITER: Viết bài...")
hook = "🔥 BREAKING: OpenAI Releases New AI Model"
body = """Để tôi explain:

Chuyện là thế này: OpenAI vừa release model mới với tính năng vượt trội.

Đoạn 1 - Cái gì xảy ra:
OpenAI công bố model mới có khả năng xử lý 100,000 tokens.

Đoạn 2 - Tại sao quan trọng:
Điều này tạo ra bước tiến lớn trong AI.

Đoạn 3 - Ảnh hưởng:
Developers có thể xây dựng ứng dụng phức tạp hơn."""
cta = "Bạn nghĩ sao? Comment bên dưới 👇"
hashtags = "#AI #OpenAI #MachineLearning #Technology"

print(f"   ✅ Generated post")
print(f"   Hook: {hook}")

print("\n4. DESIGNER: Tạo ảnh...")
print("   ✅ Downloaded from Unsplash")

print("\n5. SEO: Tối ưu...")
print("   ✅ Optimized hashtags, emoji, format")

print("\n6. PUBLISHER: Lưu vào database...")

# Save to DB
conn = sqlite3.connect("facebook_automation.db")
cursor = conn.cursor()

post_id = str(uuid.uuid4())

try:
    cursor.execute("""
        INSERT INTO posts (id, title, hook, body, insight, cta, hashtags, image_url, status, posted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post_id,
        "OpenAI Release",
        hook,
        body,
        "AI continues to advance rapidly",
        cta,
        hashtags,
        "https://images.unsplash.com/photo-ai",
        "draft",
        datetime.now()
    ))
    conn.commit()
    print("   ✅ Post saved!")
except Exception as e:
    print(f"   ⚠️ {str(e)}")

conn.close()

print("\n" + "="*60)
print("📝 RESULT:")
print("="*60)
print(f"Hook: {hook}")
print(f"\nBody:\n{body}")
print(f"\nCTA: {cta}")
print(f"Hashtags: {hashtags}")
print("\n" + "="*60)
print("✅ DEMO COMPLETE!")
print("="*60)
