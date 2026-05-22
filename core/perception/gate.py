"""Phase 4A/4B — perception and action-plan gates (no execution)."""

from __future__ import annotations

OBSERVE_KEYWORDS = (
    "屏幕", "界面", "窗口", "按钮", "UI", "截图", "screen",
    "desktop", "浏览器", "看一下屏幕", "当前页面",
)

ACTION_PLAN_KEYWORDS = (
    "点击", "输入", "填写", "打开", "关闭", "拖动", "滚动",
    "自动化", "操作", "鼠标", "键盘", "click", "type", "automate",
)


class PerceptionGate:
    @staticmethod
    def should_observe(text: str, *, force: bool = False) -> bool:
        if force:
            return True
        t = (text or "").lower()
        if ActionPlanGate.should_plan(text):
            return True
        return any(k.lower() in t for k in OBSERVE_KEYWORDS)


class ActionPlanGate:
    """Phase 4B/4C — action intent planning gate."""

    @staticmethod
    def should_plan(text: str, *, force: bool = False) -> bool:
        if force:
            return True
        t = (text or "").lower()
        return any(k.lower() in t for k in ACTION_PLAN_KEYWORDS)

    @staticmethod
    def should_use_guard_flow(text: str, action_plan) -> bool:
        return action_plan is not None and ActionPlanGate.should_plan(text)

    @staticmethod
    def should_show_plan_only(
        action_plan,
        *,
        confirmed: bool,
        plan_only_flag: bool,
        autonomous: bool = False,
    ) -> bool:
        if not action_plan:
            return False
        if confirmed:
            return False
        if autonomous:
            return plan_only_flag
        if plan_only_flag:
            return True
        return True
