import re
import sys
import shutil
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


def strip_basedir(path: str, basedir: Path | str = basedir()) -> str:
    """Remove the basedir prefix from a path, returning the relative remainder."""
    base = str(basedir)
    if path.startswith(base):
        return path.replace(base, "").lstrip("/\\")
    return path


def build_path(paths: list[str] | str, basedir: Path | str = basedir()) -> str:
    """Join one or more path segments onto basedir and return the result."""
    if not isinstance(paths, list):
        paths = [paths]
    return str(Path(basedir).joinpath(*paths))


def path_exists(path: Path | str) -> bool:
    """Return True if the path exists."""
    return Path(path).exists()


def is_dir(path: Path | str) -> bool:
    """Return True if the path is a directory."""
    return Path(path).is_dir()


def is_file(path: Path | str) -> bool:
    """Return True if the path is a regular file."""
    return Path(path).is_file()


def is_link(path: Path | str) -> bool:
    """Return True if the path is a symbolic link."""
    return Path(path).is_symlink()


def is_junction(path: Path | str) -> bool:
    """Return True if the path is a junction (Windows)."""
    return Path(path).is_junction()


def is_mount(path: Path | str) -> bool:
    """Return True if the path is a mount point."""
    return Path(path).is_mount()


def list_dir(path: Path | str) -> list[str]:
    """Return a list of entry names in the directory."""
    return [p.name for p in Path(path).iterdir()]


def create_path(path: Path | str) -> bool:
    """Create a directory and all missing parents. Return True on success."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        raise ToolboxError(f"Failed to create path: {path} [{e}]")


def basename(path: Path | str) -> str:
    """Return the final component of the path."""
    return Path(path).name


def barename(path: Path | str) -> str:
    """Return the filename without its extension."""
    return Path(path).stem


def dirname(path: Path | str) -> str:
    """Return the directory component of the path."""
    return str(Path(path).parent)


def normpath(path: Path | str) -> str:
    """Normalize separators and remove trailing slashes."""
    return str(Path(path))


def realpath(path: Path | str) -> str:
    """Resolve the path, collapsing `..` and symlinks."""
    return str(Path(path).resolve())


def join_path(base: Path | str, *parts: str) -> str:
    """Join base with one or more path components."""
    return str(Path(base).joinpath(*parts))


def sanitize_path(path: str, sub: str = "_") -> str:
    """Replace illegal filename characters with `sub` (default `_`)."""
    return re.sub(r'[<>:"|?*]', sub, path)


def dissect_path(
    path: str, basedir: Path | str = basedir()
) -> dict[str, str | list[str] | None]:
    """Break a path into components: base, dirs, file, name, and ext."""
    try:
        p = Path(path)
        parent = p.parent
        base_path = Path(basedir)
        v: dict[str, str | list[str] | None] = {}
        if parent.is_relative_to(base_path):
            v["base"] = str(base_path)
            dirs = parent.relative_to(base_path).parts
        else:
            v["base"] = None
            dirs = parent.parts
        v["dirs"] = list(dirs)
        v["file"] = p.name
        v["name"] = p.stem
        v["ext"] = p.suffix.lstrip(".")
    except Exception as e:
        raise ToolboxError(f"Error dissecting path: {path} [{e}]")
    return v


def delete(path: Path | str) -> bool:
    """Delete a file or directory tree. Return True if it existed and was removed."""
    try:
        p = Path(path)
        if p.is_file() or p.is_symlink():
            p.unlink()
            return True
        if p.is_dir():
            shutil.rmtree(p)
            return True
    except Exception as e:
        raise ToolboxError(f"Failed to delete: {path} [{e}]")
    return False


def copy(src: str, dst: str, retries: int = 3) -> bool:
    """Copy src to dst, retrying up to `retries` times on failure."""
    try:
        create_path(Path(dst).parent)
        for attempt in range(retries):
            try:
                if path_exists(src):
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
        create_path(Path(dst).parent)
        for attempt in range(retries):
            try:
                if path_exists(src):
                    shutil.move(src, dst)
                    return True
            except Exception as e:
                warn(f"Retrying move [{attempt + 1}/{retries}]: {src} to {dst} [{e}]")
        warn(f"Failed to move after {retries} attempts: {src} to {dst}")
    except Exception as e:
        raise ToolboxError(f"Failed to move: {src} to {dst} [{e}]")


def copy_move(src: str, dst: str, no_move: bool = False, retries: int = 3) -> bool:
    """Copy or move src to dst. Pass `no_move=True` to force a copy."""
    if no_move:
        return copy(src, dst, retries=retries)
    return move(src, dst, retries=retries)
