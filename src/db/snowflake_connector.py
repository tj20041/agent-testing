import os
import logging
import snowflake.connector

from src.constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


def get_snowflake_connection():
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

    # Source timeout values from environment variables with safe defaults.
    # DEFAULT_TIMEOUT (30s) is the authoritative fallback defined in src/constants.py.
    # network_timeout governs low-level TCP socket operations.
    # login_timeout governs the full authentication handshake.
    network_timeout = int(os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", str(DEFAULT_TIMEOUT)))
    login_timeout = int(os.getenv("SNOWFLAKE_LOGIN_TIMEOUT", "60"))

    logger.debug(
        "Connecting to Snowflake (account=%s, warehouse=%s, "
        "network_timeout=%ds, login_timeout=%ds)",
        account,
        warehouse,
        network_timeout,
        login_timeout,
    )

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        network_timeout=network_timeout,
        login_timeout=login_timeout,
    )
    return conn
