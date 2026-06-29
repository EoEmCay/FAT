import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect("facebook_automation.db")
cursor = conn.cursor()

post_id = str(uuid.uuid4())

query = """
    INSERT INTO posts (
        id, title, hook, body, insight, cta, hashtags,
        image_url, status, posted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

data = (
    post_id,
    "AI Breakthrough",
    "BREAKING: AI Model Shows 95% Accuracy",
    "New AI model demonstrates remarkable accuracy in market prediction.",
    "This represents a major step forward in AI capabilities.",
    "What do you think? Comment below",
    "#AI #MachineLearning #Technology",
    "https://images.unsplash.com/photo-sample",
    "draft",
    datetime.now()
)

cursor.execute(query, data)

if result:
    print("SUCCESS!")
    print("Title: " + str(result[0]))
    print("Hook: " + str(result[1]))
    print("Body: " + str(result[2]))
else:
    print("Error")

conn.close()
