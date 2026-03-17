from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any
from urllib import error as urlerror, request

from delivery_common import (
    DIAGNOSTIC_VERSION,
    DEFAULT_CONFIG_PATH,
    build_stage_result,
    inspect_telegram_runtime,
    load_config,
    resolve_self_repair_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send one generated Chat Selfie image and caption through Telegram Bot API.",
    )
    parser.add_argument("--image-path", required=True, help="Generated image path to send.")
    parser.add_argument("--text", required=True, help="Caption or final reply text.")
    parser.add_argument("--chat-id", default=None, help="Optional explicit Telegram chat id.")
    parser.add_argument("--reply-to-message-id", default=None, help="Optional Telegram reply target.")
    parser.add_argument("--parse-mode", default=None, help="Optional Telegram parse mode.")
    return parser


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_multipart_body(*, fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"chat-selfie-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )

    file_bytes = file_path.read_bytes()
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'.encode("utf-8"),
            b"Content-Type: application/octet-stream\r\n\r\n",
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(chunks), boundary


def send_telegram_photo(
    *,
    image_path: Path,
    text: str,
    chat_id: str,
    bot_token: str,
    api_base: str,
    reply_to_message_id: str | None,
    parse_mode: str | None,
) -> dict[str, Any]:
    fields = {
        "chat_id": chat_id,
        "caption": text,
    }
    if parse_mode:
        fields["parse_mode"] = parse_mode
    if reply_to_message_id:
        fields["reply_to_message_id"] = reply_to_message_id

    body, boundary = build_multipart_body(fields=fields, file_field="photo", file_path=image_path)
    endpoint = f"{api_base}/bot{bot_token}/sendPhoto"
    http_request = request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with request.urlopen(http_request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urlerror.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram sendPhoto failed: {detail}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Telegram sendPhoto failed: {exc.reason}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Telegram API returned a non-object response.")
    return payload


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    image_path = Path(args.image_path).resolve()
    if not image_path.exists():
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "failed",
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="TELEGRAM_IMAGE_MISSING",
                    message=f"Image path does not exist: {image_path}",
                    recoverability="repair_setup",
                    image_path=str(image_path),
                ),
                "user_action_required": [],
                "auto_repairs": [],
            }
        )
        return

    config = load_config(DEFAULT_CONFIG_PATH)
    repair_cfg = resolve_self_repair_config(config)
    runtime = inspect_telegram_runtime(
        config,
        explicit_chat_id=args.chat_id,
        explicit_reply_to_message_id=args.reply_to_message_id,
        explicit_parse_mode=args.parse_mode,
    )

    if not runtime["chat_id"]:
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "repair_required",
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="TELEGRAM_CHAT_ID_MISSING",
                    message="Telegram chat id is missing. Configure delivery.telegram.chat_id or its env source.",
                    recoverability="user_action",
                ),
                "user_action_required": [
                    {
                        "code": "SET_TELEGRAM_CHAT_ID",
                        "message": "Configure delivery.telegram.chat_id or its env source before Telegram delivery can succeed.",
                    }
                ],
                "auto_repairs": [],
            }
        )
        return
    if not runtime["bot_token"]:
        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "repair_required",
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="TELEGRAM_BOT_TOKEN_MISSING",
                    message="Telegram bot token is missing. Configure delivery.telegram.bot_token_env.",
                    recoverability="user_action",
                ),
                "user_action_required": [
                    {
                        "code": "SET_TELEGRAM_BOT_TOKEN",
                        "message": "Configure delivery.telegram.bot_token_env before Telegram delivery can succeed.",
                    }
                ],
                "auto_repairs": [],
            }
        )
        return

    auto_repairs: list[dict[str, Any]] = []
    attempt_parse_modes: list[str | None] = [str(runtime["parse_mode"]) if runtime["parse_mode"] else None]
    if attempt_parse_modes[0] is not None:
        attempt_parse_modes.append(None)
    max_attempts = max(1, int(repair_cfg["max_retry_attempts"]))
    last_error: RuntimeError | None = None
    response: dict[str, Any] | None = None
    used_parse_mode = attempt_parse_modes[0]

    for attempt_index in range(max_attempts):
        parse_mode = attempt_parse_modes[min(attempt_index, len(attempt_parse_modes) - 1)]
        try:
            response = send_telegram_photo(
                image_path=image_path,
                text=args.text,
                chat_id=str(runtime["chat_id"]),
                bot_token=str(runtime["bot_token"]),
                api_base=str(runtime["api_base"]),
                reply_to_message_id=runtime["reply_to_message_id"],
                parse_mode=parse_mode,
            )
            used_parse_mode = parse_mode
            if attempt_index > 0 and parse_mode is None:
                auto_repairs.append(
                    {
                        "action": "retry_without_parse_mode",
                        "applied": True,
                        "details": "Telegram send succeeded after removing parse_mode.",
                    }
                )
            break
        except RuntimeError as exc:
            last_error = exc
            if "can't parse entities" in str(exc).lower() and parse_mode is not None:
                continue
            if attempt_index + 1 >= max_attempts:
                break

    if response is None:
        error_message = str(last_error) if last_error else "Telegram delivery failed."
        error_code = "TELEGRAM_SEND_FAILED"
        recoverability = "auto_repair"
        if "failed: <urlopen error" in error_message.lower() or "timed out" in error_message.lower():
            error_code = "TELEGRAM_NETWORK_ERROR"
        elif "can't parse entities" in error_message.lower():
            error_code = "TELEGRAM_PARSE_MODE_REJECTED"
        elif "bot token" in error_message.lower():
            error_code = "TELEGRAM_BOT_TOKEN_MISSING"
            recoverability = "user_action"

        _emit(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "ok": False,
                "final_state": "failed" if recoverability != "user_action" else "repair_required",
                "stage": build_stage_result(
                    "failed",
                    attempted=True,
                    error_code=error_code,
                    message=error_message,
                    recoverability=recoverability,
                    image_path=str(image_path),
                    chat_id=str(runtime["chat_id"]),
                ),
                "chat_id": runtime["chat_id"],
                "image_path": str(image_path),
                "reply_to_message_id": runtime["reply_to_message_id"],
                "parse_mode": runtime["parse_mode"],
                "user_action_required": (
                    [
                        {
                            "code": "SET_TELEGRAM_BOT_TOKEN",
                            "message": "Configure delivery.telegram.bot_token_env before Telegram delivery can succeed.",
                        }
                    ]
                    if error_code == "TELEGRAM_BOT_TOKEN_MISSING"
                    else []
                ),
                "auto_repairs": auto_repairs,
            }
        )
        return

    _emit(
        {
            "diagnostic_version": DIAGNOSTIC_VERSION,
            "ok": bool(response.get("ok")),
            "final_state": "success" if bool(response.get("ok")) else "failed",
            "stage": build_stage_result(
                "success" if bool(response.get("ok")) else "failed",
                attempted=True,
                error_code=None if bool(response.get("ok")) else "TELEGRAM_API_REJECTED",
                message=None if bool(response.get("ok")) else "Telegram API returned ok=false.",
                recoverability=None if bool(response.get("ok")) else "repair_setup",
                image_path=str(image_path),
                chat_id=str(runtime["chat_id"]),
            ),
            "chat_id": runtime["chat_id"],
            "image_path": str(image_path),
            "reply_to_message_id": runtime["reply_to_message_id"],
            "parse_mode": used_parse_mode,
            "response": response,
            "auto_repairs": auto_repairs,
            "user_action_required": [],
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
                "stage": build_stage_result(
                    "failed",
                    attempted=False,
                    error_code="UNEXPECTED_TELEGRAM_ERROR",
                    message=str(exc),
                    recoverability="repair_setup",
                ),
                "auto_repairs": [],
                "user_action_required": [],
            }
        )
