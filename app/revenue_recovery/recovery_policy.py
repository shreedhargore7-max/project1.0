# ============================================================
# REVENUE RECOVERY - RECOVERY POLICY ENGINE
# ============================================================

from typing import Any


# ============================================================
# POLICY CONSTANTS
# ============================================================

DEFAULT_MAX_FAILED_ATTEMPTS = 3

DEFAULT_MIN_RECOVERY_AMOUNT = 100.0

DEFAULT_MAX_RECOVERY_AMOUNT = 100000.0

DEFAULT_MIN_RISK_SCORE = 40

DEFAULT_REQUIRE_APPROVAL_ABOVE_AMOUNT = 10000.0


# ============================================================
# ACTIONS
# ============================================================

POLICY_ALLOW = "ALLOW"

POLICY_REVIEW = "REVIEW"

POLICY_MONITOR = "MONITOR"

POLICY_STOP = "STOP"


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


def _normalize_status(
    value: Any,
) -> str:

    return str(
        value or ""
    ).lower().strip()


# ============================================================
# SUCCESS CHECK
# ============================================================

def is_payment_successful(
    payment: dict,
) -> bool:

    status = _normalize_status(
        payment.get(
            "status"
        )
    )

    captured = payment.get(
        "captured"
    )

    return (
        captured is True
        or status in {
            "paid",
            "captured",
            "success",
            "successful",
            "completed",
        }
    )


# ============================================================
# POLICY CONFIGURATION
# ============================================================

def default_recovery_policy() -> dict:

    return {
        "max_failed_attempts":
            DEFAULT_MAX_FAILED_ATTEMPTS,

        "min_recovery_amount":
            DEFAULT_MIN_RECOVERY_AMOUNT,

        "max_recovery_amount":
            DEFAULT_MAX_RECOVERY_AMOUNT,

        "min_risk_score":
            DEFAULT_MIN_RISK_SCORE,

        "require_approval_above_amount":
            DEFAULT_REQUIRE_APPROVAL_ABOVE_AMOUNT,
    }


# ============================================================
# POLICY VALIDATION
# ============================================================

def validate_policy(
    policy: dict,
) -> bool:

    if not isinstance(
        policy,
        dict,
    ):
        return False

    max_failed_attempts = _safe_int(
        policy.get(
            "max_failed_attempts"
        ),
        -1,
    )

    min_amount = _safe_float(
        policy.get(
            "min_recovery_amount"
        ),
        -1,
    )

    max_amount = _safe_float(
        policy.get(
            "max_recovery_amount"
        ),
        -1,
    )

    min_risk_score = _safe_int(
        policy.get(
            "min_risk_score"
        ),
        -1,
    )

    approval_amount = _safe_float(
        policy.get(
            "require_approval_above_amount"
        ),
        -1,
    )

    if max_failed_attempts < 1:
        return False

    if min_amount < 0:
        return False

    if max_amount <= 0:
        return False

    if min_amount > max_amount:
        return False

    if min_risk_score < 0:
        return False

    if min_risk_score > 100:
        return False

    if approval_amount < 0:
        return False

    return True


# ============================================================
# STOPPING RULE
# ============================================================

def should_stop_recovery(
    payment: dict,
    policy: dict | None = None,
) -> tuple[bool, str]:

    if policy is None:
        policy = default_recovery_policy()

    if is_payment_successful(
        payment
    ):

        return (
            True,
            "Payment is already successful."
        )

    failed_attempts = _safe_int(
        payment.get(
            "failed_attempts",
            0,
        )
    )

    max_failed_attempts = _safe_int(
        policy.get(
            "max_failed_attempts",
            DEFAULT_MAX_FAILED_ATTEMPTS,
        ),
        DEFAULT_MAX_FAILED_ATTEMPTS,
    )

    if failed_attempts >= max_failed_attempts:

        return (
            True,
            (
                "Recovery stopped because the payment "
                "has reached the maximum allowed failed "
                "attempt threshold."
            )
        )

    return (
        False,
        "Recovery attempt limit has not been reached."
    )


# ============================================================
# RECOVERY ELIGIBILITY
# ============================================================

def evaluate_recovery_eligibility(
    payment: dict,
    risk: dict,
    policy: dict | None = None,
) -> dict:

    if policy is None:
        policy = default_recovery_policy()

    # --------------------------------------------------------
    # Validate policy
    # --------------------------------------------------------

    if not validate_policy(
        policy
    ):

        return {
            "eligible":
                False,

            "action":
                POLICY_STOP,

            "requires_approval":
                False,

            "reason":
                "Recovery policy configuration is invalid.",
        }

    # --------------------------------------------------------
    # Basic payment validation
    # --------------------------------------------------------

    if not isinstance(
        payment,
        dict,
    ):

        return {
            "eligible":
                False,

            "action":
                POLICY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment record is invalid.",
        }

    payment_id = payment.get(
        "payment_id"
    )

    if not payment_id:

        return {
            "eligible":
                False,

            "action":
                POLICY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment ID is missing.",
        }

    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )

    # --------------------------------------------------------
    # Successful payment
    # --------------------------------------------------------

    if is_payment_successful(
        payment
    ):

        return {
            "eligible":
                False,

            "action":
                POLICY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment is already successful.",
        }

    # --------------------------------------------------------
    # Amount validation
    # --------------------------------------------------------

    min_amount = _safe_float(
        policy.get(
            "min_recovery_amount",
            DEFAULT_MIN_RECOVERY_AMOUNT,
        )
    )

    max_amount = _safe_float(
        policy.get(
            "max_recovery_amount",
            DEFAULT_MAX_RECOVERY_AMOUNT,
        )
    )

    if amount < min_amount:

        return {
            "eligible":
                False,

            "action":
                POLICY_MONITOR,

            "requires_approval":
                False,

            "reason":
                (
                    "Payment amount is below the minimum "
                    "recovery threshold."
                ),
        }

    if amount > max_amount:

        return {
            "eligible":
                False,

            "action":
                POLICY_REVIEW,

            "requires_approval":
                True,

            "reason":
                (
                    "Payment amount exceeds the maximum "
                    "automated recovery limit."
                ),
        }

    # --------------------------------------------------------
    # Risk validation
    # --------------------------------------------------------

    risk_score = _safe_int(
        risk.get(
            "risk_score",
            0,
        )
    )

    risk_level = str(
        risk.get(
            "risk_level",
            "LOW",
        )
    ).upper()

    min_risk_score = _safe_int(
        policy.get(
            "min_risk_score",
            DEFAULT_MIN_RISK_SCORE,
        )
    )

    if risk_score < min_risk_score:

        return {
            "eligible":
                False,

            "action":
                POLICY_MONITOR,

            "requires_approval":
                False,

            "reason":
                (
                    "Risk score is below the recovery "
                    "eligibility threshold."
                ),
        }

    # --------------------------------------------------------
    # Stopping rule
    # --------------------------------------------------------

    should_stop, stop_reason = (
        should_stop_recovery(
            payment,
            policy,
        )
    )

    if should_stop:

        return {
            "eligible":
                False,

            "action":
                POLICY_STOP,

            "requires_approval":
                True,

            "reason":
                stop_reason,
        }

    # --------------------------------------------------------
    # Approval policy
    # --------------------------------------------------------

    approval_threshold = _safe_float(
        policy.get(
            "require_approval_above_amount",
            DEFAULT_REQUIRE_APPROVAL_ABOVE_AMOUNT,
        )
    )

    requires_approval = (
        amount >= approval_threshold
        or risk_level == "HIGH"
    )

    # --------------------------------------------------------
    # High risk
    # --------------------------------------------------------

    if risk_level == "HIGH":

        return {
            "eligible":
                True,

            "action":
                POLICY_REVIEW,

            "requires_approval":
                True,

            "reason":
                (
                    "High-risk payment is eligible for "
                    "recovery review but requires human approval."
                ),
        }

    # --------------------------------------------------------
    # Medium risk
    # --------------------------------------------------------

    if risk_level == "MEDIUM":

        return {
            "eligible":
                True,

            "action":
                POLICY_ALLOW,

            "requires_approval":
                requires_approval,

            "reason":
                (
                    "Medium-risk payment is eligible for "
                    "a controlled recovery action."
                ),
        }

    # --------------------------------------------------------
    # Low risk
    # --------------------------------------------------------

    return {
        "eligible":
            False,

        "action":
            POLICY_MONITOR,

        "requires_approval":
            False,

        "reason":
            (
                "Payment does not meet the risk threshold "
                "for recovery."
            ),
    }


# ============================================================
# BATCH POLICY EVALUATION
# ============================================================

def evaluate_batch_eligibility(
    payments: list[dict],
    risk_results: list[dict],
    policy: dict | None = None,
) -> list[dict]:

    if policy is None:
        policy = default_recovery_policy()

    # --------------------------------------------------------
    # Map risk by payment ID
    # --------------------------------------------------------

    risk_by_payment_id = {
        item.get(
            "payment_id"
        ): item

        for item in risk_results

        if isinstance(
            item,
            dict,
        )

        and item.get(
            "payment_id"
        )
    }

    results = []

    for payment in payments:

        if not isinstance(
            payment,
            dict,
        ):
            continue

        payment_id = payment.get(
            "payment_id"
        )

        risk = (
            risk_by_payment_id.get(
                payment_id,
                {},
            )
        )

        evaluation = evaluate_recovery_eligibility(
            payment,
            risk,
            policy,
        )

        results.append({

            "payment_id":
                payment_id,

            "amount":
                _safe_float(
                    payment.get(
                        "amount",
                        0,
                    )
                ),

            **evaluation,
        })

    return results


# ============================================================
# POLICY SUMMARY
# ============================================================

def build_policy_summary(
    evaluations: list[dict],
) -> dict:

    eligible = 0
    review = 0
    monitor = 0
    stopped = 0
    approval_required = 0

    eligible_amount = 0.0

    for item in evaluations:

        action = item.get(
            "action"
        )

        amount = _safe_float(
            item.get(
                "amount",
                0,
            )
        )

        if item.get(
            "eligible",
            False,
        ):

            eligible += 1

            eligible_amount += amount

        if action == POLICY_REVIEW:

            review += 1

        elif action == POLICY_MONITOR:

            monitor += 1

        elif action == POLICY_STOP:

            stopped += 1

        if item.get(
            "requires_approval",
            False,
        ):

            approval_required += 1

    return {

        "total":
            len(evaluations),

        "eligible":
            eligible,

        "review":
            review,

        "monitor":
            monitor,

        "stopped":
            stopped,

        "approval_required":
            approval_required,

        "eligible_amount":
            round(
                eligible_amount,
                2,
            ),
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "POLICY_ALLOW",

    "POLICY_REVIEW",

    "POLICY_MONITOR",

    "POLICY_STOP",

    "DEFAULT_MAX_FAILED_ATTEMPTS",

    "DEFAULT_MIN_RECOVERY_AMOUNT",

    "DEFAULT_MAX_RECOVERY_AMOUNT",

    "DEFAULT_MIN_RISK_SCORE",

    "DEFAULT_REQUIRE_APPROVAL_ABOVE_AMOUNT",

    "default_recovery_policy",

    "validate_policy",

    "is_payment_successful",

    "should_stop_recovery",

    "evaluate_recovery_eligibility",

    "evaluate_batch_eligibility",

    "build_policy_summary",
]