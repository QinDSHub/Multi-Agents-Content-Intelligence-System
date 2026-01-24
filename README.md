### Project Overview: Lightweight Automated Content Generation Tool ###

This tool was designed as an applied Generative AI tool that were used in our school project in 2nd semester. This study was conducted in response to Expleo’s proposed research topic and adopted a structured analytical approach to progressively define the research objectives and tool development goals. The analysis workflows covered industry trends over the past year, current market dynamics, and competitor positioning, from which actionable insights were derived.

This tool can automatically produce structured content ideas tailored to three specific core business objectives:
1.	Strengthening brand visibility
2.	Attracting and hiring top talent
3.	Reaching and engaging potential clients

Each market content idea was designed to be toileted for below prompt template includes: 
1. `content_format`  
2. `key_insights` (a list of concise bullet points)  
3. `business_objective` (branding / recruitment / client_acquisition)  
4. `target_audience`  
5. `distribution_strategy`  
6. `priority` (integer from 1 to {{ max_ideas }}, where 1 is the highest priority)  
7. `explanation` (1–2 sentences explaining strategic relevance)

Main libraries used: OpenAI, Langchain, Jinja2, Pydantic, prompt template, chain functions. It demonstrates a full LLM-powered market content strategy pipeline that you can run and experiment with.

### Future Directions ###
This MVP lays the foundation for LLM-powered content strategy generation, but there are several exciting avenues for further enhancement:
1.	Agent-Oriented Workflow Introduce multiple reasoning and action steps, allowing the system to autonomously plan, research, and iterate on content ideas rather than relying on a single LLM call.
2.	RAG (Retrieval-Augmented Generation) Integration Incorporate external knowledge sources (company data, market reports, competitor analysis) to make content suggestions more data-driven and contextually relevant.
3.	Interactive and Iterative Refinement Enable multi-turn interactions with the LLM, where feedback or evaluation from previous outputs can guide subsequent content planning steps.
4.	Modular Extensibility Further modularize components (prompt templates, LLM agents, output exporters) to support multiple output formats, advanced ranking strategies, and integration with other business tools.
These directions aim to evolve the project from a single-call MVP into a fully agent-based, intelligent content strategy assistant.
