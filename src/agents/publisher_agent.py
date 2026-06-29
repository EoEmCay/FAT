"""
Agent 6: Publisher Agent
Validate dữ liệu, chọn bài tốt nhất, và đăng lên Facebook Graph API
"""

import logging
import json
import requests
from datetime import datetime
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base import get_llm
from config.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là DevOps expert chuyên quản lý API và xuất bản nội dung.
Luôn trả về JSON hợp lệ, không có text ngoài JSON."""

TASK_PROMPT = """Từ danh sách bài viết đã tối ưu và ảnh dưới đây:

POSTS:
{optimized_posts}

IMAGES:
{images}

Thực hiện:
1. Validate từng bài:
   - Content dưới 63206 ký tự
   - Có đầy đủ hook, body, cta
   - Hashtags không quá 15 cái
2. Chọn 1 bài TỐT NHẤT (estimated_reach cao nhất, content quality tốt nhất)
3. Ghép content hoàn chỉnh: hook + body + cta + hashtags
4. Chuẩn bị Facebook API payload

Trả về JSON (chỉ 1 object, không phải array):
{{
  "status": "ready_to_publish",
  "selected_article_url": "url bài được chọn",
  "validation_result": "passed",
  "facebook_payload": {{
    "message": "Toàn bộ nội dung bài (hook + body + cta + hashtags)",
    "link": "url bài gốc",
    "picture": "url ảnh hoặc null",
    "name": "Tiêu đề ngắn",
    "description": "Mô tả 1 câu"
  }},
  "estimated_reach": 25000,
  "estimated_engagement": 600
}}

Chỉ trả về JSON object, KHÔNG có text nào khác."""


class PublisherAgent:
    """Agent 6 — Validate và xuất bản lên Facebook"""

    @staticmethod
    def run(optimized_posts_json: str, images_json: str) -> str:
        """
        Chọn bài tốt nhất và chuẩn bị payload.
        Trả về JSON string của payload.
        """
        logger.info("📤 PublisherAgent running...")

        llm = get_llm(use_large=False)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", TASK_PROMPT),
        ])

        chain = prompt | llm
        result = chain.invoke({
            "optimized_posts": optimized_posts_json,
            "images": images_json,
        })

        logger.info("✅ PublisherAgent completed")
        return result.content

    @staticmethod
    async def publish_to_facebook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gọi Facebook Graph API để đăng bài.
        payload: dict chứa message, link, picture, name, description
        """
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
            headers = {"Authorization": f"Bearer {settings.facebook_access_token}"}

            # Chỉ gửi field nào có giá trị
            clean_payload = {k: v for k, v in payload.items() if v}

            resp = requests.post(url, json=clean_payload, headers=headers, timeout=30)

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
