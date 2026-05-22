import argparse
import os
from core.runtime.agent_os_runtime import AgentOSRuntime
from core.control.runtime_control import RuntimeControl


def _parse_remember(text: str):
    t = text.strip()
    for prefix in ("remember:", "记住:", "记住："):
        if t.lower().startswith(prefix.lower()):
            rest = t[len(prefix) :].strip()
            return rest if rest else None
    return None


def _parse_confirm_execute(text: str):
    t = text.strip()
    for prefix in ("确认执行:", "确认执行：", "confirm:", "confirm execute:"):
        if t.lower().startswith(prefix.lower()):
            body = t.split(":", 1)[-1].split("：", 1)[-1].strip()
            return True, body
    return False, text


def main():
    parser = argparse.ArgumentParser(description="Agent OS CLI")
    parser.add_argument(
        "--mode",
        choices=list(RuntimeControl.VALID_MODES),
        default=RuntimeControl.USER,
    )
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--observe", action="store_true", help="Phase 4A observation")
    parser.add_argument("--plan-actions", action="store_true", help="Phase 4B plan only")
    parser.add_argument("--confirm-actions", action="store_true", help="Phase 4C confirm")
    parser.add_argument(
        "--live",
        action="store_true",
        help="GUARDED_UI_LIVE=1 — real OS driver (4D, needs pyautogui + display)",
    )
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Phase 4D/5: auto-confirm + vision + autonomous loop",
    )
    parser.add_argument(
        "--autonomous-session",
        action="store_true",
        help="Phase 5: multi-step autonomous OS loop for each CLI input",
    )
    parser.add_argument(
        "--autonomous-steps",
        type=int,
        default=6,
        help="Max steps for Phase 5 loop",
    )
    parser.add_argument(
        "--vision",
        action="store_true",
        help="USE_VISION_OBSERVER=1 — Ollama vision for screen parse",
    )
    args = parser.parse_args()

    if args.live:
        os.environ["GUARDED_UI_LIVE"] = "1"
    if args.vision or args.autonomous or args.observe:
        os.environ["USE_VISION_OBSERVER"] = "1"
        os.environ["AUTONOMOUS_CAPTURE"] = "1"
        os.environ["AGENT_WINDOWS_DESKTOP"] = "1"
    if args.autonomous and args.live:
        os.environ.setdefault("AUTONOMOUS_CAPTURE", "1")

    control = RuntimeControl(
        mode=args.mode,
        trace_enabled=args.trace or args.mode != RuntimeControl.USER,
    )
    runtime = AgentOSRuntime(
        agent_id="local-agent",
        control=control,
        observe_screen=args.observe or args.autonomous,
        plan_actions=args.plan_actions,
        confirm_actions=args.confirm_actions,
        dry_run=not args.live,
        autonomous=args.autonomous,
    )

    runtime.start()

    if control.mode == RuntimeControl.USER:
        print("Agent OS 已就绪。")
        print("记住: … | 确认执行: … | --autonomous --live | exit\n")
    else:
        print(f"4D autonomous={args.autonomous} live={args.live} dry_run={not args.live}")

    while True:
        try:
            user_input = input(">>> ")
            if user_input.strip() in ("exit", "quit"):
                break

            fact = _parse_remember(user_input)
            if fact:
                print(f"已记住：{runtime.remember(fact).content}")
                continue

            confirmed, body = _parse_confirm_execute(user_input)
            if args.autonomous_session:
                out = runtime.run_autonomous_session(
                    body,
                    max_steps=args.autonomous_steps,
                    user_confirmed=confirmed or True,
                )
                print(out.to_dict())
            else:
                result = runtime.entry(body, user_confirmed=confirmed)
                print(result)

        except KeyboardInterrupt:
            print("\n[shutdown]")
            break
        except Exception as e:
            if control.show_traceback():
                import traceback

                traceback.print_exc()
            print(control.format_error(e))


if __name__ == "__main__":
    main()
