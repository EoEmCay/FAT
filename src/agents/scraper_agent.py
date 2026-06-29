"""
Agent 1: Scraper & Trend Hunter
Cào dữ liệu từ các nguồn tin tức và xu hướng công nghệ
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là chuyên gia thu thập dữ liệu AI và công nghệ.
Nhiệm vụ: Tổng hợp những tin tức nóng nhất trong 7 ngày qua.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Hãy tạo danh sách 10 bài viết công nghệ AI đang trending hiện nay.

Trả về JSON array theo đúng format sau:
[
  {{
    "source": "medium",
    "title": "Tiêu đề bài viết",
    "url": "https://...",
    "summary": "Tóm tắt 1-2 câu về nội dung bài viết",
    "published_at": "2026-06-29",
    "views": 50000,
    "tags": ["AI", "LLM"]
  }}
]

Yêu cầu:
- source phải là một trong: medium, github, huggingface, devto, arxiv
- Chủ đề xoay quanh: AI, LLM, Machine Learning, Deep Learning, Python
- views phải là số thực tế (10000-500000)
- Mỗi bài phải có summary khác nhau
- Trả về đúng 10 bài, KHÔNG có text nào ngoài JSON"""


class ScraperAgent:
    """Agent 1 — Cào & tổng hợp dữ liệu"""

    @staticmethod
    def run() -> str:
        """Chạy agent, trả về JSON string của articles."""
        logger.info("🔍 ScraperAgent running...")

        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        chain = prompt | llm
        result = chain.invoke({})

        logger.info("✅ ScraperAgent completed")
        return result.content
