#!/usr/bin/env python
# coding: utf-8

import json, re, yaml
import argparse
import os,gc,sys
from docx import Document
from jinja2 import Template
from pathlib import Path
from openai import OpenAI
from models.content import ContentIdea
from services.llm import call_chatgpt
from services.renderer import render_prompt
from exporters.word import export_to_word

def load_config():
    with open("prompts/system.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_llm_output(response_text: str) -> list[ContentIdea]:
    raw = json.loads(response_text)
    return [ContentIdea(**item) for item in raw]


def build_output_path(company_name):
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    return out_dir / f"{company_name}_content_plan.docx"


def main(company_name, year):
    config = load_config()
    
    max_ideas = config['prompt']['max_ideas']
    
    model = config['llm']['model']
    temperature = config['llm']['temperature']
    max_tokens = config['llm']['max_tokens']

    prompt = render_prompt(
        Path("prompts/planner.md"),
        company_name = company_name,
        year = year,
        max_ideas = max_ideas
    )

    try:
        response = call_chatgpt(model, prompt, temperature, max_tokens)
    except Exception as e:
        print(f"❌ Error calling ChatGPT: {e}")
        sys.exit(1)

    
    content_list = parse_llm_output(response)
    content_list = sorted(content_list, key=lambda x: x.priority)


    COLUMNS = ["content_format", "key_insights", "target_objective", "target_audience",
                        "distribution_strategy", "priority", "explanation"]

    export_to_word(
        columns = COLUMNS,
        data = content_list,
        file_path = build_output_path(company_name),
        company_name = company_name
    )
    print(f"✅ Content Saved at {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", type=str, required=True)
    parser.add_argument("--year", type=int, required=True)

    args = parser.parse_args()
    
    main(company_name=args.company, year=args.year)