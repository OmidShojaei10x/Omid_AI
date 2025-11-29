#!/usr/bin/env python3
"""
Simple Telegram bot that only replies to greetings like «سلام» or «ساام».
No Supabase, no AI — just a friendly hello.
"""

import logging
import os
from typing import Set

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("salam-bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("لطفاً متغیر محیطی TELEGRAM_BOT_TOKEN را تنظیم کنید.")

SALAAM_VARIANTS: Set[str] = {
    "سلام",
    "سلااام",
    "سلاااام",
    "ساام",
    "سلاممم",
    "سلامممم",
    "سلاممممم",
    "salam",
    "salaam",
    "salammm",
}


def _normalize(text: str) -> str:
    return "".join(text.split()).lower()


def _is_greeting(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False
    if normalized in SALAAM_VARIANTS:
        return True
    return normalized.startswith("سلام")


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = (user.first_name or user.username or "دوست عزیز").strip()
    await update.message.reply_text(f"سلام {name}! 👋 هر وقت «سلام» بگی من جواب میدم.")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("کافیه «سلام» یا «ساام» بگی تا جوابت رو بدم 😊")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return

    if _is_greeting(text):
        user = update.effective_user
        name = (user.first_name or user.username or "دوست عزیز").strip()
        await update.message.reply_text(f"سلام {name}! 😊 حالت چطوره؟")
        return

    await update.message.reply_text("من یه بات سلام‌گو هستم؛ فقط «سلام» بگو تا جواب بدم 🤗")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & (~filters.COMMAND), message_handler))

    logger.info("Simple salam bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
