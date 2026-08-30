# ============================================================
# REVENUE RECOVERY - STRATEGY ENGINE
# ============================================================

from typing import Any


# ============================================================
# STRATEGY CONSTANTS
# ============================================================

STRATEGY_MONITOR = "MONITOR"
STRATEGY_RETRY = "RETRY"
STRATEGY_PAYMENT_LINK = "PAYMENT_LINK"
STRATEGY_MANUAL_REVIEW = "MANUAL_REVIEW"
STRATEGY_STOP = "STOP"


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

def is_successful_payment(
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
# STRATEGY SELECTION
# ============================================================

def select_recovery_strategy(
    payment: dict,
    risk: dict,
    policy: dict,
) -> dict:

    # --------------------------------------------------------
    # SAFETY: INVALID INPUT
    # --------------------------------------------------------

    if not isinstance(
        payment,
        dict,
    ):

        return {
            "strategy":
                STRATEGY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment record is invalid.",
        }

    if not isinstance(
        risk,
        dict,
    ):

        risk = {}

    if not isinstance(
        policy,
        dict,
    ):

        policy = {}


    # --------------------------------------------------------
    # PAYMENT DATA
    # --------------------------------------------------------

    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )

    status = _normalize_status(
        payment.get(
            "status",
            "",
        )
    )

    failed_attempts = _safe_int(
        payment.get(
            "failed_attempts",
            0,
        )
    )


    # --------------------------------------------------------
    # RISK DATA
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
    ).upper().strip()


    # --------------------------------------------------------
    # POLICY DATA
    # --------------------------------------------------------

    eligible = bool(
        policy.get(
            "eligible",
            False,
        )
    )

    requires_approval = bool(
        policy.get(
            "requires_approval",
            False,
        )
    )

    max_attempts = _safe_int(
        policy.get(
            "max_attempts",
            policy.get(
                "max_failed_attempts",
                3,
            ),
        ),
        3,
    )


    # --------------------------------------------------------
    # STOP: INVALID / INELIGIBLE
    # --------------------------------------------------------

    if not eligible:

        return {
            "strategy":
                STRATEGY_STOP,

            "requires_approval":
                False,

            "reason":
                "Recovery is not permitted by policy.",
        }


    # --------------------------------------------------------
    # STOP: PAYMENT ALREADY SUCCESSFUL
    # --------------------------------------------------------

    if is_successful_payment(
        payment
    ):

        return {
            "strategy":
                STRATEGY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment is already successful.",
        }


    # --------------------------------------------------------
    # STOP: MAXIMUM ATTEMPTS
    # --------------------------------------------------------

    if failed_attempts >= max_attempts:

        return {
            "strategy":
                STRATEGY_STOP,

            "requires_approval":
                True,

            "reason":
                (
                    "Recovery attempts have reached the "
                    "configured stopping threshold."
                ),
        }


    # --------------------------------------------------------
    # STOP: INVALID AMOUNT
    # --------------------------------------------------------

    if amount <= 0:

        return {
            "strategy":
                STRATEGY_STOP,

            "requires_approval":
                False,

            "reason":
                "Payment amount is invalid.",
        }


    # --------------------------------------------------------
    # HIGH RISK + HIGH VALUE
    # --------------------------------------------------------

    if (
        risk_level == "HIGH"
        and amount >= 10000
    ):

        return {
            "strategy":
                STRATEGY_MANUAL_REVIEW,

            "requires_approval":
                True,

            "reason":
                (
                    "High-risk, high-value payment "
                    "requires human review."
                ),
        }


    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if risk_level == "HIGH":

        return {
            "strategy":
                STRATEGY_PAYMENT_LINK,

            "requires_approval":
                True,

            "reason":
                (
                    "A controlled payment-link recovery "
                    "is appropriate for this high-risk "
                    "payment."
                ),
        }


    # --------------------------------------------------------
    # MEDIUM RISK
    # --------------------------------------------------------

    if risk_level == "MEDIUM":

        return {
            "strategy":
                STRATEGY_RETRY,

            "requires_approval":
                requires_approval,

            "reason":
                (
                    "Medium-risk payment can use a "
                    "controlled retry within policy limits."
                ),
        }


    # --------------------------------------------------------
    # LOW RISK
    # --------------------------------------------------------

    return {
        "strategy":
            STRATEGY_MONITOR,

        "requires_approval":
            False,

        "reason":
            (
                "Risk is currently low. "
                "Continue monitoring."
            ),
    }


# ============================================================
# BATCH STRATEGY SELECTION
# ============================================================

def select_batch_recovery_strategies(
    payments: list[dict],
    risk_results: list[dict],
    policy_results: list[dict],
) -> list[dict]:

    # --------------------------------------------------------
    # MAP RISK RESULTS BY PAYMENT ID
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


    # --------------------------------------------------------
    # MAP POLICY RESULTS BY PAYMENT ID
    # --------------------------------------------------------

    policy_by_payment_id = {
        item.get(
            "payment_id"
        ): item

        for item in policy_results

        if isinstance(
            item,
            dict,
        )

        and item.get(
            "payment_id"
        )
    }


    results = []


    # --------------------------------------------------------
    # PROCESS PAYMENTS
    # --------------------------------------------------------

    for payment in payments:

        if not isinstance(
            payment,
            dict,
        ):
            continue

        payment_id = payment.get(
            "payment_id"
        )

        risk = risk_by_payment_id.get(
            payment_id,
            {},
        )

        policy = policy_by_payment_id.get(
            payment_id,
            {},
        )

        strategy = select_recovery_strategy(
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

            **strategy,
        })


    return results


# ============================================================
# STRATEGY SUMMARY
# ============================================================

def build_strategy_summary(
    strategies: list[dict],
) -> dict:

    summary = {
        "total":
            len(strategies),

        "monitor":
            0,

        "retry":
            0,

        "payment_link":
            0,

        "manual_review":
            0,

        "stop":
            0,

        "approval_required":
            0,
    }


    for item in strategies:

        strategy = item.get(
            "strategy"
        )

        if strategy == STRATEGY_MONITOR:

            summary["monitor"] += 1

        elif strategy == STRATEGY_RETRY:

            summary["retry"] += 1

        elif strategy == STRATEGY_PAYMENT_LINK:

            summary["payment_link"] += 1

        elif strategy == STRATEGY_MANUAL_REVIEW:

            summary["manual_review"] += 1

        elif strategy == STRATEGY_STOP:

            summary["stop"] += 1


        if item.get(
            "requires_approval",
            False,
        ):

            summary["approval_required"] += 1


    return summary


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "STRATEGY_MONITOR",

    "STRATEGY_RETRY",

    "STRATEGY_PAYMENT_LINK",

    "STRATEGY_MANUAL_REVIEW",

    "STRATEGY_STOP",

    "is_successful_payment",

    "select_recovery_strategy",

    "select_batch_recovery_strategies",

    "build_strategy_summary",
]