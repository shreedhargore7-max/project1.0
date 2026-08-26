# ============================================================
# REVENUE RECOVERY - AUDIT
# ============================================================

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

AUDIT_DIR = PROJECT_ROOT / "logs"

AUDIT_FILE = (
    AUDIT_DIR
    / "recovery_audit.jsonl"
)


def create_audit_event(
    *,
    event_type: str,
    payment_id: str | None = None,
    action: str | None = None,
    status: str | None = None,
    amount: Any = None,
    details: str = "",
) -> dict:

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "event_type": event_type,

        "payment_id": payment_id,

        "action": action,

        "status": status,

        "amount": amount,

        "details": details,
    }


def write_audit_event(
    event: dict,
) -> bool:

    try:

        AUDIT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with AUDIT_FILE.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False,
                )
            )

            file.write("\n")

        return True

    except Exception:
        return False


def record_recovery_event(
    *,
    event_type: str,
    payment_id: str | None = None,
    action: str | None = None,
    status: str | None = None,
    amount: Any = None,
    details: str = "",
) -> dict:

    event = create_audit_event(
        event_type=event_type,
        payment_id=payment_id,
        action=action,
        status=status,
        amount=amount,
        details=details,
    )

    write_audit_event(
        event
    )

    return event


__all__ = [
    "AUDIT_FILE",
    "create_audit_event",
    "write_audit_event",
    "record_recovery_event",
]