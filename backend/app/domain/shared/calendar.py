"""Calendar helpers with no third-party dependency."""

from __future__ import annotations

import calendar
from datetime import date


def add_months(start: date, months: int) -> date:
    """Return ``start`` shifted by ``months``, clamping the day to the month's length.

    e.g. ``add_months(date(2026, 1, 31), 1) -> date(2026, 2, 28)``.
    """
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))
