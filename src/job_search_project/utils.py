from __future__ import annotations

from typing import Any


def parse_salary(salary: dict[str, Any] | None) -> tuple[int | None, int | None, str | None]:
    """
    hh salary format: {"from": ..., "to": ..., "currency": "..."}
    """
    if not salary:
        return None, None, None
    return salary.get("from"), salary.get("to"), salary.get("currency")
