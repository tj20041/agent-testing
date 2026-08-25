# DEFAULT_TIMEOUT is the canonical Snowflake network_timeout value (seconds).
# It is used by src/db/snowflake_connector.py as the fallback when the
# SNOWFLAKE_NETWORK_TIMEOUT environment variable is not set.  Do NOT override
# this with a hardcoded literal elsewhere — reference this constant instead.
DEFAULT_TIMEOUT = 30

BATCH_SIZE = 1000
MAX_WORKERS = 4
