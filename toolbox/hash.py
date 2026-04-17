import hashlib
import pickle
from typing import Optional, Any
from toolbox.exceptions import ToolboxWarning


def hash_str(text: str, salt: str = "", length: int = 32) -> Optional[str]:
    """Return an SHA-256 hex digest of salt+text, truncated to length characters."""
    try:
        salted = salt + text
        hash_digest = hashlib.sha256(salted.encode("utf-8")).hexdigest()
        return hash_digest[:length]
    except Exception as e:
        ToolboxWarning(f"Error hashing string [{e}]")
        return None


def hash_var(*var: Any, salt: str = "", length: int = 32) -> Optional[str]:
    """Return an SHA-256 hex digest of a pickled variable, truncated to length chars."""
    try:
        data = var[0] if len(var) == 1 else var
        serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        salted = salt.encode("utf-8") + serialized
        hash_digest = hashlib.sha256(salted).hexdigest()
        return hash_digest[:length]
    except Exception as e:
        ToolboxWarning(f"Error hashing variable [{e}]")
        return None


def hash_file(file: str, salt: str = "", length: int = 32) -> Optional[str]:
    """Return an SHA-256 hex digest of a file's contents, truncated to length chars."""
    try:
        sha = hashlib.sha256()
        sha.update(salt.encode("utf-8"))
        buf = memoryview(bytearray(512 * 1024))  # 512kb buffer
        with open(file, "rb", buffering=0) as f:
            for i in iter(lambda: f.readinto(buf), 0):
                sha.update(buf[:i])
        hash_digest = sha.hexdigest()
        return hash_digest[:length]
    except Exception as e:
        ToolboxWarning(f"Error hashing file: {file} [{e}]")
        return None


def hash(*var: Any, salt: str = "", length: int = 32) -> Optional[str]:
    """Return a 32-character hash of var (alias for hash_var)."""
    return hash_var(var, salt, length)


def short_hash(*var: Any, salt: str = "", length: int = 16) -> Optional[str]:
    """Return a 16-character hash of var."""
    return hash_var(var, salt, length)


def full_hash(*var: Any, salt: str = "", length: int = 64) -> Optional[str]:
    """Return a 64-character hash of var."""
    return hash_var(var, salt, length)
