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
def split_text(text, max_length=3500):
    if len(text) <= max_length:
        return [text]

    parts = []
    total_len = len(text)

    # نحسب عدد الأجزاء المطلوبة
    num_parts = (total_len // max_length) + 1
    part_len = total_len // num_parts

    start = 0
    for i in range(num_parts):
        end = start + part_len

        # نحاول نقطع عند أقرب مسافة
        if end < total_len:
            space = text.rfind(" ", start, end)
            if space != -1:
                end = space

        parts.append(text[start:end].strip())
        start = end

    if start < total_len:
        parts.append(text[start:].strip())

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
