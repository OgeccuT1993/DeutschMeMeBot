
import logging
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это DeutschMeMeBot. Напиши /guess чтобы сыграть в угадайку!")

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 5)
    await update.message.reply_text("Я загадал число от 1 до 5... Попробуй угадать!")
    await update.message.reply_text(f"Хаха, это было: {number}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("guess", guess))
    app.run_polling()
