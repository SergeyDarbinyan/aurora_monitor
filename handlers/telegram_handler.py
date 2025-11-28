import json
import logging
import requests
from typing import List, Dict, Any
from handlers.base_handler import BaseHandler
from enums import TelegramEnum


class TelegramHandler(BaseHandler):
    """Handles Telegram messaging operations."""

    def __init__(self):
        super().__init__()
        self.bot_token = TelegramEnum.BOT_TOKEN.value
        self.chat_id = TelegramEnum.CHAT_ID.value
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_messages(self, messages_list: List[Dict[str, Any]]) -> None:
        """Send multiple messages to Telegram with inline keyboards."""
        url = f"{self.base_url}/sendMessage"

        for message_info in messages_list:
            thread_id = message_info["thread_id"]
            alert_id = message_info["alert_id"]

            inline_keyboard = [
                [
                    {
                        "text": "Escalate",
                        "callback_data": f"escalate:{thread_id}:{alert_id}"
                    },
                    {
                        "text": "Dismiss",
                        "callback_data": f"dismiss:{thread_id}:{alert_id}"
                    }
                ]
            ]

            payload = {
                "chat_id": self.chat_id,
                "text": message_info["message"],
                "parse_mode": "HTML",
                "reply_markup": json.dumps({
                    "inline_keyboard": inline_keyboard
                })
            }

            try:
                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    self.logger.info("Message sent to Telegram!")
                else:
                    self.logger.error("Failed to send message: %s", response.status_code)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error sending Telegram message: {e}")

    def send_error_message(self, message: str) -> None:
        """Send error message to Telegram."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                self.logger.info("Error message sent to Telegram!")
            else:
                self.logger.error("Failed to send error message: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending Telegram error message: {e}")

    def get_updates(self) -> List[Dict[str, Any]]:
        """Get updates from Telegram."""
        url = f"{self.base_url}/getUpdates"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('result', [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting updates: {e}")
            return []

    def edit_message(self, message_id: int, text: str, remove_buttons: bool = True) -> bool:
        """Edit an existing message."""
        url = f"{self.base_url}/editMessageText"

        inline_keyboard = [] if remove_buttons else None
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }

        if inline_keyboard is not None:
            payload["reply_markup"] = json.dumps({"inline_keyboard": inline_keyboard})

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                self.logger.info(f"Message {message_id} edited successfully")
                return True
            else:
                self.logger.error(f"Failed to edit message. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error editing message: {e}")
            return False

    def handle(self, action: str, *args, **kwargs) -> Any:
        """Handle different Telegram operations."""
        if action == "send_messages":
            return self.send_messages(*args, **kwargs)
        elif action == "send_error":
            return self.send_error_message(*args, **kwargs)
        elif action == "get_updates":
            return self.get_updates(*args, **kwargs)
        elif action == "edit_message":
            return self.edit_message(*args, **kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")