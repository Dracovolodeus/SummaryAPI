from fastapi import APIRouter, status, HTTPException
from core.config import settings
from schemas.summary.create import Create
from schemas.summary.read import Read
from exceptions.any import NotFoundError, UnknownError

from utils.get_summary_and_tags_from_url import get_summary_and_tags_from_url

router = APIRouter(prefix=f"{settings.api.prefix.create}")


@router.get(f"{settings.api.prefix.url}", status_code=status.HTTP_201_CREATED)
async def create_summary(url: str):
    summary, tags = get_summary_and_tags_from_url(url)
    try:
        return Read(
            summary=summary, tags=tags
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found error"
        )
    except UnknownError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="UnknownError"
        )

