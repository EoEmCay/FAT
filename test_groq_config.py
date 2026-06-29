import sys
sys.path.insert(0, ".")
from src.agents.base import get_llm
from config.config import settings

print("Config OK")
print(f"Groq key : {'SET' if settings.groq_api_key else 'empty — can dien'}")
print(f"Ollama   : {settings.ollama_host} (fallback local)")
llm = get_llm()
base = getattr(llm, "openai_api_base", None) or "openai default"
print(f"Active LLM: {llm.model_name} | {base}")
