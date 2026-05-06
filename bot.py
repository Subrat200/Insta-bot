import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from instagram import InstagramScraper

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

scraper = InstagramScraper()

# ── Helpers ────────────────────────────────────────────────────────────────────

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Search Instagram Profile", callback_data="search")],
        [InlineKeyboardButton("📊 Get Profile Stats", callback_data="stats")],
        [InlineKeyboardButton("📸 View Recent Posts", callback_data="posts")],
        [InlineKeyboardButton("🎭 View Stories", callback_data="stories")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ])

def profile_action_keyboard(username: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Followers & Following", callback_data=f"followers|{username}")],
        [InlineKeyboardButton("📸 Recent Posts", callback_data=f"posts|{username}")],
        [InlineKeyboardButton("🎭 Stories", callback_data=f"stories|{username}")],
        [InlineKeyboardButton("📊 Full Stats", callback_data=f"stats|{username}")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ])

# ── Command Handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = (
        f"👋 *Welcome, {user.first_name}!*\n\n"
        "🔎 *Instagram Profile Analyzer Bot*\n\n"
        "I can fetch public Instagram profile data:\n"
        "• 👥 Followers & Following count\n"
        "• 📸 Recent posts preview\n"
        "• 🎭 Public stories\n"
        "• 📊 Full profile analytics\n\n"
        "_Send any Instagram username to get started, or use the menu below!_"
    )
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *How to use this bot:*\n\n"
        "1️⃣ Just type any Instagram username\n"
        "   Example: `cristiano` or `@cristiano`\n\n"
        "2️⃣ Or use commands:\n"
        "   /profile `<username>` — Full profile info\n"
        "   /followers `<username>` — Followers & following\n"
        "   /posts `<username>` — Recent posts\n"
        "   /stories `<username>` — Public stories\n"
        "   /stats `<username>` — Analytics\n\n"
        "⚠️ *Note:* Only works for *public* Instagram accounts.\n\n"
        "🤖 Built with ❤️ using Python & python-telegram-bot"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /profile `<username>`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await fetch_and_send_profile(update, context, username)

async def followers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /followers `<username>`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await fetch_and_send_followers(update, context, username)

async def posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /posts `<username>`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await fetch_and_send_posts(update, context, username)

async def stories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /stories `<username>`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await fetch_and_send_stories(update, context, username)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /stats `<username>`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await fetch_and_send_stats(update, context, username)

# ── Message Handler (plain username) ─────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lstrip("@")
    # Simple validation: looks like a username
    if text and " " not in text and len(text) <= 30:
        await fetch_and_send_profile(update, context, text)
    else:
        await update.message.reply_text(
            "❓ Please send a valid Instagram username (no spaces).\n"
            "Example: `cristiano`",
            parse_mode="Markdown"
        )

# ── Core Fetch Functions ───────────────────────────────────────────────────────

async def fetch_and_send_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    msg = await update.message.reply_text(f"🔍 Looking up `@{username}`...", parse_mode="Markdown")
    
    data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_profile, username)
    
    if not data or data.get("error"):
        error = data.get("error", "Unknown error") if data else "Profile not found"
        await msg.edit_text(f"❌ *Error:* {error}", parse_mode="Markdown")
        return

    await msg.delete()

    # Send profile photo if available
    if data.get("profile_pic_url"):
        try:
            await update.message.reply_photo(
                photo=data["profile_pic_url"],
                caption=build_profile_caption(data),
                parse_mode="Markdown",
                reply_markup=profile_action_keyboard(username)
            )
            return
        except Exception:
            pass

    await update.message.reply_text(
        build_profile_caption(data),
        parse_mode="Markdown",
        reply_markup=profile_action_keyboard(username)
    )

async def fetch_and_send_followers(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    if update.message:
        msg = await update.message.reply_text(f"👥 Fetching follower info for `@{username}`...", parse_mode="Markdown")
    else:
        msg = await update.callback_query.message.reply_text(f"👥 Fetching follower info for `@{username}`...", parse_mode="Markdown")

    data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_profile, username)

    if not data or data.get("error"):
        await msg.edit_text(f"❌ Could not fetch data for `@{username}`", parse_mode="Markdown")
        return

    followers = data.get("followers", 0)
    following = data.get("following", 0)
    ratio = round(followers / following, 2) if following > 0 else "∞"

    text = (
        f"👥 *Followers & Following — @{username}*\n"
        f"{'─'*35}\n\n"
        f"👥 *Followers:* `{format_number(followers)}`\n"
        f"➡️ *Following:* `{format_number(following)}`\n"
        f"📊 *Follower Ratio:* `{ratio}:1`\n\n"
        f"📝 *Posts:* `{format_number(data.get('posts', 0))}`\n"
        f"✅ *Verified:* {'Yes ✅' if data.get('is_verified') else 'No'}\n"
        f"🔒 *Private:* {'Yes 🔒' if data.get('is_private') else 'No (Public)'}\n\n"
        f"_Data fetched from public Instagram profile_"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 See Posts", callback_data=f"posts|{username}"),
         InlineKeyboardButton("🎭 See Stories", callback_data=f"stories|{username}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"profile|{username}")],
    ])

    await msg.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def fetch_and_send_posts(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    if update.message:
        msg = await update.message.reply_text(f"📸 Fetching recent posts for `@{username}`...", parse_mode="Markdown")
    else:
        msg = await update.callback_query.message.reply_text(f"📸 Fetching recent posts for `@{username}`...", parse_mode="Markdown")

    data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_posts, username)

    if not data or data.get("error"):
        await msg.edit_text(f"❌ Could not fetch posts for `@{username}`", parse_mode="Markdown")
        return

    posts = data.get("posts", [])
    if not posts:
        await msg.edit_text(f"📭 No public posts found for `@{username}`", parse_mode="Markdown")
        return

    await msg.delete()

    header = (
        f"📸 *Recent Posts — @{username}*\n"
        f"{'─'*35}\n"
        f"Found *{len(posts)}* recent posts\n\n"
    )
    await (update.message or update.callback_query.message).reply_text(header, parse_mode="Markdown")

    for i, post in enumerate(posts[:6], 1):
        caption = (
            f"📸 *Post {i}*\n"
            f"❤️ Likes: `{format_number(post.get('likes', 0))}`\n"
            f"💬 Comments: `{format_number(post.get('comments', 0))}`\n"
            f"📅 Posted: `{post.get('date', 'N/A')}`\n"
        )
        if post.get("caption"):
            cap_text = post["caption"][:100] + "..." if len(post.get("caption","")) > 100 else post.get("caption","")
            caption += f"📝 Caption: _{cap_text}_\n"
        if post.get("url"):
            caption += f"\n🔗 [View on Instagram]({post['url']})"

        try:
            if post.get("thumbnail"):
                await (update.message or update.callback_query.message).reply_photo(
                    photo=post["thumbnail"],
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await (update.message or update.callback_query.message).reply_text(caption, parse_mode="Markdown")
        except Exception:
            await (update.message or update.callback_query.message).reply_text(caption, parse_mode="Markdown")

        await asyncio.sleep(0.5)

async def fetch_and_send_stories(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    if update.message:
        msg = await update.message.reply_text(f"🎭 Checking stories for `@{username}`...", parse_mode="Markdown")
        reply_target = update.message
    else:
        msg = await update.callback_query.message.reply_text(f"🎭 Checking stories for `@{username}`...", parse_mode="Markdown")
        reply_target = update.callback_query.message

    data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_stories, username)

    if not data or data.get("error"):
        await msg.edit_text(
            f"❌ Could not fetch stories for `@{username}`\n\n"
            "Stories are only visible for *public accounts* and if they have active stories.",
            parse_mode="Markdown"
        )
        return

    stories = data.get("stories", [])
    if not stories:
        await msg.edit_text(
            f"📭 *No active stories* found for `@{username}`\n\n"
            "_They may not have posted stories recently, or this is a private account._",
            parse_mode="Markdown"
        )
        return

    await msg.delete()
    await reply_target.reply_text(
        f"🎭 *Stories — @{username}*\n{'─'*35}\nFound *{len(stories)}* active stories!",
        parse_mode="Markdown"
    )

    for i, story in enumerate(stories, 1):
        caption = f"🎭 *Story {i}/{len(stories)}*\n📅 `{story.get('date', 'N/A')}`"
        try:
            if story.get("type") == "video" and story.get("url"):
                await reply_target.reply_video(video=story["url"], caption=caption, parse_mode="Markdown")
            elif story.get("thumbnail"):
                await reply_target.reply_photo(photo=story["thumbnail"], caption=caption, parse_mode="Markdown")
            else:
                await reply_target.reply_text(caption, parse_mode="Markdown")
        except Exception:
            await reply_target.reply_text(caption, parse_mode="Markdown")
        await asyncio.sleep(0.5)

async def fetch_and_send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
    if update.message:
        msg = await update.message.reply_text(f"📊 Analyzing `@{username}`...", parse_mode="Markdown")
        reply_target = update.message
    else:
        msg = await update.callback_query.message.reply_text(f"📊 Analyzing `@{username}`...", parse_mode="Markdown")
        reply_target = update.callback_query.message

    profile = await asyncio.get_event_loop().run_in_executor(None, scraper.get_profile, username)
    posts_data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_posts, username)

    if not profile or profile.get("error"):
        await msg.edit_text(f"❌ Could not analyze `@{username}`", parse_mode="Markdown")
        return

    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    posts_count = profile.get("posts", 0)
    
    posts = posts_data.get("posts", []) if posts_data and not posts_data.get("error") else []
    avg_likes = avg_comments = 0
    if posts:
        avg_likes = sum(p.get("likes", 0) for p in posts) // len(posts)
        avg_comments = sum(p.get("comments", 0) for p in posts) // len(posts)
    
    eng_rate = round((avg_likes + avg_comments) / followers * 100, 2) if followers > 0 else 0

    # Score
    if eng_rate >= 6:
        eng_label = "🔥 Excellent"
    elif eng_rate >= 3:
        eng_label = "✅ Good"
    elif eng_rate >= 1:
        eng_label = "⚠️ Average"
    else:
        eng_label = "❌ Low"

    text = (
        f"📊 *Full Analytics — @{username}*\n"
        f"{'─'*35}\n\n"
        f"👤 *Profile*\n"
        f"  • Name: `{profile.get('full_name', 'N/A')}`\n"
        f"  • Verified: {'✅ Yes' if profile.get('is_verified') else '❌ No'}\n"
        f"  • Private: {'🔒 Yes' if profile.get('is_private') else '🌐 No'}\n\n"
        f"📈 *Audience*\n"
        f"  • Followers: `{format_number(followers)}`\n"
        f"  • Following: `{format_number(following)}`\n"
        f"  • Ratio: `{round(followers/following,2) if following else '∞'}:1`\n\n"
        f"📸 *Content*\n"
        f"  • Total Posts: `{format_number(posts_count)}`\n"
        f"  • Avg Likes: `{format_number(avg_likes)}`\n"
        f"  • Avg Comments: `{format_number(avg_comments)}`\n\n"
        f"💡 *Engagement*\n"
        f"  • Rate: `{eng_rate}%`\n"
        f"  • Rating: {eng_label}\n\n"
        f"_Analysis based on recent public posts_"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Followers", callback_data=f"followers|{username}"),
         InlineKeyboardButton("📸 Posts", callback_data=f"posts|{username}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"profile|{username}")],
    ])

    await msg.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ── Callback Handler ───────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.message.reply_text(
            "🏠 *Main Menu*\nSend an Instagram username to get started!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    elif data == "search":
        await query.message.reply_text("🔍 *Send me any Instagram username!*\nExample: `cristiano`", parse_mode="Markdown")
    elif data == "help":
        await query.message.reply_text(
            "📖 *How to use:*\nJust type any Instagram username!\nOr use /help for all commands.",
            parse_mode="Markdown"
        )
    elif "|" in data:
        action, username = data.split("|", 1)
        if action == "profile":
            await fetch_and_send_profile_callback(query, context, username)
        elif action == "followers":
            await fetch_and_send_followers(update, context, username)
        elif action == "posts":
            await fetch_and_send_posts(update, context, username)
        elif action == "stories":
            await fetch_and_send_stories(update, context, username)
        elif action == "stats":
            await fetch_and_send_stats(update, context, username)

async def fetch_and_send_profile_callback(query, context, username: str):
    msg = await query.message.reply_text(f"🔍 Loading profile `@{username}`...", parse_mode="Markdown")
    data = await asyncio.get_event_loop().run_in_executor(None, scraper.get_profile, username)
    if not data or data.get("error"):
        await msg.edit_text(f"❌ Could not load profile for `@{username}`", parse_mode="Markdown")
        return
    await msg.edit_text(
        build_profile_caption(data),
        parse_mode="Markdown",
        reply_markup=profile_action_keyboard(username)
    )

# ── Formatters ─────────────────────────────────────────────────────────────────

def build_profile_caption(data: dict) -> str:
    username = data.get("username", "N/A")
    return (
        f"👤 *@{username}*\n"
        f"{'─'*35}\n"
        f"📛 *Name:* `{data.get('full_name', 'N/A')}`\n"
        f"✅ *Verified:* {'Yes ✅' if data.get('is_verified') else 'No'}\n"
        f"🔒 *Private:* {'Yes 🔒' if data.get('is_private') else 'No (Public)'}\n\n"
        f"👥 *Followers:* `{format_number(data.get('followers', 0))}`\n"
        f"➡️ *Following:* `{format_number(data.get('following', 0))}`\n"
        f"📸 *Posts:* `{format_number(data.get('posts', 0))}`\n\n"
        f"📝 *Bio:* _{data.get('bio', 'No bio')}_\n\n"
        f"🔗 *Profile:* [instagram.com/{username}](https://instagram.com/{username})"
    )

def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("followers", followers_command))
    app.add_handler(CommandHandler("posts", posts_command))
    app.add_handler(CommandHandler("stories", stories_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Instagram Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
