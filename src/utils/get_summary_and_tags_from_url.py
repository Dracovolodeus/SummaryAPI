import asyncio
import logging

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from core.config import settings
from utils.case_converter import snake_case_to_pascale_case
from utils.extract_article_text import extract_article_text
from utils.fetch_url import fetch_url

logger = logging.getLogger(__name__)
gigachat_lock = asyncio.Lock()


async def request_for_gigachat(
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Асинхронная суммаризация с помощью GigaChat"""
    chat = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Ты - опытный аналитик, который умеет глубоко и качественно анализировать информацию и идеально следует запросам, а также четко и структурированно излагает мысли.",
            ),
            Messages(role=MessagesRole.USER, content=prompt),
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    async with gigachat_lock:
        logger.info("Отправка асинхронного запроса к GigaChat...")
        try:
            async with GigaChat(
                credentials=settings.ai.token,
                verify_ssl_certs=False,
                model="GigaChat",
            ) as giga:
                response = await giga.achat(chat)
                logger.info("Успешно получен ответ от GigaChat")
                return response.choices[0].message.content
        except Exception as e:
            logger.exception("Ошибка при запросе к GigaChat")
            return f"Ошибка GigaChat: {str(e)}"


async def get_tags(article_text: str) -> tuple[str]:
    """Асинхронное получение тегов"""
    answer = await request_for_gigachat(
        prompt=(
            "Ты профессиональный аналитик. Проведи глубокий анализ статьи и на его основе составь теги:\n"
            "- Используй только релевантные теги\n"
            "- Каждый тег начинается с '#'\n"
            "- Формат ответа: #Тег1; #Тег2; #Тег3\n"
            "- 3-10 кратких тегов\n"
            "- Без дополнительных комментариев\n\n"
            "Примеры:\n"
            "#Nvim; #Neovim; #Vim; #Программирование\n"
            "#Go; #Rust; #СравнениеЯзыков\n"
            "#FastAPI; #ВебРазработка; #Python\n\n"
            f"Текст статьи:\n{article_text}"
        ),
        temperature=0.35,
        max_tokens=25,
    )
    tags = []
    for tag in answer.split("; "):
        tag = tag.rstrip().lstrip()
        if " " in tag:
            tag = tag.replace(" ", "_")
            tag = snake_case_to_pascale_case(tag)

        if not tag.startswith("#"):
            tag = f"#{tag}"
        if len(tag) >= 4:
            tags.append(tag)
    return tuple(tags)


async def get_summary(article_text: str) -> str:
    """Асинхронное получение summary"""
    return await request_for_gigachat(
        prompt=(
            "Ты профессиональный аналитик. Составь summary по статье:\n"
            "- Объем: не более 144 слов\n"
            "- Структура:\n"
            "  1. Основная тема (1 предложение)\n"
            "  2. Ключевые тезисы (3-5 пунктов)\n"
            "  3. Выводы (при наличии)\n"
            "- Без маркеров списка\n"
            "- Максимально информативно\n\n"
            f"Текст статьи:\n{article_text}"
        ),
        temperature=0.185,
        max_tokens=256,
    )


async def get_summary_and_tags_from_url(url: str) -> tuple[str, tuple[str]]:
    """Основная функция с кешированием результатов"""
    article_text = await extract_article_text({"url": url, "html_text": fetch_url(url)})
    summary, tags = await asyncio.gather(
        get_summary(article_text), get_tags(article_text)
    )
    return summary, tags
