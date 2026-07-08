"""
Agent 6: Publisher Agent
Chọn bài tốt nhất, upload ảnh lên Facebook, rồi đăng bài kèm ảnh.
Không dùng LLM — Python thuần để đảm bảo ổn định.
"""

import logging
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from src.agents.base import extract_json
from config.config import settings

logger = logging.getLogger(__name__)


class PublisherAgent:
    """Agent 6 — Upload ảnh và xuất bản lên Facebook"""

    @staticmethod
    def run(optimized_posts_json: str, images_json: str) -> str:
        logger.info("📤 PublisherAgent running...")

        posts = extract_json(optimized_posts_json, expect_array=True)
        images = extract_json(images_json, expect_array=True) or []

        if not posts:
            logger.error("❌ Không parse được SEO output")
            return json.dumps({"status": "failed", "error": "Cannot parse SEO output"})

        valid = [p for p in posts if p.get("optimized_content")]
        if not valid:
            logger.error("❌ Không có bài nào có optimized_content")
            return json.dumps({"status": "failed", "error": "No valid optimized_content"})

        best = max(valid, key=lambda p: p.get("estimated_reach", 0))
        content = best["optimized_content"]

        hashtags = best.get("hashtags_optimized", [])
        if hashtags and not any(h in content for h in hashtags):
            content += "\n\n" + " ".join(hashtags)

        # Lấy image URL hoặc local path
        image_url = None
        image_local = None
        if images and isinstance(images[0], dict):
            image_url = images[0].get("url")
            image_local = images[0].get("local_path")

        payload = {
            "status": "ready_to_publish",
            "selected_article_url": best.get("article_url", ""),
            "validation_result": "passed",
            "facebook_payload": {
                "message": content[:63000],
                "image_url": image_url,
                "image_local": image_local,
            },
            "estimated_reach": best.get("estimated_reach", 0),
            "estimated_engagement": int(best.get("estimated_reach", 0) * 0.025),
        }

        logger.debug(f"📦 PublisherAgent payload dict: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        logger.info("✅ PublisherAgent: payload built successfully")
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _upload_photo(image_url: Optional[str], image_local: Optional[str]) -> Optional[str]:
        """Upload ảnh lên Facebook, trả về photo_id hoặc None nếu thất bại."""
        token = settings.facebook_access_token
        page_id = settings.facebook_page_id
        version = settings.facebook_api_version
        upload_url = f"https://graph.facebook.com/{version}/{page_id}/photos"

        try:
            if image_local:
                # Upload từ file local
                logger.info(f"📸 Uploading local image: {image_local}")
                with open(image_local, "rb") as f:
                    resp = requests.post(
                        upload_url,
                        data={"access_token": token, "published": "false"},
                        files={"source": f},
                        timeout=30,
                    )
            elif image_url:
                # Upload từ URL
                logger.info(f"📸 Uploading image from URL: {image_url[:80]}")
                resp = requests.post(
                    upload_url,
                    data={"access_token": token, "url": image_url, "published": "false"},
                    timeout=30,
                )
            else:
                return None

            if resp.status_code in (200, 201):
                photo_id = resp.json().get("id")
                logger.info(f"✅ Photo uploaded: {photo_id}")
                return photo_id
            else:
                err = resp.json().get("error", {}).get("message", "Unknown")
                logger.warning(f"⚠️ Photo upload failed: {err} — đăng không ảnh")
                return None

        except Exception as e:
            logger.warning(f"⚠️ Photo upload exception: {e} — đăng không ảnh")
            return None

    @staticmethod
    async def publish_to_facebook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Upload ảnh rồi đăng bài lên Facebook."""
        token = settings.facebook_access_token

        if not token or "test" in token or len(token) < 30:
            logger.warning("⚠️ Facebook token không hợp lệ, bỏ qua")
            return {"status": "skipped", "reason": "token không hợp lệ"}

        try:
            page_id = settings.facebook_page_id
            version = settings.facebook_api_version
            feed_url = f"https://graph.facebook.com/{version}/{page_id}/feed"

            message = payload.get("message", "")
            image_url = payload.get("image_url")
            image_local = payload.get("image_local")

            post_data = {"message": message, "access_token": token}

            # Bước 1: Upload ảnh (nếu có) → lấy photo_id
            if image_url or image_local:
                photo_id = PublisherAgent._upload_photo(image_url, image_local)
                if photo_id:
                    post_data["attached_media[0]"] = json.dumps({"media_fbid": photo_id})
                    logger.info(f"📎 Đính kèm ảnh: {photo_id}")

            # Bước 2: Đăng bài
            logger.info("📤 Calling Facebook Graph API (feed)...")
            resp = requests.post(feed_url, data=post_data, timeout=30)

            if resp.status_code in (200, 201):
                post_id = resp.json().get("id")
                logger.info(f"✅ Published! Post ID: {post_id}")
                return {
                    "status": "published",
                    "post_id": post_id,
                    "facebook_url": f"https://www.facebook.com/{post_id}",
                    "published_at": datetime.now().isoformat(),
                }
            else:
                error = resp.json().get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ Facebook API error: {error}")
                return {"status": "failed", "error": error, "http_status": resp.status_code}

        except Exception as e:
            logger.error(f"❌ publish_to_facebook exception: {e}")
            return {"status": "error", "error": str(e)}
