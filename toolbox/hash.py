import hashlib
import zlib
import json
from typing import Optional


def hash_str(text: str) -> Optional[str]:
    try:
        text = repr(text)
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return hash
    except:
        return None


def hash_file(file: str) -> Optional[str]:
    try:
        sha = hashlib.sha256()
        buf = memoryview(bytearray(256 * 1024))  # 256kb buffer
        with open(file, "rb", buffering=0) as f:
            for i in iter(lambda: f.readinto(buf), 0):
                sha.update(buf[:i])
        hash = sha.hexdigest()
        return hash
    except:
        return None


def hash_var(*var: any) -> Optional[str]:
    try:
        if len(var) == 1:
            var = var[0]
        text = json.dumps(repr(var))
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return hash
    except:
        return None


def hash(*var: any) -> Optional[str]:
    return hash_var(var)


def short_hash_str(text: str) -> Optional[str]:
    try:
        text = repr(text)
        crc32 = format(zlib.crc32(text.encode("utf-8")), "x")
        adler = format(zlib.adler32(text.encode("utf-8")), "x")
        return f"{crc32}-{adler}"
    except:
        return None


def short_hash_file(file: str) -> Optional[str]:
    try:
        crc32 = zlib.crc32(b"")
        adler = zlib.adler32(b"")
        buf = memoryview(bytearray(256 * 1024))  # 256kb buffer
        with open(file, "rb", buffering=0) as f:
            for i in iter(lambda: f.readinto(buf), 0):
                crc32 = zlib.crc32(buf[:i], crc32)
                adler = zlib.adler32(buf[:i], adler)
        crc32 = format(crc32, "x")
        adler = format(adler, "x")
        return f"{crc32}-{adler}"
    except:
        return None


def short_hash_var(*var: any) -> Optional[str]:
    try:
        if len(var) == 1:
            var = var[0]
        text = json.dumps(repr(var))
        crc32 = format(zlib.crc32(text.encode("utf-8")), "x")
        adler = format(zlib.adler32(text.encode("utf-8")), "x")
        return f"{crc32}-{adler}"
    except:
        return None


def short_hash(*var: any) -> Optional[str]:
    return short_hash_var(var)
