
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
        "Добро пожаловать в DeutschMeMeBot! Команды:\n"
        "/talk — поболтать с ИИ\n"
        "/setstyle — выбрать стиль\n"
        "/guessnumber — угадай число\n"
        "/rps — камень/ножницы/бумага\n"
        "/quiz — мем-викторина\n"
        "/truthorlie — правда или ложь\n"
        "/insultme — оскорбление/комплимент\n"
        "/advice — тупой совет дня\n"
        "/meme — сгенерировать текстовый мем\n"
        "/tiktok — идея или фраза для TikTok",
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

async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    шаблоны = [
        "Когда {situation}, но ты {reaction}.",
        "Не я: {normal}\nЯ: {weird}",
        "{action}? Это что, я в 2020?",
        "Если бы мемы платили, я был бы миллионером."
    ]
    слова = [
        "работать на выходных", "улыбаешься через боль", "спишь по 3 часа",
        "думаешь, что всё под контролем", "смотришь в потолок", "разговариваешь с холодильником",
        "я программист", "я в 4 утра", "я в TikTok 6-й час подряд"
    ]
    текст = random.choice(шаблоны).format(
        situation=random.choice(слова),
        reaction=random.choice(слова),
        normal=random.choice(слова),
        weird=random.choice(слова),
        action=random.choice(слова)
    )
    await update.message.reply_text(текст)

async def tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    идеи = [
        "Сними ролик, где ты споришь с собой в зеркале.",
        "Покажи, как выглядишь до и после фразы 'всё нормально'.",
        "Сделай TikTok, где главный герой — твой будильник.",
        "Переозвучь свой день в стиле Netflix-драмы."
    ]
    фразы = [
        "Я не прокрастинирую, я на паузе жизни.",
        "Ты либо сгорел, либо перегорел.",
        "Этот TikTok был снят за счёт моей мотивации. RIP.",
        "Главное — делать вид, что ты в контроле."
    ]
    if random.choice([True, False]):
        await update.message.reply_text("**Идея для TikTok:**\n" + random.choice(идеи), parse_mode="Markdown")
    else:
        await update.message.reply_text("**Фраза для TikTok:**\n" + random.choice(фразы), parse_mode="Markdown")

def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setstyle", set_style))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("tiktok", tiktok))
    app.add_handler(MessageHandler(filters.Regex("^(романтик|гопник|дед|default)$"), handle_style_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_response))
    return app

if __name__ == '__main__':
    build_app().run_polling()
    
