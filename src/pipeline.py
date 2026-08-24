import time
import logging
from src.db.snowflake_connector import get_snowflake_connection
from src.utils import parse_records
from src.config import Config

logger = logging.getLogger(__name__)

def run_data_pipeline():
    logger.info("Starting pipeline run...")
    conn = None
    last_exception = None

    for attempt in range(Config.MAX_RETRIES):
        try:
            conn = get_snowflake_connection()
            logger.info(f"Snowflake connection established on attempt {attempt + 1}.")
            break
        except Exception as e:
            last_exception = e
            if attempt < Config.MAX_RETRIES - 1:
                wait_seconds = 2 ** attempt
                logger.warning(
                    f"Connection attempt {attempt + 1} of {Config.MAX_RETRIES} failed: {e}. "
                    f"Retrying in {wait_seconds}s..."
                )
                time.sleep(wait_seconds)
            else:
                logger.error(
                    f"All {Config.MAX_RETRIES} connection attempts failed. Last error: {e}"
                )

    if conn is None:
        raise last_exception

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_events LIMIT 100")
        records = cursor.fetchall()
        parsed = parse_records(records)
        logger.info(f"Processed {len(parsed)} records successfully.")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise e
    finally:
        conn.close()
