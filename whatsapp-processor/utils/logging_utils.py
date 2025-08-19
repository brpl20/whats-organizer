"""
Logging utility functions
"""
import logging
import sys
from typing import Optional

def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Create logger
    logger = logging.getLogger('whatsapp-processor')
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = 'whatsapp-processor') -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)