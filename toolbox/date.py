import pytz
from typing import Optional, Union, Tuple, List
from datetime import UTC, datetime, timedelta
from tzlocal import get_localzone
from toolbox.dot_env import get_env
from toolbox.utils import log, debug
from traceback import format_exc as exc


_DATE_FORMAT = get_env("DATE_FORMAT", "%Y-%m-%dT%H:%M:%S.%fZ")


def is_date(date: datetime) -> bool:
    return isinstance(date, datetime)


def default_date() -> datetime:
    timestamp = 946684800  # 2000-01-01 00:00:00 GMT+0000
    return datetime.fromtimestamp(timestamp)


def set_tz(date: datetime, tz_name: Optional[str] = None) -> datetime:
    try:
        tz = pytz.timezone(tz_name) if tz_name else get_localzone()
        if isinstance(date, datetime):
            return date.replace(tzinfo=tz)
    except Exception as e:
        log(f"Error setting timezone: {e}", lvl="warning")
        log(f"Exception: {exc()}", lvl="warning")
        print()
    return date


def time_now(tz_name: Optional[str] = None) -> datetime:
    tz = pytz.timezone(tz_name) if tz_name else get_localzone()
    return datetime.now(tz)


def utc_now(string: Union[bool, str] = False) -> Union[datetime, str]:
    time_now = datetime.now(UTC)
    time_now = time_now.replace(tzinfo=pytz.utc)
    if not string:
        return time_now
    elif isinstance(string, str):
        return time_now.strftime(string)
    else:
        return time_now.strftime(_DATE_FORMAT)


def utc_now_min(string: Union[bool, str] = False) -> Union[datetime, str]:
    time_now = utc_now()
    time_now = time_now.replace(second=0, microsecond=0)
    if not string:
        return time_now
    elif isinstance(string, str):
        return time_now.strftime(string)
    else:
        return time_now.strftime(_DATE_FORMAT)


def to_date(
    date: Union[datetime, str],
    format: str = _DATE_FORMAT,
    default: Union[str, datetime] = "utc",
    tz: pytz.timezone = pytz.utc,
) -> datetime:
    if is_date(date):
        return date.replace(tzinfo=tz)
    try:
        if len(date) > 27:
            date = f"{date[:26]}{date[-1]}"
        date = datetime.strptime(date, format)
        return date.replace(tzinfo=tz)
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
    if isinstance(date, datetime):
        return date.replace(tzinfo=pytz.utc)
    try:
        if len(date) > 27:
            date = f"{date[:26]}{date[-1]}"
        date = datetime.strptime(date, format)
        return date.replace(tzinfo=pytz.utc)
    except:
        log(
            f"Exception occured while converting date={date}, "
            f"format={format}; will fallback to {default}",
            lvl="warning",
        )
        log(f"Exception: {exc()}", lvl="warning")
        return utc_now() if default == "utc" else default


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


def timestamp_to_date(timestamp: int, tz: pytz.timezone = pytz.utc) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=tz)


def time_delta(
    start: Union[datetime, str],
    end: Union[datetime, str] = utc_now(),
    format: str = _DATE_FORMAT,
) -> float:
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format)
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


def round_to_last_min(date, format="%Y-%m-%dT%H:%M:%S.%fZ"):
    date = to_date(date, format=format)
    rounded = to_date(date).replace(second=0, microsecond=0)
    rounded = rounded - timedelta(minutes=1)
    return rounded


def delta_days(
    start: Union[datetime, str],
    end: Union[datetime, str] = utc_now(),
    format: str = _DATE_FORMAT,
) -> Union[int, None]:
    try:
        start = to_date(start, format=format)
        end = to_date(end, format=format)
        delta = end - start
        return delta.days
    except:
        log(f"Exception: {exc()}", lvl="error")
        return None


def fill_days(
    start: Union[datetime, str],
    end: Union[datetime, str] = utc_now(),
    mins: int = 10,
    format: str = _DATE_FORMAT,
) -> List[datetime]:
    intervals = []
    try:
        start = round_date(start, mins=mins)
        end = round_date(end, mins=mins, ceil=True)
        debug(start, lvl=2)
        debug(end, lvl=2)
        intervals = []
        current_date = start
        while current_date <= end:
            intervals.append(current_date)
            current_date += timedelta(minutes=mins)
        debug(intervals, lvl=2)
        return intervals
    except:
        log(f"Exception: {exc()}", lvl="error")
        return intervals


def date_days_ago(days: Union[int, None] = None, now: datetime = utc_now()) -> datetime:
    if not is_date(now):
        now = utc_now()
        log(f"[now] is not a date; will use current UTC time", lvl="warning")
    if not days or not isinstance(days, int):
        return now
    return now - timedelta(days=days)


def dates_between(
    start: Union[datetime, str],
    end: Union[datetime, str] = utc_now(),
    format: str = "%Y-%m-%d",
    string: bool = True,
) -> Tuple[List[Union[str, datetime]], List[int]]:
    start = to_date(start, format=format)
    end = to_date(end, format=format)
    dates = []
    intervals = []
    current = start
    while current <= end:
        curr_date = str(current.date())
        if string:
            dates.append(curr_date)
        else:
            dates.append(current.date())
        intervals.append(int(timestamp(curr_date, format="%Y-%m-%d")))
        current += timedelta(days=1)
    return dates, intervals
