import logging
import os
from datetime import datetime


class LoggingConfig:
    """Handles logging configuration for the alert monitor."""

    def __init__(self, logs_directory: str = 'logs'):
        self.logs_directory = logs_directory

    def setup_logging(self) -> None:
        """Set up logging configuration with file and console handlers."""
        # Clear any existing handlers to avoid duplicates
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create logs directory if it doesn't exist
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

        today_date = datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join(self.logs_directory, f"log_file_{today_date}.log")

        # Create formatter
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_formatter)

        # Configure root logger
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Prevent duplicate logs
        root_logger.propagate = False