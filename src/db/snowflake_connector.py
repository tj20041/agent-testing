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

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        network_timeout=DEFAULT_TIMEOUT
    )

    # Connection health-check: verify the connection is live immediately after establishing it
    probe_cursor = conn.cursor()
    try:
        probe_cursor.execute("SELECT 1")
    finally:
        probe_cursor.close()

    return conn
