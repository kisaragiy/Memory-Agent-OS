"""
Import legacy memory_store/memory_schema.json into unified MemoryLayer storage.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from core.memory.persistent_store import PersistentStore
from core.memory.types import MemoryKind

LEGACY_SCHEMA_PATH = Path("./memory_store/memory_schema.json")
MIGRATION_MARKER = ".legacy_schema_migrated"


def _truncate(text: str, max_len: int = 400) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


class SchemaMigrator:
    @staticmethod
    def legacy_exists() -> bool:
        return LEGACY_SCHEMA_PATH.is_file()

    @staticmethod
    def load_legacy() -> Dict:
        if not SchemaMigrator.legacy_exists():
            return {}
        try:
            with open(LEGACY_SCHEMA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, RecursionError, OSError):
            return {}

    @staticmethod
    def migrate_agent(agent_id: str, store: PersistentStore, memory_layer) -> bool:
        marker = store._agent_dir(agent_id) / MIGRATION_MARKER
        if marker.exists():
            return False

        legacy = SchemaMigrator.load_legacy()
        if not legacy:
            marker.write_text("empty", encoding="utf-8")
            return False

        # Mark before remember() — remember() → ensure_agent_ready() would re-enter migrate.
        marker.write_text("migrated", encoding="utf-8")

        store.save_narrative_schema(agent_id, legacy)
        lt = legacy.get("long_term") or {}

        for char in lt.get("characters") or []:
            name = (char.get("name") or "").strip()
            personality = _truncate(char.get("personality") or char.get("background") or "")
            if name:
                label = f"角色[{name}]: {personality}"
            elif personality:
                label = f"角色设定: {personality}"
            else:
                continue
            memory_layer.remember(agent_id, label, MemoryKind.PROJECT, 0.85)

        for setting in lt.get("world_settings") or []:
            key = setting.get("key", "世界观")
            value = _truncate(setting.get("value", ""))
            if value:
                memory_layer.set_project(agent_id, key, value)
                memory_layer.remember(
                    agent_id, f"{key}: {value}", MemoryKind.PROJECT, 0.9
                )

        prefs = lt.get("user_preferences") or {}
        if prefs.get("tone"):
            memory_layer.remember(
                agent_id, f"写作基调: {prefs['tone']}", MemoryKind.PREFERENCE, 0.88
            )
        if prefs.get("writing_style"):
            memory_layer.set_project(agent_id, "writing_style", prefs["writing_style"][:200])
        forbidden: List = prefs.get("forbidden") or []
        if forbidden:
            memory_layer.set_project(agent_id, "forbidden", forbidden)

        marker.write_text("ok", encoding="utf-8")
        return True
