import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from core.config import settings

main_app = FastAPI()

main_app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host="0.0.0.0",  # settings.run.host,
        port=8000,  # settings.run.port,
        reload=True,
    )
