from pydantic import BaseModel
from typing import Optional

# 데이터 스키마

class Cow(BaseModel):
    id: str
    number: str
    birthdate: Optional[str]
    breed: Optional[str]

    