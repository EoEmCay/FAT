# 🚀 Facebook Automation Pipeline

AI-powered system to automatically create, optimize, and publish content to Facebook fanpage.

## 📋 Features

✅ **6 Intelligent Agents**
- Agent 1: Scraper & Trend Hunter (Cào dữ liệu)
- Agent 2: Filter & Fact-Checker (Lọc tin)
- Agent 3: Content Writer (Viết bài)
- Agent 4: Design & Prompt Engineer (Tạo ảnh)
- Agent 5: SEO & Meta Optimizer (Tối ưu)
- Agent 6: Publisher Agent (Đăng bài)

✅ **Automated Scheduling** (24/24)
- 6:00 AM: Scrape trending articles
- 11:00 AM: Process & optimize content
- 12:00 PM: Publish to Facebook

✅ **Web UI** (Streamlit)
- Real-time monitoring
- Execution logs
- System status dashboard

✅ **Production Ready**
- PostgreSQL database
- Error handling & retries
- Email & Telegram notifications
- Docker support

## 🚀 Installation

### 1. Clone repository
```bash
cd D:/facebook-automation-pipeline
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup database
```bash
docker-compose up -d
```

### 5. Configure .env
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 6. Initialize database
```bash
python -c "from src.database.db import init_db; init_db()"
```

### 7. Run system
```bash
python main.py
```

The UI will be available at **http://localhost:8501**

## 📖 Usage

1. Open browser: http://localhost:8501
2. Click **[▶️ START SYSTEM]** button
3. Monitor execution logs in real-time
4. Check Facebook page for published posts at 12:00 PM

## ⚙️ Configuration

Edit `.env` file to configure:

- **Database**: PostgreSQL connection
- **OpenAI API**: GPT model selection
- **Facebook**: Page ID and access token
- **Schedule**: Timing for each agent
- **Notifications**: Email & Telegram settings

## 📂 Project Structure

```
facebook-automation-pipeline/
├── config/
│   └── config.py                 # Configuration
├── src/
│   ├── agents/
│   │   ├── scraper_agent.py      # Agent 1
│   │   ├── filter_agent.py       # Agent 2
│   │   ├── writer_agent.py       # Agent 3
│   │   ├── designer_agent.py     # Agent 4
│   │   ├── seo_agent.py          # Agent 5
│   │   ├── publisher_agent.py    # Agent 6
│   │   └── __init__.py
│   ├── database/
│   │   ├── models.py             # DB models
│   │   ├── db.py                 # DB connection
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logging.py            # Logging
│   │   ├── notifications.py      # Email/Telegram
│   │   └── __init__.py
│   ├── workflows.py              # Main pipeline
│   ├── orchestrator.py           # Scheduler
│   └── __init__.py
├── ui/
│   └── streamlit_app.py          # Web UI
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
├── .env.example                   # Config template
└── docker-compose.yml            # Docker setup
```

## 🔧 Architecture

```
Streamlit UI ↔ Orchestrator (APScheduler) ↔ CrewAI (6 Agents) ↔ PostgreSQL
```

## 🐛 Troubleshooting

### Issue: "Connection refused" (Database)
```bash
docker-compose ps
docker-compose restart postgres
```

### Issue: "API Key invalid"
- Check .env file
- Verify API keys have proper permissions

### Issue: "Scheduler not running"
```python
from src.orchestrator import orchestrator
print(orchestrator.get_status())
```

## 📝 System Prompts

Each agent has detailed system prompts that guide their behavior:
- Scraper: Scrapes 35-50 articles from multiple sources
- Filter: Filters to 5-10 highest-quality articles
- Writer: Writes Facebook posts with engaging copy
- Designer: Creates image search queries for Unsplash
- SEO: Optimizes hashtags and metadata
- Publisher: Validates and publishes to Facebook

## 🚀 Deployment

### Using Docker
```bash
docker build -t facebook-automation .
docker run -p 8501:8501 --env-file .env facebook-automation
```

### Using systemd (Linux)
```bash
sudo cp facebook-automation.service /etc/systemd/system/
sudo systemctl start facebook-automation
sudo systemctl enable facebook-automation
```

## 📊 Monitoring

### View logs
```bash
tail -f logs/orchestrator.log
```

### Check database
- Open pgAdmin at http://localhost:5050
- Username: admin@example.com
- Password: admin

## 🤝 Contributing

1. Create feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 💬 Support

For issues, questions, or suggestions:
- GitHub Issues
- Email: support@example.com
- Telegram: @support-bot
