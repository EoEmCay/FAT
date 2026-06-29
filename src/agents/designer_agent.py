"""
Agent 4: Design & Prompt Engineer
Tạo ảnh infographic theo phong cách "Genz Yêu Công Nghệ" bằng Pollinations AI.
Fallback sang Unsplash / Pexels nếu cần.
"""

import logging
import asyncio
import os
import re
import urllib.parse
import requests
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm, extract_json
from config.config import settings, PROJECT_ROOT

logger = logging.getLogger(__name__)

AIIMG_DIR = os.path.join(PROJECT_ROOT, "AIimg")
os.makedirs(AIIMG_DIR, exist_ok=True)


# ── SYSTEM / TASK PROMPT ───────────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là Chuyên gia Thiết kế và Sáng tạo Nội dung cho Fanpage "Genz Yêu Công Nghệ".
Nhiệm vụ: dựa vào bài viết, tạo Image Prompt chi tiết cho Pollinations AI và search query dự phòng.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách bài viết dưới đây, tạo prompt ảnh infographic:

{posts}

Với MỖI bài viết, phân tích và điền vào:

ACCENT_COLOR: chọn 1 trong [terracotta orange | clay blue | sage green | dusty purple] — phù hợp chủ đề
METAPHOR: ý tưởng hình ảnh hình học ẩn dụ ngắn gọn (ví dụ: "a brain connected to circuit nodes", "staircase rising to a glowing summit", "interconnected hexagons forming a network")
CARD_COUNT: số bước/điểm chính trong bài (từ 4 đến 8)
TITLE_EN: tiêu đề bài dịch sang tiếng Anh, ngắn gọn (tối đa 8 từ)

Tạo pollinations_prompt theo đúng template (tiếng Anh):
"An editorial style tech infographic for a Facebook page branded 'Genz Yeu Cong Nghe'. Top header features the title '[TITLE_EN]' in elegant serif typography, with 'Genz Yeu Cong Nghe' subtext and a minimalist tech icon. Clean bright warm beige background (hex #FAF7F0). On the left, a large rounded-corner rectangle card in [ACCENT_COLOR] featuring an abstract minimalist line art illustration combining geometric shapes (circles, triangles, squares) representing [METAPHOR]. On the right, a neat vertical grid of [CARD_COUNT] small rounded white cards, each with a bold number (01, 02...) and clean sans-serif mini-text label. At the very bottom, a thin horizontal bar with a small lightbulb icon and a short one-line insight text. Clean layout, generous white space, studio lighting, flat vector graphic style, premium editorial corporate design, 8k resolution --ar 4:3"

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "title_en": "TITLE_EN đã chọn",
    "accent_color": "ACCENT_COLOR đã chọn",
    "metaphor": "METAPHOR đã chọn",
    "card_count": 5,
    "pollinations_prompt": "An editorial style tech infographic...(đầy đủ theo template)",
    "search_query": "2-4 từ tiếng Anh để tìm stock photo dự phòng",
    "alt_text": "Mô tả ảnh ngắn bằng tiếng Việt"
  }}
]

Chỉ trả về JSON, KHÔNG có text nào khác."""


# ── HELPER FUNCTIONS ───────────────────────────────────────────────────────

def _is_valid_key(key: str) -> bool:
    return bool(key) and key != "test_key" and len(key) > 10


def _save_image(image_url: str, label: str, source: str) -> str | None:
    """Download ảnh về AIimg/, trả về local path."""
    try:
        slug = re.sub(r"[^a-z0-9]+", "_", label.lower())[:30]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}_{source}_{slug}.jpg"
        filepath = os.path.join(AIIMG_DIR, filename)

        resp = requests.get(image_url, timeout=45, stream=True)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            logger.info(f"💾 Ảnh lưu: AIimg/{filename}")
            return filepath
    except Exception as e:
        logger.warning(f"⚠️ Không lưu được ảnh: {e}")
    return None


def _build_pollinations_url(prompt: str, headline: str) -> str:
    encoded = urllib.parse.quote(prompt)
    seed = abs(hash(headline)) % 999999
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1200&height=900&model=flux&nologo=true&seed={seed}"
    )


# ── DESIGNER AGENT ─────────────────────────────────────────────────────────

class DesignerAgent:
    """Agent 4 — Tạo ảnh infographic bằng Pollinations AI, fallback Unsplash/Pexels"""

    @staticmethod
    def run(posts_json: str) -> str:
        """Dùng LLM tạo pollinations_prompt + search_query cho từng bài."""
        logger.info("🎨 DesignerAgent running...")
        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])
        result = (prompt | llm).invoke({"posts": posts_json})
        logger.info("✅ DesignerAgent completed")
        return result.content

    @staticmethod
    async def download_images(image_configs: list, source: str = "unsplash",
                              blocks: list = None, headline: str = "") -> list:
        """
        Ưu tiên: Pollinations AI (dùng pollinations_prompt từ LLM)
        Fallback: Unsplash → Pexels
        """
        blocks = blocks or []
        if not image_configs:
            return []

        cfg0 = image_configs[0]
        pollinations_prompt = cfg0.get("pollinations_prompt", "")
        search_query = cfg0.get("search_query", "technology infographic")

        # ── 1. Pollinations AI ─────────────────────────────────────────────
        if pollinations_prompt:
            try:
                poll_url = _build_pollinations_url(pollinations_prompt, headline)
                logger.info(f"🎨 Pollinations: {pollinations_prompt[:100]}...")
                local_path = _save_image(poll_url, search_query, "pollinations")
                if local_path:
                    for cfg in image_configs:
                        cfg["image_url"] = poll_url
                        cfg["local_path"] = local_path
                        cfg["image_source"] = "pollinations_ai"
                    logger.info("✅ Ảnh AI từ Pollinations đã lưu vào AIimg/")
                    return image_configs
                else:
                    logger.warning("⚠️ Pollinations download thất bại — fallback stock photo")
            except Exception as e:
                logger.warning(f"⚠️ Pollinations exception: {e} — fallback stock photo")

        # ── 2. Unsplash / Pexels fallback ─────────────────────────────────
        use_source = source
        if use_source == "unsplash" and not _is_valid_key(settings.unsplash_access_key):
            use_source = "pexels" if _is_valid_key(settings.pexels_api_key) else None
        elif use_source == "pexels" and not _is_valid_key(settings.pexels_api_key):
            use_source = "unsplash" if _is_valid_key(settings.unsplash_access_key) else None

        if not use_source:
            logger.warning("⚠️ Không có stock photo key — bỏ qua tải ảnh")
            return image_configs

        logger.info(f"📸 Fallback: {use_source.capitalize()} ({search_query})")
        if use_source == "unsplash":
            return await DesignerAgent._fetch_unsplash(image_configs)
        return await DesignerAgent._fetch_pexels(image_configs)

    @staticmethod
    async def _fetch_unsplash(image_configs: list) -> list:
        updated = []
        for config in image_configs:
            query = config.get("search_query", "technology")
            try:
                resp = requests.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": query, "per_page": 1, "client_id": settings.unsplash_access_key},
                    timeout=10,
                )
                results = resp.json().get("results", [])
                if results:
                    url = results[0]["urls"]["regular"]
                    config["image_url"] = url
                    config["image_source"] = "unsplash"
                    config["local_path"] = _save_image(url, query, "unsplash")
                    logger.info(f"✅ Unsplash: {query}")
                else:
                    config["image_url"] = None
            except Exception as e:
                logger.error(f"❌ Unsplash error: {e}")
                config["image_url"] = None
            updated.append(config)
            await asyncio.sleep(0.3)
        return updated

    @staticmethod
    async def _fetch_pexels(image_configs: list) -> list:
        updated = []
        headers = {"Authorization": settings.pexels_api_key}
        for config in image_configs:
            query = config.get("search_query", "technology")
            try:
                resp = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": query, "per_page": 1},
                    headers=headers,
                    timeout=10,
                )
                photos = resp.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large"]
                    config["image_url"] = url
                    config["image_source"] = "pexels"
                    config["local_path"] = _save_image(url, query, "pexels")
                    logger.info(f"✅ Pexels: {query}")
                else:
                    config["image_url"] = None
            except Exception as e:
                logger.error(f"❌ Pexels error: {e}")
                config["image_url"] = None
            updated.append(config)
            await asyncio.sleep(0.3)
        return updated
