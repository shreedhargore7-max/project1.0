# ============================================================
# TESTS - HELD-OUT EVALUATION
# ============================================================

import json
from pathlib import Path

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
    evaluate_recovery_eligibility,
    default_recovery_policy,
)


# ============================================================
# DATASET
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "revenue_recovery"
    / "evaluation_payments.json"
)


def load_evaluation_payments():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# HELD-OUT PREDICTION
# ============================================================

def evaluate_payment(
    payment: dict,
) -> dict:

    risk = analyze_payment(
        payment
    )

    root_cause = analyze_root_cause(
        payment
    )

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    policy = evaluate_recovery_eligibility(
        payment,
        risk,
        default_recovery_policy(),
    )

    return {
        "payment_id":
            payment.get(
                "payment_id"
            ),

        "risk_level":
            risk.get(
                "risk_level"
            ),

        "action":
            decision.get(
                "action"
            ),

        "priority":
            decision.get(
                "priority"
            ),

        "requires_approval":
            decision.get(
                "requires_approval",
                False,
            ),

        "policy_eligible":
            policy.get(
                "eligible",
                False,
            ),

        "policy_action":
            policy.get(
                "action"
            ),
    }


# ============================================================
# ACCURACY HELPERS
# ============================================================

def accuracy(
    correct: int,
    total: int,
) -> float:

    if total == 0:
        return 0.0

    return correct / total


# ============================================================
# RISK ACCURACY
# ============================================================

def test_heldout_risk_accuracy():

    payments = load_evaluation_payments()

    correct = 0

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        if (
            result["risk_level"]
            == payment["expected_risk_level"]
        ):
            correct += 1

    score = accuracy(
        correct,
        len(payments),
    )

    assert score >= 0.80


# ============================================================
# DECISION ACCURACY
# ============================================================

def test_heldout_decision_accuracy():

    payments = load_evaluation_payments()

    correct = 0

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        if (
            result["action"]
            == payment["expected_action"]
        ):
            correct += 1

    score = accuracy(
        correct,
        len(payments),
    )

    assert score >= 0.80


# ============================================================
# PRIORITY ACCURACY
# ============================================================

def test_heldout_priority_accuracy():

    payments = load_evaluation_payments()

    correct = 0

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        if (
            result["priority"]
            == payment["expected_priority"]
        ):
            correct += 1

    score = accuracy(
        correct,
        len(payments),
    )

    assert score >= 0.80


# ============================================================
# APPROVAL SAFETY
# ============================================================

def test_heldout_approval_safety():

    payments = load_evaluation_payments()

    unsafe = 0

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        expected_approval = payment[
            "expected_requires_approval"
        ]

        if (
            result["requires_approval"]
            != expected_approval
        ):
            unsafe += 1

    assert unsafe == 0


# ============================================================
# POLICY SAFETY
# ============================================================

def test_heldout_policy_safety():

    payments = load_evaluation_payments()

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        # A successful payment must never be eligible
        # for active recovery.

        status = str(
            payment.get(
                "status",
                "",
            )
        ).lower()

        if status == "captured":

            assert (
                result["policy_eligible"]
                is False
            )

            assert (
                result["policy_action"]
                == "STOP"
            )


# ============================================================
# HIGH-VALUE SAFETY
# ============================================================

def test_heldout_high_value_payments_require_review():

    payments = load_evaluation_payments()

    for payment in payments:

        if (
            payment["amount"] >= 10000
            and payment["expected_risk_level"]
            == "HIGH"
        ):

            result = evaluate_payment(
                payment
            )

            assert (
                result["action"]
                == "MANUAL_REVIEW"
            )

            assert (
                result["requires_approval"]
                is True
            )


# ============================================================
# COMPLETE EVALUATION
# ============================================================

def test_complete_heldout_evaluation():

    payments = load_evaluation_payments()

    assert len(
        payments
    ) == 10

    results = [
        evaluate_payment(
            payment
        )
        for payment in payments
    ]

    assert len(results) == 10

    for result in results:

        assert (
            result["payment_id"]
        )

        assert (
            result["risk_level"]
            in {
                "LOW",
                "MEDIUM",
                "HIGH",
            }
        )

        assert result[
            "action"
        ]

        assert result[
            "priority"
        ]


# ============================================================
# EVALUATION REPORT
# ============================================================

def build_evaluation_report():

    payments = load_evaluation_payments()

    total = len(
        payments
    )

    risk_correct = 0
    decision_correct = 0
    priority_correct = 0
    approval_correct = 0

    for payment in payments:

        result = evaluate_payment(
            payment
        )

        if (
            result["risk_level"]
            == payment["expected_risk_level"]
        ):

            risk_correct += 1

        if (
            result["action"]
            == payment["expected_action"]
        ):

            decision_correct += 1

        if (
            result["priority"]
            == payment["expected_priority"]
        ):

            priority_correct += 1

        if (
            result["requires_approval"]
            == payment["expected_requires_approval"]
        ):

            approval_correct += 1

    return {

        "total":
            total,

        "risk_accuracy":
            accuracy(
                risk_correct,
                total,
            ),

        "decision_accuracy":
            accuracy(
                decision_correct,
                total,
            ),

        "priority_accuracy":
            accuracy(
                priority_correct,
                total,
            ),

        "approval_safety":
            accuracy(
                approval_correct,
                total,
            ),
    }


def test_evaluation_report():

    report = build_evaluation_report()

    assert (
        report["total"]
        == 10
    )

    assert (
        report["risk_accuracy"]
        >= 0.80
    )

    assert (
        report["decision_accuracy"]
        >= 0.80
    )

    assert (
        report["priority_accuracy"]
        >= 0.80
    )

    assert (
        report["approval_safety"]
        == 1.0
    )


# ============================================================
# PRINT REPORT
# ============================================================

def test_print_heldout_evaluation_report():

    report = build_evaluation_report()

    print(
        "\n"
        "========================================\n"
        "HELD-OUT EVALUATION REPORT\n"
        "========================================"
    )

    print(
        f"Transactions evaluated: "
        f"{report['total']}"
    )

    print(
        f"Risk accuracy: "
        f"{report['risk_accuracy'] * 100:.2f}%"
    )

    print(
        f"Decision accuracy: "
        f"{report['decision_accuracy'] * 100:.2f}%"
    )

    print(
        f"Priority accuracy: "
        f"{report['priority_accuracy'] * 100:.2f}%"
    )

    print(
        f"Approval safety: "
        f"{report['approval_safety'] * 100:.2f}%"
    )

    print(
        "========================================"
    )