import time
import random
import logging
from typing import Optional
from clients.aurora_client import AuroraClient
from handlers.telegram_handler import TelegramHandler
from handlers.twilio_handler import TwilioHandler
from processors.alert_processor import AlertProcessor


class AlertMonitor:
    """Main alert monitoring class that coordinates all components."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.aurora_client = AuroraClient()
        self.telegram_handler = TelegramHandler()
        self.twilio_handler = TwilioHandler()
        self.alert_processor = AlertProcessor(self.aurora_client, self.telegram_handler)

        self.last_update_time = time.time()
        self.last_alert_time = time.time()
        self.alert_interval = 1  # Initial delay
        self.is_running = False

    def initialize(self) -> bool:
        """Initialize the monitor by logging into Aurora."""
        if not self.aurora_client.login():
            self.logger.error("Failed to login to Aurora. Cannot proceed.")
            return False

        self.logger.info("Alert monitor initialized successfully")
        return True

    def trigger_telegram_alert(self) -> None:
        """Check for new alerts and send notifications."""
        new_alerts = self.alert_processor.check_new_alerts()

        if new_alerts:
            self.logger.info(f"Found {len(new_alerts)} new alerts")
            alerts_messages = self.alert_processor.format_alert_messages(new_alerts)
            self.telegram_handler.send_messages(alerts_messages)
            self.twilio_handler.make_call()
        else:
            self.logger.info("No new alerts found")

    def process_telegram_updates(self) -> None:
        """Process incoming Telegram updates."""
        updates = self.telegram_handler.get_updates()

        for update in updates:
            if 'callback_query' in update:
                self.alert_processor.handle_callback_query(update)

    def run(self) -> None:
        """Run the main monitoring loop."""
        if not self.initialize():
            return

        self.is_running = True
        self.logger.info("Starting alert monitor...")

        try:
            while self.is_running:
                current_time = time.time()

                # Process Telegram updates every 3 seconds
                if current_time - self.last_update_time >= 3:
                    self.process_telegram_updates()
                    self.last_update_time = current_time

                # Check for alerts at random intervals
                if current_time - self.last_alert_time >= self.alert_interval:
                    self.trigger_telegram_alert()
                    self.last_alert_time = current_time
                    self.alert_interval = random.randint(45, 75)

                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Alert monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in monitor: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self.is_running = False
        self.logger.info("Alert monitor stopped")