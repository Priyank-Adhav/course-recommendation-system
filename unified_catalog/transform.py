import json
import re
from typing import Iterable, List, Optional

def parse_json_field(value) -> List[str]:
    """
    Accepts: None, list, tuple, JSON string, or plain string with commas/semicolons.
    Returns a normalized list[str] (dedup, trimmed).
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        raw = [str(v).strip() for v in value if str(v).strip()]
        return _dedup_preserve_order(raw)
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        # Try JSON
        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, tuple)):
                raw = [str(v).strip() for v in parsed if str(v).strip()]
                return _dedup_preserve_order(raw)
        except Exception:
            pass
        # Fallback split on commas/semicolons/pipes
        parts = re.split(r"[;,|]", s)
        raw = [p.strip() for p in parts if p.strip()]
        return _dedup_preserve_order(raw)
    # Fallback to string
    return [str(value).strip()]

def merge_unique_lists(*lists: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for lst in lists:
        if not lst:
            continue
        for v in lst:
            t = str(v).strip()
            key = t.lower()
            if t and key not in seen:
                seen.add(key)
                out.append(t)
    return out

def normalize_level(level: Optional[str]) -> Optional[str]:
    if not level:
        return None
    s = level.strip().lower()
    if any(k in s for k in ["intro", "beginner", "basic", "foundation"]):
        return "beginner"
    if any(k in s for k in ["intermediate", "middle"]):
        return "intermediate"
    if any(k in s for k in ["advanced", "expert"]):
        return "advanced"
    return level.strip()

def parse_weeks(value) -> Optional[int]:
    """
    Accepts int, str like '6', '6 weeks', 'Approx. 8 Weeks', '8W', '2-4 weeks'
    Returns int weeks if parseable, else None.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    s = str(value).strip().lower()
    # range like "2-4 weeks" -> take upper bound
    m = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        try:
            return int(m.group(2))
        except Exception:
            pass
    # single number
    m = re.search(r"(\d+)", s)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass
    return None

def safe_json(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return json.dumps(str(obj), ensure_ascii=False)

def _dedup_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        k = x.lower()
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out
