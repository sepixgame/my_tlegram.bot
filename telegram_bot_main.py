import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# --- تنظیمات ---
CHANNEL_ID_1 = "@sepix_shop"
CHANNEL_ID_2 = "@sepix_trust"
GROUP_ID = "@sepix_gap"
ADMIN_ID = 826685726
BOT_USERNAME = "sepix_codm_bot"
DB_FILE = "users.json"
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # امن‌تر

# --- بارگذاری کاربران ---
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    print("⚠️ فایل users.json ساختار درستی ندارد. بازنویسی می‌شود.")
                    return {}
                for uid in data:
                    data[uid]["invites"] = set(data[uid].get("invites", []))
                    data[uid]["daily"] = data[uid].get("daily", {})
                return data
        except Exception as e:
            print(f"⚠️ خطا در خواندن فایل users.json: {e}. بازنویسی می‌شود.")
            return {}
    else:
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}

# --- ذخیره کاربران ---
def save_users():
    with open(DB_FILE, "w") as f:
        json.dump({
            uid: {
                "points": user["points"],
                "invites": list(user["invites"]),
                "daily": user.get("daily", {})
            } for uid, user in users.items()
        }, f, indent=2)

users = load_users()

# باقی کد بدون تغییر...
# (همان کدی که خودت دادی از این بخش به بعد دقیقاً قرار دارد.)

# ... (کدهایی مثل is_user_member، check_membership، start، show_main_menu، handle_messages و غیره)

# --- اجرای ربات ---
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ توکن ربات در متغیر BOT_TOKEN یافت نشد.")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_with_referral))
    app.add_handler(CommandHandler("invite", lambda u, c: u.message.reply_text("از منوی ربات گزینه «🎁 دریافت لینک دعوت» را بزنید.")))
    app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("✅ ربات با موفقیت اجرا شد.")
    app.run_polling()
