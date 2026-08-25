# ============================================================
# AGENT OBSERVABILITY / LOGGER
# ============================================================

import logging
import os
import time
import uuid
from datetime import datetime


# ============================================================
# LOG DIRECTORY
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


LOG_FILE = os.path.join(
    LOG_DIR,
    "agent.log"
)


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(
    "intelligent_agent"
)

logger.setLevel(
    logging.INFO
)


if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )


# ============================================================
# REQUEST ID
# ============================================================

def create_request_id():

    return (
        "req_"
        + uuid.uuid4().hex[:12]
    )


# ============================================================
# REQUEST START
# ============================================================

def log_request(
    request_id,
    question
):

    logger.info(
        "[REQUEST] id=%s question=%s",
        request_id,
        question
    )


# ============================================================
# ROUTER
# ============================================================

def log_route(
    request_id,
    route
):

    logger.info(
        "[ROUTER] id=%s route=%s",
        request_id,
        route
    )


# ============================================================
# TOOL START
# ============================================================

def log_tool_start(
    request_id,
    tool
):

    logger.info(
        "[TOOL START] id=%s tool=%s",
        request_id,
        tool
    )


# ============================================================
# TOOL SUCCESS
# ============================================================

def log_tool_success(
    request_id,
    tool,
    duration
):

    logger.info(
        "[TOOL SUCCESS] id=%s tool=%s duration=%.3fs",
        request_id,
        tool,
        duration
    )


# ============================================================
# TOOL ERROR
# ============================================================

def log_tool_error(
    request_id,
    tool,
    error,
    duration=None
):

    if duration is None:

        logger.error(
            "[TOOL ERROR] id=%s tool=%s error=%s",
            request_id,
            tool,
            error
        )

    else:

        logger.error(
            "[TOOL ERROR] id=%s tool=%s duration=%.3fs error=%s",
            request_id,
            tool,
            duration,
            error
        )


# ============================================================
# AGENT ERROR
# ============================================================

def log_agent_error(
    request_id,
    error
):

    logger.error(
        "[AGENT ERROR] id=%s error=%s",
        request_id,
        error
    )


# ============================================================
# RESPONSE
# ============================================================

def log_response(
    request_id,
    duration
):

    logger.info(
        "[RESPONSE] id=%s duration=%.3fs",
        request_id,
        duration
    )


# ============================================================
# GENERIC EVENT
# ============================================================

def log_event(
    request_id,
    event,
    details=""
):

    logger.info(
        "[EVENT] id=%s event=%s details=%s",
        request_id,
        event,
        details
    )


# ============================================================
# TIMER
# ============================================================

class Timer:

    def __init__(self):

        self.start_time = time.perf_counter()

    def elapsed(self):

        return (
            time.perf_counter()
            - self.start_time
        )


# ============================================================
# OBSERVABILITY CONTEXT
# ============================================================

def create_observability_context(
    question
):

    request_id = create_request_id()

    timer = Timer()

    log_request(
        request_id,
        question
    )

    return {
        "request_id": request_id,
        "request_start_time": time.time(),
        "timer": timer,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "logger",
    "create_request_id",
    "log_request",
    "log_route",
    "log_tool_start",
    "log_tool_success",
    "log_tool_error",
    "log_agent_error",
    "log_response",
    "log_event",
    "Timer",
    "create_observability_context",
]