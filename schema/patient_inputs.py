from pydantic import BaseModel, Field
from typing import Optional

class BasicInfo(BaseModel):
    age: int = Field(..., gt=10, lt=120)
    sex: str = Field(..., example="male")
    test_time: float

# Note: The /analyze/voice endpoint currently accepts raw multipart form fields
# rather than a JSON body, so these models are used as reference schemas only.