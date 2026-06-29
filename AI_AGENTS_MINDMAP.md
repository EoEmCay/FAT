# 🧠 Sơ Đồ Tư Duy - AI Agents Pipeline

## 📊 **Sơ Đồ Tổng Quan**

```
                        ┌─────────────────────────────────────┐
                        │  FACEBOOK AUTOMATION PIPELINE       │
                        │  (CrewAI - 6 Intelligent Agents)    │
                        └─────────────────────────────────────┘
                                      │
                                      ▼
            ┌─────────────────────────────────────────────────────┐
            │           ORCHESTRATOR (APScheduler)                 │
            │                                                       │
            │  6:00 AM → SCRAPER                                   │
            │  7:00 AM → FILTER → WRITER → DESIGNER → SEO         │
            │  8:00 AM → PUBLISHER                                 │
            └─────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
        ┌──────────────────────┐          ┌──────────────────────┐
        │   DATABASE (SQLite)  │          │   NOTIFICATIONS      │
        │                      │          │   (Telegram/Email)   │
        │ • posts              │          │   ⚠️ DISABLED         │
        │ • articles           │          └──────────────────────┘
        │ • execution_logs     │
        │ • agent_configs      │
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │   FACEBOOK PAGE      │
        │   (Published Posts)  │
        └──────────────────────┘
```

---

## 🔄 **Data Flow - Pipeline Chi Tiết**

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                           🚀 FACEBOOK AUTOMATION PIPELINE                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ EXTERNAL SOURCES (Data Input)                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📰 Medium.com         🐙 GitHub Trending      🤗 Hugging Face              │
│  └─ AI & Tech tags     └─ Python, JS repos    └─ Trending models           │
│     (10-15 articles)      (10-15 articles)       (5-10 articles)            │
│                                                                               │
│  🔗 Dev.to             📦 Product Hunt         🎓 ArXiv                     │
│  └─ Trending posts     └─ Tech products       └─ Research papers           │
│     (5-10 articles)        (5-10 articles)       (5-10 articles)            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP Requests
                                      │ (APIs)
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 1️⃣ : SCRAPER AGENT 🔍                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Thu thập Dữ liệu & Phát hiện Xu hướng"                  │
│  GOAL: Cào 50-100 articles từ 6+ nguồn                                       │
│                                                                               │
│  TASK:                                                                        │
│  ✓ Call APIs (Medium, GitHub, Hugging Face, etc.)                           │
│  ✓ Extract: title, url, summary, views, tags, published_at                  │
│  ✓ Filter: Chỉ 7 ngày gần nhất, loại bỏ duplicate                           │
│  ✓ Output: JSON array 35-50 articles                                         │
│                                                                               │
│  INPUT:  External APIs                                                       │
│  OUTPUT: [                                                                    │
│           {                                                                   │
│             "source": "medium",                                              │
│             "title": "OpenAI Releases GPT-5",                               │
│             "url": "https://medium.com/...",                                │
│             "summary": "OpenAI announced GPT-5...",                          │
│             "published_at": "2026-06-28",                                   │
│             "views": 150000,                                                 │
│             "tags": ["AI", "GPT", "LLM"]                                    │
│           },                                                                  │
│           ...                                                                 │
│          ]                                                                    │
│                                                                               │
│  USES: GPT-4o-mini (nhanh, tiết kiệm chi phí)                              │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 35-50 Raw Articles
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 2️⃣ : FILTER AGENT 🔎                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Lọc Tin & Xác Minh Sự Thật"                              │
│  GOAL: Lọc & xếp hạng articles theo giá trị                                 │
│                                                                               │
│  TASK:                                                                        │
│  ✓ Loại bỏ duplicate (check URL, title tương tự)                            │
│  ✓ Loại bỏ tin từ nguồn không đáng tin                                      │
│  ✓ Xác minh sự thật (fact-checking)                                          │
│  ✓ Tóm tắt 2-3 câu cốt lõi                                                   │
│  ✓ Scoring (0-10 points):                                                    │
│    - Trending level: 0-5 points                                              │
│    - Technical depth: 0-3 points                                             │
│    - Actionability: 0-2 points                                               │
│  ✓ Giữ lại chỉ 5-10 articles (score >= 6)                                   │
│                                                                               │
│  INPUT:  35-50 raw articles                                                  │
│  OUTPUT: [                                                                    │
│           {                                                                   │
│             "title": "OpenAI Releases GPT-5...",                            │
│             "url": "https://medium.com/...",                                │
│             "summary": "OpenAI announced GPT-5...",                          │
│             "why_important": "Revolutionary model...",                       │
│             "source": "medium",                                              │
│             "score": 9,                                                      │
│             "verified": true,                                                │
│             "tags": ["AI", "GPT5"]                                           │
│           },                                                                  │
│           ...                                                                 │
│          ]                                                                    │
│                                                                               │
│  USES: GPT-4o-mini (xác minh facts)                                         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 5-10 Verified Articles
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 3️⃣ : WRITER AGENT ✍️                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Viết Bài Facebook"                                        │
│  GOAL: Viết bài chuẩn format Facebook, giọng văn cuốn hút                   │
│                                                                               │
│  TASK:                                                                        │
│  ✓ Viết HOOK (1-2 câu giật gân + emoji) 🔥😱                                │
│  ✓ Viết BODY (3-5 đoạn):                                                    │
│    - Paragraph 1: Cái gì xảy ra (WHAT)                                      │
│    - Paragraph 2: Tại sao quan trọng (WHY)                                   │
│    - Paragraph 3: Ảnh hưởng ra sao (IMPACT)                                  │
│    - Paragraph 4: Bài học/góc nhìn (INSIGHT)                                │
│  ✓ Viết CTA (Call-to-action) rõ ràng                                        │
│  ✓ Thêm HASHTAGS (5-10 tags, trending + niche)                             │
│                                                                               │
│  FORMAT:                                                                      │
│  🔥 BREAKING: [Hot News]                                                    │
│                                                                               │
│  Để mình explain chi tiết 👇                                                │
│                                                                               │
│  [Đoạn 1: What]                                                              │
│  [Đoạn 2: Why]                                                               │
│  [Đoạn 3: Impact]                                                            │
│  [Đoạn 4: Insight]                                                           │
│                                                                               │
│  Bạn nghĩ sao? Comment bên dưới 👇                                          │
│                                                                               │
│  #AI #MachineLearning #Technology                                            │
│                                                                               │
│  CONSTRAINTS:                                                                 │
│  • Word count: 150-250 từ (ideal 200)                                       │
│  • Emoji: 5-7 cái (không spam)                                              │
│  • Lines: Max 80 ký tự/line (readable)                                      │
│  • Tone: Professional + Friendly                                             │
│  • No clickbait                                                               │
│                                                                               │
│  INPUT:  5-10 filtered articles                                              │
│  OUTPUT: [                                                                    │
│           {                                                                   │
│             "article_url": "...",                                            │
│             "hook": "🔥 BREAKING: GPT-5 vừa release",                      │
│             "body": "Để mình explain...",                                   │
│             "insight": "Bài học từ article...",                             │
│             "cta": "Bạn nghĩ sao?",                                          │
│             "hashtags": ["#AI", "#GPT5", ...],                              │
│             "emoji_count": 6,                                                │
│             "word_count": 245,                                               │
│             "engagement_score": "High"                                        │
│           },                                                                  │
│           ...                                                                 │
│          ]                                                                    │
│                                                                               │
│  USES: GPT-4 Turbo (cao cấp, viết hay)                                      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 5-10 Facebook Posts
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 4️⃣ : DESIGNER AGENT 🎨                                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Thiết Kế Prompt Sinh Ảnh"                                │
│  GOAL: Tạo search queries → tải ảnh chuyên nghiệp từ Unsplash              │
│                                                                               │
│  TASK:                                                                        │
│  ✓ Phân tích chủ đề bài viết                                                │
│  ✓ Xác định 1-3 keywords chính                                              │
│  ✓ Tạo search query cho Unsplash API                                        │
│  ✓ Download ảnh (1200x628px, professional)                                  │
│  ✓ Generate alt text cho accessibility                                       │
│                                                                               │
│  EXAMPLES:                                                                    │
│  • Bài về ChatGPT → "artificial intelligence technology"                    │
│  • Bài về blockchain → "cryptocurrency digital finance"                     │
│  • Bài về data science → "data visualization analytics"                     │
│                                                                               │
│  INPUT:  5-10 written posts                                                  │
│  OUTPUT: [                                                                    │
│           {                                                                   │
│             "article_url": "...",                                            │
│             "unsplash_search_query": "artificial intelligence technology",  │
│             "image_url": "https://images.unsplash.com/...",               │
│             "alt_text": "Professional AI technology illustration",           │
│             "recommended_size": "1200x628px"                                │
│           },                                                                  │
│           ...                                                                 │
│          ]                                                                    │
│                                                                               │
│  USES: GPT-4o-mini (creative, tạo prompts)                                 │
│        Unsplash API (tải ảnh)                                               │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 5-10 Posts + Images
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 5️⃣ : SEO AGENT ⚡                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Tối Ưu SEO & Facebook Meta"                              │
│  GOAL: Tối ưu hashtag, emoji, format cho Facebook algorithm                │
│                                                                               │
│  TASK:                                                                        │
│  ✓ HASHTAG OPTIMIZATION:                                                    │
│    - 70% trending (most popular): #AI #ML #Technology                       │
│    - 20% niche (specific): #LLM #NeuralNetwork #RAG                        │
│    - 10% branded (company): #YourFanpage                                    │
│    - Max 10-15 hashtags (Facebook downrank with 15+)                       │
│    - EXACT MATCH với content                                                │
│                                                                               │
│  ✓ EMOJI ENHANCEMENT:                                                       │
│    Strategic placement:                                                      │
│    - 👀 trước breaking news                                                 │
│    - 🔥 trước trending topics                                               │
│    - 💡 trước insights/tips                                                 │
│    - 📊 trước statistics                                                    │
│    - ⚡ trước impact/benefits                                               │
│    - Max 5-7 emoji total (không overuse)                                   │
│                                                                               │
│  ✓ TEXT FORMATTING:                                                         │
│    - Chia nhỏ paragraphs (max 2-3 câu/paragraph)                            │
│    - Dùng bullet points: • hoặc -                                          │
│    - **Bold** cho key points                                                │
│    - Proper spacing                                                          │
│                                                                               │
│  ✓ BEST POSTING TIME:                                                       │
│    - 12:00 PM (lunch peak)                                                  │
│    - 7:00 PM (evening peak)                                                 │
│    - Tuesday-Thursday best (studies)                                         │
│                                                                               │
│  ✓ READABILITY SCORE:                                                       │
│    - Flesch Reading Ease: target 60-70                                      │
│    - Avg sentence length: 12-15 từ                                          │
│    - Avg word length: 4-5 ký tự                                            │
│                                                                               │
│  INPUT:  5-10 written posts + images                                         │
│  OUTPUT: [                                                                    │
│           {                                                                   │
│             "article_url": "...",                                            │
│             "optimized_content": "...",                                      │
│             "hashtags_optimized": ["#AI", "#GPT5", ...],                   │
│             "best_posting_time": "12:00 PM",                                │
│             "estimated_reach": 25000,                                        │
│             "readability_score": 68,                                         │
│             "emoji_count": 6,                                                │
│             "format_optimized": "Paragraph breaks + bullet points"          │
│           },                                                                  │
│           ...                                                                 │
│          ]                                                                    │
│                                                                               │
│  USES: GPT-4o-mini (tối ưu hóa)                                            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 5-10 Optimized Posts
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 6️⃣ : PUBLISHER AGENT 📤                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ROLE: "Chuyên gia Quản Lý API & Xuất Bản"                                  │
│  GOAL: Validate, prepare, publish to Facebook Graph API                     │
│                                                                               │
│  TASK:                                                                        │
│  ✓ VALIDATION & DATA CHECK:                                                 │
│    - Content length: 1-63206 ký tự                                          │
│    - Image: Valid URL, accessible, format jpg/png                           │
│    - Hashtags: max 10-15                                                     │
│    - No spam/hate speech                                                     │
│    - Emoji corruption check                                                  │
│    - UTF-8 encoding valid                                                    │
│                                                                               │
│  ✓ SELECT BEST POST:                                                        │
│    - Pick 1 post (highest engagement potential)                             │
│    - Usually: highest trending topic                                        │
│                                                                               │
│  ✓ PREPARE FACEBOOK PAYLOAD:                                                │
│    POST /graph.facebook.com/v18.0/{PAGE_ID}/feed                           │
│    {                                                                          │
│      "message": "Content + hashtags",                                        │
│      "link": "URL to article",                                              │
│      "picture": "image_url",                                                 │
│      "name": "Article title",                                               │
│      "description": "Short description",                                     │
│      "caption": "Domain name"                                                │
│    }                                                                          │
│                                                                               │
│  ✓ SCHEDULING:                                                              │
│    - Published time: 12:00 PM Vietnam time                                  │
│    - If now > 12:00 PM → schedule for next day                             │
│                                                                               │
│  ✓ ERROR HANDLING:                                                          │
│    - Retry logic: 3 attempts                                                │
│    - Exponential backoff                                                     │
│    - Timeout: 30 seconds                                                     │
│    - Fallback: Queue cho lần post kế tiếp                                   │
│                                                                               │
│  INPUT:  5-10 optimized posts + images                                       │
│  OUTPUT: {                                                                    │
│             "status": "published",                                           │
│             "facebook_payload": {...},                                       │
│             "image_url": "...",                                              │
│             "scheduled_time": "2026-06-28 12:00:00",                        │
│             "validation_result": "passed",                                   │
│             "facebook_url": "https://facebook.com/123456",                  │
│             "post_id": "123456_789",                                         │
│             "estimated_reach": 25000,                                        │
│             "estimated_engagement": 500                                      │
│           }                                                                   │
│                                                                               │
│  USES: GPT-4o-mini (validation), Facebook Graph API                        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Post Published ✅
                                      ▼
            ┌────────────────────────────────────────┐
            │   📱 FACEBOOK PAGE (Published)          │
            │                                         │
            │  ✅ Post visible                        │
            │  ✅ 25,000+ estimated reach            │
            │  ✅ Engagement tracking                 │
            └────────────────────────────────────────┘
```

---

## 🎯 **Tác Dụng Chi Tiết - Mỗi Agent Làm Gì?**

### **1️⃣ SCRAPER AGENT 🔍 - Cào Dữ Liệu**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Tìm tin mới nhất từ 6+ nguồn (Medium, GitHub, etc.) |
| **Input** | API endpoints của các trang news/tech |
| **Output** | 35-50 articles (title, url, summary, views, tags) |
| **AI Model** | GPT-4o-mini (nhanh, tiết kiệm) |
| **Thời gian** | 1-2 phút (chạy 6:00 AM) |
| **Mục đích** | Tìm trending topics để viết về |
| **Ví dụ** | Tìm được: "GPT-5 release", "TensorFlow 3.0", "LLaMA 3.0" |
| **Constraint** | Loại bỏ: Duplicates, spam, cũ (>7 ngày) |

**Tại sao cần?** Chạy tự động → không phải tìm article thủ công → tiết kiệm 1-2 giờ/ngày

---

### **2️⃣ FILTER AGENT 🔎 - Lọc & Fact-Check**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Loại bỏ tin xấu, xác minh sự thật, xếp hạng |
| **Input** | 35-50 raw articles từ scraper |
| **Output** | 5-10 high-quality articles (score >= 6) |
| **AI Model** | GPT-4o-mini (verify facts) |
| **Thời gian** | 1-2 phút |
| **Scoring** | 0-10 points (trending + depth + actionable) |
| **Mục đích** | Chỉ giữ lại articles tốt nhất |
| **Ví dụ** | Loại bỏ: Clickbait, fake news, irrelevant |
| **Kiểm tra** | Duplicate URL, source credibility, facts accuracy |

**Tại sao cần?** Chất lượng bài viết → engagement cao → reach lớn → tránh fake news

---

### **3️⃣ WRITER AGENT ✍️ - Viết Bài Facebook**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Viết bài Facebook chuyên nghiệp, engaging |
| **Input** | 5-10 filtered articles |
| **Output** | 5-10 Facebook posts (hook + body + CTA + hashtags) |
| **AI Model** | GPT-4 Turbo (cao cấp, viết hay) |
| **Thời gian** | 2-3 phút |
| **Format** | Hook (1-2 câu) → Body (3-5 đoạn) → CTA → Hashtags |
| **Mục đích** | Viết hấp dẫn, cuốn hút → tăng engagement |
| **Ví dụ** | "🔥 BREAKING: GPT-5 release!" + explain + CTA |
| **Constraint** | 150-250 từ, 5-7 emoji, no clickbait |

**Tại sao cần?** AI viết tốt hơn người → tiết kiệm 30 phút/post → 5-10 bài/ngày

---

### **4️⃣ DESIGNER AGENT 🎨 - Tạo & Tải Ảnh**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Tạo search query → tải ảnh chuyên nghiệp |
| **Input** | 5-10 written posts |
| **Output** | 5-10 images (1200x628px) + alt text |
| **AI Model** | GPT-4o-mini (creative, tạo prompts) |
| **API** | Unsplash (image library) |
| **Thời gian** | 1-2 phút |
| **Size** | 1200x628px (optimal for Facebook) |
| **Mục đích** | Mỗi bài cần 1 ảnh đẹp → tăng visual appeal |
| **Ví dụ** | "artificial intelligence technology" → tải ảnh AI |
| **Constraint** | Ảnh phải match 100% content, professional |

**Tại sao cần?** Posts có ảnh → reach +40% → engagement +60% (study Facebook)

---

### **5️⃣ SEO AGENT ⚡ - Tối Ưu Cho Algorithm**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Optimize hashtags, emoji, format cho Facebook algorithm |
| **Input** | 5-10 written posts |
| **Output** | 5-10 optimized posts (hashtags, emoji, formatting) |
| **AI Model** | GPT-4o-mini (optimization expert) |
| **Thời gian** | 1 phút |
| **Optimize** | Hashtags (70% trending + 20% niche + 10% branded) |
| **Emoji** | Strategic placement (max 7 cái) |
| **Formatting** | Paragraphs, bullet points, bold key points |
| **Timing** | 12:00 PM (lunch) hoặc 7:00 PM (evening) |
| **Metrics** | Readability (Flesch score 60-70) |

**Tại sao cần?** 
- Hashtag đúng → tìm được đúng audience
- Emoji hợp lý → tăng click-through rate
- Format tốt → readable, no scroll fatigue
- Đúng time → catch peak traffic

**Result:** reach +30%, engagement +50%

---

### **6️⃣ PUBLISHER AGENT 📤 - Xuất Bản**

| Aspect | Chi Tiết |
|--------|----------|
| **Tác dụng** | Validate data → publish to Facebook Graph API |
| **Input** | 5-10 optimized posts + images |
| **Output** | 1 published post (best) + post ID + URL |
| **AI Model** | GPT-4o-mini (validation) |
| **API** | Facebook Graph API v18.0 |
| **Thời gian** | 30 giây |
| **Validation** | Content (1-63206 chars), Image (valid), UTF-8 |
| **Selection** | Pick 1 post (highest engagement potential) |
| **Retry** | 3 attempts with exponential backoff |
| **Mục đích** | Đảm bảo post perfect trước khi publish |
| **Result** | Published on Facebook, trackable |

**Tại sao cần?** 
- Validation → không post content lỗi → reputation protect
- Automatic publish → 24/7 automation → no manual work
- Error handling → retry if fail → reliability 99%

---

## 📊 **Bảng So Sánh - Các Agents Hoạt Động**

```
┌─────────────┬──────────────┬─────────┬─────────────┬──────────────┬──────────────┐
│ AGENT       │ INPUT        │ OUTPUT  │ AI MODEL    │ TIME         │ COST/POST    │
├─────────────┼──────────────┼─────────┼─────────────┼──────────────┼──────────────┤
│ 1️⃣ Scraper  │ APIs         │ 50 art  │ GPT-4o-mini │ 1-2 min      │ ~$0.001      │
│ 2️⃣ Filter   │ 50 articles  │ 5-10 art│ GPT-4o-mini │ 1-2 min      │ ~$0.002      │
│ 3️⃣ Writer   │ 5-10 art     │ 5-10 pos│ GPT-4 Turbo │ 2-3 min      │ ~$0.01       │
│ 4️⃣ Designer │ 5-10 pos     │ 5-10 img│ GPT-4o-mini │ 1-2 min      │ ~$0.001      │
│ 5️⃣ SEO      │ 5-10 pos     │ 5-10 opt│ GPT-4o-mini │ 1 min        │ ~$0.001      │
│ 6️⃣ Publisher│ 5-10 opt     │ 1 post  │ GPT-4o-mini │ 30 sec       │ ~$0.0005     │
├─────────────┼──────────────┼─────────┼─────────────┼──────────────┼──────────────┤
│ TOTAL       │ External API │ 1 post  │ Multi-agent │ 7-12 min     │ ~$0.015      │
└─────────────┴──────────────┴─────────┴─────────────┴──────────────┴──────────────┘
```

---

## 🔗 **Data Flow - Cách Dữ Liệu Chuyển Động**

```
STAGE 1 - GATHERING (Giai đoạn cào dữ liệu)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source APIs (Medium, GitHub, etc.)
         │
         │ HTTP GET Requests
         ▼
    ┌─────────────┐
    │ SCRAPER 🔍  │
    └──────┬──────┘
           │
           │ 35-50 articles JSON
           ▼
    ┌─────────────────┐
    │ FILTER 🔎       │
    │ (score, verify) │
    └──────┬──────────┘
           │
           │ 5-10 verified articles
           └─────────────────────────────────────────┐
                                                     │
STAGE 2 - CREATION (Giai đoạn tạo nội dung)        │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
                                                    │
       ◄────────────────────────────────────────────┘
       │
       ▼
    ┌──────────────┐
    │ WRITER ✍️     │  (Write Facebook post)
    └──────┬───────┘
           │
           │ 5-10 posts (hook, body, cta, tags)
           │
           ├─────────────────────┐
           │                     │
           │                     │ (Go to Designer)
           │                     │
           ▼                     ▼
    ┌──────────────┐      ┌──────────────┐
    │ DESIGNER 🎨  │      │ SEO ⚡       │
    │ (Find image) │      │ (Optimize)   │
    └──────┬───────┘      └──────┬───────┘
           │                     │
           │ image URLs          │ optimized content
           │                     │
           └──────────┬──────────┘
                      │
                      │ 5-10 complete posts
                      │ (text + image + optimized)
                      │
STAGE 3 - PUBLISHING (Giai đoạn xuất bản)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                      │
                      ▼
                 ┌──────────────┐
                 │ PUBLISHER 📤  │
                 │ (Validate)    │
                 │ (Select best) │
                 └──────┬────────┘
                        │
                        │ 1 best post (selected)
                        │
                        ▼
                 ┌──────────────────┐
                 │ Facebook API 🌐   │
                 │ (HTTP POST)       │
                 └──────┬────────────┘
                        │
                        │ ✅ Published
                        ▼
                 ┌──────────────────┐
                 │ FACEBOOK PAGE    │
                 │ (Live)           │
                 │ 25,000+ reach    │
                 └──────────────────┘
```

---

## 💡 **Lợi Ích Của Cách Thiết Kế Pipeline Này**

```
✅ MODULAR (Riêng biệt)
   └─ Mỗi agent = 1 job cụ thể
   └─ Dễ test, debug, upgrade từng agent
   └─ Có lỗi = fix agent đó = không ảnh hưởng agent khác

✅ EFFICIENT (Hiệu quả)
   └─ Scraper chạy 1 lần/ngày (6 AM)
   └─ Processor chạy 1 lần/ngày (7 AM)
   └─ Publisher chạy 1 lần/ngày (8 AM)
   └─ Không cần can thiệp manual

✅ SCALABLE (Mở rộng)
   └─ 5 bài/ngày → có thể mở rộng thành 20 bài
   └─ 1 page → có thể mở rộng thành 10 pages
   └─ Chỉ cần config, không cần code changes

✅ SMART (Thông minh)
   └─ Scraper: Tìm trending
   └─ Filter: Loại spam
   └─ Writer: Viết hay
   └─ Designer: Ảnh đẹp
   └─ SEO: Optimize algorithm
   └─ Publisher: Quality control

✅ AUTOMATED (Tự động)
   └─ 0 human intervention
   └─ 24/7 running
   └─ Error handling built-in
   └─ Logging for monitoring
```

---

## 🎯 **Timeline Thực Tế - Hàng Ngày**

```
6:00 AM
   ▼
┌──────────────────────────────────────────┐
│ SCRAPER runs                             │
├──────────────────────────────────────────┤
│ • Cào Medium (10-15 articles)           │
│ • Cào GitHub (10-15 repos)               │
│ • Cào Hugging Face (5-10 models)         │
│ • Result: 35-50 raw articles             │
└──────────────────────────────────────────┘
   │ (Articles saved to database)
   │
   ├─ 6:30 AM: Notification logged
   │
7:00 AM
   ▼
┌──────────────────────────────────────────┐
│ PROCESSOR Pipeline runs (4 agents)       │
├──────────────────────────────────────────┤
│ FILTER (1-2 min):                        │
│ • Verify facts → 5-10 best articles      │
│                                          │
│ WRITER (2-3 min):                        │
│ • Write 5-10 Facebook posts              │
│                                          │
│ DESIGNER (1-2 min):                      │
│ • Create search queries                  │
│ • Download 5-10 images                   │
│                                          │
│ SEO (1 min):                             │
│ • Optimize hashtags, emoji, format      │
│ • Result: 5-10 optimized posts           │
└──────────────────────────────────────────┘
   │ (Posts + images saved)
   │
   ├─ 7:10 AM: Notification logged
   │
8:00 AM
   ▼
┌──────────────────────────────────────────┐
│ PUBLISHER runs (1 agent)                 │
├──────────────────────────────────────────┤
│ PUBLISHER (30 sec):                      │
│ • Validate 5-10 posts                    │
│ • Select 1 best post                     │
│ • Call Facebook Graph API                │
│ • Result: POST PUBLISHED! ✅             │
└──────────────────────────────────────────┘
   │
   ├─ 8:00:30 AM: Post live on Facebook!
   │
   └─ Estimated reach: 25,000+ people
      Estimated engagement: 500+ interactions
```

---

## 🎓 **Key Takeaways**

```
1. PIPELINE = Sequential (Tuần tự)
   Scraper → Filter → Writer → Designer → SEO → Publisher
   Không thể bỏ qua bước nào

2. AGENTS = Intelligent (Thông minh)
   Mỗi agent có AI (GPT-4/GPT-4o-mini)
   Không phải template, mà thực sự "think"

3. AUTOMATION = Complete (Hoàn toàn)
   6 AM cào → 7 AM viết → 8 AM publish
   0 manual intervention

4. QUALITY = Multi-stage (Nhiều giai đoạn)
   Filter xác minh → Writer viết hay → SEO tối ưu
   = High engagement posts

5. SCALE = Easy (Dễ mở rộng)
   Config thay đổi = tự động chạy với volume lớn
   Không cần code changes
```

---

## 📞 **Sơ Đồ Tóm Tắt (1 trang)**

```
INPUT                                                OUTPUT
───────────────────────────────────────────────────────────────────

External           ┌────────────────────────────────────┐
APIs ──────────────│ 1️⃣ SCRAPER (Cào dữ liệu)        │─────┐
(6:00 AM)          │ Input: External APIs              │     │
                   │ Output: 35-50 articles            │     │
                   └────────────────────────────────────┘     │
                                                              │
                   ┌────────────────────────────────────┐     │
                   │ 2️⃣ FILTER (Lọc & Verify)         │◄────┘
                   │ Input: 35-50 articles             │
                   │ Output: 5-10 verified articles    │
                   └────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
   │ 3️⃣ WRITER   │  │ 4️⃣ DESIGNER│  │ 5️⃣ SEO      │
   │ Viết bài    │  │ Ảnh từ      │  │ Optimize     │
   │ Facebook    │  │ Unsplash    │  │ hashtags     │
   └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
          │                │                │
          └────────┬───────┴────────┬───────┘
                   │                │
                   ▼                ▼
            ┌─────────────────────────────────┐
            │ 6️⃣ PUBLISHER (Xuất bản)        │
            │ Input: 5-10 posts + images      │
            │ Output: 1 published post ✅     │
            └──────────┬──────────────────────┘
                       │
                       ▼
                ┌──────────────────┐
                │ FACEBOOK PAGE    │
                │ 25,000+ reach    │
                └──────────────────┘
```

---

**Ready để chạy agents? Start với `python simple_pipeline_demo.py`! 🚀**
