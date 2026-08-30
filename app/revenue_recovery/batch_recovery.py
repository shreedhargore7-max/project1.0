# ============================================================
# BATCH RECOVERY ANALYSIS
# ============================================================

from typing import Any

from app.revenue_recovery.outcome_tracker import (
    track_batch_outcomes,
    calculate_outcome_metrics,
)


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


# ============================================================
# BATCH RECOVERY METRICS
# ============================================================

def calculate_batch_recovery_metrics(
    payments: list[dict],
    decisions: list[dict],
    recovered_payment_ids: set[str] | None = None,
    recovery_outcomes: dict[str, str] | None = None,
) -> dict:
    """
    Calculate batch-level revenue recovery metrics.

    A recovery action being created does NOT mean the money
    was recovered.

    Actual recovery requires a confirmed successful/captured
    payment outcome.

    Parameters
    ----------
    payments:
        Normalized payment records.

    decisions:
        Recovery decisions.

    recovered_payment_ids:
        Backward-compatible way of explicitly marking a
        payment as recovered.

    recovery_outcomes:
        Optional mapping such as:

            {
                "pay_001": "captured",
                "pay_002": "pending",
                "pay_003": "created",
                "pay_004": "failed",
            }
    """

    if recovered_payment_ids is None:

        recovered_payment_ids = set()

    if recovery_outcomes is None:

        recovery_outcomes = {}


    # --------------------------------------------------------
    # TOTAL TRANSACTIONS
    # --------------------------------------------------------

    total_transactions = len(
        payments
    )


    # --------------------------------------------------------
    # TOTAL REVENUE
    # --------------------------------------------------------

    total_revenue = sum(

        _safe_float(
            payment.get(
                "amount",
                0,
            )
        )

        for payment in payments

        if isinstance(
            payment,
            dict,
        )
    )


    # --------------------------------------------------------
    # RISK METRICS
    # --------------------------------------------------------

    total_revenue_at_risk = 0.0

    high_risk_transactions = 0

    medium_risk_transactions = 0


    for payment in payments:

        if not isinstance(
            payment,
            dict,
        ):
            continue

        amount = _safe_float(
            payment.get(
                "amount",
                0,
            )
        )

        risk_level = str(
            payment.get(
                "risk_level",
                "",
            )
        ).upper()


        if risk_level == "HIGH":

            high_risk_transactions += 1

            total_revenue_at_risk += amount


        elif risk_level == "MEDIUM":

            medium_risk_transactions += 1


    # --------------------------------------------------------
    # RECOVERY ELIGIBILITY
    # --------------------------------------------------------

    recovery_eligible_ids = set()

    approved_ids = set()

    approved_amount = 0.0


    for decision in decisions:

        if not isinstance(
            decision,
            dict,
        ):
            continue

        payment_id = decision.get(
            "payment_id"
        )

        action = decision.get(
            "action",
            "",
        )

        requires_approval = decision.get(
            "requires_approval",
            False,
        )

        amount = _safe_float(
            decision.get(
                "amount",
                0,
            )
        )


        # Active recovery opportunities
        if action in {
            "RECOVERY_REVIEW",
            "MANUAL_REVIEW",
        }:

            if payment_id:

                recovery_eligible_ids.add(
                    payment_id
                )


        # Backward-compatible approved logic
        if (
            requires_approval is False
            and action not in {
                "NO_ACTION",
                "MONITOR",
            }
        ):

            if payment_id:

                approved_ids.add(
                    payment_id
                )

                approved_amount += amount


    # --------------------------------------------------------
    # ELIGIBLE AMOUNT
    # --------------------------------------------------------

    eligible_amount = sum(

        _safe_float(
            decision.get(
                "amount",
                0,
            )
        )

        for decision in decisions

        if isinstance(
            decision,
            dict,
        )

        and decision.get(
            "payment_id"
        ) in recovery_eligible_ids
    )


    # --------------------------------------------------------
    # DEFAULT OUTCOME METRICS
    # --------------------------------------------------------

    outcome_metrics = {

        "total_transactions":
            total_transactions,

        "recovered_transactions":
            0,

        "recovered_amount":
            0.0,

        "pending_transactions":
            0,

        "pending_amount":
            0.0,

        "created_transactions":
            0,

        "created_amount":
            0.0,

        "failed_transactions":
            0,

        "failed_amount":
            0.0,

        "eligible_amount":
            round(
                eligible_amount,
                2,
            ),

        "recovery_rate":
            0.0,

        "unrecovered_amount":
            round(
                eligible_amount,
                2,
            ),
    }


    # --------------------------------------------------------
    # OUTCOME-TRACKED PATH
    # --------------------------------------------------------

    if recovery_outcomes:

        tracked_outcomes = track_batch_outcomes(
            payments,
            recovery_outcomes,
        )

        outcome_metrics = calculate_outcome_metrics(
            tracked_outcomes,
            eligible_amount=eligible_amount,
        )


    # --------------------------------------------------------
    # BACKWARD-COMPATIBLE RECOVERED IDS
    # --------------------------------------------------------

    elif recovered_payment_ids:

        recovered_amount = 0.0

        recovered_transactions = 0


        for payment in payments:

            if not isinstance(
                payment,
                dict,
            ):
                continue

            payment_id = payment.get(
                "payment_id"
            )

            if payment_id in recovered_payment_ids:

                recovered_amount += _safe_float(
                    payment.get(
                        "amount",
                        0,
                    )
                )

                recovered_transactions += 1


        recovery_rate = 0.0

        if eligible_amount > 0:

            recovery_rate = (
                recovered_amount
                / eligible_amount
            )


        outcome_metrics = {

            "total_transactions":
                total_transactions,

            "recovered_transactions":
                recovered_transactions,

            "recovered_amount":
                round(
                    recovered_amount,
                    2,
                ),

            "pending_transactions":
                0,

            "pending_amount":
                0.0,

            "created_transactions":
                0,

            "created_amount":
                0.0,

            "failed_transactions":
                0,

            "failed_amount":
                0.0,

            "eligible_amount":
                round(
                    eligible_amount,
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
                        eligible_amount
                        - recovered_amount,
                        0,
                    ),
                    2,
                ),
        }


    # --------------------------------------------------------
    # NO OUTCOME PROVIDED
    # --------------------------------------------------------

    else:

        outcome_metrics[
            "total_transactions"
        ] = total_transactions


    # --------------------------------------------------------
    # FINAL METRICS
    # --------------------------------------------------------

    return {

        "total_transactions":
            total_transactions,

        "total_revenue":
            round(
                total_revenue,
                2,
            ),

        "total_revenue_at_risk":
            round(
                total_revenue_at_risk,
                2,
            ),

        "high_risk_transactions":
            high_risk_transactions,

        "medium_risk_transactions":
            medium_risk_transactions,

        "recovery_eligible_transactions":
            len(
                recovery_eligible_ids
            ),

        "recovery_eligible_amount":
            round(
                eligible_amount,
                2,
            ),

        "approved_transactions":
            len(
                approved_ids
            ),

        "approved_amount":
            round(
                approved_amount,
                2,
            ),

        "recovered_transactions":
            outcome_metrics.get(
                "recovered_transactions",
                0,
            ),

        "recovered_amount":
            round(
                outcome_metrics.get(
                    "recovered_amount",
                    0,
                ),
                2,
            ),

        "created_transactions":
            outcome_metrics.get(
                "created_transactions",
                0,
            ),

        "created_amount":
            round(
                outcome_metrics.get(
                    "created_amount",
                    0,
                ),
                2,
            ),

        "pending_transactions":
            outcome_metrics.get(
                "pending_transactions",
                0,
            ),

        "pending_amount":
            round(
                outcome_metrics.get(
                    "pending_amount",
                    0,
                ),
                2,
            ),

        "failed_transactions":
            outcome_metrics.get(
                "failed_transactions",
                0,
            ),

        "failed_amount":
            round(
                outcome_metrics.get(
                    "failed_amount",
                    0,
                ),
                2,
            ),

        "recovery_rate":
            round(
                outcome_metrics.get(
                    "recovery_rate",
                    0,
                ),
                4,
            ),

        "unrecovered_amount":
            round(
                outcome_metrics.get(
                    "unrecovered_amount",
                    eligible_amount,
                ),
                2,
            ),
    }


# ============================================================
# BATCH RECOVERY REPORT
# ============================================================

def build_batch_recovery_report(
    metrics: dict,
) -> str:

    return "\n".join(
        [

            "# Batch Revenue Recovery Report",

            "",

            (
                f"Transactions analyzed: "
                f"{metrics.get('total_transactions', 0)}"
            ),

            (
                f"Total revenue: ₹"
                f"{metrics.get('total_revenue', 0):,.2f}"
            ),

            (
                f"Revenue at risk: ₹"
                f"{metrics.get('total_revenue_at_risk', 0):,.2f}"
            ),

            (
                f"Recovery eligible: "
                f"{metrics.get('recovery_eligible_transactions', 0)} "
                f"transactions"
            ),

            (
                f"Eligible amount: ₹"
                f"{metrics.get('recovery_eligible_amount', 0):,.2f}"
            ),

            (
                f"Approved transactions: "
                f"{metrics.get('approved_transactions', 0)}"
            ),

            (
                f"Approved amount: ₹"
                f"{metrics.get('approved_amount', 0):,.2f}"
            ),

            (
                f"Recovered transactions: "
                f"{metrics.get('recovered_transactions', 0)}"
            ),

            (
                f"Recovered: ₹"
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
                f"Pending transactions: "
                f"{metrics.get('pending_transactions', 0)}"
            ),

            (
                f"Pending amount: ₹"
                f"{metrics.get('pending_amount', 0):,.2f}"
            ),

            (
                f"Failed transactions: "
                f"{metrics.get('failed_transactions', 0)}"
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
    "calculate_batch_recovery_metrics",
    "build_batch_recovery_report",
]