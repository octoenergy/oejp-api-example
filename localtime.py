import datetime
from typing import Optional

import pytz

TIMEZONE = "Asia/Tokyo"


def now() -> datetime.datetime:
    return datetime.datetime.now(tz=_default_tz())


def today() -> datetime.date:
    return as_localtime(now())


def days_in_the_past(
    num_days: int, date_: Optional[datetime.date] = None
) -> datetime.date:
    if not date_:
        date_ = today()
    return date_ - datetime.timedelta(days=num_days)


def midnight(date_: Optional[datetime.date] = None) -> datetime.datetime:
    if date_ is None:
        date_ = today()
    naive_midnight = datetime.datetime.combine(date_, datetime.datetime.min.time())
    return _default_tz().localize(naive_midnight, is_dst=True)


def date(dt: datetime.datetime) -> datetime.date:
    return as_localtime(dt).date()


def as_localtime(dt: datetime.datetime) -> datetime.datetime:
    return as_timezone(dt, _default_tz())


def as_timezone(dt: datetime.datetime, tz: pytz.tzinfo) -> datetime.datetime:
    if _is_naive_datetime(dt):
        raise ValueError("localtime() cannot be applied to a naive datetime")

    return dt.astimezone(tz)


def _default_tz() -> pytz.tzinfo:
    return pytz.timezone(TIMEZONE)


def _is_naive_datetime(dt: datetime.datetime) -> bool:
    return dt.utcoffset() is None
