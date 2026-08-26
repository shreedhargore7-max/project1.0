# ============================================================
# REVENUE RECOVERY - END TO END WORKFLOW
# ============================================================

from typing import Any, Callable

from app.revenue_recovery.agent_node import (
    analyze_revenue_recovery,
)

from app.revenue_recovery.approval import (
    build_approval_request,
    approve_recovery,
    can_execute_recovery,
)

from app.revenue_recovery.audit import (
    record_recovery_event,
)

from app.revenue_recovery.mcp_executor import (
    recovery_executor,
)


# ============================================================
# END-TO-END ANALYSIS
# ============================================================

def analyze_recovery_request(
    payments: list[dict],
) -> dict:
    """
    Analyze payment data and return prioritized
    recovery opportunities.
    """

    analysis = analyze_revenue_recovery(
        payments
    )

    return analysis


# ============================================================
# SELECT TOP OPPORTUNITY
# ============================================================

def select_top_opportunity(
    analysis: dict,
) -> dict | None:

    prioritized = analysis.get(
        "prioritized_decisions",
        []
    )

    if not prioritized:
        return None

    return prioritized[0]


# ============================================================
# BUILD APPROVAL REQUEST
# ============================================================

def build_top_approval_request(
    payments: list[dict],
    analysis: dict,
) -> dict | None:

    opportunity = select_top_opportunity(
        analysis
    )

    if not opportunity:
        return None

    payment_id = opportunity.get(
        "payment_id"
    )

    payment = next(
        (
            item
            for item in payments
            if item.get("payment_id")
            == payment_id
        ),
        None,
    )

    if payment is None:
        return None

    return build_approval_request(
        payment=payment,
        decision=opportunity,
    )


# ============================================================
# APPROVAL
# ============================================================

def process_approval(
    approval_request: dict,
    approved: bool,
) -> dict:

    result = approve_recovery(
        approval_request,
        approved=approved,
    )

    event_type = (
        "RECOVERY_APPROVED"
        if approved
        else "RECOVERY_REJECTED"
    )

    record_recovery_event(
        event_type=event_type,
        payment_id=result.get(
            "payment_id"
        ),
        action=result.get(
            "action"
        ),
        status=result.get(
            "status"
        ),
        amount=result.get(
            "amount"
        ),
        details=result.get(
            "approval_reason",
            ""
        ),
    )

    return result


# ============================================================
# EXECUTION
# ============================================================

def execute_approved_recovery(
    approval_result: dict,
    payment: dict,
    *,
    dry_run: bool = True,
    executor: Callable[..., Any] | None = None,
) -> dict:

    if not can_execute_recovery(
        approval_result
    ):

        return {
            "success": False,
            "executed": False,
            "status": "BLOCKED",
            "reason": (
                "Recovery has not been approved."
            ),
        }

    # --------------------------------------------------------
    # Use injected executor when supplied
    # --------------------------------------------------------

    if executor is not None:

        execution = executor(
            payment=payment,
            action=approval_result.get(
                "action"
            ),
        )

    else:

        execution = recovery_executor(
            payment=payment,
            action=approval_result.get(
                "action"
            ),
            dry_run=dry_run,
        )

    # --------------------------------------------------------
    # AUDIT EXECUTION
    # --------------------------------------------------------

    if execution.get(
        "executed",
        False
    ):

        event_type = "RECOVERY_EXECUTED"

    else:

        event_type = "RECOVERY_EXECUTION_BLOCKED"

    record_recovery_event(
        event_type=event_type,
        payment_id=payment.get(
            "payment_id"
        ),
        action=approval_result.get(
            "action"
        ),
        status=execution.get(
            "mode",
            "UNKNOWN"
        ),
        amount=payment.get(
            "amount"
        ),
        details=execution.get(
            "reason",
            execution.get(
                "execution_reason",
                ""
            )
        ),
    )

    return execution


# ============================================================
# COMPLETE WORKFLOW
# ============================================================

def run_end_to_end_recovery(
    payments: list[dict],
    *,
    approved: bool = False,
    dry_run: bool = True,
    executor: Callable[..., Any] | None = None,
) -> dict:

    # --------------------------------------------------------
    # STEP 1 — ANALYSIS
    # --------------------------------------------------------

    analysis = analyze_recovery_request(
        payments
    )

    # --------------------------------------------------------
    # STEP 2 — SELECT TOP OPPORTUNITY
    # --------------------------------------------------------

    top_opportunity = (
        select_top_opportunity(
            analysis
        )
    )

    if top_opportunity is None:

        return {
            "status": "NO_OPPORTUNITY",
            "analysis": analysis,
            "approval": None,
            "execution": None,
        }

    # --------------------------------------------------------
    # STEP 3 — APPROVAL REQUEST
    # --------------------------------------------------------

    approval_request = (
        build_top_approval_request(
            payments,
            analysis,
        )
    )

    if approval_request is None:

        return {
            "status": "APPROVAL_FAILED",
            "analysis": analysis,
            "approval": None,
            "execution": None,
        }

    # --------------------------------------------------------
    # STEP 4 — PROCESS APPROVAL
    # --------------------------------------------------------

    approval_result = process_approval(
        approval_request,
        approved=approved,
    )

    # --------------------------------------------------------
    # STEP 5 — FIND PAYMENT
    # --------------------------------------------------------

    payment = next(
        (
            item
            for item in payments
            if item.get("payment_id")
            == approval_result.get(
                "payment_id"
            )
        ),
        None,
    )

    if payment is None:

        return {
            "status": "PAYMENT_NOT_FOUND",
            "analysis": analysis,
            "approval": approval_result,
            "execution": None,
        }

    # --------------------------------------------------------
    # STEP 6 — EXECUTE
    # --------------------------------------------------------

    execution = execute_approved_recovery(
        approval_result,
        payment,
        dry_run=dry_run,
        executor=executor,
    )

    return {
        "status": execution.get(
            "mode",
            "UNKNOWN"
        ),
        "analysis": analysis,
        "top_opportunity":
            top_opportunity,
        "approval":
            approval_result,
        "execution":
            execution,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "analyze_recovery_request",
    "select_top_opportunity",
    "build_top_approval_request",
    "process_approval",
    "execute_approved_recovery",
    "run_end_to_end_recovery",
]