"""
Agent 3: Content Writer
Viết bài Facebook theo phong cách Infographic Structured Content
— Modular Grid Layout, Data-Driven, Vivid Color Psychology
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là Infographic Designer và Content Strategist với 10 năm kinh nghiệm.
Chuyên viết nội dung fanpage công nghệ dạng INFOGRAPHIC STRUCTURED — không viết bài văn dài.
Mỗi bài phải: scannable ngay trong 3 giây, có số liệu cụ thể, cấu trúc block rõ ràng.
Tone: Professional, Empowering, Practical. Dùng tiếng Việt.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách articles dưới đây, tạo bài Facebook post dạng INFOGRAPHIC STRUCTURED:

{filtered_articles}

Với MỖI bài, viết theo format INFOGRAPHIC:

━━━ HEADER (1 dòng, UPPERCASE, bold) ━━━
Headline lớn, súc tích, high-contrast. Ví dụ:
"🚀 AI THAY THẾ 300 TRIỆU VIỆC LÀM — ĐÂY LÀ NHỮNG GÌ BẠN CẦN BIẾT"

━━━ BODY (3-5 blocks dạng Step/Pillar/Rule) ━━━
Mỗi block gồm:
  [SỐ THỨ TỰ + ICON] TÊN BLOCK (bold, ngắn)
  • Bullet point 1 (có số liệu cụ thể nếu có)
  • Bullet point 2
  • Bullet point 3
  ➤ KẾT QUẢ/METRIC: [số liệu hoặc insight nổi bật]

Số lượng blocks linh hoạt theo chủ đề:
  - "3 Trụ Cột của..." → 3 blocks
  - "4 Bước để..." → 4 blocks
  - "5 Quy Tắc..." → 5 blocks

━━━ SUMMARY ROI BLOCK ━━━
📊 TÓM TẮT: [1-2 câu tổng kết insight quan trọng nhất]

━━━ CTA FOOTER (full-width) ━━━
1 câu kêu gọi + emoji mạnh

━━━ CAPTION + HASHTAGS ━━━
Caption ngắn 1-2 câu để đăng kèm + 5 hashtag

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "headline": "🚀 AI THAY THẾ 300 TRIỆU VIỆC LÀM — ĐÂY LÀ NHỮNG GÌ BẠN CẦN BIẾT",
    "blocks": [
      {{
        "number": "01",
        "icon": "🤖",
        "title": "TÌNH TRẠNG HIỆN TẠI",
        "bullets": ["GPT-4 xử lý 10 triệu request/ngày", "Chi phí giảm 80% so với nhân lực", "300 triệu việc làm bị ảnh hưởng"],
        "metric": "➤ KẾT QUẢ: 40% công việc văn phòng có thể tự động hóa"
      }},
      {{
        "number": "02",
        "icon": "💡",
        "title": "CƠ HỘI TRONG NGUY HIỂM",
        "bullets": ["Nghề mới: AI Trainer, Prompt Engineer", "Lương tăng 3x nếu biết dùng AI", "Thời điểm học AI tốt nhất là BÂY GIỜ"],
        "metric": "➤ KẾT QUẢ: 97 triệu việc làm mới sẽ xuất hiện"
      }}
    ],
    "summary": "📊 TÓM TẮT: AI không thay thế bạn — người biết dùng AI mới thay thế bạn.",
    "cta": "💬 Bạn đang làm nghề gì? Tag người bạn cần đọc bài này ngay! 👇",
    "caption": "AI đang reshape thị trường lao động. Đây là roadmap để bạn không bị bỏ lại phía sau.",
    "hashtags": ["#AI", "#TríTuệNhânTạo", "#CôngNghệ", "#GenZYêuCôngNghệ", "#ViệcLàmTươngLai"],
    "color_theme": "Cobalt Blue → Vibrant Orange (progression)"
  }}
]

Ràng buộc:
- Mỗi bullet PHẢI có số liệu cụ thể hoặc fact thực tế
- KHÔNG viết bài văn dài — chỉ blocks súc tích
- Dùng UPPERCASE cho tiêu đề blocks
- Chỉ trả về JSON, KHÔNG có text nào khác"""


class WriterAgent:
    """Agent 3 — Viết bài Facebook dạng Infographic Structured Content"""

    @staticmethod
    def run(filtered_articles_json: str) -> str:
        logger.info("✍️  WriterAgent (Infographic Style) running...")

        llm = get_llm(use_large=True)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        result = (prompt | llm).invoke({"filtered_articles": filtered_articles_json})

        logger.info("✅ WriterAgent completed")
        return result.content
