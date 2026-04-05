from flask import Flask, render_template
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import deepl
from langdetect import detect
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
DEEPL_AUTH_KEY = os.environ.get('DEEPL_AUTH_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

translator = deepl.Translator(DEEPL_AUTH_KEY)


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
# ✂️ تقسيم الترجمة
# =========================
def split_text(text, max_length=4000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


# =========================
# 🧠 تجميع الرسائل
# =========================
user_buffers = {}
user_timers = {}

def process_user_text(user_id, context):
    text = user_buffers.get(user_id, "").strip()

    if not text:
        return

    user_buffers[user_id] = ""

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

    translated = translate(text, target)

    parts = split_text(translated)

    for part in parts:
        context.bot.send_message(chat_id=user_id, text=part)
        time.sleep(0.4)


# =========================
# 📩 استقبال الرسائل
# =========================
def handle_message(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    if user_id not in user_buffers:
        user_buffers[user_id] = ""

    user_buffers[user_id] += " " + text

    # إعادة ضبط المؤقت
    if user_id in user_timers:
        user_timers[user_id].cancel()

    timer = threading.Timer(1.2, process_user_text, args=(user_id, context))
    user_timers[user_id] = timer
    timer.start()


# =========================
# ▶️ /start
# =========================
def start(update, context):
    update.message.reply_text(
        "أرسل لي نصًا طويلًا أو قصيرًا وسأترجمه كاملًا.\n"
        "يمكنك إرسال عدة رسائل متتالية وسيتم جمعها."
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
