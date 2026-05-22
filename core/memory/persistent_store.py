from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.memory.types import ConversationTurn, Episode, MemoryKind, MemoryRecord


class PersistentStore:
    def __init__(self, base_dir: str = "./memory_db/agents"):
        self.base_dir = Path(base_dir)

    def _agent_dir(self, agent_id: str) -> Path:
        path = self.base_dir / agent_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_records(self, agent_id: str) -> List[MemoryRecord]:
        raw = self._read_json(self._agent_dir(agent_id) / "records.json", [])
        records = []
        for item in raw:
            records.append(
                MemoryRecord(
                    id=item["id"],
                    agent_id=item["agent_id"],
                    kind=MemoryKind(item["kind"]),
                    content=item["content"],
                    importance=float(item.get("importance", 0.5)),
                    metadata=item.get("metadata", {}),
                    created_at=item.get("created_at", ""),
                )
            )
        return records

    def save_records(self, agent_id: str, records: List[MemoryRecord]) -> None:
        payload = [
            {
                "id": r.id,
                "agent_id": r.agent_id,
                "kind": r.kind.value,
                "content": r.content,
                "importance": r.importance,
                "metadata": r.metadata,
                "created_at": r.created_at,
            }
            for r in records
        ]
        self._write_json(self._agent_dir(agent_id) / "records.json", payload)

    def append_conversation(self, agent_id: str, turn: ConversationTurn) -> None:
        path = self._agent_dir(agent_id) / "conversation.jsonl"
        line = json.dumps(
            {
                "role": turn.role,
                "content": turn.content,
                "trace_id": turn.trace_id,
                "created_at": turn.created_at,
            },
            ensure_ascii=False,
        )
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def load_conversation(self, agent_id: str, limit: int = 40) -> List[ConversationTurn]:
        path = self._agent_dir(agent_id) / "conversation.jsonl"
        if not path.exists():
            return []
        turns: List[ConversationTurn] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                turns.append(
                    ConversationTurn(
                        role=item["role"],
                        content=item["content"],
                        trace_id=item.get("trace_id"),
                        created_at=item.get("created_at", ""),
                    )
                )
        return turns[-limit:]

    def load_world_snapshot(self, agent_id: str) -> Dict:
        return self._read_json(self._agent_dir(agent_id) / "world.json", {})

    def save_world_snapshot(self, agent_id: str, data: Dict) -> None:
        self._write_json(self._agent_dir(agent_id) / "world.json", data)

    def load_narrative_schema(self, agent_id: str) -> Dict:
        return self._read_json(self._agent_dir(agent_id) / "narrative_schema.json", {})

    def save_narrative_schema(self, agent_id: str, data: Dict) -> None:
        self._write_json(self._agent_dir(agent_id) / "narrative_schema.json", data)

    def load_episodes(self, agent_id: str, limit: int = 200) -> List[Episode]:
        raw = self._read_json(self._agent_dir(agent_id) / "episodes.json", [])
        episodes: List[Episode] = []
        for item in raw[-limit:]:
            episodes.append(
                Episode(
                    trace_id=item.get("trace_id", ""),
                    user_input=item.get("user_input", ""),
                    plan_summary=item.get("plan_summary", ""),
                    status=item.get("status", "unknown"),
                    assistant_output=item.get("assistant_output", ""),
                    result=None,
                    reflection=item.get("reflection"),
                    created_at=item.get("created_at", ""),
                )
            )
        return episodes

    def save_episodes(self, agent_id: str, episodes: List[Episode], max_keep: int = 200) -> None:
        payload = [
            {
                "trace_id": e.trace_id,
                "user_input": e.user_input,
                "plan_summary": e.plan_summary,
                "status": e.status,
                "assistant_output": e.assistant_output,
                "reflection": e.reflection,
                "created_at": e.created_at,
            }
            for e in episodes[-max_keep:]
        ]
        self._write_json(self._agent_dir(agent_id) / "episodes.json", payload)

    def load_project(self, agent_id: str) -> Dict[str, Any]:
        return self._read_json(self._agent_dir(agent_id) / "project.json", {})

    def save_project(self, agent_id: str, data: Dict[str, Any]) -> None:
        self._write_json(self._agent_dir(agent_id) / "project.json", data)

    def load_session_meta(self, agent_id: str) -> Dict[str, Any]:
        return self._read_json(self._agent_dir(agent_id) / "session_meta.json", {})

    def save_session_meta(self, agent_id: str, data: Dict[str, Any]) -> None:
        self._write_json(self._agent_dir(agent_id) / "session_meta.json", data)

    def _snapshots_dir(self, agent_id: str) -> Path:
        d = self._agent_dir(agent_id) / "snapshots"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def create_snapshot(self, agent_id: str, snapshot_id: str) -> Dict[str, Any]:
        """Point-in-time bundle for rollback (kernel-triggered only)."""
        bundle = {
            "snapshot_id": snapshot_id,
            "records": self._read_json(self._agent_dir(agent_id) / "records.json", []),
            "project": self.load_project(agent_id),
            "episodes": self._read_json(self._agent_dir(agent_id) / "episodes.json", []),
            "narrative_schema": self.load_narrative_schema(agent_id),
            "world": self.load_world_snapshot(agent_id),
            "session_meta": self.load_session_meta(agent_id),
        }
        self._write_json(self._snapshots_dir(agent_id) / f"{snapshot_id}.json", bundle)
        return {"snapshot_id": snapshot_id, "agent_id": agent_id}

    def restore_snapshot(self, agent_id: str, snapshot_id: str) -> None:
        path = self._snapshots_dir(agent_id) / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
        bundle = self._read_json(path, {})
        self._write_json(self._agent_dir(agent_id) / "records.json", bundle.get("records", []))
        self.save_project(agent_id, bundle.get("project", {}))
        self._write_json(self._agent_dir(agent_id) / "episodes.json", bundle.get("episodes", []))
        self.save_narrative_schema(agent_id, bundle.get("narrative_schema", {}))
        self.save_world_snapshot(agent_id, bundle.get("world", {}))
        self.save_session_meta(agent_id, bundle.get("session_meta", {}))

    def list_snapshots(self, agent_id: str) -> List[str]:
        d = self._snapshots_dir(agent_id)
        return sorted(p.stem for p in d.glob("*.json"))
