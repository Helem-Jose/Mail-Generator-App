import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(level='INFO', log_file='app.log', max_bytes=10485760, backup_count=5):
    """
    Setup logging configuration
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Log file path
        max_bytes (int): Maximum size of log file before rotation
        backup_count (int): Number of backup log files to keep
    """
    # Convert string level to numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific levels for external libraries if needed
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)

# Logging levels available:
# DEBUG: Detailed information for debugging
# INFO: General information about program execution
# WARNING: Indicate a potential problem
# ERROR: A more serious problem
# CRITICAL: A critical problem that may prevent the program from running 