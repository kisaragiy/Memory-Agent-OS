"""
LLM transport — invoke models only. No policy, no mode, no prompt assembly.
All strategy lives in core.control.model_policy.ModelPolicy.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import List, Optional

import requests

from core.control.model_policy import LLMInvocationSpec

DEFAULT_TIMEOUT = 60


def strip_markdown_fences(text: str) -> str:
    text = (text or "").strip()
    if "```" not in text:
        return text
    parts = text.split("```")
    if len(parts) >= 2:
        inner = parts[1]
        if inner.startswith(("python", "text", "markdown")):
            inner = inner.split("\n", 1)[-1]
        return inner.strip()
    return text


def invoke_llm(spec: LLMInvocationSpec) -> str:
    """Single entry for text generation — spec from ModelPolicy only."""
    url = "http://localhost:11434/api/chat"
    messages = [
        {"role": "system", "content": spec.system},
        {"role": "user", "content": spec.user},
    ]
    payload = {
        "model": spec.model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": spec.max_tokens,
            "temperature": spec.temperature,
        },
    }
    response = requests.post(url, json=payload, timeout=spec.timeout)
    response.raise_for_status()
    message = response.json().get("message") or {}
    text = (message.get("content") or "").strip()
    if spec.strip_fences:
        text = strip_markdown_fences(text)
    return text


def call_llm(
    prompt: str,
    model: str = "qwen3-writer:latest",
    timeout: int = DEFAULT_TIMEOUT,
    *,
    strip_fences: bool = False,
) -> str:
    """Deprecated — use ModelPolicy + invoke_llm(LLMInvocationSpec)."""
    spec = LLMInvocationSpec(
        model=model,
        system="",
        user=prompt,
        max_tokens=2000,
        temperature=0.7,
        timeout=timeout,
        strip_fences=strip_fences,
    )
    return invoke_llm(spec)


def call_vision(spec: LLMInvocationSpec, image_path: str) -> str:
    """Vision via Ollama /api/chat — spec from ModelPolicy."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Screenshot not found: {image_path}")

    b64 = base64.b64encode(path.read_bytes()).decode()
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": spec.model,
        "messages": [
            {"role": "system", "content": spec.system},
            {
                "role": "user",
                "content": spec.user,
                "images": [b64],
            },
        ],
        "stream": False,
        "options": {
            "num_predict": spec.max_tokens,
            "temperature": spec.temperature,
        },
    }
    response = requests.post(url, json=payload, timeout=spec.timeout)
    response.raise_for_status()
    data = response.json()
    message = data.get("message") or {}
    return (message.get("content") or "").strip()


def extract_json_block(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("{"):
        return json.loads(text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object in vision response")
