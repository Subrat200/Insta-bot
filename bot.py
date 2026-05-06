import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from instagram import InstagramScraper

logging.basicConfig(level=logging.INFO)
scraper = InstagramScraper()

def start(update, context):
    update.message.reply_text(
        "👋 Instagram Bot\n\n"
        "Koi bhi Instagram username bhejo!\n"
        "Example: cristiano"
    )

def handle(update, context):
    username = update.message.text.strip().lstrip("@")
    msg = update.message.reply_text(f"🔍 Searching @{username}...")
    data = scraper.get_profile(username)
    if data.get("error"):
        msg.edit_text(f"❌ {data['error']}")
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