import asyncio

import httpx


async def process_urls(url_list: list[str], api_endpoint: str):
    """
    Асинхронно отправляет URL на обработку через указанный API endpoint

    Параметры:
        url_list (list[str]): Список URL для обработки
        api_endpoint (str): Базовый URL API (без параметров)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(
        timeout=30.0, headers=headers, http2=True, verify=False
    ) as client:
        tasks = [client.get(f"{api_endpoint}?url={url}") for url in url_list]

        # Выполняем все задачи параллельно
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        for url, response in zip(url_list, responses):
            if isinstance(response, Exception):
                print(f"⚠️ Ошибка для {url}: {type(response).__name__} - {response}")
            elif response.status_code == 200:
                print(f"✅ Успех для {url}: {response.json().get('message')}")
            else:
                print(
                    f"❌ Ошибка API для {url}: {response.status_code} - {response.text}"
                )


if __name__ == "__main__":
    # Настройки
    API_ENDPOINT = "http://0.0.0.0:8000/api/summary/create/url"
    URLS = [
        "https://habr.com/ru/companies/nexign/articles/786512/",
        "https://habr.com/ru/articles/683054/",
        "https://habr.com/ru/articles/889316/",
        "https://habr.com/ru/articles/706110/",
    ]

    # Запуск обработки
    asyncio.run(process_urls(URLS, API_ENDPOINT))
