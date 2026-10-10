# Copyright (c) 2026 yudukikun5120

"""Module EstimatorStore reads and writes pickled estimators with SHA-256 pinning.

``pickle.loads`` executes arbitrary code embedded in the data, so an estimator
file is only deserialized after its digest matches ``estimator/SHA256SUMS``.
The digest is computed over the very bytes handed to pickle, so the file cannot
be swapped between verification and loading.
"""

import hashlib
import hmac
import pickle
from pathlib import Path
from typing import Any

ESTIMATOR_DIR = Path("estimator")
MANIFEST_PATH = ESTIMATOR_DIR / "SHA256SUMS"


class EstimatorIntegrityError(RuntimeError):
    """Raised when an estimator file does not match its pinned digest."""


def _read_manifest() -> dict[str, str]:
    """Parse the ``sha256sum``-style manifest into ``{filename: hexdigest}``."""
    entries: dict[str, str] = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            entries[name.strip().removeprefix("*")] = digest
    return entries


def load_estimator(kanji_set: str) -> Any:  # noqa: ANN401
    """Load a pickled estimator after verifying its pinned SHA-256 digest.

    Raises:
        EstimatorIntegrityError: If the file has no pinned digest or differs.

    """
    name = f"{kanji_set}.pkl"
    data = (ESTIMATOR_DIR / name).read_bytes()
    expected = _read_manifest().get(name)
    actual = hashlib.sha256(data).hexdigest()
    if expected is None or not hmac.compare_digest(actual, expected):
        msg = f"{name} does not match the digest pinned in {MANIFEST_PATH}"
        raise EstimatorIntegrityError(msg)
    return pickle.loads(data)  # noqa: S301


def store_estimator_file(kanji_set: str, obj: Any) -> None:  # noqa: ANN401
    """Pickle ``obj`` and update its entry in the manifest."""
    name = f"{kanji_set}.pkl"
    data = pickle.dumps(obj)
    (ESTIMATOR_DIR / name).write_bytes(data)
    entries = _read_manifest() if MANIFEST_PATH.exists() else {}
    entries[name] = hashlib.sha256(data).hexdigest()
    MANIFEST_PATH.write_text(
        "".join(f"{d}  {n}\n" for n, d in sorted(entries.items())),
        encoding="utf-8",
    )
