from datetime import datetime, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
BISHKEK = ZoneInfo("Asia/Bishkek")

def now_utc() -> datetime:
    return datetime.now(UTC)

def to_bishkek(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(BISHKEK)

def format_bishkek(dt: datetime | None, fmt: str = "%Y-%m-%d | %H:%M:%S") -> str:
    dt_b = to_bishkek(dt)
    return "" if not dt_b else dt_b.strftime(fmt)