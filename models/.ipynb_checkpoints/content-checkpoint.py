from pydantic import BaseModel, Field
from typing import List

class ContentIdea(BaseModel):
    content_format: str
    key_insights: List[str]
    target_objective: str
    target_audience: List[str]
    distribution_strategy: List[str]
    priority: int = Field(ge=1)
    explanation: str