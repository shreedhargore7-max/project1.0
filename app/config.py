import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# HELPERS
# ============================================================

def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def require_env(name: str) -> str:
    value = get_env(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is missing."
        )

    return value


# ============================================================
# AI CONFIGURATION
# ============================================================

GEMINI_API_KEY = get_env("GEMINI_API_KEY")

HF_TOKEN = get_env("HF_TOKEN")


# ============================================================
# RAZORPAY CONFIGURATION
# ============================================================

RAZORPAY_KEY_ID = get_env("RAZORPAY_KEY_ID")

RAZORPAY_KEY_SECRET = get_env("RAZORPAY_KEY_SECRET")


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_ENV = get_env(
    "APP_ENV",
    "development"
)

LOG_LEVEL = get_env(
    "LOG_LEVEL",
    "INFO"
)


# ============================================================
# VALIDATION
# ============================================================

def validate_configuration(
    require_gemini: bool = False,
    require_razorpay: bool = False,
):
    missing = []

    if require_gemini and not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")

    if require_razorpay:
        if not RAZORPAY_KEY_ID:
            missing.append("RAZORPAY_KEY_ID")

        if not RAZORPAY_KEY_SECRET:
            missing.append("RAZORPAY_KEY_SECRET")

    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
        )

    return True


# ============================================================
# SAFE CONFIGURATION SUMMARY
# ============================================================

def configuration_status():

    return {
        "environment": APP_ENV,
        "log_level": LOG_LEVEL,
        "gemini_configured": bool(GEMINI_API_KEY),
        "huggingface_configured": bool(HF_TOKEN),
        "razorpay_configured": bool(
            RAZORPAY_KEY_ID
            and RAZORPAY_KEY_SECRET
        ),
    }


__all__ = [
    "PROJECT_ROOT",
    "GEMINI_API_KEY",
    "HF_TOKEN",
    "RAZORPAY_KEY_ID",
    "RAZORPAY_KEY_SECRET",
    "APP_ENV",
    "LOG_LEVEL",
    "get_env",
    "require_env",
    "validate_configuration",
    "configuration_status",
]