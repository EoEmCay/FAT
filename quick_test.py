"""
Quick test để kiểm tra xem hệ thống có chạy được không
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 FACEBOOK AUTOMATION - QUICK TEST")
print("=" * 70)

# ============ TEST 1: Check Python Version ============
print("\n[TEST 1] Python Version")
print(f"✅ Python {sys.version.split()[0]}")

# ============ TEST 2: Check Config Loading ============
print("\n[TEST 2] Loading Configuration")
try:
    # First check if we have minimal dependencies
    import os
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env file found and loaded")

        # Check key settings
        db_url = os.getenv("DATABASE_URL", "NOT SET")
        scheduler_tz = os.getenv("SCHEDULER_TIMEZONE", "NOT SET")

        print(f"   - Database: {db_url}")
        print(f"   - Timezone: {scheduler_tz}")
        print(f"   - Scraper Time: {os.getenv('SCRAPER_TIME')}")
        print(f"   - Processor Time: {os.getenv('PROCESSOR_TIME')}")
        print(f"   - Publisher Time: {os.getenv('PUBLISHER_TIME')}")
    else:
        print("❌ .env file NOT found")

except Exception as e:
    print(f"❌ Error loading config: {e}")

# ============ TEST 3: Check Database ============
print("\n[TEST 3] Database Connection")
try:
    import sqlite3
    db_path = Path(__file__).parent / "facebook_automation.db"

    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if tables:
            print(f"✅ Database found with {len(tables)} tables")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  Database exists but no tables")

        conn.close()
    else:
        print("⚠️  Database file not found (will be created on first run)")

except Exception as e:
    print(f"⚠️  Database check failed: {e}")

# ============ TEST 4: Check Required Modules ============
print("\n[TEST 4] Checking Dependencies")
dependencies = [
    ("python-dotenv", "dotenv"),
    ("pytz", "pytz"),
    ("APScheduler", "apscheduler"),
    ("SQLAlchemy", "sqlalchemy"),
    ("Streamlit", "streamlit"),
    ("CrewAI", "crewai"),
]

installed = 0
missing = []

for name, module in dependencies:
    try:
        __import__(module)
        print(f"✅ {name}")
        installed += 1
    except ImportError:
        print(f"❌ {name}")
        missing.append(name)

print(f"\n   Summary: {installed}/{len(dependencies)} installed")

# ============ TEST 5: Check Logs Directory ============
print("\n[TEST 5] Log Directory")
logs_dir = Path(__file__).parent / "logs"
if logs_dir.exists():
    print(f"✅ Logs directory exists")
else:
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created logs directory")
    except Exception as e:
        print(f"❌ Failed to create logs directory: {e}")

# ============ TEST 6: Try importing orchestrator ============
print("\n[TEST 6] Orchestrator Import")
try:
    from src.orchestrator import orchestrator
    print(f"✅ Orchestrator imported successfully")
    print(f"   - Is running: {orchestrator.is_running}")
    print(f"   - Current status: {orchestrator.current_status}")
except Exception as e:
    print(f"❌ Failed to import orchestrator: {e}")
    print(f"   Reason: You need to install missing dependencies first")

# ============ SUMMARY ============
print("\n" + "=" * 70)
print("📋 SUMMARY")
print("=" * 70)

if missing:
    print(f"\n⚠️  {len(missing)} dependencies missing:")
    for dep in missing:
        print(f"   - {dep}")

    print("\n🔧 To fix, run:")
    print("   python -m pip install -r requirements.txt")
    print("\nOr minimal fix:")
    print("   python -m pip install python-dotenv APScheduler pytz sqlalchemy")
else:
    print("\n✅ All critical dependencies installed!")
    print("✅ System should be ready to run")

print("\n" + "=" * 70)
