DEFAULT_TIMEOUT = 30
BATCH_SIZE = 1000
MAX_WORKERS = 4

# Snowflake-specific connection timeout (seconds).
# Used as the network_timeout argument in snowflake.connector.connect().
# Can be overridden at runtime via the SNOWFLAKE_NETWORK_TIMEOUT environment variable.
SNOWFLAKE_CONNECT_TIMEOUT = 30
