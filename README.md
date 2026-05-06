# 📸 Instagram Telegram Bot

A powerful Telegram bot that fetches **public Instagram profile data** — followers, following, posts, stories, and analytics.

---

## ✨ Features

| Feature | Description |
|---|---|
| 👤 Profile Info | Name, bio, verification, private/public status |
| 👥 Followers & Following | Counts + follower ratio |
| 📸 Recent Posts | Thumbnails, likes, comments, captions |
| 🎭 Stories | Public stories (images & videos) |
| 📊 Analytics | Engagement rate, avg likes/comments, audience score |

---

## 🚀 Setup in 5 Minutes

### 1. Get a Bot Token

1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Follow the steps — you'll get a token like:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
   ```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Set Your Token

**Option A — Edit bot.py directly:**
```python
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
```

**Option B — Environment variable:**
```bash
export BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
python bot.py
```

**Option C — .env file:**
```bash
cp .env.example .env
# Edit .env and add your token
pip install python-dotenv
```

Then add this at the top of `bot.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Run the Bot

```bash
python bot.py
```

---

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message + main menu |
| `/help` | Full command reference |
| `/profile <username>` | Full profile info |
| `/followers <username>` | Followers & following count |
| `/posts <username>` | Recent posts with images |
| `/stories <username>` | Active public stories |
| `/stats <username>` | Analytics & engagement rate |

**Or just type any Instagram username** — the bot will auto-detect it!

---

## 📁 File Structure

```
instagram_bot/
├── bot.py           # Main Telegram bot logic
├── instagram.py     # Instagram scraper (no login needed)
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── README.md        # This file
```

---

## ⚠️ Important Notes

- ✅ **Works for public accounts only**
- ❌ Cannot access private account followers lists
- ❌ Cannot access private account stories
- 🔄 Instagram may rate-limit frequent requests
- 📋 This uses only publicly available data

---

## 🛠️ Troubleshooting

**"Rate limited" error:**
→ Wait 1-2 minutes and try again. Instagram limits frequent requests.

**"Profile not found":**
→ Check the username spelling. Make sure the account exists and is public.

**"Stories not available":**
→ The account either has no active stories, or stories require login (most accounts).

**Bot not responding:**
→ Make sure your token is correct and the bot is running.

---

## 🔧 Running 24/7 (Optional)

**On a Linux server with screen:**
```bash
screen -S instabot
python bot.py
# Press Ctrl+A, then D to detach
```

**With systemd service:**
```ini
[Unit]
Description=Instagram Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/instagram_bot
ExecStart=/usr/bin/python3 bot.py
Environment=BOT_TOKEN=your_token_here
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📜 License

For personal/educational use. Respect Instagram's Terms of Service.
