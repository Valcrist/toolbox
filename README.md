<h1 align="center">Toolbox</h1>

<p align="center">
  <strong>Every project needs a toolbox. This one doesn't rust.</strong>
</p>

<p align="center">
  The Python glue code you keep rewriting, packaged once.
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/tag/Valcrist/toolbox?style=flat&label=version&color=green" alt="Version">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-polyform--nc-orange?style=flat" alt="License"></a>
  <img src="https://img.shields.io/github/languages/top/Valcrist/toolbox?style=flat" alt="Top Language">
  <img src="https://img.shields.io/badge/code%20style-pep8-73e?style=flat" alt="Code Style">
  <img src="https://img.shields.io/badge/req:python-3.10%2B-c47?style=flat" alt="Python Version">
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat" alt="Status">
</p>

---

## Overview

Toolbox is a personal Python utility library built for real-world use. It handles the tedious plumbing so you can focus on what matters:

| Module | What it does |
|---|---|
| [`toolbox.utils`](#toolboxutils) | Serialization, type conversion, string manipulation, debug output |
| [`toolbox.dot_env`](#toolboxdot_env) | Type-casting env var loader via `python-dotenv` |
| [`toolbox.fs`](#toolboxfs) | Filesystem ops — path building, copy/move, path dissection |
| [`toolbox.date`](#toolboxdate) | Timezone-aware datetime parsing, formatting, rounding, and ranges |
| [`toolbox.api`](#toolboxapi) | FastAPI middleware, Scalar docs, and uvicorn launcher |
| [`toolbox.hash`](#toolboxhash) | SHA-256 hashing for strings, variables, and files |
| [`toolbox.log`](#toolboxlog) | Colored, caller-tagged logging via `colorlog` |
| [`toolbox.runner`](#toolboxrunner) | Sync/async task runners, safe wrappers, and timed execution |
| [`toolbox.calc`](#toolboxcalc) | Numeric utilities — deltas and nearest-value selection |
| [`toolbox.web`](#toolboxweb) | Async multi-URL fetching via `aiohttp` |
| [`toolbox.exceptions`](#toolboxexceptions) | Colored custom exceptions with auto-patched `sys.excepthook` |

## Install

```
pip install git+https://github.com/Valcrist/toolbox.git
```

With FastAPI/Uvicorn support:

```
pip install "git+https://github.com/Valcrist/toolbox.git#egg=toolbox[api]"
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `0` | Debug verbosity level (0–9) |
| `DATE_FORMAT` | `%Y-%m-%d %H:%M:%S.%f %z` | Default datetime format string |
| `LOG_LEVEL` | `10` | Python logging level (10=DEBUG, 20=INFO) |

---

## `toolbox.utils`

General-purpose utilities for serialization, type conversion, string manipulation, and debugging.

---

### Serialization

#### `obj_to_srl(obj, dt_format, verbose) → Any`
Recursively convert an object to a JSON-serializable form.

| Param | Type | Default | Description |
|---|---|---|---|
| `obj` | `Any` | — | Object to convert |
| `dt_format` | `str` | `DATE_FORMAT` | Datetime format string |
| `verbose` | `bool` | `False` | Enable verbose logging |

#### `obj_to_json(obj) → str`
Serialize an object to a JSON string.

| Param | Type | Description |
|---|---|---|
| `obj` | `Any` | Object to serialize |

#### `var2str(var, indent) → str`
Serialize a variable to an indented JSON string.

| Param | Type | Default | Description |
|---|---|---|---|
| `var` | `Any` | — | Variable to serialize |
| `indent` | `int` | `2` | Indentation level |

#### `var2json(file, data) → bool`
Serialize `data` and write it to a JSON file, creating directories as needed.

| Param | Type | Description |
|---|---|---|
| `file` | `str` | Output file path |
| `data` | `Any` | Data to serialize |

#### `json2var(file, default, validity) → Any`
Load a JSON file into a Python object, optionally rejecting stale files.

| Param | Type | Default | Description |
|---|---|---|---|
| `file` | `str` | — | Path to JSON file |
| `default` | `Any` | `None` | Value to return if file missing or stale |
| `validity` | `bool \| int` | `False` | Max age in seconds before treating file as stale |

#### `csv2var(csv_path) → list[dict]`
Load a CSV file into a list of row dicts.

| Param | Type | Description |
|---|---|---|
| `csv_path` | `str` | Path to CSV file |

#### `varDump(var, label, get) → str | None`
Pretty-print a variable as JSON. Pass `get=True` to return the string instead of printing.

| Param | Type | Default | Description |
|---|---|---|---|
| `var` | `Any` | — | Variable to dump |
| `label` | `str` | `None` | Optional label printed before the value |
| `get` | `bool` | `False` | Return string instead of printing |

`var_dump` is a snake_case alias for `varDump`.

---

### Type Conversion

#### `str2float(s) → float`
Convert a string (with optional commas) to a float.

#### `str2dec(s) → Decimal`
Strip non-numeric characters and return a `Decimal`.

#### `dec2float(v) → float`
Convert a `Decimal` to `float`; passes non-`Decimal` values through unchanged.

#### `to_usd(val) → str`
Format a float as a USD currency string (e.g. `$1,234.56`).

#### `df2dict(df) → dict`
Convert a pandas DataFrame to a dict keyed by column index.

---

### ORM Helpers

#### `row_to_dict(row) → dict`
Convert a SQLAlchemy ORM row to a plain dict.

#### `to_dict(result) → dict | list[dict]`
Convert one or more ORM rows to a dict or list of dicts.

#### `sqldata_to_json(data) → str`
Convert ORM result(s) directly to a JSON string.

---

### Float Helpers

#### `get_float_len(val) → int`
Return the number of decimal places in a float.

#### `float_normalize(val, float_len, ref) → float`
Round `val` to a precision inferred from `float_len` or a reference float `ref`.

| Param | Type | Default | Description |
|---|---|---|---|
| `val` | `float` | — | Value to normalize |
| `float_len` | `int` | `None` | Explicit decimal precision |
| `ref` | `float` | `None` | Reference float to infer precision from |

#### `float_to_str(num, precision) → str`
Convert a float to a string with trailing zeros stripped.

| Param | Type | Default | Description |
|---|---|---|---|
| `num` | `float` | — | Float to convert |
| `precision` | `int` | `20` | Max decimal places |

---

### List Utilities

#### `split_list_by_parts(lst, parts) → list[list]`
Split a list into `parts` roughly equal chunks.

#### `split_list_by_length(lst, max) → list[list]`
Split a list into chunks of at most `max` elements.

#### `truncate_strings(obj, limit) → list | tuple | dict`
Truncate string values longer than `limit` inside a list, tuple, or dict.

| Param | Type | Default | Description |
|---|---|---|---|
| `obj` | `list \| tuple \| dict` | — | Container to process |
| `limit` | `int` | `3000` | Max string length |

---

### String Utilities

#### `camel_to_snake(s) → str`
Convert a camelCase string to snake_case.

#### `snake_to_camel(s) → str`
Convert a snake_case string to camelCase.

#### `fix_spaces(text) → str`
Insert spaces between tokens where parentheses adjoin non-space characters.

#### `strip_brackets(text) → str`
Remove all `[...]` and `{...}` bracketed substrings from text.

#### `strip_spaces(text) → str`
Collapse all whitespace (including newlines) into single spaces.

#### `strip_non_num(text) → str`
Remove all non-digit characters from text.

#### `longest_common_subsequence(strings, no_case) → str`
Return the longest common prefix shared by all strings.

| Param | Type | Default | Description |
|---|---|---|---|
| `strings` | `list[str]` | — | Strings to compare |
| `no_case` | `bool` | `False` | Case-insensitive comparison |

#### `longest_common_subsequence_any(strings, no_case) → str`
Return the longest substring present anywhere in all strings.

#### `get_basename(file_path, split) → str | tuple`
Return the basename of a path. `split=1` returns the stem; `split=2` returns `(stem, ext)`.

---

### Debugging & Output

#### `debug(var, var_name, lvl, caller, always, no_nl) → None`
Print a labeled debug dump of `var` when `DEBUG >= lvl`.

| Param | Type | Default | Description |
|---|---|---|---|
| `var` | `Any` | — | Variable to inspect |
| `var_name` | `str` | auto-detected | Label for the variable |
| `lvl` | `int` | `1` | Minimum DEBUG level required |
| `always` | `bool` | `False` | Print regardless of DEBUG level |
| `no_nl` | `bool` | `False` | Suppress trailing newline |

#### `printc(text, color, bg, pad, no_nl, end, lvl) → None`
Print text with ANSI foreground/background color and optional padding.

| Param | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | — | Text to print |
| `color` | `str` | `"default"` | Foreground color name |
| `bg` | `str` | `"default"` | Background color name |
| `pad` | `int` | `1` | Padding spaces around text |
| `no_nl` | `int \| bool` | `0` | Suppress trailing newline |
| `end` | `str` | `"\n"` | Line ending character |
| `lvl` | `int` | `-1` | Minimum DEBUG level required |

Available colors: `default`, `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, and all `bright_*` variants.

#### `hr(symbol, len, color, bg, lvl, no_nl, no_leading_nl, end) → None`
Print a horizontal rule made of repeated `symbol` characters.

| Param | Type | Default | Description |
|---|---|---|---|
| `symbol` | `str` | `"-"` | Character to repeat |
| `len` | `int` | `80` | Number of repetitions |
| `color` | `str` | `"bright_magenta"` | Foreground color |

#### `err(text, caller, traceback) → str`
Log and print an ERROR message with red styling.

#### `warn(text, caller, traceback) → str`
Log and print a WARNING message with magenta styling.

#### `get_logged_msgs() → list`
Return all messages logged via `err()` or `warn()` this session.

#### `print_logged_msgs() → None`
Print all buffered error/warning messages with colored separators.

#### `trace(msg) → str`
Return `msg` appended with the current traceback when `DEBUG >= 2`.

#### `last_run(init, reset) → float`
Return seconds elapsed since the caller last called this function. Useful for rate-limiting within a function.

| Param | Type | Default | Description |
|---|---|---|---|
| `init` | `int` | `0` | Treat last call as `init` seconds ago |
| `reset` | `bool` | `False` | Clear the stored timestamp |

#### `clean_log_file(input_file, output_file) → None`
Strip ANSI escape codes from `input_file` and write clean output to `output_file`.

---

## `toolbox.dot_env`

Environment variable loading via `python-dotenv`.

#### `get_env(key, default, verbose) → Any`
Read an environment variable, casting it to the same type as `default`.

| Param | Type | Default | Description |
|---|---|---|---|
| `key` | `str` | — | Environment variable name |
| `default` | `Any` | `None` | Default value (also determines cast type) |
| `verbose` | `int` | `0` | Print value when `DEBUG >= verbose` |

```python
from toolbox.dot_env import get_env

port = get_env("PORT", 8080)       # returns int
debug = get_env("DEBUG", False)    # returns bool
name = get_env("APP_NAME", "app")  # returns str
```

#### `print_env(title, var) → None`
Print an env var name and value with color coding.

---

## `toolbox.fs`

Filesystem utilities built on `pathlib.Path`.

#### `basedir() → Path`
Return the directory containing the running script.

#### `os_path(path) → str`
Normalize a path string using the OS-native separator.

#### `slash_nix(path) → str`
Convert backslashes to forward slashes.

#### `slash_win(path) → str`
Convert forward slashes to backslashes.

#### `strip_basedir(path, basedir) → str`
Remove the basedir prefix from a path, returning the relative remainder.

#### `build_path(paths, basedir) → str`
Join one or more path segments onto `basedir`.

| Param | Type | Default | Description |
|---|---|---|---|
| `paths` | `list[str] \| str` | — | Path segment(s) to append |
| `basedir` | `Path \| str` | script dir | Base directory |

#### `path_exists(path) → bool`
Return `True` if the path exists.

#### `is_dir(path) → bool`
Return `True` if the path is a directory.

#### `is_file(path) → bool`
Return `True` if the path is a regular file.

#### `is_link(path) → bool`
Return `True` if the path is a symbolic link.

#### `is_junction(path) → bool`
Return `True` if the path is a Windows junction.

#### `is_mount(path) → bool`
Return `True` if the path is a mount point.

#### `list_dir(path) → list[str]`
Return a list of entry names in a directory.

#### `create_path(path) → bool`
Create a directory and all missing parents.

#### `basename(path) → str`
Return the final component of the path (filename with extension).

#### `barename(path) → str`
Return the filename without its extension.

#### `dirname(path) → str`
Return the directory component of the path.

#### `normpath(path) → str`
Normalize separators and remove trailing slashes.

#### `realpath(path) → str`
Resolve the path, collapsing `..` and symlinks.

#### `join_path(base, *parts) → str`
Join `base` with one or more path components.

#### `sanitize_path(path, sub) → str`
Replace illegal filename characters with `sub` (default `_`).

#### `dissect_path(path, basedir) → dict`
Break a path into components: `base`, `dirs`, `file`, `name`, and `ext`.

#### `delete(path) → bool`
Delete a file or directory tree. Returns `True` if it existed and was removed.

#### `copy(src, dst, retries) → bool`
Copy `src` to `dst`, retrying up to `retries` times on failure.

| Param | Type | Default | Description |
|---|---|---|---|
| `src` | `str` | — | Source path |
| `dst` | `str` | — | Destination path |
| `retries` | `int` | `3` | Max retry attempts |

#### `move(src, dst, retries) → bool`
Move `src` to `dst`, retrying up to `retries` times.

#### `copy_move(src, dst, no_move, retries) → bool`
Copy or move `src` to `dst`. Pass `no_move=True` to force a copy.

---

## `toolbox.date`

Date/time utilities with timezone support via `pytz`.

#### `is_date(date) → bool`
Return `True` if `date` is a `datetime` instance.

#### `default_date() → datetime`
Return `2000-01-01 00:00:00 UTC` as a sentinel date.

#### `set_tz(date, tz_name) → datetime`
Replace the timezone on `date` with `tz_name`, or the local zone if omitted.

#### `time_now(tz_name, format, s, ms) → datetime | str`
Return the current time in the given timezone.

| Param | Type | Default | Description |
|---|---|---|---|
| `tz_name` | `str \| BaseTzInfo` | local zone | Timezone name or object |
| `format` | `bool \| str` | `False` | Format string, or `True` for `DATE_FORMAT` |
| `s` | `bool` | `True` | Include seconds |
| `ms` | `bool` | `False` | Include microseconds |

#### `utc_now(format, s, ms) → datetime | str`
Return the current UTC time.

#### `utc_now_min(format, ms) → datetime | str`
Return the current UTC time truncated to the minute.

#### `to_date(date, format, default, tz, tz_override) → datetime`
Parse a date string or pass through a datetime, applying `tz` when needed.

| Param | Type | Default | Description |
|---|---|---|---|
| `date` | `datetime \| str` | — | Date to parse |
| `format` | `str` | `DATE_FORMAT` | Parse format string |
| `default` | `str \| datetime` | `"utc"` | Fallback on parse error (`"utc"` or a datetime) |
| `tz` | `BaseTzInfo` | `pytz.utc` | Timezone to apply |
| `tz_override` | `bool` | `False` | Replace existing timezone even if set |

#### `to_str(date, format) → str`
Format a datetime as a string.

#### `to_utc_date(date, format, default) → datetime`
Parse `date` and force its timezone to UTC.

#### `to_utc_str(date, format) → str`
Replace `date`'s timezone with UTC and return it as a formatted string.

#### `to_timestamp(date, format) → int`
Convert a date or date string to a Unix timestamp integer.

#### `timestamp_to_date(timestamp, tz) → datetime`
Convert a Unix timestamp (seconds or milliseconds) to a datetime.

#### `time_delta(start, end, format) → float`
Return the absolute difference in seconds between `start` and `end` (default: now).

#### `round_date(date, mins, ceil, format) → datetime`
Round date down (or up when `ceil=True`) to the nearest multiple of `mins` minutes.

| Param | Type | Default | Description |
|---|---|---|---|
| `date` | `datetime \| str` | — | Date to round |
| `mins` | `int` | `5` | Minute interval to round to |
| `ceil` | `bool` | `False` | Round up instead of down |

#### `round_to_last_min(date, format) → datetime`
Truncate date to the start of the preceding minute.

#### `delta_days(start, end, format) → int`
Return the number of calendar days between `start` and `end` (default: now).

#### `fill_days(start, end, mins, format) → list[datetime]`
Return a list of datetimes at `mins`-minute intervals from `start` to `end`.

| Param | Type | Default | Description |
|---|---|---|---|
| `start` | `datetime \| str` | — | Start of range |
| `end` | `datetime \| str` | now | End of range |
| `mins` | `int` | `10` | Interval in minutes |

#### `date_days_ago(days, now) → datetime`
Return the datetime that was `days` days before `now` (default: UTC now).

#### `dates_between(start, end, format, string) → tuple[list, list]`
Return `(date_list, timestamp_list)` for every calendar day from `start` to `end`.

| Param | Type | Default | Description |
|---|---|---|---|
| `string` | `bool` | `True` | Return dates as strings; `False` returns `date` objects |

---

## `toolbox.api`

FastAPI utilities. Requires the `api` extra: `pip install toolbox[api]`.

#### `logger_middleware(app, env, log_requests, log_response, skip_paths, tarpit_max_concurrent, tarpit_delay) → None`
Register HTTP middleware that logs requests/responses and tarpits unknown routes.

| Param | Type | Default | Description |
|---|---|---|---|
| `app` | `FastAPI` | — | FastAPI app instance |
| `env` | `str` | — | Environment name (`"DEV"` enables full logging) |
| `log_requests` | `bool` | `False` | Log all request headers and bodies |
| `log_response` | `bool` | `False` | Log all response bodies |
| `skip_paths` | `list[str]` | `["/", "/docs", ...]` | Paths to exclude from logging/tarpit |
| `tarpit_max_concurrent` | `int` | `20` | Max concurrent tarpit connections |
| `tarpit_delay` | `int` | `300` | Tarpit delay in seconds for unknown routes |

#### `init_scalar_docs(app, title, favicon_url, dark_mode, targets, default_http_client) → None`
Register a `/docs` route serving a Scalar API reference page.

| Param | Type | Default | Description |
|---|---|---|---|
| `app` | `FastAPI` | — | FastAPI app instance |
| `title` | `str` | — | API title shown in the docs |
| `favicon_url` | `str` | `""` | URL to a favicon |
| `dark_mode` | `bool` | `True` | Enable dark mode |
| `targets` | `list[str]` | `["shell", "python3", "node"]` | Code sample languages |
| `default_http_client` | `dict` | `{"targetKey": "python", "clientKey": "httpx_async"}` | Default client shown in docs |

#### `run_server(module, env, port, hot_reload, use_ssl, ssl_keyfile, ssl_certfile) → None`
Start a uvicorn server for the given ASGI module string.

| Param | Type | Default | Description |
|---|---|---|---|
| `module` | `str` | — | ASGI module path (e.g. `"main:app"`) |
| `env` | `str` | — | Environment label printed at startup |
| `port` | `int` | `8080` | Port to listen on |
| `hot_reload` | `bool` | `False` | Enable auto-reload on file changes |
| `use_ssl` | `bool` | `False` | Enable HTTPS |
| `ssl_keyfile` | `str` | `None` | Path to SSL key file |
| `ssl_certfile` | `str` | `None` | Path to SSL certificate file |

---

## `toolbox.hash`

SHA-256 hashing utilities.

#### `hash_str(text, salt, length) → str | None`
Return an SHA-256 hex digest of `salt + text`, truncated to `length` characters.

| Param | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | — | String to hash |
| `salt` | `str` | `""` | Optional salt prefix |
| `length` | `int` | `32` | Output length |

#### `hash_var(*var, salt, length) → str | None`
Return an SHA-256 hex digest of a pickled variable.

#### `hash_file(file, salt, length) → str | None`
Return an SHA-256 hex digest of a file's contents (streamed, 512 KB buffer).

#### `hash(*var, salt, length) → str | None`
Alias for `hash_var` with a default `length` of `32`.

#### `short_hash(*var, salt, length) → str | None`
Return a 16-character hash of `var`.

#### `full_hash(*var, salt, length) → str | None`
Return a 64-character hash of `var`.

```python
from toolbox.hash import hash_str, hash_var, hash_file

hash_str("hello")                  # "2cf24dba5fb0..."  (32 chars)
hash_str("hello", salt="secret")   # salted hash
hash_var({"key": "value"})         # hash of pickled dict
hash_file("/path/to/file.bin")     # hash of file contents
```

---

## `toolbox.log`

Colored logging via `colorlog`.

#### `log(message, lvl, category, traceback) → None`
Log `message` at the given level, tagging it with the caller's file and function name.

| Param | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Message to log |
| `lvl` | `str` | `"info"` | Log level: `"debug"`, `"info"`, `"warning"`, `"error"` |
| `category` | `str` | `None` | Optional category prefix in the tag |
| `traceback` | `bool` | `True` | Include traceback on error |

```python
from toolbox.log import log

log("Server started", lvl="info")
log("Missing key", lvl="warning", category="config")
log("DB connection failed", lvl="error")
```

---

## `toolbox.runner`

Async task execution helpers.

#### `get_or_create_event_loop() → asyncio.AbstractEventLoop`
Return the running event loop, creating and setting a new one if none exists.

#### `run_async_tasks(*tasks) → Any | list`
Run one or more awaitables synchronously. Returns a single result if one task, otherwise a list.

```python
from toolbox.runner import run_async_tasks

result = run_async_tasks(some_coroutine())
results = run_async_tasks(coro_a(), coro_b(), coro_c())
```

#### `run_async_bg_tasks(*coro_or_future) → Any | list`
Schedule awaitables on a new event loop in a background thread.

#### `safe_run(func, default) → Any`
Call `func()`, returning `default` and emitting a warning on any exception.

#### `async_safe_run(func, default) → Any`
Async version of `safe_run`.

#### `timed_run(func, *args, **kwargs) → Any`
Call `func` with args/kwargs, print elapsed time, and return the result.

---

## `toolbox.calc`

Math utilities.

#### `calc_delta(a, b) → int | float`
Return `b - a`, or `0` if equal.

#### `select_nearest(target, options) → int | float`
Return the value in `options` closest to `target`.

| Param | Type | Description |
|---|---|---|
| `target` | `int \| float` | Reference value |
| `options` | `list[int \| float]` | Candidate values |

```python
from toolbox.calc import select_nearest

select_nearest(7, [1, 5, 10, 20])  # 5
```

---

## `toolbox.web`

Async HTTP utilities via `aiohttp`.

#### `async_get_url(url, headers, payload, response_type) → dict`
Fetch one or more URLs asynchronously. Returns `{"code": int, "resp": ...}` for a single URL, or a dict keyed by URL for multiple.

| Param | Type | Default | Description |
|---|---|---|---|
| `url` | `str \| list[str]` | — | URL or list of URLs to fetch |
| `headers` | `dict` | `{}` | Request headers |
| `payload` | `dict` | `{}` | Request body (sent as JSON) |
| `response_type` | `str` | `"text"` | `"text"` or `"json"` |

#### `get_url(url, headers, payload, response_type)`
Synchronous wrapper around `async_get_url`.

```python
from toolbox.web import get_url

result = get_url("https://example.com")
# {"code": 200, "resp": "..."}

results = get_url(["https://a.com", "https://b.com"], response_type="json")
# {"https://a.com": {"code": 200, "resp": {...}}, ...}
```

---

## `toolbox.exceptions`

Custom exception classes with colored terminal output.

### `sys.excepthook`
Automatically replaced on import to print uncaught exceptions in yellow with full traceback.

#### `ToolboxError(message)`
Raised for errors. Prints a red-highlighted banner with file/function context.

#### `ToolboxWarning(message)`
Raised for warnings. Prints a magenta-highlighted banner with file/function context.

```python
from toolbox.exceptions import ToolboxError, ToolboxWarning

raise ToolboxError("Something broke")
raise ToolboxWarning("Something looks off")
```
