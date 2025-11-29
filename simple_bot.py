"""
Simple Telegram Bot - Responds to "ساام"
بات ساده تلگرام - پاسخ به "ساام"
"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن بات
BOT_TOKEN = "8587674168:AAEa_llY2S0JtVyE3cW22J_a9JHQMNlO7Jw"

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start"""
    await update.message.reply_text(
        "سلام! 👋\n"
        "من یک بات چت هستم.\n"
        "وقتی بگی 'ساام' بهت جواب می‌دم!\n"
        "همچنین می‌تونی با من چت کنی. 😊"
    )

# دستور /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /help"""
    await update.message.reply_text(
        "📝 راهنما:\n"
        "• فقط بگو 'ساام' تا بهت جواب بدم\n"
        "• هر چیزی بگی باهات حرف می‌زنم\n"
        "• دستورات:\n"
        "  /start - شروع\n"
        "  /help - راهنما"
    )

# پاسخ به "ساام"
async def handle_salam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به پیام‌های حاوی 'ساام'"""
    message_text = update.message.text.strip()
    
    # اگر پیام شامل "ساام" بود
    if "ساام" in message_text or "سام" in message_text:
        responses = [
            "سلام! چطوری؟ 😊",
            "هِی! خوبی؟ 👋",
            "ساااام! چه خبر؟ 🤗",
            "علیک سلام! حالت چطوره؟ ✨",
            "سلام عزیز! چیکار کنم براتon? 💫"
        ]
        import random
        response = random.choice(responses)
        await update.message.reply_text(response)
    else:
        # پاسخ به پیام‌های معمولی
        await chat_response(update, context)

# پاسخ به پیام‌های معمولی
async def chat_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به پیام‌های عادی"""
    message_text = update.message.text.strip()
    
    # پاسخ‌های ساده
    if "چطوری" in message_text or "خوبی" in message_text:
        await update.message.reply_text("ممنون! من خوبم 😊 تو چطوری؟")
    elif "خوبم" in message_text or "عالی" in message_text:
        await update.message.reply_text("چه خوب! خوشحالم که خوبی 🎉")
    elif "بای" in message_text or "خداحافظ" in message_text:
        await update.message.reply_text("خداحافظ! مواظب خودت باش 👋")
    elif "اسمت چیه" in message_text or "کی هستی" in message_text:
        await update.message.reply_text("من یک بات چت هستم! اسمم رو می‌تونی هر چی دوست داری بذاری 😊")
    elif "ممنون" in message_text or "مرسی" in message_text:
        await update.message.reply_text("خواهش می‌کنم! 🤗")
    else:
        # پاسخ پیش‌فرض
        responses = [
            "جالب بود! بگو چیز دیگه‌ای 🤔",
            "آهان! بیشتر بگو 👂",
            "درک می‌کنم... ادامه بده 💭",
            "حتماً! و بعدش؟ 🌟",
            "می‌شنوم... 👀"
        ]
        import random
        response = random.choice(responses)
        await update.message.reply_text(response)

def main():
    """اجرای بات"""
    # ساخت اپلیکیشن
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_salam))
    
    # شروع بات
    logger.info("🤖 بات شروع به کار کرد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
