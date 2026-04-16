import os
import sys
import inspect
import traceback
from types import FrameType


def _emit(txt: str, clr: FrameType, lbl: str, col: str) -> None:
    print(
        f"\033[93m{col} ⚠️ [{os.path.basename(clr.f_code.co_filename)}"
        f":{clr.f_code.co_name}] {lbl}: {txt} \033[0m\033[40m\n"
    )


def _excepthook(exc_type: type, exc_value: BaseException, exc_tb: object) -> None:
    if isinstance(exc_value, ToolboxError):
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        print(f"\033[91m🔍 {''.join(lines)}\033[0m\033[40m")
    elif isinstance(exc_value, ToolboxWarning):
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        print(f"\033[33m🔍 {''.join(lines)}\033[0m\033[40m")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook


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
