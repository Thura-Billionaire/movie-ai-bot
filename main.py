import os
import asyncio
from flask import Flask
from threading import Thread
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY.strip())

def call_gemini_api(user_prompt):
    if not GEMINI_KEY:
        return "⚠️ Gemini API Key ထည့်သွင်းထားခြင်း မရှိသေးပါ။"
        
    system_instruction = (
        "You are an intelligent, friendly Movie Assistant. "
        "Recommend movies, summarize plots, and reply clearly in Myanmar language.\n"
        f"User Question: {user_prompt}"
    )
    
    # Try using official SDK model names
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(system_instruction)
            if response and response.text:
                return response.text
        except Exception:
            continue
            
    return "⚠️ API Key စစ်ဆေးရန် လိုအပ်နေပါသည်။ Google AI Studio (aistudio.google.com) မှ API Key အသစ်တစ်ခု ပြန်ထုတ်ပေးပါရန်။"

# Telegram Handlers
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
    
    loop = asyncio.get_running_loop()
    ai_response = await loop.run_in_executor(None, call_gemini_api, user_text)
    
    await update.message.reply_text(ai_response)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.updater.start_polling(drop_pending_updates=True))
    loop.run_until_complete(bot_app.start())
    loop.run_forever()

# Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Movie AI Bot is Alive and Running"

if __name__ == '__main__':
    t = Thread(target=run_bot, daemon=True)
    t.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
