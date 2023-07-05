import datetime
from app_core.statistic_logic import MonthInfo, separate_month_time_segments
import pytest


def test_month():
    now = datetime.date(year=2025, month=5, day=12)
    assert separate_month_time_segments(now) == [
        datetime.date(2023, 2, 1),
        datetime.date(2023, 3, 1),
        datetime.date(2023, 4, 1),
        datetime.date(2023, 5, 1),
        datetime.date(2023, 6, 1),
        datetime.date(2023, 7, 1),
        datetime.date(2023, 8, 1),
        datetime.date(2023, 9, 1),
        datetime.date(2023, 10, 1),
        datetime.date(2023, 11, 1),
        datetime.date(2023, 12, 1),
        datetime.date(2024, 1, 1),
        datetime.date(2024, 2, 1),
        datetime.date(2024, 3, 1),
        datetime.date(2024, 4, 1),
        datetime.date(2024, 5, 1),
        datetime.date(2024, 6, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 8, 1),
        datetime.date(2024, 9, 1),
        datetime.date(2024, 10, 1),
        datetime.date(2024, 11, 1),
        datetime.date(2024, 12, 1),
        datetime.date(2025, 1, 1),
        datetime.date(2025, 2, 1),
        datetime.date(2025, 3, 1),
        datetime.date(2025, 4, 1),
        datetime.date(2025, 5, 1)]
    now = datetime.date(2023,12,29)
    assert separate_month_time_segments(now) == [
        datetime.date(2023, 2, 1),
        datetime.date(2023, 3, 1),
        datetime.date(2023, 4, 1),
        datetime.date(2023, 5, 1),
        datetime.date(2023, 6, 1),
        datetime.date(2023, 7, 1),
        datetime.date(2023, 8, 1),
        datetime.date(2023, 9, 1),
        datetime.date(2023, 10, 1),
        datetime.date(2023, 11, 1),
        datetime.date(2023, 12, 1)
    ]
    now = datetime.date(2024,4,29)
    assert separate_month_time_segments(now) == [
        datetime.date(2023, 2, 1),
        datetime.date(2023, 3, 1),
        datetime.date(2023, 4, 1),
        datetime.date(2023, 5, 1),
        datetime.date(2023, 6, 1),
        datetime.date(2023, 7, 1),
        datetime.date(2023, 8, 1),
        datetime.date(2023, 9, 1),
        datetime.date(2023, 10, 1),
        datetime.date(2023, 11, 1),
        datetime.date(2023, 12, 1),
        datetime.date(2024, 1, 1),
        datetime.date(2024, 2, 1),
        datetime.date(2024, 3, 1),
        datetime.date(2024, 4, 1)

    ]


def test_MonthInfo():
    date = datetime.date(2023, 12, 2)
    december = MonthInfo(date)
    assert december.end_interval == datetime.date(2024, 1, 1)
    assert december.month == 'Декабрь'
