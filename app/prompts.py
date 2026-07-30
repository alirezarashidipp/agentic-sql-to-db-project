from functools import cache

import yaml

from .config import PROMPTS_DIR


@cache
def load_prompt(name: str) -> str:
    document = yaml.safe_load(
        (PROMPTS_DIR / f"{name}.yml").read_text(encoding="utf-8")
    )
    template = document.get("template") if isinstance(document, dict) else None
    if not isinstance(template, str) or not template.strip():
        raise ValueError(f"Prompt {name!r} must contain a non-empty template.")
    return template.strip()


def render_prompt(name: str, **values: object) -> str:
    prompt = load_prompt(name)
    for key, value in values.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
    return prompt
