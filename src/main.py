import asyncio
import nest_asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import httpx
import os
# Токен бота
load_dotenv()
TOKEN=os.getenv('TOKEN')
API_KEY=os.getenv('API_KEY')
# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне фото растения, и я попробую его определить.")

# Обработчик фото
async def handle_photo(update: Update, context):
    try:
        # Получаем файл
        photo = update.message.photo[-1]
        file = await photo.get_file()
        photo_path = await file.download_to_drive()

        await update.message.reply_text("Фото получено, отправляю на анализ...")

        # Отправляем фото в Plant.id API
        response = await analyze_plant(photo_path)

        if response:
            plant_name = response.get("suggestions", [{}])[0].get("plant_name", "Не могу распознать растение.")
            await update.message.reply_text(f"Я думаю, что это: {plant_name}")
        else:
            await update.message.reply_text("Не удалось распознать растение.")

    except Exception as e:
        await update.message.reply_text("Ошибка при обработке фото.")
        logger.error(f"Ошибка: {e}")

# Функция для анализа растения через API
async def analyze_plant(image_path):
    url = "https://api.plant.id/v2/identify"

    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as image:
            files = {"images": image}
            data = {"organs": ["leaf"]}
            headers = {"Api-Key": API_KEY}

            response = await client.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Главная функция для запуска бота
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    await application.run_polling()

# Обход ошибки "RuntimeError: This event loop is already running"
nest_asyncio.apply()

async def run():
    await main()

if __name__ == "__main__":
    asyncio.run(run())  # Запускаем корректно событийный цикл

