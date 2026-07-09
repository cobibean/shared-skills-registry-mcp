from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_KEY_PARTS = (
    "token",
    "secret",
    "private_key",
    "password",
    "authorization",
    "signature",
    "oauth",
    "refresh",
    "api_key",
    "cookie",
)
MAX_TEXT = 2000
MAX_RECORD_BYTES = 20000
# Bundle payloads never belong in the audit log; summaries carry counts/paths only.
_DROPPED_VALUE_KEYS = {"content", "files"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_audit_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            key = str(k)
            if any(part in key.lower() for part in SECRET_KEY_PARTS):
                out[key] = "[REDACTED]"
            elif key in _DROPPED_VALUE_KEYS:
                out[key] = "[OMITTED]"
            else:
                out[key] = redact_audit_value(v)
        return out
    if isinstance(value, (list, tuple)):
        return [redact_audit_value(v) for v in value]
    if isinstance(value, str):
        lower = value.lower()
        if any(marker in lower for marker in ("authorization:", "bearer ", "private key", "refresh_token=", "token=", "api_key=")):
            return "[REDACTED]"
        return value[:MAX_TEXT]
    return value


class AuditLog:
    """Narrow SSR activity log: one JSON object per line, redacted arguments,
    result summaries only — never bundle content or secrets."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()

    def record_event(
        self,
        *,
        event_type: str,
        tool_name: str | None = None,
        arguments: dict[str, Any] | None = None,
        result_summary: dict[str, Any] | None = None,
        status: str = "ok",
        error_class: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        record = {
            "created_at": utc_now(),
            "event_type": event_type,
            "tool_name": tool_name,
            "arguments": redact_audit_value(arguments or {}),
            "result_summary": redact_audit_value(result_summary or {}),
            "status": status,
            "error_class": error_class,
            "latency_ms": latency_ms,
        }
        line = json.dumps(record, sort_keys=True, default=str, separators=(",", ":"))[:MAX_RECORD_BYTES]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def record_tool_call(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        result_summary: dict[str, Any] | None = None,
        status: str,
        error_class: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        self.record_event(
            event_type="tool_call",
            tool_name=tool_name,
            arguments=arguments,
            result_summary=result_summary,
            status=status,
            error_class=error_class,
            latency_ms=latency_ms,
        )

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events[-limit:][::-1]
