from flask import Flask, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text:
        return

    if contains_url(text):
        return

    try:
        lang = detect(text)
    except:
        return

    if lang == 'ar':
        target = 'ru'
    elif lang == 'ru':
        target = 'ar'
    else:
        await update.message.reply_text("أرسل نصًا بالعربية أو الروسية فقط.")
        return

    original_parts = split_text(text)

    for part in original_parts:
        translated = translate(part, target)
        translated_parts = split_text(translated)

        for t_part in translated_parts:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=t_part,
                reply_to_message_id=update.message.message_id
            )
            await asyncio.sleep(0.4)


# =========================
# ▶️ أمر /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل لي نصًا بالعربية أو الروسية وسأترجمه لك.\n"
        "Пришли мне текст на арабском или русском языке, и я его переведу.\n"
        "https://t.me/Jamaatalmuslimin"
    )


# =========================
# 🤖 تشغيل البوت
# =========================
import asyncio

async def run_telegram_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app_bot.run_polling()


# =========================
# 🚀 التشغيل
# =========================
if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.daemon = True
    flask_thread.start()

    asyncio.run(run_telegram_bot())
