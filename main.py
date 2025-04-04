
from flask import Flask, render_template, request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import deepl
from langdetect import detect
import os
import threading

app = Flask('app')

@app.route('/')
def home():
    return render_template('index.html')

# Use environment variables for API keys
DEEPL_AUTH_KEY = os.environ.get('DEEPL_AUTH_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

translator = deepl.Translator(DEEPL_AUTH_KEY)

def translate(text, target_lang):
    try:
        result = translator.translate_text(text, target_lang=target_lang.upper())
        return result.text
    except Exception as e:
        return f"حدث خطأ أثناء الترجمة: {e}"

def handle_message(update, context):
    text = update.message.text
    try:
        lang = detect(text)
    except:
        update.message.reply_text("تعذّر تحديد اللغة.")
        return

    if lang == 'ar':
        target = 'ru'
    elif lang == 'ru':
        target = 'ar'
    else:
        update.message.reply_text("أرسل نصًا بالعربية أو الروسية فقط.")
        return

    translated = translate(text, target)
    update.message.reply_text(translated)

def start(update, context):
    update.message.reply_text("أرسل لي نصاً بالعربية أو الروسية وسأترجمه بإذن الله.")

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

if __name__ == '__main__':
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run Telegram bot in the main thread
    run_telegram_bot()
