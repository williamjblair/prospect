"""Release contract for the deterministic Marson backbone."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKBONE = ROOT / "examples" / "data" / "atlas_backbone.json"


def test_fresh_checkout_contains_the_frozen_backbone():
    assert BACKBONE.exists()
    assert hashlib.sha256(BACKBONE.read_bytes()).hexdigest() == (
        "60ce305107d8d3d2f8b726c91c5c2afff970a4126d512f0abcff55ef6ae8122c"
    )

    rows = json.loads(BACKBONE.read_text())
    assert len(rows) == 11526
    assert len({row["gene"] for row in rows}) == 11526
