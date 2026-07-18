from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=64)
def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def federal_tax_data(year: int) -> dict[str, Any]:
    return load_json(PROJECT_ROOT / "tax_data" / "federal" / f"{year}.json")


def state_tax_data(state: str, year: int) -> dict[str, Any]:
    return load_json(PROJECT_ROOT / "tax_data" / "states" / state.upper() / f"{year}.json")
