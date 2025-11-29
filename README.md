# 🤖 Telegram Bot - Omid AI

A powerful Telegram bot with user management, group permissions, AI-powered reports, and multilingual support.

## ✨ Features

- 👥 **User Management** - Add, edit, delete users with different roles
- 🔐 **Role-Based Access** - Owner, Admin, Supervisor, User, Blocked
- 💬 **Group Permissions** - Manage user access to specific groups
- 🤖 **AI Reports** - Generate weekly/monthly reports using GPT
- 🌐 **Multilingual** - Persian & English support
- 📊 **Audit Logs** - Track all admin actions
- ⚡ **Optimized** - Async operations, caching, non-blocking logging

## 🚀 Quick Start

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/OmidShojaei10x/Omid_AI.git
cd Omid_AI
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
```

5. Run the full bot:
```bash
python main.py
```

### 🪄 فقط بات سلام‌گو؟

اگر فقط می‌خواهید یک بات خیلی ساده داشته باشید که وقتی «سلام» یا «ساام» می‌فرستید جواب بدهد، فایل `simple_bot.py` را اجرا کنید:

```bash
python simple_bot.py
```

این نسخه فقط به متغیر محیطی `TELEGRAM_BOT_TOKEN` نیاز دارد و خبری از Supabase یا APIهای دیگر نیست.

### GitHub Actions (Cloud)

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**

2. Add this repository secret:
   - `TELEGRAM_BOT_TOKEN` ← همون توکن ربات تلگرام

3. Go to **Actions** tab and enable workflows

4. The bot will run automatically using `simple_bot.py` on every push to `main`, on schedule (هر ۵ ساعت)، یا هر بار که `workflow_dispatch` بزنی. چون GitHub Actions دائمی نیست، هر اجرا حدود ۴.۵ ساعت روشن می‌مونه و اجرای بعدی خودش دوباره شروع می‌شود.

## 📁 Project Structure

```
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in repo)
├── .gitignore          # Git ignore rules
├── start_bot.sh        # Start script
├── stop_bot.sh         # Stop script
├── restart_bot.sh      # Restart script
└── .github/
    └── workflows/
        └── bot.yml     # GitHub Actions workflow
```

## 🛠 Tech Stack

- **Python 3.11+**
- **python-telegram-bot** - Telegram API
- **Supabase** - Database
- **OpenAI GPT** - AI Reports
- **asyncio** - Async operations

## 📝 License

MIT License - feel free to use and modify!

## 👨‍💻 Author

**Omid Shojaei**
- GitHub: [@OmidShojaei10x](https://github.com/OmidShojaei10x)



