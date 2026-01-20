#!/usr/bin/env python
# coding: utf-8

from jinja2 import Template
from pathlib import Path

# extract prompt
def render_prompt(template_path: Path, **kwargs) -> str:
    template_text = template_path.read_text(encoding="utf-8")
    return Template(template_text).render(**kwargs)    

