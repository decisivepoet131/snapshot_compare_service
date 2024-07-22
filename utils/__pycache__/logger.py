import logging
import os
import time
from datetime import datetime, timezone
import json

# Create the /logs/ directory if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(script_dir, "../logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Read logging level from environment variable, default to DEBUG if not set
log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()

# Map log level string to logging level
level_map = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

# Set up the logger
logger = logging.getLogger('snapshot_compare_service')
logger.setLevel(level_map.get(log_level, logging.DEBUG))  # Default to DEBUG if the level is not recognized
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create console handler and set level to the configured log level
ch = logging.StreamHandler()
ch.setLevel(level_map.get(log_level, logging.DEBUG))
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create file handler and set level to the configured log level
log_file = os.path.join(logs_dir, f'snapshot_compare_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.log')
fh = logging.FileHandler(log_file)
fh.setLevel(level_map.get(log_level, logging.DEBUG))
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_entry_exit(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting: {func.__name__}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}")
            raise e
    return wrapper

def log_response(response, status_code):
    logger.info(f"HTTP Response Code: {status_code}")
    response.status_code = status_code
    return response

def save_result_and_log(result, request_path):
    # Create the /results/ directory if it doesn't exist
    results_dir = os.path.join(script_dir, "../results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Determine the filename based on the request path
    timestamp = int(time.time())
    if request_path.endswith('item-attributes'):
        filename = f"item-attributes-compare-{timestamp}.json"
    else:
        filename = f"item-price-compare-{timestamp}.json"
    filepath = os.path.join(results_dir, filename)

    # Save the result to a file
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=4)

    logger.debug(f"Comparison result saved to {filepath}")

    return filepath

def log_service_start_stop(message):
    # Always log service start and stop messages at INFO level
    service_logger = logging.getLogger('service_logger')
    service_logger.setLevel(logging.INFO)
    service_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ensure it doesn't duplicate handlers
    if not service_logger.hasHandlers():
        # Create console handler and set level to info
        service_ch = logging.StreamHandler()
        service_ch.setLevel(logging.INFO)
        service_ch.setFormatter(service_formatter)
        service_logger.addHandler(service_ch)
    
        # Create file handler and set level to info
        service_fh = logging.FileHandler(log_file)
        service_fh.setLevel(logging.INFO)
        service_fh.setFormatter(service_formatter)
        service_logger.addHandler(service_fh)

    service_logger.info(message)