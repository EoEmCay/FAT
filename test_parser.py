import sys
sys.path.insert(0, ".")
from src.agents.base import extract_json

PASS = 0
FAIL = 0

def check(label, result, expect_type, expect_len=None, expect_key=None):
    global PASS, FAIL
    ok = isinstance(result, expect_type)
    if ok and expect_len is not None:
        ok = len(result) == expect_len
    if ok and expect_key is not None:
        ok = expect_key in result
    status = "✅ PASS" if ok else "❌ FAIL"
    print(f"  {status}  {label}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
        print(f"         Got: {result}")

# ── TEST 1: Text thừa TRƯỚC JSON array (llama2 hay làm) ──────────
t1 = """Of course! Here are 10 trending AI articles:

[
  {"source": "medium", "title": "Why LLMs Are the Future", "url": "https://example.com", "views": 40000},
  {"source": "arxiv",  "title": "AI in Healthcare",        "url": "https://example2.com", "views": 25000}
]

Hope this helps!"""
r1 = extract_json(t1, expect_array=True)
check("Text trước + JSON array", r1, list, expect_len=2)

# ── TEST 2: Markdown code block ```json ... ``` ───────────────────
t2 = """Sure! Here is the result:
```json
[{"title": "Article 1", "score": 9}, {"title": "Article 2", "score": 7}]
```
That's all."""
r2 = extract_json(t2, expect_array=True)
check("Markdown ```json``` block", r2, list, expect_len=2)

# ── TEST 3: JSON object thuần túy ─────────────────────────────────
t3 = '{"status": "ready", "facebook_payload": {"message": "Hello world"}}'
r3 = extract_json(t3, expect_array=False)
check("Pure JSON object", r3, dict, expect_key="facebook_payload")

# ── TEST 4: Writer output thật của llama2 ─────────────────────────
t4 = """Great! Here are Facebook posts based on the articles:

Post 1:
[
  {
    "hook": "LLMs are revolutionizing AI!",
    "body": "Large language models are changing how we work.",
    "cta": "Click to learn more",
    "hashtags": ["#AI", "#ML"]
  }
]"""
r4 = extract_json(t4, expect_array=True)
check("llama2 Writer output thật", r4, list, expect_len=1)

# ── TEST 5: JSON thuần, không có text thừa ────────────────────────
t5 = '[{"title": "A"}, {"title": "B"}, {"title": "C"}]'
r5 = extract_json(t5, expect_array=True)
check("Pure JSON array (OpenAI format)", r5, list, expect_len=3)

# ── TEST 6: Text rác hoàn toàn, không có JSON ─────────────────────
t6 = "I'm sorry, I cannot provide that information."
r6 = extract_json(t6, expect_array=True)
check("Không có JSON (trả về None)", r6, type(None))

# ── SUMMARY ───────────────────────────────────────────────────────
print()
print(f"Kết quả: {PASS} PASS, {FAIL} FAIL")
if FAIL == 0:
    print("🎉 extract_json hoạt động với mọi format của AI!")
