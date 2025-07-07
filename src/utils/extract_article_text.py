import logging

from bs4 import BeautifulSoup, Comment

from core.config import settings
from exceptions.any import UnknownError

logger = logging.getLogger(__name__)


async def extract_article_text(content: dict) -> str:
    """
    Improved asynchronous extraction of article text
    content keys:
        url - url
        html_text - content by url
    """
    logger.info(f"Start extract text from {content['url']}")

    try:
        soup = BeautifulSoup(content["html_text"], "html.parser")

        # Remove unnecessary items
        for element in soup(
            [
                "script",
                "style",
                "header",
                "footer",
                "aside",
                "nav",
                "form",
                "button",
                "iframe",
                "noscript",
            ]
        ):
            element.decompose()

        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Extended search for main content
        article = None
        content_selectors = [
            {"name": "article"},
            {"selector": "main"},
            {"selector": ".article-content"},
            {"selector": ".post-content"},
            {"selector": ".entry-content"},
            {"selector": ".story-content"},
            {"selector": "#article-body"},
            {"selector": "#main-content"},
            {"selector": ".content-wrapper"},
        ]

        for selector in content_selectors:
            if "name" in selector:
                article = soup.find(selector["name"])
            else:
                article = soup.select_one(selector["selector"])

            if article:
                logger.debug(f"Used selector: {selector} for {content['url']}")
                break

        text = ""
        if article:
            text = article.get_text(separator=" ", strip=True)
        else:
            logger.warning(
                f"No article container found for {content['url']}, using full text"
            )
            text = soup.get_text(separator=" ", strip=True)

        # Improved text cleaning
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)

        # Trimming while preserving whole words
        if len(cleaned_text) > settings.ai.max_text_length:
            logger.info(
                f"Text truncated to {settings.ai.max_text_length} chars for {content['url']}"
            )
            end_index = cleaned_text.rfind(" ", 0, settings.ai.max_text_length)
            cleaned_text = (
                cleaned_text[:end_index] + "..."
                if end_index != -1
                else cleaned_text[: settings.ai.max_text_length] + "..."
            )

        logger.info(f"Successful text extraction from {content['url']}")
        return cleaned_text

    except Exception as e:
        logger.exception(
            f"Unexpected error in article extraction from {content['url']}"
        )
        raise UnknownError(str(e))
