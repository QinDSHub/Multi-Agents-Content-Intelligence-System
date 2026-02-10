# 6_MULTI_AGENTS Optimized

Multi-agent workflow built with LangGraph for researching industry reports, extracting insights, ranking them, generating marketing content, and optionally distributing posts to Facebook.

## What this project does

- Searches the web for relevant industry reports.
- Builds a vector retriever and summarizes insights (map -> reduce -> rank).
- Generates publishable marketing content from ranked insights.
- Supports a manual review gate before automated distribution.

## Architecture

Nodes are defined in [src/agent/graph.py](src/agent/graph.py):

1. research: search and build retriever
2. map: extract raw insights
3. reduce: synthesize strategic insights
4. rank: score and order insights
5. content_generator: generate marketing content
6. distributor: post to Facebook (optional, gated)

## Setup

### Install

```bash
cd d:/projects/6_multi_agents_optimized
pip install -e . "langgraph-cli[inmem]"
```

### Environment variables

Create a .env file in the project root:

```text
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional if you integrate Tavily later
TAVILY_API_KEY=your_key
TAVILY_BASE_URL=https://api.tavily.com
```

### Run the LangGraph server

```bash
langgraph dev
```

### Run locally (example)

```bash
python -m agent.graph
```

You will see a manual confirmation prompt before any distribution action.

## Quickstart (sample inputs)

The default demo values are in [src/agent/graph.py](src/agent/graph.py). You can change them directly or pass a custom state when running in a script.

Example state values you can use:

```python
initial_state = {
	"company": "OpenAI",
	"year": "2025",
	"period": "full year",
	"steps": [],
	# Optional for distribution:
	# "page_id": "YOUR_FACEBOOK_PAGE_ID",
	# "fb_access_token": "YOUR_ACCESS_TOKEN",
}
```

If you set `page_id` and `fb_access_token`, the distributor node can post after you confirm.

## Troubleshooting

- Search returns empty results: Google HTML can change or rate limit. Try again later or swap in a paid search API.
- `OPENAI_API_KEY` missing: ensure your .env is in the project root and `dotenv` loads it.
- `No data retrieved from search`: verify search results are non-empty and the network is available.
- Facebook post fails: confirm `page_id` and `fb_access_token` are valid and have publish permissions.
- Cache conflicts: delete the `.agent_cache` folder to reset cached outputs.

## Notes

- The search utility uses Google HTML parsing and can be rate limited. For production, consider a dedicated search API.
- Retriever building stores embeddings in memory for each run.
- Simple disk caching is used in .agent_cache for map/reduce/rank results.

## Project structure

- [src/agent/graph.py](src/agent/graph.py): graph definition and entry point
- [src/agent/services/multi_agents.py](src/agent/services/multi_agents.py): LLM agents and Facebook distributor
- [src/agent/services/rag.py](src/agent/services/rag.py): retrieval helpers
- [src/agent/services/tools.py](src/agent/services/tools.py): search helper
- [src/agent/services/utils.py](src/agent/services/utils.py): cache helpers
- [src/agent/services/schemas.py](src/agent/services/schemas.py): pydantic models

## Safety

This project includes a manual confirmation step before publishing to social media. Ensure your access tokens and page IDs are stored securely.
