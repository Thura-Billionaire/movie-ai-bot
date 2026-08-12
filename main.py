import os
import asyncio
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

def get_active_gemini_model(api_key):
    """Find an available model automatically from Google API"""
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(list_url, timeout=10)
        if res.status_code == 200:
            models_data = res.json().get('models', [])
            for m in models_data:
                # Look for flash or pro models that support generateContent
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    model_name = m.get('name')
                    if 'flash' in model_name or 'pro' in model_name:
                        return model_name
    except Exception:
        pass
    # Default fallback models if listing fails
    return "models/gemini-1.5-flash"

def call_gemini_api(user_prompt):
    if not GEMINI_KEY:
        return "Gemini API Key ထည့်သွင်းထားခြင်း မရှိသေးပါ။"
        
    api_key = GEMINI_KEY.strip()
    selected_model = get_active_gemini_model(api_key)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    "You are an intelligent, friendly Movie Assistant. "
                    "Recommend movies, summarize plots, and reply clearly in Myanmar language.\n"
                    f"User Question: {user_prompt}"
                )
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Error: {response.status_code} - Gemini API Key ကို အသစ်ပြန်ယူ၍ Render တွင် ပြန်ထည့်ပေးပါ။"
    except Exception as e:
        return "ချိတ်ဆက်မှု ကြန့်ကြာနေပါသည်၊ ခဏနေမှ ပြန်လည်စမ်းသပ်ပေးပါ။"

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
    
    loop = asyncio.get_running_loop()
    ai_response = await loop.run_in_executor(None, call_gemini_api, user_text)
    
    await update.message.reply_text(ai_response)

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
