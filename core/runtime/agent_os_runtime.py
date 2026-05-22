from core.tools.tool_registry import (
    GLOBAL_TOOL_REGISTRY,
    bootstrap,
)
from core.kernel.tool_router import ToolRouter
from core.runtime.execution_engine import ExecutionEngine
from core.schema.schema_gate import SchemaGate
from core.runtime.input_normalizer import InputNormalizer
from core.control.runtime_control import RuntimeControl
from core.control.intent_router import IntentRouter
from core.control.output_policy import OutputPolicy
from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.control.alignment_spec import AlignmentFlags
from core.control.memory_control import MemoryControl, MemoryGovernanceError
from core.contracts.memory_mutation import MemoryMutationTrace
from core.contracts.intent import ExecutionChannel
from core.runtime import observability
from core.memory import get_memory_layer
from core.orchestration import KernelOrchestrator, ReflectionLoop
from core.orchestration.autonomous_loop import AutonomousOSLoop
from core.contracts.autonomous import AutonomousSessionResult
from core.world.world_runtime import WorldRuntime
from core.world.scaffold import build_scaffold
from core.perception import (
    PerceptionGate,
    ActionPlanGate,
    ScreenObserver,
    UIParser,
    ActionPlanBuilder,
    ActionPlanPresenter,
)
from core.guard import ActionGuard, ExecutionSandbox, GuardedDispatch, AutonomyPolicy
from core.contracts.guard import GuardedExecutionResult, ExecutionReceipt
import os
import uuid


def _render_result_text(final: dict) -> str:
    inner = final.get("result") if isinstance(final, dict) else None
    if isinstance(inner, dict):
        if inner.get("value") is not None:
            return str(inner["value"])
        if inner.get("stdout"):
            return str(inner["stdout"]).strip()
    return str(final)[:500]


class AgentOSRuntime:
    """
    Single entry — execution authority ONLY in ExecutionEngine.

    Phase 4A: observation-only.
    Phase 4B: action plan (no confirm).
    Phase 4C: guarded execution via guarded_ui_action tool only.
    Phase 4D: autonomous + vision + live OS driver (still single ExecutionEngine).
    """

    def __init__(
        self,
        agent_id="local-agent",
        output_mode="user",
        control=None,
        observe_screen: bool = False,
        plan_actions: bool = False,
        confirm_actions: bool = False,
        dry_run: bool = True,
        autonomous: bool = False,
    ):
        self.agent_id = agent_id
        self.control = control or RuntimeControl(mode=output_mode)
        self.output_mode = self.control.mode
        self.observe_screen = observe_screen
        self.plan_actions = plan_actions
        self.confirm_actions = confirm_actions
        self.dry_run = dry_run
        self.autonomous = autonomous

        self.schema_gate = SchemaGate()
        self.input_normalizer = InputNormalizer()
        self.memory = get_memory_layer()
        self.orchestrator = KernelOrchestrator()
        self.reflection = ReflectionLoop()

        if not getattr(GLOBAL_TOOL_REGISTRY, "_bootstrapped", False):
            bootstrap(quiet=(self.control.mode == RuntimeControl.USER))
            GLOBAL_TOOL_REGISTRY._bootstrapped = True

        self.tool_registry = GLOBAL_TOOL_REGISTRY
        self.tool_router = ToolRouter(self.tool_registry)
        self.execution_engine = ExecutionEngine(tool_router=self.tool_router)
        self.execution_engine.set_runtime_context("AgentOSRuntime")

        from core.tools.code_tool import CodeTool
        from core.tools.narrative_tool import NarrativeTool

        if "execute_code" not in self.tool_registry.list():
            self.tool_registry.register("execute_code", CodeTool(self.execution_engine))
        if "narrative_respond" not in self.tool_registry.list():
            self.tool_registry.register("narrative_respond", NarrativeTool())
        if "guarded_ui_action" not in self.tool_registry.list():
            from core.tools.guarded_ui_action_tool import GuardedUiActionTool

            self.tool_registry.register("guarded_ui_action", GuardedUiActionTool())
        if "execute_memory_op" not in self.tool_registry.list():
            from core.tools.memory_op_tool import MemoryOpTool

            self.tool_registry.register("execute_memory_op", MemoryOpTool())

    def dispatch_memory_mutation(
        self,
        raw_intent: dict,
        *,
        trace_id: str | None = None,
    ) -> dict:
        """
        Governed memory write — Control → plan → ExecutionEngine → MemoryLayer.
        """
        trace_id = trace_id or str(uuid.uuid4())
        intent = MemoryControl.authorize(self.control, raw_intent)
        plan = MemoryControl.build_kernel_plan(intent, self.agent_id, trace_id)

        flags = self._alignment_flags()
        if flags.show_trace:
            observability._hub.append_trace(
                trace_id, "memory_mutation_authorized", intent.to_dict()
            )

        syscalls = self.orchestrator.plan_to_syscalls(plan, trace_id)
        if not syscalls:
            raise ValueError("No memory mutation syscall generated")

        syscall = syscalls[0]
        syscall["payload"]["trace_id"] = trace_id
        validated = self.schema_gate.validate(syscall)
        step_result = self.execution_engine.execute(validated)

        status = step_result.get("status", "error")
        trace = MemoryMutationTrace(
            trace_id=trace_id,
            intent=intent.to_dict(),
            status=status,
            result=step_result.get("result"),
            error=step_result.get("error"),
        )
        MemoryControl.append_mutation_trace(self.agent_id, trace)

        if flags.show_trace:
            observability._hub.append_trace(
                trace_id, "memory_mutation_complete", trace.to_dict()
            )

        payload = {
            "trace_id": trace_id,
            "status": status,
            "result": step_result.get("result"),
            "error": step_result.get("error"),
            "mutation": intent.to_dict(),
            "_meta": {"source": "memory_governance", "observable": True},
        }
        return OutputFilter.filter_output(payload, flags)

    def start(self):
        if self.control.mode != RuntimeControl.USER:
            print(
                f"[AgentOSRuntime] started "
                f"(agent_id={self.agent_id}, control={self.control.to_dict()})"
            )

    def normalize_input(self, raw_input):
        if isinstance(raw_input, dict):
            text = raw_input.get("input") or raw_input.get("text") or ""
            return self.input_normalizer.normalize(str(text))
        return self.input_normalizer.normalize(raw_input)

    def set_mode(self, mode: str):
        self.control = RuntimeControl(mode=mode)
        self.output_mode = self.control.mode

    def _alignment_flags(self) -> AlignmentFlags:
        flags = ModelPolicy.resolve_flags(self.control.mode)
        if os.environ.get("AGENT_WINDOWS_DESKTOP", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ):
            return flags.merge(enable_vision=True)
        return flags

    def _run_perception(self, text: str):
        if not PerceptionGate.should_observe(
            text,
            force=self.observe_screen or self.plan_actions or self.autonomous,
        ):
            return None

        flags = self._alignment_flags()
        from core.platform.windows_desktop import WindowsDesktop

        use_vision = flags.enable_vision and (
            self.autonomous
            or os.environ.get("USE_VISION_OBSERVER", "").strip() in ("1", "true", "yes")
            or WindowsDesktop.desktop_mode_enabled()
            or WindowsDesktop.capture_enabled()
        )
        if use_vision:
            from core.perception.vision_observer import VisionObserver

            obs = VisionObserver().observe(hint=text[:500])
            if obs.captured and obs.elements:
                return obs
            if obs._meta.get("fallback_reason"):
                parsed = UIParser().parse(obs)
                if parsed.elements:
                    return parsed

        obs = ScreenObserver().observe(hint=text[:500])
        return UIParser().parse(obs)

    def _build_enriched_context(self, text: str):
        observation = self._run_perception(text)
        context = self.memory.build_context(
            self.agent_id, text, observation=observation
        )
        context["agent_id"] = self.agent_id
        context["control_mode"] = self.control.mode
        context["alignment_flags"] = self._alignment_flags().to_dict()

        action_plan = None
        if ActionPlanGate.should_plan(text, force=self.plan_actions):
            action_plan = ActionPlanBuilder.build(text, observation)
            context["action_plan"] = action_plan.to_dict()

        world_state = self.memory.load_world_state(self.agent_id)
        world_state, world_frame, narrative = WorldRuntime.step(
            world_state, text, context
        )
        context["world"] = world_frame
        if world_frame.get("brief"):
            context["memory_prompt"] = (
                context.get("memory_prompt", "")
                + "\n\n## 叙事世界\n"
                + world_frame["brief"]
            ).strip()
        return context, world_state, narrative, action_plan, observation

    def _attach_render_bundles(self, syscalls, context, world_state, narrative):
        world_frame = context.get("world") or {}
        for syscall in syscalls:
            if syscall.get("type") != "narrative_respond":
                continue
            payload = syscall.setdefault("payload", {})
            prompt = payload.get("prompt") or context.get("input", "")
            scaffold = build_scaffold(
                world_state, narrative, world_frame, prompt
            )
            plan_meta = context.get("plan_meta") or {}
            payload["render_bundle"] = {
                "prompt": prompt,
                "scaffold": scaffold,
                "memory_prompt": context.get("memory_prompt", ""),
                "narrative_schema": context.get("narrative_schema") or {},
                "world_view": world_frame,
                "control_mode": context.get("control_mode", "user"),
                "alignment_flags": context.get("alignment_flags"),
                "model_mode": plan_meta.get("model_mode")
                or context.get("model_mode"),
                "intent": plan_meta.get("intent")
                or (context.get("intent_classification") or {}).get(
                    "route", {}
                ).get("intent"),
            }
        return syscalls

    def _handle_awaiting_confirmation(
        self,
        trace_id,
        text,
        action_plan,
        context,
        world_state,
        perception_meta,
    ):
        summary = ActionPlanPresenter.render_awaiting_confirmation(action_plan)
        return self._handle_plan_only(
            trace_id,
            text,
            action_plan,
            context,
            world_state,
            perception_meta,
            plan_summary_override=summary,
            plan_meta_source="4C_awaiting_confirmation",
        )

    def _handle_plan_only(
        self,
        trace_id,
        text,
        action_plan,
        context,
        world_state,
        perception_meta,
        plan_summary_override=None,
        plan_meta_source="4B_plan_only",
    ):
        summary = plan_summary_override or ActionPlanPresenter.render_user(action_plan)
        plan = {
            "task": text,
            "task_type": "os_action_plan",
            "intent": "plan_only",
            "strategy": plan_meta_source,
            "actions": [],
            "_meta": {
                "source": plan_meta_source,
                "execution": "blocked",
                "action_plan_source": action_plan._meta.get("source"),
                "observable": True,
            },
        }
        execution_results = [
            {
                "trace_id": trace_id,
                "status": "success",
                "result": {
                    "value": summary,
                    "stdout": summary,
                    "_plan_only": True,
                },
                "error": None,
            }
        ]

        world_state = WorldRuntime.apply_turn(world_state, text, summary)
        reflection_note = self.reflection.reflect(
            text,
            plan,
            execution_results,
            action_plan_meta=action_plan._meta,
            perception_meta=perception_meta,
        )
        self.memory.record_episode(
            self.agent_id,
            trace_id,
            text,
            plan,
            execution_results,
            reflection=reflection_note,
            world_state=world_state,
        )

        flags = self._alignment_flags()
        if self.control.mode in (RuntimeControl.DEVELOPER, RuntimeControl.DEBUG):
            dev = ActionPlanPresenter.render_developer(action_plan)
            payload = {
                "result": summary,
                "trace_id": trace_id,
                "plan": plan,
                "action_plan": dev["action_plan"],
                "reflection": reflection_note,
                "observation": context.get("observation"),
                "steps": execution_results,
            }
            return OutputFilter.filter_output(payload, flags)
        return summary

    def _handle_guarded_execution(
        self,
        trace_id,
        text,
        action_plan,
        decision,
        context,
        world_state,
        perception_meta,
        autonomy_meta=None,
    ):
        ExecutionSandbox.reset_journal()
        action_plan = ActionGuard.mark_intents_executable(action_plan, decision)
        kernel_plan = GuardedDispatch.to_kernel_plan(
            action_plan,
            decision,
            dry_run=self.dry_run,
            agent_id=self.agent_id,
        )
        flags = AlignmentFlags.from_dict(context.get("alignment_flags")) or self._alignment_flags()
        if not flags.enable_autonomy and self.autonomous:
            return (
                "自主执行未启用。"
                if self.control.is_user_mode()
                else OutputFilter.filter_output(
                    {"status": "error", "message": "autonomy_disabled_by_alignment"},
                    flags,
                )
            )

        syscalls = GuardedDispatch.plan_to_syscalls(kernel_plan, trace_id)
        execution_results = []

        for syscall in syscalls:
            validated = self.schema_gate.validate(syscall)
            step_result = self.execution_engine.execute(validated)
            step_result = OutputFilter.filter_execution_step(step_result, flags)
            execution_results.append(step_result)
            if flags.show_trace:
                observability._hub.append_trace(
                    syscall["trace_id"], "guarded_execution_step", step_result
                )
            if step_result.get("status") != "success":
                break

        receipts = []
        for step in execution_results:
            inner = step.get("result") or {}
            rec = inner.get("receipt")
            if rec:
                receipts.append(
                    ExecutionReceipt(
                        intent_id=rec.get("intent_id", ""),
                        action_type=rec.get("action_type", ""),
                        status=rec.get("status", ""),
                        dry_run=bool(rec.get("dry_run")),
                        message=rec.get("message", ""),
                        rollback_id=rec.get("rollback_id", ""),
                        _meta=rec.get("_meta") or {},
                    )
                )

        phase = "4D" if self.autonomous and not self.dry_run else "4C"
        guarded_result = GuardedExecutionResult(
            receipts=receipts,
            rollback_available=bool(ExecutionSandbox.get_journal()),
            _meta={
                "source": f"{phase}_guarded_execution",
                "dry_run": self.dry_run,
                "live": ExecutionSandbox.is_live_enabled() and not self.dry_run,
                "guard_token": decision.guard_token[:8] + "…",
                "observable": True,
            },
        )
        summary = ActionPlanPresenter.render_guarded_result(
            guarded_result, dry_run=self.dry_run
        )

        reflection_note = self.reflection.reflect(
            text,
            kernel_plan,
            execution_results,
            perception_meta=perception_meta,
            action_plan_meta=action_plan._meta,
            guard_meta=guarded_result._meta,
            autonomy_meta=autonomy_meta if autonomy_meta else None,
        )

        world_state = WorldRuntime.apply_turn(world_state, text, summary)
        self.memory.record_episode(
            self.agent_id,
            trace_id,
            text,
            kernel_plan,
            execution_results,
            reflection=reflection_note,
            world_state=world_state,
        )

        if self.control.mode in (RuntimeControl.DEVELOPER, RuntimeControl.DEBUG):
            payload = {
                "result": summary,
                "trace_id": trace_id,
                "plan": kernel_plan,
                "action_plan": action_plan.to_dict(),
                "guard_decision": decision.to_dict(),
                "guarded_execution": guarded_result.to_dict(),
                "sandbox_journal": ExecutionSandbox.get_journal(),
                "reflection": reflection_note,
                "observation": context.get("observation"),
                "steps": execution_results,
            }
            return OutputFilter.filter_output(payload, flags)
        return summary

    def entry(self, user_input, *, user_confirmed: bool = False):
        """ONLY SYSTEM ENTRY POINT."""
        trace_id = str(uuid.uuid4())
        execution_results = []
        plan = {}
        context = {}
        world_state = None
        perception_meta = None
        action_plan = None

        try:
            normalized = self.normalize_input(user_input)
            text = normalized["raw"]

            context, world_state, narrative, action_plan, observation = (
                self._build_enriched_context(text)
            )
            obs = context.get("observation")
            if obs:
                perception_meta = obs.get("_meta")

            flags = self._alignment_flags()
            context["alignment_flags"] = flags.to_dict()

            classification = IntentRouter.classify(text, context)
            context["intent_classification"] = classification.to_dict()
            route = classification.route

            if flags.show_trace:
                observability._hub.append_trace(
                    trace_id,
                    "intent_classified",
                    classification.to_dict(),
                )

            if route.channel == ExecutionChannel.MEMORY:
                if not flags.enable_memory_write:
                    msg = "记忆写入功能当前不可用。"
                    return msg if self.control.is_user_mode() else {"status": "error", "message": msg}
                fact = classification.normalized_task
                mut = None
                if fact:
                    mut = self.dispatch_memory_mutation(
                        MemoryControl.remember_intent(fact),
                        trace_id=trace_id,
                    )
                    if mut.get("status") != "success":
                        if self.control.is_user_mode():
                            return "未能保存记忆，请稍后重试。"
                        return mut
                msg = f"已记住：{fact}" if fact else "已记录。"
                if self.control.mode in (RuntimeControl.DEVELOPER, RuntimeControl.DEBUG):
                    payload = {
                        "result": msg,
                        "trace_id": trace_id,
                        "intent": classification.to_dict(),
                        "mutation": mut,
                    }
                    return OutputFilter.filter_output(payload, flags)

                return msg

            confirmed = self.confirm_actions or user_confirmed
            autonomy_meta = {}

            if action_plan and self.autonomous and flags.enable_autonomy:
                action_plan._meta["autonomous"] = True
                auto_ok, autonomy_meta = AutonomyPolicy.try_auto_confirm(
                    action_plan,
                    autonomous_enabled=True,
                    user_confirmed=user_confirmed,
                    confirm_flag=self.confirm_actions,
                )
                if auto_ok:
                    confirmed = True

            if action_plan and ActionPlanGate.should_use_guard_flow(text, action_plan):
                if self.control.show_trace():
                    observability._hub.append_trace(
                        trace_id,
                        "action_plan_built",
                        {"action_plan": action_plan.to_dict()},
                    )

                if not action_plan.intents:
                    return self._handle_plan_only(
                        trace_id, text, action_plan, context, world_state, perception_meta
                    )

                if ActionPlanGate.should_show_plan_only(
                    action_plan,
                    confirmed=confirmed,
                    plan_only_flag=self.plan_actions,
                    autonomous=self.autonomous,
                ):
                    return self._handle_awaiting_confirmation(
                        trace_id, text, action_plan, context, world_state, perception_meta
                    )

                decision = ActionGuard.evaluate(
                    action_plan,
                    confirmed=confirmed,
                    agent_id=self.agent_id,
                    autonomous=self.autonomous,
                    autonomy_meta=autonomy_meta,
                )

                if not decision.approved:
                    reason = "; ".join(decision.blocked_reasons) or "guard_rejected"
                    if self.control.mode == RuntimeControl.USER:
                        return f"操作未通过安全校验：{reason}"
                    return {
                        "status": "error",
                        "guard_decision": decision.to_dict(),
                        "message": reason,
                        "_meta": {"source": "4C_guard_rejected", "observable": True},
                    }

                return self._handle_guarded_execution(
                    trace_id,
                    text,
                    action_plan,
                    decision,
                    context,
                    world_state,
                    perception_meta,
                    autonomy_meta,
                )

            plan = self.orchestrator.build_plan(context, classification)
            context["plan_meta"] = plan.get("_meta") or {}
            context["model_mode"] = context["plan_meta"].get("model_mode")
            flags = AlignmentFlags.from_dict(context["plan_meta"].get("alignment_flags")) or flags

            if plan.get("_meta", {}).get("routing") == "blocked" and not plan.get("actions"):
                blocked = "当前模式不允许该操作。"
                return blocked if self.control.is_user_mode() else OutputFilter.filter_output(
                    {"status": "error", "message": blocked, "plan": plan}, flags
                )

            if flags.show_trace:
                observability._hub.append_trace(
                    trace_id,
                    "plan_built",
                    {
                        "plan": plan,
                        "world": context.get("world"),
                        "_meta": plan.get("_meta"),
                        "action_plan": context.get("action_plan"),
                        "intent": classification.to_dict(),
                    },
                )

            syscalls = self.orchestrator.plan_to_syscalls(plan, trace_id, route)
            if not syscalls:
                raise ValueError("No executable actions in plan")

            syscalls = self._attach_render_bundles(
                syscalls, context, world_state, narrative
            )

            for syscall in syscalls:
                validated = self.schema_gate.validate(syscall)
                step_result = self.execution_engine.execute(validated)
                step_result = OutputPolicy.sanitize_execution_step(
                    self.control, step_result
                )
                step_result = OutputFilter.filter_execution_step(step_result, flags)
                execution_results.append(step_result)

                if flags.show_trace:
                    observability._hub.append_trace(
                        syscall["trace_id"], "execution_step", step_result
                    )

                if step_result.get("status") != "success":
                    break

            final = execution_results[-1]
            output_text = _render_result_text(final)
            world_state = WorldRuntime.apply_turn(world_state, text, output_text)

            reflection_note = self.reflection.reflect(
                text,
                plan,
                execution_results,
                planner_fallback=plan.get("_meta", {}).get("source") == "fallback",
                perception_meta=perception_meta,
                action_plan_meta=(
                    action_plan._meta if action_plan else None
                ),
            )

            self.memory.record_episode(
                self.agent_id,
                trace_id,
                text,
                plan,
                execution_results,
                reflection=reflection_note,
                world_state=world_state,
            )

            if final.get("status") != "success":
                return self.control.format_execution_error(final)

            if self.control.mode in (RuntimeControl.DEVELOPER, RuntimeControl.DEBUG):
                out = {
                    "result": observability.render(RuntimeControl.USER, final, flags),
                    "trace_id": trace_id,
                    "plan": plan,
                    "reflection": reflection_note,
                    "memory": self.memory.export_snapshot(self.agent_id),
                    "world": context.get("world"),
                    "observation": context.get("observation"),
                    "steps": execution_results,
                }
                if action_plan:
                    out["action_plan"] = action_plan.to_dict()
                return OutputFilter.filter_output(out, flags)

            return observability.render(self.control.mode, final, flags)

        except Exception as e:
            if self.control.show_traceback():
                import traceback

                traceback.print_exc()
            err = self.control.format_error(e)
            err_flags = self._alignment_flags()
            if err_flags.show_trace:
                observability._hub.append_trace(
                    trace_id,
                    "execution_error",
                    {"error": str(e), "plan": plan},
                )
            if isinstance(err, dict):
                return OutputFilter.filter_output(err, err_flags)
            return err

    def run_autonomous_session(
        self,
        goal: str,
        *,
        max_steps: int = AutonomousOSLoop.DEFAULT_MAX_STEPS,
        user_confirmed: bool = True,
    ) -> AutonomousSessionResult:
        """
        Phase 5 — multi-step observe/plan/act/reflect via repeated entry() only.
        """
        saved = (
            self.observe_screen,
            self.plan_actions,
            self.autonomous,
            self.confirm_actions,
            self.dry_run,
        )
        try:
            self.observe_screen = True
            self.plan_actions = True
            self.autonomous = True
            self.confirm_actions = True
            flags = self._alignment_flags()
            if not flags.enable_autonomy:
                self.confirm_actions = user_confirmed
            loop = AutonomousOSLoop(max_steps=max_steps)
            return loop.run(self, goal, user_confirmed=self.confirm_actions)
        finally:
            (
                self.observe_screen,
                self.plan_actions,
                self.autonomous,
                self.confirm_actions,
                self.dry_run,
            ) = saved

    def iter_autonomous_session(
        self,
        goal: str,
        *,
        max_steps: int = AutonomousOSLoop.DEFAULT_MAX_STEPS,
        user_confirmed: bool = True,
    ):
        """Streaming variant for /api/autonomous/stream."""
        saved = (
            self.observe_screen,
            self.plan_actions,
            self.autonomous,
            self.confirm_actions,
            self.dry_run,
        )
        try:
            self.observe_screen = True
            self.plan_actions = True
            self.autonomous = True
            self.confirm_actions = True
            loop = AutonomousOSLoop(max_steps=max_steps)
            yield from loop.iter_steps(self, goal, user_confirmed=self.confirm_actions)
        finally:
            (
                self.observe_screen,
                self.plan_actions,
                self.autonomous,
                self.confirm_actions,
                self.dry_run,
            ) = saved

    def remember(self, fact: str):
        """Governed merge — routes through kernel execute_memory_op."""
        out = self.dispatch_memory_mutation(MemoryControl.remember_intent(fact))
        if out.get("status") != "success":
            raise MemoryGovernanceError(out.get("error") or "memory mutation failed")
        inner = out.get("result") or {}
        from core.memory.types import MemoryRecord, MemoryKind

        return MemoryRecord(
            id=inner.get("id", ""),
            agent_id=self.agent_id,
            kind=MemoryKind.FACT,
            content=inner.get("content", fact),
            importance=0.9,
        )

    def __getattr__(self, name):
        if name == "execution_engine":
            raise AttributeError("Direct access to execution_engine is not allowed")
        raise AttributeError(name)
