# ============================================================
# REVENUE RECOVERY - RECOVERY WORKFLOW
# ============================================================

from typing import Any, Callable

from app.revenue_recovery.risk_engine import (
    analyze_payment,
)

from app.revenue_recovery.root_cause import (
    analyze_root_cause,
)

from app.revenue_recovery.decision_engine import (
    decide_recovery_action,
)


# ============================================================
# WORKFLOW STATUS
# ============================================================

STATUS_ANALYZED = "ANALYZED"
STATUS_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
STATUS_APPROVED = "APPROVED"
STATUS_EXECUTED = "EXECUTED"
STATUS_REJECTED = "REJECTED"
STATUS_BLOCKED = "BLOCKED"


# ============================================================
# SAFE ACTION POLICY
# ============================================================

ALLOWED_RECOVERY_ACTIONS = {
    "RECOVERY_REVIEW",
    "MANUAL_REVIEW",
}


# ============================================================
# ANALYZE PAYMENT
# ============================================================

def analyze_recovery_opportunity(
    payment: dict,
) -> dict:

    risk_result = analyze_payment(
        payment
    )

    root_cause_result = analyze_root_cause(
        payment
    )

    decision = decide_recovery_action(
        payment,
        risk_result,
        root_cause_result,
    )

    return {
        "payment": payment,
        "risk": risk_result,
        "root_cause": root_cause_result,
        "decision": decision,
        "status": STATUS_ANALYZED,
    }


# ============================================================
# CHECK RECOVERY POLICY
# ============================================================

def check_recovery_policy(
    opportunity: dict,
) -> dict:

    decision = opportunity.get(
        "decision",
        {}
    )

    action = decision.get(
        "action"
    )

    risk = opportunity.get(
        "risk",
        {}
    )

    risk_level = str(
        risk.get(
            "risk_level",
            "LOW"
        )
    ).upper()

    # --------------------------------------------------------
    # HIGH-RISK UNSUPPORTED ACTION
    # --------------------------------------------------------

    if action not in ALLOWED_RECOVERY_ACTIONS:

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
            "policy_allowed": False,
            "policy_reason": (
                "The proposed action is not an approved "
                "recovery action."
            ),
        }

    # --------------------------------------------------------
    # LOW RISK SHOULD NOT BE EXECUTED
    # --------------------------------------------------------

    if risk_level == "LOW":

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
            "policy_allowed": False,
            "policy_reason": (
                "Low-risk transactions are not eligible "
                "for active recovery."
            ),
        }

    # --------------------------------------------------------
    # ALLOWED
    # --------------------------------------------------------

    return {
        **opportunity,
        "status": STATUS_APPROVAL_REQUIRED,
        "policy_allowed": True,
        "policy_reason": (
            "The recovery action is permitted but requires "
            "human approval before execution."
        ),
    }


# ============================================================
# REQUEST APPROVAL
# ============================================================

def request_recovery_approval(
    opportunity: dict,
    approved: bool,
) -> dict:

    if not opportunity.get(
        "policy_allowed",
        False
    ):

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
        }

    if not approved:

        return {
            **opportunity,
            "status": STATUS_REJECTED,
            "approval": False,
        }

    return {
        **opportunity,
        "status": STATUS_APPROVED,
        "approval": True,
    }


# ============================================================
# DRY-RUN EXECUTION
# ============================================================

def execute_recovery(
    opportunity: dict,
    executor: Callable[..., Any] | None = None,
    dry_run: bool = True,
) -> dict:

    status = opportunity.get(
        "status"
    )

    # --------------------------------------------------------
    # EXECUTION GUARD
    # --------------------------------------------------------

    if status != STATUS_APPROVED:

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
            "execution": None,
            "execution_reason": (
                "Recovery cannot execute because "
                "the action has not been approved."
            ),
        }

    payment = opportunity.get(
        "payment",
        {}
    )

    decision = opportunity.get(
        "decision",
        {}
    )

    action = decision.get(
        "action"
    )

    payment_id = payment.get(
        "payment_id"
    )

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if dry_run:

        return {
            **opportunity,
            "status": STATUS_EXECUTED,
            "execution": {
                "mode": "dry_run",
                "action": action,
                "payment_id": payment_id,
                "executed": False,
            },
            "execution_reason": (
                "Dry-run mode was enabled. "
                "No external payment operation was executed."
            ),
        }

    # --------------------------------------------------------
    # REAL EXECUTOR REQUIRED
    # --------------------------------------------------------

    if executor is None:

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
            "execution": None,
            "execution_reason": (
                "A real execution function was not provided."
            ),
        }

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    try:

        result = executor(
            payment=payment,
            action=action,
        )

        return {
            **opportunity,
            "status": STATUS_EXECUTED,
            "execution": {
                "mode": "live",
                "action": action,
                "payment_id": payment_id,
                "executed": True,
                "result": result,
            },
        }

    except Exception as error:

        return {
            **opportunity,
            "status": STATUS_BLOCKED,
            "execution": None,
            "execution_reason": (
                f"Recovery execution failed: {error}"
            ),
        }


# ============================================================
# COMPLETE WORKFLOW
# ============================================================

def run_recovery_workflow(
    payment: dict,
    approved: bool = False,
    executor: Callable[..., Any] | None = None,
    dry_run: bool = True,
) -> dict:

    # --------------------------------------------------------
    # STEP 1 — ANALYZE
    # --------------------------------------------------------

    opportunity = analyze_recovery_opportunity(
        payment
    )

    # --------------------------------------------------------
    # STEP 2 — POLICY
    # --------------------------------------------------------

    opportunity = check_recovery_policy(
        opportunity
    )

    # --------------------------------------------------------
    # STEP 3 — APPROVAL
    # --------------------------------------------------------

    opportunity = request_recovery_approval(
        opportunity,
        approved=approved,
    )

    # --------------------------------------------------------
    # STEP 4 — EXECUTION
    # --------------------------------------------------------

    opportunity = execute_recovery(
        opportunity,
        executor=executor,
        dry_run=dry_run,
    )

    return opportunity


# ============================================================
# USER-FRIENDLY SUMMARY
# ============================================================

def build_recovery_message(
    workflow_result: dict,
) -> str:

    payment = workflow_result.get(
        "payment",
        {}
    )

    risk = workflow_result.get(
        "risk",
        {}
    )

    decision = workflow_result.get(
        "decision",
        {}
    )

    status = workflow_result.get(
        "status",
        ""
    )

    payment_id = payment.get(
        "payment_id",
        "unknown"
    )

    amount = payment.get(
        "amount",
        0
    )

    risk_level = risk.get(
        "risk_level",
        "UNKNOWN"
    )

    action = decision.get(
        "action",
        "UNKNOWN"
    )

    lines = [
        f"Payment: {payment_id}",
        f"Amount: ₹{amount}",
        f"Risk level: {risk_level}",
        f"Recommended action: {action}",
        f"Workflow status: {status}",
    ]

    reasons = workflow_result.get(
        "root_cause",
        {}
    ).get(
        "explanations",
        []
    )

    if reasons:

        lines.append(
            "Reasons:"
        )

        for reason in reasons:

            lines.append(
                f"- {reason}"
            )

    execution_reason = workflow_result.get(
        "execution_reason"
    )

    if execution_reason:

        lines.append(
            f"Execution: {execution_reason}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "STATUS_ANALYZED",
    "STATUS_APPROVAL_REQUIRED",
    "STATUS_APPROVED",
    "STATUS_EXECUTED",
    "STATUS_REJECTED",
    "STATUS_BLOCKED",
    "ALLOWED_RECOVERY_ACTIONS",
    "analyze_recovery_opportunity",
    "check_recovery_policy",
    "request_recovery_approval",
    "execute_recovery",
    "run_recovery_workflow",
    "build_recovery_message",
]