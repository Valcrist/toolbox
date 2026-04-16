import os
import re
import sys
import shutil
from typing import Union
from pathlib import Path
from toolbox.utils import warn
from toolbox.exceptions import ToolboxError


def basedir() -> Path | None:
    """Return the directory containing the running script, or None on error."""
    try:
        return Path(sys.argv[0]).resolve().parent
    except Exception as e:
        raise ToolboxError(f"Error getting basedir: {e}")


def os_path(path: str) -> str:
    """Normalize a path string using the OS-native separator."""
    return str(Path(path))


def slash_nix(path: str) -> str:
    """Convert backslashes to forward slashes."""
    return path.replace("\\", "/")


def slash_win(path: str) -> str:
    """Convert forward slashes to backslashes."""
    return path.replace("/", "\\")


def strip_basedir(path: str, basedir: Union[Path, str] = basedir()) -> str:
    """Remove the basedir prefix from a path, returning the relative remainder."""
    if path.startswith(str(basedir)):
        return path.replace(str(basedir), "").lstrip(os.sep)
    return path


def build_path(paths: list[str] | str, basedir: Union[Path, str] = basedir()) -> str:
    """Join one or more path segments onto basedir and return the result."""
    if not isinstance(paths, list):
        paths = [paths]
    final = str(basedir)
    for path in paths:
        path = os_path(path)
        final = os.path.join(final, path)
    return final


def create_path(path: Union[Path, str]) -> bool:
    """Create a directory and all missing parents. Return True on success."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        raise ToolboxError(f"Failed to create path: {path} [{e}]")


def sanitize_path(path: str, sub: str = "_") -> str:
    """Replace illegal filename characters with `sub` (default `_`)."""
    return re.sub(r'[<>:"|?*]', sub, path)


def dissect_path(
    path: str, basedir: Union[Path, str] = basedir()
) -> dict[str, str | list[str] | None]:
    """Break a path into components: base, dirs, file, name, and ext."""
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
    except Exception as e:
        raise ToolboxError(f"Error dissecting path: {path} [{e}]")
    return v


def delete(path: Union[Path, str]) -> bool:
    """Delete a file or directory tree. Return True if it existed and was removed."""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return True
    except Exception as e:
        raise ToolboxError(f"Failed to delete: {path} [{e}]")
    return False


def copy(src: str, dst: str, retries: int = 3) -> bool:
    """Copy src to dst, retrying up to `retries` times on failure."""
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for attempt in range(retries):
            try:
                if os.path.exists(src):
                    shutil.copy(src, dst)
                    return True
            except Exception as e:
                warn(f"Retrying copy [{attempt + 1}/{retries}]: {src} to {dst} [{e}]")
        warn(f"Failed to copy after {retries} attempts: {src} to {dst}")
    except Exception as e:
        raise ToolboxError(f"Failed to copy: {src} to {dst} [{e}]")
    return False


def move(src: str, dst: str, retries: int = 3) -> bool:
    """Move src to dst, retrying up to `retries` times. Falls back to copy on fail."""
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for attempt in range(retries):
            try:
                if os.path.exists(src):
                    shutil.move(src, dst)
                    return True
            except Exception as e:
                warn(f"Retrying move [{attempt + 1}/{retries}]: {src} to {dst} [{e}]")
        warn(f"Failed to move after {retries} attempts: {src} to {dst}")
    except Exception as e:
        raise ToolboxError(f"Failed to move: {src} to {dst} [{e}]")


def copy_move(src: str, dst: str, no_move: bool = False, not_retries: int = 3) -> bool:
    """Copy or move src to dst. Pass `no_move=True` to force a copy."""
    if no_move:
        return copy(src, dst, retries=not_retries)
    return move(src, dst, retries=not_retries)
