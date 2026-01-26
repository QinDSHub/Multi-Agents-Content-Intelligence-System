📂 Project Overview

This project presents an applied Generative Artificial Intelligence (GenAI) system developed using the LangChain framework, implemented as part of a second-semester laboratory course. The study was conducted in response to a research topic proposed by Expleo and follows a structured, analytical research methodology aimed at bridging theoretical GenAI techniques with practical business applications.

The research adopts a progressive analytical approach to define both the research objectives and the system development goals. The analytical workflows incorporate:

☑ Industry trend analysis over the preceding year

☑ Evaluation of current market dynamics

☑ Competitive landscape and positioning analysis

Based on these analyses, the system derives actionable, structured content strategies intended to support organizational decision-making in marketing, recruitment, and client engagement contexts.
________________________________________
📂 Definition of Core Business Objectives

The system is designed to automatically generate structured content ideas aligned with three predefined core business objectives, ensuring that all outputs remain strategically grounded:

☑ Enhancement of brand visibility

☑ Attraction and recruitment of high-quality talent

☑ Engagement and acquisition of potential clients

Each generated content idea is explicitly associated with one of these objectives to maintain interpretability and strategic relevance.

________________________________________
📂 Prompt Template Specification

To ensure consistency, reproducibility, and explainability, all content ideas are generated using a standardized prompt template schema. The template is designed to produce structured outputs suitable for downstream automation and analysis.

Each generated content idea includes the following fields:

☑ content_format

☑ key_insights (a concise list of bullet-pointed insights)

☑ business_objective (branding / recruitment / client_acquisition)

☑ target_audience

☑ distribution_strategy

☑ priority (an integer ranging from 1 to {{ max_ideas }}, where 1 indicates the highest priority)

☑ explanation (1–2 sentences justifying the strategic relevance of the content)

Primary APIs and frameworks employed:

LangChain, Agent-based architectures, Retrieval-Augmented Generation (RAG), conversational memory, OpenAI API, Jinja2 templating, Pydantic-based schema validation, prompt templates, and automated DOCX export utilities.

________________________________________
📂 System Architecture and Workflow

The system supports both a baseline and an advanced pipeline to facilitate comparative evaluation.

☑ User Input (company, year, number of ideas, execution mode) ---> Baseline OR LangChain-based pipeline

☑ Baseline (Legacy):
  Direct OpenAI API invocation → Structured output → Word document export

☑ LangChain Pipeline:
  Agent + PromptTemplate
      
      → [Optional RAG: document loading → FAISS vector indexing → contextual retrieval]
      
      → Prompt augmentation
      
      → LLM-based generation
      
      → ChatMessageHistory (conversational memory)
      
      → [Optional iterative refinement]
      
      → Structured output → Word document export
________________________________________
📂 Execution Modes

☑ --mode legacy

A lightweight baseline implementation using direct OpenAI API calls for rapid execution.

☑ --mode langchain

An agent-based LangChain pipeline incorporating prompt templates and conversational memory.

☑ --mode langchain + RAG

An enhanced LangChain pipeline augmented with FAISS-based document retrieval from the data/ directory.

________________________________________
📂 Key Features

☑ Integration of LangChain components, including ChatOpenAI, PromptTemplate, and conversational memory

☑ Optional Retrieval-Augmented Generation using a FAISS vector database

☑ Support for iterative refinement through conversational context retention

☑ Structured JSON output with automated Word document generation

☑ Multiple execution modes to support flexibility, extensibility, and performance trade-offs

________________________________________
📂 Future Work

Several extensions are proposed to enhance the system’s autonomy, scalability, and real-world applicability:

☑ Integration of additional external tools to enable autonomous agent tool invocation

☑ Introduction of multi-agent architectures, allowing each generated content idea to:

o	Automatically expand into complete textual marketing materials

o	Generate corresponding visual assets (e.g. image generation models)

o	Publish content to designated marketing platforms

o	Collect and evaluate marketing performance metrics and ROI

☑ Expansion of the RAG pipeline with:

o	Industry-specific domain corpora

o	Continuously updated market intelligence

o	Real-time or near-real-time news and trend data

📂 AI Assistance Disclosure

This project was developed with limited assistance from Claude (Haiku 4.5), which was used solely for language refinement and prompt iteration support. All system design, implementation, and final outputs were independently developed and validated by the author, who assumes full responsibility for the project’s academic integrity.

