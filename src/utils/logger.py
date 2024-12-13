import logging
from src.config.settings import LOG_LEVEL

def setup_logger(name):
    """
    Set up logger with consistent configuration
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    logger.setLevel(LOG_LEVEL)
    return logger