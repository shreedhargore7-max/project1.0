# ============================================================
# REVENUE RECOVERY - OUTCOME TRACKER
# ============================================================

from typing import Any


# ============================================================
# OUTCOME STATUSES
# ============================================================

OUTCOME_CREATED = "CREATED"
OUTCOME_PENDING = "PENDING"
OUTCOME_CAPTURED = "CAPTURED"
OUTCOME_FAILED = "FAILED"
OUTCOME_EXPIRED = "EXPIRED"
OUTCOME_STOPPED = "STOPPED"
OUTCOME_REJECTED = "REJECTED"


# ============================================================
# STATUS GROUPS
# ============================================================

SUCCESS_STATUSES = {
    OUTCOME_CAPTURED,
    "PAID",
    "SUCCESS",
    "SUCCESSFUL",
    "COMPLETED",
}

PENDING_STATUSES = {
    OUTCOME_PENDING,
}

CREATED_STATUSES = {
    OUTCOME_CREATED,
}

FAILED_STATUSES = {
    OUTCOME_FAILED,
    OUTCOME_EXPIRED,
    OUTCOME_STOPPED,
    OUTCOME_REJECTED,
}


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


def _normalize_status(
    value: Any,
) -> str:

    return str(
        value or ""
    ).upper().strip()


# ============================================================
# OUTCOME CLASSIFICATION
# ============================================================

def classify_outcome_status(
    status: Any,
) -> str:
    """
    Normalize an outcome status.

    CREATED remains CREATED.
    PENDING remains PENDING.

    This distinction is important because creation of a
    recovery payment link is not the same as a pending
    customer payment.
    """

    normalized = _normalize_status(
        status
    )

    if normalized in SUCCESS_STATUSES:
        return OUTCOME_CAPTURED

    if normalized in CREATED_STATUSES:
        return OUTCOME_CREATED

    if normalized in PENDING_STATUSES:
        return OUTCOME_PENDING

    if normalized in FAILED_STATUSES:
        return OUTCOME_FAILED

    return normalized or OUTCOME_PENDING


# ============================================================
# SINGLE PAYMENT OUTCOME
# ============================================================

def track_payment_outcome(
    payment: dict,
    outcome_status: str,
) -> dict:

    if not isinstance(
        payment,
        dict,
    ):

        return {
            "payment_id": None,
            "amount": 0.0,
            "status": OUTCOME_FAILED,
            "recovered": False,
            "recovered_amount": 0.0,
        }

    payment_id = payment.get(
        "payment_id"
    )

    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )

    normalized_status = classify_outcome_status(
        outcome_status
    )

    recovered = (
        normalized_status
        == OUTCOME_CAPTURED
    )

    recovered_amount = (
        amount
        if recovered
        else 0.0
    )

    return {
        "payment_id":
            payment_id,

        "amount":
            round(
                amount,
                2,
            ),

        "status":
            normalized_status,

        "recovered":
            recovered,

        "recovered_amount":
            round(
                recovered_amount,
                2,
            ),
    }


# ============================================================
# BATCH OUTCOME TRACKING
# ============================================================

def track_batch_outcomes(
    payments: list[dict],
    outcomes: dict[str, str],
) -> list[dict]:

    if not isinstance(
        outcomes,
        dict,
    ):

        outcomes = {}

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

        status = outcomes.get(
            payment_id,
            OUTCOME_PENDING,
        )

        result = track_payment_outcome(
            payment,
            status,
        )

        results.append(
            result
        )

    return results


# ============================================================
# OUTCOME METRICS
# ============================================================

def calculate_outcome_metrics(
    outcomes: list[dict],
    eligible_amount: float = 0.0,
) -> dict:

    total = len(
        outcomes
    )

    recovered_transactions = 0
    recovered_amount = 0.0

    pending_transactions = 0
    pending_amount = 0.0

    created_transactions = 0
    created_amount = 0.0

    failed_transactions = 0
    failed_amount = 0.0

    for outcome in outcomes:

        if not isinstance(
            outcome,
            dict,
        ):
            continue

        amount = _safe_float(
            outcome.get(
                "amount",
                0,
            )
        )

        status = classify_outcome_status(
            outcome.get(
                "status"
            )
        )

        if status == OUTCOME_CAPTURED:

            recovered_transactions += 1
            recovered_amount += amount

        elif status == OUTCOME_CREATED:

            created_transactions += 1
            created_amount += amount

        elif status == OUTCOME_PENDING:

            pending_transactions += 1
            pending_amount += amount

        else:

            failed_transactions += 1
            failed_amount += amount

    # --------------------------------------------------------
    # Eligible amount
    # --------------------------------------------------------

    eligible = _safe_float(
        eligible_amount
    )

    if eligible <= 0:

        eligible = sum(
            _safe_float(
                outcome.get(
                    "amount",
                    0,
                )
            )

            for outcome in outcomes

            if isinstance(
                outcome,
                dict,
            )
        )

    # --------------------------------------------------------
    # Recovery rate
    # --------------------------------------------------------

    recovery_rate = 0.0

    if eligible > 0:

        recovery_rate = (
            recovered_amount
            / eligible
        )

    return {

        "total_transactions":
            total,

        "recovered_transactions":
            recovered_transactions,

        "recovered_amount":
            round(
                recovered_amount,
                2,
            ),

        "pending_transactions":
            pending_transactions,

        "pending_amount":
            round(
                pending_amount,
                2,
            ),

        "created_transactions":
            created_transactions,

        "created_amount":
            round(
                created_amount,
                2,
            ),

        "failed_transactions":
            failed_transactions,

        "failed_amount":
            round(
                failed_amount,
                2,
            ),

        "eligible_amount":
            round(
                eligible,
                2,
            ),

        "recovery_rate":
            round(
                recovery_rate,
                4,
            ),

        "unrecovered_amount":
            round(
                max(
                    eligible
                    - recovered_amount,
                    0,
                ),
                2,
            ),
    }


# ============================================================
# SUMMARY
# ============================================================

def build_outcome_summary(
    metrics: dict,
) -> str:

    return "\n".join(
        [
            "# Recovery Outcome Summary",
            "",
            (
                f"Transactions tracked: "
                f"{metrics.get('total_transactions', 0)}"
            ),
            (
                f"Eligible recovery amount: ₹"
                f"{metrics.get('eligible_amount', 0):,.2f}"
            ),
            (
                f"Recovered transactions: "
                f"{metrics.get('recovered_transactions', 0)}"
            ),
            (
                f"Money recovered: ₹"
                f"{metrics.get('recovered_amount', 0):,.2f}"
            ),
            (
                f"Recovery rate: "
                f"{metrics.get('recovery_rate', 0) * 100:.2f}%"
            ),
            (
                f"Created transactions: "
                f"{metrics.get('created_transactions', 0)}"
            ),
            (
                f"Created amount: ₹"
                f"{metrics.get('created_amount', 0):,.2f}"
            ),
            (
                f"Pending amount: ₹"
                f"{metrics.get('pending_amount', 0):,.2f}"
            ),
            (
                f"Failed amount: ₹"
                f"{metrics.get('failed_amount', 0):,.2f}"
            ),
            (
                f"Unrecovered amount: ₹"
                f"{metrics.get('unrecovered_amount', 0):,.2f}"
            ),
        ]
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "OUTCOME_CREATED",

    "OUTCOME_PENDING",

    "OUTCOME_CAPTURED",

    "OUTCOME_FAILED",

    "OUTCOME_EXPIRED",

    "OUTCOME_STOPPED",

    "OUTCOME_REJECTED",

    "SUCCESS_STATUSES",

    "PENDING_STATUSES",

    "CREATED_STATUSES",

    "FAILED_STATUSES",

    "classify_outcome_status",

    "track_payment_outcome",

    "track_batch_outcomes",

    "calculate_outcome_metrics",

    "build_outcome_summary",
]