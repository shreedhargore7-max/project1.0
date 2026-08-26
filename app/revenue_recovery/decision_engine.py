# ============================================================
# REVENUE RECOVERY - DECISION ENGINE
# ============================================================

from typing import Any


# ============================================================
# ACTIONS
# ============================================================

ACTION_NONE = "NO_ACTION"
ACTION_MONITOR = "MONITOR"
ACTION_RECOVERY_REVIEW = "RECOVERY_REVIEW"
ACTION_MANUAL_REVIEW = "MANUAL_REVIEW"


# ============================================================
# PRIORITIES
# ============================================================

PRIORITY_LOW = "LOW"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_HIGH = "HIGH"


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
# SUCCESS STATUS
# ============================================================

def _is_successful_status(
    status: str,
) -> bool:

    return status in {
        "paid",
        "captured",
        "success",
        "successful",
        "completed",
    }


# ============================================================
# SINGLE PAYMENT DECISION
# ============================================================

def decide_recovery_action(
    payment: dict,
    risk_result: dict,
    root_cause_result: dict,
) -> dict:

    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )

    status = str(
        payment.get(
            "status",
            "",
        )
    ).lower().strip()

    risk_score = _safe_int(
        risk_result.get(
            "risk_score",
            0,
        )
    )

    risk_level = str(
        risk_result.get(
            "risk_level",
            "LOW",
        )
    ).upper().strip()

    causes = root_cause_result.get(
        "root_causes",
        [],
    )

    if not isinstance(
        causes,
        list,
    ):
        causes = []


    # --------------------------------------------------------
    # SUCCESSFUL PAYMENT
    # --------------------------------------------------------

    if _is_successful_status(
        status
    ):

        return {
            "action":
                ACTION_NONE,

            "priority":
                PRIORITY_LOW,

            "requires_approval":
                False,

            "reason":
                "Payment is already successful. "
                "No recovery action is required.",
        }


    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if risk_level == "HIGH":

        # ----------------------------------------------------
        # HIGH VALUE
        # ----------------------------------------------------

        if amount >= 10000:

            return {
                "action":
                    ACTION_MANUAL_REVIEW,

                "priority":
                    PRIORITY_HIGH,

                "requires_approval":
                    True,

                "reason":
                    "The transaction is high risk and "
                    "high value. A human should review "
                    "the recovery action before execution.",
            }


        # ----------------------------------------------------
        # REPEATED FAILURE
        # ----------------------------------------------------

        if (
            "repeated_failure"
            in causes
        ):

            return {
                "action":
                    ACTION_RECOVERY_REVIEW,

                "priority":
                    PRIORITY_HIGH,

                "requires_approval":
                    True,

                "reason":
                    "The payment has repeated failures. "
                    "It should be reviewed for a permitted "
                    "recovery intervention.",
            }


        # ----------------------------------------------------
        # OTHER HIGH-RISK PAYMENT
        # ----------------------------------------------------

        return {
            "action":
                ACTION_RECOVERY_REVIEW,

            "priority":
                PRIORITY_HIGH,

            "requires_approval":
                True,

            "reason":
                "The payment has been classified as high "
                "risk and requires human review before "
                "recovery.",
        }


    # --------------------------------------------------------
    # MEDIUM RISK
    # --------------------------------------------------------

    if risk_level == "MEDIUM":

        return {
            "action":
                ACTION_RECOVERY_REVIEW,

            "priority":
                PRIORITY_MEDIUM,

            "requires_approval":
                True,

            "reason":
                "The transaction has meaningful risk "
                "indicators and should be reviewed before "
                "a recovery action is taken.",
        }


    # --------------------------------------------------------
    # LOW RISK
    # --------------------------------------------------------

    if risk_level == "LOW":

        return {
            "action":
                ACTION_MONITOR,

            "priority":
                PRIORITY_LOW,

            "requires_approval":
                False,

            "reason":
                "Risk is currently low. "
                "Monitor the transaction for further changes.",
        }


    # --------------------------------------------------------
    # SCORE FALLBACK
    # --------------------------------------------------------

    if risk_score >= 75:

        return {
            "action":
                ACTION_RECOVERY_REVIEW,

            "priority":
                PRIORITY_HIGH,

            "requires_approval":
                True,

            "reason":
                "The risk score is high and the transaction "
                "requires human review.",
        }


    if risk_score >= 40:

        return {
            "action":
                ACTION_RECOVERY_REVIEW,

            "priority":
                PRIORITY_MEDIUM,

            "requires_approval":
                True,

            "reason":
                "The risk score indicates meaningful "
                "recovery risk.",
        }


    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    return {
        "action":
            ACTION_MONITOR,

        "priority":
            PRIORITY_LOW,

        "requires_approval":
            False,

        "reason":
            "No active recovery action is required. "
            "Continue monitoring.",
    }


# ============================================================
# BATCH DECISIONS
# ============================================================

def decide_batch_actions(
    payments: list[dict],
    risk_results: list[dict],
    root_cause_results: list[dict],
) -> list[dict]:

    results = []

    # --------------------------------------------------------
    # MAP RISK RESULTS BY PAYMENT ID
    # --------------------------------------------------------

    risk_by_payment_id = {
        result.get("payment_id"): result
        for result in risk_results
        if isinstance(
            result,
            dict,
        )
        and result.get(
            "payment_id"
        )
    }

    # --------------------------------------------------------
    # MAP ROOT CAUSES BY PAYMENT ID
    # --------------------------------------------------------

    root_cause_by_payment_id = {
        result.get("payment_id"): result
        for result in root_cause_results
        if isinstance(
            result,
            dict,
        )
        and result.get(
            "payment_id"
        )
    }

    # --------------------------------------------------------
    # BUILD DECISIONS
    # --------------------------------------------------------

    for index, payment in enumerate(
        payments
    ):

        if not isinstance(
            payment,
            dict,
        ):
            continue

        payment_id = payment.get(
            "payment_id"
        )

        # ----------------------------------------------------
        # PRIMARY MATCH: PAYMENT ID
        # ----------------------------------------------------

        risk_result = (
            risk_by_payment_id.get(
                payment_id
            )
        )

        root_cause_result = (
            root_cause_by_payment_id.get(
                payment_id
            )
        )

        # ----------------------------------------------------
        # FALLBACK FOR LEGACY TEST DATA
        # ----------------------------------------------------

        if risk_result is None:

            if (
                index < len(risk_results)
                and isinstance(
                    risk_results[index],
                    dict,
                )
            ):

                risk_result = (
                    risk_results[index]
                )

            else:

                risk_result = {}


        if root_cause_result is None:

            if (
                index < len(root_cause_results)
                and isinstance(
                    root_cause_results[index],
                    dict,
                )
            ):

                root_cause_result = (
                    root_cause_results[index]
                )

            else:

                root_cause_result = {}


        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        decision = decide_recovery_action(
            payment,
            risk_result,
            root_cause_result,
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

            **decision,
        })

    return results


# ============================================================
# PRIORITIZATION
# ============================================================

def prioritize_decisions(
    decisions: list[dict],
) -> list[dict]:

    priority_order = {
        PRIORITY_HIGH: 3,
        PRIORITY_MEDIUM: 2,
        PRIORITY_LOW: 1,
    }

    return sorted(
        decisions,
        key=lambda item: (

            priority_order.get(
                item.get(
                    "priority"
                ),
                0,
            ),

            _safe_float(
                item.get(
                    "amount",
                    0,
                )
            ),
        ),
        reverse=True,
    )


# ============================================================
# SUMMARY
# ============================================================

def build_decision_summary(
    decisions: list[dict],
) -> dict:

    high = sum(
        1
        for item in decisions
        if item.get(
            "priority"
        )
        == PRIORITY_HIGH
    )

    medium = sum(
        1
        for item in decisions
        if item.get(
            "priority"
        )
        == PRIORITY_MEDIUM
    )

    low = sum(
        1
        for item in decisions
        if item.get(
            "priority"
        )
        == PRIORITY_LOW
    )

    approval_required = sum(
        1
        for item in decisions
        if item.get(
            "requires_approval"
        )
        is True
    )

    recovery_review = sum(
        1
        for item in decisions
        if item.get(
            "action"
        )
        == ACTION_RECOVERY_REVIEW
    )

    manual_review = sum(
        1
        for item in decisions
        if item.get(
            "action"
        )
        == ACTION_MANUAL_REVIEW
    )

    monitor = sum(
        1
        for item in decisions
        if item.get(
            "action"
        )
        == ACTION_MONITOR
    )

    no_action = sum(
        1
        for item in decisions
        if item.get(
            "action"
        )
        == ACTION_NONE
    )

    return {

        "total_decisions":
            len(decisions),

        "high_priority":
            high,

        "medium_priority":
            medium,

        "low_priority":
            low,

        "approval_required":
            approval_required,

        "recovery_review":
            recovery_review,

        "manual_review":
            manual_review,

        "monitor":
            monitor,

        "no_action":
            no_action,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "ACTION_NONE",

    "ACTION_MONITOR",

    "ACTION_RECOVERY_REVIEW",

    "ACTION_MANUAL_REVIEW",

    "PRIORITY_LOW",

    "PRIORITY_MEDIUM",

    "PRIORITY_HIGH",

    "decide_recovery_action",

    "decide_batch_actions",

    "prioritize_decisions",

    "build_decision_summary",
]