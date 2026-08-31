import time
import logging
from snowflake.connector.errors import OperationalError
from src.db.snowflake_connector import get_snowflake_connection
from src.config import Config
from src.utils import parse_records

logger = logging.getLogger(__name__)

def run_data_pipeline():
    logger.info("Starting pipeline run...")

    conn = None
    last_exception = None

    for attempt in range(1, Config.MAX_RETRIES + 1):
        try:
            logger.info(f"Snowflake connection attempt {attempt} of {Config.MAX_RETRIES}...")
            conn = get_snowflake_connection()
            break  # Connection succeeded; exit the retry loop
        except OperationalError as e:
            last_exception = e
            logger.warning(
                f"Snowflake connection attempt {attempt} of {Config.MAX_RETRIES} failed: {e}"
            )
            if attempt == Config.MAX_RETRIES:
                logger.error(
                    f"All {Config.MAX_RETRIES} Snowflake connection attempts exhausted. "
                    f"Final error: {e}"
                )
                raise
            backoff_seconds = 2 ** attempt
            logger.info(f"Retrying in {backoff_seconds} seconds (exponential backoff)...")
            time.sleep(backoff_seconds)

    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM raw_events LIMIT 100")
            records = cursor.fetchall()
        finally:
            cursor.close()

        parsed = parse_records(records)
        logger.info(f"Processed {len(parsed)} records successfully.")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            logger.info("Snowflake connection closed.")
