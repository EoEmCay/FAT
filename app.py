import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime
from config.config import settings, TZ
from src.orchestrator import orchestrator

st.set_page_config(
    page_title="Facebook Automation Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        padding: 0.6rem 1.5rem;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

if "is_running" not in st.session_state:
    st.session_state.is_running = orchestrator.is_running

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🚀 Facebook Automation Pipeline")
    st.markdown("**AI-Powered Content Creation & Publishing — Genz Yêu Công Nghệ**")

st.markdown("---")

# ── CONTROL PANEL ──────────────────────────────────────────────
st.subheader("⚙️ System Control")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ START SYSTEM", use_container_width=True):
        response = orchestrator.start_system()
        st.session_state.is_running = True
        if response["status"] == "success":
            st.success("✅ System started!")
            st.balloons()
        else:
            st.warning(f"ℹ️ {response['message']}")

with col2:
    if st.button("⏹️ STOP SYSTEM", use_container_width=True):
        response = orchestrator.stop_system()
        st.session_state.is_running = False
        if response["status"] == "success":
            st.success("✅ System stopped")
        else:
            st.error(f"❌ {response['message']}")

with col3:
    if st.button("🔄 REFRESH", use_container_width=True):
        st.rerun()

# ── STATUS ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 System Status")

status = orchestrator.get_status()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", "🟢 RUNNING" if status["is_running"] else "🔴 STOPPED")
with col2:
    last = status["last_execution"]
    st.metric("Last Execution", last[:16].replace("T", " ") if last else "Never")
with col3:
    st.metric("Lần 1 đăng lúc", settings.publisher_time)
with col4:
    st.metric("Lần 2 đăng lúc", settings.publisher_time_2)

# ── SCHEDULE ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("🕐 Lịch đăng bài hôm nay")

col1, col2 = st.columns(2)
with col1:
    st.info(f"""
    **Lần 1 (Unsplash)**
    - 🔍 Scraper: {settings.scraper_time}
    - ✍️ Writer:  {settings.processor_time}
    - 📤 Đăng:   {settings.publisher_time}
    """)
with col2:
    st.info(f"""
    **Lần 2 (Pexels)**
    - 🔍 Scraper: {settings.scraper_time_2}
    - ✍️ Writer:  {settings.processor_time_2}
    - 📤 Đăng:   {settings.publisher_time_2}
    """)

# ── LOGS ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Execution Logs")

if orchestrator.execution_logs:
    rows = []
    for log in reversed(orchestrator.execution_logs[-30:]):
        icon = {"STARTED": "🔵", "COMPLETED": "🟢", "FAILED": "🔴", "PUBLISHED": "✅", "SKIPPED": "⚠️"}.get(log["status"], "⚪")
        rows.append({
            "Time": log["timestamp"][:19].replace("T", " "),
            "": icon,
            "Agent": log["agent"],
            "Status": log["status"],
            "Error": log.get("error") or "-",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=350)
else:
    st.info("📭 Chưa có log. Bấm START SYSTEM để bắt đầu.")

st.markdown("---")
st.caption(f"🕐 Server time: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} (ICT) | Timezone: {settings.scheduler_timezone}")
