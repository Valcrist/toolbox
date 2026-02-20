import os
from typing import Any
from dotenv import find_dotenv, load_dotenv
from traceback import format_exc


def print_env(title: str, var: Any = None):
    print(f"\033[36m[env] \033[96m{title}\033[36m : \033[92m{var}\033[0m")


ENV_FILE = find_dotenv()
print_env("ENV_FILE", ENV_FILE)
load_dotenv(ENV_FILE, override=True)
DEBUG = int(os.environ.get("DEBUG", 0))


def get_env(key: str, default: Any = None, verbose: int = 0) -> Any:
    val = os.environ.get(key, default)

    if verbose and DEBUG >= verbose:
        print_env(f"{key} [{type(val).__name__}]", f"{val} (default={default})")

    if isinstance(default, bool) and not isinstance(val, bool):
        if val.lower() in ["false", "0", "none", "null"]:
            val = False
        else:
            val = bool(val)

    elif isinstance(default, int):
        try:
            val = int(float(val))
        except:
            print(f"⚠️\033[93m\033[41m Exception: {format_exc()}\033[0m\033[40m")
            val = 0

    elif isinstance(default, float):
        try:
            val = float(val)
        except:
            print(f"⚠️\033[93m\033[41m Exception: {format_exc()}\033[0m\033[40m")
            val = float(0)

    return val
