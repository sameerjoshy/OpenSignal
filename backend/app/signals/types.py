from dataclasses import dataclass
from datetime import datetime


@dataclass
class SignalDraft:
    source: str
    signal_type: str
    title: str
    description: str | None = None
    url: str | None = None
    raw_data: dict | None = None
    detected_at: datetime | None = None
