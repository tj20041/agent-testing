import os

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    SNOWFLAKE_NETWORK_TIMEOUT = int(os.getenv('SNOWFLAKE_NETWORK_TIMEOUT', '30'))
