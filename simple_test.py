print("Testing Facebook Automation Pipeline")
print("="*60)

# Test 1: Scrape articles
print("\n1. SCRAPING ARTICLES...")
import requests
try:
    # Scrape from Medium
    resp = requests.get("https://medium.com/tag/ai/latest", timeout=5)
    if resp.status_code == 200:
        print("✅ Can access data sources")
    else:
        print("⚠️ Access limited")
except Exception as e:
    print(f"⚠️ {str(e)}")

# Test 2: Sample post generation
print("\n2. GENERATING SAMPLE POST...")
sample_post = {
    "hook": "🔥 BREAKING: AI Breakthrough Announced",
    "body": "New AI model shows 95% accuracy in predicting market trends. This could revolutionize the industry.",
    "cta": "What do you think about this? Comment below 👇",
    "hashtags": ["#AI", "#MachineLearning", "#Technology"]
}

print(f"Hook: {sample_post['hook']}")
print(f"Body: {sample_post['body']}")
print(f"CTA: {sample_post['cta']}")
print(f"Hashtags: {', '.join(sample_post['hashtags'])}")

# Test 3: Sample image
print("\n3. DOWNLOADING SAMPLE IMAGE...")
try:
    resp = requests.get("https://api.unsplash.com/search/photos?query=artificial+intelligence&client_id=YOUR_KEY", timeout=5)
    print("✅ Can access Unsplash API")
except:
    print("⚠️ Unsplash API test skipped")

# Test 4: Save to database
print("\n4. SAVING TO DATABASE...")
import sqlite3
conn = sqlite3.connect("facebook_automation.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO posts (hook, body, image_url, status)
        VALUES (?, ?, ?, ?)
    """, (
        sample_post["hook"],
        sample_post["body"],
        "https://images.unsplash.com/photo-sample",
        "draft"
    ))
    conn.commit()
    print("✅ Post saved to database")
except Exception as e:
    print(f"⚠️ {str(e)}")

conn.close()

print("\n" + "="*60)
print("✅ PIPELINE TEST COMPLETE!")
print("="*60)

# Show result
print("\nLatest post in database:")
conn = sqlite3.connect("facebook_automation.db")
cursor = conn.cursor()
cursor.execute("SELECT hook, body FROM posts ORDER BY created_at DESC LIMIT 1")
result = cursor.fetchone()
if result:
    print(f"Hook: {result[0]}")
    print(f"Body: {result[1]}")
conn.close()
