import json
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.memory import ChatMessageHistory
from rag.simple_rag import SimpleRAG


class ContentAgent:

    def __init__(self, model: str = "gpt-4-turbo", temperature: float = 0.7, use_rag: bool = True):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.memory = ChatMessageHistory()
        self.rag = SimpleRAG() if use_rag else None
        
        if self.rag:
            self.rag.load_and_index()
    
    def generate_ideas(self, company_name: str, year: int, max_ideas: int = 5) -> list:

        rag_context = ""
        if self.rag and self.rag.vector_store:
            rag_context = self.rag.retrieve(f"{company_name} content marketing strategy")
            if rag_context:
                rag_context = f"\n\nRelevant Knowledge Base:\n{rag_context}"
        
        prompt_template = PromptTemplate(
            input_variables=["company_name", "year", "max_ideas", "rag_context"],
            template="""You are a marketing content strategist. Generate {max_ideas} strategic content ideas for {company_name} in {year}.

For each idea, provide JSON with: content_format, key_insights (list), business_objective, target_audience, distribution_strategy, priority, explanation.

Output ONLY valid JSON array, no markdown or extra text.{rag_context}

Return exactly {max_ideas} ideas ranked by priority (1=highest)."""
        )
        
        formatted_prompt = prompt_template.format(
            company_name=company_name,
            year=year,
            max_ideas=max_ideas,
            rag_context=rag_context
        )
        
        messages = ChatPromptTemplate.from_messages([
            ("system", "You are a marketing content strategist generating strategic content ideas. Always return valid JSON."),
            ("user", formatted_prompt)
        ])
        
        response = self.llm.invoke(messages.format_prompt().to_messages())
        
        self.memory.add_user_message(f"Generate ideas for {company_name} ({year})")
        self.memory.add_ai_message(response.content)
        
        try:
            ideas = json.loads(response.content)
            return ideas if isinstance(ideas, list) else [ideas]
        except:
            return []
    
    def refine_ideas(self, ideas: list, feedback: str) -> list:
        
        prompt = f"""You are refining content ideas based on feedback.

Original ideas (summary):
{json.dumps([{'format': i.get('content_format'), 'objective': i.get('business_objective')} for i in ideas], indent=2)}

Feedback: {feedback}

Refine and improve the ideas. Return valid JSON array with same structure."""
        
        messages = ChatPromptTemplate.from_messages([
            ("system", "You refine content ideas based on user feedback. Return only valid JSON."),
            ("user", prompt)
        ])
        
        response = self.llm.invoke(messages.format_prompt().to_messages())
        
        self.memory.add_user_message(feedback)
        self.memory.add_ai_message(response.content)
        
        try:
            refined = json.loads(response.content)
            return refined if isinstance(refined, list) else [refined]
        except:
            return ideas
    
    def get_memory(self) -> str:
        return "\n".join([f"{msg.type}: {msg.content}" for msg in self.memory.messages])
