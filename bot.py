import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from pymongo import MongoClient

# ─── লগিং ───
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── কনফিগ ───
BOT_TOKEN = "8737107611:AAG7Sn9xfFFx-9xmylMu4bt9Z89byRvvcpM"
ADMIN_ID = 7200936473
MONGO_URI = os.getenv("MONGO_URI")
WEB_URL = os.getenv("WEB_URL", "https://natokhub-bd-bot-1.onrender.com")

# ─── MongoDB ───
client = MongoClient(MONGO_URI)
db = client["natokhub"]
episodes_col = db["episodes"]

# ─── কনভার্সেশন স্টেট ───
WAIT_EP_NUMBER, WAIT_EP_TITLE, WAIT_EP_THUMB, WAIT_EP_VIDEO = range(4)

# ══════════════════════════════════════════
#  ডেটা ফাংশন
# ══════════════════════════════════════════

def load_episodes():
    return list(episodes_col.find({}, {"_id": 0}).sort("number", -1))

def save_episode(ep):
    episodes_col.update_one(
        {"number": ep["number"]},
        {"$set": ep},
        upsert=True
    )

def delete_episode(number):
    episodes_col.delete_one({"number": number})

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ══════════════════════════════════════════
#  ইউজার — /start
# ══════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    episodes = load_episodes()

    if not episodes:
        await update.message.reply_text(
            "🎬 *Bachelor Point Bot*\n\nএখনো কোনো এপিসোড নেই।",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"🎬 *Bachelor Point Season 5*\n\nস্বাগতম {user.first_name}! নিচে এপিসোড বেছে নিন 👇",
        parse_mode="Markdown"
    )

    for ep in episodes[:8]:
        keyboard = [[InlineKeyboardButton(
            f"▶️ Episode {ep['number']} দেখুন",
            callback_data=f"watch_{ep['number']}"
        )]]
        caption = f"🎬 *Bachelor Point Season 5*\n📺 *Episode {ep['number']}*\n📝 {ep['title']}"

        try:
            await update.message.reply_photo(
                photo=ep["thumb_file_id"],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            await update.message.reply_text(
                caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# ══════════════════════════════════════════
#  ওয়াচ বাটন
# ══════════════════════════════════════════

async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ep_number = int(query.data.split("_")[1])
    ad_url = f"{WEB_URL}/ad?ep={ep_number}&user={query.from_user.id}"

    keyboard = [[InlineKeyboardButton(
        "🎬 অ্যাড দেখে ভিডিও পান",
        web_app=WebAppInfo(url=ad_url)
    )]]

    await query.edit_message_caption(
        caption=f"📺 *Episode {ep_number}*\n\n⚠️ ভিডিও পেতে নিচের বাটনে ক্লিক করুন।\n_(১৫ সেকেন্ড অ্যাড দেখতে হবে)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ══════════════════════════════════════════
#  ওয়েব অ্যাপ থেকে ভিডিও পাঠাও
# ══════════════════════════════════════════

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_str = update.effective_message.web_app_data.data
    try:
        info = json.loads(data_str)
        ep_number = int(info.get("ep", 0))
    except Exception:
        await update.message.reply_text("❌ কিছু একটা সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    ep = episodes_col.find_one({"number": ep_number}, {"_id": 0})

    if not ep:
        await update.message.reply_text("❌ এপিসোড পাওয়া যায়নি!")
        return

    await update.message.reply_text(
        f"✅ *অ্যাড দেখা সম্পন্ন!*\n\n📺 Episode {ep_number} পাঠানো হচ্ছে...",
        parse_mode="Markdown"
    )

    try:
        await context.bot.send_video(
            chat_id=update.effective_user.id,
            video=ep["video_file_id"],
            caption=f"🎬 *Bachelor Point Season 5*\n📺 *Episode {ep['number']}*\n📝 {ep['title']}\n\n🔔 Join: @Natokhub_BD",
            parse_mode="Markdown",
            supports_streaming=True
        )
    except Exception as e:
        await update.message.reply_text(f"❌ ভিডিও পাঠাতে সমস্যা হয়েছে: {str(e)}")

# ══════════════════════════════════════════
#  অ্যাডমিন — এপিসোড অ্যাড
# ══════════════════════════════════════════

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ আপনার পারমিশন নেই!")
        return ConversationHandler.END

    await update.message.reply_text(
        "➕ *নতুন এপিসোড অ্যাড*\n\nএপিসোড নম্বর দিন:\n\n/cancel — বাতিল",
        parse_mode="Markdown"
    )
    return WAIT_EP_NUMBER

async def got_ep_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ শুধু নম্বর দিন!")
        return WAIT_EP_NUMBER

    ep_num = int(text)
    if episodes_col.find_one({"number": ep_num}):
        await update.message.reply_text(f"⚠️ Episode {ep_num} আগেই আছে! অন্য নম্বর দিন:")
        return WAIT_EP_NUMBER

    context.user_data["new_ep"] = {"number": ep_num}
    await update.message.reply_text(
        f"✅ EP {ep_num}\n\nএখন *টাইটেল* দিন:",
        parse_mode="Markdown"
    )
    return WAIT_EP_TITLE

async def got_ep_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text.strip()
    context.user_data["new_ep"]["title"] = title
    await update.message.reply_text(
        f"✅ টাইটেল: *{title}*\n\nএখন *থাম্বনেইল ছবি* পাঠান:",
        parse_mode="Markdown"
    )
    return WAIT_EP_THUMB

async def got_ep_thumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ ছবি পাঠান!")
        return WAIT_EP_THUMB

    photo = update.message.photo[-1]
    context.user_data["new_ep"]["thumb_file_id"] = photo.file_id
    await update.message.reply_text(
        "✅ থাম্বনেইল পেয়েছি!\n\nএখন *ভিডিও ফাইল* পাঠান:",
        parse_mode="Markdown"
    )
    return WAIT_EP_VIDEO

async def got_ep_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video and not update.message.document:
        await update.message.reply_text("❌ ভিডিও ফাইল পাঠান!")
        return WAIT_EP_VIDEO

    video = update.message.video or update.message.document
    context.user_data["new_ep"]["video_file_id"] = video.file_id

    ep = context.user_data["new_ep"]
    save_episode(ep)

    await update.message.reply_text(
        f"✅ *সফলভাবে অ্যাড হয়েছে!*\n\n📺 Episode {ep['number']} — {ep['title']}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ বাতিল।")
    return ConversationHandler.END

# ══════════════════════════════════════════
#  অ্যাডমিন — ডিলিট ও লিস্ট
# ══════════════════════════════════════════

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ পারমিশন নেই!")
        return

    if not context.args:
        await update.message.reply_text("❓ /delete 88")
        return

    try:
        ep_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ সঠিক নম্বর দিন!")
        return

    if not episodes_col.find_one({"number": ep_num}):
        await update.message.reply_text(f"❌ Episode {ep_num} নেই!")
        return

    delete_episode(ep_num)
    await update.message.reply_text(f"🗑️ Episode {ep_num} ডিলিট হয়েছে।")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ পারমিশন নেই!")
        return

    episodes = list(episodes_col.find({}, {"_id": 0}).sort("number", 1))

    if not episodes:
        await update.message.reply_text("📭 কোনো এপিসোড নেই।")
        return

    lines = [f"📋 *মোট {len(episodes)}টি:*\n"]
    for ep in episodes:
        lines.append(f"EP {ep['number']} — {ep['title']}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ══════════════════════════════════════════
#  মেইন
# ══════════════════════════════════════════

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            WAIT_EP_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_ep_number)],
            WAIT_EP_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_ep_title)],
            WAIT_EP_THUMB: [MessageHandler(filters.PHOTO, got_ep_thumb)],
            WAIT_EP_VIDEO: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, got_ep_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(add_conv)
    app.add_handler(CallbackQueryHandler(watch_callback, pattern=r"^watch_\d+$"))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    print("✅ Natokhub Bot চালু!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
