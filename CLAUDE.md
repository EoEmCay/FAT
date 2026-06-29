# 🚀 Facebook Automation Pipeline - Project Guide

## 📌 Tên Dự Án
**Facebook Automation Pipeline** - Hệ thống tự động tạo, tối ưu, và đăng bài lên Facebook Fanpage

---

## 🎯 Mục Đích
Xây dựng hệ thống **AI-powered, fully automated 24/24** để:
1. **6:00 AM** → Cào dữ liệu từ các nguồn tin tức (Medium, GitHub, Hugging Face)
2. **11:00 AM** → Lọc, viết, thiết kế, tối ưu bài viết
3. **12:00 PM** → Đăng bài tự động lên Facebook Graph API

**Mô tả ngắn gọn:** Một pipeline hoàn toàn tự động, không cần can thiệp, từ scraping → writing → publishing

---

## 🏗️ Kiến Trúc Tổng Quan

```
┌─────────────────┐
│  Streamlit UI   │ ← Giao diện web (START/STOP/Logs)
└────────┬────────┘
         │
┌────────▼────────┐
│  Orchestrator   │ ← APScheduler (6AM, 11AM, 12PM)
│  (scheduler)    │
└────────┬────────┘
         │
┌────────▼──────────────────┐
│  CrewAI Workflow Pipeline  │
│  Agent 1 → Agent 2 → ... → Agent 6
│  (6 AI agents chạy tuần tự)
└────────┬──────────────────┘
         │
┌────────▼────────┐
│  PostgreSQL DB  │ ← Lưu posts, logs, articles
└─────────────────┘
```

---

## 👥 6 AI Agents (Tách riêng từng file)

| # | Agent | File | Mục đích | Input | Output |
|---|-------|------|---------|-------|--------|
| 1️⃣ | **Scraper & Trend Hunter** | `src/agents/scraper_agent.py` | Cào 50-100 articles từ Medium, GitHub, Hugging Face | (API calls) | 50-100 raw articles |
| 2️⃣ | **Filter & Fact-Checker** | `src/agents/filter_agent.py` | Lọc, verify facts, score articles | 50-100 articles | 5-10 best articles |
| 3️⃣ | **Content Writer** | `src/agents/writer_agent.py` | Viết bài Facebook (hook+body+CTA+hashtag) | 5-10 articles | 5-10 FB posts |
| 4️⃣ | **Designer & Prompt Engineer** | `src/agents/designer_agent.py` | Tạo search queries, download ảnh từ Unsplash | 5-10 posts | Ảnh + metadata |
| 5️⃣ | **SEO & Meta Optimizer** | `src/agents/seo_agent.py` | Tối ưu hashtag, emoji, format cho FB algorithm | 5-10 posts | Optimized posts |
| 6️⃣ | **Publisher Agent** | `src/agents/publisher_agent.py` | Validate data, call Facebook Graph API | 1 post + image | Published ✅ |

---

## 📂 Cấu Trúc File (Option B - Clean & Modular)

```
facebook-automation-pipeline/
├── CLAUDE.md                 ← FILE NÀY (Context toàn bộ)
├── config/
│   └── config.py             ← Load .env, settings
├── src/
│   ├── agents/               ← 6 AI agents (riêng file)
│   │   ├── scraper_agent.py
│   │   ├── filter_agent.py
│   │   ├── writer_agent.py
│   │   ├── designer_agent.py
│   │   ├── seo_agent.py
│   │   ├── publisher_agent.py
│   │   └── __init__.py       ← Imports all agents
│   ├── database/
│   │   ├── models.py         ← Post, ExecutionLog, Article models
│   │   ├── db.py             ← SQLAlchemy engine + session
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logging.py        ← setup_logger() function
│   │   ├── notifications.py  ← Email + Telegram
│   │   └── __init__.py
│   ├── workflows.py          ← FacebookContentPipeline (orchestrate all 6 agents)
│   ├── orchestrator.py       ← Orchestrator class (APScheduler + monitoring)
│   └── __init__.py
├── ui/
│   └── streamlit_app.py      ← Web dashboard (START/STOP buttons + logs)
├── logs/
│   └── orchestrator.log      ← Auto-generated (rotated 10MB files)
├── main.py                   ← Entry point (python main.py)
├── requirements.txt          ← pip install -r requirements.txt
├── .env.example              ← Config template
├── .env                       ← ACTUAL secrets (gitignored)
├── docker-compose.yml        ← PostgreSQL + pgAdmin
└── README.md                 ← Public documentation
```

---

## ⚙️ Configuration (.env)

**File:** `.env` (copy from `.env.example`)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/facebook_automation

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_MODEL_MINI=gpt-4o-mini

# Facebook
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...

# Schedule (Vietnam timezone)
SCRAPER_TIME=06:00      # Run at 6 AM daily
PROCESSOR_TIME=11:00    # Run at 11 AM daily
PUBLISHER_TIME=12:00    # Run at 12 PM daily

# APIs
UNSPLASH_ACCESS_KEY=...
GITHUB_TOKEN=...
HUGGINGFACE_TOKEN=...

# Notifications (optional)
SMTP_USERNAME=...
SMTP_PASSWORD=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

---

## 🔄 Workflow Flow (Timeline)

### **Daily Flow:**

```
6:00 AM
├─ Orchestrator triggers _execute_scraper()
├─ Agent 1: Scraper cào articles
├─ Save to execution_logs
└─ Status: ✅ COMPLETED

11:00 AM
├─ Orchestrator triggers _execute_processor()
├─ Load articles from DB
├─ Agent 2: Filter
├─ Agent 3: Write
├─ Agent 4: Designer (download images)
├─ Agent 5: SEO optimize
└─ Status: ✅ COMPLETED

12:00 PM
├─ Orchestrator triggers _execute_publisher()
├─ Load optimized post from DB
├─ Agent 6: Validate + prepare Facebook payload
├─ Call Facebook Graph API POST /feed
├─ Get back post_id
├─ Save to posts table (status='posted')
├─ Send Telegram notification ✅
└─ Status: ✅ PUBLISHED
```

---

## 🚀 Cách Chạy

### **Setup (one-time)**
```bash
cd D:/facebook-automation-pipeline

# 1. Virtual env
python -m venv venv
venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Database
docker-compose up -d
python -c "from src.database.db import init_db; init_db()"

# 4. Config
copy .env.example .env
# Edit .env with your API keys
```

### **Run (daily)**
```bash
# Terminal 1: Start the system
python main.py

# UI opens at: http://localhost:8501
# Click "▶️ START SYSTEM" button
# System now runs automatically at 6AM, 11AM, 12PM
```

---

## 📊 Database Schema

### **posts** table (Facebook published posts)
```sql
id, facebook_post_id, title, hook, body, insight, cta, 
hashtags, image_url, status, posted_at, reach, engagement, ...
```

### **execution_logs** table (Track each agent run)
```sql
agent_name, status (success/error), result_summary, 
execution_id, error_message, executed_at, ...
```

### **articles** table (Scraped articles)
```sql
source, title, url, summary, verified, fact_check_score, 
selected_for_post, selection_score, scraped_at, ...
```

---

## 🎨 Agent System Prompts (Summary)

**Agent 1 (Scraper):**
- Input: (API calls to Medium, GitHub, Hugging Face)
- Output: JSON with [title, url, summary, views, tags, ...]
- Constraint: 35-50 articles, last 7 days, no duplicates

**Agent 2 (Filter):**
- Input: 35-50 raw articles
- Output: JSON with [title, summary, score(0-10), verified, why_important, ...]
- Constraint: Keep only 5-10 articles (score >= 6)

**Agent 3 (Writer):**
- Input: 5-10 filtered articles
- Output: JSON with [hook, body, insight, cta, hashtags, emoji_count, ...]
- Format: Hook + Body(3-5 paragraphs) + CTA + Hashtag (max 10)

**Agent 4 (Designer):**
- Input: 5-10 written posts
- Output: JSON with [unsplash_search_query, image_url, alt_text, ...]
- Action: Download images via Unsplash API

**Agent 5 (SEO):**
- Input: 5-10 posts
- Output: JSON with [optimized_content, hashtags_optimized, best_posting_time, readability_score, ...]
- Optimize: Hashtags (trending+niche), emoji count, formatting, readability

**Agent 6 (Publisher):**
- Input: 5-10 optimized posts + images
- Output: JSON with [status, facebook_payload, validation_result, ...]
- Action: Pick best post → Call Facebook Graph API → Get post_id

---

## 🔍 Key Classes & Functions

### **Orchestrator** (`src/orchestrator.py`)
- `start_system()` → Schedule 3 tasks (scraper, processor, publisher)
- `stop_system()` → Shutdown scheduler
- `get_status()` → Return {is_running, current_status, recent_logs}
- `get_execution_logs()` → Return recent logs

### **FacebookContentPipeline** (`src/workflows.py`)
- `run_full_pipeline()` → Run all 6 agents sequentially
- Returns: {status, pipeline_completed, post_id, facebook_url, summary}

### **Database** (`src/database/`)
- `init_db()` → Create all tables
- `get_session()` → Get SQLAlchemy session
- Models: Post, ExecutionLog, Article, AgentConfig

---

## ✅ Checklist Khi Làm Việc Trên Project

- [ ] Có .env file với tất cả API keys?
- [ ] PostgreSQL running (`docker-compose up -d`)?
- [ ] Database initialized (`python -c "from src.database.db import init_db; init_db()"`)?
- [ ] Tất cả requirements installed (`pip install -r requirements.txt`)?
- [ ] Muốn chạy full pipeline? Bấm "START SYSTEM" ở Streamlit UI
- [ ] Muốn test Agent nào riêng? Import từ `src.agents` và call `.create()` method
- [ ] Muốn check logs? Mở `logs/orchestrator.log` hoặc Streamlit UI
- [ ] Muốn check database? Mở pgAdmin ở http://localhost:5050

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Connection refused" (DB) | `docker-compose restart postgres` |
| "API Key invalid" | Check .env has CORRECT keys with permissions |
| "Module not found" | `pip install -r requirements.txt` |
| "Scheduler not running" | Check `orchestrator.get_status()['is_running']` |
| "No post generated" | Check `execution_logs` in Streamlit UI for errors |

---

## 📝 Coding Standards

- **Language:** Python 3.9+
- **Framework:** CrewAI (agents), APScheduler (scheduling), Streamlit (UI)
- **Database:** PostgreSQL + SQLAlchemy ORM
- **API Calls:** Facebook Graph API v18.0
- **Logging:** Python logging module (file + console)
- **Error Handling:** Try-except with logging, retries with exponential backoff
- **Comments:** Minimal - only for WHY, not WHAT
- **Naming:** snake_case for functions/variables, PascalCase for classes

---

## 🚀 Deployment

**Local (Development):**
```bash
python main.py
```

**Docker (Production):**
```bash
docker build -t facebook-automation .
docker run -p 8501:8501 --env-file .env facebook-automation
```

---

## 📚 Files You'll Most Likely Edit

1. **Add new data source?** → Edit `src/agents/scraper_agent.py`
2. **Change filter criteria?** → Edit `src/agents/filter_agent.py`
3. **Modify post format?** → Edit `src/agents/writer_agent.py`
4. **Change schedule time?** → Edit `.env` (SCRAPER_TIME, PROCESSOR_TIME, PUBLISHER_TIME)
5. **Add new feature?** → Create new file in `src/` or `src/agents/`

---

## 🎓 How to Understand Each Agent

**Rule of Thumb:**
```
Each Agent file has:
├── class AgentName
│   ├── @staticmethod
│   │   └── def create() → Agent (CrewAI Agent object)
│   └── @staticmethod
│       └── def create_task() → Task (with detailed description)
└── Optionally: async helper methods (like download_images)
```

**Example:** Read `src/agents/scraper_agent.py`
- `ScraperAgent.create()` → Returns Agent with role/goal/backstory
- `ScraperAgent.create_task()` → Returns Task with detailed prompt
- Task description = System Prompt (tells Agent exactly what to do)

---

## 🔗 Integration Points

**External APIs:**
- Facebook Graph API v18.0 (POST /feed)
- Medium.com API
- GitHub API (trending repos)
- Hugging Face API (trending models)
- Unsplash API (image search)
- OpenAI API (gpt-4-turbo)

**Internal Integrations:**
- Orchestrator → CrewAI Pipeline
- Agents → Database (save results)
- Database → Streamlit UI (display logs)
- Orchestrator → Notifications (email/telegram on success/failure)

---

## 💾 Remember

- This is a **COMPLETE, PRODUCTION-READY** system
- No additional setup needed beyond `.env` configuration
- All 6 agents are implemented and ready to use
- Database schema is pre-defined and auto-created on first run
- Streamlit UI is ready to monitor the system 24/24
- All error handling, logging, and notifications are built-in

**Just:** Edit `.env` → Run `python main.py` → Click "START SYSTEM" → Done ✅

---

**Last Updated:** 2026-06-28  
**Version:** 1.0.0  
**Status:** Production-Ready 🚀
