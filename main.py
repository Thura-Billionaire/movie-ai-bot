import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask App for Keeping Alive
app = Flask(__name__)
@app.route('/')
def home():
    return "AI Bot is Running Smoothly!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Telegram Bot Token & Settings
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    # Task Button to Channel & WebApp
    keyboard = [
        [InlineKeyboardButton("🎬 Join Official Movie Channel", url="https://t.me/telegram")],
        [InlineKeyboardButton("🤖 Use AI Movie Assistant", web_app={"url": "https://bing.com"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_first_name}!\n\n"
        f"ကျွန်တော်ကတော့ ရုပ်ရှင်ချစ်သူများအတွက် AI Movie Assistant ဖြစ်ပါတယ်။\n"
        f"ဇာတ်ကား ရွေးချယ်ခိုင်းချင်တာပဲဖြစ်ဖြစ်၊ ရုပ်ရှင်နဲ့ ပတ်သက်တာတွေ မေးချင်တာပဲဖြစ်ဖြစ် စာရိုက်ပြီး မေးမြန်းနိုင်ပါတယ်!",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"AI က သင့်မေးခွန်းကို လက်ခံရရှိပါပြီ: '{user_text}'\n\n(ယခု စနစ်သည် အခြေခံ စမ်းသပ်အဆင့် ဖြစ်ပါသည်။)")

def main():
    # Start Flask Server
    Thread(target=run_flask).start()
    
    # Start Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()
  
