# ---------------------------------------------------------------------------
# General defaults
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT = 30
BATCH_SIZE = 1000
MAX_WORKERS = 4

# ---------------------------------------------------------------------------
# Snowflake-specific timeouts
# ---------------------------------------------------------------------------
# DEFAULT_SNOWFLAKE_NETWORK_TIMEOUT is the fallback value (in seconds) used by
# get_snowflake_connection() when the SNOWFLAKE_NETWORK_TIMEOUT environment
# variable is not set.  30 seconds provides sufficient headroom for DNS
# resolution, TCP handshake, and TLS negotiation under realistic network
# conditions, while still surfacing genuine connectivity failures in a
# reasonable time.  Override via the SNOWFLAKE_NETWORK_TIMEOUT env var in any
# deployment environment where a different value is required.
DEFAULT_SNOWFLAKE_NETWORK_TIMEOUT = 30
