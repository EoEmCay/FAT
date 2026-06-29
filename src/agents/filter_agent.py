"""
Agent 2: Filter & Fact-Checker
Lọc tin, xác minh sự thật, và chọn bài viết giá trị cao
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là chuyên gia lọc tin và fact-checking công nghệ AI.
Nhiệm vụ: Chỉ giữ lại những bài viết chất lượng cao nhất.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách bài viết dưới đây, hãy lọc và xếp hạng:

{articles}

Thực hiện:
1. Loại bỏ bài duplicate (tiêu đề tương tự)
2. Loại bỏ bài không liên quan đến AI/Tech
3. Chấm điểm mỗi bài (0-10):
   - Trending: 0-5 (viral/hot topic)
   - Depth: 0-3 (technical depth)
   - Actionable: 0-2 (có thể áp dụng ngay)
4. Chỉ giữ lại bài có score >= 6

Trả về JSON array theo format:
[
  {{
    "title": "Tiêu đề",
    "url": "https://...",
    "summary": "Tóm tắt 2-3 câu cốt lõi",
    "why_important": "Tại sao bài này quan trọng với developer VN",
    "source": "medium",
    "score": 8,
    "verified": true,
    "tags": ["AI", "LLM"]
  }}
]

Chỉ trả về JSON, KHÔNG có text nào khác."""


class FilterAgent:
    """Agent 2 — Lọc tin và fact-check"""

    @staticmethod
    def run(articles_json: str) -> str:
        """
        Lọc articles, trả về JSON string của articles đã lọc.
        articles_json: JSON string từ ScraperAgent
        """
        logger.info("🔎 FilterAgent running...")

        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        chain = prompt | llm
        result = chain.invoke({"articles": articles_json})

        logger.info("✅ FilterAgent completed")
        return result.content
