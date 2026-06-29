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
        # Bài đang chờ duyệt: {"run1": {...}, "run2": {...}}
        self.pending_posts: Dict[str, Any] = {"run1": None, "run2": None}

    def run_now(self, run_id: str = "run1"):
        """Chạy Scraper + Processor ngay, dừng lại chờ duyệt."""
        def _run():
            logger.info(f"🚀 RUN NOW triggered ({run_id})")
            self._execute_scraper(run_id)
            self._execute_processor(run_id)
            logger.info(f"✋ Pipeline dừng — chờ duyệt bài ({run_id})")

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return {"status": "started", "run_id": run_id}

    def approve_and_publish(self, run_id: str, image_bytes: bytes = None, image_name: str = None):
        """Duyệt bài và đăng lên Facebook, có thể kèm ảnh upload từ user."""
        def _publish():
            # Lưu ảnh upload vào temp file nếu có
            if image_bytes:
                import tempfile, os
                ext = (image_name or "image.jpg").rsplit(".", 1)[-1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                tmp.write(image_bytes)
                tmp.close()
                # Ghi đè image vào pipeline_data
                self._pipeline_data[run_id]["images"] = [{"local_path": tmp.name, "url": None}]
                _save_pipeline_cache(self._pipeline_data)
                logger.info(f"📸 Ảnh upload được lưu: {tmp.name}")
            self._execute_publisher(run_id)
            self.pending_posts[run_id] = None

        t = threading.Thread(target=_publish, daemon=True)
        t.start()
        return {"status": "publishing"}

    def reject_post(self, run_id: str):
        """Bỏ qua bài, xóa data pipeline."""
        self._pipeline_data[run_id] = {}
        self.pending_posts[run_id] = None
        _save_pipeline_cache(self._pipeline_data)
        logger.info(f"❌ Bài {run_id} bị từ chối, xóa data")
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

            # ── Designer Agent ────────────────────────────────────
            t_step = datetime.now(TZ)
            logger.info(f"[{execution_id}] 🎨 Designer Agent running...")
            design_json = DesignerAgent.run(written)
            design_configs = extract_json(design_json, expect_array=True) or []
            img_source = "unsplash" if run_id == "run1" else "pexels"
            images = asyncio.run(DesignerAgent.download_images(design_configs, source=img_source)) if design_configs else []
            elapsed = (datetime.now(TZ) - t_step).seconds
            logger.info(f"[{execution_id}] ✅ Designer xong sau {elapsed}s — {len(images)} ảnh ({img_source})")
            for img in images[:2]:
                logger.info(f"    🖼  {str(img.get('url',''))[:80]}")

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
            seo_posts = _ej(optimized, expect_array=True) or []
            if seo_posts:
                best = max(seo_posts, key=lambda p: p.get("estimated_reach", 0))
                self.pending_posts[run_id] = {
                    "run_id": run_id,
                    "content": best.get("optimized_content", ""),
                    "hashtags": best.get("hashtags_optimized", []),
                    "image_url": images[0].get("url") if images else None,
                    "image_local": images[0].get("local_path") if images else None,
                    "estimated_reach": best.get("estimated_reach", 0),
                }
                logger.info(f"[{execution_id}] 📋 Bài đang chờ duyệt trên UI")

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
            # Nếu được gọi từ scheduler (không phải approve), bỏ qua nếu chưa duyệt
            if not self._pipeline_data[run_id].get("optimized"):
                logger.info(f"[{execution_id}] ⏭️ Không có bài chờ đăng cho {run_id}, bỏ qua")
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
