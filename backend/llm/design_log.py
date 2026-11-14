"""Design log: records who chose each value, user or AI, for accountability."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DesignLogEntry:
    field: str
    value: object
    chosen_by: str  # "user" or "ai"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DesignLog:
    def __init__(self):
        self.entries: list[DesignLogEntry] = []

    def record(self, field_name: str, value, chosen_by: str):
        assert chosen_by in ("user", "ai")
        self.entries.append(DesignLogEntry(field_name, value, chosen_by))

    def as_list(self) -> list[dict]:
        return [e.__dict__ for e in self.entries]
