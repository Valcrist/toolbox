import os
import inspect
import logging
from typing import Optional
from colorlog import ColoredFormatter
from toolbox.dot_env import get_env
from traceback import format_exc


LOG_LEVEL = get_env("LOG_LEVEL", 10, verbose=1)  # debug=10, info=20

_utils_log = logging.getLogger("_utils_log")
_utils_log.setLevel(LOG_LEVEL)

_utils_formatter = ColoredFormatter(
    "%(log_color)s%(message)s",
    log_colors={
        "DEBUG": "green",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "white,bg_red,bold",
        "CRITICAL": "yellow,bg_red,bold",
    },
)

_utils_handler = logging.StreamHandler()
_utils_handler.setFormatter(_utils_formatter)
_utils_log.addHandler(_utils_handler)


def log(message: str, lvl: str = "info", category: Optional[str] = None):
    lvl = lvl.lower()
    cat = f"{category}:" if category else ""
    try:
        caller = inspect.currentframe().f_back
        caller_file = os.path.basename(caller.f_code.co_filename)
        caller_func = caller.f_code.co_name
        tag = f"{cat}{caller_file}:{caller_func}"
        if lvl == "info":
            _utils_log.info(f"[INFO:{tag}] {message}")
        elif lvl == "warning":
            _utils_log.warning(f"[WARNING:{tag}] ⚠️ {message}")
        elif lvl == "error":
            _utils_log.error(f"[ERROR:{tag}] ❌ {message}")
        elif lvl == "debug":
            _utils_log.debug(f"[DEBUG:{tag}] 🔧 {message}")
        else:
            _utils_log.info(f"[LOG:{tag}] {message}")
    except Exception as e:
        _utils_log.error(f"[EXCEPTION:{tag}:utils.log] ❌ {e}")
        _utils_log.warning(f"[TRACEBACK:{tag}:utils.log] 🕵🏻‍♂️\n{format_exc()}")
