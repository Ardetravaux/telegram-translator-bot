from flask import Flask, render_template
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from langdetect import detect
from googletrans import Translator
import os
import threading
import time

app = Flask('app')

@app.route('/')
def home():
    return render_template('index.html')


# =========================
# 🔐 Environment Variables
# =========================
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

translator = Translator()


# =========================
# 🌍 الترجمة
# =========================
def translate(text, target_lang):
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        return f"خطأ في الترجمة: {e}"


# =========================
# ✂️ تقسيم النص
# =========================
def split_text(text, max_length=3000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


# =========================
# 🧠 تجميع الرسائل بدون تكرار
# =========================
user_data = {}

def process_user_text(user_id, context, timestamp):
    time.sleep(1.2)

    if user_id not in user_data or user_data[user_id]["time"] != timestamp:
        return

    text = user_data[user_id]["text"]

    try:
        lang = detect(text)
    except:
        return

    if lang == 'ar':
        target = 'ru'
    elif lang == 'ru':
        target = 'ar'
    else:
        context.bot.send_message(chat_id=user_id, text="أرسل نصًا بالعربية أو الروسية فقط.")
        return

    # تقسيم قبل الترجمة
    text_parts = split_text(text, 3000)

    for part in text_parts:
        translated = translate(part, target)

        # تقسيم بعد الترجمة (Telegram limit)
        translated_parts = split_text(translated, 4000)

        for t in translated_parts:
            context.bot.send_message(chat_id=user_id, text=t)
            time.sleep(0.4)

    del user_data[user_id]


# =========================
# 📩 استقبال الرسائل
# =========================
def handle_message(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"text": "", "time": 0}

    user_data[user_id]["text"] += " " + text
    user_data[user_id]["time"] = time.time()

    timestamp = user_data[user_id]["time"]

    threading.Thread(target=process_user_text, args=(user_id, context, timestamp)).start()


# =========================
# ▶️ /start
# =========================
def start(update, context):
    update.message.reply_text(
        "أرسل نصًا طويلًا أو عدة رسائل، وسأجمعها وأترجمها كاملة بدون تكرار."
    )


# =========================
# 🤖 تشغيل البوت
# =========================
def init_telegram_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    return updater


def run_telegram_bot():
    bot_updater = init_telegram_bot()
    bot_updater.idle()


# =========================
# 🚀 التشغيل
# =========================
if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.daemon = True
    flask_thread.start()

    run_telegram_bot()
