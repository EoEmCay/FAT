import sys
sys.path.insert(0, ".")

print("=== Checking all imports ===\n")

from src.agents.base import get_llm
print("[OK] base.get_llm")

from src.agents.scraper_agent import ScraperAgent
print("[OK] ScraperAgent")

from src.agents.filter_agent import FilterAgent
print("[OK] FilterAgent")

from src.agents.writer_agent import WriterAgent
print("[OK] WriterAgent")

from src.agents.designer_agent import DesignerAgent
print("[OK] DesignerAgent")

from src.agents.seo_agent import SEOAgent
print("[OK] SEOAgent")

from src.agents.publisher_agent import PublisherAgent
print("[OK] PublisherAgent")

from src.workflows import FacebookContentPipeline
print("[OK] FacebookContentPipeline")

from src.orchestrator import orchestrator
print("[OK] Orchestrator")

print()
print("=== LLM config ===")
llm = get_llm()
print(f"Model: {llm.model_name}")
base = getattr(llm, "openai_api_base", None) or getattr(llm, "base_url", "default openai")
print(f"Base URL: {base}")

print()
print("=== All imports OK — No CrewAI needed! ===")
