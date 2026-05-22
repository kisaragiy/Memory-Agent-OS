"""
Phase 4D — Autonomy policy (confirmation resolution only, no dispatch).
"""

from __future__ import annotations

from typing import Dict, Tuple

from core.contracts.action_plan import ActionPlan


class AutonomyPolicy:
    @staticmethod
    def try_auto_confirm(
        action_plan: ActionPlan,
        *,
        autonomous_enabled: bool,
        user_confirmed: bool,
        confirm_flag: bool,
    ) -> Tuple[bool, Dict]:
        meta = {"source": "autonomy_policy", "phase": "4D", "observable": True}

        if user_confirmed or confirm_flag:
            meta["reason"] = "explicit_confirm"
            return True, meta

        if not autonomous_enabled:
            meta["reason"] = "autonomous_disabled"
            return False, meta

        if not action_plan.intents:
            meta["reason"] = "empty_plan"
            return False, meta

        high_risk = [i for i in action_plan.intents if i.risk_level == "high"]
        if high_risk:
            meta["reason"] = "high_risk_requires_manual_confirm"
            meta["high_risk_count"] = len(high_risk)
            return False, meta

        meta["reason"] = "auto_confirm_low_medium"
        meta["intent_count"] = len(action_plan.intents)
        return True, meta

    @staticmethod
    def requires_live_execution(autonomous_enabled: bool, dry_run: bool) -> bool:
        return autonomous_enabled and not dry_run
