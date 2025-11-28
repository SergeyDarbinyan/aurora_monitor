import html
import time
import logging
from typing import List, Dict, Any, Set
from clients.aurora_client import AuroraClient
from handlers.telegram_handler import TelegramHandler


class AlertProcessor:
    """Processes alerts and manages alert state."""

    def __init__(self, aurora_client: AuroraClient, telegram_handler: TelegramHandler):
        self.aurora_client = aurora_client
        self.telegram_handler = telegram_handler
        self.alert_ids: Set[str] = set()
        self.handled_alerts: Dict[str, str] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_new_alerts(self) -> List[Dict[str, Any]]:
        """Check for new alerts and return only new ones."""
        alerts = self.aurora_client.get_alerts()

        if not alerts:
            self.alert_ids.clear()
            return []

        new_alerts = []
        if len(alerts) > 0:
            for item in alerts:
                if item['id'] not in self.alert_ids:
                    self.alert_ids.add(item['id'])
                    new_alerts.append(item)

            if new_alerts:
                return new_alerts.copy()
        else:
            self.alert_ids.clear()

        return []

    def format_alert_messages(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format alerts into Telegram messages."""
        messages = []

        for alert in alerts:
            alert_description = self.aurora_client.get_alert_description(alert["threadID"])
            if alert_description:
                alert_description = alert_description[:100]
            else:
                alert_description = "No description available"

            if alert.get('severity') == 'critical':
                message_text = (
                    f"<b>Critical</b> 🔴 {alert['customer']}:{alert['environment']} - "
                    f"{alert['subject']}\n{html.escape(alert_description)}\n"
                )
            else:
                message_text = (
                    f"<b>Trivial</b> 🟡 {alert['customer']} : {alert['environment']} \n"
                    f"{alert['subject']}\n{html.escape(alert_description)}\n"
                )

            messages.append({
                "message": message_text,
                "thread_id": alert["threadID"],
                "alert_id": alert["id"]
            })

        return messages

    def handle_callback_query(self, update: Dict[str, Any]) -> None:
        """Handle callback queries from Telegram."""
        callback_data = update.get('callback_query', {}).get('data', '')
        message_id = update.get('callback_query', {}).get('message', {}).get('message_id')
        user_id = update.get('callback_query', {}).get('from', {}).get('id')
        message_text = update.get('callback_query', {}).get('message', {}).get('text', '')

        try:
            action, thread_id, alert_id = callback_data.split(":")
        except ValueError:
            self.logger.error(f"Invalid callback data format: {callback_data}")
            return

        if alert_id in self.handled_alerts:
            self.logger.info(f"Alert {alert_id} has already been handled.")
            return

        if action == 'dismiss':
            self.logger.info(f"User {user_id} dismissed alert {alert_id}")
            if self.aurora_client.dismiss_alert(thread_id):
                self.handled_alerts[alert_id] = 'dismissed'
                response_text = "The alert has been dismissed."
                self._acknowledge_callback(message_id, response_text, message_text)
            else:
                self.logger.error(f"Failed to dismiss alert {alert_id} in system")

        elif action == 'escalate':
            self.logger.info(f"User {user_id} escalated alert {alert_id}")
            if self.aurora_client.escalate_alert(alert_id):
                self.handled_alerts[alert_id] = 'escalated'
                response_text = "The alert has been escalated."
                self._acknowledge_callback(message_id, response_text, message_text)
            else:
                self.logger.error(f"Failed to escalate alert {alert_id} in system")
        else:
            self.logger.warning(f"Unknown action: {action}")

    def _acknowledge_callback(self, message_id: int, response_text: str, alert_snippet: str) -> None:
        """Acknowledge callback by updating the message."""
        if message_id not in self.handled_alerts:
            current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            alert_snippet = alert_snippet[:100] + "..." if len(alert_snippet) > 100 else alert_snippet

            updated_text = f"{response_text} [Updated at {current_timestamp}] - Alert: {alert_snippet}"

            self.handled_alerts[message_id] = True
            self.telegram_handler.edit_message(message_id, updated_text, remove_buttons=True)
        else:
            self.logger.info(f"Alert for message_id {message_id} has already been dismissed")
