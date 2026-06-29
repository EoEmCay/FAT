"""
Agent 3: Content Writer
Viết bài Facebook chuyên nghiệp với giọng văn cuốn hút
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là copywriter chuyên viết bài Facebook cho Fanpage công nghệ 1 triệu followers.
Phong cách: chuyên nghiệp nhưng gần gũi, dùng tiếng Việt tự nhiên.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách bài viết dưới đây, viết bài Facebook post:

{filtered_articles}

Với MỖI bài, viết theo format:
- HOOK: 1-2 câu giật gân mở đầu (có emoji 🔥😱💡)
- BODY: 3-4 đoạn ngắn gồm: (1) Chuyện gì xảy ra, (2) Tại sao quan trọng, (3) Ảnh hưởng, (4) Góc nhìn
- CTA: 1 câu kêu gọi comment/share
- HASHTAGS: 5-8 hashtag liên quan

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "hook": "🔥 BREAKING: ...",
    "body": "Để mình explain...\n\nĐoạn 1...\n\nĐoạn 2...\n\nĐoạn 3...",
    "cta": "Bạn nghĩ sao về điều này? Comment bên dưới 👇",
    "hashtags": ["#AI", "#MachineLearning", "#Technology"],
    "word_count": 200,
    "emoji_count": 6
  }}
]

Ràng buộc:
- 150-250 từ mỗi bài
- 5-7 emoji, đặt đúng chỗ (không spam)
- Giọng gần gũi, dùng "bạn", "mình", "chúng ta"
- KHÔNG clickbait
- Chỉ trả về JSON, KHÔNG có text nào khác"""


class WriterAgent:
    """Agent 3 — Viết bài Facebook chuyên nghiệp"""

    @staticmethod
    def run(filtered_articles_json: str) -> str:
        """
        Viết bài Facebook, trả về JSON string của posts.
        filtered_articles_json: JSON string từ FilterAgent
        """
        logger.info("✍️  WriterAgent running...")

        # Writer dùng model lớn hơn để chất lượng cao hơn
        llm = get_llm(use_large=True)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        chain = prompt | llm
        result = chain.invoke({"filtered_articles": filtered_articles_json})

        logger.info("✅ WriterAgent completed")
        return result.content
