import os
import inspect
from types import FrameType
from traceback import format_exc


def _emit(
    txt: str, clr: FrameType, lbl: str, c1: str, c2: str, tb: bool = True
) -> None:
    print(
        f"\033[93m{c1} ⚠️ [{os.path.basename(clr.f_code.co_filename)}"
        f":{clr.f_code.co_name}] {lbl}: {txt} \033[0m\033[40m\n"
    )
    if tb:
        print(f"{c2}🔍 {format_exc()}\033[0m\033[40m")


class ToolboxError(Exception):
    def __init__(self, message: str, traceback: bool = True):
        super().__init__(message)
        _emit(
            message,
            inspect.currentframe().f_back,
            "ERROR",
            "\033[41m",
            "\033[91m",
            traceback,
        )


class ToolboxWarning(Exception):
    def __init__(self, message: str, traceback: bool = True):
        super().__init__(message)
        _emit(
            message,
            inspect.currentframe().f_back,
            "WARNING",
            "\033[45m",
            "\033[33m",
            traceback,
        )
