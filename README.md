
# Multi-Agent Marketing Content Intelligence System

This project implements a multi-agent content intelligence pipeline built with LangChain and LangGraph, designed to generate high-quality, publish-ready industry content while minimizing hallucinations, controlling GenAI costs, and improving operational efficiency.

The system evolves from an earlier version and adopts a sequential, agent-based architecture, where each agent is responsible for a well-defined stage of the content lifecycle.

---

## System Architecture & Agent Pipeline

The pipeline is composed of the following agents, executed in series:

- **Search Agent**  
  Retrieves professional and industry-grade reports to ground downstream generation and reduce hallucinations.  
  Supported retrieval methods:
  - Custom web crawler  
  - Tavily Search  
  - User-provided professional reports

- **Map Agent**  
  Identifies and extracts the most relevant sections of retrieved documents based on the user query.

- **Reduce Agent**  
  Synthesizes and summarizes key insights from the mapped content.

- **Rank Agent**  
  Scores and prioritizes summarized insights based on importance and relevance.  
  This step is designed to:
  - Control GenAI token usage
  - Optimize downstream API and publishing costs
  - Select only high-value content for generation

- **Marketing Agent**  
  Generates post-ready marketing or insight content based on ranked outputs.  
  > Note: The current version supports text-based content only. Short-form AI video generation would require multimodal LLM integration.

- **Human-in-the-Loop (HITL)**  
  Allows manual review, validation, or revision of generated content before publication.  
  Approved or edited content automatically proceeds to the next stage.

- **Distributor Agent**  
  Publishes approved content according to configurable schedules, platforms, and timing.  
  - Currently supports Facebook API
  - Additional platforms can be integrated modularly

---

## Design Principles & Key Features

The system incorporates several engineering mechanisms to ensure robustness, accuracy, and efficiency:

- **Pydantic schemas** for structured data validation
- **Retrieval-Augmented Generation (RAG)** to ground LLM outputs
- **Short-term memory** for contextual continuity
- **Caching mechanisms** to reduce redundant computation and cost
- **Fallback strategies** for tool and API failures
- **Citation enforcement** to improve transparency and reliability and decrease hallucinations
- **Human-in-the-loop control** for quality assurance and safety

Together, these design choices help:
- Reduce hallucinations
- Improve response precision
- Control operational costs
- Increase system reliability and throughput

---

## Main Tech Stack & Libraries

- Python 3.12.7  
- chromadb 1.4.1  
- langchain 1.2.8  
- langchain-openai 1.1.7  
- langgraph 1.0.7  
- openai 2.17.0  

---

## GenAI Assistance Disclosure

This multi-agent automation system was designed and implemented by the author using LangChain and LangGraph. GPT-5.2-Codex was used exclusively for code optimization, language refinement, and prompt iteration support.

All system architecture, implementation decisions, and final outputs were independently developed and validated by the author, who assumes full responsibility for the project’s integrity and correctness.
