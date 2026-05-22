"""
Reflection loop — plan → act → observe → reflect.
All fallbacks must be observable (_meta, notes, sources).
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.contracts.memory import ReflectionRecord


class ReflectionLoop:
    def reflect(
        self,
        user_input: str,
        plan: Dict,
        execution_results: List[Dict],
        *,
        planner_fallback: bool = False,
        perception_meta: Dict | None = None,
        action_plan_meta: Dict | None = None,
        guard_meta: Dict | None = None,
        autonomy_meta: Dict | None = None,
    ) -> Dict[str, Any]:
        failures = [r for r in execution_results if r.get("status") != "success"]
        notes: List[str] = []
        sources: Dict[str, str] = {}

        plan_meta = plan.get("_meta") or {}
        sources["plan"] = plan_meta.get("source", "unknown")
        if plan_meta.get("fallback_reason"):
            notes.append(f"Plan fallback: {plan_meta['fallback_reason']}")

        if planner_fallback:
            notes.append("Planner used deterministic fallback (LLM unavailable or invalid plan).")
            sources["planner"] = "fallback"

        renderer_meta = {}
        if execution_results:
            inner = (execution_results[-1].get("result") or {})
            if isinstance(inner, dict):
                renderer_meta = inner.get("_renderer_meta") or {}
        if renderer_meta:
            sources["renderer"] = renderer_meta.get("source", "unknown")
            if renderer_meta.get("source") == "renderer_fallback":
                notes.append(
                    f"Renderer LLM fallback: {renderer_meta.get('fallback_reason', 'unknown')}"
                )

        if perception_meta:
            sources["perception"] = perception_meta.get("source", "none")
            if perception_meta.get("source") == "stub":
                notes.append("Perception: Phase 4A stub (observation-only, no screen capture).")

        if action_plan_meta:
            sources["action_plan"] = action_plan_meta.get("source", "unknown")
            if action_plan_meta.get("fallback_reason"):
                notes.append(
                    f"Action plan fallback: {action_plan_meta['fallback_reason']}"
                )
            if action_plan_meta.get("phase") == "4B":
                notes.append("Phase 4B: action intents planned, execution not dispatched.")

        if guard_meta:
            sources["guard"] = guard_meta.get("source", "action_guard")
            if guard_meta.get("dry_run"):
                notes.append("Phase 4C: guarded dry-run execution via ExecutionEngine.")
            elif guard_meta.get("live"):
                notes.append("Phase 4D: live guarded execution via ExecutionEngine + OsDriver.")
            if guard_meta.get("fallback_reason"):
                notes.append(f"Guard: {guard_meta['fallback_reason']}")

        if autonomy_meta:
            sources["autonomy"] = autonomy_meta.get("reason", "unknown")
            if autonomy_meta.get("reason") == "auto_confirm_low_medium":
                notes.append("Phase 4D: low/medium risk auto-confirmed.")
            if autonomy_meta.get("reason") == "high_risk_requires_manual_confirm":
                notes.append("High-risk actions require manual confirm.")

        if failures:
            notes.append(f"{len(failures)} execution step(s) failed.")
            for f in failures:
                err = f.get("error")
                if err:
                    notes.append(str(err))
        elif not notes:
            notes.append("All execution steps completed successfully.")

        should_retry = bool(failures) and plan_meta.get("retryable", False)

        record = ReflectionRecord(
            should_retry=should_retry,
            notes=notes,
            failure_count=len(failures),
            step_count=len(execution_results),
            sources=sources,
        )
        return record.to_dict()
