from src.workflows import FacebookContentPipeline

print("Running full pipeline...")
pipeline = FacebookContentPipeline()
result = pipeline.run_full_pipeline()

print("\nPipeline result:")
print(result)

# Check database
import sqlite3
conn = sqlite3.connect("facebook_automation.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM posts")
posts = cursor.fetchone()[0]
print(f"\nTotal posts: {posts}")

if posts > 0:
    cursor.execute("SELECT hook, body, image_url FROM posts ORDER BY created_at DESC LIMIT 1")
    result = cursor.fetchone()
    print("\n" + "="*60)
    print("HOOK:")
    print(result[0])
    print("\nBODY:")
    print(result[1])
    print("\nIMAGE:")
    print(result[2])
    print("="*60)
else:
    print("No posts created")

conn.close()
