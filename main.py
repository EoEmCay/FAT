"""
Main entry point for the system
Run this file to start the orchestrator and Streamlit UI
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config import settings
from src.database.db import init_db, close_db
from src.utils.logging import setup_logger
from src.orchestrator import orchestrator
import subprocess
import time

logger = setup_logger(__name__)

def main():
    """
    Main entry point
    1. Initialize database
    2. Start orchestrator
    3. Start Streamlit UI
    """

    logger.info("=" * 60)
    logger.info("🚀 Facebook Automation Pipeline Starting...")
    logger.info("=" * 60)

    try:
        # Step 1: Initialize database
        logger.info("Step 1: Initializing database...")
        init_db()
        logger.info("✅ Database ready")

        # Step 2: Start orchestrator
        logger.info("\nStep 2: Starting orchestrator...")
        response = orchestrator.start_system()
        if response["status"] != "success":
            logger.error(f"Failed to start orchestrator: {response['message']}")
            return
        logger.info("✅ Orchestrator running")

        # Step 3: Start Streamlit UI
        logger.info("\nStep 3: Starting Streamlit UI...")
        logger.info(f"📱 UI will be available at http://0.0.0.0:{settings.streamlit_server_port}")
        logger.info("Press Ctrl+C to stop\n")

        time.sleep(2)

        # Start Streamlit
        subprocess.run([
            "streamlit", "run",
            "ui/streamlit_app.py",
            "--logger.level=info",
            "--client.showErrorDetails=false"
        ])

    except KeyboardInterrupt:
        logger.info("\n\n🛑 Stopping system...")
        orchestrator.stop_system()
        close_db()
        logger.info("✅ System stopped gracefully")
        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        orchestrator.stop_system()
        close_db()
        sys.exit(1)

if __name__ == "__main__":
    main()
