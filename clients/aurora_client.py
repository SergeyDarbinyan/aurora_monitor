import logging
import requests
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from enums import AuroraEnum


class AuroraClient:
    """Handles communication with Aurora alert system."""

    def __init__(self, base_url: str = 'https://aurora.onetick.com'):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sessionid = ''
        self.csrftoken = ''
        self.headers = {}

    def login(self) -> bool:
        """Login to Aurora system and establish session."""
        login_url = f"{self.base_url}/alerts/login/"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": login_url,
            "User-Agent": "Mozilla/5.0"
        }

        try:
            # Get login page to retrieve CSRF token
            resp = self.session.get(login_url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})

            if not csrf_input:
                self.logger.error("No CSRF token found on login page.")
                return False

            csrf_token = csrf_input["value"]

            # Prepare login payload
            data = {
                "csrfmiddlewaretoken": csrf_token,
                "username": AuroraEnum.AURORA_USERNAME.value,
                "password": AuroraEnum.AURORA_PASSWORD.value
            }

            self.session.headers.update(headers)
            self.session.cookies.set("csrftoken", csrf_token)

            # Post login data
            response = self.session.post(login_url, data=data)

            # Retrieve cookies
            cookies = self.session.cookies.get_dict()
            self.sessionid = cookies.get("sessionid", "")
            self.csrftoken = cookies.get("csrftoken", "")

            if self.sessionid and self.csrftoken:
                self.headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": f"{self.base_url}/alerts/login/",
                    "Cookie": f"csrftoken={self.csrftoken}; sessionid={self.sessionid}"
                }
                self.logger.info("Successfully logged in to Aurora")
                return True
            else:
                self.logger.error("Failed to obtain session credentials")
                return False

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False

    def get_alerts(self) -> Optional[List[Dict]]:
        """Fetch alerts from Aurora system."""
        if not self.headers:
            self.logger.error("Not logged in. Please login first.")
            return None

        url = f"{self.base_url}/alerts/get_alerts/alerts"

        try:
            self.logger.info("Checking for new alerts...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching alerts: {e}")
            return None
        except ValueError:
            self.logger.error("Response is not in valid JSON format. Check Cookie...")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching alerts: {e}")
            return None

    def get_alert_description(self, alert_thread_id: str) -> Optional[str]:
        """Get detailed description for a specific alert."""
        if not self.headers:
            self.logger.error("Not logged in. Please login first.")
            return None

        url = f'{self.base_url}/alerts/get_thread_main_alert/{alert_thread_id}'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data[0]['body'] if data else ""

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching alert description: {e}")
            return None
        except (ValueError, IndexError, KeyError) as e:
            self.logger.error(f"Error parsing alert description: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching alert description: {e}")
            return None

    def dismiss_alert(self, thread_id: str) -> bool:
        """Dismiss an alert in the system."""
        if not self.headers:
            self.logger.error("Not logged in. Please login first.")
            return False

        url = f"{self.base_url}/alerts/dismiss_thread/{thread_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                self.logger.info(f"Alert {thread_id} dismissed successfully.")
                return True
            else:
                self.logger.error(f"Failed to dismiss alert {thread_id}. Status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error dismissing alert {thread_id}: {e}")
            return False

    def escalate_alert(self, alert_id: str) -> bool:
        """Escalate an alert in the system."""
        if not self.headers:
            self.logger.error("Not logged in. Please login first.")
            return False

        url = f"{self.base_url}/alerts/escalate_alert/{alert_id}/fyi/"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                self.logger.info(f"Alert {alert_id} escalated successfully.")
                return True
            else:
                self.logger.error(f"Failed to escalate alert {alert_id}. Status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error escalating alert {alert_id}: {e}")
            return False