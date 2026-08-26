# ============================================================
# REVENUE RECOVERY - PAYMENT NORMALIZER
# ============================================================

from typing import Any


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
    payment: dict,
) -> str:

    status = payment.get(
        "status"
    )

    if status:
        return str(
            status
        ).lower()

    return "unknown"


# ============================================================
# NORMALIZE ONE PAYMENT
# ============================================================

def normalize_payment(
    payment: dict,
) -> dict:

    if not isinstance(
        payment,
        dict,
    ):
        return {}


    # --------------------------------------------------------
    # CORE PAYMENT FIELDS
    # --------------------------------------------------------

    payment_id = (
        payment.get(
            "payment_id"
        )
        or payment.get(
            "id"
        )
    )


    amount = _safe_float(
        payment.get(
            "amount",
            0,
        )
    )


    currency = str(
        payment.get(
            "currency",
            "INR",
        )
    ).upper()


    status = _normalize_status(
        payment
    )


    # --------------------------------------------------------
    # DERIVED / HISTORY FIELDS
    # --------------------------------------------------------

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


    previous_successes = _safe_int(
        payment.get(
            "previous_successes",
            0,
        )
    )


    # --------------------------------------------------------
    # CAPTURED STATUS
    # --------------------------------------------------------

    captured = payment.get(
        "captured"
    )


    if captured is True:

        normalized_status = "captured"

    elif status in {
        "captured",
        "paid",
        "success",
        "successful",
    }:

        normalized_status = "captured"

    else:

        normalized_status = status


    # --------------------------------------------------------
    # SAFE ATTEMPT FALLBACK
    # --------------------------------------------------------

    if (
        attempts == 0
        and failed_attempts > 0
    ):

        attempts = failed_attempts


    # --------------------------------------------------------
    # STANDARDIZED PAYMENT
    # --------------------------------------------------------

    normalized = {

        "payment_id":
            payment_id,

        "amount":
            amount,

        "currency":
            currency,

        "status":
            normalized_status,

        "failed_attempts":
            failed_attempts,

        "attempts":
            attempts,

        "previous_successes":
            previous_successes,
    }


    # --------------------------------------------------------
    # PRESERVE CUSTOMER / IDENTITY FIELDS
    # --------------------------------------------------------
    #
    # These are required by the historical enrichment layer.
    # Do NOT discard them.
    # --------------------------------------------------------

    for field in (

        "customer_id",

        "customer_email",

        "email",

        "customer_contact",

        "contact",

        "customer_phone",

    ):

        if field in payment:

            normalized[field] = (
                payment[field]
            )


    # --------------------------------------------------------
    # PRESERVE OTHER USEFUL RAZORPAY FIELDS
    # --------------------------------------------------------

    for field in (

        "order_id",

        "invoice_id",

        "method",

        "created_at",

    ):

        if field in payment:

            normalized[field] = (
                payment[field]
            )


    return normalized


# ============================================================
# NORMALIZE BATCH
# ============================================================

def normalize_payments(
    payments: list[dict],
) -> list[dict]:

    normalized = []

    for payment in payments:

        result = normalize_payment(
            payment
        )

        if result:

            normalized.append(
                result
            )

    return normalized


# ============================================================
# VALIDATION
# ============================================================

def validate_normalized_payment(
    payment: dict,
) -> bool:

    if not isinstance(
        payment,
        dict,
    ):

        return False


    payment_id = payment.get(
        "payment_id"
    )

    if not payment_id:

        return False


    amount = payment.get(
        "amount"
    )

    if not isinstance(
        amount,
        (int, float),
    ):

        return False


    if amount < 0:

        return False


    currency = payment.get(
        "currency"
    )

    if not currency:

        return False


    status = payment.get(
        "status"
    )

    if not status:

        return False


    return True


# ============================================================
# FILTER VALID PAYMENTS
# ============================================================

def filter_valid_payments(
    payments: list[dict],
) -> list[dict]:

    result = []

    for payment in payments:

        if validate_normalized_payment(
            payment
        ):

            result.append(
                payment
            )

    return result


# ============================================================
# NORMALIZE + VALIDATE
# ============================================================

def normalize_and_validate_payments(
    payments: list[dict],
) -> list[dict]:

    normalized = normalize_payments(
        payments
    )

    return filter_valid_payments(
        normalized
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "normalize_payment",

    "normalize_payments",

    "validate_normalized_payment",

    "filter_valid_payments",

    "normalize_and_validate_payments",
]