import time
import logging

import snowflake.connector
from snowflake.connector.errors import OperationalError

from src.config import Config
from src.db.snowflake_connector import get_snowflake_connection
from src.utils import parse_records

logger = logging.getLogger(__name__)


def run_data_pipeline():
    """Run the end-to-end data pipeline.

    Attempts to acquire a Snowflake connection and process records.
    Retries the full pipeline execution up to Config.MAX_RETRIES times
    on OperationalError before aborting.  Connection and cursor resources
    are always released via a finally block to prevent connection leaks.
    """
    logger.info("Starting pipeline run...")

    last_exc = None
    for attempt in range(Config.MAX_RETRIES):
        conn = None
        cursor = None
        try:
            conn = get_snowflake_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_events LIMIT 100")
            records = cursor.fetchall()
            parsed = parse_records(records)
            logger.info("Processed %d records successfully.", len(parsed))
            # Successful run — exit the retry loop.
            return
        except OperationalError as exc:
            # FIX: catch OperationalError specifically rather than broad Exception
            # so unrelated errors are not swallowed silently.
            last_exc = exc
            backoff = 2 ** attempt
            logger.warning(
                "Pipeline attempt %d/%d failed with OperationalError: %s. "
                "Retrying in %d second(s)...",
                attempt + 1,
                Config.MAX_RETRIES,
                exc,
                backoff,
            )
            if attempt < Config.MAX_RETRIES - 1:
                time.sleep(backoff)
        except Exception as exc:
            # Non-retriable error — log and re-raise immediately.
            logger.error("Pipeline execution failed with unexpected error: %s", exc)
            raise
        finally:
            # FIX: always close cursor and connection to prevent resource leaks
            # on both successful runs and partial failures.
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

    logger.error(
        "Pipeline aborted after %d attempt(s). Last error: %s",
        Config.MAX_RETRIES,
        last_exc,
    )
    raise last_exc
