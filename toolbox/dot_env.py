import os
import inspect
from typing import Any
from dotenv import load_dotenv, find_dotenv
from traceback import format_exc as exc


def debug(title: str, var: Any = None):
    caller = inspect.currentframe().f_back
    caller_file = os.path.basename(caller.f_code.co_filename)
    print(
        f"🪲 \033[36m[{caller_file}:get_env] ⮞ \033[30m\033[106m"
        f" {title} \033[36m\033[40m : \033[96m{var}\033[0m\n"
    )


env_file = find_dotenv()
debug("env_file", env_file)
load_dotenv(env_file, override=True)


def get_env(key: str, default: Any = None, verbose: bool = False) -> Any:
    val = os.environ.get(key, default)

    if verbose:
        debug(key, f"{val} (default={default}) {type(val)}")

    if isinstance(default, bool) and not isinstance(val, bool):
        if val.lower() in ["false", "0", "none", "null"]:
            val = False
        else:
            val = bool(val)

    elif isinstance(default, int):
        try:
            val = int(float(val))
        except:
            print(f"⚠️\033[93m\033[41m Exception: {exc()}\033[0m\033[40m")
            val = 0

    elif isinstance(default, float):
        try:
            val = float(val)
        except:
            print(f"⚠️\033[93m\033[41m Exception: {exc()}\033[0m\033[40m")
            val = float(0)

    return val
