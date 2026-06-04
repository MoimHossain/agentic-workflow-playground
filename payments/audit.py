"""Append-only audit sink shim (demo only)."""
from __future__ import annotations

import json
import time
from pathlib import Path

_AUDIT_FILE = Path("/var/log/audit/payments.log")


def emit(event_name: str, actor: str, target: str, outcome: str) -> None:
    record = {
        "ts": time.time(),
        "event": event_name,
        "actor": actor,
        "target": target,
        "outcome": outcome,
    }
    try:
        _AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _AUDIT_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except PermissionError:
        pass
