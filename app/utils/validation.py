import re


# ============================================================
# AMOUNT VALIDATION
# ============================================================

def validate_amount(amount):

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False

    return amount > 0


# ============================================================
# RECEIPT VALIDATION
# ============================================================

def validate_receipt(receipt):

    if not receipt:
        return False

    receipt = str(receipt).strip()

    if not receipt:
        return False

    # Razorpay receipt should be a reasonable
    # alphanumeric identifier.
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_-]{1,40}",
            receipt
        )
    )


# ============================================================
# ORDER ID VALIDATION
# ============================================================

def validate_order_id(order_id):

    if not order_id:
        return False

    return bool(
        re.fullmatch(
            r"order_[A-Za-z0-9]+",
            str(order_id).strip()
        )
    )


# ============================================================
# PAYMENT ID VALIDATION
# ============================================================

def validate_payment_id(payment_id):

    if not payment_id:
        return False

    return bool(
        re.fullmatch(
            r"pay_[A-Za-z0-9]+",
            str(payment_id).strip()
        )
    )


# ============================================================
# REFUND ID VALIDATION
# ============================================================

def validate_refund_id(refund_id):

    if not refund_id:
        return False

    return bool(
        re.fullmatch(
            r"rfnd_[A-Za-z0-9]+",
            str(refund_id).strip()
        )
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "validate_amount",
    "validate_receipt",
    "validate_order_id",
    "validate_payment_id",
    "validate_refund_id",
]