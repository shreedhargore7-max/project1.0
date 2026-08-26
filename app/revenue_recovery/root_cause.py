# ============================================================
# REVENUE RECOVERY - ROOT CAUSE ENGINE
# ============================================================

from collections import Counter
from typing import Any


# ============================================================
# ROOT CAUSE TYPES
# ============================================================

CAUSE_PAYMENT_FAILURE = "payment_failure"
CAUSE_REPEATED_FAILURE = "repeated_failure"
CAUSE_HIGH_VALUE = "high_value_transaction"
CAUSE_MANY_ATTEMPTS = "many_attempts"
CAUSE_CUSTOMER_HISTORY = "strong_customer_history"
CAUSE_UNKNOWN = "unknown"


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
# FIND ROOT CAUSES FOR ONE PAYMENT
# ============================================================

def find_root_causes(
    payment: dict,
) -> list[str]:

    causes = []

    status = str(
        payment.get(
            "status",
            "",
        )
    ).lower()

    failed_attempts = _safe_int(
        payment.get(
            "failed_attempts",
            0,
        )
    )

    attempts = _safe_int(
        payment.get(
            "attempts",
            0,
        )
    )

    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )

    previous_successes = _safe_int(
        payment.get(
            "previous_successes",
            0,
        )
    )


    # --------------------------------------------------------
    # PAYMENT FAILURE
    # --------------------------------------------------------

    if status in {
        "failed",
        "failure",
        "cancelled",
        "canceled",
    }:

        causes.append(
            CAUSE_PAYMENT_FAILURE
        )


    # --------------------------------------------------------
    # REPEATED FAILURE
    # --------------------------------------------------------

    if failed_attempts >= 2:

        causes.append(
            CAUSE_REPEATED_FAILURE
        )


    # --------------------------------------------------------
    # MANY ATTEMPTS
    # --------------------------------------------------------

    if attempts >= 4:

        causes.append(
            CAUSE_MANY_ATTEMPTS
        )


    # --------------------------------------------------------
    # HIGH VALUE
    # --------------------------------------------------------

    if amount >= 10000:

        causes.append(
            CAUSE_HIGH_VALUE
        )


    # --------------------------------------------------------
    # CUSTOMER HISTORY
    # --------------------------------------------------------

    if previous_successes >= 3:

        causes.append(
            CAUSE_CUSTOMER_HISTORY
        )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not causes:

        causes.append(
            CAUSE_UNKNOWN
        )


    return causes


# ============================================================
# HUMAN-READABLE EXPLANATION
# ============================================================

CAUSE_DESCRIPTIONS = {

    CAUSE_PAYMENT_FAILURE:
        "The payment is currently unsuccessful.",

    CAUSE_REPEATED_FAILURE:
        "The payment has failed multiple times.",

    CAUSE_HIGH_VALUE:
        "The transaction has a high monetary value.",

    CAUSE_MANY_ATTEMPTS:
        "The transaction has had multiple payment attempts.",

    CAUSE_CUSTOMER_HISTORY:
        "The customer has a strong history of successful payments.",

    CAUSE_UNKNOWN:
        "No dominant revenue-risk cause was identified.",
}


# ============================================================
# EXPLAIN ROOT CAUSES
# ============================================================

def explain_root_causes(
    causes: list[str],
) -> list[str]:

    explanations = []

    for cause in causes:

        description = (
            CAUSE_DESCRIPTIONS.get(
                cause,
                "An unknown risk factor was detected.",
            )
        )

        explanations.append(
            description
        )

    return explanations


# ============================================================
# ANALYZE ONE PAYMENT
# ============================================================

def analyze_root_cause(
    payment: dict,
) -> dict:

    causes = find_root_causes(
        payment
    )

    explanations = explain_root_causes(
        causes
    )

    return {

        "payment_id":
            payment.get(
                "payment_id"
            ),

        "root_causes":
            causes,

        "explanations":
            explanations,

    }


# ============================================================
# ANALYZE BATCH
# ============================================================

def analyze_root_causes(
    payments: list[dict],
) -> list[dict]:

    results = []

    for payment in payments:

        if not isinstance(
            payment,
            dict,
        ):
            continue

        results.append(
            analyze_root_cause(
                payment
            )
        )

    return results


# ============================================================
# AGGREGATE ROOT CAUSES
# ============================================================

def aggregate_root_causes(
    results: list[dict],
) -> dict:

    counter = Counter()

    for result in results:

        causes = result.get(
            "root_causes",
            [],
        )

        for cause in causes:

            counter[cause] += 1

    return dict(
        counter.most_common()
    )


# ============================================================
# PRIMARY ROOT CAUSE
# ============================================================

def get_primary_root_cause(
    causes: list[str],
) -> str:

    if not causes:

        return CAUSE_UNKNOWN

    # Priority order:
    priority = [

        CAUSE_REPEATED_FAILURE,

        CAUSE_PAYMENT_FAILURE,

        CAUSE_HIGH_VALUE,

        CAUSE_MANY_ATTEMPTS,

        CAUSE_CUSTOMER_HISTORY,

        CAUSE_UNKNOWN,
    ]

    for cause in priority:

        if cause in causes:

            return cause

    return causes[0]


# ============================================================
# BUILD ROOT-CAUSE SUMMARY
# ============================================================

def build_root_cause_summary(
    results: list[dict],
) -> dict:

    aggregated = aggregate_root_causes(
        results
    )

    total = len(results)

    primary_cause = (
        next(
            iter(aggregated),
            CAUSE_UNKNOWN,
        )
    )

    return {

        "total_transactions":
            total,

        "root_cause_counts":
            aggregated,

        "primary_root_cause":
            primary_cause,

    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "CAUSE_PAYMENT_FAILURE",
    "CAUSE_REPEATED_FAILURE",
    "CAUSE_HIGH_VALUE",
    "CAUSE_MANY_ATTEMPTS",
    "CAUSE_CUSTOMER_HISTORY",
    "CAUSE_UNKNOWN",
    "find_root_causes",
    "explain_root_causes",
    "analyze_root_cause",
    "analyze_root_causes",
    "aggregate_root_causes",
    "get_primary_root_cause",
    "build_root_cause_summary",
]