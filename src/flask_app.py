import threading
import time
import requests
from flask import Flask, request, Response
from core.config import settings

app = Flask(__name__)
FASTAPI_URL = f"http://{settings.run.host}:{settings.run.port}"  # Без слэша в конце

def run_fastapi():
    from main import main  # Локальный импорт для избежания циклических зависимостей
    main()

def is_fastapi_ready():
    try:
        return requests.get(FASTAPI_URL, timeout=2).status_code < 500
    except:
        return False

@app.before_request
def wait_for_fastapi():
    # Ожидание готовности FastAPI (макс 30 секунд)
    for _ in range(30):
        if is_fastapi_ready():
            return
        time.sleep(1)
    return Response("FastAPI backend not available", status=502)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    target_url = f"{FASTAPI_URL}/{path}" if path else FASTAPI_URL
    
    headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'content-length']}
    
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        timeout=30  # Таймаут на запрос
    )
    
    return Response(
        resp.content,
        status=resp.status_code,
        headers=dict(resp.headers)
    )

if __name__ == '__main__':
    # Ожидание готовности FastAPI перед запуском Flask
    time.sleep(3)
    
    app.run(
        port=settings.run.flask_port,
        debug=True,
        use_reloader=False  # Важно для работы в потоке
    )
