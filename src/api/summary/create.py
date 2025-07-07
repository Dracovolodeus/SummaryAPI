from fastapi import APIRouter, HTTPException, status

from core.config import settings
from exceptions.any import NotFoundError, UnknownError
from schemas.summary.create import Create
from schemas.summary.read import Read
from utils.get_summary_and_tags_from_url import get_summary_and_tags_from_url

router = APIRouter(prefix=f"{settings.api.prefix.create}")


@router.get(f"{settings.api.prefix.url}", status_code=status.HTTP_201_CREATED)
async def create_summary(url: str):
    try:
        summary, tags = await get_summary_and_tags_from_url(url)
        return Read(summary=summary, tags=tags)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found error"
        )
    except UnknownError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="UnknownError"
        )
