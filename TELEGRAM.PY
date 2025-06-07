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

# --- بارگذاری کاربران ---
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    print("⚠️ users.json به صورت لیست است. فایل نادرست است. بازنویسی می‌شود.")
                    return {}
                for uid in data:
                    data[uid]["invites"] = set(data[uid].get("invites", []))
                    data[uid]["daily"] = data[uid].get("daily", {})
                return data
        except Exception as e:
            print(f"⚠️ خطا در خواندن فایل users.json: {e}. بازنویسی می‌شود.")
            return {}
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

# --- بررسی عضویت ---
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member1 = await context.bot.get_chat_member(CHANNEL_ID_1, user_id)
        member2 = await context.bot.get_chat_member(CHANNEL_ID_2, user_id)
        member3 = await context.bot.get_chat_member(GROUP_ID, user_id)
        return all(m.status in ['member', 'administrator', 'creator'] for m in [member1, member2, member3])
    except:
        return False

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_user_member(update, context):
        await query.edit_message_text("✅ عضویت تأیید شد. دوباره /start را بزنید.")
    else:
        await query.edit_message_text("❌ هنوز عضو نیستید. لطفاً ابتدا عضو شوید.")

# --- منو اصلی ---
async def show_main_menu(update: Update):
    user_id = update.effective_user.id
    keyboard = [
        [KeyboardButton("📦 سی پی رایگان"), KeyboardButton("🎫 بتل پس رایگان")],
        [KeyboardButton("🔄 چنج اکانت کرکی"), KeyboardButton("🛡️ سالم کردن اکانت کرکی")],
        [KeyboardButton("📢 آگهی فروش اکانت"), KeyboardButton("🛒 آگهی خرید اکانت")],
        [KeyboardButton("🆘 پشتیبانی"), KeyboardButton("🎁 دریافت لینک دعوت")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton("👥 لیست کاربران")])
    await update.message.reply_text(
        "به ربات خوش آمدید!\nیکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# --- دستور شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not await is_user_member(update, context):
        await update.message.reply_text(
            "برای استفاده از ربات، ابتدا در کانال‌ها و گروه عضو شوید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📣 عضویت در کانال اول", url=f"https://t.me/{CHANNEL_ID_1[1:]}")],
                [InlineKeyboardButton("📣 عضویت در کانال دوم", url=f"https://t.me/{CHANNEL_ID_2[1:]}")],
                [InlineKeyboardButton("💬 عضویت در گروه", url=f"https://t.me/{GROUP_ID[1:]}")],
                [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_membership")]
            ])
        )
        return

    if user_id not in users:
        users[user_id] = {"points": 0, "invites": set(), "daily": {}}
        save_users()

    await show_main_menu(update)

# --- هندل پیام‌ها ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    services = {
        "📦 سی پی رایگان": 3,
        "🎫 بتل پس رایگان": 2,
        "🔄 چنج اکانت کرکی": 2,
        "🛡️ سالم کردن اکانت کرکی": 2,
        "📢 آگهی فروش اکانت": 0,
        "🛒 آگهی خرید اکانت": 0,
        "🆘 پشتیبانی": 0
    }

    if text in services:
        cost = services[text]
        if cost > 0 and users[user_id]["points"] < cost:
            await update.message.reply_text(f"❌ برای استفاده از این خدمت به {cost} امتیاز نیاز دارید.")
            return
        if cost > 0:
            users[user_id]["points"] -= cost
            save_users()

        if text == "📢 آگهی فروش اکانت":
            context.user_data['state'] = text
            await update.message.reply_text(
                "#فروش_اکانت\n\n"
                "🌐 | ریجن: \n"
                "⚙️ | لینک: \n"
                "💎 | سی‌پی: \n"
                "🔓 | بتل پس: \n\n"
                "📝 | توضیحات: \n\n"
                "💵 | قیمت :\n"
                "🔄 | طاق: ندارد\n\n"
                "💳 | آیدی فروشنده: \n\n"
                "✅ | آیدی واسطه : @mr_sepix 🆔\n\n"
                "🛍 | @sepix_shop\n"
                "🛒 | @sepix_trust\n"
                "💬 | @sepix_gap"
            )

        elif text == "🛒 آگهی خرید اکانت":
            context.user_data['state'] = text
            await update.message.reply_text(
                "#خرید_اکانت\n\n"
                "📝 | توضیحات: \n\n"
                "💵 | قیمت :\n"
                "🔄 | طاق :\n\n"
                "💳 | آیدی خریدار : \n\n"
                "✅ | آیدی واسطه : @mr_sepix 🆔\n\n"
                "🛍 | @sepix_shop\n"
                "🛒 | @sepix_trust\n"
                "💬 | @sepix_gap"
            )

        else:
            messages = {
                "📦 سی پی رایگان": "لطفاً رمز و ایمیل اکانت خود را وارد کنید.",
                "🎫 بتل پس رایگان": "لطفاً نام بتل پس و ایمیل را وارد کنید. (حداکثر ۳ عدد)",
                "🔄 چنج اکانت کرکی": "رمز ایمیل را ارسال کنید و تا ۳ روز با پشتیبانی در تماس باشید.",
                "🛡️ سالم کردن اکانت کرکی": "رمز و جیمیل خود را ارسال کنید. تا ۳ روز پیام دهید.",
                "🆘 پشتیبانی": "سؤال خود را بنویسید. پشتیبانی به زودی پاسخ می‌دهد."
            }
            if text == "🆘 پشتیبانی":
                context.user_data['support'] = True

            await update.message.reply_text(messages.get(text, "درخواست شما ثبت شد."))
        return

    elif text == "🎁 دریافت لینک دعوت":
        invite_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        await update.message.reply_text(
            f"🔗 لینک دعوت اختصاصی شما:\n{invite_link}\nهر کاربر که با این لینک وارد شود، ۱ امتیاز به شما تعلق می‌گیرد. (تا سقف ۱۰ امتیاز در روز)"
        )

    elif text == "👥 لیست کاربران":
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ این گزینه فقط مخصوص مدیر ربات است.")
            return
        filename = "users_list.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("📋 لیست کاربران:\n\n")
            for uid in users:
                try:
                    user = await context.bot.get_chat(int(uid))
                    username = f"@{user.username}" if user.username else f"ID: {uid}"
                    f.write(f"- {username} | امتیاز: {users[uid]['points']}\n")
                except:
                    f.write(f"- ID: {uid} | امتیاز: {users[uid]['points']} (نام کاربری نامشخص)\n")
        await update.message.reply_document(document=open(filename, "rb"), filename=filename, caption="📄 لیست کاربران:")
        os.remove(filename)

    elif context.user_data.get('state'):
        await update.message.reply_text("✅ اطلاعات شما ثبت شد.")
        context.user_data.pop('state')

    elif context.user_data.get("support"):
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"پیام پشتیبانی از {user_id}:\n{text}")
        await update.message.reply_text("پیام شما برای پشتیبانی ارسال شد.")
        context.user_data["support"] = False

# --- شروع با رفرال و محدودیت روزانه ---
async def start_with_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    referrer = args[0] if args else None

    if user_id not in users:
        users[user_id] = {"points": 0, "invites": set(), "daily": {}}

    if referrer and referrer != user_id:
        ref_data = users.get(referrer)
        if ref_data and user_id not in ref_data["invites"]:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_points = int(ref_data.get("daily", {}).get(today, 0))
            if daily_points < 10:
                ref_data["invites"].add(user_id)
                ref_data["points"] += 1
                ref_data.setdefault("daily", {})[today] = daily_points + 1
                save_users()

    save_users()
    await start(update, context)

# --- اجرای ربات ---
app = ApplicationBuilder().token('7867275226:AAF7z0xC5OExUw02WeILCPDE_e5xvFmxUTQ').build()
app.add_handler(CommandHandler("start", start_with_referral))
app.add_handler(CommandHandler("invite", lambda u, c: u.message.reply_text("از منوی ربات گزینه «🎁 دریافت لینک دعوت» را بزنید.")))
app.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("✅ ربات با موفقیت اجرا شد.")
app.run_polling()
