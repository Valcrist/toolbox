import re
import pytz
from typing import Optional, Union, Tuple, List
from datetime import datetime, timedelta
from tzlocal import get_localzone
from toolbox.dot_env import get_env
from toolbox.utils import log, debug, exc


_DATE_FORMAT = get_env("DATE_FORMAT", "%Y-%m-%d %H:%M:%S.%f %z", verbose=3)


def is_date(date: datetime) -> bool:
    return isinstance(date, datetime)


def default_date() -> datetime:
    timestamp = 946684800  # 2000-01-01 00:00:00 GMT+0000
    return datetime.fromtimestamp(timestamp, tz=pytz.utc)


def set_tz(date: datetime, tz_name: Optional[str] = None) -> datetime:
    try:
        tz = pytz.timezone(tz_name) if tz_name else get_localzone()
        if isinstance(date, datetime):
            return date.replace(tzinfo=tz)
    except Exception as e:
        log(f"Error setting timezone: {e}", lvl="warning")
        log(f"Exception: {exc()}", lvl="warning")
    return date


def time_now(
    tz_name: Optional[Union[str, pytz.BaseTzInfo]] = None,
    format: Union[bool, str] = False,
    s: bool = True,
    ms: bool = False,
) -> Union[datetime, str]:
    if isinstance(tz_name, pytz.BaseTzInfo):
        tz = tz_name
    elif isinstance(tz_name, str):
        tz = pytz.timezone(tz_name)
    else:
        tz = get_localzone()
    now = datetime.now(tz)
    if not s:
        now = now.replace(second=0)
    if not ms:
        now = now.replace(microsecond=0)
    if not format:
        return now
    elif isinstance(format, str):
        return now.strftime(format)
    else:
        return now.strftime(_DATE_FORMAT)


def utc_now(
    format: Union[bool, str] = False, s: bool = True, ms: bool = False
) -> Union[datetime, str]:
    return time_now(tz_name=pytz.utc, format=format, s=s, ms=ms)


def utc_now_min(
    format: Union[bool, str] = False, ms: bool = False
) -> Union[datetime, str]:
    return time_now(tz_name=pytz.utc, format=format, s=False, ms=ms)


def to_date(
    date: Union[datetime, str],
    format: str = _DATE_FORMAT,
    default: Union[str, datetime] = "utc",
    tz: pytz.BaseTzInfo = pytz.utc,
    tz_override: bool = False,
) -> datetime:
    if is_date(date):
        return date.replace(tzinfo=tz) if tz_override or not date.tzinfo else date
    try:
        date = re.sub(r"(\.\d{6})\d+", r"\1", date)
        parsed = datetime.strptime(date, format)
        return parsed.replace(tzinfo=tz) if tz_override or not parsed.tzinfo else parsed
    except:
        log(
            f"Exception occured while converting date={date}, "
            f"format={format}; will fallback to {default}",
            lvl="warning",
        )
        log(f"Exception: {exc()}", lvl="warning")
        return utc_now() if default == "utc" else default


def to_str(date: datetime, format: str = _DATE_FORMAT) -> Union[str, None]:
    try:
        return date.strftime(format)
    except:
        log(f"Exception: {exc()}", lvl="error")
        return None


def to_utc_date(
    date: Union[datetime, str],
    format: str = _DATE_FORMAT,
    default: Union[str, datetime] = "utc",
) -> datetime:
    return to_date(date, format=format, default=default, tz=pytz.utc, tz_override=True)


def to_utc_str(date: datetime, format: str = _DATE_FORMAT) -> Union[str, None]:
    try:
        date = date.replace(tzinfo=pytz.utc)
        return date.strftime(format)
    except:
        log(f"Exception: {exc()}", lvl="error")
        return None


def to_timestamp(date: Union[datetime, str], format: str = _DATE_FORMAT) -> int:
    date = to_date(date, format=format)
    return int(date.timestamp())


def timestamp_to_date(timestamp: int, tz: pytz.BaseTzInfo = pytz.utc) -> datetime:
    # If timestamp is in milliseconds (> year 2286), convert to seconds
    if timestamp > 999999999999:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp, tz=tz)


def time_delta(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    format: str = _DATE_FORMAT,
) -> float:
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format) if end else utc_now()
        debug(start, lvl=2)
        debug(end, lvl=2)
        delta = abs(end - start)
        return delta.total_seconds()
    except:
        log(f"Exception: {exc()}", lvl="error")
        return 0


def round_date(
    date: Union[datetime, str],
    mins: int = 5,
    ceil: bool = False,
    format: str = _DATE_FORMAT,
) -> datetime:
    try:
        date = to_date(date, format=format)
        minute = date.minute
        delta = 0 if ceil else 1
        adj_mins = (minute // mins + delta) * mins
        rounded = date + timedelta(minutes=adj_mins - minute)
        rounded = rounded.replace(second=0, microsecond=0)
        debug(date, "original date", lvl=2)
        debug(rounded, "rounded date", lvl=2)
        return rounded
    except:
        log(
            f"Exception occured while rounding date={date}; "
            f"will return original date",
            lvl="warning",
        )
        log(f"Exception: {exc()}", lvl="warning")
        return date


def round_to_last_min(
    date: Union[datetime, str], format: str = _DATE_FORMAT
) -> datetime:
    parsed = to_date(date, format=format)
    rounded = parsed.replace(second=0, microsecond=0)
    return rounded - timedelta(minutes=1)


def delta_days(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    format: str = _DATE_FORMAT,
) -> Union[int, None]:
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format) if end else utc_now()
        delta = end - start
        return delta.days
    except:
        log(f"Exception: {exc()}", lvl="error")
        return None


def fill_days(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    mins: int = 10,
    format: str = _DATE_FORMAT,
) -> List[datetime]:
    intervals = []
    try:
        end = end or utc_now()
        start = round_date(start, mins=mins)
        end = round_date(end, mins=mins, ceil=True)
        debug(start, lvl=2)
        debug(end, lvl=2)
        current_date = start
        while current_date <= end:
            intervals.append(current_date)
            current_date += timedelta(minutes=mins)
        debug(intervals, lvl=2)
        return intervals
    except:
        log(f"Exception: {exc()}", lvl="error")
        return intervals


def date_days_ago(
    days: Union[int, None] = None, now: Optional[datetime] = None
) -> datetime:
    if now and not is_date(now):
        log(f"[now] is not a date; will use current UTC time", lvl="warning")
        now = utc_now()
    elif not now:
        now = utc_now()
    if not days or not isinstance(days, int):
        return now
    return now - timedelta(days=days)


def dates_between(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    format: str = "%Y-%m-%d",
    string: bool = True,
) -> Tuple[List[Union[str, datetime]], List[int]]:
    start = to_date(start, format=format)
    end = to_date(end, format=format) if end else utc_now()
    dates = []
    intervals = []
    current = start
    while current <= end:
        curr_date = str(current.date())
        if string:
            dates.append(curr_date)
        else:
            dates.append(current.date())
        intervals.append(to_timestamp(curr_date, format="%Y-%m-%d"))
        current += timedelta(days=1)
    return dates, intervals
