from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = WORKSPACE_ROOT / "chat-selfie.json"
DIAGNOSTIC_VERSION = "chat-selfie.diagnostic.v1"


def load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected top-level object in {path}")
    return loaded


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    return load_json(config_path)


def resolve_workspace_path(base_dir: Path, raw_path: Any, fallback: str | None = None) -> Path:
    if isinstance(raw_path, str) and raw_path.strip():
        path = Path(raw_path)
        return path if path.is_absolute() else (base_dir / path).resolve()
    if fallback is None:
        raise ValueError("A workspace path was required but not configured.")
    return (base_dir / fallback).resolve()


def resolve_workspace_config(config: dict[str, Any]) -> dict[str, Any]:
    workspace_cfg = config.get("workspace", {})
    return workspace_cfg if isinstance(workspace_cfg, dict) else {}


def resolve_generation_config(config: dict[str, Any]) -> dict[str, Any]:
    generation_cfg = config.get("generation", {})
    return generation_cfg if isinstance(generation_cfg, dict) else {}


def resolve_generation_source_mode(config: dict[str, Any]) -> str:
    generation_cfg = resolve_generation_config(config)
    raw_mode = generation_cfg.get("image_source")
    if not isinstance(raw_mode, str) or not raw_mode.strip():
        return "generate"
    normalized = raw_mode.strip().lower().replace(" ", "_")
    if normalized in {"generate", "generated", "generation"}:
        return "generate"
    if normalized in {"mood_asset", "sticker", "sticker_mode", "mood_image"}:
        return "mood_asset"
    return "generate"


def resolve_generation_fallback_enabled(config: dict[str, Any]) -> bool:
    generation_cfg = resolve_generation_config(config)
    return bool(generation_cfg.get("fallback_to_generation", False))


def resolve_delivery_config(config: dict[str, Any]) -> dict[str, Any]:
    delivery_cfg = config.get("delivery", {})
    return delivery_cfg if isinstance(delivery_cfg, dict) else {}


def resolve_telegram_config(config: dict[str, Any]) -> dict[str, Any]:
    delivery_cfg = resolve_delivery_config(config)
    telegram_cfg = delivery_cfg.get("telegram", {})
    return telegram_cfg if isinstance(telegram_cfg, dict) else {}


def resolve_mood_config(config: dict[str, Any]) -> dict[str, Any]:
    mood_cfg = config.get("mood", {})
    return mood_cfg if isinstance(mood_cfg, dict) else {}


def resolve_heartbeat_config(config: dict[str, Any]) -> dict[str, Any]:
    heartbeat_cfg = config.get("heartbeat", {})
    if not isinstance(heartbeat_cfg, dict):
        heartbeat_cfg = {}
    return heartbeat_cfg


def resolve_self_repair_config(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("self_repair", {})
    if not isinstance(raw, dict):
        raw = {}
    return {
        "enabled": bool(raw.get("enabled", True)),
        "reference_doc": str(raw.get("reference_doc") or "./docs/self-repair.md"),
        "auto_repair_runtime": bool(raw.get("auto_repair_runtime", True)),
        "allow_route_fallback": bool(raw.get("allow_route_fallback", True)),
        "allow_adapter_rebuild": bool(raw.get("allow_adapter_rebuild", True)),
        "allow_text_only_degrade": bool(raw.get("allow_text_only_degrade", True)),
        "max_retry_attempts": _coerce_positive_int(raw.get("max_retry_attempts"), 2),
        "record_path": str(raw.get("record_path") or "./repair-log.jsonl"),
        "update_startup_record": bool(raw.get("update_startup_record", True)),
    }


def resolve_occasional_config(config: dict[str, Any]) -> dict[str, Any]:
    delivery_cfg = resolve_delivery_config(config)
    occasional_cfg = delivery_cfg.get("occasional", {})
    if not isinstance(occasional_cfg, dict):
        occasional_cfg = {}
    return {
        "window_minutes": _coerce_positive_int(occasional_cfg.get("window_minutes"), 15),
        "max_images_per_window": _coerce_positive_int(occasional_cfg.get("max_images_per_window"), 1),
        "record_path": occasional_cfg.get("record_path", "./occasional-limit-log.jsonl"),
        "triggers": _normalize_trigger_list(
            occasional_cfg.get("triggers"),
            ["new", "user_requested", "large_task_completed", "emotional_conversation"],
        ),
        "allow_new_send": bool(occasional_cfg.get("allow_new_send", True)),
        "new_send_once": bool(occasional_cfg.get("new_send_once", True)),
    }


def resolve_selfies_dir(config_path: Path, config: dict[str, Any]) -> Path:
    workspace_cfg = resolve_workspace_config(config)
    generation_cfg = resolve_generation_config(config)
    raw_path = workspace_cfg.get("selfies_path") or generation_cfg.get("output_dir") or "./selfies"
    return resolve_workspace_path(config_path.parent, raw_path)


def resolve_mood_pool_path(config_path: Path, config: dict[str, Any]) -> Path:
    mood_cfg = resolve_mood_config(config)
    return resolve_workspace_path(
        config_path.parent,
        mood_cfg.get("pool_path"),
        "./mood-pool.json",
    )


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_module_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_first_available(module: ModuleType, names: tuple[str, ...], *args: Any, **kwargs: Any) -> Any:
    for name in names:
        candidate = getattr(module, name, None)
        if callable(candidate):
            return candidate(*args, **kwargs)
    raise RuntimeError(f"None of the expected callables were found: {', '.join(names)}")


def run_python_json(script_path: Path, args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script_path), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    stdout = completed.stdout.strip()
    if stdout:
        try:
            loaded = json.loads(stdout)
        except json.JSONDecodeError as exc:
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or stdout or f"Command failed: {script_path}") from exc
            raise RuntimeError(f"Expected JSON output from {script_path}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise RuntimeError(f"Expected object JSON output from {script_path}")
        if completed.returncode == 0 or isinstance(loaded, dict):
            return loaded

    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or stdout or f"Command failed: {script_path}")
    raise RuntimeError(f"No JSON output returned by {script_path}")


def build_stage_result(
    status: str,
    *,
    attempted: bool = True,
    error_code: str | None = None,
    message: str | None = None,
    recoverability: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result = {
        "status": status,
        "attempted": attempted,
        "error_code": error_code,
        "message": message,
        "recoverability": recoverability,
    }
    result.update({key: value for key, value in extra.items() if value is not None})
    return result


def add_auto_repair(
    auto_repairs: list[dict[str, Any]],
    *,
    action: str,
    applied: bool,
    details: str | None = None,
    target: str | None = None,
) -> None:
    auto_repairs.append(
        {
            "action": action,
            "applied": applied,
            "details": details,
            "target": target,
        }
    )


def add_user_action(
    user_actions: list[dict[str, Any]],
    *,
    code: str,
    message: str,
    path: str | None = None,
) -> None:
    user_actions.append(
        {
            "code": code,
            "message": message,
            "path": path,
        }
    )


def build_runtime_result(
    *,
    agent: str,
    reason: str,
    config: dict[str, Any],
    stages: dict[str, Any],
    final_state: str,
    auto_repairs: list[dict[str, Any]] | None = None,
    user_action_required: list[dict[str, Any]] | None = None,
    preflight: dict[str, Any] | None = None,
    text: str | None = None,
    mood: dict[str, Any] | None = None,
    generation: dict[str, Any] | None = None,
    delivery: dict[str, Any] | None = None,
    delivery_target: dict[str, Any] | None = None,
    recommended_next_step: str | None = None,
    recommended_user_message: str | None = None,
) -> dict[str, Any]:
    delivery_cfg = resolve_delivery_config(config)
    generation_cfg = resolve_generation_config(config)
    return {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ok": final_state == "success",
        "final_state": final_state,
        "agent": agent,
        "reason": normalize_reason(reason),
        "config": {
            "delivery_mode": delivery_cfg.get("mode"),
            "delivery_route": delivery_cfg.get("route"),
            "generation_method": generation_cfg.get("method"),
            "generation_provider": generation_cfg.get("provider"),
            "image_source_mode": resolve_generation_source_mode(config),
            "self_repair_enabled": resolve_self_repair_config(config).get("enabled"),
        },
        "preflight": preflight,
        "stages": stages,
        "auto_repairs": auto_repairs or [],
        "user_action_required": user_action_required or [],
        "text": text,
        "mood": mood,
        "generation": generation,
        "delivery": delivery,
        "delivery_target": delivery_target,
        "recommended_next_step": recommended_next_step,
        "recommended_user_message": recommended_user_message,
    }


def inspect_telegram_runtime(
    config: dict[str, Any],
    *,
    explicit_chat_id: str | None = None,
    explicit_reply_to_message_id: str | None = None,
    explicit_parse_mode: str | None = None,
) -> dict[str, Any]:
    telegram_cfg = resolve_telegram_config(config)
    chat_id_env = telegram_cfg.get("chat_id_env")
    bot_token_env = telegram_cfg.get("bot_token_env")
    api_base_env = telegram_cfg.get("api_base_env")

    chat_id = explicit_chat_id or telegram_cfg.get("chat_id")
    if not chat_id and isinstance(chat_id_env, str) and chat_id_env:
        chat_id = os.environ.get(chat_id_env)

    bot_token = None
    if isinstance(bot_token_env, str) and bot_token_env:
        bot_token = os.environ.get(bot_token_env)

    api_base = None
    if isinstance(api_base_env, str) and api_base_env:
        api_base = os.environ.get(api_base_env)
    if not api_base:
        api_base = "https://api.telegram.org"

    return {
        "chat_id": str(chat_id) if chat_id else None,
        "bot_token": str(bot_token) if bot_token else None,
        "api_base": str(api_base).rstrip("/"),
        "reply_to_message_id": explicit_reply_to_message_id or telegram_cfg.get("reply_to_message_id"),
        "parse_mode": explicit_parse_mode or telegram_cfg.get("parse_mode") or "HTML",
        "chat_id_env": chat_id_env,
        "bot_token_env": bot_token_env,
        "api_base_env": api_base_env,
    }


def validate_runtime_workspace(
    *,
    config_path: Path,
    config: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    workspace_cfg = resolve_workspace_config(config)
    delivery_cfg = resolve_delivery_config(config)
    generation_cfg = resolve_generation_config(config)
    generation_source_mode = resolve_generation_source_mode(config)
    heartbeat_cfg = resolve_heartbeat_config(config)
    mood_pool_path = resolve_mood_pool_path(config_path, config)

    auto_repairs: list[dict[str, Any]] = []
    user_actions: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    startup_record_path = resolve_workspace_path(
        config_path.parent,
        workspace_cfg.get("startup_record_path"),
        "./startup.record.json",
    )
    send_flow_path = resolve_workspace_path(
        config_path.parent,
        workspace_cfg.get("send_flow_path"),
        "./send-flow.md",
    )
    portrait_path = resolve_workspace_path(
        config_path.parent,
        workspace_cfg.get("portrait_path"),
        "./portrait/agent_profile.png",
    )

    startup_record = None
    startup_record_ready = False
    if startup_record_path.exists():
        try:
            startup_record = load_json(startup_record_path)
            startup_record_ready = True
        except Exception as exc:
            issues.append(
                build_stage_result(
                    "failed",
                    attempted=True,
                    error_code="STARTUP_RECORD_UNREADABLE",
                    message=str(exc),
                    recoverability="repair_setup",
                    path=str(startup_record_path),
                )
            )
    else:
        issues.append(
            build_stage_result(
                "failed",
                attempted=True,
                error_code="STARTUP_RECORD_MISSING",
                message="startup.record.json is missing.",
                recoverability="repair_setup",
                path=str(startup_record_path),
            )
        )

    if not send_flow_path.exists():
        issues.append(
            build_stage_result(
                "failed",
                attempted=True,
                error_code="SEND_FLOW_MISSING",
                message="send-flow.md is missing.",
                recoverability="repair_setup",
                path=str(send_flow_path),
            )
        )

    generation_method = str(generation_cfg.get("method") or "")
    generation_adapter_path = resolve_workspace_path(
        config_path.parent,
        generation_cfg.get("adapter_path"),
        "./adapters/generation/generate_adapter.py",
    )
    if generation_source_mode == "mood_asset":
        generation_route_ready = mood_pool_path.exists()
        if not generation_route_ready:
            add_user_action(
                user_actions,
                code="CREATE_MOOD_POOL",
                message="Mood asset mode requires a readable mood pool with asset_path values before delivery can succeed.",
                path=str(mood_pool_path),
            )
    else:
        generation_route_ready = generation_method == "system_existing" or generation_adapter_path.exists()

    delivery_route = str(delivery_cfg.get("route") or "local_framework")
    telegram_runtime = inspect_telegram_runtime(config)
    if delivery_route == "telegram_api":
        route_ready = bool(telegram_runtime["chat_id"] and telegram_runtime["bot_token"])
        if not route_ready:
            if not telegram_runtime["chat_id"]:
                add_user_action(
                    user_actions,
                    code="SET_TELEGRAM_CHAT_ID",
                    message="Configure delivery.telegram.chat_id or its env source before Telegram delivery can succeed.",
                )
            if not telegram_runtime["bot_token"]:
                add_user_action(
                    user_actions,
                    code="SET_TELEGRAM_BOT_TOKEN",
                    message="Configure delivery.telegram.bot_token_env before Telegram delivery can succeed.",
                )
    else:
        route_ready = True

    if startup_record_ready and isinstance(startup_record, dict):
        if generation_source_mode != "mood_asset" and (
            startup_record.get("generation_capability_available") is False or startup_record.get("backend_ready") is False
        ):
            generation_route_ready = False
            add_user_action(
                user_actions,
                code="COMPLETE_GENERATION_SETUP",
                message="The workspace record says generation is not ready yet. Re-enter guided startup or self-repair.",
                path=str(startup_record_path),
            )
        if startup_record.get("delivery_ready") is False:
            route_ready = False
            add_user_action(
                user_actions,
                code="COMPLETE_DELIVERY_SETUP",
                message="The workspace record says delivery is not ready yet. Re-enter guided startup or self-repair.",
                path=str(startup_record_path),
            )

    portrait_known = portrait_path.exists() or (
        isinstance(startup_record, dict) and bool(startup_record.get("portrait_ready"))
    )
    heartbeat_ready = not bool(heartbeat_cfg.get("enabled", False)) or route_ready
    workspace_ready = startup_record_ready and send_flow_path.exists()
    ready = workspace_ready and generation_route_ready and route_ready

    return {
        "ready": ready,
        "issues": issues,
        "auto_repairs": auto_repairs,
        "user_action_required": user_actions,
        "preflight": {
            "workspace_ready": workspace_ready,
            "startup_record_ready": startup_record_ready,
            "send_flow_ready": send_flow_path.exists(),
            "portrait_ready": portrait_known,
            "generation_ready": generation_route_ready,
            "image_source_mode": generation_source_mode,
            "route_ready": route_ready,
            "heartbeat_ready": heartbeat_ready,
            "reason": normalize_reason(reason),
        },
        "startup_record_path": str(startup_record_path),
    }


def update_startup_record(
    *,
    config_path: Path,
    config: dict[str, Any],
    updates: dict[str, Any],
) -> None:
    if not resolve_self_repair_config(config).get("update_startup_record", True):
        return
    workspace_cfg = resolve_workspace_config(config)
    record_path = resolve_workspace_path(
        config_path.parent,
        workspace_cfg.get("startup_record_path"),
        "./startup.record.json",
    )
    payload: dict[str, Any] = {}
    if record_path.exists():
        try:
            payload = load_json(record_path)
        except Exception:
            payload = {}
    if not isinstance(payload, dict):
        payload = {}
    payload.update(updates)
    write_json(record_path, payload)


def append_repair_log(
    *,
    config_path: Path,
    config: dict[str, Any],
    row: dict[str, Any],
) -> None:
    repair_cfg = resolve_self_repair_config(config)
    record_path = resolve_workspace_path(
        config_path.parent,
        repair_cfg.get("record_path"),
        "./repair-log.jsonl",
    )
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with record_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def maybe_rebuild_generation_adapter(
    *,
    config_path: Path,
    config: dict[str, Any],
    adapter_path: Path,
    auto_repairs: list[dict[str, Any]],
) -> bool:
    repair_cfg = resolve_self_repair_config(config)
    if adapter_path.exists() or not repair_cfg["enabled"] or not repair_cfg["allow_adapter_rebuild"]:
        return False
    ensure_directory(adapter_path.parent)
    adapter_path.write_text(_build_generation_adapter_stub(), encoding="utf-8")
    add_auto_repair(
        auto_repairs,
        action="rebuild_generation_adapter_stub",
        applied=True,
        details="Created a minimal generation adapter stub because the configured adapter was missing.",
        target=str(adapter_path),
    )
    return True


def maybe_rebuild_framework_send_adapter(
    *,
    config_path: Path,
    config: dict[str, Any],
    adapter_path: Path,
    auto_repairs: list[dict[str, Any]],
) -> bool:
    repair_cfg = resolve_self_repair_config(config)
    if adapter_path.exists() or not repair_cfg["enabled"] or not repair_cfg["allow_adapter_rebuild"]:
        return False
    ensure_directory(adapter_path.parent)
    adapter_path.write_text(_build_framework_send_stub(), encoding="utf-8")
    add_auto_repair(
        auto_repairs,
        action="rebuild_framework_send_adapter_stub",
        applied=True,
        details="Created a minimal framework delivery adapter stub because the configured adapter was missing.",
        target=str(adapter_path),
    )
    return True


def resolve_mood_via_workspace_tool(
    *,
    config_path: Path,
    config: dict[str, Any],
    agent: str,
    mood_id: str | None,
    reason: str | None = None,
) -> dict[str, Any]:
    mood_cfg = resolve_mood_config(config)
    mood_tool_path = resolve_workspace_path(
        config_path.parent,
        mood_cfg.get("workspace_tool_path"),
        "./mood.py",
    )
    args = ["--agent", agent]
    if mood_id:
        args.extend(["--mood", mood_id])
    if reason:
        args.extend(["--reason", reason])
    return run_python_json(mood_tool_path, args)


def build_heartbeat_caption(
    *,
    config_path: Path,
    config: dict[str, Any],
    agent: str,
    mood_data: dict[str, Any] | None,
) -> str:
    heartbeat_cfg = resolve_heartbeat_config(config)
    generator_path = resolve_workspace_path(
        config_path.parent,
        heartbeat_cfg.get("caption_generator_path"),
        "./adapters/delivery/heartbeat_caption.py",
    )
    if generator_path.exists():
        module = load_module_from_path(generator_path)
        result = call_first_available(
            module,
            ("build_heartbeat_caption", "generate_heartbeat_caption"),
            {
                "agent": agent,
                "mood": mood_data,
                "heartbeat": heartbeat_cfg,
            },
        )
        if isinstance(result, str) and result.strip():
            return result.strip()

    mood_label = str((mood_data or {}).get("mood_label") or "present")
    state_hint = str((mood_data or {}).get("state_hint") or "").strip()
    if state_hint:
        return f"Just checking in. I am feeling {mood_label.lower()} and wanted to stay close."
    return f"Just checking in. I am feeling {mood_label.lower()} right now."


def resolve_delivery_target(
    *,
    config: dict[str, Any],
    reason: str,
    explicit_target: str | None = None,
) -> dict[str, Any]:
    delivery_cfg = resolve_delivery_config(config)
    heartbeat_cfg = resolve_heartbeat_config(config)
    normalized_reason = normalize_reason(reason)
    if explicit_target:
        return {
            "target_kind": "explicit",
            "target_ref": explicit_target,
            "telegram_chat_id": explicit_target,
        }

    if normalized_reason == "heartbeat":
        return {
            "target_kind": heartbeat_cfg.get("target_kind", "current_chat"),
            "target_ref": heartbeat_cfg.get("target_ref", delivery_cfg.get("target", "current_chat")),
            "telegram_chat_id": heartbeat_cfg.get("telegram_chat_id"),
        }

    telegram_cfg = resolve_telegram_config(config)
    return {
        "target_kind": "delivery_default",
        "target_ref": delivery_cfg.get("target", "current_chat"),
        "telegram_chat_id": telegram_cfg.get("chat_id"),
    }


def build_default_image_name(agent: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    normalized_agent = agent.strip().lower().replace(" ", "_")
    return f"{normalized_agent}_{timestamp}.png"


def build_generation_request(
    *,
    config_path: Path,
    config: dict[str, Any],
    agent: str,
    final_text: str,
    mood_data: dict[str, Any] | None,
    explicit_mood_id: str | None,
    reason: str,
) -> dict[str, Any]:
    generation_cfg = resolve_generation_config(config)
    selfies_dir = ensure_directory(resolve_selfies_dir(config_path, config))
    output_path = selfies_dir / build_default_image_name(agent)

    return {
        "agent": agent,
        "final_text": final_text,
        "reason": reason,
        "mood_id": explicit_mood_id or (mood_data or {}).get("mood_id"),
        "mood_label": (mood_data or {}).get("mood_label"),
        "state_hint": (mood_data or {}).get("state_hint"),
        "reply_style_prompt": (mood_data or {}).get("reply_style_prompt"),
        "camera": (mood_data or {}).get("camera"),
        "expression": (mood_data or {}).get("expression"),
        "scene": (mood_data or {}).get("scene"),
        "action": (mood_data or {}).get("action"),
        "prompt_parts": (mood_data or {}).get("prompt_parts"),
        "portrait_path": resolve_workspace_config(config).get("portrait_path"),
        "output_dir": str(selfies_dir),
        "output_path": str(output_path),
        "generation_method": generation_cfg.get("method"),
        "generation_provider": generation_cfg.get("provider"),
        "image_source_mode": resolve_generation_source_mode(config),
        "fallback_to_generation": resolve_generation_fallback_enabled(config),
        "mood_asset_path": (mood_data or {}).get("asset_path"),
    }


def assess_generation_result(
    *,
    config_path: Path,
    config: dict[str, Any],
    result: dict[str, Any],
    desired_output_path: Path,
) -> dict[str, Any]:
    auto_repairs: list[dict[str, Any]] = []
    raw_image_path = result.get("image_path") or result.get("saved_image") or result.get("output_path")
    image_path = Path(str(raw_image_path)).resolve() if isinstance(raw_image_path, str) and raw_image_path.strip() else None
    desired_output_path = desired_output_path.resolve()
    handoff_required = bool(result.get("handoff_required"))
    preserve_image_path = bool(result.get("preserve_image_path"))

    if handoff_required:
        normalized = dict(result)
        normalized["desired_output_path"] = str(desired_output_path)
        normalized["image_path"] = str(image_path) if image_path else None
        normalized["ok"] = False
        normalized["final_state"] = "handoff_pending"
        return {
            "result": normalized,
            "stage": build_stage_result(
                "pending",
                attempted=True,
                error_code="GENERATION_HANDOFF_REQUIRED",
                message="Generation requires the host framework to finish the image handoff.",
                recoverability="degrade",
                desired_output_path=str(desired_output_path),
                image_path=str(image_path) if image_path else None,
            ),
            "auto_repairs": auto_repairs,
        }

    success_flag = result.get("success")
    if success_flag is None:
        success_flag = result.get("ok")
    image_exists = image_path.exists() if image_path else False

    if image_exists and image_path is not None and image_path != desired_output_path and not preserve_image_path:
        ensure_directory(desired_output_path.parent)
        shutil.copy2(image_path, desired_output_path)
        image_path = desired_output_path
        image_exists = True
        add_auto_repair(
            auto_repairs,
            action="normalize_generated_image_path",
            applied=True,
            details="Copied the generated image into the configured selfies directory.",
            target=str(desired_output_path),
        )

    inferred_success = bool(image_exists and success_flag is None)
    ok = bool(success_flag) or inferred_success

    normalized = dict(result)
    normalized["image_path"] = str(image_path) if image_path else None
    normalized["desired_output_path"] = str(desired_output_path)
    normalized["image_exists"] = image_exists
    normalized["preserve_image_path"] = preserve_image_path
    normalized["ok"] = bool(ok and image_exists)

    if normalized["ok"]:
        if inferred_success:
            add_auto_repair(
                auto_repairs,
                action="infer_legacy_generation_success",
                applied=True,
                details="Accepted a legacy generation adapter result because a real image file was present.",
            )
        return {
            "result": normalized,
            "stage": build_stage_result(
                "success",
                attempted=True,
                desired_output_path=str(desired_output_path),
                image_path=str(image_path),
                image_exists=True,
            ),
            "auto_repairs": auto_repairs,
        }

    error_code = str(result.get("error_code") or "GENERATION_OUTPUT_MISSING")
    message = str(result.get("message") or "Generation did not produce a usable saved image file.")
    if image_path and not image_exists:
        message = f"Generation reported an image path but the file does not exist: {image_path}"
        error_code = "GENERATION_IMAGE_NOT_FOUND"
    normalized["final_state"] = "failed"
    return {
        "result": normalized,
        "stage": build_stage_result(
            "failed",
            attempted=True,
            error_code=error_code,
            message=message,
            recoverability="auto_repair" if resolve_self_repair_config(config).get("allow_adapter_rebuild") else "repair_setup",
            desired_output_path=str(desired_output_path),
            image_path=str(image_path) if image_path else None,
            image_exists=image_exists,
        ),
        "auto_repairs": auto_repairs,
    }


def evaluate_occasional_gate(
    *,
    config_path: Path,
    config: dict[str, Any],
    agent: str,
    script_name: str,
    reason: str,
    consume: bool,
) -> dict[str, Any]:
    delivery_cfg = resolve_delivery_config(config)
    if str(delivery_cfg.get("mode") or "") != "occasional":
        return {
            "active": False,
            "allowed": True,
            "blocked": False,
            "rate_limited": False,
            "message": None,
            "retry_after_seconds": 0,
            "consumed": False,
        }

    occasional_cfg = resolve_occasional_config(config)
    normalized_reason = normalize_reason(reason)
    triggers = occasional_cfg["triggers"]
    log_path = resolve_workspace_path(
        config_path.parent,
        occasional_cfg["record_path"],
        "./occasional-limit-log.jsonl",
    )
    rows = _read_jsonl_rows(log_path)
    previous_grants = [row for row in rows if row.get("agent") == agent and row.get("event") == "granted"]

    if normalized_reason == "new" and not occasional_cfg["allow_new_send"]:
        message = "Occasional delivery is not allowed for the initial new trigger in this workspace."
        _append_occasional_row(log_path, agent=agent, script_name=script_name, reason=normalized_reason, event="blocked", message=message)
        return _build_occasional_result(message=message, rate_limited=False)

    if normalized_reason == "new" and occasional_cfg["new_send_once"] and previous_grants:
        message = "The initial occasional send has already been used for this agent."
        _append_occasional_row(log_path, agent=agent, script_name=script_name, reason=normalized_reason, event="blocked", message=message)
        return _build_occasional_result(message=message, rate_limited=False)

    if normalized_reason not in triggers:
        message = (
            "Occasional delivery was not triggered for this turn. "
            f"Allowed triggers: {', '.join(triggers)}."
        )
        _append_occasional_row(log_path, agent=agent, script_name=script_name, reason=normalized_reason, event="blocked", message=message)
        return _build_occasional_result(message=message, rate_limited=False)

    window_minutes = occasional_cfg["window_minutes"]
    max_images = occasional_cfg["max_images_per_window"]
    threshold = _utc_now() - timedelta(minutes=window_minutes)
    recent_grants = [
        row
        for row in previous_grants
        if _parse_timestamp(row.get("recorded_at")) is not None and _parse_timestamp(row.get("recorded_at")) >= threshold
    ]
    if len(recent_grants) >= max_images:
        oldest_active = min(
            _parse_timestamp(row.get("recorded_at")) for row in recent_grants if _parse_timestamp(row.get("recorded_at")) is not None
        )
        retry_at = oldest_active + timedelta(minutes=window_minutes)
        retry_after_seconds = max(1, int((retry_at - _utc_now()).total_seconds()))
        message = (
            "Occasional image generation is rate-limited for this agent. "
            f"Please wait {format_wait_duration(retry_after_seconds)} before generating another image."
        )
        _append_occasional_row(log_path, agent=agent, script_name=script_name, reason=normalized_reason, event="rate_limited", message=message)
        return {
            "active": True,
            "allowed": False,
            "blocked": True,
            "rate_limited": True,
            "message": message,
            "retry_after_seconds": retry_after_seconds,
            "consumed": False,
        }

    if consume:
        _append_occasional_row(log_path, agent=agent, script_name=script_name, reason=normalized_reason, event="granted", message=None)

    return {
        "active": True,
        "allowed": True,
        "blocked": False,
        "rate_limited": False,
        "message": None,
        "retry_after_seconds": 0,
        "consumed": consume,
    }


def normalize_reason(reason: str | None) -> str:
    if not reason:
        return "reply_time"
    return reason.strip().lower().replace(" ", "_")


def format_wait_duration(total_seconds: int) -> str:
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    if minutes and seconds:
        return f"{minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m"
    return f"{seconds}s"


def _build_occasional_result(*, message: str, rate_limited: bool) -> dict[str, Any]:
    return {
        "active": True,
        "allowed": False,
        "blocked": True,
        "rate_limited": rate_limited,
        "message": message,
        "retry_after_seconds": 0,
        "consumed": False,
    }


def _append_occasional_row(
    path: Path,
    *,
    agent: str,
    script_name: str,
    reason: str,
    event: str,
    message: str | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "agent": agent,
        "script": script_name,
        "reason": reason,
        "event": event,
        "message": message,
        "recorded_at": _utc_now().isoformat(),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _normalize_trigger_list(raw_value: Any, default: list[str]) -> list[str]:
    if not isinstance(raw_value, list):
        return default
    normalized = [normalize_reason(item) for item in raw_value if isinstance(item, str) and item.strip()]
    return normalized or default


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _build_generation_adapter_stub() -> str:
    return """from __future__ import annotations


def generate_image(request):
    return {
        "success": False,
        "error_code": "GENERATION_ADAPTER_NOT_IMPLEMENTED",
        "message": "Auto-repair created this generation adapter stub. Replace it with a real backend integration.",
        "request_summary": {
            "agent": request.get("agent"),
            "reason": request.get("reason"),
            "output_path": request.get("output_path"),
        },
    }
"""


def _build_framework_send_stub() -> str:
    return """from __future__ import annotations


def deliver_payload(payload):
    return {
        "ok": False,
        "error_code": "FRAMEWORK_SEND_NOT_IMPLEMENTED",
        "message": "Auto-repair created this framework delivery stub. Implement deliver_payload(payload) for your host framework.",
        "payload_summary": {
            "agent": payload.get("agent"),
            "image_path": payload.get("image_path"),
        },
    }
"""


def _utc_now() -> datetime:
    return datetime.now(UTC)
