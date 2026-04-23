import os
import sys
import inspect
import traceback


sys.excepthook = lambda exc_type, exc_value, exc_tb: print(
    f"\033[33m🔍 {''.join(traceback.format_exception(exc_type, exc_value, exc_tb))}"
    f"\033[0m\033[40m"
)


def emit_exc(txt: str, lbl: str, col: str) -> None:
    """Print a colored error/warning banner with file and function context."""
    f = inspect.currentframe().f_back
    print(
        f"\n\033[93m{col} ⚠️ [{os.path.basename(f.f_code.co_filename)}"
        f":{f.f_code.co_name}] {lbl}: {txt} \033[0m\033[40m\n"
    )


class ToolboxError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        emit_exc(message, "ERROR", "\033[41m")


class ToolboxWarning(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        emit_exc(message, "WARNING", "\033[45m")
