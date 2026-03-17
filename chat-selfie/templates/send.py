from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from delivery_common import (
    DEFAULT_CONFIG_PATH,
    build_runtime_result,
    build_stage_result,
    load_config,
    load_module_from_path,
    maybe_rebuild_framework_send_adapter,
    normalize_reason,
    resolve_delivery_config,
    resolve_delivery_target,
    resolve_mood_config,
    resolve_mood_via_workspace_tool,
    resolve_self_repair_config,
    resolve_workspace_config,
    resolve_workspace_path,
    run_python_json,
    validate_runtime_workspace,
    build_heartbeat_caption,
    evaluate_occasional_gate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified Chat Selfie delivery entry for local-framework and Telegram routes.",
    )
    parser.add_argument("--agent", required=True, help="Target agent id.")
    parser.add_argument("--text", default=None, help="Final reply text for this turn.")
    parser.add_argument("--mood", default=None, help="Optional explicit mood id.")
    parser.add_argument("--mood-payload", default=None, help="Optional JSON mood payload to reuse without resolving again.")
    parser.add_argument("--reason", default="reply_time", help="Delivery reason such as reply_time or heartbeat.")
    parser.add_argument("--reply-to-message-id", default=None, help="Optional reply target for Telegram route.")
    parser.add_argument("--chat-id", default=None, help="Optional explicit target override for Telegram delivery.")
    return parser


def _load_optional_adapter(path: Path):
    if not path.exists():
        return None
    return load_module_from_path(path)


def _resolve_mood_if_needed(
    config: dict[str, Any],
    agent: str,
    mood_id: str | None,
    mood_payload: dict[str, Any] | None,
    reason: str,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if mood_payload is not None:
        return mood_payload, mood_payload.get("stage") or build_stage_result("success", attempted=True)
    mood_cfg = resolve_mood_config(config)
    if not bool(mood_cfg.get("enabled", False)) and not mood_id:
        return None, build_stage_result("skipped", attempted=False)
    try:
        result = resolve_mood_via_workspace_tool(
            config_path=DEFAULT_CONFIG_PATH,
            config=config,
            agent=agent,
            mood_id=mood_id,
            reason=reason,
        )
    except Exception as exc:
        return None, build_stage_result(
            "failed",
            attempted=True,
            error_code="MOOD_TOOL_FAILED",
            message=str(exc),
            recoverability="degrade",
        )
    return result, result.get("stage") or build_stage_result("success", attempted=True)


def _call_generate_tool(
    *,
    config: dict[str, Any],
    agent: str,
    final_text: str,
    mood_id: str | None,
    mood_data: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    workspace_cfg = resolve_workspace_config(config)
    generate_tool_path = resolve_workspace_path(
        DEFAULT_CONFIG_PATH.parent,
        workspace_cfg.get("generate_tool_path") or config.get("generation", {}).get("workspace_tool_path"),
        "./generate.py",
    )

    generate_args = [
        "--agent",
        agent,
        "--text",
        final_text,
        "--reason",
        reason,
    ]
    if mood_id:
        generate_args.extend(["--mood", mood_id])
    if mood_data is not None:
        generate_args.extend(["--mood-payload", json.dumps(mood_data, ensure_ascii=False)])

    return run_python_json(generate_tool_path, generate_args)


def _deliver_via_local_framework(
    *,
    config: dict[str, Any],
    agent: str,
    final_text: str,
    mood_data: dict[str, Any] | None,
    generation_result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    delivery_cfg = resolve_delivery_config(config)
    adapter_path = resolve_workspace_path(
        DEFAULT_CONFIG_PATH.parent,
        delivery_cfg.get("framework_send_adapter_path"),
        "./adapters/delivery/framework_send.py",
    )
    auto_repairs: list[dict[str, Any]] = []
    maybe_rebuild_framework_send_adapter(
        config_path=DEFAULT_CONFIG_PATH,
        config=config,
        adapter_path=adapter_path,
        auto_repairs=auto_repairs,
    )
    adapter_module = _load_optional_adapter(adapter_path)

    handoff_payload = {
        "agent": agent,
        "final_text": final_text,
        "image_path": generation_result.get("image_path") or generation_result.get("desired_output_path"),
        "generation_result": generation_result,
        "mood": mood_data,
        "delivery_route": "local_framework",
    }

    delivery_result = None
    if adapter_module is not None:
        callable_result = getattr(adapter_module, "deliver_payload", None)
        if callable(callable_result):
            delivery_result = callable_result(handoff_payload)
        else:
            delivery_result = {
                "ok": False,
                "error_code": "FRAMEWORK_ADAPTER_CONTRACT_INVALID",
                "message": "framework_send adapter must expose deliver_payload(payload).",
            }

    if adapter_module is None:
        framework_stage = build_stage_result(
            "pending",
            attempted=False,
            error_code="FRAMEWORK_HANDOFF_UNCONFIRMED",
            message="No framework_send adapter is present. The host framework must complete the handoff.",
            recoverability="degrade",
            adapter_path=str(adapter_path),
        )
        return (
            {
                "ok": False,
                "delivery_route": "local_framework",
                "framework_handoff_required": True,
                "reply_consumed": False,
                "should_send_followup_text": True,
                "should_send_success_notice": False,
                "framework_payload": handoff_payload,
                "delivery_result": None,
            },
            framework_stage,
            auto_repairs,
        )

    if isinstance(delivery_result, dict):
        delivery_ok = bool(delivery_result.get("ok", delivery_result.get("success", False)))
        if delivery_ok:
            framework_stage = build_stage_result("success", attempted=True, adapter_path=str(adapter_path))
            return (
                {
                    "ok": True,
                    "delivery_route": "local_framework",
                    "framework_handoff_required": False,
                    "reply_consumed": bool(delivery_result.get("reply_consumed", False)),
                    "should_send_followup_text": bool(delivery_result.get("should_send_followup_text", False)),
                    "should_send_success_notice": bool(delivery_result.get("should_send_success_notice", False)),
                    "framework_payload": handoff_payload,
                    "delivery_result": delivery_result,
                },
                framework_stage,
                auto_repairs,
            )
        if delivery_result.get("handoff_pending") or delivery_result.get("pending"):
            framework_stage = build_stage_result(
                "pending",
                attempted=True,
                error_code=str(delivery_result.get("error_code") or "FRAMEWORK_HANDOFF_PENDING"),
                message=str(delivery_result.get("message") or "Framework handoff is still pending."),
                recoverability="degrade",
                adapter_path=str(adapter_path),
            )
        else:
            framework_stage = build_stage_result(
                "failed",
                attempted=True,
                error_code=str(delivery_result.get("error_code") or "FRAMEWORK_DELIVERY_FAILED"),
                message=str(delivery_result.get("message") or "Framework delivery failed."),
                recoverability="degrade",
                adapter_path=str(adapter_path),
            )
    else:
        framework_stage = build_stage_result(
            "failed",
            attempted=True,
            error_code="FRAMEWORK_DELIVERY_INVALID_RESULT",
            message="framework_send adapter returned a non-object result.",
            recoverability="repair_setup",
            adapter_path=str(adapter_path),
        )

    return (
        {
            "ok": False,
            "delivery_route": "local_framework",
            "framework_handoff_required": framework_stage["status"] == "pending",
            "reply_consumed": False,
            "should_send_followup_text": True,
            "should_send_success_notice": False,
            "framework_payload": handoff_payload,
            "delivery_result": delivery_result,
        },
        framework_stage,
        auto_repairs,
    )


def _deliver_via_telegram(
    *,
    config: dict[str, Any],
    final_text: str,
    generation_result: dict[str, Any],
    reply_to_message_id: str | None,
    chat_id: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if generation_result.get("handoff_required"):
        return (
            {
                "ok": False,
                "delivery_route": "telegram_api",
                "reply_consumed": False,
                "should_send_followup_text": True,
                "should_send_success_notice": False,
            },
            build_stage_result(
                "failed",
                attempted=False,
                error_code="TELEGRAM_IMAGE_HANDOFF_REQUIRED",
                message="Telegram delivery requires a saved image path before send.",
                recoverability="degrade",
            ),
        )

    workspace_cfg = resolve_workspace_config(config)
    telegram_tool_path = resolve_workspace_path(
        DEFAULT_CONFIG_PATH.parent,
        workspace_cfg.get("telegram_send_tool_path") or config.get("delivery", {}).get("telegram", {}).get("workspace_tool_path"),
        "./send_telegram.py",
    )
    image_path = generation_result.get("image_path")
    if not image_path:
        return (
            {
                "ok": False,
                "delivery_route": "telegram_api",
                "reply_consumed": False,
                "should_send_followup_text": True,
                "should_send_success_notice": False,
            },
            build_stage_result(
                "failed",
                attempted=False,
                error_code="TELEGRAM_IMAGE_MISSING",
                message="Telegram delivery requires generation_result.image_path.",
                recoverability="degrade",
            ),
        )

    telegram_args = [
        "--image-path",
        str(image_path),
        "--text",
        final_text,
    ]
    if chat_id:
        telegram_args.extend(["--chat-id", chat_id])
    if reply_to_message_id:
        telegram_args.extend(["--reply-to-message-id", reply_to_message_id])

    telegram_result = run_python_json(telegram_tool_path, telegram_args)
    return (
        {
            "ok": bool(telegram_result.get("ok", False)),
            "delivery_route": "telegram_api",
            "reply_consumed": bool(telegram_result.get("ok", False)),
            "should_send_followup_text": not bool(telegram_result.get("ok", False)),
            "should_send_success_notice": False,
            "telegram_result": telegram_result,
        },
        telegram_result.get("stage")
        or build_stage_result(
            "success" if bool(telegram_result.get("ok", False)) else "failed",
            attempted=True,
            error_code=None if bool(telegram_result.get("ok", False)) else "TELEGRAM_SEND_FAILED",
            message=None if bool(telegram_result.get("ok", False)) else "Telegram send failed.",
            recoverability=None if bool(telegram_result.get("ok", False)) else "degrade",
        ),
    )


def _build_gate_response(*, agent: str, message: str, retry_after_seconds: int, rate_limited: bool) -> dict[str, Any]:
    return {
        "ok": False,
        "final_state": "blocked",
        "agent": agent,
        "blocked": True,
        "rate_limited": rate_limited,
        "rate_limit_message": message,
        "retry_after_seconds": retry_after_seconds,
        "delivery": {
            "ok": False,
            "delivery_route": None,
            "reply_consumed": False,
            "should_send_followup_text": False,
            "should_send_success_notice": False,
        },
    }


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(DEFAULT_CONFIG_PATH)
    delivery_cfg = resolve_delivery_config(config)
    delivery_route = str(delivery_cfg.get("route") or "local_framework")
    normalized_reason = normalize_reason(args.reason)
    self_repair_cfg = resolve_self_repair_config(config)
    mood_payload = json.loads(args.mood_payload) if args.mood_payload else None
    if mood_payload is not None and not isinstance(mood_payload, dict):
        _emit(
            build_runtime_result(
                agent=args.agent,
                reason=normalized_reason,
                config=config,
                final_state="failed",
                stages={
                    "mood": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="INVALID_MOOD_PAYLOAD",
                        message="--mood-payload must be a JSON object",
                        recoverability="repair_setup",
                    ),
                    "generation": build_stage_result("skipped", attempted=False),
                    "delivery": build_stage_result("skipped", attempted=False),
                    "telegram": build_stage_result("skipped", attempted=False),
                    "framework_handoff": build_stage_result("skipped", attempted=False),
                },
            )
        )
        return

    preflight = validate_runtime_workspace(
        config_path=DEFAULT_CONFIG_PATH,
        config=config,
        reason=normalized_reason,
    )
    auto_repairs = list(preflight["auto_repairs"])
    user_actions = list(preflight["user_action_required"])
    stages: dict[str, Any] = {
        "mood": build_stage_result("skipped", attempted=False),
        "generation": build_stage_result("skipped", attempted=False),
        "delivery": build_stage_result("skipped", attempted=False),
        "telegram": build_stage_result("skipped", attempted=False),
        "framework_handoff": build_stage_result("skipped", attempted=False),
    }

    if not preflight["preflight"]["generation_ready"]:
        final_state = "degraded_text_only" if self_repair_cfg.get("allow_text_only_degrade", True) else "repair_required"
        _emit(
            build_runtime_result(
                agent=args.agent,
                reason=normalized_reason,
                config=config,
                final_state=final_state,
                stages={
                    **stages,
                    "generation": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="GENERATION_ROUTE_NOT_READY",
                        message="The configured generation route is not ready.",
                        recoverability="repair_setup",
                    ),
                },
                auto_repairs=auto_repairs,
                user_action_required=user_actions,
                preflight=preflight["preflight"],
                recommended_next_step="repair_generation_setup",
                recommended_user_message="当前自拍链路没有可用生图路线，本回合应先降级为文本回复并进入修复。",
            )
        )
        return

    if delivery_route == "telegram_api" and not preflight["preflight"]["route_ready"]:
        if self_repair_cfg.get("allow_route_fallback", True) and bool(delivery_cfg.get("fallback_to_local_framework", True)):
            auto_repairs.append(
                {
                    "action": "fallback_delivery_route_to_local_framework",
                    "applied": True,
                    "details": "Telegram runtime was not ready, so delivery fell back to local_framework.",
                }
            )
            delivery_route = "local_framework"
        else:
            _emit(
                build_runtime_result(
                    agent=args.agent,
                    reason=normalized_reason,
                    config=config,
                    final_state="repair_required",
                    stages={
                        **stages,
                        "delivery": build_stage_result(
                            "failed",
                            attempted=False,
                            error_code="DELIVERY_ROUTE_NOT_READY",
                            message="The configured delivery route is not ready.",
                            recoverability="repair_setup",
                        ),
                    },
                    auto_repairs=auto_repairs,
                    user_action_required=user_actions,
                    preflight=preflight["preflight"],
                    recommended_next_step="repair_delivery_setup",
                )
            )
            return

    mood_data, mood_stage = _resolve_mood_if_needed(config, args.agent, args.mood, mood_payload, normalized_reason)
    stages["mood"] = mood_stage
    if mood_data is not None and (mood_data.get("status") == "blocked" or mood_data.get("blocked") or mood_data.get("rate_limited")):
        _emit(
            build_runtime_result(
                agent=args.agent,
                reason=normalized_reason,
                config=config,
                final_state="blocked",
                stages=stages,
                auto_repairs=auto_repairs + list(mood_data.get("auto_repairs") or []),
                user_action_required=user_actions,
                preflight=preflight["preflight"],
                mood=mood_data,
                recommended_next_step="fallback_to_text_only",
            )
        )
        return
    if mood_data is not None and not mood_data.get("ok", True):
        auto_repairs.extend(list(mood_data.get("auto_repairs") or []))
        mood_data = None

    final_text = (args.text or "").strip()
    if not final_text and normalized_reason == "heartbeat":
        final_text = build_heartbeat_caption(
            config_path=DEFAULT_CONFIG_PATH,
            config=config,
            agent=args.agent,
            mood_data=mood_data,
        )
    if not final_text:
        _emit(
            build_runtime_result(
                agent=args.agent,
                reason=normalized_reason,
                config=config,
                final_state="failed",
                stages={
                    **stages,
                    "delivery": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="FINAL_TEXT_MISSING",
                        message="--text is required unless heartbeat caption generation is being used.",
                        recoverability="repair_setup",
                    ),
                },
                auto_repairs=auto_repairs,
                user_action_required=user_actions,
                preflight=preflight["preflight"],
            )
        )
        return

    target_info = resolve_delivery_target(
        config=config,
        reason=normalized_reason,
        explicit_target=args.chat_id,
    )

    occasional_gate = None
    if mood_data is None or not bool(mood_data.get("occasional_gate_consumed")):
        occasional_gate = evaluate_occasional_gate(
            config_path=DEFAULT_CONFIG_PATH,
            config=config,
            agent=args.agent,
            script_name="send.py",
            reason=normalized_reason,
            consume=True,
        )
        if not occasional_gate["allowed"]:
            stages["delivery"] = build_stage_result(
                "blocked",
                attempted=False,
                error_code="OCCASIONAL_GATE_BLOCKED",
                message=str(occasional_gate["message"]),
                recoverability="degrade",
                retry_after_seconds=int(occasional_gate["retry_after_seconds"]),
            )
            _emit(
                build_runtime_result(
                    agent=args.agent,
                    reason=normalized_reason,
                    config=config,
                    final_state="blocked",
                    stages=stages,
                    auto_repairs=auto_repairs,
                    user_action_required=user_actions,
                    preflight=preflight["preflight"],
                    text=final_text,
                    mood=mood_data,
                    recommended_next_step="fallback_to_text_only",
                    recommended_user_message=str(occasional_gate["message"]),
                )
            )
            return

    generation_result = _call_generate_tool(
        config=config,
        agent=args.agent,
        final_text=final_text,
        mood_id=args.mood,
        mood_data=mood_data,
        reason=normalized_reason,
    )
    stages["generation"] = generation_result.get("stage") or build_stage_result(
        "success" if generation_result.get("ok") else "failed",
        attempted=True,
        error_code=generation_result.get("error_code"),
        message=generation_result.get("message"),
    )
    auto_repairs.extend(list(generation_result.get("auto_repairs") or []))
    user_actions.extend(list(generation_result.get("user_action_required") or []))

    if generation_result.get("final_state") in {"failed", "repair_required"} or stages["generation"]["status"] == "failed":
        final_state = "degraded_text_only" if self_repair_cfg.get("allow_text_only_degrade", True) else "repair_required"
        _emit(
            build_runtime_result(
                agent=args.agent,
                reason=normalized_reason,
                config=config,
                final_state=final_state,
                stages=stages,
                auto_repairs=auto_repairs,
                user_action_required=user_actions,
                preflight=preflight["preflight"],
                text=final_text,
                mood=mood_data,
                generation=generation_result,
                delivery_target=target_info,
                recommended_next_step="fallback_to_text_only" if final_state == "degraded_text_only" else "repair_generation_setup",
            )
        )
        return

    if delivery_route == "telegram_api":
        delivery_result, telegram_stage = _deliver_via_telegram(
            config=config,
            final_text=final_text,
            generation_result=generation_result,
            reply_to_message_id=args.reply_to_message_id,
            chat_id=(
                str(target_info["telegram_chat_id"])
                if target_info.get("telegram_chat_id") is not None
                else None
            ),
        )
        stages["telegram"] = telegram_stage
        stages["delivery"] = telegram_stage
        if not delivery_result.get("ok") and self_repair_cfg.get("allow_route_fallback", True) and bool(delivery_cfg.get("fallback_to_local_framework", True)):
            auto_repairs.append(
                {
                    "action": "fallback_delivery_route_to_local_framework",
                    "applied": True,
                    "details": "Telegram delivery failed, so delivery fell back to local_framework.",
                }
            )
            delivery_result, framework_stage, framework_repairs = _deliver_via_local_framework(
                config=config,
                agent=args.agent,
                final_text=final_text,
                mood_data=mood_data,
                generation_result=generation_result,
            )
            auto_repairs.extend(framework_repairs)
            stages["framework_handoff"] = framework_stage
            stages["delivery"] = framework_stage
    else:
        delivery_result, framework_stage, framework_repairs = _deliver_via_local_framework(
            config=config,
            agent=args.agent,
            final_text=final_text,
            mood_data=mood_data,
            generation_result=generation_result,
        )
        auto_repairs.extend(framework_repairs)
        stages["framework_handoff"] = framework_stage
        stages["delivery"] = framework_stage
        delivery_result["delivery_target"] = target_info

    if stages["delivery"]["status"] == "success":
        final_state = "success"
    elif stages["delivery"]["status"] == "pending":
        final_state = "handoff_pending"
    else:
        final_state = "degraded_text_only" if self_repair_cfg.get("allow_text_only_degrade", True) else "failed"

    _emit(
        build_runtime_result(
            agent=args.agent,
            reason=normalized_reason,
            config=config,
            final_state=final_state,
            stages=stages,
            auto_repairs=auto_repairs,
            user_action_required=user_actions,
            preflight=preflight["preflight"],
            text=final_text,
            mood=mood_data,
            generation=generation_result,
            delivery=delivery_result,
            delivery_target=target_info,
            recommended_next_step=(
                None
                if final_state == "success"
                else "wait_for_framework_handoff"
                if final_state == "handoff_pending"
                else "fallback_to_text_only"
            ),
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        config = {"delivery": {}, "generation": {}}
        _emit(
            build_runtime_result(
                agent="unknown",
                reason="reply_time",
                config=config,
                final_state="failed",
                stages={
                    "mood": build_stage_result("skipped", attempted=False),
                    "generation": build_stage_result("skipped", attempted=False),
                    "delivery": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="UNEXPECTED_SEND_ERROR",
                        message=str(exc),
                        recoverability="repair_setup",
                    ),
                    "telegram": build_stage_result("skipped", attempted=False),
                    "framework_handoff": build_stage_result("skipped", attempted=False),
                },
            )
        )
