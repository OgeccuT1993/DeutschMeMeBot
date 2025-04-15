
import os
import logging
import random
import openai
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    filters
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

STYLES = {
    "default": "Ты странный, постироничный, слегка поехавший Telegram-бот с чёрным юмором.",
    "романтик": "Ты поэтичный, романтичный бот, говоришь, как будто ты герой любовного романа.",
    "гопник": "Ты дерзкий, слегка хамоватый бот с улиц 90-х. Много сленга и понтов.",
    "дед": "Ты говоришь, как советский дед, ворчливый, но мудрый.",
}

user_styles = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_styles[update.effective_user.id] = "default"
    await update.message.reply_text(
        "Добро пожаловать в DeutschMeMeBot! Команды:
"
        "/talk — поболтать с ИИ
"
        "/setstyle — выбрать стиль
"
        "/guessnumber — угадай число
"
        "/rps — камень/ножницы/бумага
"
        "/quiz — мем-викторина
"
        "/truthorlie — правда или ложь
"
        "/insultme — оскорбление/комплимент
"
        "/advice — тупой совет дня",
    )

async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["романтик", "гопник", "дед", "default"]]
    await update.message.reply_text("Выбери стиль:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

async def handle_style_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text.strip().lower()
    if style in STYLES:
        user_styles[update.effective_user.id] = style
        await update.message.reply_text(f"Стиль установлен: {style}")
    else:
        await update.message.reply_text("Неизвестный стиль.")

async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = user_styles.get(update.effective_user.id, "default")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": STYLES[style]},
                {"role": "user", "content": update.message.text}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except:
        await update.message.reply_text("GPT завис. Попробуй позже.")

async def guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    context.user_data["secret_number"] = number
    await update.message.reply_text("Я загадал число от 1 до 100. Попробуй угадать!")

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "secret_number" not in context.user_data:
        return
    try:
        guess = int(update.message.text)
        secret = context.user_data["secret_number"]
        if guess < secret:
            await update.message.reply_text("Больше.")
        elif guess > secret:
            await update.message.reply_text("Меньше.")
        else:
            await update.message.reply_text("ДА! Ты угадал!")
            del context.user_data["secret_number"]
    except ValueError:
        pass

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Я выбрал: {random.choice(['камень', 'ножницы', 'бумага'])}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Кто из них не мем?
A) Шрек
B) Гигачад
C) Windows XP
D) Бублик")

async def truthorlie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Правда или ложь: В Германии запрещено называть ребёнка Nutella.")

async def insult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice([
        "Ты как Wi-Fi в автобусе — вроде есть, а вроде и нет.",
        "Ты светишься как BIOS в тумане.",
        "Ты не тупой — ты альтернативно умный."
    ]))

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice([
        "Не можешь изменить мир — смени шторы.",
        "Будь собой. Остальное — баги в системе.",
        "Пиши глупости — вдруг это станет искусством."
    ]))

def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setstyle", set_style))
    app.add_handler(MessageHandler(filters.Regex("^(романтик|гопник|дед|default)$"), handle_style_choice))
    app.add_handler(CommandHandler("guessnumber", guess_number))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("truthorlie", truthorlie))
    app.add_handler(CommandHandler("insultme", insult))
    app.add_handler(CommandHandler("advice", advice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_response))
    return app

if __name__ == '__main__':
    app = build_app()
    app.run_polling()
