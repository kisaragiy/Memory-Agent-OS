"""
Phase 5 — Autonomous Agent OS loop (single kernel path).

observe → plan → act → reflect → (retry) until goal satisfied or max_steps.
All execution via AgentOSRuntime.entry() — no second engine.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Generator, List, Optional

from core.contracts.autonomous import AutonomousSessionResult, AutonomousStepRecord
from core.control.presentation_policy import PresentationPolicy
from core.perception.gate import ActionPlanGate, PerceptionGate


class AutonomousOSLoop:
    DEFAULT_MAX_STEPS = 6

    def __init__(self, max_steps: int = DEFAULT_MAX_STEPS):
        self.max_steps = max(1, min(max_steps, 12))

    def run(self, runtime, goal: str, *, user_confirmed: bool = True) -> AutonomousSessionResult:
        steps: List[AutonomousStepRecord] = []
        final_output: Any = None
        status = "incomplete"

        for event in self.iter_steps(runtime, goal, user_confirmed=user_confirmed):
            if event.get("type") == "step":
                steps.append(event["record"])
            elif event.get("type") == "complete":
                final_output = event.get("final_output")
                status = event.get("status", "success")
            elif event.get("type") == "error":
                status = "error"
                steps.append(event["record"])
                final_output = event.get("error")
                break

        return AutonomousSessionResult(
            session_id=runtime.agent_id,
            goal=goal,
            status=status,
            steps=steps,
            final_output=final_output,
            _meta={
                "phase": "5",
                "max_steps": self.max_steps,
                "source": "autonomous_os_loop",
                "observable": True,
            },
        )

    def iter_steps(
        self,
        runtime,
        goal: str,
        *,
        user_confirmed: bool = True,
    ) -> Generator[Dict[str, Any], None, None]:
        """Yield progress events for streaming API."""
        original_goal = (goal or "").strip()
        if not original_goal:
            yield {
                "type": "error",
                "error": "empty_goal",
                "record": AutonomousStepRecord(
                    0, "validate", "error", "目标为空", _meta={"observable": True}
                ).to_dict(),
            }
            return

        prompt = original_goal
        last_output: Any = None

        for idx in range(self.max_steps):
            trace_id = str(uuid.uuid4())
            yield {
                "type": "progress",
                "step_index": idx,
                "phase": "observe",
                "message": "正在观察屏幕…",
                "trace_id": trace_id,
            }

            try:
                result = runtime.entry(prompt, user_confirmed=user_confirmed)
                last_output = result
                summary = PresentationPolicy.extract_display_text(result)
                success = not (
                    isinstance(result, dict)
                    and result.get("status") == "error"
                )

                record = AutonomousStepRecord(
                    step_index=idx,
                    phase="act",
                    status="success" if success else "error",
                    summary=summary[:500] or ("完成" if success else "失败"),
                    trace_id=trace_id,
                    intent_trace=self._intent_trace_from_result(result, runtime),
                    _meta={"observable": True, "prompt": prompt[:200]},
                )
                yield {"type": "step", "record": record}

                if success and self._should_stop(result, original_goal, idx):
                    yield {
                        "type": "complete",
                        "status": "success",
                        "final_output": result,
                        "step_index": idx,
                    }
                    return

                if not success:
                    prompt = f"上一步失败，请重试完成：{original_goal}"
                    continue

                if idx + 1 < self.max_steps and self._needs_continuation(
                    result, original_goal
                ):
                    prompt = f"继续完成目标（第{idx + 2}步）：{original_goal}"
                    yield {
                        "type": "progress",
                        "step_index": idx + 1,
                        "phase": "plan",
                        "message": "继续下一步…",
                    }
                    continue

                yield {
                    "type": "complete",
                    "status": "success",
                    "final_output": result,
                    "step_index": idx,
                }
                return

            except Exception as exc:
                record = AutonomousStepRecord(
                    step_index=idx,
                    phase="error",
                    status="error",
                    summary=str(exc)[:300],
                    trace_id=trace_id,
                    _meta={"observable": True},
                )
                yield {"type": "error", "error": str(exc), "record": record}
                return

        yield {
            "type": "complete",
            "status": "max_steps",
            "final_output": last_output,
            "step_index": self.max_steps - 1,
        }

    @staticmethod
    def _intent_trace_from_result(result: Any, runtime) -> Dict[str, Any]:
        trace: Dict[str, Any] = {
            "mode": runtime.control.mode,
            "phase": "5",
        }
        if isinstance(result, dict):
            if result.get("intent"):
                trace["intent"] = result["intent"]
            meta = result.get("_meta") or result.get("plan_meta") or {}
            if isinstance(meta, dict):
                trace["routing"] = meta.get("routing")
                trace["policy"] = meta.get("model_mode")
        return trace

    @staticmethod
    def _should_stop(result: Any, goal: str, step_index: int) -> bool:
        if isinstance(result, str) and result.strip():
            if not ActionPlanGate.should_plan(goal) and step_index == 0:
                return True
        if isinstance(result, dict):
            guarded = result.get("guarded_execution")
            if guarded and step_index >= 0:
                receipts = (guarded.get("receipts") if isinstance(guarded, dict) else None) or []
                if receipts and all(
                    r.get("status") in ("success", "simulated") for r in receipts
                ):
                    return True
        return False

    @staticmethod
    def _needs_continuation(result: Any, goal: str) -> bool:
        if not PerceptionGate.should_observe(goal) and not ActionPlanGate.should_plan(goal):
            return False
        if isinstance(result, dict) and result.get("action_plan"):
            return True
        if isinstance(result, dict) and result.get("status") == "awaiting_confirmation":
            return True
        return ActionPlanGate.should_plan(goal)
