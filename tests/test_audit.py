import json

from app.revenue_recovery.audit import (
    create_audit_event,
    write_audit_event,
)


def test_create_audit_event():

    event = create_audit_event(
        event_type="RECOVERY_APPROVED",
        payment_id="pay_AUDIT001",
        action="CREATE_PAYMENT_LINK",
        status="APPROVED",
        amount=5000,
        details="User approved recovery",
    )

    assert (
        event["event_type"]
        == "RECOVERY_APPROVED"
    )

    assert (
        event["payment_id"]
        == "pay_AUDIT001"
    )

    assert (
        event["action"]
        == "CREATE_PAYMENT_LINK"
    )

    assert (
        event["status"]
        == "APPROVED"
    )

    assert event["amount"] == 5000

    assert event["timestamp"]


def test_write_audit_event(tmp_path):

    import app.revenue_recovery.audit as audit

    original_file = audit.AUDIT_FILE

    audit.AUDIT_FILE = (
        tmp_path
        / "recovery_audit.jsonl"
    )

    try:

        event = create_audit_event(
            event_type="RECOVERY_REJECTED",
            payment_id="pay_AUDIT002",
            action="CREATE_PAYMENT_LINK",
            status="REJECTED",
            amount=2000,
        )

        result = write_audit_event(
            event
        )

        assert result is True

        assert audit.AUDIT_FILE.exists()

        lines = (
            audit.AUDIT_FILE
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )

        assert len(lines) == 1

        saved = json.loads(
            lines[0]
        )

        assert (
            saved["payment_id"]
            == "pay_AUDIT002"
        )

    finally:

        audit.AUDIT_FILE = (
            original_file
        )