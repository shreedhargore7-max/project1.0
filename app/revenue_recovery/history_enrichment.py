# ============================================================
# REVENUE RECOVERY - HISTORICAL PAYMENT ENRICHMENT
# ============================================================

from collections import defaultdict
from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _safe_int(
    value: Any,
    default: int = 0,
) -> int:

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_successful(
    payment: dict,
) -> bool:

    status = str(
        payment.get(
            "status",
            "",
        )
    ).lower().strip()

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


def _is_failed(
    payment: dict,
) -> bool:

    status = str(
        payment.get(
            "status",
            "",
        )
    ).lower().strip()

    return status in {
        "failed",
        "failure",
        "error",
    }


# ============================================================
# CUSTOMER / PAYMENT GROUP KEY
# ============================================================

def build_history_key(
    payment: dict,
    index: int,
) -> str:
    """
    Build a safe grouping key.

    Preferred identity:
        customer_id
        customer email
        customer contact
        customer_phone

    If no customer identity exists, isolate the payment
    using a deterministic payment-specific key.
    """

    for field in (
        "customer_id",
        "customer_email",
        "email",
        "customer_contact",
        "contact",
        "customer_phone",
    ):

        value = payment.get(
            field
        )

        if value:

            return (
                f"{field}:"
                f"{str(value).strip().lower()}"
            )

    payment_id = payment.get(
        "payment_id"
    )

    if payment_id:

        return f"payment:{payment_id}"

    return f"anonymous:{index}"


# ============================================================
# HISTORY SUMMARY
# ============================================================

def build_history_summary(
    payments: list[dict],
) -> dict[str, dict]:
    """
    Aggregate historical payment behavior by customer.

    Returns one summary per customer/group.
    """

    grouped: dict[str, list[dict]] = (
        defaultdict(list)
    )

    for index, payment in enumerate(
        payments
    ):

        if not isinstance(
            payment,
            dict,
        ):
            continue

        key = build_history_key(
            payment,
            index,
        )

        grouped[key].append(
            payment
        )

    summaries = {}

    for key, records in grouped.items():

        total_attempts = 0

        failed_attempts = 0

        successful_payments = 0

        failed_payments = 0

        total_value = 0.0

        successful_value = 0.0

        failed_value = 0.0

        for payment in records:

            amount = _safe_float(
                payment.get(
                    "amount",
                    0,
                )
            )

            explicit_attempts = _safe_int(
                payment.get(
                    "attempts",
                    0,
                )
            )

            explicit_failed = _safe_int(
                payment.get(
                    "failed_attempts",
                    0,
                )
            )

            is_success = _is_successful(
                payment
            )

            is_failure = _is_failed(
                payment
            )

            if explicit_attempts > 0:

                total_attempts += (
                    explicit_attempts
                )

            else:

                total_attempts += 1

            if explicit_failed > 0:

                failed_attempts += (
                    explicit_failed
                )

            elif is_failure:

                failed_attempts += 1

            total_value += amount

            if is_success:

                successful_payments += 1

                successful_value += amount

            if is_failure:

                failed_payments += 1

                failed_value += amount

        failure_rate = 0.0

        if total_attempts > 0:

            failure_rate = (
                failed_attempts
                / total_attempts
            )

        summaries[key] = {
            "history_key": key,
            "history_count": len(records),
            "attempts": total_attempts,
            "failed_attempts": failed_attempts,
            "previous_successes": (
                successful_payments
            ),
            "failed_payments": (
                failed_payments
            ),
            "failure_rate": round(
                failure_rate,
                4,
            ),
            "total_value": round(
                total_value,
                2,
            ),
            "successful_value": round(
                successful_value,
                2,
            ),
            "failed_value": round(
                failed_value,
                2,
            ),
        }

    return summaries


# ============================================================
# ENRICH PAYMENTS
# ============================================================

def enrich_payment_history(
    payments: list[dict],
) -> list[dict]:
    """
    Add derived historical features to every payment.

    Existing explicitly supplied values are preserved when
    they are greater than the derived values.
    """

    if not payments:

        return []

    summaries = build_history_summary(
        payments
    )

    enriched = []

    for index, payment in enumerate(
        payments
    ):

        if not isinstance(
            payment,
            dict,
        ):
            continue

        key = build_history_key(
            payment,
            index,
        )

        history = summaries.get(
            key,
            {},
        )

        current = dict(
            payment
        )

        # ----------------------------------------------------
        # Derived history
        # ----------------------------------------------------

        derived_attempts = _safe_int(
            history.get(
                "attempts",
                0,
            )
        )

        derived_failed = _safe_int(
            history.get(
                "failed_attempts",
                0,
            )
        )

        derived_successes = _safe_int(
            history.get(
                "previous_successes",
                0,
            )
        )

        # ----------------------------------------------------
        # Preserve explicitly supplied values
        # ----------------------------------------------------

        existing_attempts = _safe_int(
            current.get(
                "attempts",
                0,
            )
        )

        existing_failed = _safe_int(
            current.get(
                "failed_attempts",
                0,
            )
        )

        existing_successes = _safe_int(
            current.get(
                "previous_successes",
                0,
            )
        )

        current["attempts"] = max(
            existing_attempts,
            derived_attempts,
        )

        current["failed_attempts"] = max(
            existing_failed,
            derived_failed,
        )

        current["previous_successes"] = max(
            existing_successes,
            derived_successes,
        )

        # ----------------------------------------------------
        # Extra features
        # ----------------------------------------------------

        current["failure_rate"] = (
            history.get(
                "failure_rate",
                0.0,
            )
        )

        current["history_count"] = (
            history.get(
                "history_count",
                1,
            )
        )

        current["customer_history_key"] = (
            key
        )

        current["historical_total_value"] = (
            history.get(
                "total_value",
                0.0,
            )
        )

        current["historical_successful_value"] = (
            history.get(
                "successful_value",
                0.0,
            )
        )

        current["historical_failed_value"] = (
            history.get(
                "failed_value",
                0.0,
            )
        )

        enriched.append(
            current
        )

    return enriched


# ============================================================
# BATCH METRICS
# ============================================================

def calculate_batch_history_metrics(
    payments: list[dict],
) -> dict:

    if not payments:
        return {
            "total_payments": 0,
            "total_attempts": 0,
            "total_failed_attempts": 0,
            "total_successes": 0,
            "failure_rate": 0.0,
        }

    summaries = build_history_summary(
        payments
    )

    total_attempts = sum(
        _safe_int(
            summary.get(
                "attempts",
                0,
            )
        )
        for summary in summaries.values()
    )

    total_failed_attempts = sum(
        _safe_int(
            summary.get(
                "failed_attempts",
                0,
            )
        )
        for summary in summaries.values()
    )

    total_successes = sum(
        _safe_int(
            summary.get(
                "previous_successes",
                0,
            )
        )
        for summary in summaries.values()
    )

    failure_rate = 0.0

    if total_attempts > 0:
        failure_rate = (
            total_failed_attempts
            / total_attempts
        )

    return {
        "total_payments": len(payments),
        "total_attempts": total_attempts,
        "total_failed_attempts": total_failed_attempts,
        "total_successes": total_successes,
        "failure_rate": round(
            failure_rate,
            4,
        ),
    }
