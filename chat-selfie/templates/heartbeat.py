from __future__ import annotations

import argparse
import json

from delivery_common import (
    DIAGNOSTIC_VERSION,
    DEFAULT_CONFIG_PATH,
    build_heartbeat_caption,
    build_stage_result,
    load_config,
    normalize_reason,
    resolve_delivery_config,
    resolve_heartbeat_config,
    resolve_mood_via_workspace_tool,
    resolve_self_repair_config,
    resolve_workspace_path,
    run_python_json,
    validate_runtime_workspace,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Heartbeat entry for scheduled Chat Selfie pushes.",
    )
    parser.add_argument("--agent", required=True, help="Target agent id.")
    parser.add_argument("--mood", default=None, help="Optional explicit mood id.")
    parser.add_argument("--text", default=None, help="Optional explicit heartbeat caption.")
    parser.add_argument("--chat-id", default=None, help="Optional explicit push target override for Telegram route.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(DEFAULT_CONFIG_PATH)
    heartbeat_cfg = resolve_heartbeat_config(config)
    if not bool(heartbeat_cfg.get("enabled", False)):
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "final_state": "blocked",
                    "stage": build_stage_result(
                        "blocked",
                        attempted=False,
                        error_code="HEARTBEAT_DISABLED",
                        message="Heartbeat delivery is disabled in this workspace.",
                        recoverability="degrade",
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    preflight = validate_runtime_workspace(
        config_path=DEFAULT_CONFIG_PATH,
        config=config,
        reason="heartbeat",
    )
    if not preflight["preflight"]["heartbeat_ready"]:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "final_state": "repair_required",
                    "stage": build_stage_result(
                        "failed",
                        attempted=True,
                        error_code="HEARTBEAT_ROUTE_NOT_READY",
                        message="Heartbeat is enabled but the configured delivery route is not ready.",
                        recoverability="repair_setup",
                    ),
                    "preflight": preflight["preflight"],
                    "user_action_required": preflight["user_action_required"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    mood_data = None
    mood_stage = build_stage_result("skipped", attempted=False)
    if bool(heartbeat_cfg.get("use_mood", True)) or args.mood:
        mood_data = resolve_mood_via_workspace_tool(
            config_path=DEFAULT_CONFIG_PATH,
            config=config,
            agent=args.agent,
            mood_id=args.mood,
            reason="heartbeat",
        )
        mood_stage = mood_data.get("stage") or build_stage_result("success", attempted=True)
        if mood_data.get("status") == "blocked" or mood_data.get("blocked") or mood_data.get("rate_limited"):
            print(json.dumps(mood_data, ensure_ascii=False, indent=2))
            return
        if not mood_data.get("ok", True) and resolve_self_repair_config(config).get("allow_text_only_degrade", True):
            mood_data = None

    final_text = (args.text or "").strip()
    if not final_text:
        final_text = build_heartbeat_caption(
            config_path=DEFAULT_CONFIG_PATH,
            config=config,
            agent=args.agent,
            mood_data=mood_data,
        )

    send_tool_path = resolve_workspace_path(
        DEFAULT_CONFIG_PATH.parent,
        config.get("workspace", {}).get("send_tool_path"),
        "./send.py",
    )
    send_args = [
        "--agent",
        args.agent,
        "--reason",
        normalize_reason("heartbeat"),
        "--text",
        final_text,
    ]
    if args.mood:
        send_args.extend(["--mood", args.mood])
    if mood_data is not None:
        send_args.extend(["--mood-payload", json.dumps(mood_data, ensure_ascii=False)])
    if args.chat_id:
        send_args.extend(["--chat-id", args.chat_id])

    result = run_python_json(send_tool_path, send_args)
    result["heartbeat"] = {
        "enabled": True,
        "delivery_route": resolve_delivery_config(config).get("route"),
        "mood_stage": mood_stage,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "final_state": "failed",
                    "stage": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="UNEXPECTED_HEARTBEAT_ERROR",
                        message=str(exc),
                        recoverability="repair_setup",
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
