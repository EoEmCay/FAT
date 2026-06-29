"""
Test Writer Agent - Xem AI viết bài như thế nào
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.writer_agent import WriterAgent
from langchain_openai import ChatOpenAI
from config.config import settings
import json

# Sample articles để test
sample_articles = """
1. Anthropic Releases Claude 4 Model - More Powerful AI
   URL: https://anthropic.com/news/claude-4
   Summary: Anthropic vừa công bố Claude 4, mô hình AI mạnh hơn với khả năng xử lý 200k tokens.

2. OpenAI Announces GPT-5 in Development
   URL: https://openai.com/news/gpt5
   Summary: OpenAI công bố đang phát triển GPT-5 với tính năng reasoning cao cấp hơn.
"""

def test_writer():
    """Test Writer Agent"""
    print("="*70)
    print("🤖 AI WRITER AGENT TEST")
    print("="*70)

    # Check OpenAI API key
    if not settings.openai_api_key:
        print("\n⚠️  OPENAI_API_KEY không được set trong .env")
        print("\n📝 Để enable AI Writer, bạn cần:")
        print("   1. Tạo OpenAI account tại https://platform.openai.com")
        print("   2. Tạo API key")
        print("   3. Thêm vào .env:")
        print("      OPENAI_API_KEY=sk-your_key_here")
        print("\n💡 Nếu không muốn dùng OpenAI, bạn có thể:")
        print("   - Dùng Ollama (local AI, free)")
        print("   - Dùng LLaMA2 model")
        return

    print("\n✅ OPENAI_API_KEY được set")
    print(f"📊 Model: {settings.openai_model}")

    try:
        print("\n" + "-"*70)
        print("🔄 Tạo Writer Agent...")
        writer = WriterAgent.create()
        print("✅ Writer Agent created")

        print("\n" + "-"*70)
        print("📝 Sample Articles:")
        print(sample_articles)

        print("\n" + "-"*70)
        print("🚀 Generating Facebook posts...")
        print("-"*70)

        # Create task
        task = WriterAgent.create_task(sample_articles)
        print(f"\n📋 Task Description:\n{task.description[:500]}...")

        print("\n💭 Running Writer Agent (this may take a moment)...")
        print("(CrewAI is processing your content...)\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n📝 Có thể bạn cần:")
        print("   1. Thiết lập OPENAI_API_KEY")
        print("   2. Kiểm tra kết nối internet")
        print("   3. Kiểm tra quota OpenAI")

if __name__ == "__main__":
    test_writer()
