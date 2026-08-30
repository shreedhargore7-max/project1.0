# ============================================================
# REVENUE RECOVERY - PRODUCTION GUARDRAILS
# ============================================================

from typing import Any


# ============================================================
# GUARDRAIL STATUS
# ============================================================

GUARDRAIL_ALLOW = "ALLOW"
GUARDRAIL_BLOCK = "BLOCK"
GUARDRAIL_REVIEW = "REVIEW"


# ============================================================
# DEFAULT LIMITS
# ============================================================

DEFAULT_MAX_RECOVERY_AMOUNT = 100000.0
DEFAULT_MAX_EXECUTION_ATTEMPTS = 1


# ============================================================
# HELPERS
# ============================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(
    value: Any,
    default: int = 0,
) -> int:

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# AMOUNT GUARD
# ============================================================

def check_amount_limit(
    amount: Any,
    max_amount: float = DEFAULT_MAX_RECOVERY_AMOUNT,
) -> dict:

    normalized_amount = _safe_float(
        amount
    )

    normalized_max = _safe_float(
        max_amount,
        DEFAULT_MAX_RECOVERY_AMOUNT,
    )

    if normalized_amount <= 0:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Recovery amount must be greater than zero.",
        }

    if normalized_amount > normalized_max:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                (
                    "Recovery amount exceeds the configured "
                    "maximum execution limit."
                ),
        }

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "reason":
            "Recovery amount is within the configured limit.",
    }


# ============================================================
# APPROVAL GUARD
# ============================================================

def check_approval(
    approved: Any,
) -> dict:

    if approved is not True:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                (
                    "Explicit human approval is required "
                    "before recovery execution."
                ),
        }

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "reason":
            "Explicit human approval was provided.",
    }


# ============================================================
# DUPLICATE / IDEMPOTENCY GUARD
# ============================================================

def check_idempotency(
    payment_id: Any,
    action: Any,
    executed_operations: set[str] | None = None,
) -> dict:

    if executed_operations is None:

        executed_operations = set()

    if not payment_id:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Payment ID is required for idempotent execution.",
        }

    if not action:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Recovery action is required.",
        }

    operation_key = (
        f"{payment_id}:{action}"
    )

    if operation_key in executed_operations:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "duplicate":
                True,

            "operation_key":
                operation_key,

            "reason":
                (
                    "The same recovery operation has "
                    "already been executed."
                ),
        }

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "duplicate":
            False,

        "operation_key":
            operation_key,

        "reason":
            "No duplicate recovery operation was detected.",
    }


# ============================================================
# EXECUTION ATTEMPT LIMIT
# ============================================================

def check_execution_attempt_limit(
    execution_attempts: Any,
    max_attempts: int = DEFAULT_MAX_EXECUTION_ATTEMPTS,
) -> dict:

    attempts = _safe_int(
        execution_attempts
    )

    maximum = _safe_int(
        max_attempts,
        DEFAULT_MAX_EXECUTION_ATTEMPTS,
    )

    if maximum < 1:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Maximum execution attempts must be at least one.",
        }

    if attempts >= maximum:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                (
                    "Execution attempt limit has already "
                    "been reached."
                ),
        }

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "reason":
            "Execution attempt remains within the configured limit.",
    }


# ============================================================
# ACTION GUARD
# ============================================================

def check_recovery_action(
    action: Any,
) -> dict:

    allowed_actions = {
        "RECOVERY_REVIEW",
        "MANUAL_REVIEW",
        "PAYMENT_LINK",
    }

    normalized_action = str(
        action or ""
    ).upper().strip()

    if normalized_action not in allowed_actions:

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Recovery action is not permitted by the guardrail.",
        }

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "reason":
            "Recovery action is permitted.",
    }


# ============================================================
# COMPLETE EXECUTION GUARD
# ============================================================

def evaluate_execution_guardrails(
    payment: dict,
    action: str,
    approved: bool,
    executed_operations: set[str] | None = None,
    execution_attempts: int = 0,
    max_execution_attempts: int = DEFAULT_MAX_EXECUTION_ATTEMPTS,
    max_recovery_amount: float = DEFAULT_MAX_RECOVERY_AMOUNT,
) -> dict:
    """
    Evaluate all execution guardrails before an external
    recovery action.

    ALL checks must pass before execution is permitted.
    """

    # --------------------------------------------------------
    # Validate payment
    # --------------------------------------------------------

    if not isinstance(
        payment,
        dict,
    ):

        return {
            "status":
                GUARDRAIL_BLOCK,

            "allowed":
                False,

            "reason":
                "Payment record is invalid.",
        }

    payment_id = payment.get(
        "payment_id"
    )

    amount = payment.get(
        "amount",
        0,
    )

    # --------------------------------------------------------
    # Action
    # --------------------------------------------------------

    action_result = check_recovery_action(
        action
    )

    if not action_result["allowed"]:

        return {
            **action_result,
            "guardrail":
                "action",
        }

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    amount_result = check_amount_limit(
        amount,
        max_amount=max_recovery_amount,
    )

    if not amount_result["allowed"]:

        return {
            **amount_result,
            "guardrail":
                "amount",
        }

    # --------------------------------------------------------
    # Approval
    # --------------------------------------------------------

    approval_result = check_approval(
        approved
    )

    if not approval_result["allowed"]:

        return {
            **approval_result,
            "guardrail":
                "approval",
        }

    # --------------------------------------------------------
    # Execution attempt limit
    # --------------------------------------------------------

    attempt_result = check_execution_attempt_limit(
        execution_attempts,
        max_attempts=max_execution_attempts,
    )

    if not attempt_result["allowed"]:

        return {
            **attempt_result,
            "guardrail":
                "execution_attempt_limit",
        }

    # --------------------------------------------------------
    # Idempotency
    # --------------------------------------------------------

    idempotency_result = check_idempotency(
        payment_id,
        action,
        executed_operations,
    )

    if not idempotency_result["allowed"]:

        return {
            **idempotency_result,
            "guardrail":
                "idempotency",
        }

    # --------------------------------------------------------
    # All guardrails passed
    # --------------------------------------------------------

    return {
        "status":
            GUARDRAIL_ALLOW,

        "allowed":
            True,

        "guardrail":
            "all",

        "operation_key":
            idempotency_result[
                "operation_key"
            ],

        "reason":
            (
                "All execution guardrails passed. "
                "Recovery execution is permitted."
            ),
    }


# ============================================================
# REGISTER EXECUTED OPERATION
# ============================================================

def register_executed_operation(
    payment_id: Any,
    action: Any,
    executed_operations: set[str] | None = None,
) -> set[str]:

    if executed_operations is None:

        executed_operations = set()

    if payment_id and action:

        operation_key = (
            f"{payment_id}:{action}"
        )

        executed_operations.add(
            operation_key
        )

    return executed_operations


# ============================================================
# SUMMARY
# ============================================================

def build_guardrail_summary(
    result: dict,
) -> str:

    status = result.get(
        "status",
        GUARDRAIL_BLOCK,
    )

    allowed = result.get(
        "allowed",
        False,
    )

    reason = result.get(
        "reason",
        "",
    )

    operation_key = result.get(
        "operation_key",
        "",
    )

    lines = [
        "Recovery Execution Guardrails",
        "",
        f"Status: {status}",
        f"Allowed: {allowed}",
        f"Reason: {reason}",
    ]

    if operation_key:

        lines.append(
            f"Operation key: {operation_key}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "GUARDRAIL_ALLOW",

    "GUARDRAIL_BLOCK",

    "GUARDRAIL_REVIEW",

    "DEFAULT_MAX_RECOVERY_AMOUNT",

    "DEFAULT_MAX_EXECUTION_ATTEMPTS",

    "check_amount_limit",

    "check_approval",

    "check_idempotency",

    "check_execution_attempt_limit",

    "check_recovery_action",

    "evaluate_execution_guardrails",

    "register_executed_operation",

    "build_guardrail_summary",
]