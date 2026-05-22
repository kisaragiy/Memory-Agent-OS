"""
Local Ollama model registry (user environment).
"""

from __future__ import annotations

# Role → model name (must exist in `ollama list`)
MODELS = {
    "planner": "qwen3:1.7b",
    "coder": "qwen2.5-coder:14b",
    "writer": "qwen3-writer:latest",
    "reasoning": "deepseek-r1:14b",
    "vision": "llama3.2-vision:latest",
    "vision_alt": "qwen2.5vl:7b",
    "embed": "nomic-embed-text:latest",
    "general": "qwen3:14b",
}

TIMEOUTS = {
    "planner": 30,
    "coder": 120,
    "writer": 120,
    "vision": 90,
    "reasoning": 90,
}
