from datetime import datetime
from typing import Optional


def parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    # Try a few formats used in dataset
    for fmt in (
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S+00:00",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            # Handle "+00:00" as UTC offset if %z not matched
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
