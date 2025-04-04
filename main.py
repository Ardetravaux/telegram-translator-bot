from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import deepl
from langdetect import detect

# إعداد خادم Flask للإبقاء على Replit نشطًا
app = Flask('')
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return from flask import Flask

app = Flask(__name__)

# Your existing routes and logic here...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)open("index.html").read()

def keep_alive():
    t = Thread(target=run)
    t.start()

# أدخل مفتاح DeepL هنا
DEEPL_AUTH_KEY = "837d1d6a-b369-41a9-9e28-9bc1cebcb990:fx"
translator = deepl.Translator(DEEPL_AUTH_KEY)

# دالة الترجمة
def translate(text, target_lang):
    try:
        result = translator.translate_text(text, target_lang=target_lang.upper())
        return result.text
    except Exception as e:
        return f"حدث خطأ أثناء الترجمة: {e}"

# دالة استقبال الرسائل
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

# دالة البدء
def start(update, context):
    update.message.reply_text("أرسل لي نصاً بالعربية أو الروسية وسأترجمه بإذن الله.")

# توكن البوت من BotFather
TELEGRAM_TOKEN = "7565032765:AAEL25UxEfr7I62mSiH7FF1lt7GUl5iICz0"

# إعداد البوت
updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ربط الأوامر والرسائل
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# تشغيل الخادم والبوت
keep_alive()
updater.start_polling()
updater.idle()