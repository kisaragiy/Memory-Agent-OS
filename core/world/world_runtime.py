"""
World Runtime — pure state only (Phase 3/4).

ALLOWED: update state, generate context, compute transitions, emit constraints.
FORBIDDEN: I/O, tools, network, shell, memory writes.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from core.contracts.narrative import NarrativeState
from core.contracts.world import CharacterState, WorldState
from core.world.character_graph import CharacterGraph
from core.world.emotion_engine import EmotionEngine
from core.world.narrative_engine import NarrativeEngine
from core.world.world_state_machine import WorldStateMachine

NARRATIVE_KEYWORDS = (
    "小说", "剧本", "角色", "剧情", "漫剧", "故事", "世界观",
    "对话", "续写", "场景", "章节", "人设", "叙事",
    "恐怖", "写一段", "写一篇", "短篇", "大纲",
)


class WorldRuntime:
    @staticmethod
    def is_narrative_task(text: str, context: Optional[Dict] = None) -> bool:
        if any(k in (text or "") for k in NARRATIVE_KEYWORDS):
            return True
        if context and context.get("project"):
            return True
        return False

    @staticmethod
    def hydrate_from_schema(state: WorldState, narrative_schema: Dict) -> WorldState:
        lt = narrative_schema.get("long_term") or narrative_schema
        if not isinstance(lt, dict):
            return state
        for char in lt.get("characters") or []:
            name = (char.get("name") or "").strip()
            if not name:
                continue
            traits = []
            if char.get("personality"):
                traits.append(str(char["personality"])[:60])
            state.characters[name] = CharacterState(
                name=name,
                role=char.get("role", "character"),
                traits=traits,
            )
        for setting in lt.get("world_settings") or []:
            key = setting.get("key", "")
            if key and not state.scene:
                state.scene = str(key)[:40]
        return state

    @staticmethod
    def _sync_graph(state: WorldState) -> Tuple[CharacterGraph, EmotionEngine, WorldStateMachine, NarrativeEngine]:
        graph = CharacterGraph()
        for name, c in state.characters.items():
            graph.upsert(name, c.role, c.traits)
            for other, rel in c.relationships.items():
                graph.relate(name, other, rel)
        emotions = EmotionEngine()
        emotions.states = {k: dict(v) for k, v in state.emotions.items()}
        machine = WorldStateMachine()
        machine.state = state.story_state
        machine.scene = state.scene
        machine.timeline = list(state.timeline)
        return graph, emotions, machine, NarrativeEngine()

    @staticmethod
    def _state_from_components(
        agent_id: str,
        graph: CharacterGraph,
        emotions: EmotionEngine,
        machine: WorldStateMachine,
    ) -> WorldState:
        characters = {}
        for name, node in graph.nodes.items():
            characters[name] = CharacterState(
                name=name,
                role=node.role,
                traits=list(node.traits),
                relationships=dict(node.relationships),
            )
        return WorldState(
            agent_id=agent_id,
            story_state=machine.state,
            scene=machine.scene,
            timeline=list(machine.timeline),
            characters=characters,
            emotions={k: dict(v) for k, v in emotions.states.items()},
        )

    @staticmethod
    def step(
        state: WorldState,
        user_input: str,
        memory_context: Dict,
    ) -> Tuple[WorldState, Dict[str, Any], NarrativeState]:
        graph, emotions, machine, narrative_engine = WorldRuntime._sync_graph(state)

        graph.extract_from_text(user_input)
        chars = list(graph.nodes.keys())
        emotions.infer_from_text(user_input, chars)
        emotions.decay()

        narrative = NarrativeState.from_dict(
            narrative_engine.generate(
                {"timeline": machine.timeline, "scene": machine.scene},
                user_input,
            )
        )
        machine.transition(narrative.to_dict())

        new_state = WorldRuntime._state_from_components(
            state.agent_id, graph, emotions, machine
        )

        brief = narrative_engine.render_passage(
            narrative.to_dict(),
            graph.to_dict(),
            emotions.to_dict(),
        )

        frame = {
            "active": WorldRuntime.is_narrative_task(user_input, memory_context),
            "story_state": new_state.story_state,
            "characters": {k: v.to_dict() for k, v in new_state.characters.items()},
            "emotions": new_state.emotions,
            "narrative": narrative.to_dict(),
            "brief": brief,
            "constraints": [
                "保持角色关系一致",
                "遵守 narrative_schema 中的基调与禁忌",
            ],
        }
        return new_state, frame, narrative

    @staticmethod
    def apply_turn(
        state: WorldState,
        user_input: str,
        system_output: str,
    ) -> WorldState:
        state = WorldState.from_dict(state.to_dict())
        state.timeline.append(f"user: {user_input[:120]}")
        if system_output:
            state.timeline.append(f"system: {system_output[:120]}")
        state.timeline = state.timeline[-30:]
        return state

    @staticmethod
    def emit_constraints(state: WorldState, narrative: NarrativeState) -> Dict[str, Any]:
        return {
            "story_state": state.story_state,
            "scene": state.scene,
            "tension": narrative.tension,
            "constraints": [
                f"剧情阶段: {state.story_state}",
                f"张力: {narrative.tension:.2f}",
            ],
        }
