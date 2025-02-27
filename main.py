import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

TOKEN = "7868831300:AAGK9OwEaXxz8QsnWSun2BzCEWk-Uceu5Og"
CHANNEL_USERNAME = "@Teacher_Mubina"
PAID_CHANNEL_LINK = "https://t.me/+Jx3zeCLm4KlmOGMy"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        if "referrals_count" not in data:
            data["referrals_count"] = {}
        if "invited_users" not in data:
            data["invited_users"] = []
        if "subscribed_users" not in data: 
            data["subscribed_users"] = []

        return data

    return {"referrals_count": {}, "invited_users": [], "subscribed_users": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "referrals_count": referrals_count,
            "invited_users": list(invited_users),
            "subscribed_users": list(subscribed_users)  
        }, f)

data = load_data()
referrals_count = data["referrals_count"]
invited_users = set(data["invited_users"])
subscribed_users = set(data["subscribed_users"]) 

pending_users = {}  

def is_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def is_bot_admin():
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, bot.get_me().id)
        return chat_member.status in ["administrator", "creator"]
    except Exception:
        return False

# 📌 START komandasi
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    user_id = str(message.chat.id)  # JSON uchun string sifatida saqlaymiz

    # 🔹 Agar foydalanuvchi oldin yetarlicha odam taklif qilgan bo‘lsa, obuna so‘ramaymiz
    if user_id in subscribed_users:
        markup = InlineKeyboardMarkup()
        btn_paid_channel = InlineKeyboardButton("🔓 Pullik kanalga kirish", url=PAID_CHANNEL_LINK)
        markup.add(btn_paid_channel)

        bot.send_message(user_id, f"✅ Siz allaqachon yetarlicha odam taklif qilgansiz!\n"
                              f"Mana sizga Pullik kanal", 
                              reply_markup=markup)
        return

    if len(args) > 1:
        referrer_id = args[1]

        if user_id in invited_users:
            bot.send_message(user_id, "🚫 Siz allaqachon taklif qilingan foydalanuvchisiz.")
            return

        if user_id != referrer_id:
            pending_users[user_id] = referrer_id  

    markup = InlineKeyboardMarkup()
    btn_subscribe = InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    btn_check = InlineKeyboardButton("✅ Bosdim", callback_data="check_subscription")
    markup.add(btn_subscribe)
    markup.add(btn_check)

    bot.send_message(user_id, f"📢 Avval {CHANNEL_USERNAME} kanaliga obuna bo‘ling va «✅ Bosdim» tugmasini bosing!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):
    user_id = str(call.message.chat.id)

    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "✅ Obuna bo‘ldingiz!")
        bot.send_message(user_id, "🎉 Siz muvaffaqiyatli obuna bo‘ldingiz!")

        if user_id in pending_users:
            referrer_id = pending_users.pop(user_id)

            if referrer_id in referrals_count:
                referrals_count[referrer_id] += 1
            else:
                referrals_count[referrer_id] = 1

            count = referrals_count[referrer_id]
            invited_users.add(user_id)
            save_data() 

            bot.send_message(referrer_id, f"🎉 {count} ta do‘stingiz obuna bo‘ldi!")

            if count >= 7:
                subscribed_users.add(referrer_id)  
                save_data()

                if is_bot_admin():
                    markup = InlineKeyboardMarkup()
                    btn_paid_channel = InlineKeyboardButton("🔓 Pullik kanalga kirish", url=PAID_CHANNEL_LINK)
                    markup.add(btn_paid_channel)
                    bot.send_message(referrer_id, "🎉 Siz 7 ta do‘stingizni taklif qildingiz! Quyidagi tugma orqali pullik kanalga kirishingiz mumkin:", reply_markup=markup)
                else:
                    bot.send_message(referrer_id, "⚠️ Bot kanalga admin emas! Iltimos, admin qilish uchun kanal sozlamalariga kiring.")

        referral_link = f"https://t.me/LinkGivePro_Bot?start={user_id}"
        bot.send_message(user_id, f"✅ Sizning referal havolangiz:\n{referral_link}\n"
                                  f"7 ta do‘stingizni taklif qiling va pullik kanalga kirish havolasini oling!")
    else:
        bot.answer_callback_query(call.id, "❌ Siz hali obuna bo‘lmagansiz!")

bot.polling()
