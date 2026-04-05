from flask import Flask, render_template
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import deepl
from langdetect import detect
import os
import threading
import re
import time

app = Flask('app')

@app.route('/')
def home():
    return render_template('index.html')


# =========================
# 🔐 Environment Variables
# =========================
DEEPL_AUTH_KEY = os.environ.get('DEEPL_AUTH_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

translator = deepl.Translator(DEEPL_AUTH_KEY)


# =========================
# 🔗 تجاهل الروابط
# =========================
def contains_url(text):
    url_pattern = r'(https?://\S+|www\.\S+)'
    return re.search(url_pattern, text) is not None


# =========================
# ✂️ تقسيم النص الطويل
# =========================
def split_text(text, max_length=3000):
    parts = []
    while len(text) > max_length:
        part = text[:max_length]

        # نحاول نقطع عند آخر مسافة
        last_space = part.rfind(" ")
        if last_space != -1:
            part = text[:last_space]

        parts.append(part)
        text = text[len(part):]

    parts.append(text)
    return parts


# =========================
# 🌍 الترجمة
# =========================
def translate(text, target_lang):
    try:
        result = translator.translate_text(text, target_lang=target_lang.upper())
        return result.text
    except Exception as e:
        return f"حدث خطأ أثناء الترجمة: {e}"


# =========================
# 📩 التعامل مع الرسائل
# =========================
def handle_message(update, context):
    text = update.message.text.strip()

    # 🚫 تجاهل الرسائل الفارغة
    if not text:
        return

    # 🚫 تجاهل الروابط
    if contains_url(text):
        return

    # 🌐 تحديد اللغة
    try:
        lang = detect(text)
    except:
        return  # بدون رسالة خطأ

    # 🎯 اختيار اللغة الهدف
    if lang == 'ar':
        target = 'ru'
    elif lang == 'ru':
        target = 'ar'
    else:
        update.message.reply_text("أرسل نصًا بالعربية أو الروسية فقط.")
        return

    # ✂️ تقسيم النص الطويل
    parts = split_text(text)

    total_parts = len(parts)

    for i, part in enumerate(parts, start=1):
        translated = translate(part, target)

        # 🧾 ترقيم الأجزاء (اختياري)
        if total_parts > 1:
            message = f"({i}/{total_parts})\n{translated}"
        else:
            message = translated

        update.message.reply_text(message)

        # ⏳ تجنب Flood
        time.sleep(0.4)


# =========================
# ▶️ أمر /start
# =========================
def start(update, context):
    update.message.reply_text(
        "أرسل لي نصًا بالعربية أو الروسية وسأترجمه لك.\n"
        "Пришли мне текст на арабском или русском языке, и я его переведу."
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
    # Flask في Thread منفصل
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.daemon = True
    flask_thread.start()

    # Telegram bot
    run_telegram_bot()
