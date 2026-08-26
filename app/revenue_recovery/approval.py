# ============================================================
# REVENUE RECOVERY - APPROVAL ENGINE
# ============================================================

from typing import Any


APPROVAL_APPROVED = "APPROVED"
APPROVAL_REJECTED = "REJECTED"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
APPROVAL_BLOCKED = "BLOCKED"


def build_approval_request(
    payment: dict,
    decision: dict,
) -> dict:

    return {
        "payment_id": payment.get(
            "payment_id"
        ),
        "amount": payment.get(
            "amount",
            0,
        ),
        "currency": payment.get(
            "currency",
            "INR",
        ),
        "action": decision.get(
            "action",
        ),
        "priority": decision.get(
            "priority",
            "LOW",
        ),
        "reason": decision.get(
            "reason",
            "",
        ),
        "requires_approval": bool(
            decision.get(
                "requires_approval",
                False,
            )
        ),
        "status": (
            APPROVAL_REQUIRED
            if decision.get(
                "requires_approval",
                False,
            )
            else APPROVAL_BLOCKED
        ),
    }


def approve_recovery(
    approval_request: dict,
    approved: bool,
) -> dict:

    request = dict(
        approval_request
    )

    if not request.get(
        "requires_approval",
        False,
    ):

        request["status"] = (
            APPROVAL_BLOCKED
        )

        request["approved"] = False

        request["approval_reason"] = (
            "This action cannot be approved "
            "through the recovery approval flow."
        )

        return request

    if approved:

        request["status"] = (
            APPROVAL_APPROVED
        )

        request["approved"] = True

        request["approval_reason"] = (
            "User explicitly approved the "
            "recovery action."
        )

    else:

        request["status"] = (
            APPROVAL_REJECTED
        )

        request["approved"] = False

        request["approval_reason"] = (
            "User rejected the recovery action."
        )

    return request


def can_execute_recovery(
    approval_request: dict,
) -> bool:

    return (
        approval_request.get(
            "status"
        )
        == APPROVAL_APPROVED
        and approval_request.get(
            "approved"
        )
        is True
    )


__all__ = [
    "APPROVAL_APPROVED",
    "APPROVAL_REJECTED",
    "APPROVAL_REQUIRED",
    "APPROVAL_BLOCKED",
    "build_approval_request",
    "approve_recovery",
    "can_execute_recovery",
]