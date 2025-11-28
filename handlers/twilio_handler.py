import logging
from twilio.rest import Client
from handlers.base_handler import BaseHandler
from enums import TwilioEnum


class TwilioHandler(BaseHandler):
    """Handles Twilio phone call operations."""

    def __init__(self):
        super().__init__()
        self.account_sid = TwilioEnum.ACCOUNT_SID.value
        self.auth_token = TwilioEnum.AUTH_TOKEN.value
        self.phone_to = TwilioEnum.PHONE_TO.value
        self.phone_from = TwilioEnum.PHONE_FROM.value
        self.client = Client(self.account_sid, self.auth_token)

    def make_call(self, message: str = "Alert! Something is wrong on the server!") -> str:
        """Make a phone call with the specified message."""
        try:
            call_result = self.client.calls.create(
                twiml=f'<Response><Say>{message}</Say></Response>',
                to=self.phone_to,
                from_=self.phone_from
            )
            self.logger.warning(f"Call initiated: {call_result.sid}")
            return call_result.sid
        except Exception as e:
            self.logger.error(f"Error making call: {e}")
            return ""

    def handle(self, message: str = None) -> str:
        """Handle phone call operation."""
        return self.make_call(message)