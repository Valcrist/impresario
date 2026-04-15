from pydantic import BaseModel


class FetchRequest(BaseModel):
    url: str


class FetchResponse(BaseModel):
    url: str
    status_code: int
    title: str
    html: str
