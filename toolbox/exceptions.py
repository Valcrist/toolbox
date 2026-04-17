import os
import sys
import inspect
import traceback
from types import FrameType


sys.excepthook = lambda exc_type, exc_value, exc_tb: print(
    f"\033[33m🔍 {''.join(traceback.format_exception(exc_type, exc_value, exc_tb))}"
    f"\033[0m\033[40m"
)


def _emit(txt: str, clr: FrameType, lbl: str, col: str) -> None:
    """Print a colored error/warning banner with file and function context."""
    print(
        f"\n\033[93m{col} ⚠️ [{os.path.basename(clr.f_code.co_filename)}"
        f":{clr.f_code.co_name}] {lbl}: {txt} \033[0m\033[40m\n"
    )


class ToolboxError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        _emit(
            message,
            inspect.currentframe().f_back,
            "ERROR",
            "\033[41m",
        )


class ToolboxWarning(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        _emit(
            message,
            inspect.currentframe().f_back,
            "WARNING",
            "\033[45m",
        )
