from app.revenue_recovery.payment_normalizer import (
    normalize_payment,
    normalize_payments,
    validate_normalized_payment,
    filter_valid_payments,
    normalize_and_validate_payments,
)


# ============================================================
# BASIC DEMO PAYMENT
# ============================================================

def test_normalize_demo_payment():

    payment = {

        "payment_id":
            "pay_DEMO001",

        "amount":
            20000,

        "currency":
            "INR",

        "status":
            "failed",

        "failed_attempts":
            4,

        "attempts":
            5,

        "previous_successes":
            6,
    }


    result = normalize_payment(
        payment
    )


    assert (
        result["payment_id"]
        == "pay_DEMO001"
    )

    assert (
        result["amount"]
        == 20000
    )

    assert (
        result["currency"]
        == "INR"
    )

    assert (
        result["status"]
        == "failed"
    )

    assert (
        result["failed_attempts"]
        == 4
    )

    assert (
        result["attempts"]
        == 5
    )

    assert (
        result["previous_successes"]
        == 6
    )


# ============================================================
# REALISTIC RAZORPAY PAYMENT
# ============================================================

def test_normalize_realistic_razorpay_payment():

    payment = {

        "id":
            "pay_REAL001",

        "amount":
            5000,

        "currency":
            "INR",

        "status":
            "captured",

        "captured":
            True,

        "order_id":
            "order_ABC123",

        "method":
            "upi",
    }


    result = normalize_payment(
        payment
    )


    assert (
        result["payment_id"]
        == "pay_REAL001"
    )

    assert (
        result["amount"]
        == 5000
    )

    assert (
        result["status"]
        == "captured"
    )

    assert (
        result["order_id"]
        == "order_ABC123"
    )

    assert (
        result["method"]
        == "upi"
    )


# ============================================================
# FAILED ATTEMPTS
# ============================================================

def test_failed_attempts_preserved():

    payment = {

        "id":
            "pay_REAL002",

        "amount":
            10000,

        "currency":
            "INR",

        "status":
            "failed",

        "failed_attempts":
            3,
    }


    result = normalize_payment(
        payment
    )


    assert (
        result["failed_attempts"]
        == 3
    )

    assert (
        result["attempts"]
        == 3
    )


# ============================================================
# CUSTOMER ID PRESERVATION
# ============================================================

def test_customer_id_is_preserved():

    payment = {

        "id":
            "pay_CUSTOMER001",

        "customer_id":
            "cust_001",

        "amount":
            5000,

        "currency":
            "INR",

        "status":
            "failed",
    }


    result = normalize_payment(
        payment
    )


    assert (
        result["customer_id"]
        == "cust_001"
    )


# ============================================================
# CUSTOMER EMAIL PRESERVATION
# ============================================================

def test_customer_email_is_preserved():

    payment = {

        "id":
            "pay_CUSTOMER002",

        "customer_email":
            "customer@example.com",

        "amount":
            3000,

        "currency":
            "INR",

        "status":
            "failed",
    }


    result = normalize_payment(
        payment
    )


    assert (
        result["customer_email"]
        == "customer@example.com"
    )


# ============================================================
# BATCH NORMALIZATION
# ============================================================

def test_batch_normalization():

    payments = [

        {

            "id":
                "pay_001",

            "amount":
                1000,

            "currency":
                "INR",

            "status":
                "captured",
        },

        {

            "id":
                "pay_002",

            "amount":
                2000,

            "currency":
                "INR",

            "status":
                "failed",
        },
    ]


    result = normalize_payments(
        payments
    )


    assert len(result) == 2


    assert (
        result[0]["payment_id"]
        == "pay_001"
    )


    assert (
        result[1]["payment_id"]
        == "pay_002"
    )


# ============================================================
# VALID PAYMENT
# ============================================================

def test_valid_payment():

    payment = {

        "payment_id":
            "pay_VALID001",

        "amount":
            1000,

        "currency":
            "INR",

        "status":
            "failed",
    }


    assert (
        validate_normalized_payment(
            payment
        )
        is True
    )


# ============================================================
# INVALID PAYMENT ID
# ============================================================

def test_invalid_payment_id():

    payment = {

        "payment_id":
            "",

        "amount":
            1000,

        "currency":
            "INR",

        "status":
            "failed",
    }


    assert (
        validate_normalized_payment(
            payment
        )
        is False
    )


# ============================================================
# INVALID AMOUNT
# ============================================================

def test_invalid_amount():

    payment = {

        "payment_id":
            "pay_INVALID001",

        "amount":
            "invalid",

        "currency":
            "INR",

        "status":
            "failed",
    }


    assert (
        validate_normalized_payment(
            payment
        )
        is False
    )


# ============================================================
# NEGATIVE AMOUNT
# ============================================================

def test_negative_amount():

    payment = {

        "payment_id":
            "pay_INVALID002",

        "amount":
            -100,

        "currency":
            "INR",

        "status":
            "failed",
    }


    assert (
        validate_normalized_payment(
            payment
        )
        is False
    )


# ============================================================
# FILTER VALID PAYMENTS
# ============================================================

def test_filter_valid_payments():

    payments = [

        {

            "payment_id":
                "pay_VALID001",

            "amount":
                1000,

            "currency":
                "INR",

            "status":
                "failed",
        },

        {

            "payment_id":
                "",

            "amount":
                2000,

            "currency":
                "INR",

            "status":
                "failed",
        },
    ]


    result = filter_valid_payments(
        payments
    )


    assert len(result) == 1


    assert (
        result[0]["payment_id"]
        == "pay_VALID001"
    )


# ============================================================
# NORMALIZE + VALIDATE
# ============================================================

def test_normalize_and_validate():

    payments = [

        {

            "id":
                "pay_FINAL001",

            "amount":
                5000,

            "currency":
                "INR",

            "status":
                "failed",
        },

        {

            "id":
                "",

            "amount":
                2000,

            "currency":
                "INR",

            "status":
                "failed",
        },
    ]


    result = (
        normalize_and_validate_payments(
            payments
        )
    )


    assert len(result) == 1


    assert (
        result[0]["payment_id"]
        == "pay_FINAL001"
    )