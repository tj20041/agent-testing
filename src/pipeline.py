import time
import logging

import snowflake.connector.errors

from src.db.snowflake_connector import get_snowflake_connection
from src.utils import parse_records
from src.config import Config

logger = logging.getLogger(__name__)


def run_data_pipeline():
    """
    Execute the main data pipeline:
      1. Connect to Snowflake (with retry + exponential backoff).
      2. Query raw_events.
      3. Parse and log the returned records.

    Retries up to Config.MAX_RETRIES times on transient
    snowflake.connector.errors.OperationalError (e.g. network timeouts).
    Non-connection errors (e.g. SQL errors) are raised immediately without
    consuming the retry budget.

    Connection and cursor teardown is guaranteed via try/finally so that
    Snowflake connections are never leaked, even when all retries are
    exhausted.
    """
    logger.info("Starting pipeline run...")

    last_error = None

    for attempt in range(1, Config.MAX_RETRIES + 1):
        conn = None
        cursor = None
        try:
            logger.info(
                "Attempting Snowflake connection (attempt %d / %d)...",
                attempt,
                Config.MAX_RETRIES,
            )
            conn = get_snowflake_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_events LIMIT 100")
            records = cursor.fetchall()
            parsed = parse_records(records)
            logger.info("Processed %d records successfully.", len(parsed))
            # Success — exit the retry loop.
            return parsed

        except snowflake.connector.errors.OperationalError as e:
            last_error = e
            logger.warning(
                "Transient Snowflake OperationalError on attempt %d / %d: %s",
                attempt,
                Config.MAX_RETRIES,
                e,
            )
            if attempt < Config.MAX_RETRIES:
                backoff_seconds = 2 ** (attempt - 1)  # 1 s, 2 s, 4 s, …
                logger.info(
                    "Retrying in %d second(s)...", backoff_seconds
                )
                time.sleep(backoff_seconds)
            # Non-OperationalError exceptions (e.g. SQL / programming errors)
            # propagate immediately without retrying.

        finally:
            # Guarantee cursor and connection are always released.
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    logger.debug("Failed to close Snowflake cursor.", exc_info=True)
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    logger.debug("Failed to close Snowflake connection.", exc_info=True)

    # All retry attempts exhausted.
    logger.error(
        "Pipeline execution failed after %d attempt(s): %s",
        Config.MAX_RETRIES,
        last_error,
    )
    raise last_error
