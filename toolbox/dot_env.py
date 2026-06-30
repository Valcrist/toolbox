import os
import pathlib
from typing import Any
from dotenv import find_dotenv, load_dotenv
from traceback import format_exc
from toolbox.exceptions import ToolboxError


def print_env(title: str, var: Any = None):
    """Print an env var name and value with color coding."""
    print(f"\033[36m[env] \033[96m{title}\033[36m : \033[92m{var}\033[0m")


ENV_FILE = find_dotenv()
print_env("ENV_FILE", ENV_FILE)
load_dotenv(ENV_FILE, override=True)

_ENV_OVERRIDE_MAP = {
    "DEV": ".env.dev",
    "STAGING": ".env.staging",
    "PROD": ".env.prod",
    "LOCAL": ".env.local",
    "TEST": ".env.test",
}
_env_name = os.environ.get("ENV", "").upper()
_override_filename = _ENV_OVERRIDE_MAP.get(_env_name)

if _env_name and not _override_filename:
    print_env(
        "ENV_OVERRIDE", f"WARNING: unknown ENV value '{_env_name}'; using default .env"
    )
elif _override_filename:
    _base_dir = pathlib.Path(ENV_FILE).parent if ENV_FILE else pathlib.Path.cwd()
    _override_path = _base_dir / _override_filename
    if _override_path.exists():
        load_dotenv(_override_path, override=True)
        print_env("ENV_OVERRIDE", _override_path)
    else:
        print_env(
            "ENV_OVERRIDE",
            f"WARNING: {_override_filename} not found; using default .env",
        )

DEBUG = int(os.environ.get("DEBUG", 0))


def get_env(
    key: str, default: Any = None, verbose: int = 0, required: bool = False
) -> Any:
    """Read an environment variable, casting it to the same type as default."""
    val = os.environ.get(key, default)

    if verbose and DEBUG >= verbose:
        print_env(f"{key} [{type(val).__name__}]", f"{val} (default={default})")

    if required and val is None:
        raise ToolboxError(f"Environment variable {key} is required but not set")

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
