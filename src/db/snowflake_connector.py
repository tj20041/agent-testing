import os
import time
import logging
import snowflake.connector
from snowflake.connector import errors as snowflake_errors

from src.constants import DEFAULT_SNOWFLAKE_NETWORK_TIMEOUT
from src.config import Config

logger = logging.getLogger(__name__)


def get_snowflake_connection():
    """
    Establish and return a Snowflake connection using credentials and configuration
    sourced exclusively from environment variables.

    Network timeout is driven by the SNOWFLAKE_NETWORK_TIMEOUT environment variable,
    falling back to DEFAULT_SNOWFLAKE_NETWORK_TIMEOUT (30 s) if not set.

    Connection attempts are retried up to Config.MAX_RETRIES times with exponential
    backoff (2^attempt seconds: 1 s, 2 s, 4 s) before re-raising the final exception.

    Raises:
        snowflake.connector.errors.OperationalError: if all retry attempts are exhausted.
        snowflake.connector.errors.DatabaseError: if all retry attempts are exhausted.
        ValueError: if any required environment variable is missing.
    """
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

    # Validate required credentials before attempting a connection so that a
    # missing env-var produces a clear, actionable error rather than an opaque
    # connector failure with None passed as a parameter value.
    missing = [
        name
        for name, value in (
            ("SNOWFLAKE_ACCOUNT", account),
            ("SNOWFLAKE_USER", user),
            ("SNOWFLAKE_PASSWORD", password),
            ("SNOWFLAKE_WAREHOUSE", warehouse),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            f"Missing required Snowflake environment variable(s): {', '.join(missing)}"
        )

    # Allow ops to tune the timeout via environment variable without a code deploy,
    # consistent with the Snowflake Connectivity & Timeout Runbook guidance that all
    # Snowflake configuration must be driven by environment variables.
    network_timeout = int(
        os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", str(DEFAULT_SNOWFLAKE_NETWORK_TIMEOUT))
    )

    max_retries = Config.MAX_RETRIES
    last_exc = None

    for attempt in range(max_retries):
        try:
            logger.info(
                "Attempting Snowflake connection (attempt %d/%d) — account=%s, "
                "warehouse=%s, network_timeout=%ds",
                attempt + 1,
                max_retries,
                account,
                warehouse,
                network_timeout,
            )
            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account,
                warehouse=warehouse,
                network_timeout=network_timeout,
            )
            logger.info(
                "Snowflake connection established successfully on attempt %d/%d — "
                "account=%s",
                attempt + 1,
                max_retries,
                account,
            )
            return conn

        except (
            snowflake_errors.OperationalError,
            snowflake_errors.DatabaseError,
        ) as exc:
            last_exc = exc
            backoff_seconds = 2 ** attempt  # 1 s, 2 s, 4 s
            logger.warning(
                "Snowflake connection attempt %d/%d failed — account=%s, "
                "error=%s. Retrying in %ds.",
                attempt + 1,
                max_retries,
                account,
                exc,
                backoff_seconds,
            )
            if attempt < max_retries - 1:
                time.sleep(backoff_seconds)

    logger.error(
        "Snowflake connection failed after %d attempt(s) — account=%s. "
        "Raising final exception.",
        max_retries,
        account,
    )
    raise last_exc
