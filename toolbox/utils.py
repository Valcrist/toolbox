import ast
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
from rich.pretty import pretty_repr
from toolbox.dot_env import get_env
from toolbox.exceptions import ToolboxError, ToolboxWarning
from traceback import format_exc
from rich.console import Console


DEBUG = get_env("DEBUG", 0, verbose=1)
DATE_FORMAT = get_env("DATE_FORMAT", "%Y-%m-%d %H:%M:%S.%f %z", verbose=2)
_console = Console()


def obj_to_srl(obj: Any, dt_format: str = DATE_FORMAT, verbose: bool = False) -> Any:
    """Recursively convert an object to a JSON-serializable form."""
    lvl = 0 if verbose else 9
    if DEBUG >= lvl:
        printc(
            f"[obj_to_srl] object type: {type(obj)}", color="bright_cyan", bg="black"
        )
        printc(f"[obj_to_srl] object value: {obj}", color="bright_cyan", bg="black")
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


def obj_to_json(obj: Any) -> str:
    """Serialize an object to a JSON string."""
    return json.dumps(obj_to_srl(obj))


def trace(msg: Optional[str] = "") -> str:
    """Return msg appended with the current traceback when DEBUG >= 2."""
    if DEBUG < 2:
        return msg
    return f"{msg}\n\n{format_exc()}" if msg else format_exc()


def var2json(file: str, data: Any) -> bool:
    """Serialize data and write it to a JSON file, creating directories as needed."""
    try:
        Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
        with open(file, "w", encoding="utf-8") as outfile:
            json.dump(obj_to_srl(data), outfile, indent=2)
        return True
    except Exception as e:
        ToolboxError(f"Failed to save JSON to file: {file} [{e}]")
    return False


def json2var(
    file: str, default: Optional[Any] = None, validity: Union[bool, int] = False
) -> Any:
    """Load a JSON file into a Python object, optionally rejecting stale files."""
    if not os.path.isfile(file):
        return default
    if validity and (time.time() - os.path.getmtime(file)) > validity:
        ToolboxWarning(f"File is stale; ignoring: {file}")
        return default
    try:
        with open(file, encoding="utf-8") as json_file:
            return json.load(json_file)
    except Exception as e:
        ToolboxError(f"Failed to load JSON from file: {file} [{e}]")
    return default


def csv2var(csv_path: str) -> List[Dict[str, Any]]:
    """Load a CSV file into a list of row dicts."""
    data = []
    try:
        with open(csv_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row:
                    data.append(row)
    except Exception as e:
        ToolboxError(f"Failed to load CSV from file: {csv_path} [{e}]")
    return data


def df2dict(df: Any) -> Dict[str, Any]:
    """Convert a DataFrame to a dict keyed by column index."""
    try:
        return df.T.to_dict()
    except Exception as e:
        ToolboxWarning(f"Failed to convert dataframe to dict [{e}]")
        return {}


def str2float(s: Union[str, float]) -> float:
    """Convert a string (with optional commas) to a float."""
    if isinstance(s, float):
        return s
    try:
        return float(s.replace(",", ""))
    except Exception as e:
        ToolboxWarning(f"Failed to convert string to float: {s!r} [{e}]")
        return 0


def str2dec(s: str) -> dec:
    """Strip non-numeric characters from a string and return it as a Decimal."""
    try:
        return dec(re.sub(r"[^\d.]", "", s))
    except Exception as e:
        ToolboxWarning(f"Failed to convert string to decimal: {s!r} [{e}]")
        return dec(0)


def dec2float(v: Union[dec, float]) -> float:
    """Convert a Decimal to float, returning non-Decimal values unchanged."""
    if not isinstance(v, dec):
        return v
    try:
        return float(v)
    except Exception as e:
        ToolboxWarning(f"Failed to convert decimal to float: {v!r} [{e}]")
        return v


def to_usd(val: float) -> str:
    """Format a float as a USD currency string."""
    return f"${'{:,.02f}'.format(val)}"


def split_list_by_parts(lst: List[Any], parts: int) -> List[List[Any]]:
    """Split a list into N roughly equal parts."""
    size = len(lst) // parts
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def split_list_by_length(lst: List[Any], max: int) -> List[List[Any]]:
    """Split a list into chunks of at most max elements."""
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
    """Convert a SQLAlchemy ORM row to a plain dict."""
    data = {}
    for column in row.__table__.columns:
        data[column.name] = getattr(row, column.name)
    return data


def to_dict(
    result: Union[List[Any], tuple, set, Any]
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Convert one or more ORM rows to a dict or list of dicts."""
    if isinstance(result, (list, tuple, set)):
        data = []
        for row in result:
            data.append(row_to_dict(row))
        return data
    else:
        return row_to_dict(result)


def sqldata_to_json(data: Any) -> str:
    """Convert ORM result(s) directly to a JSON string."""
    return json.dumps(obj_to_srl(to_dict(data)))


def get_float_len(val: float) -> int:
    """Return the number of decimal places in a float."""
    val_str = str(val)
    return len(val_str.split(".")[1]) if "." in val_str else 0


def float_normalize(
    val: float, float_len: Optional[int] = None, ref: Optional[float] = None
) -> float:
    """Round val to a precision inferred from float_len or a reference float."""
    if not isinstance(float_len, int):
        if isinstance(ref, float):
            float_len = get_float_len(ref)
        else:
            float_len = get_float_len(val)
    return round(val, float_len)


def float_to_str(num: float, precision: int = 20) -> str:
    """Convert a float to a string with trailing zeros stripped."""
    format_string = "{:." + str(precision) + "f}"
    return format_string.format(num).rstrip("0").rstrip(".")


def truncate_strings(
    obj: list | tuple | dict, limit: int = 3000
) -> list | tuple | dict:
    """Truncate any string values longer than limit inside a list, tuple, or dict."""

    def _trim(v: object) -> object:
        return (
            v[:limit] + " ⟪✂️ truncated ✂️⟫"
            if isinstance(v, str) and len(v) > limit
            else v
        )

    if isinstance(obj, dict):
        return {k: _trim(v) for k, v in obj.items()}
    truncated = [_trim(v) for v in obj]
    return tuple(truncated) if isinstance(obj, tuple) else truncated


def last_run(init: int = 0, reset: bool = False) -> float:
    """Return seconds elapsed since the caller last called this function."""
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
    """Convert a camelCase string to snake_case."""
    snake_case = "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")
    return snake_case


def snake_to_camel(s: str) -> str:
    """Convert a snake_case string to camelCase."""
    camel_case = "".join(word.capitalize() for word in s.split("_"))
    camel_case = camel_case[0].lower() + camel_case[1:]  # lowercase 1st char
    return camel_case


def varDump(var: Any, label: Optional[str] = None, get: bool = False) -> Optional[str]:
    """Pretty-print a variable as JSON; return the string instead when get=True."""
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
    """Snake_case alias for varDump."""
    varDump(var, label=label, get=get)


def get_basename(file_path: str, split: Union[bool, int] = False) -> Union[str, tuple]:
    """Return basename of a path; split=1 returns stem, split=2 returns (stem, ext)."""
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
    no_nl: Union[int, bool] = 0,
    end: str = "\n",
    lvl: int = -1,
) -> None:
    """Print text with ANSI foreground/background color and optional padding."""
    if DEBUG < lvl:
        return
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
    print(f"{color_code}{bgcol_code}{padding}{text}{padding}{reset_code}", end=end)
    if color != "default" and bg == "default" and no_nl == 0:
        no_nl = True
    if not no_nl:
        print()


def get_caller(caller: Optional[FrameType] = None) -> str:
    """Return (filename, function_name) of the calling frame."""
    if not caller:
        caller = inspect.currentframe().f_back
    caller_file = os.path.basename(caller.f_code.co_filename)
    caller_func = caller.f_code.co_name
    return caller_file, caller_func


def proc_msg(
    tag: str,
    msg: str,
    col1: str,
    col2: str,
    bg: str,
    caller: Optional[FrameType] = None,
    traceback: bool = True,
) -> str:
    """Print a tagged diagnostic message, optionally with a traceback."""
    caller_file, caller_func = get_caller(caller)
    header = f"⚠️ [{caller_file}:{caller_func}] {tag}:"
    printc(f"{header} {msg}", col1, bg, pad=1)
    if traceback and DEBUG > 1:
        printc(f"🔍 {format_exc()}", col2, pad=0)
    message = trace(msg) if traceback else msg
    return message


def err(text: str, caller: Optional[FrameType] = None, traceback: bool = True) -> str:
    """Log and print an ERROR message with red styling."""
    return proc_msg(
        "ERROR", text, "bright_yellow", "bright_red", "red", caller, traceback
    )


def warn(text: str, caller: Optional[FrameType] = None, traceback: bool = True) -> str:
    """Log and print a WARNING message with magenta styling."""
    return proc_msg(
        "WARNING", text, "bright_yellow", "yellow", "magenta", caller, traceback
    )


def debug(
    var: Any,
    var_name: Optional[str] = None,
    lvl: int = 1,
    caller: Optional[FrameType] = None,
    always: bool = False,
    no_nl: bool = False,
) -> None:
    """Print a labeled debug dump of var when DEBUG >= lvl."""
    if not always and DEBUG < lvl:
        return

    i = f":{lvl}" if lvl > 1 else ""

    if not caller:
        caller = inspect.currentframe().f_back

    caller_file = os.path.basename(caller.f_code.co_filename)
    caller_func = caller.f_code.co_name

    try:
        if not var_name:
            source_line = (
                inspect.getframeinfo(caller, context=1).code_context[0].strip()
            )
            call = ast.parse(source_line, mode="eval").body
            if isinstance(call, ast.Call) and call.args:
                var_name = ast.unparse(call.args[0])
    except Exception:
        pass

    if not var_name:
        var_name = "unlabelled var"

    if isinstance(var, str):
        try:
            var = json.loads(var)
        except Exception:
            pass

    if not isinstance(var, (list, tuple, dict)):
        print(
            f"🪲{i} \033[36m[{caller_file}:{caller_func}] ⮞ \033[30m\033[106m"
            f" {var_name} \033[36m\033[40m : \033[96m{var}\033[0m"
            f"{'' if no_nl else '\n'}"
        )

    else:
        print(
            f"🪲{i} \033[36m[{caller_file}:{caller_func}] ⮞ \033[30m\033[106m"
            f" {var_name} \033[36m\033[40m :\033[0m\033[40m"
        )
        _console.print(
            pretty_repr(truncate_strings(var), expand_all=True).replace("'", '"'),
            markup=False,
        )
        if not no_nl:
            print()


def hr(
    symbol: str = "-",
    len: int = 80,
    color: str = "bright_magenta",
    bg: str = "default",
    lvl: int = -1,
    no_nl: Union[int, bool] = 0,
    no_leading_nl: Union[int, bool] = 0,
    end: str = "\n",
) -> None:
    """Print a horizontal rule made of repeated symbol characters."""
    printc(
        f"{'' if no_leading_nl else '\n'}{symbol*len}{'' if no_nl else '\n'}",
        color=color,
        bg=bg,
        no_nl=no_nl,
        end=end,
        lvl=lvl,
    )


def var2str(var: Any, indent: int = 2) -> str:
    """Serialize a variable to an indented JSON string."""
    return json.dumps(obj_to_srl(var), indent=indent)


def fix_spaces(text: str) -> str:
    """Insert spaces between tokens where parentheses adjoin non-space characters."""
    try:
        return re.sub(r"(\S)(\()|(\))(\S)", r"\1\3 \2\4", text).strip()
    except Exception as e:
        ToolboxWarning(f"Failed to fix spaces in: {text!r} [{e}]")
        return text


def strip_brackets(text: str) -> str:
    """Remove all [...] and {...} bracketed substrings from text."""
    try:
        return re.sub(r"[\[\{].*?[\]\}]", "", text)
    except Exception as e:
        ToolboxWarning(f"Failed to strip brackets from: {text!r} [{e}]")
        return text


def strip_spaces(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    try:
        return " ".join(text.replace("\n", " ").replace("\r", " ").split()).strip()
    except Exception as e:
        ToolboxWarning(f"Failed to strip spaces from: {text!r} [{e}]")
        return text


def strip_non_num(text: Any) -> str:
    """Remove all non-digit characters from text."""
    return "".join(filter(str.isdigit, str(text)))


def longest_common_subsequence(strings: List[str], no_case: bool = False) -> str:
    """Return the longest common prefix shared by all strings."""
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
    """Return longest substr present in all strings (anywhere, not just as a prefix)."""
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


def clean_log_file(input_file: str, output_file: str) -> None:
    """Strip ANSI escape codes from input_file and write the result to output_file."""
    ansi = re.compile(r"\x1b\[[0-9;]*[mKJH]|\x1b\([AB]")
    with open(input_file, "r", encoding="utf-8", errors="replace") as fin:
        content = fin.read()
    with open(output_file, "w", encoding="utf-8") as fout:
        fout.write(ansi.sub("", content))
