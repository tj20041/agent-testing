import time
import logging

import snowflake.connector.errors

from src.config import Config
from src.db.snowflake_connector import get_snowflake_connection
from src.utils import parse_records

logger = logging.getLogger(__name__)

def run_data_pipeline():
    logger.info("Starting pipeline run...")

    conn = None
    cursor = None
    last_exception = None

    for attempt in range(Config.MAX_RETRIES):
        try:
            conn = get_snowflake_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_events LIMIT 100")
            records = cursor.fetchall()
            parsed = parse_records(records)
            logger.info(f"Processed {len(parsed)} records successfully.")
            # Pipeline succeeded — exit the retry loop.
            return parsed
        except snowflake.connector.errors.OperationalError as e:
            last_exception = e
            wait_seconds = 2 ** attempt
            logger.warning(
                f"Snowflake connection attempt {attempt + 1}/{Config.MAX_RETRIES} failed: {e}. "
                f"Retrying in {wait_seconds}s..."
            )
            time.sleep(wait_seconds)
        except Exception as e:
            # Non-transient errors are not retried.
            logger.error(f"Pipeline execution failed with non-retryable error: {e}")
            raise
        finally:
            # Always clean up cursor and connection handles to prevent leaks.
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
                cursor = None
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
                conn = None

    # All retry attempts exhausted.
    logger.error(
        f"Pipeline execution failed after {Config.MAX_RETRIES} attempt(s). "
        f"Last error: {last_exception}"
    )
    raise last_exception
