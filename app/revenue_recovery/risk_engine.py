# ============================================================
# REVENUE RECOVERY - RISK ENGINE
# ============================================================

from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RISK_SCORE = 100

HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value: Any, default: float = 0.0) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# SINGLE PAYMENT RISK SCORE
# ============================================================

def calculate_risk_score(payment: dict) -> int:
    """
    Calculate a simple explainable revenue-risk score.

    Score components:

    - Payment failed
    - Multiple failed attempts
    - High transaction value
    - Previous successful payment history
    - Payment status indicating incomplete recovery
    """

    score = 0


    # --------------------------------------------------------
    # PAYMENT STATUS
    # --------------------------------------------------------

    status = str(
        payment.get(
            "status",
            ""
        )
    ).lower()

    if status in {
        "failed",
        "failure",
        "cancelled",
        "canceled",
    }:

        score += 30


    # --------------------------------------------------------
    # FAILED ATTEMPTS
    # --------------------------------------------------------

    failed_attempts = _safe_int(
        payment.get(
            "failed_attempts",
            0
        )
    )

    if failed_attempts >= 3:

        score += 25

    elif failed_attempts == 2:

        score += 15

    elif failed_attempts == 1:

        score += 8


    # --------------------------------------------------------
    # TOTAL ATTEMPTS
    # --------------------------------------------------------

    attempts = _safe_int(
        payment.get(
            "attempts",
            0
        )
    )

    if attempts >= 4:

        score += 10

    elif attempts >= 2:

        score += 5


    # --------------------------------------------------------
    # TRANSACTION VALUE
    # --------------------------------------------------------

    amount = _safe_float(
        payment.get(
            "amount",
            0
        )
    )

    if amount >= 20000:

        score += 25

    elif amount >= 10000:

        score += 20

    elif amount >= 5000:

        score += 15

    elif amount >= 1000:

        score += 8


    # --------------------------------------------------------
    # PREVIOUS SUCCESS HISTORY
    # --------------------------------------------------------

    previous_successes = _safe_int(
        payment.get(
            "previous_successes",
            0
        )
    )

    if previous_successes >= 5:

        score += 10

    elif previous_successes >= 2:

        score += 5


    # --------------------------------------------------------
    # CAP SCORE
    # --------------------------------------------------------

    return min(
        score,
        MAX_RISK_SCORE
    )


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(
    score: int
) -> str:

    if score >= HIGH_RISK_THRESHOLD:

        return "HIGH"

    if score >= MEDIUM_RISK_THRESHOLD:

        return "MEDIUM"

    return "LOW"


# ============================================================
# RISK REASON
# ============================================================

def explain_risk(
    payment: dict,
    score: int
) -> list[str]:

    reasons = []


    status = str(
        payment.get(
            "status",
            ""
        )
    ).lower()

    failed_attempts = _safe_int(
        payment.get(
            "failed_attempts",
            0
        )
    )

    attempts = _safe_int(
        payment.get(
            "attempts",
            0
        )
    )

    amount = _safe_float(
        payment.get(
            "amount",
            0
        )
    )

    previous_successes = _safe_int(
        payment.get(
            "previous_successes",
            0
        )
    )


    # --------------------------------------------------------
    # STATUS REASON
    # --------------------------------------------------------

    if status in {
        "failed",
        "failure",
        "cancelled",
        "canceled",
    }:

        reasons.append(
            "Payment is currently unsuccessful."
        )


    # --------------------------------------------------------
    # FAILURE ATTEMPTS
    # --------------------------------------------------------

    if failed_attempts >= 3:

        reasons.append(
            f"{failed_attempts} failed payment attempts."
        )

    elif failed_attempts > 0:

        reasons.append(
            f"{failed_attempts} failed payment attempt(s)."
        )


    # --------------------------------------------------------
    # TOTAL ATTEMPTS
    # --------------------------------------------------------

    if attempts >= 4:

        reasons.append(
            "Multiple payment attempts indicate "
            "continued recovery difficulty."
        )


    # --------------------------------------------------------
    # HIGH VALUE
    # --------------------------------------------------------

    if amount >= 20000:

        reasons.append(
            "High-value transaction."
        )

    elif amount >= 10000:

        reasons.append(
            "Above-average transaction value."
        )


    # --------------------------------------------------------
    # PREVIOUS SUCCESS
    # --------------------------------------------------------

    if previous_successes >= 5:

        reasons.append(
            "Customer has a strong previous successful "
            "payment history."
        )

    elif previous_successes >= 2:

        reasons.append(
            "Customer has previous successful payments."
        )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "Limited risk indicators were detected."
        )


    return reasons


# ============================================================
# ANALYZE ONE PAYMENT
# ============================================================

def analyze_payment(
    payment: dict
) -> dict:

    score = calculate_risk_score(
        payment
    )

    level = get_risk_level(
        score
    )

    reasons = explain_risk(
        payment,
        score
    )

    amount = _safe_float(
        payment.get(
            "amount",
            0
        )
    )

    return {

        "payment_id":
            payment.get(
                "payment_id"
            ),

        "amount":
            amount,

        "currency":
            payment.get(
                "currency",
                "INR"
            ),

        "risk_score":
            score,

        "risk_level":
            level,

        "revenue_at_risk":
            amount
            if level in {
                "HIGH",
                "MEDIUM"
            }
            else 0,

        "reasons":
            reasons,

    }


# ============================================================
# ANALYZE PAYMENT BATCH
# ============================================================

def analyze_payments(
    payments: list[dict]
) -> list[dict]:

    results = []

    for payment in payments:

        if not isinstance(
            payment,
            dict
        ):
            continue

        results.append(
            analyze_payment(
                payment
            )
        )

    results.sort(
        key=lambda item: (
            item["risk_score"],
            item["amount"],
        ),
        reverse=True
    )

    return results


# ============================================================
# TOTAL REVENUE AT RISK
# ============================================================

def calculate_total_revenue_at_risk(
    results: list[dict]
) -> float:

    total = 0.0

    for result in results:

        total += _safe_float(
            result.get(
                "revenue_at_risk",
                0
            )
        )

    return total


# ============================================================
# SUMMARY
# ============================================================

def build_risk_summary(
    results: list[dict]
) -> dict:

    high_count = sum(
        1
        for item in results
        if item.get(
            "risk_level"
        ) == "HIGH"
    )

    medium_count = sum(
        1
        for item in results
        if item.get(
            "risk_level"
        ) == "MEDIUM"
    )

    low_count = sum(
        1
        for item in results
        if item.get(
            "risk_level"
        ) == "LOW"
    )

    total_at_risk = (
        calculate_total_revenue_at_risk(
            results
        )
    )

    return {

        "total_transactions":
            len(results),

        "high_risk_transactions":
            high_count,

        "medium_risk_transactions":
            medium_count,

        "low_risk_transactions":
            low_count,

        "total_revenue_at_risk":
            total_at_risk,

    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "calculate_risk_score",
    "get_risk_level",
    "explain_risk",
    "analyze_payment",
    "analyze_payments",
    "calculate_total_revenue_at_risk",
    "build_risk_summary",
]