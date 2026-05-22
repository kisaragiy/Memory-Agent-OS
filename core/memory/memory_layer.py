"""
Unified Memory Layer — Claude-grade single entry (Phase 3).

Layers: short-term conversation · long-term facts · semantic retrieval ·
episodic trace · procedural hints · project slots.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from core.memory.consolidator import consolidate_session
from core.memory.extractor import extract_memories
from core.memory.memory_policy import (
    CONSOLIDATE_AFTER_TURNS,
    MAX_EPISODES_PERSIST,
    bump_access,
    is_duplicate,
    normalize_content,
)
from core.memory.persistent_store import PersistentStore
from core.memory.schema_migrator import SchemaMigrator
from core.memory.summarizer import summarize_turns
from core.memory.types import ConversationTurn, Episode, MemoryKind, MemoryRecord
from core.memory.vector_store import VectorStore
from core.contracts.world import WorldState
from core.contracts.perception import ObservationState
from core.contracts.memory_mutation import MemoryMutationIntent


def _render_result(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, dict):
        inner = result.get("result")
        if isinstance(inner, dict):
            if inner.get("value") is not None:
                return str(inner["value"])
            if inner.get("stdout"):
                return str(inner["stdout"]).strip()
        if result.get("error"):
            return f"[error] {result['error']}"
    return str(result)[:2000]


class MemoryLayer:
    _instance: Optional["MemoryLayer"] = None

    def __init__(self):
        self._store = PersistentStore()
        self._vectors = VectorStore()
        self._records_cache: Dict[str, List[MemoryRecord]] = {}
        self._episodic: Dict[str, List[Episode]] = {}
        self._project: Dict[str, Dict[str, Any]] = {}
        self._conversation_cache: Dict[str, List[ConversationTurn]] = {}

    @classmethod
    def get(cls) -> "MemoryLayer":
        if cls._instance is None:
            cls._instance = MemoryLayer()
        return cls._instance

    def _load_records(self, agent_id: str) -> List[MemoryRecord]:
        if agent_id not in self._records_cache:
            self._records_cache[agent_id] = self._store.load_records(agent_id)
        return self._records_cache[agent_id]

    def _persist_records(self, agent_id: str) -> None:
        self._store.save_records(agent_id, self._load_records(agent_id))

    def ensure_agent_ready(self, agent_id: str) -> None:
        SchemaMigrator.migrate_agent(agent_id, self._store, self)
        if agent_id not in self._episodic:
            self._episodic[agent_id] = self._store.load_episodes(
                agent_id, limit=MAX_EPISODES_PERSIST
            )
        if agent_id not in self._project:
            self._project[agent_id] = self._store.load_project(agent_id)

    def get_narrative_schema(self, agent_id: str) -> Dict:
        self.ensure_agent_ready(agent_id)
        return self._store.load_narrative_schema(agent_id)

    def update_narrative_schema(self, agent_id: str, patch: Dict) -> Dict:
        schema = self.get_narrative_schema(agent_id)
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(schema.get(key), dict):
                schema[key] = {**schema[key], **value}
            else:
                schema[key] = value
        self._store.save_narrative_schema(agent_id, schema)
        return schema

    def apply_mutation(
        self,
        agent_id: str,
        intent: MemoryMutationIntent,
        *,
        trace_id: str = "",
    ) -> Dict:
        """
        Sole write surface for governed mutations (called only from execute_memory_op).
        """
        self.ensure_agent_ready(agent_id)
        self._records_cache.pop(agent_id, None)

        if intent.action == "snapshot":
            sid = intent.snapshot_id or trace_id or str(uuid.uuid4())
            return self._store.create_snapshot(agent_id, sid)

        if intent.action == "rollback":
            if not intent.snapshot_id:
                raise ValueError("rollback requires snapshot_id")
            self._store.restore_snapshot(agent_id, intent.snapshot_id)
            self._episodic[agent_id] = self._store.load_episodes(agent_id)
            self._project[agent_id] = self._store.load_project(agent_id)
            self._records_cache[agent_id] = self._store.load_records(agent_id)
            return {"rolled_back": intent.snapshot_id, "agent_id": agent_id}

        if intent.target == "episodic":
            raise ValueError("episodic target cannot be mutated except snapshot/rollback")

        if intent.target == "world_state":
            raise ValueError("world_state must go through World Engine")

        if intent.target == "procedural":
            kind = MemoryKind.PROCEDURAL
        else:
            kind = self._kind_from_string(intent.kind)

        if intent.action == "delete":
            records = self._load_records(agent_id)
            kept = [r for r in records if r.id != intent.record_id]
            if len(kept) == len(records):
                raise ValueError(f"record not found: {intent.record_id}")
            self._records_cache[agent_id] = kept
            self._persist_records(agent_id)
            return {"deleted": intent.record_id}

        if intent.action == "override":
            records = self._load_records(agent_id)
            for rec in records:
                if rec.id == intent.record_id or (
                    intent.fact and normalize_content(rec.content) == normalize_content(intent.fact)
                ):
                    rec.content = intent.fact or rec.content
                    rec.importance = max(rec.importance, 0.85)
                    bump_access(rec)
                    self._persist_records(agent_id)
                    self._vectors.upsert(agent_id, rec)
                    return {"id": rec.id, "content": rec.content, "action": "override"}
            raise ValueError("override target not found")

        if intent.action == "inject":
            rec = self.remember(
                agent_id,
                intent.fact,
                kind,
                0.7 if intent.inject_test else 0.85,
            )
            rec.metadata["injected"] = True
            rec.metadata["inject_test"] = intent.inject_test
            rec.metadata["mutation_trace_id"] = trace_id
            self._persist_records(agent_id)
            return {"id": rec.id, "content": rec.content, "action": "inject"}

        # merge (default)
        rec = self.remember(agent_id, intent.fact, kind, 0.9)
        rec.metadata["mutation_trace_id"] = trace_id
        return {"id": rec.id, "content": rec.content, "action": "merge"}

    @staticmethod
    def _kind_from_string(kind: str) -> MemoryKind:
        try:
            return MemoryKind(kind)
        except ValueError:
            return MemoryKind.FACT

    def remember(
        self,
        agent_id: str,
        content: str,
        kind: MemoryKind = MemoryKind.FACT,
        importance: float = 0.9,
    ) -> MemoryRecord:
        """Internal helper — external callers must use kernel execute_memory_op."""
        self.ensure_agent_ready(agent_id)
        records = self._load_records(agent_id)
        existing = is_duplicate(records, content, kind)
        if existing:
            existing.importance = max(existing.importance, importance)
            bump_access(existing)
            self._persist_records(agent_id)
            self._vectors.upsert(agent_id, existing)
            return existing

        record = MemoryRecord.create(agent_id, kind, content, importance)
        record.metadata["access_count"] = 0
        records.append(record)
        self._persist_records(agent_id)
        self._vectors.upsert(agent_id, record)
        return record

    def load_world_state(self, agent_id: str) -> WorldState:
        self.ensure_agent_ready(agent_id)
        raw = self._store.load_world_snapshot(agent_id)
        state = WorldState.from_dict({**raw, "agent_id": agent_id})
        schema = self._store.load_narrative_schema(agent_id)
        from core.world.world_runtime import WorldRuntime

        return WorldRuntime.hydrate_from_schema(state, schema)

    def save_world_state(self, agent_id: str, state: WorldState) -> None:
        self._store.save_world_snapshot(agent_id, state.to_dict())

    def build_context(
        self,
        agent_id: str,
        user_input: str,
        limit: int = 8,
        observation: Optional[ObservationState] = None,
    ) -> Dict:
        self.ensure_agent_ready(agent_id)
        records = self._load_records(agent_id)
        narrative_schema = self._store.load_narrative_schema(agent_id)
        conversation = self._store.load_conversation(agent_id, limit=30)
        self._conversation_cache[agent_id] = conversation

        vector_hits = self._vectors.query(agent_id, user_input, top_k=6)
        if not vector_hits:
            vector_hits = VectorStore.keyword_search(records, user_input, top_k=6)

        for rec, _score in vector_hits:
            for stored in records:
                if stored.id == rec.id:
                    bump_access(stored)
                    break
        if vector_hits:
            self._persist_records(agent_id)

        facts = [r for r in records if r.kind in (MemoryKind.FACT, MemoryKind.PREFERENCE)]
        project = dict(self._project.get(agent_id, {}))
        episodes = self._episodic.get(agent_id, [])[-limit:]

        summary = ""
        if len(conversation) > 16:
            summary = summarize_turns(conversation[:-6])

        ctx = {
            "agent_id": agent_id,
            "input": user_input,
            "conversation": [
                {"role": t.role, "content": t.content} for t in conversation[-12:]
            ],
            "conversation_summary": summary,
            "user_facts": [
                {
                    "content": r.content,
                    "kind": r.kind.value,
                    "access_count": r.metadata.get("access_count", 0),
                }
                for r in facts[-20:]
            ],
            "retrieved_memories": [
                {
                    "content": r.content,
                    "kind": r.kind.value,
                    "score": round(s, 3),
                    "access_count": r.metadata.get("access_count", 0),
                }
                for r, s in vector_hits
            ],
            "recent_episodes": [
                {
                    "trace_id": e.trace_id,
                    "user_input": e.user_input,
                    "assistant_output": e.assistant_output,
                    "status": e.status,
                }
                for e in episodes
            ],
            "project": project,
            "narrative_schema": narrative_schema,
            "observation": observation.to_dict() if observation else None,
            "procedural": self._procedural_hints(agent_id),
            "memory_prompt": "",
        }
        ctx["memory_prompt"] = self.format_prompt_block(ctx)
        return ctx

    def format_prompt_block(self, context: Dict) -> str:
        parts: List[str] = []
        facts = context.get("user_facts") or []
        if facts:
            lines = "\n".join(f"- [{f['kind']}] {f['content']}" for f in facts[-12:])
            parts.append(f"## 长期记忆（用户事实与偏好）\n{lines}")

        retrieved = context.get("retrieved_memories") or []
        if retrieved:
            lines = "\n".join(f"- {m['content']}" for m in retrieved[:8])
            parts.append(f"## 语义检索（相关历史）\n{lines}")

        summary = context.get("conversation_summary")
        if summary:
            parts.append(f"## 对话摘要\n{summary}")

        conv = context.get("conversation") or []
        if conv:
            lines = "\n".join(
                f"{m['role']}: {m['content'][:300]}" for m in conv[-8:]
            )
            parts.append(f"## 近期对话\n{lines}")

        project = context.get("project") or {}
        if project:
            lines = "\n".join(f"- {k}: {str(v)[:200]}" for k, v in project.items())
            parts.append(f"## 项目/世界观\n{lines}")

        schema = context.get("narrative_schema") or {}
        lt = schema.get("long_term") or schema
        if isinstance(lt, dict) and lt.get("session_summary"):
            parts.append(f"## 会话摘要（长期）\n{lt['session_summary'][:600]}")
        prefs = lt.get("user_preferences") if isinstance(lt, dict) else {}
        if prefs:
            tone = prefs.get("tone", "")
            style = prefs.get("writing_style", "")
            if tone or style:
                parts.append(
                    f"## 叙事偏好\n基调: {str(tone)[:80]}\n风格: {str(style)[:80]}"
                )

        world = context.get("world")
        if world:
            parts.append(f"## 世界状态\n{world.get('brief', '')}")

        obs = context.get("observation")
        if obs and obs.get("captured"):
            parts.append(
                f"## 屏幕观察（只读）\n{obs.get('raw_hint', '')[:400]}"
            )

        return "\n\n".join(parts)

    def _procedural_hints(self, agent_id: str) -> List[str]:
        episodes = self._episodic.get(agent_id, [])[-20:]
        errors = sum(1 for e in episodes if e.status != "success")
        hints = []
        if errors >= 3:
            hints.append("近期多次执行失败，优先澄清需求或拆分步骤。")
        return hints

    def ingest_user_message(self, agent_id: str, text: str) -> List[MemoryRecord]:
        created = []
        for kind, snippet, importance in extract_memories(text):
            created.append(self.remember(agent_id, snippet, kind, importance))
        return created

    def record_episode(
        self,
        agent_id: str,
        trace_id: str,
        user_input: str,
        plan: Dict,
        execution_results: List[Dict],
        reflection: Optional[Dict] = None,
        world_state: Optional[WorldState] = None,
    ) -> None:
        status = "success"
        final_result = None
        for r in execution_results:
            if r.get("status") != "success":
                status = "error"
            final_result = r

        assistant_output = _render_result(final_result)
        actions = plan.get("actions") or []
        summary = plan.get("task") or user_input[:200]
        if actions:
            names = [a.get("name", "?") for a in actions]
            summary = f"{summary} | tools={','.join(names)}"

        episode = Episode(
            trace_id=trace_id,
            user_input=user_input,
            plan_summary=summary,
            status=status,
            assistant_output=assistant_output,
            result=final_result,
            reflection=reflection,
        )
        epis = self._episodic.setdefault(agent_id, [])
        epis.append(episode)
        self._store.save_episodes(agent_id, epis, max_keep=MAX_EPISODES_PERSIST)

        self._store.append_conversation(
            agent_id, ConversationTurn("user", user_input, trace_id=trace_id)
        )
        if assistant_output:
            self._store.append_conversation(
                agent_id,
                ConversationTurn("assistant", assistant_output, trace_id=trace_id),
            )

        self.ingest_user_message(agent_id, user_input)

        if world_state is not None:
            self.save_world_state(agent_id, world_state)

        if status == "success" and assistant_output and len(assistant_output) > 30:
            qa = f"Q: {user_input[:200]}\nA: {assistant_output[:400]}"
            records = self._load_records(agent_id)
            if not is_duplicate(records, qa, MemoryKind.EPISODE):
                rec = MemoryRecord.create(
                    agent_id,
                    MemoryKind.EPISODE,
                    qa,
                    0.55,
                )
                rec.metadata["access_count"] = 0
                records.append(rec)
                self._persist_records(agent_id)
                self._vectors.upsert(agent_id, rec)

        self._maybe_consolidate(agent_id)

        if reflection:
            self.apply_reflection(agent_id, reflection)

    def apply_reflection(self, agent_id: str, reflection: Optional[Dict]) -> None:
        """Write observable reflection notes into procedural memory (no silent drop)."""
        if not reflection:
            return
        self.ensure_agent_ready(agent_id)
        sources = reflection.get("sources") or {}
        for key, src in sources.items():
            if src in ("fallback", "unknown", "stub"):
                self.remember(
                    agent_id,
                    f"[反思] {key} 使用 {src} 路径",
                    MemoryKind.PROCEDURAL,
                    0.55,
                )
        if reflection.get("failure_count", 0) > 0:
            self.remember(
                agent_id,
                f"[反思] 本轮 {reflection['failure_count']} 步执行失败，需澄清或拆分任务",
                MemoryKind.PROCEDURAL,
                0.65,
            )

    def _maybe_consolidate(self, agent_id: str) -> None:
        conversation = self._store.load_conversation(agent_id, limit=60)
        if len(conversation) < CONSOLIDATE_AFTER_TURNS:
            return
        meta = self._store.load_session_meta(agent_id)
        last_at = meta.get("last_consolidation_turn_count", 0)
        if len(conversation) - last_at < CONSOLIDATE_AFTER_TURNS:
            return
        schema = self._store.load_narrative_schema(agent_id)
        updated = consolidate_session(
            conversation, schema, min_turns=CONSOLIDATE_AFTER_TURNS
        )
        if updated:
            self._store.save_narrative_schema(agent_id, updated)
            meta["last_consolidation_turn_count"] = len(conversation)
            meta["source"] = "memory_consolidator"
            self._store.save_session_meta(agent_id, meta)

    def set_project(self, agent_id: str, key: str, value: Any) -> None:
        self.ensure_agent_ready(agent_id)
        self._project.setdefault(agent_id, {})[key] = value
        self._store.save_project(agent_id, self._project[agent_id])
        self.remember(agent_id, f"{key}: {value}", MemoryKind.PROJECT, 0.8)

    def get_episodes(self, agent_id: str) -> List[Episode]:
        return list(self._episodic.get(agent_id, []))

    def list_snapshots(self, agent_id: str) -> List[str]:
        self.ensure_agent_ready(agent_id)
        return self._store.list_snapshots(agent_id)

    def export_snapshot(self, agent_id: str) -> Dict:
        turns = self._store.load_conversation(agent_id, limit=50)
        episodes = self._episodic.get(agent_id, [])
        return {
            "facts": [
                {
                    "id": r.id,
                    "kind": r.kind.value,
                    "content": r.content,
                    "importance": r.importance,
                    "access_count": r.metadata.get("access_count", 0),
                    "created_at": r.created_at,
                }
                for r in self._load_records(agent_id)
            ],
            "world_state": self._store.load_world_snapshot(agent_id),
            "conversation": [
                {"role": t.role, "content": t.content, "created_at": t.created_at}
                for t in turns
            ],
            "episodes": [
                {
                    "id": ep.trace_id,
                    "summary": ep.plan_summary or ep.user_input,
                    "content": ep.assistant_output,
                    "status": ep.status,
                    "timestamp": ep.created_at,
                }
                for ep in episodes[-20:]
            ],
            "episode_count": len(episodes),
            "project": self._project.get(agent_id, {}),
            "narrative_schema": self.get_narrative_schema(agent_id),
        }
