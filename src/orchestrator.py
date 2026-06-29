"""
Main Orchestrator - Controls the entire pipeline
Runs on APScheduler with timezone support
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from config.config import settings, TZ
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


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
        # Lưu output riêng cho từng lần chạy: {"run1": {...}, "run2": {...}}
        self._pipeline_data: Dict[str, Any] = {"run1": {}, "run2": {}}
        # Lưu lịch sử các bài đã đăng thành công
        self.published_posts: list = []

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
        try:
            logger.info(f"[{execution_id}] 🔍 Scraper Agent starting ({run_id})...")
            self._log_execution("Scraper", "STARTED", execution_id)

            from src.agents.scraper_agent import ScraperAgent
            result = ScraperAgent.run()
            self._pipeline_data[run_id]["scraper"] = result

            logger.info(f"[{execution_id}] ✅ Scraper completed ({len(result)} chars)")
            self._log_execution("Scraper", "COMPLETED", execution_id)
            self.last_execution_time = datetime.now(TZ)

        except Exception as e:
            logger.error(f"[{execution_id}] ❌ Scraper failed: {str(e)}")
            self._log_execution("Scraper", "FAILED", execution_id, str(e))

    def _execute_processor(self, run_id: str = "run1"):
        """Execute Filter → Writer → Designer → SEO — gọi AI thật"""
        execution_id = f"processor_{run_id}_{datetime.now(TZ).timestamp()}"
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

            logger.info(f"[{execution_id}] Filter Agent running...")
            filtered = FilterAgent.run(raw)

            logger.info(f"[{execution_id}] Writer Agent running...")
            written = WriterAgent.run(filtered)

            logger.info(f"[{execution_id}] Designer Agent running...")
            design_json = DesignerAgent.run(written)
            design_configs = extract_json(design_json, expect_array=True) or []
            # run1 → Unsplash, run2 → Pexels (xen kẽ)
            img_source = "unsplash" if run_id == "run1" else "pexels"
            images = asyncio.run(DesignerAgent.download_images(design_configs, source=img_source)) if design_configs else []

            logger.info(f"[{execution_id}] SEO Agent running...")
            optimized = SEOAgent.run(written)

            logger.info(f"[{execution_id}] [DEBUG] SEOAgent.run() raw output (first 500 chars): {optimized[:500]!r}")
            logger.info(f"[{execution_id}] [DEBUG] SEOAgent.run() total output length: {len(optimized)} chars")

            self._pipeline_data[run_id]["optimized"] = optimized
            self._pipeline_data[run_id]["images"] = images

            logger.info(f"[{execution_id}] ✅ Processor completed")
            self._log_execution("Processor", "COMPLETED", execution_id)
            self.last_execution_time = datetime.now(TZ)

        except Exception as e:
            logger.error(f"[{execution_id}] ❌ Processor failed: {str(e)}", exc_info=True)
            self._log_execution("Processor", "FAILED", execution_id, str(e))


    def _execute_publisher(self, run_id: str = "run1"):
        """Execute Publisher Agent → đăng lên Facebook thật"""
        execution_id = f"publisher_{run_id}_{datetime.now(TZ).timestamp()}"
        try:
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

            logger.info(f"[{execution_id}] [DEBUG] optimized passed to PublisherAgent (first 500 chars): {optimized[:500]!r}")
            logger.info(f"[{execution_id}] [DEBUG] images passed to PublisherAgent: {images!r}")

            payload_json = PublisherAgent.run(optimized, json.dumps(images))

            logger.info(f"[{execution_id}] [DEBUG] PublisherAgent.run() raw return (first 1000 chars): {payload_json[:1000]!r}")

            payload_data = extract_json(payload_json, expect_array=False) or {}

            logger.info(f"[{execution_id}] [DEBUG] extract_json() result: {payload_data!r}")

            if not payload_data or "facebook_payload" not in payload_data:
                logger.error(f"[{execution_id}] ❌ Publisher không tạo được payload")
                self._log_execution("Publisher", "FAILED", execution_id, "No payload")
                return

            result = asyncio.run(PublisherAgent.publish_to_facebook(payload_data["facebook_payload"]))
            status = result.get("status")

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
            else:
                logger.error(f"[{execution_id}] ❌ Đăng thất bại: {result.get('error')}")

            # Reset data sau khi đăng xong
            self._pipeline_data[run_id] = {}

            self._log_execution("Publisher", status.upper(), execution_id)
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
