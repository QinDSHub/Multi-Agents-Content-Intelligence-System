#!/usr/bin/env python
# coding: utf-8

import json
import yaml
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from models.content import ContentIdea
from exporters.word import export_to_word
from core.simple_agent import ContentAgent
load_dotenv()

def load_config():
    with open("prompts/system.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def parse_llm_output(response_text: str) -> list[ContentIdea]:
    try:
        raw = json.loads(response_text)
        return [ContentIdea(**item) for item in raw]
    except Exception as e:
        print(f"⚠ Parse error: {e}")
        return []


def build_output_path(company_name):
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    return out_dir / f"{company_name}_content_plan.docx"


def main_langchain_mode(company_name: str, year: int, max_ideas: int = 5, use_rag: bool = True):
    print(f"\nLangChain Mode (RAG: {'Enabled' if use_rag else 'Disabled'})")
    print(f"Generating ideas for {company_name} ({year})...")

    agent = ContentAgent(use_rag=use_rag)
    
    raw_ideas = agent.generate_ideas(company_name, year, max_ideas)
    
    if not raw_ideas:
        print("Failed to generate ideas")
        return
    
    content_list = []
    for idea in raw_ideas:
        try:
            content_list.append(ContentIdea(**idea))
        except:
            continue
    
    if not content_list:
        print("No valid ideas generated")
        return
    
    content_list = sorted(content_list, key=lambda x: x.priority)
    
    COLUMNS = ["content_format", "key_insights", "business_objective", "target_audience",
               "distribution_strategy", "priority", "explanation"]
    
    file_path = build_output_path(company_name)
    export_to_word(
        columns=COLUMNS,
        data=content_list,
        file_path=file_path,
        company_name=company_name
    )
    
    print(f"Content saved to {file_path}")
    print(f"Generated {len(content_list)} ideas")
    
    print(f"\nConversation Memory (first 300 chars):\n{agent.get_memory()[:300]}...")


def main_legacy_mode(company_name: str, year: int):
    print(f"\nLegacy Mode (Direct API)")
    
    from services.llm import call_chatgpt
    from services.renderer import render_prompt
    
    config = load_config()
    max_ideas = config['prompt']['max_ideas']
    model = config['llm']['model']
    temperature = config['llm']['temperature']
    max_tokens = config['llm']['max_tokens']
    
    prompt = render_prompt(
        Path("prompts/planner.md"),
        company_name=company_name,
        year=year,
        max_ideas=max_ideas
    )
    
    try:
        response = call_chatgpt(model, prompt, temperature, max_tokens)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    content_list = parse_llm_output(response)
    content_list = sorted(content_list, key=lambda x: x.priority)
    
    COLUMNS = ["content_format", "key_insights", "business_objective", "target_audience",
               "distribution_strategy", "priority", "explanation"]
    
    file_path = build_output_path(company_name)
    export_to_word(
        columns=COLUMNS,
        data=content_list,
        file_path=file_path,
        company_name=company_name
    )
    
    print(f"Content saved to {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Content Generation Tool")
    parser.add_argument("--company", type=str, required=True, help="Company name")
    parser.add_argument("--year", type=int, required=True, help="Year for planning")
    parser.add_argument("--ideas", type=int, default=5, help="Number of ideas (default: 5)")
    parser.add_argument("--mode", type=str, choices=["langchain", "legacy"], default="langchain",
                       help="Execution mode (default: langchain)")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG in LangChain mode")
    
    args = parser.parse_args()
    
    if args.mode == "langchain":
        main_langchain_mode(args.company, args.year, args.ideas, use_rag=not args.no_rag)
    else:
        main_legacy_mode(args.company, args.year)