import os
import asyncio
from flask import Flask
from threading import Thread
from google import genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

# Gemini Client Setup
ai_client = genai.Client(api_key=GEMINI_KEY)

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
    
    try:
        system_instruction = "You are an intelligent, friendly Movie Assistant. Recommend movies, summarize plots, and reply clearly in Myanmar language."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_instruction}\nUser Question: {user_text}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ခဏနေမှ ပြန်လည်မေးမြန်းပေးပါ၊ AI ချိတ်ဆက်မှုတွင် အနည်းငယ် ကြန့်ကြာနေပါသည်။")

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
    
