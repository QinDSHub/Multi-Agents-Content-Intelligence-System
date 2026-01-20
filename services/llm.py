#!/usr/bin/env python
# coding: utf-8

from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def call_chatgpt(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": "You are a senior marketing strategist."},
            {"role": "user", "content": prompt}
        ],
        temperature = temperature,
        max_tokens = max_tokens,
    )
    return response.choices[0].message.content
