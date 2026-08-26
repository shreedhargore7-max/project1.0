# ============================================================
# REVENUE RECOVERY - EVALUATION ENGINE
# ============================================================

from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _get_payment_id(
    item: dict,
) -> str | None:

    return item.get(
        "payment_id"
    )


# ============================================================
# RISK EVALUATION
# ============================================================

def evaluate_risk_predictions(
    expected: dict[str, str],
    actual_results: list[dict],
) -> dict:

    actual = {
        item.get("payment_id"):
            item.get("risk_level")
        for item in actual_results
        if item.get("payment_id")
    }

    total = len(expected)

    correct = sum(
        1
        for payment_id, expected_level
        in expected.items()
        if actual.get(payment_id)
        == expected_level
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": round(
            accuracy,
            4,
        ),
    }


# ============================================================
# DECISION EVALUATION
# ============================================================

def evaluate_decisions(
    expected: dict[str, str],
    actual_results: list[dict],
) -> dict:

    actual = {
        item.get("payment_id"):
            item.get("action")
        for item in actual_results
        if item.get("payment_id")
    }

    total = len(expected)

    correct = sum(
        1
        for payment_id, expected_action
        in expected.items()
        if actual.get(payment_id)
        == expected_action
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": round(
            accuracy,
            4,
        ),
    }


# ============================================================
# PRIORITY EVALUATION
# ============================================================

def evaluate_priorities(
    expected: dict[str, str],
    actual_results: list[dict],
) -> dict:

    actual = {
        item.get("payment_id"):
            item.get("priority")
        for item in actual_results
        if item.get("payment_id")
    }

    total = len(expected)

    correct = sum(
        1
        for payment_id, expected_priority
        in expected.items()
        if actual.get(payment_id)
        == expected_priority
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": round(
            accuracy,
            4,
        ),
    }


# ============================================================
# APPROVAL SAFETY EVALUATION
# ============================================================

def evaluate_approval_safety(
    decisions: list[dict],
) -> dict:

    write_actions = {
        "RECOVERY_REVIEW",
        "MANUAL_REVIEW",
    }

    protected = 0
    violations = 0

    for decision in decisions:

        action = decision.get(
            "action"
        )

        requires_approval = (
            decision.get(
                "requires_approval",
                False,
            )
        )

        if action in write_actions:

            if requires_approval:
                protected += 1

            else:
                violations += 1

    total_sensitive = (
        protected + violations
    )

    safety_rate = (
        protected / total_sensitive
        if total_sensitive
        else 1.0
    )

    return {
        "sensitive_actions":
            total_sensitive,

        "protected":
            protected,

        "violations":
            violations,

        "safety_rate":
            round(
                safety_rate,
                4,
            ),
    }


# ============================================================
# PRIORITY ORDER EVALUATION
# ============================================================

def evaluate_top_priority(
    expected_payment_id: str,
    prioritized_results: list[dict],
) -> dict:

    actual_top = None

    if prioritized_results:

        actual_top = (
            prioritized_results[0]
            .get("payment_id")
        )

    correct = (
        actual_top
        == expected_payment_id
    )

    return {
        "expected":
            expected_payment_id,

        "actual":
            actual_top,

        "correct":
            correct,
    }


# ============================================================
# COMPLETE EVALUATION
# ============================================================

def evaluate_recovery_system(
    *,
    expected_risk_levels: dict[str, str],
    expected_actions: dict[str, str],
    expected_priorities: dict[str, str],
    expected_top_payment: str,
    risk_results: list[dict],
    decisions: list[dict],
    prioritized_decisions: list[dict],
) -> dict:

    risk_metrics = evaluate_risk_predictions(
        expected_risk_levels,
        risk_results,
    )

    decision_metrics = evaluate_decisions(
        expected_actions,
        decisions,
    )

    priority_metrics = evaluate_priorities(
        expected_priorities,
        decisions,
    )

    approval_metrics = evaluate_approval_safety(
        decisions,
    )

    top_priority = evaluate_top_priority(
        expected_top_payment,
        prioritized_decisions,
    )

    return {
        "risk": risk_metrics,
        "decisions": decision_metrics,
        "priorities": priority_metrics,
        "approval_safety": approval_metrics,
        "top_priority": top_priority,
    }


# ============================================================
# BUILD REPORT
# ============================================================

def build_evaluation_report(
    evaluation: dict,
) -> str:

    risk = evaluation[
        "risk"
    ]

    decisions = evaluation[
        "decisions"
    ]

    priorities = evaluation[
        "priorities"
    ]

    approval = evaluation[
        "approval_safety"
    ]

    top = evaluation[
        "top_priority"
    ]

    lines = [

        "# Revenue Recovery Evaluation",

        "",

        (
            f"Risk accuracy: "
            f"{risk['accuracy'] * 100:.1f}%"
        ),

        (
            f"Decision accuracy: "
            f"{decisions['accuracy'] * 100:.1f}%"
        ),

        (
            f"Priority accuracy: "
            f"{priorities['accuracy'] * 100:.1f}%"
        ),

        (
            f"Approval safety: "
            f"{approval['safety_rate'] * 100:.1f}%"
        ),

        (
            f"Top-priority selection: "
            f"{'PASS' if top['correct'] else 'FAIL'}"
        ),

        "",

        "Safety violations: "
        f"{approval['violations']}",

    ]

    return "\n".join(
        lines
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "evaluate_risk_predictions",
    "evaluate_decisions",
    "evaluate_priorities",
    "evaluate_approval_safety",
    "evaluate_top_priority",
    "evaluate_recovery_system",
    "build_evaluation_report",
]