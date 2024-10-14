import os
import re
import csv
import time
import json
import uuid
import inspect
from types import FrameType
from typing import Any, Union, Optional, List, Dict
from pprint import pp, pformat
from decimal import Decimal as dec
from datetime import datetime
from base64 import b64encode
from pathlib import Path
from hexbytes import HexBytes
from toolbox.dot_env import get_env
from toolbox.log import log
from traceback import format_exc as exc


_DEBUG = get_env("DEBUG", 0)
_DATE_FORMAT = get_env("DATE_FORMAT", "%Y-%m-%dT%H:%M:%S.%fZ")
_utils_logged_msgs = []


def obj_to_srl(obj: Any, dt_format: str = _DATE_FORMAT, verbose: bool = False) -> Any:
    lvl = 0 if verbose else 2
    debug(type(obj), "object type", lvl=lvl)
    if isinstance(obj, list) or isinstance(obj, tuple):
        return [obj_to_srl(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: obj_to_srl(value) for key, value in obj.items()}
    elif isinstance(obj, datetime):
        return obj.strftime(dt_format)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, HexBytes):
        return obj.hex()
    else:
        return obj


def var2json(file: str, data: Any) -> bool:
    try:
        Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
        with open(file, "w") as outfile:
            json.dump(obj_to_srl(data), outfile, indent=2)
        return True
    except:
        log(exc(), lvl="error")
    return False


def json2var(
    file: str, default: Optional[Any] = None, validity: Union[bool, int] = False
) -> Any:
    if not os.path.isfile(file):
        return default
    if validity and (time.time() - os.path.getmtime(file)) > validity:
        log(f"File is stale; ignoring: {file}", lvl="warning")
        return default
    try:
        with open(file) as json_file:
            return json.load(json_file)
    except:
        log(exc(), lvl="error")
    return default


def csv2var(csv_path: str) -> List[Dict[str, Any]]:
    data = []
    try:
        with open(csv_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row:
                    data.append(row)
    except:
        log(exc(), lvl="error")
    return data


def df2dict(df: Any) -> Dict[str, Any]:
    try:
        return df.T.to_dict()
    except:
        return {}


def str2float(s: Union[str, float]) -> float:
    if isinstance(s, float):
        return s
    try:
        return float(s.replace(",", ""))
    except:
        return 0


def str2dec(s: str) -> dec:
    try:
        return dec(re.sub(r"[^\d.]", "", s))
    except:
        return dec(0)


def dec2float(v: Union[dec, float]) -> float:
    if not isinstance(v, dec):
        return v
    try:
        return float(v)
    except:
        return v


def to_usd(val: float) -> str:
    return f"${'{:,.02f}'.format(val)}"


def split_list_by_parts(lst: List[Any], parts: int) -> List[List[Any]]:
    size = len(lst) // parts
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def split_list_by_length(lst: List[Any], max: int) -> List[List[Any]]:
    split = []
    part = []

    for item in lst:
        if len(part) == max:
            split.append(part)
            part = []
        part.append(item)

    if part:
        split.append(part)

    return split


def row_to_dict(row: Any) -> Dict[str, Any]:
    data = {}
    for column in row.__table__.columns:
        data[column.name] = getattr(row, column.name)
    return data


def to_dict(
    result: Union[List[Any], tuple, set, Any]
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    if isinstance(result, (list, tuple, set)):
        data = []
        for row in result:
            data.append(row_to_dict(row))
        return data
    else:
        return row_to_dict(result)


def get_float_len(val: float) -> int:
    val_str = str(val)
    return len(val_str.split(".")[1]) if "." in val_str else 0


def float_normalize(
    val: float, float_len: Optional[int] = None, ref: Optional[float] = None
) -> float:
    if not isinstance(float_len, int):
        if isinstance(ref, float):
            float_len = get_float_len(ref)
        else:
            float_len = get_float_len(val)
    return round(val, float_len)


def float_to_str(num: float, precision: int = 20) -> str:
    format_string = "{:." + str(precision) + "f}"
    return format_string.format(num).rstrip("0").rstrip(".")


def last_run(init: int = 0, reset: bool = False) -> float:
    current_time = time.time()
    caller_name = inspect.stack()[1].function

    if not hasattr(last_run, "tracker"):
        last_run.tracker = {}

    if init:
        last_run.tracker[caller_name] = current_time - (init + 1)

    if reset and caller_name in last_run.tracker:
        del last_run.tracker[caller_name]

    if caller_name not in last_run.tracker:
        last_run.tracker[caller_name] = current_time

    time_passed = current_time - last_run.tracker[caller_name]

    return time_passed


def camel_to_snake(s: str) -> str:
    snake_case = "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")
    return snake_case


def snake_to_camel(s: str) -> str:
    camel_case = "".join(word.capitalize() for word in s.split("_"))
    camel_case = camel_case[0].lower() + camel_case[1:]  # lowercase 1st char
    return camel_case


def varDump(var: Any, label: Optional[str] = None, get: bool = False) -> Optional[str]:
    if label and not get:
        print(f"{label}:")
    try:
        if get:
            return json.dumps(obj_to_srl(var), indent=2)
        else:
            print(json.dumps(obj_to_srl(var), indent=2))
    except Exception as ex:
        pp(var)


def var_dump(var: Any, label: Optional[str] = None, get: bool = False) -> None:
    varDump(var, label=label, get=get)


def get_basename(file_path: str, split: Union[bool, int] = False) -> Union[str, tuple]:
    base_name = os.path.basename(file_path)
    if not split:
        return base_name
    else:
        name, ext = os.path.splitext(base_name)
        if split == 1:
            return name
        else:
            return name, ext


def printc(
    text: str,
    color: str = "default",
    bg: str = "default",
    pad: int = 1,
    no_nl: bool = False,
) -> None:
    colors = {
        "default": "\033[0m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
    }
    bg_colors = {
        "default": "\033[40m",
        "black": "\033[40m",
        "red": "\033[41m",
        "green": "\033[42m",
        "yellow": "\033[43m",
        "blue": "\033[44m",
        "magenta": "\033[45m",
        "cyan": "\033[46m",
        "white": "\033[47m",
        "bright_black": "\033[100m",
        "bright_red": "\033[101m",
        "bright_green": "\033[102m",
        "bright_yellow": "\033[103m",
        "bright_blue": "\033[104m",
        "bright_magenta": "\033[105m",
        "bright_cyan": "\033[106m",
        "bright_white": "\033[107m",
    }
    color_code = colors.get(color.lower(), colors["default"])
    bgcol_code = bg_colors.get(bg.lower(), bg_colors["default"])
    reset_code = f"{colors['default']}\033[40m"
    if pad == 1 and bg == "default":
        pad = 0
    padding = " " * pad
    print(f"{color_code}{bgcol_code}{padding}{text}{padding}{reset_code}")
    if not no_nl:
        print()


def err(text: str, caller: Optional[FrameType] = None) -> None:
    global _utils_logged_msgs
    if not caller:
        caller = inspect.currentframe().f_back
    caller_file = os.path.basename(caller.f_code.co_filename)
    caller_func = caller.f_code.co_name
    message = f"⚠️ [{caller_file}:{caller_func}] ERROR: {text}"
    _utils_logged_msgs.append([0, message])
    printc(message, "bright_yellow", "red", pad=1)


def warn(text: str, caller: Optional[FrameType] = None) -> None:
    global _utils_logged_msgs
    if not caller:
        caller = inspect.currentframe().f_back
    caller_file = os.path.basename(caller.f_code.co_filename)
    caller_func = caller.f_code.co_name
    message = f"⚠️ [{caller_file}:{caller_func}] WARNING: {text}"
    _utils_logged_msgs.append([1, message])
    printc(message, "bright_yellow", "magenta", pad=1)


def get_logged_msgs() -> List[List[Any]]:
    global _utils_logged_msgs
    return _utils_logged_msgs


def print_logged_msgs() -> None:
    global _utils_logged_msgs
    if not _utils_logged_msgs:
        return
    hr("⚠️", len=50)
    printc("Logged Messages:", "black", "yellow", pad=1)
    for msg in _utils_logged_msgs:
        if msg[0] == 0:
            printc(msg[1], "bright_yellow", "red", pad=1)
        else:
            printc(msg[1], "bright_yellow", "bright_yellow", "magenta", pad=1)


def debug(
    var: Any,
    var_name: Optional[str] = None,
    lvl: int = 1,
    caller: Optional[FrameType] = None,
    always: bool = False,
) -> None:
    if not always and _DEBUG < lvl:
        return

    i = f":{lvl}" if lvl > 1 else ""

    if not caller:
        caller = inspect.currentframe().f_back

    caller_file = os.path.basename(caller.f_code.co_filename)
    caller_func = caller.f_code.co_name

    try:
        if not var_name:
            var_name = [k for k, v in caller.f_locals.items() if v is var][0]
    except:
        pass

    if not var_name:
        var_name = "unknown"

    if not isinstance(var, (list, tuple, dict)):
        print(
            f"🪲{i} \033[36m[{caller_file}:{caller_func}] ⮞ \033[30m\033[106m"
            f" {var_name} \033[36m\033[40m : \033[96m{var}\033[0m\n"
        )

    else:
        print(
            f"🪲{i} \033[36m[{caller_file}:{caller_func}] ⮞ \033[30m\033[106m"
            f" {var_name} \033[36m\033[40m :\033[0m\033[40m"
        )
        printc(pformat(var), color="bright_cyan", bg="black")
        print()


def hr(
    symbol: str = "-",
    len: int = 100,
    color: str = "bright_magenta",
    bg: str = "default",
) -> None:
    printc(f"\n{symbol*len}\n", color=color, bg=bg)


def var2str(var: Any) -> str:
    return json.dumps(obj_to_srl(var), indent=2)


def fix_spaces(text: str) -> str:
    try:
        return re.sub(r"(\S)(\()|(\))(\S)", r"\1\3 \2\4", text).strip()
    except:
        return text


def strip_brackets(text: str) -> str:
    try:
        return re.sub(r"[\[\{].*?[\]\}]", "", text)
    except:
        return text


def strip_spaces(text: str) -> str:
    try:
        return " ".join(text.replace("\n", " ").replace("\r", " ").split()).strip()
    except:
        return text


def strip_non_num(text: Any) -> str:
    return "".join(filter(str.isdigit, str(text)))


def longest_common_subsequence(strings: List[str], no_case: bool = False) -> str:
    if not strings:
        return ""
    if no_case:
        strings = [s.lower() for s in strings]
    s1 = min(strings, key=len)
    lcs = ""
    for i in range(len(s1)):
        subseq = s1[: i + 1]  # Get subsequence from the start
        if all(s.startswith(subseq) for s in strings):
            lcs = subseq
    return lcs


def longest_common_subsequence_any(strings: List[str], no_case: bool = False) -> str:
    if not strings:
        return ""
    if no_case:
        strings = [s.lower() for s in strings]
    s1 = min(strings, key=len)
    lcs = ""
    for i in range(len(s1)):
        for j in range(i + 1, len(s1) + 1):
            subseq = s1[i:j]
            if all(subseq in s for s in strings):
                if len(subseq) > len(lcs):
                    lcs = subseq
    return lcs
