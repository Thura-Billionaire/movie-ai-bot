import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🎬 Join Official Movie Channel", url="https://t.me/telegram")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_first_name}!\n\nကျွန်တော်ကတော့ ရုပ်ရှင်ချစ်သူများအတွက် AI Movie Assistant ဖြစ်ပါတယ်။\nဇာတ်ကား ရွေးချယ်ခိုင်းချင်တာပဲဖြစ်ဖြစ်၊ ရုပ်ရှင်နဲ့ ပတ်သက်တာတွေ မေးချင်တာပဲဖြစ်ဖြစ် စာရိုက်ပြီး မေးမြန်းနိုင်ပါတယ်!",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"AI က သင့်မေးခွန်းကို လက်ခံရရှိပါပြီ - '{user_text}'")

def run_async_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run polling smoothly without locking thread
    app.run_polling(drop_pending_updates=True, stop_signals=None)

# Flask Server for Render Keep-Alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot status: Running Live"

# Start Async Bot Thread
bot_thread = Thread(target=run_async_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port)
    
