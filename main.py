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

def split_text(text, max_length=2000):
    lines = text.split("\n")

    parts = []
    current = ""

    for line in lines:
        # نحافظ على السطر كما هو
        if current:
            candidate = current + "\n" + line
        else:
            candidate = line

        # إذا داخل الحد
        if len(candidate) <= max_length:
            current = candidate
        else:
            # 🔥 نحترم نهاية الجملة
            if not current:
                # إذا السطر وحدو طويل → نقسمو لجمل
                sentences = re.split(r'(?<=[.!?])\s+', line)
                for s in sentences:
                    if len(current) + len(s) + 1 <= max_length:
                        current += " " + s if current else s
                    else:
                        parts.append(current)
                        current = s
            else:
                parts.append(current)
                current = line

    if current:
        parts.append(current)

    return parts

# =========================
# 📩 التعامل مع الرسائل
# =========================
import time

def handle_message(update, context):
    if not update.message:
        return

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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="أرسل نصًا بالعربية أو الروسية فقط."
        )
        return

    # ✅ ترجمة
    translated = translate(text, target)

    # ✅ تقسيم
    parts = split_text(translated)

import time
import re

for part in parts:
    sent = False

    while not sent:
        try:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=part
            )
            sent = True
            time.sleep(1.5)

        except Exception as e:
            error_text = str(e)
            print("ERROR:", error_text)

            # 🔥 إذا كان flood control
            match = re.search(r"Retry in (\d+)", error_text)

            if match:
                wait_time = int(match.group(1))
                print(f"Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                time.sleep(5)

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
