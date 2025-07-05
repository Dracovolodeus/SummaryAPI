from fastapi import APIRouter

from core.config import settings

from .create import router as create_router

router = APIRouter(prefix=f"{settings.api.prefix.summary}")
router.include_router(create_router)
