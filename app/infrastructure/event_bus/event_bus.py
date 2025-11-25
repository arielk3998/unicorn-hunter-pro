"""
Event bus and event schemas for in-memory event-driven architecture
"""
import queue
import threading
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

# Event Schemas
@dataclass
class ProfileUpdatedEvent:
    profile_id: int
    updated_fields: Dict[str, Any]

@dataclass
class JobIngestedEvent:
    job_id: int
    source: str

@dataclass
class MatchComputedEvent:
    application_id: int
    match_score: int

@dataclass
class ApplicationSubmittedEvent:
    application_id: int
    profile_id: int
    job_posting_id: int

@dataclass
class DocumentGeneratedEvent:
    document_id: int
    application_id: int
    document_type: str

# Event Bus Implementation
class EventBus:
    def __init__(self):
        self._queue = queue.Queue()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._worker = threading.Thread(target=self._process_events, daemon=True)
        self._worker.start()

    def publish(self, event: Any):
        self._queue.put(event)

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def _process_events(self):
        while True:
            event = self._queue.get()
            event_type = type(event).__name__
            for handler in self._subscribers.get(event_type, []):
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error handling {event_type}: {e}")
