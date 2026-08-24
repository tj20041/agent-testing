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

    # Read network_timeout and login_timeout from environment variables with safe defaults.
    # DEFAULT_TIMEOUT (30s) is used as the fallback; override via SNOWFLAKE_NETWORK_TIMEOUT
    # and SNOWFLAKE_LOGIN_TIMEOUT env vars per environment (CI, staging, production).
    network_timeout = int(os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", str(DEFAULT_TIMEOUT)))
    login_timeout = int(os.getenv("SNOWFLAKE_LOGIN_TIMEOUT", str(DEFAULT_TIMEOUT)))

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        network_timeout=network_timeout,
        login_timeout=login_timeout
    )
    return conn
