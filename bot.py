import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from instagram import InstagramScraper

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
scraper = InstagramScraper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Instagram Bot*\n\nKoi bhi Instagram username bhejo!",
        parse_mode="Markdown"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lstrip("@")
    msg = await update.message.reply_text(f"🔍 Searching `@{username}`...", parse_mode="Markdown")
    data = scraper.get_profile(username)
    if data.get("error"):
        await msg.edit_text(f"❌ {data['error']}")
        return
    text = (
        f"👤 *@{data['username']}*\n"
        f"📛 Name: {data['full_name']}\n"
        f"👥 Followers: {data['followers']:,}\n"
        f"➡️ Following: {data['following']:,}\n"
        f"📸 Posts: {data['posts']:,}\n"
        f"✅ Verified: {'Yes' if data['is_verified'] else 'No'}\n"
        f"🔒 Private: {'Yes' if data['is_private'] else 'No'}\n"
        f"📝 Bio: {data.get('bio','')}"
    )
    await msg.edit_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
