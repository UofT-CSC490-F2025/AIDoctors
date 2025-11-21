from datetime import datetime
from typing import Optional, Union


def parse_date(value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    s = value.strip()
    if not s:
        return None

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # fast path: all of our known formats are iso-compatible.
    try:
        # Handles:
        #   - "YYYY-MM-DD"
        #   - "YYYY-MM-DD HH:MM:SS"
        #   - "YYYY-MM-DD HH:MM:SS+00:00"
        #   - "YYYY-MM-DD HH:MM:SS+HH:MM"
        return datetime.fromisoformat(s)
    except ValueError:
        for fmt in (
            "%Y-%m-%d %H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S+00:00",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                if fmt.endswith("+00:00") and s.endswith("+00:00"):
                    s_fixed = s.replace("+00:00", "+0000")
                    fmt_fixed = fmt.replace("+00:00", "%z")
                    return datetime.strptime(s_fixed, fmt_fixed)
                return datetime.strptime(s, fmt)
            except Exception:
                continue

    return None


def compute_overlap_days(start: Optional[str], stop: Optional[str]) -> Optional[int]:
    ds, de = parse_date(start), parse_date(stop)
    if ds and de:
        return max(0, (de - ds).days)
    return None
