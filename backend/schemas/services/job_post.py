from pydantic import BaseModel
from typing import TypedDict

class Job_Post(BaseModel):
    company : str
    position : str
    links: list[str]