
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import deepl
from langdetect import detect
import os

app = Flask(__name__)

@app.route('/')
def home():
    return open("index.html").read()

# Use environment variables for API keys
DEEPL_AUTH_KEY = os.environ.get('837d1d6a-b369-41a9-9e28-9bc1cebcb990:fx')
TELEGRAM_TOKEN = os.environ.get('7565032765:AAEL25UxEfr7I62mSiH7FF1lt7GUl5iICz0')

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

if __name__ == '__main__':
    # Initialize Telegram bot
    bot_updater = init_telegram_bot()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
    
    # Keep the bot running
    bot_updater.idle()
