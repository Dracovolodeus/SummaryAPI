from pydantic import BaseModel


class Read(BaseModel):
    summary: str
    tags: tuple
