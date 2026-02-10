from typing import List

import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from env_utils import OPENAI_API_KEY, OPENAI_BASE_URL
from agent.services.schemas import (
    AllRawInsights,
    AllStrategicInsights,
    AllRankedInsights,
    AllMarketingContents,
    RawInsight,
    DistributorInput,
    DistributorOutput,
)
from agent.services.utils import cache_key, cache_get, cache_set, safe_invoke


def _make_llm(schema, temperature: float):
    return ChatOpenAI(
        model="gpt-5-mini",
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    ).with_structured_output(schema)


map_llm = _make_llm(AllRawInsights, 0.2)


MAP_PROMPT = ChatPromptTemplate.from_template("""
    Extract 2-3 factual business insights from the following document.

    Focus on:
    - Industry trends
    - Technologies
    - Concrete metrics

    Document:
    {content}

    Output JSON strictly matching:
    {schema}
    """, partial_variables={"schema": AllRawInsights.model_json_schema()})


def map_agent(retriever, query: str) -> List[RawInsight]:
    ck = cache_key("map", {"query": query})
    cached = cache_get(ck)
    if cached:
        return [RawInsight(**x) for x in cached]

    docs = retriever.get_relevant_documents(query)
    splitter = RecursiveCharacterTextSplitter(1200, 50)
    results = []
    chain = MAP_PROMPT | map_llm

    for doc in docs:
        for chunk in splitter.create_documents([doc.page_content])[:3]:
            res = safe_invoke(chain, {"content": chunk.page_content})
            for i in res.insights:
                i.source_id = doc.metadata["source_id"]
                i.source_url = doc.metadata["url"]
                results.append(i)

    cache_set(ck, [r.model_dump() for r in results])
    return results


reduce_llm = _make_llm(AllStrategicInsights, 0.2)


REDUCE_PROMPT = ChatPromptTemplate.from_template("""
    Merge, deduplicate and synthesize the following insights
    into FIVE strategic insights.

    Insights:
    {insights}

    Output JSON strictly matching:
    {schema}
    """, partial_variables={"schema": AllStrategicInsights.model_json_schema()})


def reduce_agent(raw_insights: List[RawInsight]) -> AllStrategicInsights:
    ck = cache_key("reduce", {"insights": [i.key_insight for i in raw_insights]})
    cached = cache_get(ck)
    if cached:
        return AllStrategicInsights(**cached)

    text = "\n".join(
        f"- {i.key_insight} (source={i.source_id})"
        for i in raw_insights
    )

    chain = REDUCE_PROMPT | reduce_llm
    res = safe_invoke(chain, {"insights": text})

    cache_set(ck, res.model_dump())
    return res




rank_llm = _make_llm(AllRankedInsights, 0.1)


RANK_PROMPT = ChatPromptTemplate.from_template("""
    Rank the following strategic insights.

    Score each insight by:
    - Business value
    - Content potential

    Insights:
    {insights}

    Output JSON strictly matching:
    {schema}
    """, partial_variables={"schema": AllRankedInsights.model_json_schema()})


def rank_agent(strategic: AllStrategicInsights) -> AllRankedInsights:
    ck = cache_key("rank", strategic.model_dump())
    cached = cache_get(ck)
    if cached:
        return AllRankedInsights(**cached)

    chain = RANK_PROMPT | rank_llm
    res = safe_invoke(chain, {"insights": strategic.model_dump()})

    cache_set(ck, res.model_dump())
    return res


content_llm = _make_llm(AllMarketingContents, 0.4)

CONTENT_PROMPT = ChatPromptTemplate.from_template("""
    Generate concrete marketing content based on the ranked insights.

    For each insight:
    - Choose the best content format
    - Write actual publishable content
    - Include CTA

    Ranked insights:
    {insights}

    Output JSON strictly matching:
    {schema}
    """, partial_variables={"schema": AllMarketingContents.model_json_schema()})


def marketing_content_agent(ranked: AllRankedInsights) -> AllMarketingContents:
    text = "\n".join(
        f"{i.insight_id}: {i.key_insight} (sources={i.source_ids})"
        for i in ranked.insights
    )

    chain = CONTENT_PROMPT | content_llm
    res = safe_invoke(chain, {"insights": text})

    return res


def distributor_agent(input_data: DistributorInput) -> DistributorOutput:
    """
    发布营销内容到 Facebook Page。
    """

    def normalize_content(marketing_content: dict) -> dict:
        if not isinstance(marketing_content, dict):
            return {}
        contents = marketing_content.get("contents")
        if isinstance(contents, list) and contents:
            if isinstance(contents[0], dict):
                return contents[0]
        return marketing_content

    content = normalize_content(input_data.marketing_content)
    headline = content.get("headline") or ""
    body = content.get("body") or content.get("body_text") or ""
    cta = content.get("cta") or content.get("call_to_action") or ""
    
    message = f"{headline}\n\n{body}\n\n{cta}"

    # Facebook Graph API endpoint
    url = f"https://graph.facebook.com/v17.0/{input_data.page_id}/feed"

    payload = {
        "message": message,
        "access_token": input_data.access_token
    }

    try:
        resp = requests.post(url, data=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return DistributorOutput(
            post_id=data.get("id"),
            status="success",
            response=data
        )
    except requests.HTTPError as e:
        return DistributorOutput(
            post_id="",
            status="failed",
            response={"error": str(e), "response_text": resp.text if 'resp' in locals() else ""}
        )
    

