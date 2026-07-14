from pydantic import BaseModel
from datetime import datetime, timezone

class Request(BaseModel):
    company: str
    position: str
    links: list[str]
    rating: int
    description: str
    author: str
    create_date: datetime = str(datetime.now(timezone.utc))