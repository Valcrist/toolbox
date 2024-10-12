import os
from typing import Any
from dotenv import load_dotenv
from traceback import format_exc as exc

load_dotenv()


def get_env(key: str, default: Any = None, verbose: bool = False) -> Any:
    lvl = 0 if verbose else 2
    val = os.environ.get(key, default)

    if verbose:
        print(f"{key} ({type(val)}): {val}")
        print(f"DEFAULT ({type(default)}): {default}")

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
