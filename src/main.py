import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import httpx

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка .env
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

API_ENDPOINT = os.getenv("API_URL") + "/api/summary/create/url"

# Обработчик команды /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Отправь мне URL статьи для получения summary и тегов")

# Обработчик текстовых сообщений (URL)
@dp.message(F.text)
async def handle_url(message: types.Message):
    url = message.text.strip()
    
    # Валидация URL
    if not url.startswith(('http://', 'https://')):
        return await message.answer("⚠️ Пожалуйста, отправьте корректный URL")

    try:
        async with httpx.AsyncClient(timeout=113) as client:
            response = await client.get(
                API_ENDPOINT,
                params={"url": url}  # Параметры GET-запроса
            )            
        # Обработка статус-кодов
        if response.status_code == 201:
            data = response.json()
            response_text = (
                f"📝{data['summary']}\n\n"
                f"🏷 Теги:\n{', '.join(data['tags'])}"
            )
        elif response.status_code == 404:
            response_text = "❌ Статья не найдена (404)"
        elif response.status_code == 500:
            response_text = "🚫 Ошибка сервера (500)"
        else:
            response_text = f"⚠️ Неизвестная ошибка: {response.status_code}"

    except httpx.ConnectError:
        response_text = "🔌 Ошибка подключения к API"
    except httpx.ReadTimeout:
        response_text = "⏱ Таймаут при запросе к API"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        response_text = "⚠️ Непредвиденная ошибка"

    await message.answer(response_text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
