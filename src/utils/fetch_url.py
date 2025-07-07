import httpx

from exceptions.any import NotFoundError, UnknownError


def fetch_url(url: str) -> str | None:
    """
    Получает HTML-содержимое веб-страницы по указанному URL.

    Параметры:
        url (str): URL-адрес веб-страницы

    Возвращает:
        str: HTML-содержимое при успешном запросе (статус 200)
        None: в случае ошибки или неверного статуса
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Отключаем проверку SSL и устанавливаем таймаут
        with httpx.Client(http2=True, verify=False, timeout=10.0) as client:
            response = client.get(url, headers=headers, follow_redirects=True)

        # Проверяем успешный статус
        if response.status_code == 200:
            return response.text
        else:
            raise NotFoundError("Not found error")
    except httpx.HTTPError as e:
        raise UnknownError(f"{e}")
