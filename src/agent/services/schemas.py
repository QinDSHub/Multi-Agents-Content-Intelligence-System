from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

############## map phase ###############
class RawInsight(BaseModel):
    key_insight: str
    trend: str
    technology: Optional[str]
    data_points: Optional[str]
    source_id: str
    source_url: Optional[str]


class AllRawInsights(BaseModel):
    insights: List[RawInsight]



############## reduce phase ###############
class StrategicInsight(BaseModel):
    insight_id: str
    key_insight: str
    strategic_relevance: str

class AllStrategicInsights(BaseModel):
    insights: List[StrategicInsight]


############## rank phase ##############
class RankedInsight(BaseModel):
    insight_id: str
    key_insight: str
    business_value_score: int = Field(ge=1, le=10)
    content_potential_score: int = Field(ge=1, le=10)
    reasoning: str
    source_ids: List[str]

class AllRankedInsights(BaseModel):
    insights: List[RankedInsight]


############## final output for posting content ##############
class MarketingContent(BaseModel):
    insight_id: str 
    content_format: str
    headline: str
    body_text: str
    call_to_action: str
    target_audience: str
    distribution_channel: List[str]
    sources: List[str]

class AllMarketingContents(BaseModel):
    contents: List[MarketingContent]


############## Automated Posting to Facebook social media ##############
class DistributorInput(BaseModel):
    marketing_content: Dict[str, Any]  # output of marketing_content_agent
    page_id: str
    access_token: str

class DistributorOutput(BaseModel):
    post_id: str
    status: str
    response: Dict[str, Any]




