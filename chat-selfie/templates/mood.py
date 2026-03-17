from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType

from delivery_common import DEFAULT_CONFIG_PATH, DIAGNOSTIC_VERSION, build_stage_result, evaluate_occasional_gate, load_config


WORKSPACE_ROOT = Path(__file__).resolve().parent
SKILL_BASE_PLACEHOLDER = "__CHAT_SELFIE_BASE_DIR__"
DEFAULT_RESOLVER_PATH = f"{SKILL_BASE_PLACEHOLDER}/tools/mood_resolver.py"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve the current mood for one Chat Selfie agent.",
    )
    parser.add_argument("--agent", required=True, help="Agent id or mapped agent name.")
    parser.add_argument("--mood", default=None, help="Optional explicit mood id.")
    parser.add_argument("--reason", default="reply_time", help="Why mood is being resolved for this turn.")
    parser.add_argument(
        "--help-moods",
        action="store_true",
        help="List all available mood ids for the given agent and exit.",
    )
    args = parser.parse_args()

    config = load_config(DEFAULT_CONFIG_PATH)
    mood_cfg = _extract_mood_config(config)
    pool_path = _resolve_workspace_path(DEFAULT_CONFIG_PATH.parent, mood_cfg.get("pool_path", "./mood-pool.json"))
    resolver_path = _resolve_workspace_path(
        DEFAULT_CONFIG_PATH.parent,
        mood_cfg.get("resolver_path", str(DEFAULT_RESOLVER_PATH)),
    )

    try:
        resolver = _load_resolver_module(resolver_path)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "status": "repair_required",
                    "mood_id": None,
                    "source": "resolver_error",
                    "allow_send_without_mood": True,
                    "stage": build_stage_result(
                        "failed",
                        attempted=True,
                        error_code="MOOD_RESOLVER_MISSING",
                        message=str(exc),
                        recoverability="degrade",
                        resolver_path=str(resolver_path),
                    ),
                    "auto_repairs": [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.help_moods:
        moods = resolver.list_agent_moods(pool_path, args.agent, DEFAULT_CONFIG_PATH)
        print(json.dumps({"agent": args.agent, "moods": moods}, ensure_ascii=False, indent=2))
        return

    occasional_gate = evaluate_occasional_gate(
        config_path=DEFAULT_CONFIG_PATH,
        config=config,
        agent=args.agent,
        script_name="mood.py",
        reason=args.reason,
        consume=True,
    )
    if not occasional_gate["allowed"]:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "status": "blocked",
                    "agent": args.agent,
                    "blocked": True,
                    "rate_limited": bool(occasional_gate["rate_limited"]),
                    "rate_limit_message": occasional_gate["message"],
                    "retry_after_seconds": occasional_gate["retry_after_seconds"],
                    "source": "occasional_limit",
                    "allow_send_without_mood": False,
                    "stage": build_stage_result(
                        "blocked",
                        attempted=True,
                        error_code="OCCASIONAL_GATE_BLOCKED",
                        message=str(occasional_gate["message"]),
                        recoverability="degrade",
                        retry_after_seconds=occasional_gate["retry_after_seconds"],
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    auto_repairs: list[dict[str, object]] = []
    try:
        result = resolver.resolve_mood(pool_path, args.agent, DEFAULT_CONFIG_PATH, mood_id=args.mood)
    except KeyError as exc:
        if args.mood:
            result = resolver.resolve_mood(pool_path, args.agent, DEFAULT_CONFIG_PATH, mood_id=None)
            auto_repairs.append(
                {
                    "action": "fallback_invalid_mood_id",
                    "applied": True,
                    "details": f"Explicit mood id was invalid and was replaced by a fallback mood: {exc}",
                }
            )
        else:
            raise
    except Exception as exc:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "status": "repair_required",
                    "mood_id": None,
                    "source": "resolver_error",
                    "allow_send_without_mood": True,
                    "stage": build_stage_result(
                        "failed",
                        attempted=True,
                        error_code="MOOD_POOL_INVALID",
                        message=str(exc),
                        recoverability="degrade",
                        pool_path=str(pool_path),
                    ),
                    "auto_repairs": auto_repairs,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    visible_result = {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ok": True,
        "status": "success",
        "mood_id": result["mood_id"],
        "mood_label": result["mood_label"],
        "reply_style_prompt": result["reply_style_prompt"],
        "state_hint": result["state_hint"],
        "camera": result["camera"],
        "expression": result["expression"],
        "scene": result["scene"],
        "action": result["action"],
        "source": result["source"],
        "rate_limited": False,
        "occasional_gate_consumed": occasional_gate["consumed"],
        "allow_send_without_mood": True,
        "stage": build_stage_result(
            "success",
            attempted=True,
            pool_path=str(pool_path),
            resolver_path=str(resolver_path),
        ),
        "auto_repairs": auto_repairs,
    }
    print(json.dumps(visible_result, ensure_ascii=False, indent=2))


def _load_resolver_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("chat_selfie_mood_resolver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load mood resolver from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _extract_mood_config(config: dict) -> dict:
    mood_cfg = config.get("mood", {})
    return mood_cfg if isinstance(mood_cfg, dict) else {}


def _resolve_workspace_path(base_dir: Path, raw_path: str) -> Path:
    if raw_path.startswith(f"{SKILL_BASE_PLACEHOLDER}/"):
        suffix = raw_path[len(SKILL_BASE_PLACEHOLDER) + 1 :]
        return (_resolve_skill_base() / suffix).resolve()
    path = Path(raw_path)
    return path if path.is_absolute() else (base_dir / path).resolve()


def _resolve_skill_base() -> Path:
    configured = os.environ.get("CHAT_SELFIE_BASE_DIR")
    if configured:
        return Path(configured).resolve()

    candidates = [
        WORKSPACE_ROOT.parent / "chat-selfie",
        WORKSPACE_ROOT.parent / "skills" / "chat-selfie",
    ]
    for candidate in candidates:
        if (candidate / "tools" / "mood_resolver.py").exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "Unable to locate Chat Selfie skill base. Set CHAT_SELFIE_BASE_DIR or update mood.resolver_path."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            json.dumps(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "status": "repair_required",
                    "allow_send_without_mood": True,
                    "stage": build_stage_result(
                        "failed",
                        attempted=False,
                        error_code="UNEXPECTED_MOOD_ERROR",
                        message=str(exc),
                        recoverability="degrade",
                    ),
                    "auto_repairs": [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
