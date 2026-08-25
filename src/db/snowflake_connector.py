import os
import time
import logging
import snowflake.connector
from snowflake.connector.errors import OperationalError

from src.config import Config
from src.constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)

# Network timeout for Snowflake TCP/TLS connection phase (seconds).
# Driven by SNOWFLAKE_NETWORK_TIMEOUT env var; falls back to DEFAULT_TIMEOUT (30 s).
SNOWFLAKE_NETWORK_TIMEOUT = int(os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", str(DEFAULT_TIMEOUT)))

# Login/auth timeout for the Snowflake authentication phase (seconds).
# Kept separate so a slow auth response does not cause an indefinite hang.
SNOWFLAKE_LOGIN_TIMEOUT = int(os.getenv("SNOWFLAKE_LOGIN_TIMEOUT", "60"))


def get_snowflake_connection():
    """Establish and return a Snowflake connection.

    Retries up to Config.MAX_RETRIES times (default 3) with exponential
    back-off on OperationalError 250001 (connection timeout / network blip)
    before raising the exception to the caller.

    Raises:
        snowflake.connector.errors.OperationalError: after all retries are
            exhausted and a connection could not be established.
    """
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

    last_exc = None
    for attempt in range(Config.MAX_RETRIES):
        try:
            logger.info(
                "Attempting Snowflake connection (attempt %d/%d) "
                "[account=%s, network_timeout=%ds, login_timeout=%ds]",
                attempt + 1,
                Config.MAX_RETRIES,
                account,
                SNOWFLAKE_NETWORK_TIMEOUT,
                SNOWFLAKE_LOGIN_TIMEOUT,
            )
            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account,
                warehouse=warehouse,
                # FIX: was hardcoded to 1 second — now uses DEFAULT_TIMEOUT (30 s)
                # or the SNOWFLAKE_NETWORK_TIMEOUT environment variable.
                network_timeout=SNOWFLAKE_NETWORK_TIMEOUT,
                # FIX: added login_timeout to cap the Snowflake auth phase
                # separately from the TCP connection phase.
                login_timeout=SNOWFLAKE_LOGIN_TIMEOUT,
            )
            logger.info("Snowflake connection established successfully.")
            return conn
        except OperationalError as exc:
            last_exc = exc
            backoff = 2 ** attempt
            logger.warning(
                "Snowflake connection attempt %d/%d failed: %s. "
                "Retrying in %d second(s)...",
                attempt + 1,
                Config.MAX_RETRIES,
                exc,
                backoff,
            )
            if attempt < Config.MAX_RETRIES - 1:
                time.sleep(backoff)

    logger.error(
        "Snowflake connection failed after %d attempt(s). Last error: %s",
        Config.MAX_RETRIES,
        last_exc,
    )
    raise last_exc
