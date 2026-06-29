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

# ── HEADER ─────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🚀 Facebook Automation Pipeline")
    st.markdown("**AI-Powered Content Creation — Genz Yêu Công Nghệ**")

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
    if st.button("🔄 REFRESH NOW", use_container_width=True):
        st.rerun()

st.markdown("")
col_run1, col_run2 = st.columns(2)
with col_run1:
    if st.button("⚡ RUN PIPELINE NOW (Lần 1 — Unsplash)", use_container_width=True):
        orchestrator.run_now("run1")
        st.success("✅ Pipeline run1 đang chạy — chờ vài giây rồi xem bài bên dưới")
with col_run2:
    if st.button("⚡ RUN PIPELINE NOW (Lần 2 — Pexels)", use_container_width=True):
        orchestrator.run_now("run2")
        st.success("✅ Pipeline run2 đang chạy — chờ vài giây rồi xem bài bên dưới")

st.markdown("---")

# ── DUYỆT BÀI TRƯỚC KHI ĐĂNG (tự refresh mỗi 5 giây) ──────────
@st.fragment(run_every=5)
def review_panel():
    has_pending = any(orchestrator.pending_posts.get(r) for r in ["run1", "run2"])
    if not has_pending:
        return

    st.subheader("📋 Bài chờ duyệt")

    for run_id in ["run1", "run2"]:
        post = orchestrator.pending_posts.get(run_id)
        if not post:
            continue

        label = "Lần 1 (Unsplash)" if run_id == "run1" else "Lần 2 (Pexels)"
        with st.expander(f"✍️ {label} — Bấm để xem & duyệt bài", expanded=True):

            # Thông báo drip
            blocks = post.get("blocks", [])
            if post.get("drip_eligible"):
                st.info(f"💬 **Comment Drip ON** — {len(blocks)} comments sẽ tự đăng cách nhau {60//len(blocks)} phút sau khi bài lên")
            else:
                st.warning(f"ℹ️ {len(blocks)} blocks — Comment drip chỉ chạy với 5 hoặc 7 blocks")

            # Hiện nội dung bài
            st.markdown("**📝 Nội dung bài viết:**")
            st.text_area(
                label="",
                value=post.get("content", ""),
                height=400,
                key=f"content_{run_id}",
                disabled=True,
            )

            # Hiện ảnh tìm được (nếu có)
            image_url = post.get("image_url")
            if image_url:
                st.markdown("**🖼 Ảnh AI tìm được:**")
                st.image(image_url, width=400)

            # Upload ảnh tùy chọn
            st.markdown("**📤 Upload ảnh của bạn (tùy chọn — ghi đè ảnh AI):**")
            uploaded = st.file_uploader(
                "Chọn ảnh JPG/PNG",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"upload_{run_id}",
            )

            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button(f"✅ Duyệt & Đăng lên Facebook", key=f"approve_{run_id}", use_container_width=True):
                    img_bytes = uploaded.read() if uploaded else None
                    img_name = uploaded.name if uploaded else None
                    orchestrator.approve_and_publish(run_id, img_bytes, img_name)
                    st.success("🚀 Đang đăng lên Facebook...")
            with col_reject:
                if st.button(f"❌ Bỏ qua bài này", key=f"reject_{run_id}", use_container_width=True):
                    orchestrator.reject_post(run_id)
                    st.warning("🗑️ Đã bỏ qua bài.")
                    st.rerun()

    st.markdown("---")

review_panel()

# ── LIVE MONITOR (tự refresh mỗi 5 giây) ──────────────────────
@st.fragment(run_every=5)
def live_monitor():
    status = orchestrator.get_status()
    logs = orchestrator.execution_logs

    # Status bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Status", "🟢 RUNNING" if status["is_running"] else "🔴 STOPPED")
    with col2:
        last = status["last_execution"]
        st.metric("Last Execution", last[:16].replace("T", " ") if last else "Never")
    with col3:
        st.metric("📤 Đăng lần 1", settings.publisher_time)
    with col4:
        st.metric("📤 Đăng lần 2", settings.publisher_time_2)

    # Hiện agent đang chạy
    if logs:
        last_log = logs[-1]
        agent = last_log["agent"]
        log_status = last_log["status"]

        AGENT_STEPS = {
            "Scraper":   ("1/6", "🔍 Đang cào tin tức từ internet..."),
            "Processor": ("2-5/6", "⚙️ Đang filter → viết bài → tìm ảnh → SEO..."),
            "Publisher": ("6/6", "📤 Đang đăng lên Facebook..."),
        }
        step, desc = AGENT_STEPS.get(agent, ("?", "Đang xử lý..."))

        if log_status == "STARTED":
            st.info(f"**Bước {step}** — {desc}")
            with st.spinner(f"{agent} Agent đang chạy..."):
                pass
        elif log_status == "COMPLETED":
            st.success(f"✅ **{agent}** hoàn tất — xem bài chờ duyệt ở trên ☝️")
        elif log_status in ("PUBLISHED", "SKIPPED"):
            st.success(f"✅ **Đăng bài xong!** ({log_status})")
        elif log_status == "FAILED":
            st.error(f"❌ **{agent}** thất bại: {last_log.get('error', '')}")

    st.markdown("---")
    st.subheader("📋 Log chi tiết (tự cập nhật mỗi 5 giây)")

    if logs:
        rows = []
        for log in reversed(logs[-50:]):
            icon = {
                "STARTED": "🔵",
                "COMPLETED": "🟢",
                "FAILED": "🔴",
                "PUBLISHED": "✅",
                "SKIPPED": "⚠️",
            }.get(log["status"], "⚪")
            rows.append({
                "Thời gian": log["timestamp"][:19].replace("T", " "),
                "": icon,
                "Agent": log["agent"],
                "Trạng thái": log["status"],
                "Lỗi": log.get("error") or "-",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=400)
    else:
        st.info("📭 Chưa có log. Bấm RUN PIPELINE NOW để bắt đầu.")

    # ── BÀI ĐÃ ĐĂNG THÀNH CÔNG ────────────────────────────────
    if orchestrator.published_posts:
        st.markdown("---")
        st.subheader("✅ Bài đã đăng thành công")
        for post in reversed(orchestrator.published_posts):
            st.success(
                f"🕐 **{post['time']}** — "
                f"[Xem bài viết trên Facebook]({post['url']})  "
                f"*(Post ID: {post['post_id']})*"
            )

    st.caption(f"🕐 {datetime.now(TZ).strftime('%H:%M:%S')} ICT | Tự cập nhật mỗi 5 giây")

live_monitor()

# ── SCHEDULE INFO ──────────────────────────────────────────────
st.markdown("---")
st.subheader("🕐 Lịch đăng bài")
col1, col2 = st.columns(2)
with col1:
    st.info(f"""
**Lần 1 (Unsplash)**
- 🔍 {settings.scraper_time} — Cào tin tức
- ✍️ {settings.processor_time} — AI viết bài → chờ duyệt
- 📤 {settings.publisher_time} — Tự đăng nếu đã duyệt
    """)
with col2:
    st.info(f"""
**Lần 2 (Pexels)**
- 🔍 {settings.scraper_time_2} — Cào tin tức
- ✍️ {settings.processor_time_2} — AI viết bài → chờ duyệt
- 📤 {settings.publisher_time_2} — Tự đăng nếu đã duyệt
    """)
