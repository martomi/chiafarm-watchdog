# std
import http.client
import logging
import json
from typing import List

# project
from . import Notifier, Event, EventType


class TelegramNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Telegram notifier.")
        super().__init__(title_prefix, config)
        try:
            self.bot_token = config["bot_token"]
            self.chat_id = config["chat_id"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type == EventType.USER:
                request_body = json.dumps(
                    {
                        "chat_id": self.chat_id,
                        "text": f"*{self.get_title_for_event(event)}*\n{event.message}",
                        "parse_mode": "Markdown",
                        "disable_notification": event.priority == event.priority.LOW,
                    }
                )
                conn = http.client.HTTPSConnection("api.telegram.org")
                conn.request(
                    "POST",
                    f"/bot{self.bot_token}/sendMessage",
                    request_body,
                    {"Content-type": "application/json"},
                )
                response = conn.getresponse()
                if response.getcode() != 200:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return errors
