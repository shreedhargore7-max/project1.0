import logging
import traceback


logger = logging.getLogger("intelligent_agent")


# ============================================================
# SAFE ERROR MESSAGE
# ============================================================

def safe_error_message(
    error: Exception,
    default_message: str = "Something went wrong."
) -> str:

    if error is None:
        return default_message

    message = str(error).strip()

    if not message:
        return default_message

    # Never expose common secret values directly
    sensitive_words = [
        "api_key",
        "api-key",
        "secret",
        "password",
        "token",
        "authorization",
    ]

    lowered = message.lower()

    if any(
        word in lowered
        for word in sensitive_words
    ):
        return default_message

    return message


# ============================================================
# LOG EXCEPTION
# ============================================================

def log_exception(
    error: Exception,
    context: str = ""
):

    try:

        logger.error(
            "[ERROR] context=%s error=%s",
            context,
            safe_error_message(error),
        )

        logger.debug(
            "[TRACEBACK]\n%s",
            traceback.format_exc(),
        )

    except Exception:
        # Logging must never crash the application.
        pass


# ============================================================
# SAFE EXECUTION
# ============================================================

def safe_execute(
    function,
    *args,
    default=None,
    context="",
    **kwargs,
):

    try:

        return function(
            *args,
            **kwargs,
        )

    except Exception as error:

        log_exception(
            error,
            context=context,
        )

        return default


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "safe_error_message",
    "log_exception",
    "safe_execute",
]