from flask import Flask, render_template
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from langdetect import detect
from googletrans import Translator
import os
import threading

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
# ✂️ تقسيم الترجمة فقط
# =========================
import re

def split_text(text, max_length=3500):
    # تقسيم إلى جمل
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    parts = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_length:
            current += " " + sentence
        else:
            parts.append(current.strip())
            current = sentence

    if current:
        parts.append(current.strip())

    return parts


# =========================
# 📩 التعامل مع الرسائل
# =========================
def handle_message(update, context):
    text = update.message.text

    try:
        lang = detect(text)
    except:
        return

    if lang == 'ar':
        target = 'ru'
    elif lang == 'ru':
        target = 'ar'
    else:
        update.message.reply_text("أرسل نصًا بالعربية أو الروسية فقط.")
        return

    translated = translate(text, target)

    # تقسيم فقط إذا كانت الترجمة طويلة
    parts = split_text(translated)

    for part in parts:
        update.message.reply_text(part)


# =========================
# ▶️ /start
# =========================
def start(update, context):
    update.message.reply_text(
        "أرسل أي رسالة وسأترجمها.\n"
        "إذا كانت طويلة سيتم تقسيم الترجمة."
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
