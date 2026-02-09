import hashlib
import pickle
from typing import Optional, Any


def hash_str(text: str, salt: str = "", length: int = 32) -> Optional[str]:
    try:
        salted = salt + text
        hash_digest = hashlib.sha256(salted.encode("utf-8")).hexdigest()
        return hash_digest[:length]
    except Exception:
        return None


def hash_var(*var: Any, salt: str = "", length: int = 32) -> Optional[str]:
    try:
        data = var[0] if len(var) == 1 else var
        serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        salted = salt.encode("utf-8") + serialized
        hash_digest = hashlib.sha256(salted).hexdigest()
        return hash_digest[:length]
    except Exception:
        return None


def hash_file(file: str, salt: str = "", length: int = 32) -> Optional[str]:
    try:
        sha = hashlib.sha256()
        sha.update(salt.encode("utf-8"))
        buf = memoryview(bytearray(512 * 1024))  # 512kb buffer
        with open(file, "rb", buffering=0) as f:
            for i in iter(lambda: f.readinto(buf), 0):
                sha.update(buf[:i])
        hash_digest = sha.hexdigest()
        return hash_digest[:length]
    except Exception:
        return None


def hash(*var: Any, salt: str = "", length: int = 32) -> Optional[str]:
    return hash_var(var, salt, length)


def short_hash(*var: Any, salt: str = "", length: int = 16) -> Optional[str]:
    return hash_var(var, salt, length)


def full_hash(*var: Any, salt: str = "", length: int = 64) -> Optional[str]:
    return hash_var(var, salt, length)
