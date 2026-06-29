"""
Streamlit Web UI for Orchestrator
Simple interface with START button, status, and real-time logs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from config.config import settings, TZ
from src.orchestrator import orchestrator

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Facebook Automation Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CUSTOM STYLING ============
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton > button {
        width: 100%;
        padding: 0.6rem 1.5rem;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATE INITIALIZATION ============
if "is_running" not in st.session_state:
    st.session_state.is_running = orchestrator.is_running
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# ============ HEADER ============
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🚀 Facebook Automation Pipeline")
    st.markdown("**AI-Powered Content Creation & Publishing System**")

st.markdown("---")

# ============ MAIN CONTROL PANEL ============
st.subheader("⚙️ System Control")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ START SYSTEM", use_container_width=True, key="start_btn"):
        with st.spinner("Starting system..."):
            response = orchestrator.start_system()
            st.session_state.is_running = True
            if response["status"] == "success":
                st.success("✅ System started successfully!")
                st.balloons()
            else:
                st.error(f"❌ Failed to start: {response['message']}")

with col2:
    if st.button("⏹️ STOP SYSTEM", use_container_width=True, key="stop_btn"):
        with st.spinner("Stopping system..."):
            response = orchestrator.stop_system()
            st.session_state.is_running = False
            if response["status"] == "success":
                st.success("✅ System stopped")
            else:
                st.error(f"❌ Failed to stop: {response['message']}")

with col3:
    if st.button("🔄 REFRESH", use_container_width=True, key="refresh_btn"):
        st.rerun()

with col4:
    st.session_state.auto_refresh = st.checkbox("🔁 Auto-Refresh", value=True)

# ============ STATUS DASHBOARD ============
st.subheader("📊 System Status Dashboard")

status = orchestrator.get_status()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if status["is_running"]:
        st.metric("Status", "🟢 RUNNING", "System is active")
    else:
        st.metric("Status", "🔴 STOPPED", "System is offline")

with col2:
    st.metric(
        "📅 Last Execution",
        status["last_execution"][:10] if status["last_execution"] else "Never",
        "Today" if status["last_execution"] and status["last_execution"].startswith(datetime.now(TZ).strftime("%Y-%m-%d")) else "Previous"
    )

with col3:
    st.metric(
        "⏰ Next Execution",
        status["next_execution"][11:16] if status["next_execution"] else settings.publisher_time,
        settings.publisher_time
    )

with col4:
    st.metric(
        "📊 Total Executions",
        len(orchestrator.execution_logs),
        "logs in memory"
    )

st.markdown("---")

# ============ AGENT EXECUTION TIMELINE ============
st.subheader("📈 Agent Execution Timeline")

if len(orchestrator.execution_logs) > 0:
    timeline_data = []
    for log in orchestrator.execution_logs[-30:]:
        timeline_data.append({
            "Time": log["timestamp"],
            "Agent": log["agent"],
            "Status": log["status"],
            "Error": log.get("error", "-")
        })

    df_timeline = pd.DataFrame(timeline_data)

    def get_status_icon(status):
        if status == "STARTED":
            return "🔵"
        elif status == "COMPLETED":
            return "🟢"
        elif status == "FAILED":
            return "🔴"
        else:
            return "⚪"

    df_timeline["Status_Icon"] = df_timeline["Status"].apply(get_status_icon)

    st.dataframe(
        df_timeline[["Time", "Status_Icon", "Agent", "Status", "Error"]].rename(
            columns={"Status_Icon": "📍", "Agent": "Agent Name", "Status": "Execution Status", "Error": "Error Message"}
        ),
        use_container_width=True,
        hide_index=True,
        height=400
    )
else:
    st.info("📭 No execution logs yet. Click START SYSTEM to begin.")

st.markdown("---")

# ============ SCHEDULE CONFIGURATION ============
st.subheader("🕐 Schedule Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌅 Scraper Time",
        settings.scraper_time,
        "Daily at 6:00 AM"
    )

with col2:
    st.metric(
        "📝 Processor Time",
        settings.processor_time,
        "Daily at 11:00 AM"
    )

with col3:
    st.metric(
        "📤 Publisher Time",
        settings.publisher_time,
        "Daily at 12:00 PM"
    )

st.markdown("---")

# ============ FOOTER ============
st.markdown(f"""
    <div style='text-align: center; color: #888; font-size: 12px; margin-top: 2rem;'>
        <p>🚀 Facebook Automation Pipeline v1.0 | Powered by CrewAI & Streamlit</p>
        <p>Last updated: {datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
""", unsafe_allow_html=True)

# ============ AUTO-REFRESH LOGIC ============
if st.session_state.auto_refresh:
    placeholder = st.empty()
    with placeholder.container():
        st.info("🔄 Auto-refreshing every 5 seconds...")
    time.sleep(5)
    st.rerun()
