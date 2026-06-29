"""
Agent 5: SEO & Meta Optimizer
Tối ưu hashtag, định dạng, và metadata cho Facebook algorithm
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là SEO expert chuyên tối ưu bài đăng cho Facebook algorithm.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Tối ưu các bài viết Facebook sau để đạt reach tối đa:

{posts}

Với MỖI bài viết, thực hiện:
1. HASHTAGS: Chọn 7-10 hashtag tối ưu gồm:
   - 70% trending: #AI #MachineLearning #Technology
   - 20% niche: #LLM #NeuralNetwork #DeepLearning
   - 10% local: #LapTrinhVietNam #AIVietNam
2. EMOJI: Đặt emoji chiến lược (tối đa 7 cái):
   - 🔥 trước trending
   - 💡 trước insight
   - 📊 trước số liệu
   - ⚡ trước benefit
3. FORMAT: Chia đoạn ngắn (2-3 câu/đoạn), dễ đọc trên mobile
4. BEST TIME: Xác định giờ đăng tốt nhất (12:00 PM hoặc 7:00 PM)

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "optimized_content": "Toàn bộ nội dung bài đã format đẹp",
    "hashtags_optimized": ["#AI", "#MachineLearning"],
    "best_posting_time": "12:00 PM",
    "estimated_reach": 20000,
    "readability_score": 70
  }}
]

Chỉ trả về JSON, KHÔNG có text nào khác."""


class SEOAgent:
    """Agent 5 — Tối ưu SEO và Facebook meta"""

    @staticmethod
    def run(posts_json: str) -> str:
        """
        Tối ưu posts, trả về JSON string.
        posts_json: JSON string từ WriterAgent
        """
        logger.info("⚡ SEOAgent running...")

        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        chain = prompt | llm
        result = chain.invoke({"posts": posts_json})

        logger.info("✅ SEOAgent completed")
        return result.content
