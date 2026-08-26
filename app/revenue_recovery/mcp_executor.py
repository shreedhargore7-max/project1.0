# ============================================================
# REVENUE RECOVERY - RAZORPAY MCP EXECUTOR
# ============================================================

from typing import Any

from app.agent.mcp_tools import (
    mcp_razorpay_create_payment_link,
)


# ============================================================
# ACTIONS
# ============================================================

ACTION_CREATE_PAYMENT_LINK = (
    "CREATE_PAYMENT_LINK"
)


# ============================================================
# ALLOWED ACTIONS
# ============================================================

ALLOWED_MCP_ACTIONS = {
    ACTION_CREATE_PAYMENT_LINK,
}


# ============================================================
# EXECUTE APPROVED ACTION
# ============================================================

def execute_approved_action(
    *,
    payment: dict,
    action: str,
    dry_run: bool = True,
) -> dict:

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if action not in ALLOWED_MCP_ACTIONS:

        return {
            "success": False,
            "executed": False,
            "mode": "blocked",
            "reason": (
                "This MCP recovery action is not "
                "allowed by policy."
            ),
        }

    amount = payment.get(
        "amount"
    )

    currency = payment.get(
        "currency",
        "INR"
    )

    payment_id = payment.get(
        "payment_id"
    )

    if amount is None:

        return {
            "success": False,
            "executed": False,
            "mode": "blocked",
            "reason": (
                "Payment amount is required."
            ),
        }

    if not payment_id:

        return {
            "success": False,
            "executed": False,
            "mode": "blocked",
            "reason": (
                "Payment ID is required."
            ),
        }

    try:

        amount = int(
            float(amount)
        )

    except (
        TypeError,
        ValueError,
    ):

        return {
            "success": False,
            "executed": False,
            "mode": "blocked",
            "reason": (
                "Payment amount must be numeric."
            ),
        }

    if amount <= 0:

        return {
            "success": False,
            "executed": False,
            "mode": "blocked",
            "reason": (
                "Payment amount must be greater than zero."
            ),
        }

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if dry_run:

        return {
            "success": True,
            "executed": False,
            "mode": "dry_run",
            "action": action,
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "description": (
                "Revenue recovery payment link "
                f"for {payment_id}"
            ),
        }

    # --------------------------------------------------------
    # REAL MCP EXECUTION
    # --------------------------------------------------------

    try:

        result = (
            mcp_razorpay_create_payment_link(
                amount=amount,
                description=(
                    "Revenue recovery payment link "
                    f"for {payment_id}"
                ),
                currency=currency,
                reference_id=payment_id,
            )
        )

        return {
            "success": True,
            "executed": True,
            "mode": "live",
            "action": action,
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "result": result,
        }

    except Exception as error:

        return {
            "success": False,
            "executed": False,
            "mode": "live",
            "action": action,
            "payment_id": payment_id,
            "reason": (
                f"MCP execution failed: {error}"
            ),
        }


# ============================================================
# WORKFLOW EXECUTOR ADAPTER
# ============================================================

def recovery_executor(
    *,
    payment: dict,
    action: str,
    dry_run: bool = True,
) -> dict:
    """
    Adapter used by recovery_workflow.execute_recovery().
    """

    # --------------------------------------------------------
    # MAP DECISION ACTION
    # --------------------------------------------------------

    if action in {
        "RECOVERY_REVIEW",
        "MANUAL_REVIEW",
    }:

        return execute_approved_action(
            payment=payment,
            action=ACTION_CREATE_PAYMENT_LINK,
            dry_run=dry_run,
        )

    return {
        "success": False,
        "executed": False,
        "mode": "blocked",
        "reason": (
            "No MCP recovery operation is mapped "
            "to this decision."
        ),
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ACTION_CREATE_PAYMENT_LINK",
    "ALLOWED_MCP_ACTIONS",
    "execute_approved_action",
    "recovery_executor",
]