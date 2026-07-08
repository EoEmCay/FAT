"""
Main Orchestrator - Controls the entire pipeline
Runs on APScheduler with timezone support
"""

import logging
import json
import os
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from config.config import settings, TZ
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

_PIPELINE_CACHE_FILE = "/tmp/pipeline_data.json"


def _load_pipeline_cache() -> Dict[str, Any]:
    try:
        if os.path.exists(_PIPELINE_CACHE_FILE):
            with open(_PIPELINE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"run1": {}, "run2": {}}


def _save_pipeline_cache(data: Dict[str, Any]):
    try:
        with open(_PIPELINE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"⚠️ Không lưu được pipeline cache: {e}")


class Orchestrator:
    """
    Main Orchestrator class that manages:
    - APScheduler for scheduling tasks
    - Pipeline execution (6 agents workflow)
    - Logging & monitoring
    - Error handling & retries
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=TZ)
        self.is_running = False
        self.last_execution_time: Optional[datetime] = None
        self.next_execution_time: Optional[datetime] = None
        self.current_status: str = "STOPPED"
        self.execution_logs: list = []
        # Load từ file để tồn tại qua restart
        self._pipeline_data: Dict[str, Any] = _load_pipeline_cache()
        # Lưu lịch sử các bài đã đăng thành công
        self.published_posts: list = []
        # Hàng đợi bài chờ duyệt (tối đa 99)
        self.post_queue: list = []
        self._queue_counter: int = 0

    def run_now(self, run_id: str = "run1"):
        """Chạy Scraper + Processor ngay, dừng lại chờ duyệt."""
        def _run():
            logger.info(f"🚀 RUN NOW triggered ({run_id})")
            self._execute_scraper(run_id)
            self._execute_processor(run_id)
            logger.info(f"✋ Pipeline dừng — bài đã vào hàng đợi ({run_id})")

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return {"status": "started", "run_id": run_id}

    def approve_and_publish(self, queue_idx: int, image_bytes: bytes = None, image_name: str = None):
        """Duyệt bài theo index trong queue và đăng lên Facebook."""
        if queue_idx >= len(self.post_queue):
            return {"status": "error", "message": "Index không hợp lệ"}

        post = self.post_queue[queue_idx]
        run_id = post.get("run_id", "run1")

        def _publish():
            if image_bytes:
                # User upload ảnh riêng → ghi đè ảnh AI
                import tempfile
                ext = (image_name or "image.jpg").rsplit(".", 1)[-1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                tmp.write(image_bytes)
                tmp.close()
                self._pipeline_data[run_id]["images"] = [{"local_path": tmp.name, "url": None}]
                logger.info(f"📸 Dùng ảnh user upload: {tmp.name}")
            else:
                # Tự động dùng ảnh AI đã lưu trong AIimg/
                ai_local = post.get("image_local")
                ai_url   = post.get("image_url")
                if ai_local or ai_url:
                    self._pipeline_data[run_id]["images"] = [{"local_path": ai_local, "url": ai_url}]
                    logger.info(f"📸 Tự dùng ảnh AI: {ai_local or ai_url}")
            _save_pipeline_cache(self._pipeline_data)
            self._execute_publisher(run_id)
            if post in self.post_queue:
                self.post_queue.remove(post)

        t = threading.Thread(target=_publish, daemon=True)
        t.start()
        return {"status": "publishing"}

    def reject_post(self, queue_idx: int):
        """Bỏ qua bài theo index, xóa khỏi queue."""
        if queue_idx >= len(self.post_queue):
            return {"status": "error"}
        post = self.post_queue.pop(queue_idx)
        run_id = post.get("run_id", "run1")
        self._pipeline_data[run_id] = {}
        _save_pipeline_cache(self._pipeline_data)
        logger.info(f"❌ Bài #{post.get('queue_num')} bị từ chối")
        return {"status": "rejected"}

    def start_system(self) -> Dict[str, Any]:
        """
        Start the orchestrator system

        Returns:
            dict: Status and metadata
        """
        try:
            if self.is_running:
                logger.warning("System is already running!")
                return {"status": "already_running", "message": "System already started"}

            # Schedule tasks
            self._schedule_tasks()

            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            self.current_status = "RUNNING"

            logger.info("✅ Orchestrator started successfully")

            return {
                "status": "success",
                "message": "System started",
                "is_running": True,
                "started_at": datetime.now(TZ).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Failed to start system: {str(e)}")
            self.current_status = "ERROR"
            return {
                "status": "error",
                "message": str(e),
                "is_running": False
            }

    def stop_system(self) -> Dict[str, Any]:
        """
        Stop the orchestrator system

        Returns:
            dict: Status and metadata
        """
        try:
            if not self.is_running:
                logger.warning("System is not running!")
                return {"status": "already_stopped", "message": "System not running"}

            self.scheduler.shutdown()
            self.is_running = False
            self.current_status = "STOPPED"

            logger.info("✅ Orchestrator stopped successfully")

            return {
                "status": "success",
                "message": "System stopped",
                "is_running": False,
                "stopped_at": datetime.now(TZ).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Failed to stop system: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "is_running": self.is_running
            }

    def _schedule_tasks(self):
        """Schedule 6 jobs (2 lần/ngày) + health check"""

        runs = [
            ("run1", settings.scraper_time,   settings.processor_time,   settings.publisher_time),
            ("run2", settings.scraper_time_2, settings.processor_time_2, settings.publisher_time_2),
        ]

        for run_id, s_time, p_time, pub_time in runs:
            s_h, s_m   = map(int, s_time.split(":"))
            p_h, p_m   = map(int, p_time.split(":"))
            pub_h, pub_m = map(int, pub_time.split(":"))

            self.scheduler.add_job(
                func=self._execute_scraper,
                kwargs={"run_id": run_id},
                trigger=CronTrigger(hour=s_h, minute=s_m, timezone=TZ),
                id=f"scraper_{run_id}",
                name=f"Scraper [{run_id}]",
                replace_existing=True,
            )
            self.scheduler.add_job(
                func=self._execute_processor,
                kwargs={"run_id": run_id},
                trigger=CronTrigger(hour=p_h, minute=p_m, timezone=TZ),
                id=f"processor_{run_id}",
                name=f"Processor [{run_id}]",
                replace_existing=True,
            )
            self.scheduler.add_job(
                func=self._execute_publisher,
                kwargs={"run_id": run_id},
                trigger=CronTrigger(hour=pub_h, minute=pub_m, timezone=TZ),
                id=f"publisher_{run_id}",
                name=f"Publisher [{run_id}]",
                replace_existing=True,
            )
            logger.info(f"📅 [{run_id}] {s_time} → {p_time} → {pub_time}")

        self.scheduler.add_job(
            func=self._health_check,
            trigger="interval",
            minutes=5,
            id="health_check",
            name="Health Check",
        )
        logger.info("🏥 Health check every 5 minutes")

    def _execute_scraper(self, run_id: str = "run1"):
        """Execute Scraper Agent — gọi AI thật"""
        execution_id = f"scraper_{run_id}_{datetime.now(TZ).timestamp()}"
        t0 = datetime.now(TZ)
        try:
            logger.info(f"[{execution_id}] 🔍 Scraper Agent starting ({run_id})...")
            self._log_execution("Scraper", "STARTED", execution_id)

            from src.agents.scraper_agent import ScraperAgent
            result = ScraperAgent.run()
            self._pipeline_data[run_id]["scraper"] = result

            elapsed = (datetime.now(TZ) - t0).seconds
            # Log tóm tắt nội dung cào được
            preview_lines = [l.strip() for l in result.split("\n") if l.strip()][:8]
            logger.info(f"[{execution_id}] ✅ Scraper xong sau {elapsed}s — {len(result)} ký tự")
            logger.info(f"[{execution_id}] 📰 Nội dung cào được (8 dòng đầu):")
            for line in preview_lines:
                logger.info(f"    {line}")
            self._log_execution("Scraper", "COMPLETED", execution_id)
            self.last_execution_time = datetime.now(TZ)

        except Exception as e:
            logger.error(f"[{execution_id}] ❌ Scraper failed: {str(e)}")
            self._log_execution("Scraper", "FAILED", execution_id, str(e))

    def _execute_processor(self, run_id: str = "run1"):
        """Execute Filter → Writer → Designer → SEO — gọi AI thật"""
        execution_id = f"processor_{run_id}_{datetime.now(TZ).timestamp()}"
        t0 = t_step = datetime.now(TZ)
        try:
            logger.info(f"[{execution_id}] ⚙️ Processor Pipeline starting ({run_id})...")
            self._log_execution("Processor", "STARTED", execution_id)

            from src.agents.filter_agent import FilterAgent
            from src.agents.writer_agent import WriterAgent
            from src.agents.designer_agent import DesignerAgent
            from src.agents.renderer import render_infographic
            from src.agents.seo_agent import SEOAgent
            from src.agents.base import extract_json

            raw = self._pipeline_data[run_id].get("scraper")
            if not raw:
                logger.warning(f"[{execution_id}] ⚠️ Không có Scraper output, chạy Scraper ngay")
                from src.agents.scraper_agent import ScraperAgent
                raw = ScraperAgent.run()

            # ── Filter Agent ──────────────────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] 🔎 Filter Agent running...")
            filtered = FilterAgent.run(raw)
            filtered_data = extract_json(filtered, expect_array=True) or []
            elapsed = (datetime.now(TZ) - t_step).seconds
            logger.info(f"[{execution_id}] ✅ Filter xong sau {elapsed}s — {len(filtered_data)} bài lọc được")
            for i, a in enumerate(filtered_data[:3]):
                logger.info(f"    [{i+1}] {a.get('title','?')[:80]} — {a.get('source','?')}")

            # ── Writer Agent ──────────────────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] ✍️  Writer Agent running...")
            written = WriterAgent.run(filtered)
            elapsed = (datetime.now(TZ) - t_step).seconds
            written_data = extract_json(written, expect_array=True) or []
            logger.info(f"[{execution_id}] ✅ Writer xong sau {elapsed}s — {len(written_data)} bài viết")
            for i, p in enumerate(written_data[:2]):
                headline = p.get("headline", p.get("hook", "?"))[:80]
                logger.info(f"    [{i+1}] {headline}")

            # ── Designer Agent — chọn màu ─────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] 🎨 Designer Agent running...")
            design_json     = DesignerAgent.run(written)
            design_configs  = extract_json(design_json, expect_array=True) or []
            accent_color    = (design_configs[0].get("accent_color", "clay blue")
                               if design_configs else "clay blue")
            elapsed = (datetime.now(TZ) - t_step).seconds
            logger.info(f"[{execution_id}] ✅ Designer xong sau {elapsed}s — màu: {accent_color}")

            # ── Parse writer output sớm (cần cho renderer + drip) ─────
            writer_posts = extract_json(written, expect_array=True) or []
            best_written = (max(writer_posts, key=lambda p: len(p.get("blocks", [])))
                            if writer_posts else {})
            blocks   = best_written.get("blocks", [])
            headline = best_written.get("headline", "")
            summary  = best_written.get("summary", "")
            cta      = best_written.get("cta", "")
            post_hashtags = best_written.get("hashtags", [])
            self._pipeline_data[run_id]["blocks"]   = blocks
            self._pipeline_data[run_id]["headline"] = headline
            _save_pipeline_cache(self._pipeline_data)

            # ── Render infographic với Pillow ──────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] 🖼  Rendering infographic ({accent_color})...")
            local_path = render_infographic(
                headline=headline,
                blocks=blocks,
                summary=summary,
                cta=cta,
                hashtags=post_hashtags,
                accent_color_name=accent_color,
            )
            images = [{"local_path": local_path, "url": None, "image_source": "pillow_render"}] \
                     if local_path else []
            elapsed = (datetime.now(TZ) - t_step).seconds
            logger.info(f"[{execution_id}] ✅ Render xong sau {elapsed}s — {local_path}")

            # ── SEO Agent ─────────────────────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] ⚡ SEO Agent running...")
            optimized = SEOAgent.run(written)
            elapsed = (datetime.now(TZ) - t_step).seconds
            logger.info(f"[{execution_id}] ✅ SEO xong sau {elapsed}s")

            self._pipeline_data[run_id]["optimized"] = optimized
            self._pipeline_data[run_id]["images"] = images
            _save_pipeline_cache(self._pipeline_data)

            # Parse bài viết để hiển thị preview trên UI
            from src.agents.base import extract_json as _ej
            from src.agents.seo_agent import _assemble_post
            seo_posts = _ej(optimized, expect_array=True) or []

            logger.info(f"[{execution_id}] 🔍 SEO posts count: {len(seo_posts)}, writer posts count: {len(writer_posts)}")

            # Fallback: nếu SEO output rỗng, dùng writer output trực tiếp
            if not seo_posts and writer_posts:
                logger.warning(f"[{execution_id}] ⚠️ SEO output rỗng — fallback dùng writer output")
                for wp in writer_posts:
                    assembled = _assemble_post(wp)
                    if assembled:
                        seo_posts.append({
                            "article_url": wp.get("article_url", ""),
                            "optimized_content": assembled,
                            "hashtags_optimized": wp.get("hashtags", []),
                            "estimated_reach": 25000,
                        })
                logger.info(f"[{execution_id}] ✅ Fallback tạo được {len(seo_posts)} bài từ writer output")

            if seo_posts:
                best = max(seo_posts, key=lambda p: p.get("estimated_reach", 0))
                n_blocks = len(blocks)
                drip_eligible = n_blocks in (5, 7)

                if drip_eligible and headline:
                    hashtags = best.get("hashtags_optimized", [])
                    post_content = f"{headline}\n\n👇 Đọc thêm bên dưới\n\n" + " ".join(hashtags)
                else:
                    post_content = best.get("optimized_content", "")

                # Giới hạn queue 99 bài
                logger.info(f"[{execution_id}] 📝 Content preview: {post_content[:100]}")
                if len(self.post_queue) < 99:
                    self._queue_counter += 1
                    self.post_queue.append({
                        "queue_num": self._queue_counter,
                        "run_id": run_id,
                        "content": post_content,
                        "hashtags": best.get("hashtags_optimized", []),
                        "blocks": blocks,
                        "headline": headline,
                        "drip_eligible": drip_eligible,
                        "image_url": images[0].get("url") if images else None,
                        "image_local": images[0].get("local_path") if images else None,
                        "estimated_reach": best.get("estimated_reach", 0),
                        "created_at": datetime.now(TZ).strftime("%H:%M %d/%m/%Y"),
                    })
                    logger.info(f"[{execution_id}] 📋 Bài #{self._queue_counter} vào hàng đợi — {n_blocks} blocks {'(drip)' if drip_eligible else ''}")
                else:
                    logger.warning(f"[{execution_id}] ⚠️ Hàng đợi đã đầy (99 bài)")

            total = (datetime.now(TZ) - t0).seconds
            logger.info(f"[{execution_id}] ✅ Processor hoàn tất sau {total}s — chờ duyệt bài")
            self._log_execution("Processor", "COMPLETED", execution_id)
            self.last_execution_time = datetime.now(TZ)

        except Exception as e:
            logger.error(f"[{execution_id}] ❌ Processor failed: {str(e)}", exc_info=True)
            self._log_execution("Processor", "FAILED", execution_id, str(e))

    def _execute_publisher(self, run_id: str = "run1"):
        """Execute Publisher Agent → đăng lên Facebook thật"""
        execution_id = f"publisher_{run_id}_{datetime.now(TZ).timestamp()}"
        try:
            if not self._pipeline_data[run_id].get("optimized"):
                logger.info(f"[{execution_id}] ⏭️ Không có bài được duyệt cho {run_id}, bỏ qua")
                return

            logger.info(f"[{execution_id}] 📤 Publisher Agent starting ({run_id})...")
            self._log_execution("Publisher", "STARTED", execution_id)

            import json
            from src.agents.publisher_agent import PublisherAgent
            from src.agents.base import extract_json

            optimized = self._pipeline_data[run_id].get("optimized")
            images = self._pipeline_data[run_id].get("images", [])

            if not optimized:
                logger.error(f"[{execution_id}] ❌ Không có Processor output cho {run_id}")
                self._log_execution("Publisher", "FAILED", execution_id, "No processor output")
                return

            payload_json = PublisherAgent.run(optimized, json.dumps(images))
            logger.debug(f"[{execution_id}] 🔍 Raw PublisherAgent output: {payload_json!r}")
            payload_data = extract_json(payload_json, expect_array=False) or {}

            if not payload_data or "facebook_payload" not in payload_data:
                logger.error(f"[{execution_id}] ❌ Publisher không tạo được payload")
                self._log_execution("Publisher", "FAILED", execution_id, "No payload")
                return

            fb_payload = payload_data["facebook_payload"]
            logger.info(f"[{execution_id}] 📦 Payload message preview: {str(fb_payload.get('message',''))[:100]}")

            result = asyncio.run(PublisherAgent.publish_to_facebook(fb_payload))
            status = result.get("status")
            logger.info(f"[{execution_id}] 📬 Facebook API result: {result}")

            if status == "published":
                post_id = result.get("post_id")
                post_url = result.get("facebook_url", f"https://facebook.com/{post_id}")
                published_at = datetime.now(TZ).strftime("%H:%M %d/%m/%Y")
                logger.info(f"[{execution_id}] ✅ Đăng thành công! Post ID: {post_id}")
                self.published_posts.append({
                    "time": published_at,
                    "post_id": post_id,
                    "url": post_url,
                    "run_id": run_id,
                })
                # Bắt đầu comment drip nếu đủ điều kiện
                blocks = self._pipeline_data[run_id].get("blocks", [])
                if len(blocks) in (5, 7) and post_id:
                    t = threading.Thread(
                        target=self._comment_drip,
                        args=(post_id, blocks),
                        daemon=True,
                    )
                    t.start()
                    logger.info(f"[{execution_id}] 💬 Comment drip bắt đầu — {len(blocks)} comments trong 60 phút")
            elif status == "skipped":
                logger.warning(f"[{execution_id}] ⚠️ Bỏ qua: {result.get('reason')}")
            elif status == "failed":
                err_msg = f"Facebook từ chối: {result.get('error')} | HTTP {result.get('http_status')}"
                logger.error(f"[{execution_id}] ❌ {err_msg}")
                self._log_execution("Publisher", "FAILED", execution_id, err_msg)
            else:
                err_msg = f"Lỗi không xác định: {result}"
                logger.error(f"[{execution_id}] ❌ {err_msg}")
                self._log_execution("Publisher", "FAILED", execution_id, err_msg)

            # Reset data sau khi đăng xong
            self._pipeline_data[run_id] = {}
            _save_pipeline_cache(self._pipeline_data)

            if status == "published":
                self._log_execution("Publisher", "PUBLISHED", execution_id)
            elif status == "skipped":
                self._log_execution("Publisher", "SKIPPED", execution_id)

            self.last_execution_time = datetime.now(TZ)

        except Exception as e:
            logger.error(f"[{execution_id}] ❌ Publisher failed: {str(e)}", exc_info=True)
            self._log_execution("Publisher", "FAILED", execution_id, str(e))

    def _health_check(self):
        """Health check - every 5 minutes"""
        try:
            if self.scheduler.running:
                logger.debug("✅ Scheduler is healthy")
            else:
                logger.warning("⚠️ Scheduler stopped unexpectedly!")
                self._restart_scheduler()

        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")

    def _comment_drip(self, post_id: str, blocks: list):
        """Đăng từng block thành comment cách đều nhau trong 60 phút."""
        import time as _time
        import requests as _req

        n = len(blocks)  # 5 hoặc 7
        interval = 3600 / n  # giây giữa mỗi comment

        token = settings.facebook_access_token
        version = settings.facebook_api_version
        url = f"https://graph.facebook.com/{version}/{post_id}/comments"

        logger.info(f"💬 Comment drip: {n} comments, cách nhau {interval/60:.1f} phút")

        for i, block in enumerate(blocks):
            # Format comment: "1. 🤖 TIÊU ĐỀ\n\n• bullet\n• bullet\n\n➤ metric"
            number = i + 1
            icon = block.get("icon", "")
            title = block.get("title", "")
            bullets = block.get("bullets", [])
            metric = block.get("metric", "")

            lines = [f"{number}. {icon} {title}"]
            lines.append("")
            for b in bullets:
                lines.append(f"• {b}")
            if metric:
                lines.append("")
                lines.append(metric)

            comment_text = "\n".join(lines)

            try:
                resp = _req.post(url, data={"message": comment_text, "access_token": token}, timeout=15)
                if resp.status_code in (200, 201):
                    cmt_id = resp.json().get("id", "?")
                    logger.info(f"💬 Comment {number}/{n} đăng thành công (ID: {cmt_id})")
                else:
                    err = resp.json().get("error", {}).get("message", "?")
                    logger.warning(f"⚠️ Comment {number}/{n} thất bại: {err}")
            except Exception as e:
                logger.warning(f"⚠️ Comment {number}/{n} exception: {e}")

            # Chờ trước comment tiếp theo (trừ comment cuối)
            if i < n - 1:
                logger.info(f"⏳ Chờ {interval/60:.1f} phút trước comment {number+1}...")
                _time.sleep(interval)

        logger.info(f"✅ Comment drip hoàn tất — {n} comments đã đăng")

    def _restart_scheduler(self):
        """Restart scheduler if failed"""
        try:
            logger.info("Attempting to restart scheduler...")
            self.scheduler.start()
            logger.info("✅ Scheduler restarted")
        except Exception as e:
            logger.error(f"Failed to restart scheduler: {str(e)}")

    def _log_execution(self, agent_name: str, status: str, execution_id: str, error: Optional[str] = None):
        """Log agent execution to memory"""
        log_entry = {
            "timestamp": datetime.now(TZ).isoformat(),
            "agent": agent_name,
            "status": status,
            "execution_id": execution_id,
            "error": error
        }
        self.execution_logs.append(log_entry)

        # Keep only last 100 logs in memory
        if len(self.execution_logs) > 100:
            self.execution_logs.pop(0)

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "is_running": self.is_running,
            "current_status": self.current_status,
            "last_execution": self.last_execution_time.isoformat() if self.last_execution_time else None,
            "next_execution": self.next_execution_time.isoformat() if self.next_execution_time else None,
            "recent_logs": self.execution_logs[-20:]
        }

    def get_execution_logs(self, limit: int = 50) -> list:
        """Get execution logs"""
        return self.execution_logs[-limit:]


# Global orchestrator instance
orchestrator = Orchestrator()
