from __future__ import annotations

# Author: Zhihao Kang

import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_REUSE_HOURS = 4


def resolve_mood(
    mood_pool_path: str | Path,
    agent_id: str,
    chat_selfie_config_path: str | Path,
    mood_id: str | None = None,
) -> dict[str, Any]:
    pool_path = Path(mood_pool_path)
    config_path = Path(chat_selfie_config_path)
    pool = _load_json(pool_path)
    config = _load_json(config_path)
    mood_cfg = _extract_mood_config(config)

    agent_key, agent_entry = _resolve_agent_entry(pool, mood_cfg, agent_id)
    reuse_hours = _coerce_reuse_hours(mood_cfg.get("reuse_hours", DEFAULT_REUSE_HOURS))
    log_path = _resolve_workspace_path(config_path.parent, mood_cfg.get("record_path", "./mood-log.jsonl"))
    generate_prompt_parts = bool(mood_cfg.get("generate_prompt_parts", True))

    if mood_id:
        resolved_mood_id = _resolve_mood_id(agent_entry, mood_id)
        source = "explicit"
        should_record = True
    else:
        recent_record = _read_recent_record(log_path, agent_key, reuse_hours)
        if recent_record is not None:
            resolved_mood_id = recent_record["mood_id"]
            source = "recent"
            should_record = False
        else:
            resolved_mood_id = _choose_random_mood(agent_entry)
            source = "random"
            should_record = True

    mood_entry = agent_entry["moods"][resolved_mood_id]
    prompt_parts = _materialize_prompt_parts(mood_entry, generate_prompt_parts)
    resolved_at = _utc_now().isoformat()

    result = {
        "agent": agent_key,
        "requested_agent": agent_id,
        "mood_id": resolved_mood_id,
        "mood_label": mood_entry.get("label", resolved_mood_id),
        "reply_style_prompt": mood_entry.get("reply_style_prompt", ""),
        "state_hint": mood_entry.get("state_hint") or mood_entry.get("reply_style_prompt", ""),
        "camera": prompt_parts["camera"],
        "expression": prompt_parts["expression"],
        "scene": prompt_parts["scene"],
        "action": prompt_parts["action"],
        "prompt_parts": prompt_parts,
        "source": source,
        "resolved_at": resolved_at,
        "record_path": str(log_path),
    }

    if should_record:
        _append_jsonl(
            log_path,
            {
                "agent": agent_key,
                "requested_agent": agent_id,
                "mood_id": resolved_mood_id,
                "source": source,
                "recorded_at": resolved_at,
            },
        )
        result["record_written"] = True
    else:
        result["record_written"] = False

    return result


def list_agent_moods(
    mood_pool_path: str | Path,
    agent_id: str,
    chat_selfie_config_path: str | Path | None = None,
) -> list[dict[str, str]]:
    pool = _load_json(Path(mood_pool_path))
    mood_cfg = _extract_mood_config(_load_json(Path(chat_selfie_config_path))) if chat_selfie_config_path else {}
    _, agent_entry = _resolve_agent_entry(pool, mood_cfg, agent_id)
    return [
        {
            "mood_id": mood_key,
            "label": mood_value.get("label", mood_key),
        }
        for mood_key, mood_value in sorted(agent_entry["moods"].items())
    ]


def _extract_mood_config(config: dict[str, Any]) -> dict[str, Any]:
    mood_cfg = config.get("mood", {})
    return mood_cfg if isinstance(mood_cfg, dict) else {}


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected top-level object in {path}")
    return loaded


def _resolve_agent_entry(
    pool: dict[str, Any],
    mood_cfg: dict[str, Any],
    requested_agent: str,
) -> tuple[str, dict[str, Any]]:
    agents = pool.get("agents")
    if not isinstance(agents, dict) or not agents:
        raise ValueError("Mood pool must define a non-empty 'agents' object.")

    normalized_requested = _normalize_key(requested_agent)
    mapped_agent = mood_cfg.get("agent_mappings", {}).get(normalized_requested, normalized_requested)
    normalized_mapped = _normalize_key(mapped_agent)

    if normalized_mapped in agents:
        return normalized_mapped, _validate_agent_entry(agents[normalized_mapped], normalized_mapped)

    for agent_key, raw_entry in agents.items():
        entry = _validate_agent_entry(raw_entry, agent_key)
        aliases = {_normalize_key(alias) for alias in entry.get("aliases", []) if isinstance(alias, str)}
        if normalized_requested in aliases or normalized_mapped in aliases:
            return agent_key, entry

    raise KeyError(f"Unknown agent id for mood resolution: {requested_agent}")


def _validate_agent_entry(raw_entry: Any, agent_key: str) -> dict[str, Any]:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"Agent entry for {agent_key} must be an object.")
    moods = raw_entry.get("moods")
    if not isinstance(moods, dict) or not moods:
        raise ValueError(f"Agent entry for {agent_key} must define a non-empty 'moods' object.")
    return raw_entry


def _resolve_mood_id(agent_entry: dict[str, Any], requested_mood_id: str) -> str:
    normalized_requested = _normalize_key(requested_mood_id)
    if normalized_requested in agent_entry["moods"]:
        return normalized_requested

    for mood_key, raw_mood in agent_entry["moods"].items():
        if not isinstance(raw_mood, dict):
            continue
        aliases = {_normalize_key(alias) for alias in raw_mood.get("aliases", []) if isinstance(alias, str)}
        if normalized_requested in aliases:
            return mood_key

    raise KeyError(f"Unknown mood id: {requested_mood_id}")


def _choose_random_mood(agent_entry: dict[str, Any]) -> str:
    candidate_ids = agent_entry.get("random_pool")
    if not isinstance(candidate_ids, list) or not candidate_ids:
        candidate_ids = list(agent_entry["moods"].keys())

    valid_candidates = [mood_id for mood_id in candidate_ids if mood_id in agent_entry["moods"]]
    if not valid_candidates:
        raise ValueError("Mood pool does not contain any valid random candidates.")
    return random.choice(valid_candidates)


def _materialize_prompt_parts(mood_entry: dict[str, Any], enabled: bool) -> dict[str, str | None]:
    if not enabled:
        return {
            "camera": None,
            "expression": None,
            "scene": None,
            "action": None,
        }

    prompt_parts = mood_entry.get("prompt_parts", {})
    if not isinstance(prompt_parts, dict):
        prompt_parts = {}

    return {
        "camera": _pick_prompt(prompt_parts.get("camera")),
        "expression": _pick_prompt(prompt_parts.get("expression")),
        "scene": _pick_prompt(prompt_parts.get("scene")),
        "action": _pick_prompt(prompt_parts.get("action")),
    }


def _pick_prompt(raw_values: Any) -> str | None:
    if not isinstance(raw_values, list):
        return None
    values = [value for value in raw_values if isinstance(value, str) and value.strip()]
    if not values:
        return None
    return random.choice(values)


def _read_recent_record(log_path: Path, agent_key: str, reuse_hours: int) -> dict[str, Any] | None:
    if not log_path.exists():
        return None

    threshold = _utc_now() - timedelta(hours=reuse_hours)
    rows = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)

    for row in reversed(rows):
        if row.get("agent") != agent_key:
            continue
        recorded_at = _parse_timestamp(row.get("recorded_at"))
        if recorded_at is None or recorded_at < threshold:
            continue
        mood_id = row.get("mood_id")
        if isinstance(mood_id, str) and mood_id:
            return row
    return None


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _resolve_workspace_path(base_dir: Path, raw_path: Any) -> Path:
    if isinstance(raw_path, str) and raw_path.strip():
        path = Path(raw_path)
        return path if path.is_absolute() else (base_dir / path).resolve()
    return (base_dir / "mood-log.jsonl").resolve()


def _coerce_reuse_hours(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return DEFAULT_REUSE_HOURS
    return parsed if parsed > 0 else DEFAULT_REUSE_HOURS


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _utc_now() -> datetime:
    return datetime.now(UTC)
