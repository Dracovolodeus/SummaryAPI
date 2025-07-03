from fastapi import APIRouter

from core.config import settings
from .summary import router as summary_router

router = APIRouter(prefix=settings.api.prefix.prefix)

router.include_router(summary_router)

