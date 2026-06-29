"""
LangChain Workflow — Kết nối 6 agents theo pipeline tuần tự
Agent 1 → Agent 2 → Agent 3 → Agent 4+5 → Agent 6
Không dùng CrewAI, chỉ dùng LangChain + Python thuần
"""

import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from config.config import settings, TZ
from src.utils.logging import setup_logger
from src.agents.base import extract_json
from src.agents.scraper_agent import ScraperAgent
from src.agents.filter_agent import FilterAgent
from src.agents.writer_agent import WriterAgent
from src.agents.designer_agent import DesignerAgent
from src.agents.seo_agent import SEOAgent
from src.agents.publisher_agent import PublisherAgent

logger = setup_logger(__name__)


def _parse(text: str, expect_array: bool = True, fallback=None):
    """Wrapper: extract_json với log khi thất bại."""
    result = extract_json(text, expect_array=expect_array)
    if result is None:
        logger.warning(f"⚠️  JSON extract failed, raw: {text[:200]}")
        return fallback
    return result


class FacebookContentPipeline:
    """
    Pipeline chính — chạy 6 agents tuần tự.
    Mỗi agent nhận output của agent trước làm input.
    """

    def __init__(self):
        self.scraped_articles = None
        self.filtered_articles = None
        self.written_posts = None
        self.image_configs = None
        self.optimized_posts = None
        self.final_result = None

    async def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Chạy toàn bộ pipeline: Agent1 → 2 → 3 → 4+5 → 6

        Workflow:
          6:00 AM → Scraper
          7:00 AM → Filter → Writer → Designer → SEO → Publisher
          8:00 AM → Publisher gọi Facebook API

        Returns:
            dict: {status, post_id, facebook_url, ...}
        """
        logger.info("=" * 60)
        logger.info("🚀 FacebookContentPipeline starting...")
        logger.info("=" * 60)

        try:
            # ── AGENT 1: SCRAPER ──────────────────────────────────────
            logger.info("\n📍 [1/6] ScraperAgent — cào dữ liệu")
            raw_json = await asyncio.to_thread(ScraperAgent.run)
            self.scraped_articles = raw_json
            count = len(_parse(raw_json, fallback=[]))
            logger.info(f"✅ Scraper: {count} articles")

            # ── AGENT 2: FILTER ───────────────────────────────────────
            logger.info("\n📍 [2/6] FilterAgent — lọc & verify")
            filtered_json = await asyncio.to_thread(FilterAgent.run, raw_json)
            self.filtered_articles = filtered_json
            count = len(_parse(filtered_json, fallback=[]))
            logger.info(f"✅ Filter: {count} articles sau khi lọc")

            # ── AGENT 3: WRITER ───────────────────────────────────────
            logger.info("\n📍 [3/6] WriterAgent — viết bài Facebook")
            written_json = await asyncio.to_thread(WriterAgent.run, filtered_json)
            self.written_posts = written_json
            count = len(_parse(written_json, fallback=[]))
            logger.info(f"✅ Writer: {count} bài viết")

            # ── AGENT 4: DESIGNER ─────────────────────────────────────
            logger.info("\n📍 [4/6] DesignerAgent — tạo search query + tải ảnh")
            design_json = await asyncio.to_thread(DesignerAgent.run, written_json)
            design_configs = _parse(design_json, fallback=[])
            if design_configs:
                self.image_configs = await DesignerAgent.download_images(design_configs)
            else:
                self.image_configs = []
            logger.info(f"✅ Designer: {len(self.image_configs)} images")

            # ── AGENT 5: SEO ──────────────────────────────────────────
            logger.info("\n📍 [5/6] SEOAgent — tối ưu hashtag & format")
            optimized_json = await asyncio.to_thread(SEOAgent.run, written_json)
            self.optimized_posts = optimized_json
            count = len(_parse(optimized_json, fallback=[]))
            logger.info(f"✅ SEO: {count} bài đã optimize")

            # ── AGENT 6: PUBLISHER ────────────────────────────────────
            logger.info("\n📍 [6/6] PublisherAgent — validate & publish")
            images_json = json.dumps(self.image_configs)
            payload_json = await asyncio.to_thread(
                PublisherAgent.run, optimized_json, images_json
            )
            payload_data = _parse(payload_json, expect_array=False, fallback={})

            if not payload_data or "facebook_payload" not in payload_data:
                logger.error("❌ Publisher không tạo được payload hợp lệ")
                return self._error_result("publisher", "No valid payload generated")

            # ── GỌI FACEBOOK API ──────────────────────────────────────
            logger.info("\n📍 Gọi Facebook Graph API...")
            fb_result = await PublisherAgent.publish_to_facebook(
                payload_data["facebook_payload"]
            )

            if fb_result["status"] in ("published", "skipped"):
                logger.info(f"✅ Pipeline hoàn tất! Status: {fb_result['status']}")
                return {
                    "status": "success",
                    "pipeline_completed": True,
                    "post_id": fb_result.get("post_id"),
                    "facebook_url": fb_result.get("facebook_url"),
                    "published_at": fb_result.get("published_at", datetime.now(TZ).isoformat()),
                    "estimated_reach": payload_data.get("estimated_reach", 0),
                    "note": fb_result.get("reason", ""),
                }
            else:
                logger.error(f"❌ Facebook publish thất bại: {fb_result.get('error')}")
                return self._error_result("facebook_api", fb_result.get("error", "Unknown"))

        except Exception as e:
            logger.error(f"❌ Pipeline exception: {e}", exc_info=True)
            return self._error_result("unknown", str(e))

    def _error_result(self, stage: str, message: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "pipeline_completed": False,
            "failed_at_stage": stage,
            "error": message,
        }
