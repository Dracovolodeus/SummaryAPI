import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import requests
from exceptions.any import NotFoundError, UnknownError
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

GIGACHAT_CREDENTIALS = "MTk3ZjlhZTktY2RlOC00YjljLTgyNmItOGIwMTE3N2IxYjdhOjEzNDY0OTBmLTJiMWQtNDdmNC1hYzI4LWFjOTM4OThhODI4Mw=="


def extract_article_text(url):
    """Извлечение текста статьи с помощью BeautifulSoup"""
    logger.info(f"Загрузка статьи по URL: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Удаление ненужных элементов
        for element in soup(
            ["script", "style", "header", "footer", "aside", "nav", "form", "button"]
        ):
            element.decompose()

        article = soup.find("article")
        text = article.get_text() if article else soup.get_text()

        # Очистка текста
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        if text.lower().startswith("ошибка") or text.lower().startswith("error"):
            raise UnknownError("Couldn't extract the text of the article")

        logger.info(f"The text of the article was successfully received")
        return text[:10000]
    except Exception as e:
        if ((not url.startswith("https") or not url.startswith("http")) or
            (type(e) is requests.exceptions.ConnectionError and "404" in str(e).split())):
            raise NotFoundError
        raise UnknownError(str(e))


def request_for_ai(prompt: str, temperature: float, max_tokens: int, timeout: int):
    """Суммаризация статьи с помощью GigaChat"""

    chat = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Ты - опытный аналитик, который умеет глубоко и качественно анализировать информацию и идеально следует запросам, а также четко и структурированно излагать мысли.",
            ),
            Messages(role=MessagesRole.USER, content=prompt),
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    logger.info("Отправка запроса к GigaChat...")
    try:
        with GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            verify_ssl_certs=False,
#           model="GigaCha-Pro",
            timeout=timeout,
        ) as giga:
            response = giga.chat(chat)
            logger.info("Успешно получен ответ от GigaChat")
            return response.choices[0].message.content
    except Exception as e:
        logger.exception("Ошибка при запросе к GigaChat")
        return f"Ошибка GigaChat: {str(e)}"


def get_tags(article_text: str) -> str:
    return request_for_ai(
        prompt=(
            "Ты профессиональный аналитик. Проведи глубокий анализ статьи и на его основе составь теги следующим пунктам:\n"
            "Сам анализ не нужен.\n"
            "Нужно в минимальный объем тегов вместить максимум информации.\n"

            "Каждый тег имеет в начале этот символ \"#\".\n"
            "Теги нужно дать в виде \"<Тег1>; <Тег2>; <Тег3>\"\n"
            "Достаточно 3-10 КРАТКИХ тегов. Кол-во тегов зависит от объема статьи, для кратких достаточно 3-4, для длинных 8-9.\n"
            "Никакие твои комментарии не нужны. В ответе только перечисли теги.\n"
            "Примеры:\n"
            "Nvim; Neovim; Vim; Программирование; Редактор кода; IDE\n"
            "Go; Rust; Языки программирования; Сравнение; Скорость\n"
            "FastAPI; API; Python; Разработка; Веб разработка\n\n"

            f"Текст статьи:\n{article_text[:5000]}"
        ),
        temperature=0.35, max_tokens=16, timeout=20
    )


def get_summary(article_text: str) -> str:
    return request_for_ai(
        prompt=(
            "Ты профессиональный аналитик. Проведи глубокий анализ статьи и на его основе составь summary по следующим пунктам:\n"
            "Сам анализ не нужен.\n"
            "Нужно в минимальный объем текста вместить максимум информации.\n"
            "План для составления summary\n"
            "1. Основная, главная тема. (1 предложение).\n"
            "2. Ключевые тезисы (3-5 пунктов).\n"
            "3. Выводы (кратко, при наличии).\n\n"

            f"Текст статьи:\n{article_text[:5000]}"
        ),
        temperature=0.185, max_tokens=192, timeout=120
    )


def get_summary_and_tags_from_url(url) -> tuple:
    article_text = extract_article_text(url)
    summary, tags = get_summary(article_text), get_tags(article_text)
    tags = tags.split("; ")
    if "#" in tags:
        tags.remove('#')
    return summary, tuple(tags)

