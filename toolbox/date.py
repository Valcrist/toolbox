import re
import pytz
from typing import Optional, Union, Tuple, List
from datetime import datetime, timedelta
from tzlocal import get_localzone
from toolbox.dot_env import get_env
from toolbox.utils import debug
from toolbox.exceptions import ToolboxError, ToolboxWarning


_DATE_FORMAT = get_env("DATE_FORMAT", "%Y-%m-%d %H:%M:%S.%f %z", verbose=3)


def is_date(date: datetime) -> bool:
    """Return True if date is a datetime instance."""
    return isinstance(date, datetime)


def default_date() -> datetime:
    """Return 2000-01-01 00:00:00 UTC as the default sentinel date."""
    timestamp = 946684800  # 2000-01-01 00:00:00 GMT+0000
    return datetime.fromtimestamp(timestamp, tz=pytz.utc)


def set_tz(date: datetime, tz_name: Optional[str] = None) -> datetime:
    """Replace the timezone on date with tz_name, or the local zone if omitted."""
    try:
        tz = pytz.timezone(tz_name) if tz_name else get_localzone()
        if isinstance(date, datetime):
            return date.replace(tzinfo=tz)
    except Exception as e:
        ToolboxWarning(f"Error setting timezone: {e}")
    return date


def time_now(
    tz_name: Optional[Union[str, pytz.BaseTzInfo]] = None,
    format: Union[bool, str] = False,
    s: bool = True,
    ms: bool = False,
) -> Union[datetime, str]:
    """Return the current time in the given timezone, or as a formatted string."""
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
    """Return the current UTC time, optionally as a formatted string."""
    return time_now(tz_name=pytz.utc, format=format, s=s, ms=ms)


def utc_now_min(
    format: Union[bool, str] = False, ms: bool = False
) -> Union[datetime, str]:
    """Return the current UTC time truncated to the minute."""
    return time_now(tz_name=pytz.utc, format=format, s=False, ms=ms)


def to_date(
    date: Union[datetime, str],
    format: str = _DATE_FORMAT,
    default: Union[str, datetime] = "utc",
    tz: pytz.BaseTzInfo = pytz.utc,
    tz_override: bool = False,
) -> datetime:
    """Parse a date string or passthrough a datetime, applying tz when needed."""
    if is_date(date):
        return date.replace(tzinfo=tz) if tz_override or not date.tzinfo else date
    try:
        date = re.sub(r"(\.\d{6})\d+", r"\1", date)
        parsed = datetime.strptime(date, format)
        return parsed.replace(tzinfo=tz) if tz_override or not parsed.tzinfo else parsed
    except Exception as e:
        ToolboxWarning(
            f"Error converting date={date}, format={format}, default={default} [{e}]"
        )
        return utc_now() if default == "utc" else default


def to_str(date: datetime, format: str = _DATE_FORMAT) -> Union[str, None]:
    """Format a datetime as a string, raising ToolboxError on failure."""
    try:
        return date.strftime(format)
    except Exception as e:
        raise ToolboxError(f"Error converting date={date}, format={format} [{e}]")


def to_utc_date(
    date: Union[datetime, str],
    format: str = _DATE_FORMAT,
    default: Union[str, datetime] = "utc",
) -> datetime:
    """Parse date and force its timezone to UTC."""
    return to_date(date, format=format, default=default, tz=pytz.utc, tz_override=True)


def to_utc_str(date: datetime, format: str = _DATE_FORMAT) -> Union[str, None]:
    """Replace date's timezone with UTC and return it as a formatted string."""
    try:
        date = date.replace(tzinfo=pytz.utc)
        return date.strftime(format)
    except Exception as e:
        raise ToolboxError(f"Error converting date={date}, format={format} [{e}]")


def to_timestamp(date: Union[datetime, str], format: str = _DATE_FORMAT) -> int:
    """Convert a date or date string to a Unix timestamp integer."""
    date = to_date(date, format=format)
    return int(date.timestamp())


def timestamp_to_date(timestamp: int, tz: pytz.BaseTzInfo = pytz.utc) -> datetime:
    """Convert a Unix timestamp (seconds or milliseconds) to a datetime."""
    # If timestamp is in milliseconds (> year 2286), convert to seconds
    if timestamp > 999999999999:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp, tz=tz)


def time_delta(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    format: str = _DATE_FORMAT,
) -> float:
    """Return the absolute difference in seconds between start and end (default=now)."""
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format) if end else utc_now()
        debug(start, lvl=2)
        debug(end, lvl=2)
        delta = abs(end - start)
        return delta.total_seconds()
    except Exception as e:
        raise ToolboxError(
            f"Error calculating time delta: start={start}, end={end}, "
            f"format={format} [{e}]"
        )


def round_date(
    date: Union[datetime, str],
    mins: int = 5,
    ceil: bool = False,
    format: str = _DATE_FORMAT,
) -> datetime:
    """Round date down (up when ceil=True) to the nearest multiple of mins minutes."""
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
    except Exception as e:
        raise ToolboxError(f"Error rounding date={date}, format={format} [{e}]")


def round_to_last_min(
    date: Union[datetime, str], format: str = _DATE_FORMAT
) -> datetime:
    """Truncate date to the start of the preceding minute."""
    parsed = to_date(date, format=format)
    rounded = parsed.replace(second=0, microsecond=0)
    return rounded - timedelta(minutes=1)


def delta_days(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    format: str = _DATE_FORMAT,
) -> Union[int, None]:
    """Return the number of calendar days between start and end (defaults to now)."""
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format) if end else utc_now()
        delta = end - start
        return delta.days
    except Exception as e:
        raise ToolboxError(
            f"Error calculating delta days: start={start}, end={end}, "
            f"format={format} [{e}]"
        )


def fill_days(
    start: Union[datetime, str],
    end: Optional[Union[datetime, str]] = None,
    mins: int = 10,
    format: str = _DATE_FORMAT,
) -> List[datetime]:
    """Return a list of datetimes at mins-minute intervals from start to end."""
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
    except Exception as e:
        raise ToolboxError(
            f"Error filling days: start={start}, end={end}, format={format} [{e}]"
        )


def date_days_ago(
    days: Union[int, None] = None, now: Optional[datetime] = None
) -> datetime:
    """Return the datetime that was days days before now (defaults to UTC now)."""
    if now and not is_date(now):
        ToolboxWarning("[now] is not a date")
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
    """Return (date_list, timestamp_list) for every calendar day from start to end."""
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
