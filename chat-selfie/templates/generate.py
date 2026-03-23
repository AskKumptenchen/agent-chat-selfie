from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from delivery_common import (
    DIAGNOSTIC_VERSION,
    DEFAULT_CONFIG_PATH,
    assess_generation_result,
    build_generation_request,
    build_stage_result,
    call_first_available,
    load_config,
    load_module_from_path,
    maybe_rebuild_generation_adapter,
    resolve_generation_config,
    resolve_selfies_dir,
    resolve_self_repair_config,
    resolve_workspace_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate one Chat Selfie image using the configured workspace route.",
    )
    parser.add_argument("--agent", required=True, help="Target agent id.")
    parser.add_argument("--text", required=True, help="Final reply text or caption context.")
    parser.add_argument("--reason", default="reply_time", help="Why this image is being generated.")
    parser.add_argument("--mood", default=None, help="Optional explicit mood id.")
    parser.add_argument("--mood-payload", default=None, help="Optional JSON string containing resolved mood data.")
    return parser


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _emit_generation_result(
    *,
    desired_output_path: Path,
    generation_cfg: dict[str, Any],
    route_type: str,
    stage: dict[str, Any],
    normalized: dict[str, Any],
    auto_repairs: list[dict[str, Any]],
    user_action_required: list[dict[str, Any]],
    image_source_mode: str,
) -> None:
    final_state = "success"
    if stage["status"] == "pending":
        final_state = "handoff_pending"
    elif stage["status"] != "success":
        final_state = "failed"
    _emit(
        {
            "diagnostic_version": DIAGNOSTIC_VERSION,
            "ok": final_state == "success",
            "final_state": final_state,
            "handoff_required": bool(normalized.get("handoff_required")),
            "route_type": route_type,
            "image_path": normalized.get("image_path"),
            "desired_output_path": str(desired_output_path),
            "revised_prompt_summary": normalized.get("revised_prompt_summary"),
            "debug_notes": normalized.get("debug_notes"),
            "generation_method": generation_cfg.get("method"),
            "generation_provider": generation_cfg.get("provider"),
            "image_source_mode": image_source_mode,
            "stage": stage,
            "auto_repairs": auto_repairs,
            "user_action_required": user_action_required,
            "raw_result": normalized,
        }
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config_path = DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    generation_cfg = resolve_generation_config(config)

    mood_payload = json.loads(args.mood_payload) if args.mood_payload else None
    if mood_payload is not None and not isinstance(mood_payload, dict):
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "failed",
                "route_type": "adapter",
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="INVALID_MOOD_PAYLOAD",
                    message="--mood-payload must be a JSON object",
                    recoverability="repair_setup",
                ),
            }
        )
        return

    request = build_generation_request(
        config_path=config_path,
        config=config,
        agent=args.agent,
        final_text=args.text,
        mood_data=mood_payload,
        explicit_mood_id=args.mood,
        reason=args.reason,
    )

    desired_output_path = Path(request["output_path"])
    adapter_path = resolve_workspace_path(
        config_path.parent,
        generation_cfg.get("adapter_path"),
        "./adapters/generation/generate_adapter.py",
    )
    auto_repairs: list[dict[str, Any]] = []
    user_action_required: list[dict[str, Any]] = []
    self_repair_cfg = resolve_self_repair_config(config)
    image_source_mode = str(request.get("image_source_mode") or "generate")

    if image_source_mode == "mood_asset":
        raw_asset_path = request.get("mood_asset_path")
        if isinstance(raw_asset_path, str) and raw_asset_path.strip():
            assessed = assess_generation_result(
                config_path=config_path,
                config=config,
                result={
                    "ok": True,
                    "success": True,
                    "image_path": str(resolve_workspace_path(config_path.parent, raw_asset_path)),
                    "preserve_image_path": True,
                    "source_mode": "mood_asset",
                    "mood_id": request.get("mood_id"),
                },
                desired_output_path=desired_output_path,
            )
            auto_repairs.extend(assessed["auto_repairs"])
            normalized = assessed["result"]
            normalized["image_source_mode"] = image_source_mode
            stage = assessed["stage"]
            _emit_generation_result(
                desired_output_path=desired_output_path,
                generation_cfg=generation_cfg,
                route_type="mood_asset",
                stage=stage,
                normalized=normalized,
                auto_repairs=auto_repairs,
                user_action_required=user_action_required,
                image_source_mode=image_source_mode,
            )
            return

        if not bool(request.get("fallback_to_generation")):
            _emit(
                {
                    "diagnostic_version": DIAGNOSTIC_VERSION,
                    "ok": False,
                    "final_state": "failed",
                    "handoff_required": False,
                    "route_type": "mood_asset",
                    "image_path": None,
                    "desired_output_path": str(desired_output_path),
                    "generation_method": generation_cfg.get("method"),
                    "generation_provider": generation_cfg.get("provider"),
                    "image_source_mode": image_source_mode,
                    "stage": build_stage_result(
                        "failed",
                        attempted=True,
                        error_code="MOOD_ASSET_PATH_MISSING",
                        message=(
                            "Mood asset mode is enabled, but the resolved mood does not provide an asset_path. "
                            "Add an asset_path to the current mood entry or enable fallback_to_generation."
                        ),
                        recoverability="repair_setup",
                    ),
                    "auto_repairs": auto_repairs,
                    "user_action_required": [
                        {
                            "code": "ADD_MOOD_ASSET_PATH",
                            "message": "Add asset_path to the relevant mood entry in mood-pool.json for mood asset delivery.",
                        }
                    ],
                }
            )
            return

    if adapter_path.exists():
        try:
            module = load_module_from_path(adapter_path)
            result = call_first_available(
                module,
                ("generate_image", "run_generation", "generate"),
                request,
            )
            if not isinstance(result, dict):
                raise RuntimeError("Generation adapter must return a JSON-like object.")
        except Exception as exc:
            result = {
                "success": False,
                "error_code": "GENERATION_ADAPTER_CONTRACT_INVALID",
                "message": str(exc),
            }

        assessed = assess_generation_result(
            config_path=config_path,
            config=config,
            result=result,
            desired_output_path=desired_output_path,
        )
        auto_repairs.extend(assessed["auto_repairs"])
        normalized = assessed["result"]
        normalized["image_source_mode"] = image_source_mode
        stage = assessed["stage"]
        _emit_generation_result(
            desired_output_path=desired_output_path,
            generation_cfg=generation_cfg,
            route_type="adapter",
            stage=stage,
            normalized=normalized,
            auto_repairs=auto_repairs,
            user_action_required=user_action_required,
            image_source_mode=image_source_mode,
        )
        return

    maybe_rebuild_generation_adapter(
        config_path=config_path,
        config=config,
        adapter_path=adapter_path,
        auto_repairs=auto_repairs,
    )
    if adapter_path.exists():
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "repair_required",
                "handoff_required": False,
                "route_type": "adapter",
                "image_path": None,
                "desired_output_path": str(desired_output_path),
                "generation_method": generation_cfg.get("method"),
                "generation_provider": generation_cfg.get("provider"),
                "image_source_mode": image_source_mode,
                "stage": build_stage_result(
                    "failed",
                    attempted=True,
                    error_code="GENERATION_ADAPTER_REBUILT",
                    message=(
                        "The configured generation adapter was missing. "
                        "A minimal stub was rebuilt, but a real generation backend is still required."
                    ),
                    recoverability="repair_setup",
                    adapter_path=str(adapter_path),
                ),
                "auto_repairs": auto_repairs,
                "user_action_required": [
                    {
                        "code": "IMPLEMENT_GENERATION_ADAPTER",
                        "message": "Replace the rebuilt generation adapter stub with a real backend integration.",
                        "path": str(adapter_path),
                    }
                ],
                "raw_result": {
                    "success": False,
                    "error_code": "GENERATION_ADAPTER_REBUILT",
                },
            }
        )
        return

    if generation_cfg.get("method") == "system_existing":
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "handoff_pending",
                "handoff_required": True,
                "route_type": "system_existing",
                "generation_method": generation_cfg.get("method"),
                "generation_provider": generation_cfg.get("provider"),
                "image_source_mode": image_source_mode,
                "desired_output_path": str(desired_output_path),
                "request": request,
                "stage": build_stage_result(
                    "pending",
                    attempted=True,
                    error_code="GENERATION_HANDOFF_REQUIRED",
                    message="Use the current agent's existing image capability and confirm the saved image path before delivery.",
                    recoverability="degrade",
                    desired_output_path=str(desired_output_path),
                ),
                "auto_repairs": auto_repairs,
                "user_action_required": [],
                "instructions": (
                    "Use the current agent's existing image capability, then save the generated image to "
                    f"{desired_output_path} before delivery."
                ),
            }
        )
        return

    selfies_dir = resolve_selfies_dir(config_path, config)
    if self_repair_cfg.get("allow_text_only_degrade"):
        user_action_required.append(
            {
                "code": "CONFIGURE_GENERATION_ROUTE",
                "message": (
                    "Provide a generation adapter or switch generation.method to a route the current agent can satisfy."
                ),
                "path": str(adapter_path),
            }
        )
    _emit(
        {
            "diagnostic_version": DIAGNOSTIC_VERSION,
            "ok": False,
            "final_state": "repair_required",
            "handoff_required": False,
            "route_type": "adapter",
            "image_path": None,
            "desired_output_path": str(desired_output_path),
            "generation_method": generation_cfg.get("method"),
            "generation_provider": generation_cfg.get("provider"),
            "image_source_mode": image_source_mode,
            "stage": build_stage_result(
                "failed",
                attempted=True,
                error_code="GENERATION_ROUTE_MISSING",
                message=(
                    "No usable generation route is configured. Provide a generation adapter at "
                    f"{adapter_path} or switch generation.method to a supported route. "
                    f"When generation is enabled, images should be saved under {selfies_dir}."
                ),
                recoverability="repair_setup",
                adapter_path=str(adapter_path),
            ),
            "auto_repairs": auto_repairs,
            "user_action_required": user_action_required,
        }
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "failed",
                "route_type": "adapter",
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="UNEXPECTED_GENERATION_ERROR",
                    message=str(exc),
                    recoverability="repair_setup",
                ),
            }
        )
