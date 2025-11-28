import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.logging_config import LoggingConfig
from core.alert_monitor import AlertMonitor


def main():
    """Main function to run the alert monitor."""
    # Setup logging
    logging_config = LoggingConfig()
    logging_config.setup_logging()

    # Create and run the alert monitor
    monitor = AlertMonitor()
    monitor.run()


if __name__ == "__main__":
    main()