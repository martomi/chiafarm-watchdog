"""Notifier package responsible for user notification

"""

# std
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import datetime


class EventPriority(Enum):
    """Event priority dictates how urgently
    the user needs to be notified about it
    """

    LOW = -1
    NORMAL = 0
    HIGH = 1


class EventType(Enum):
    """Events can either be user events
    that are propagated directly to the
    user, or keep-alive events that are
    processed to ensure the system runs
    """

    KEEPALIVE = 0
    USER = 1
    DAILY_STATS = 2
    PLOTDECREASE = 3
    PLOTINCREASE = 4


class EventService(Enum):
    """Even service helps to distinguish
    between similar events for different services
    """

    HARVESTER = 0
    FARMER = 1
    FULL_NODE = 2
    DAILY = 3
    WALLET = 4


@dataclass
class Event:
    type: EventType
    priority: EventPriority
    service: EventService
    message: str
    iteration: int = 0


class Notifier(ABC):
    """This abstract class provides common interface for
    any notifier implementation. It should be easy to add
    extensions that integrate with variety of services such as
    Pushover, E-mail, Slack, WhatsApp, etc
    """

    def __init__(self, title_prefix: str, config: dict):
        self._title_prefix = title_prefix
        self._config = config
        self._conn_timeout_seconds = 10
        self._notification_types = [EventType.USER]
        self._notification_services = [EventService.HARVESTER, EventService.FARMER, EventService.FULL_NODE]

        daily_stats = config.get("daily_stats", False)
        wallet_events = config.get("wallet_events", False)
        decreasing_plot_events = config.get("decreasing_plot_events", False)
        increasing_plot_events = config.get("increasing_plot_events", False)
        if daily_stats:
            self._notification_types.append(EventType.DAILY_STATS)
            self._notification_services.append(EventService.DAILY)
        if wallet_events:
            self._notification_services.append(EventService.WALLET)
        if decreasing_plot_events:
            self._notification_types.append(EventType.PLOTDECREASE)
        if increasing_plot_events:
            self._notification_types.append(EventType.PLOTINCREASE)

    def get_title_for_event(self, event):
        icon = ""
        if event.priority == EventPriority.HIGH:
            icon = "🚨"
        elif event.priority == EventPriority.NORMAL:
            icon = "⚠️"
        elif event.priority == EventPriority.LOW:
            icon = "ℹ️"

        return f"{icon} {self._title_prefix} {event.service.name}"

    @abstractmethod
    def send_events_to_user(self, events: List[Event]) -> bool:
        """Implementation specific to the integration"""
        pass

def exponential_backoff(incident_time, interval, iteration=0, rate=1.5) -> float:
    """Calculate timestamps of notification thresholds.

    Given an initial incident time and normal reasonable notification interval in seconds,
    calculate notification threshold timestamps for different iterations.
    The iteration is expected to increase every time a notification is sent.
    """
    if type(incident_time) is datetime:
        incident_time = incident_time.timestamp()
    timestamp = incident_time + (interval * pow(rate, iteration))
    return datetime.fromtimestamp(timestamp)
