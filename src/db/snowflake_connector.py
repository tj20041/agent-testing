import os
import logging
import snowflake.connector

logger = logging.getLogger(__name__)

def get_snowflake_connection():
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    
    # BUG: network_timeout is set to only 1 second, causing network failures under latency
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        network_timeout=1
    )
    return conn
