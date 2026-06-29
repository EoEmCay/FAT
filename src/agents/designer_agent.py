"""
Agent 4: Design & Prompt Engineer
Tạo search query và tải ảnh — xen kẽ Unsplash (run1) và Pexels (run2)
"""

import logging
import asyncio
import os
import re
import requests
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm
from config.config import settings, PROJECT_ROOT

logger = logging.getLogger(__name__)

AIIMG_DIR = os.path.join(PROJECT_ROOT, "AIimg")
os.makedirs(AIIMG_DIR, exist_ok=True)


def _save_image(image_url: str, query: str, source: str) -> str | None:
    """Download ảnh từ URL về thư mục AIimg/, trả về local path."""
    try:
        slug = re.sub(r"[^a-z0-9]+", "_", query.lower())[:30]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}_{source}_{slug}.jpg"
        filepath = os.path.join(AIIMG_DIR, filename)

        resp = requests.get(image_url, timeout=15, stream=True)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            logger.info(f"💾 Ảnh lưu: AIimg/{filename}")
            return filepath
    except Exception as e:
        logger.warning(f"⚠️ Không lưu được ảnh: {e}")
    return None

SYSTEM_PROMPT = """Bạn là prompt engineer chuyên tạo search query cho stock photo.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách bài viết dưới đây, tạo search query để tìm ảnh:

{posts}

Với MỖI bài viết, tạo 1 search query phù hợp:
- Phân tích chủ đề chính của bài
- Tạo query 2-4 từ tiếng Anh
- Query phải tìm được ảnh thực tế (không quá đặc biệt)

Ví dụ tốt: "artificial intelligence technology", "machine learning neural network"
Ví dụ xấu: "gpt5 openai robot typing" (quá cụ thể)

Trả về JSON array:
[
  {{
    "article_url": "url nguồn",
    "search_query": "artificial intelligence technology",
    "alt_text": "Mô tả ảnh ngắn gọn bằng tiếng Việt"
  }}
]

Chỉ trả về JSON, KHÔNG có text nào khác."""


def _is_valid_key(key: str) -> bool:
    return bool(key) and key != "test_key" and len(key) > 10


class DesignerAgent:
    """Agent 4 — Tạo search query và tải ảnh (Unsplash hoặc Pexels)"""

    @staticmethod
    def run(posts_json: str) -> str:
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
    async def download_images(image_configs: list, source: str = "unsplash") -> list:
        """
        Tải ảnh từ Unsplash hoặc Pexels.
        source: "unsplash" | "pexels"
        Tự động fallback sang source còn lại nếu key thiếu.
        """
        # Chọn nguồn, fallback nếu key không hợp lệ
        use_source = source
        if use_source == "unsplash" and not _is_valid_key(settings.unsplash_access_key):
            if _is_valid_key(settings.pexels_api_key):
                logger.warning("⚠️  Unsplash key chưa set, fallback sang Pexels")
                use_source = "pexels"
            else:
                logger.warning("⚠️  Cả 2 key chưa set, bỏ qua tải ảnh")
                for c in image_configs:
                    c["image_url"] = None
                return image_configs
        elif use_source == "pexels" and not _is_valid_key(settings.pexels_api_key):
            if _is_valid_key(settings.unsplash_access_key):
                logger.warning("⚠️  Pexels key chưa set, fallback sang Unsplash")
                use_source = "unsplash"
            else:
                logger.warning("⚠️  Cả 2 key chưa set, bỏ qua tải ảnh")
                for c in image_configs:
                    c["image_url"] = None
                return image_configs

        logger.info(f"📸 Downloading {len(image_configs)} images from {use_source.capitalize()}...")

        if use_source == "unsplash":
            return await DesignerAgent._fetch_unsplash(image_configs)
        else:
            return await DesignerAgent._fetch_pexels(image_configs)

    @staticmethod
    async def _fetch_unsplash(image_configs: list) -> list:
        updated = []
        for config in image_configs:
            query = config.get("search_query") or config.get("unsplash_search_query", "technology")
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
                    logger.warning(f"⚠️  Unsplash no result: {query}")
            except Exception as e:
                logger.error(f"❌ Unsplash error ({query}): {e}")
                config["image_url"] = None
            updated.append(config)
            await asyncio.sleep(0.3)
        return updated

    @staticmethod
    async def _fetch_pexels(image_configs: list) -> list:
        updated = []
        headers = {"Authorization": settings.pexels_api_key}
        for config in image_configs:
            query = config.get("search_query") or config.get("unsplash_search_query", "technology")
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
                    logger.warning(f"⚠️  Pexels no result: {query}")
            except Exception as e:
                logger.error(f"❌ Pexels error ({query}): {e}")
                config["image_url"] = None
            updated.append(config)
            await asyncio.sleep(0.3)
        return updated
