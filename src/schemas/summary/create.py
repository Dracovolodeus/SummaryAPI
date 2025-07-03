from pydantic import BaseModel


class Create(BaseModel):
    url: str
