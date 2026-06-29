# 🔑 Setup API Keys - Hướng Dẫn Chi Tiết

## 📋 Table of Contents
1. [OpenAI API Key](#1-openai-api-key) - AI viết bài
2. [Ollama (Free Alternative)](#2-ollama-free-alternative) - AI local, miễn phí
3. [Facebook Access Token](#3-facebook-access-token) - Post lên Facebook
4. [Unsplash Access Key](#4-unsplash-access-key) - Tải ảnh
5. [Testing](#5-testing) - Kiểm tra hoạt động

---

## 1. OpenAI API Key

### ✨ **Lợi Ích:**
- Viết bài chuyên nghiệp, nhanh (~30 giây)
- Chất lượng cao, natural language
- Hỗ trợ tiếng Việt tốt

### ⚠️ **Chi Phí:**
- ~$0.01-0.05 per post
- ~$0.30-1.50 per day (50 posts)
- ~$10/month (300 posts)

### 📍 **Cách Lấy:**

**Bước 1: Tạo OpenAI Account**
```
1. Vào: https://platform.openai.com
2. Sign up (hoặc login)
3. Verify email + add payment method (credit card)
```

**Bước 2: Generate API Key**
```
1. Vào: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy key: sk-proj-xxxxxxxxxxxxx
4. Save somewhere safe (không share!)
```

**Bước 3: Add vào .env**
```bash
# Mở .env file
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo
OPENAI_MODEL_MINI=gpt-4o-mini
USE_OLLAMA=false
```

**Bước 4: Test**
```bash
python test_agents_with_ai.py
```

### 💳 **Setup Payment:**
1. https://platform.openai.com/account/billing/overview
2. Add credit card
3. Set usage limits (ngăn charge quá nhiều)
4. Monitor usage: https://platform.openai.com/account/usage/overview

---

## 2. Ollama (Free Alternative)

### ✨ **Lợi Ích:**
- 100% free, chạy local
- Không cần internet (sau khi download)
- Riêng tư, không gửi data lên cloud

### ⚠️ **Nhược Điểm:**
- Chậm hơn OpenAI (3-5 phút per post)
- Chất lượng bài viết không tốt bằng
- Cần RAM 8GB+ (llama2 chạy ~6GB)

### 📍 **Cách Cài:**

**Bước 1: Download Ollama**
```
1. Vào: https://ollama.ai
2. Click "Download"
3. Chọn OS (Windows/Mac/Linux)
4. Cài đặt như app bình thường
```

**Bước 2: Pull Model**
```bash
# Mở Terminal/PowerShell
ollama pull llama2

# Hoặc model tốt hơn:
ollama pull mistral
ollama pull neural-chat
```

**Bước 3: Start Ollama Server**
```bash
# Terminal 1 - chạy server
ollama serve

# Terminal 2 - kiểm tra
curl http://localhost:11434/api/tags
```

**Bước 4: Config .env**
```bash
# .env đã có sẵn, chỉ cần:
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
OPENAI_API_KEY=
```

**Bước 5: Test**
```bash
python test_agents_with_ai.py
# (chạy chậm, but completely free!)
```

### 🎯 **Comparison: OpenAI vs Ollama**

| Aspect | OpenAI | Ollama |
|--------|--------|--------|
| Speed | ⚡ 30 sec | 🐢 3-5 min |
| Cost | 💰 $0.01-0.05 | 🆓 Free |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Setup | 5 min | 15 min |
| RAM | ~1GB | 8GB+ |
| Internet | Required | After download |

**Khuyến Nghị:** Dùng OpenAI nếu có budget, Ollama nếu muốn free.

---

## 3. Facebook Access Token

### ✨ **Mục Đích:**
- Post bài lên Facebook Page thực tế
- Không có thì chỉ lưu vào database, không post

### ⚠️ **Hạn Chế:**
- Cần có Facebook Page
- Token có hạn (60 ngày)
- Cần refresh định kỳ

### 📍 **Cách Lấy:**

**Bước 1: Tạo Facebook App**
```
1. Vào: https://developers.facebook.com/apps
2. Click "Create App"
3. Chọn "Business" type
4. Nhập thông tin app
5. Click "Create App"
```

**Bước 2: Setup Facebook Login**
```
1. Vào app settings
2. Add "Facebook Login" product
3. Configure OAuth:
   - Valid OAuth Redirect URIs: http://localhost:3000
   - Valid Domains: localhost
```

**Bước 3: Generate Long-Lived Token**
```bash
# Cách 1: Dùng Graph API Explorer
1. Vào: https://developers.facebook.com/tools/explorer
2. Select app của bạn
3. Select "Page" (não User)
4. Click "Get Token"
5. Get "Page Access Token"

# Cách 2: Dùng Terminal
curl "https://graph.instagram.com/oauth/authorize?client_id={app-id}&redirect_uri={redirect-uri}&scope=pages_read_engagement,pages_manage_metadata,pages_read_user_content,pages_manage_posts&response_type=code"
```

**Bước 4: Add vào .env**
```bash
FACEBOOK_ACCESS_TOKEN=EAABsbCS1iHgBAxxxxxx
FACEBOOK_PAGE_ID=100063549952241
FACEBOOK_API_VERSION=v18.0
```

**Bước 5: Test**
```bash
# Xem page info
curl "https://graph.facebook.com/v18.0/{PAGE_ID}?access_token={TOKEN}"
```

### 🔄 **Refresh Token:**
```bash
# Token expire sau 60 ngày
# Tạo long-lived token:
curl -i -X GET "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}"
```

---

## 4. Unsplash Access Key

### ✨ **Mục Đích:**
- Tải ảnh chuyên nghiệp từ Unsplash
- Mỗi post có 1 ảnh đẹp

### ⚠️ **Rate Limit:**
- 50 requests/hour (free)
- 5000 requests/month (free)

### 📍 **Cách Lấy:**

**Bước 1: Create Unsplash Account**
```
1. Vào: https://unsplash.com
2. Sign up / Login
3. Verify email
```

**Bước 2: Register Application**
```
1. Vào: https://unsplash.com/oauth/applications
2. Click "New Application"
3. Accept terms
4. Fill form:
   - App name: Facebook Automation
   - Description: Auto posting to Facebook
   - Intended use: Commercial
```

**Bước 3: Get Access Key**
```
1. Click created app
2. Copy "Access Key" (starts with random string)
3. Save to .env:

UNSPLASH_ACCESS_KEY=xxxxxxxxxxxxx
```

**Bước 4: Test**
```bash
curl "https://api.unsplash.com/search/photos?query=technology&client_id={ACCESS_KEY}"
```

---

## 5. Testing

### ✅ **Test Các API Keys:**

**Test 1: Check Configuration**
```bash
cd D:\facebook-automation-pipeline
python -c "
from config.config import settings
print(f'OpenAI: {\"SET\" if settings.openai_api_key else \"NOT SET\"}')
print(f'Ollama: {\"ENABLED\" if settings.use_ollama else \"DISABLED\"}')
print(f'Unsplash: {\"SET\" if settings.unsplash_access_key != \"test_key\" else \"NOT SET\"}')
print(f'Facebook: {\"SET\" if \"test\" not in settings.facebook_access_token else \"NOT SET\"}')
"
```

**Test 2: Agents with AI**
```bash
# Viết bài với AI
python test_agents_with_ai.py

# Xem kết quả
# → Nếu có API key, sẽ thấy AI viết bài thực sự
# → Nếu không, sẽ demo output
```

**Test 3: Full Pipeline**
```bash
# Chạy tất cả 6 agents
python simple_pipeline_demo.py

# Xem kết quả:
# - Cào articles ✅
# - Lọc articles ✅
# - Viết bài ✅
# - Tạo ảnh ✅
# - Tối ưu ✅
# - Publish ✅
```

**Test 4: Real System**
```bash
# Start orchestrator
python main.py

# Mở http://localhost:8501
# Bấm "START SYSTEM"
# Check logs
```

---

## 📊 **Bảng Quyết Định**

| Mục Đích | Cần | Khuyến Nghị |
|----------|------|----------|
| Test agents viết bài | ❌ | Không cần, test trước |
| AI thực tế | ✅ OpenAI hoặc Ollama | OpenAI nếu có budget |
| Post lên Facebook | ✅ | Bắt buộc để auto-post |
| Tải ảnh | ✅ | Khuyến khích |

---

## 🎯 **Scenario:**

### **Scenario 1: Test Local (No Cost)**
```bash
USE_OLLAMA=true
FACEBOOK_ACCESS_TOKEN=test_token
UNSPLASH_ACCESS_KEY=test_key

# Chạy demo:
python simple_pipeline_demo.py
```

### **Scenario 2: Production (Auto Post Real)**
```bash
OPENAI_API_KEY=sk-proj-xxxxx
FACEBOOK_ACCESS_TOKEN=EAAxxxxx (real token)
UNSPLASH_ACCESS_KEY=xxxxx (real key)

# Run:
python main.py
# → System auto post lên Facebook hàng ngày!
```

---

## ⚡ **Troubleshooting**

| Error | Fix |
|-------|-----|
| `Invalid OpenAI API key` | Check API key in https://platform.openai.com/api-keys |
| `Ollama connection refused` | Run `ollama serve` in terminal |
| `Facebook token invalid` | Regenerate token at https://developers.facebook.com/tools/explorer |
| `Unsplash not found` | Check access key at https://unsplash.com/oauth/applications |
| `Rate limit exceeded` | Wait 1 hour or upgrade plan |

---

## 📞 **Help & Resources**

- OpenAI Docs: https://platform.openai.com/docs
- Ollama Docs: https://github.com/ollama/ollama
- Facebook API: https://developers.facebook.com/docs
- Unsplash API: https://unsplash.com/napi

---

**Ready to setup? Start with Test 1! 🚀**
