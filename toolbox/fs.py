import os
import re
import sys
import time
import shutil
from typing import Union
from pathlib import Path
from toolbox.log import log, exc


def basedir() -> Path | None:
    try:
        return Path(sys.argv[0]).resolve().parent
    except Exception as e:
        log(f"Error getting basedir: {e}", lvl="error")
        log(f"Traceback:\n{exc()}", lvl="warning")
        return None


def os_path(path: str) -> str:
    return str(path).replace("/", os.sep).replace("\\", os.sep)


def strip_basedir(path: str, basedir: Union[Path, str] = basedir()) -> str:
    if path.startswith(str(basedir)):
        return path.replace(str(basedir), "").lstrip(os.sep)
    return path


def build_path(paths: list[str] | str, basedir: Union[Path, str] = basedir()) -> str:
    if not isinstance(paths, list):
        paths = [paths]
    final = str(basedir)
    for path in paths:
        path = os_path(path)
        final = os.path.join(final, path)
    return final


def dissect_path(
    path: str, basedir: Union[Path, str] = basedir()
) -> dict[str, str | list[str] | None]:
    v = {}
    dirs = os.path.dirname(os_path(path))
    try:
        if dirs.startswith(str(basedir)):
            v["base"] = str(basedir)
            dirs = os.path.relpath(dirs, basedir)
        else:
            v["base"] = None
        v["dirs"] = dirs.split(os.sep)
        v["file"] = os.path.basename(os_path(path))
        v["name"], v["ext"] = os.path.splitext(v["file"])
        v["ext"] = v["ext"].lstrip(".")
    except:
        log(f"Error dissecting path: {path}", lvl="error")
        log(f"Traceback:\n{exc()}", lvl="warning")
    return v


def sanitize_path(path: str, sub: str = "_") -> str:
    return re.sub(r'[<>:"|?*]', sub, path)


def delete(path: Union[Path, str]) -> bool:
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return True
    except:
        log(f"Failed to delete: {path}", lvl="error")
        log(f"Traceback:\n{exc()}", lvl="warning")
    return False


def copy(src: str, dst: str, retries: int = 3, delay: int = 1) -> bool:
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for attempt in range(retries):
            try:
                if os.path.exists(src):
                    shutil.copy(src, dst)
                    return True
            except Exception as e:
                log(f"Retrying copy: {src} to {dst}", lvl="warning")
                log(f"Exception: {e}", lvl="warning")
                time.sleep(delay)
    except:
        log(f"Failed to copy: {src} to {dst}", lvl="error")
        log(f"Traceback:\n{exc()}", lvl="warning")
    return False


def move(src: str, dst: str, retries: int = 3, delay: int = 1) -> bool:
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for attempt in range(retries):
            try:
                if os.path.exists(src):
                    shutil.move(src, dst)
                    return True
            except Exception as e:
                log(f"Retrying move: {src} to {dst}", lvl="warning")
                log(f"Exception: {e}", lvl="warning")
                time.sleep(delay)
        log(
            f"Failed to move after {retries} attempts; copying instead: "
            f"{src} to {dst}",
            lvl="warning",
        )
        return copy(src, dst, retries=retries, delay=delay)
    except:
        log(f"Failed to move: {src} to {dst}", lvl="error")
        log(f"Traceback:\n{exc()}", lvl="warning")
    return False


def copy_move(
    src: str, dst: str, no_move: bool = False, not_retries: int = 3, not_delay: int = 1
) -> bool:
    if no_move:
        return copy(src, dst, retries=not_retries, delay=not_delay)
    return move(src, dst, retries=not_retries, delay=not_delay)
