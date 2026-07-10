"""Cached reads for immutable, content-addressed Prospect substrates."""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=64)
def _sha256_at_version(path_text: str, size: int, modified_ns: int) -> str:
    del size, modified_ns
    digest = hashlib.sha256()
    with Path(path_text).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    """Hash a frozen file, invalidating the cache if its filesystem version changes."""

    resolved = path.resolve()
    stat = resolved.stat()
    return _sha256_at_version(str(resolved), stat.st_size, stat.st_mtime_ns)


def clear_hash_cache() -> None:
    _sha256_at_version.cache_clear()
