import os
import asyncio
from flask import Flask
from threading import Thread
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

# Configure Gemini AI
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY.strip())

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🎬 Join Official Movie Channel", url="https://t.me/telegram")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_first_name}!\n\nကျွန်တော်ကတော့ Movie AI Assistant ဖြစ်ပါတယ်။\n"
        f"ဇာတ်ကားသစ် ညွှန်းခိုင်းချင်တာပဲဖြစ်ဖြစ်၊ ရုပ်ရှင်ဇာတ်လမ်း အကျဉ်းချုပ်တွေ မေးချင်တာပဲဖြစ်ဖြစ် စာရိုက်ပြီး မေးမြန်းနိုင်ပါပြီ!",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Try models in order of availability
    candidate_models = ['gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro']
    response_text = None
    last_error = None

    prompt = (
        "You are an intelligent, friendly Movie Assistant. "
        "Recommend movies, summarize plots, and reply clearly in Myanmar language.\n"
        f"User Question: {user_text}"
    )

    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and res.text:
                response_text = res.text
                break
        except Exception as e:
            last_error = e
            continue

    if response_text:
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("ခဏနေမှ ပြန်လည်မေးမြန်းပေးပါ၊ AI ချိတ်ဆက်မှု အနည်းငယ် ငြိမ်အောင် ပြန်လည်စမ်းသပ်နေပါသည်။")

def start_bot_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.updater.start_polling(drop_pending_updates=True))
    loop.run_until_complete(bot_app.start())
    loop.run_forever()

# Flask Server Setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Movie AI Bot is Running Live"

# Start Background Thread
bot_thread = Thread(target=start_bot_loop, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
