import sys
sys.path.insert(0, ".")
from src.agents.base import get_llm
from config.config import settings

print(f"Groq key: {settings.groq_api_key[:20]}...")

llm = get_llm(use_large=False)
print(f"Model: {llm.model_name}")

result = llm.invoke("Viết 1 câu về AI bằng tiếng Việt.")
print(f"\n✅ Groq trả lời:\n{result.content}")
