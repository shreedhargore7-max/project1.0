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

from app.revenue_recovery.recovery_policy import (
    default_recovery_policy,
    evaluate_recovery_eligibility,
)

from app.revenue_recovery.strategy_engine import (
    select_recovery_strategy,
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
        "payment":
            payment,

        "risk":
            risk_result,

        "root_cause":
            root_cause_result,

        "decision":
            decision,

        "status":
            STATUS_ANALYZED,
    }


# ============================================================
# CHECK RECOVERY POLICY
# ============================================================

def check_recovery_policy(
    opportunity: dict,
    policy: dict | None = None,
) -> dict:

    # --------------------------------------------------------
    # Use default policy when none is provided
    # --------------------------------------------------------

    if policy is None:

        policy = (
            default_recovery_policy()
        )

    # --------------------------------------------------------
    # Read decision
    # --------------------------------------------------------

    decision = opportunity.get(
        "decision",
        {},
    )

    action = decision.get(
        "action"
    )

    # --------------------------------------------------------
    # Safety: only recovery actions can continue
    # --------------------------------------------------------

    if action not in ALLOWED_RECOVERY_ACTIONS:

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "policy_allowed":
                False,

            "policy_action":
                "STOP",

            "policy_requires_approval":
                False,

            "policy_reason":
                (
                    "The proposed action is not an "
                    "approved recovery action."
                ),

            "policy_result":
                {
                    "eligible": False,
                    "action": "STOP",
                    "requires_approval": False,
                    "reason":
                        (
                            "The proposed action is not an "
                            "approved recovery action."
                        ),
                },

            "policy_config":
                policy,
        }

    # --------------------------------------------------------
    # Payment + risk
    # --------------------------------------------------------

    payment = opportunity.get(
        "payment",
        {},
    )

    risk = opportunity.get(
        "risk",
        {},
    )

    # --------------------------------------------------------
    # Part 27 policy evaluation
    # --------------------------------------------------------

    policy_result = evaluate_recovery_eligibility(
        payment,
        risk,
        policy,
    )

    policy_action = policy_result.get(
        "action",
        "STOP",
    )

    policy_allowed = policy_result.get(
        "eligible",
        False,
    )

    requires_approval = policy_result.get(
        "requires_approval",
        False,
    )

    policy_reason = policy_result.get(
        "reason",
        "Recovery policy evaluated.",
    )

    # --------------------------------------------------------
    # POLICY DENIED
    # --------------------------------------------------------

    if not policy_allowed:

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "policy_allowed":
                False,

            "policy_action":
                policy_action,

            "policy_requires_approval":
                requires_approval,

            "policy_reason":
                policy_reason,

            "policy_result":
                policy_result,

            "policy_config":
                policy,
        }

    # --------------------------------------------------------
    # POLICY ALLOWED
    # --------------------------------------------------------

    return {
        **opportunity,

        "status":
            STATUS_APPROVAL_REQUIRED,

        "policy_allowed":
            True,

        "policy_action":
            policy_action,

        "policy_requires_approval":
            requires_approval,

        "policy_reason":
            policy_reason,

        "policy_result":
            policy_result,

        "policy_config":
            policy,
    }


# ============================================================
# SELECT RECOVERY STRATEGY
# ============================================================

def select_workflow_strategy(
    opportunity: dict,
) -> dict:

    # --------------------------------------------------------
    # POLICY MUST ALLOW
    # --------------------------------------------------------

    if not opportunity.get(
        "policy_allowed",
        False,
    ):

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "strategy":
                "STOP",

            "strategy_allowed":
                False,

            "strategy_requires_approval":
                False,

            "strategy_reason":
                (
                    "Strategy selection was blocked "
                    "by recovery policy."
                ),

            "strategy_result":
                {
                    "strategy": "STOP",
                    "requires_approval": False,
                    "reason":
                        (
                            "Strategy selection was blocked "
                            "by recovery policy."
                        ),
                },
        }

    # --------------------------------------------------------
    # Collect input
    # --------------------------------------------------------

    payment = opportunity.get(
        "payment",
        {},
    )

    risk = opportunity.get(
        "risk",
        {},
    )

    policy_config = opportunity.get(
        "policy_config"
    )

    # --------------------------------------------------------
    # Ensure valid policy configuration
    # --------------------------------------------------------

    if not isinstance(
        policy_config,
        dict,
    ):

        policy_config = (
            default_recovery_policy()
        )

    # --------------------------------------------------------
    # Policy evaluation result
    # --------------------------------------------------------

    policy_result = opportunity.get(
        "policy_result",
        {},
    )

    if not isinstance(
        policy_result,
        dict,
    ):

        policy_result = {}

    # --------------------------------------------------------
    # Build complete strategy policy
    #
    # Strategy engine needs:
    # - eligibility
    # - approval requirement
    # - maximum attempts
    # - policy limits
    # --------------------------------------------------------

    strategy_policy = {

        **policy_config,

        "eligible":
            True,

        "requires_approval":
            policy_result.get(
                "requires_approval",
                opportunity.get(
                    "policy_requires_approval",
                    False,
                ),
            ),
    }

    # --------------------------------------------------------
    # Select strategy
    # --------------------------------------------------------

    strategy_result = (
        select_recovery_strategy(
            payment,
            risk,
            strategy_policy,
        )
    )

    strategy = strategy_result.get(
        "strategy",
        "STOP",
    )

    strategy_requires_approval = (
        strategy_result.get(
            "requires_approval",
            False,
        )
    )

    strategy_reason = (
        strategy_result.get(
            "reason",
            "Recovery strategy evaluated.",
        )
    )

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    if strategy == "STOP":

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "strategy":
                strategy,

            "strategy_allowed":
                False,

            "strategy_requires_approval":
                strategy_requires_approval,

            "strategy_reason":
                strategy_reason,

            "strategy_result":
                strategy_result,
        }

    # --------------------------------------------------------
    # MONITOR
    # --------------------------------------------------------

    if strategy == "MONITOR":

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "strategy":
                strategy,

            "strategy_allowed":
                False,

            "strategy_requires_approval":
                False,

            "strategy_reason":
                strategy_reason,

            "strategy_result":
                strategy_result,
        }

    # --------------------------------------------------------
    # CONTROLLED RECOVERY STRATEGY
    # --------------------------------------------------------

    return {
        **opportunity,

        "status":
            STATUS_APPROVAL_REQUIRED,

        "strategy":
            strategy,

        "strategy_allowed":
            True,

        "strategy_requires_approval":
            strategy_requires_approval,

        "strategy_reason":
            strategy_reason,

        "strategy_result":
            strategy_result,
    }


# ============================================================
# REQUEST APPROVAL
# ============================================================

def request_recovery_approval(
    opportunity: dict,
    approved: bool,
) -> dict:

    # --------------------------------------------------------
    # Policy guard
    # --------------------------------------------------------

    if not opportunity.get(
        "policy_allowed",
        False,
    ):

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "approval":
                False,

            "approval_reason":
                (
                    "Recovery cannot be approved because "
                    "policy did not allow the operation."
                ),
        }

    # --------------------------------------------------------
    # Strategy guard
    # --------------------------------------------------------

    if not opportunity.get(
        "strategy_allowed",
        False,
    ):

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "approval":
                False,

            "approval_reason":
                (
                    "Recovery cannot be approved because "
                    "no policy-approved strategy exists."
                ),
        }

    # --------------------------------------------------------
    # Strategy approval requirement
    # --------------------------------------------------------

    requires_approval = opportunity.get(
        "strategy_requires_approval",
        opportunity.get(
            "policy_requires_approval",
            True,
        ),
    )

    # --------------------------------------------------------
    # Controlled strategy that does not require approval
    # --------------------------------------------------------

    if not requires_approval:

        return {
            **opportunity,

            "status":
                STATUS_APPROVED,

            "approval":
                True,

            "approval_reason":
                (
                    "The selected recovery strategy does "
                    "not require explicit human approval."
                ),
        }

    # --------------------------------------------------------
    # Explicit human approval
    # --------------------------------------------------------

    if not approved:

        return {
            **opportunity,

            "status":
                STATUS_REJECTED,

            "approval":
                False,

            "approval_reason":
                "Human approval was not granted.",
        }

    # --------------------------------------------------------
    # Approved
    # --------------------------------------------------------

    return {
        **opportunity,

        "status":
            STATUS_APPROVED,

        "approval":
            True,

        "approval_reason":
            "Human approval was granted.",
    }


# ============================================================
# EXECUTION
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
    # APPROVAL GUARD
    # --------------------------------------------------------

    if status != STATUS_APPROVED:

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
                    "Recovery cannot execute because "
                    "the action has not been approved."
                ),
        }

    # --------------------------------------------------------
    # STRATEGY GUARD
    # --------------------------------------------------------

    if not opportunity.get(
        "strategy_allowed",
        False,
    ):

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
                    "Recovery cannot execute because "
                    "no policy-approved strategy exists."
                ),
        }

    payment = opportunity.get(
        "payment",
        {},
    )

    decision = opportunity.get(
        "decision",
        {},
    )

    action = decision.get(
        "action"
    )

    strategy = opportunity.get(
        "strategy"
    )

    payment_id = payment.get(
        "payment_id"
    )

    # --------------------------------------------------------
    # STOP STRATEGY
    # --------------------------------------------------------

    if strategy == "STOP":

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
                    "Execution was blocked because "
                    "the recovery strategy is STOP."
                ),
        }

    # --------------------------------------------------------
    # MONITOR STRATEGY
    # --------------------------------------------------------

    if strategy == "MONITOR":

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
                    "Execution was blocked because "
                    "the selected strategy is MONITOR."
                ),
        }

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if dry_run:

        return {
            **opportunity,

            "status":
                STATUS_EXECUTED,

            "execution": {
                "mode":
                    "dry_run",

                "action":
                    action,

                "strategy":
                    strategy,

                "payment_id":
                    payment_id,

                "executed":
                    False,
            },

            "execution_reason":
                (
                    "Dry-run mode was enabled. "
                    "No external payment operation was executed."
                ),
        }

    # --------------------------------------------------------
    # LIVE EXECUTOR REQUIRED
    # --------------------------------------------------------

    if executor is None:

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
                    "A real execution function was not provided."
                ),
        }

    # --------------------------------------------------------
    # LIVE EXECUTION
    # --------------------------------------------------------

    try:

        result = executor(
            payment=payment,
            action=action,
        )

        return {
            **opportunity,

            "status":
                STATUS_EXECUTED,

            "execution": {
                "mode":
                    "live",

                "action":
                    action,

                "strategy":
                    strategy,

                "payment_id":
                    payment_id,

                "executed":
                    True,

                "result":
                    result,
            },

            "execution_reason":
                "Recovery action executed successfully.",
        }

    except Exception as error:

        return {
            **opportunity,

            "status":
                STATUS_BLOCKED,

            "execution":
                None,

            "execution_reason":
                (
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
    policy: dict | None = None,
) -> dict:

    # --------------------------------------------------------
    # STEP 1 — ANALYZE
    # --------------------------------------------------------

    opportunity = (
        analyze_recovery_opportunity(
            payment
        )
    )

    # --------------------------------------------------------
    # STEP 2 — POLICY
    # --------------------------------------------------------

    opportunity = (
        check_recovery_policy(
            opportunity,
            policy=policy,
        )
    )

    # --------------------------------------------------------
    # STOP when policy blocks
    # --------------------------------------------------------

    if (
        not opportunity.get(
            "policy_allowed",
            False,
        )
    ):

        return opportunity

    # --------------------------------------------------------
    # STEP 3 — STRATEGY
    # --------------------------------------------------------

    opportunity = (
        select_workflow_strategy(
            opportunity
        )
    )

    # --------------------------------------------------------
    # STOP when strategy blocks
    # --------------------------------------------------------

    if (
        not opportunity.get(
            "strategy_allowed",
            False,
        )
    ):

        return opportunity

    # --------------------------------------------------------
    # STEP 4 — APPROVAL
    # --------------------------------------------------------

    opportunity = (
        request_recovery_approval(
            opportunity,
            approved=approved,
        )
    )

    # --------------------------------------------------------
    # STOP if rejected / blocked
    # --------------------------------------------------------

    if opportunity.get(
        "status"
    ) != STATUS_APPROVED:

        return opportunity

    # --------------------------------------------------------
    # STEP 5 — EXECUTION
    # --------------------------------------------------------

    opportunity = execute_recovery(
        opportunity,
        executor=executor,
        dry_run=dry_run,
    )

    return opportunity


# ============================================================
# USER-FRIENDLY MESSAGE
# ============================================================

def build_recovery_message(
    workflow_result: dict,
) -> str:

    payment = workflow_result.get(
        "payment",
        {},
    )

    risk = workflow_result.get(
        "risk",
        {},
    )

    decision = workflow_result.get(
        "decision",
        {},
    )

    status = workflow_result.get(
        "status",
        "",
    )

    payment_id = payment.get(
        "payment_id",
        "unknown",
    )

    amount = payment.get(
        "amount",
        0,
    )

    risk_level = risk.get(
        "risk_level",
        "UNKNOWN",
    )

    action = decision.get(
        "action",
        "UNKNOWN",
    )

    strategy = workflow_result.get(
        "strategy",
        "UNKNOWN",
    )

    lines = [

        f"Payment: {payment_id}",

        f"Amount: ₹{amount}",

        f"Risk level: {risk_level}",

        f"Recommended action: {action}",

        f"Recovery strategy: {strategy}",

        f"Workflow status: {status}",
    ]

    # --------------------------------------------------------
    # Policy
    # --------------------------------------------------------

    policy_reason = workflow_result.get(
        "policy_reason"
    )

    if policy_reason:

        lines.append(
            f"Policy: {policy_reason}"
        )

    # --------------------------------------------------------
    # Strategy
    # --------------------------------------------------------

    strategy_reason = workflow_result.get(
        "strategy_reason"
    )

    if strategy_reason:

        lines.append(
            f"Strategy: {strategy_reason}"
        )

    # --------------------------------------------------------
    # Approval
    # --------------------------------------------------------

    approval_reason = workflow_result.get(
        "approval_reason"
    )

    if approval_reason:

        lines.append(
            f"Approval: {approval_reason}"
        )

    # --------------------------------------------------------
    # Root cause
    # --------------------------------------------------------

    reasons = (
        workflow_result.get(
            "root_cause",
            {},
        ).get(
            "explanations",
            [],
        )
    )

    if reasons:

        lines.append(
            "Reasons:"
        )

        for reason in reasons:

            lines.append(
                f"- {reason}"
            )

    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------

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

    "select_workflow_strategy",

    "request_recovery_approval",

    "execute_recovery",

    "run_recovery_workflow",

    "build_recovery_message",
]