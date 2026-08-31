import os
import logging
import snowflake.connector

from src.constants import DEFAULT_TIMEOUT, SNOWFLAKE_CONNECT_TIMEOUT

logger = logging.getLogger(__name__)

def get_snowflake_connection():
    """
    Establish and return a Snowflake connection using credentials sourced
    exclusively from environment variables.  No credentials are hard-coded.

    The network_timeout value is resolved in priority order:
      1. SNOWFLAKE_NETWORK_TIMEOUT environment variable (ops-tunable at runtime)
      2. SNOWFLAKE_CONNECT_TIMEOUT constant (30 s) defined in src/constants.py
      3. Fallback to DEFAULT_TIMEOUT (30 s) if the constant is unavailable

    Raises:
        EnvironmentError: if any required Snowflake environment variable is missing.
    """
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

    # Validate that all required environment variables are present before
    # attempting a connection, so failures are diagnosed clearly.
    missing = [
        name
        for name, value in (
            ("SNOWFLAKE_ACCOUNT", account),
            ("SNOWFLAKE_USER", user),
            ("SNOWFLAKE_PASSWORD", password),
            ("SNOWFLAKE_WAREHOUSE", warehouse),
        )
        if value is None
    ]
    if missing:
        raise EnvironmentError(
            f"Missing required Snowflake environment variable(s): {', '.join(missing)}"
        )

    # Allow ops teams to tune the timeout without a code change.
    network_timeout_val = int(
        os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", str(SNOWFLAKE_CONNECT_TIMEOUT))
    )

    logger.debug(
        "Connecting to Snowflake account=%s warehouse=%s network_timeout=%ds",
        account,
        warehouse,
        network_timeout_val,
    )

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        network_timeout=network_timeout_val,
    )
    return conn
