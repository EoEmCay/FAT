"""
Agent 6: Publisher Agent
Chọn bài tốt nhất từ SEO output và đăng lên Facebook Graph API.
Không dùng LLM — Python thuần để tránh AI trả JSON sai format.
"""

import logging
import json
import requests
from datetime import datetime
from typing import Dict, Any
from src.agents.base import extract_json
from config.config import settings

logger = logging.getLogger(__name__)


class PublisherAgent:
    """Agent 6 — Validate và xuất bản lên Facebook"""

    @staticmethod
    def run(optimized_posts_json: str, images_json: str) -> str:
        """
        Chọn bài tốt nhất từ SEO Agent output và build Facebook payload.
        Parse JSON trực tiếp, không qua LLM.
        """
        logger.info("📤 PublisherAgent running...")

        posts = extract_json(optimized_posts_json, expect_array=True)
        images = extract_json(images_json, expect_array=True) or []

        if not posts:
            logger.error("❌ Không parse được SEO output")
            return json.dumps({"status": "failed", "error": "Cannot parse SEO output"})

        # Lọc bài có optimized_content
        valid = [p for p in posts if p.get("optimized_content")]
        if not valid:
            logger.error("❌ Không có bài nào có optimized_content")
            return json.dumps({"status": "failed", "error": "No valid optimized_content"})

        # Chọn bài estimated_reach cao nhất
        best = max(valid, key=lambda p: p.get("estimated_reach", 0))

        content = best["optimized_content"]

        # Ghép hashtags vào cuối nếu chưa có trong content
        hashtags = best.get("hashtags_optimized", [])
        if hashtags and not any(h in content for h in hashtags):
            content += "\n\n" + " ".join(hashtags)

        # Lấy ảnh đầu tiên nếu có
        picture = None
        if images and isinstance(images[0], dict):
            picture = images[0].get("url") or images[0].get("local_path")

        payload = {
            "status": "ready_to_publish",
            "selected_article_url": best.get("article_url", ""),
            "validation_result": "passed",
            "facebook_payload": {
                "message": content[:63000],
                "link": best.get("article_url") or "",
                "picture": picture,
                "name": content.split("\n")[0][:100],
                "description": content[:200],
            },
            "estimated_reach": best.get("estimated_reach", 0),
            "estimated_engagement": int(best.get("estimated_reach", 0) * 0.025),
        }

        logger.info("✅ PublisherAgent: payload built successfully")
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    async def publish_to_facebook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Gọi Facebook Graph API để đăng bài."""
        if "test" in settings.facebook_access_token or len(settings.facebook_access_token) < 30:
            logger.warning("⚠️  Facebook token là test token, bỏ qua gọi API thật")
            return {
                "status": "skipped",
                "reason": "test token — cần Facebook Access Token thật",
                "payload_preview": str(payload)[:200],
            }

        try:
            logger.info("📤 Calling Facebook Graph API...")

            url = (
                f"https://graph.facebook.com/"
                f"{settings.facebook_api_version}/"
                f"{settings.facebook_page_id}/feed"
            )
            # Dùng access_token trong body + form-encoded (cách duy nhất đã test thành công)
            post_data = {k: v for k, v in payload.items() if v}
            post_data["access_token"] = settings.facebook_access_token

            resp = requests.post(url, data=post_data, timeout=30)

            if resp.status_code in (200, 201):
                post_id = resp.json().get("id")
                logger.info(f"✅ Published! Post ID: {post_id}")
                return {
                    "status": "published",
                    "post_id": post_id,
                    "facebook_url": f"https://facebook.com/{post_id}",
                    "published_at": datetime.now().isoformat(),
                }
            else:
                error = resp.json().get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ Facebook API error: {error}")
                return {"status": "failed", "error": error, "http_status": resp.status_code}

        except Exception as e:
            logger.error(f"❌ publish_to_facebook exception: {e}")
            return {"status": "error", "error": str(e)}
