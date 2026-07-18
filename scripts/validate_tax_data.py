from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if "metadata" not in data:
        errors.append(f"{path}: missing metadata")
    if "federal" in path.parts and "filing_statuses" not in data:
        errors.append(f"{path}: missing filing_statuses")
    if "states" in path.parts and "tax_type" not in data:
        errors.append(f"{path}: missing tax_type")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in ROOT.glob("tax_data/**/*.json"):
        if "schemas" in path.parts:
            continue
        errors.extend(validate_file(path))
    if errors:
        print("\n".join(errors))
        return 1
    print("Tax data validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
