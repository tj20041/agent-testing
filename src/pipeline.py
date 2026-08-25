import time
import logging

import snowflake.connector.errors

from src.db.snowflake_connector import get_snowflake_connection
from src.config import Config
from src.utils import parse_records

logger = logging.getLogger(__name__)


def run_data_pipeline():
    logger.info("Starting pipeline run...")

    conn = _get_connection_with_retry()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_events LIMIT 100")
        records = cursor.fetchall()
        parsed = parse_records(records)
        logger.info("Processed %d records successfully.", len(parsed))
    except snowflake.connector.errors.DatabaseError as e:
        # Non-retryable Snowflake error (e.g. bad SQL, permission denied).
        logger.error("Snowflake database error during pipeline execution: %s", e)
        raise
    except Exception as e:
        # Catch-all for unexpected errors that are not Snowflake-specific.
        logger.error("Unexpected error during pipeline execution: %s", e)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _get_connection_with_retry():
    """Attempt to obtain a Snowflake connection with exponential-backoff retries.

    Uses Config.MAX_RETRIES (default 3, overridable via MAX_RETRIES env var).
    Only snowflake.connector.errors.OperationalError (transient connectivity
    failures such as error 250001) triggers a retry.  Non-transient errors
    (e.g. authentication failures surfaced as DatabaseError) are re-raised
    immediately without consuming retry attempts.

    Raises:
        snowflake.connector.errors.OperationalError: if all retry attempts are
            exhausted without a successful connection.
    """
    last_exc = None
    for attempt in range(Config.MAX_RETRIES):
        try:
            conn = get_snowflake_connection()
            if attempt > 0:
                logger.info(
                    "Snowflake connection established on attempt %d/%d.",
                    attempt + 1,
                    Config.MAX_RETRIES,
                )
            return conn
        except snowflake.connector.errors.OperationalError as e:
            last_exc = e
            if attempt < Config.MAX_RETRIES - 1:
                sleep_seconds = 2 ** attempt
                logger.warning(
                    "Snowflake connection attempt %d/%d failed (OperationalError: %s). "
                    "Retrying in %d second(s)...",
                    attempt + 1,
                    Config.MAX_RETRIES,
                    e,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
            else:
                logger.error(
                    "Snowflake connection failed after %d attempt(s). "
                    "Giving up. Last error: %s",
                    Config.MAX_RETRIES,
                    e,
                )
    raise last_exc
