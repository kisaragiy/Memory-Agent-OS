"""Format ActionPlan for user / developer output (Renderer-style, no execution)."""

from __future__ import annotations

from core.contracts.action_plan import ActionPlan


class ActionPlanPresenter:
    @staticmethod
    def render_user(plan: ActionPlan) -> str:
        if not plan.intents:
            reason = plan._meta.get("fallback_reason", "")
            if reason == "no_observation":
                return "需要先观察屏幕内容才能制定操作计划。请使用 --observe 或设置 SCREEN_OBSERVATION_HINT。"
            return "未能从当前界面生成操作步骤，请补充更具体的描述或观察数据。"

        lines = ["已生成操作计划（尚未执行）："]
        for i, intent in enumerate(plan.intents, 1):
            lines.append(
                ActionPlanPresenter._format_intent_line(i, intent)
            )
        lines.append("")
        lines.append("确认后可通过「确认执行: …」或 `--confirm-actions` 经 Guard 执行（Phase 4C）。")
        return "\n".join(lines)

    @staticmethod
    def render_developer(plan: ActionPlan) -> dict:
        return {
            "summary": ActionPlanPresenter.render_user(plan),
            "action_plan": plan.to_dict(),
        }

    @staticmethod
    def render_awaiting_confirmation(plan: ActionPlan) -> str:
        base = ActionPlanPresenter.render_user(plan)
        return (
            base
            + "\n\n如需执行，请添加 `--confirm-actions` 或以「确认执行: …」发起。"
        )

    @staticmethod
    def render_guarded_result(result, *, dry_run: bool) -> str:
        lines = [
            "受控执行完成（" + ("模拟" if dry_run else "live-stub") + "）："
        ]
        for r in result.receipts:
            lines.append(f"- [{r.status}] {r.message}")
        if result.rollback_available:
            lines.append("\n回滚日志已记录（dry-run journal）。")
        return "\n".join(lines)

    @staticmethod
    def _format_intent_line(index: int, intent) -> str:
        label = intent.target_label or intent.target_element_id or "目标"
        type_map = {
            "click": "点击",
            "type_text": "输入",
            "navigate": "打开/导航",
            "focus": "聚焦",
            "scroll": "滚动",
        }
        verb = type_map.get(intent.action_type, intent.action_type)
        extra = ""
        if intent.action_type == "type_text" and intent.parameters.get("text"):
            extra = f" → 「{intent.parameters['text'][:40]}」"
        risk = f" [风险:{intent.risk_level}]" if intent.risk_level != "low" else ""
        return f"{index}. {verb}「{label}」{extra}{risk}"
