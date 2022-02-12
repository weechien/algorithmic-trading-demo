import os
from datetime import datetime, timezone
from os.path import splitext, basename, dirname

from utils.constants import CANDLESTICK_INTERVAL_TO_MS_MAP, CandlestickInterval


def interval_in_ms(interval: CandlestickInterval) -> int:
    return CANDLESTICK_INTERVAL_TO_MS_MAP[interval]


def date_to_timestamp(date: datetime) -> int:
    """Returned timestamp is offset-aware"""
    return int((date - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds() * (10 ** 3))


def timestamp_to_date(timestamp: int) -> datetime:
    """Returned datetime is offset-aware"""
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc)


def split_full_path(full_path: str) -> (str, str, str):
    filename, ext = splitext(basename(full_path.rstrip(os.sep)))
    return dirname(full_path), filename, ext
