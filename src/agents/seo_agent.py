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

TASK_PROMPT = """Tối ưu các bài viết Facebook dạng INFOGRAPHIC STRUCTURED sau:

{posts}

Với MỖI bài, ghép nội dung hoàn chỉnh theo format:

[HEADLINE]
[BLOCK 01] icon + title
• bullet 1
• bullet 2
• bullet 3
➤ metric

[BLOCK 02] icon + title
...

[SUMMARY]
[CTA]

Sau đó tối ưu:
1. HASHTAGS: 7-10 hashtag gồm trending + niche + local Vietnamese
2. BEST TIME: giờ đăng tốt nhất cho fanpage công nghệ Việt Nam
3. ESTIMATED REACH: ước tính reach dựa trên chủ đề

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "optimized_content": "Toàn bộ nội dung bài đã format — headline + blocks + summary + cta",
    "hashtags_optimized": ["#AI", "#TríTuệNhânTạo", "#GenZYêuCôngNghệ"],
    "best_posting_time": "17:00",
    "estimated_reach": 25000,
    "readability_score": 85
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
