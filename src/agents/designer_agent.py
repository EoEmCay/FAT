"""
Agent 4: Design Color Picker
Dùng LLM phân tích bài viết và chọn accent color phù hợp cho infographic.
Ảnh được vẽ bởi renderer.py (Pillow) — không dùng AI image gen.
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là designer phân tích nội dung và chọn màu sắc chủ đạo.
Luôn trả về JSON hợp lệ, không có text nào ngoài JSON."""

TASK_PROMPT = """Từ bài viết dưới đây, chọn accent color phù hợp nhất:

{posts}

Quy tắc chọn màu:
- Công nghệ, AI, tương lai, dữ liệu → "clay blue"
- Khởi nghiệp, thành công, growth, kinh doanh → "terracotta orange"
- Sức khỏe, môi trường, cân bằng, bền vững → "sage green"
- Sáng tạo, nghệ thuật, tư duy, giáo dục → "dusty purple"

Trả về JSON array, mỗi phần tử gồm:
[
  {{
    "article_url": "url bài gốc hoặc chuỗi rỗng",
    "accent_color": "terracotta orange",
    "search_query": "2-4 từ tiếng Anh mô tả chủ đề"
  }}
]

Chỉ trả JSON, không có text nào khác."""


class DesignerAgent:
    """Agent 4 — Chọn màu infographic dựa trên nội dung bài viết"""

    @staticmethod
    def run(posts_json: str) -> str:
        logger.info("🎨 DesignerAgent (color picker) running...")
        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])
        result = (prompt | llm).invoke({"posts": posts_json})
        logger.info("✅ DesignerAgent completed")
        return result.content
