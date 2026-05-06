import os
import logging
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)

def get_instagram(username):
    try:
        s = requests.Session()
        s.headers["User-Agent"] = "Mozilla/5.0"
        s.headers["X-IG-App-ID"] = "936619743392459"
        r = s.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            timeout=15
        )
        u = r.json().get("data", {}).get("user", {})
        if not u:
            return None
        return {
            "username": u.get("username", ""),
            "full_name": u.get("full_name", ""),
            "bio": u.get("biography", ""),
            "followers": u.get("edge_followed_by", {}).get("count", 0),
            "following": u.get("edge_follow", {}).get("count", 0),
            "posts": u.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "is_verified": u.get("is_verified", False),
            "is_private": u.get("is_private", False),
        }
    except:
        return None

def start(update, context):
    update.message.reply_text(
        "👋 Instagram Bot\n\n"
        "Koi bhi Instagram username bhejo!\n"
        "Example: cristiano"
    )

def handle(update, context):
    username = update.message.text.strip().lstrip("@")
    msg = update.message.reply_text(f"🔍 Searching @{username}...")
    data = get_instagram(username)
    if not data:
        msg.edit_text("❌ Profile not found!")
        return
    text = (
        f"👤 @{data['username']}\n"
        f"📛 Name: {data['full_name']}\n"
        f"👥 Followers: {data['followers']:,}\n"
        f"➡️ Following: {data['following']:,}\n"
        f"📸 Posts: {data['posts']:,}\n"
        f"✅ Verified: {'Yes' if data['is_verified'] else 'No'}\n"
        f"🔒 Private: {'Yes' if data['is_private'] else 'No'}\n"
        f"📝 Bio: {data.get('bio', 'No bio')}"
    )
    msg.edit_text(text)

def main():
    token = os.environ.get("BOT_TOKEN", "")
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, handle
    ))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()