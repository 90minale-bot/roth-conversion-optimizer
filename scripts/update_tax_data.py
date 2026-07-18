from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    draft = ROOT / "tax_data" / "federal" / f"{args.year}.draft.json"
    if (ROOT / "tax_data" / "federal" / f"{args.year}.json").exists():
        print(f"Reviewed federal {args.year}.json exists; refusing to replace it silently.")
        return 0
    payload = {
        "metadata": {
            "tax_year": args.year,
            "retrieval_date": date.today().isoformat(),
            "manual_review_required": True,
            "source_url": "TODO: official IRS/Treasury source",
            "assumptions": "Draft placeholder created by updater; review required."
        },
        "filing_statuses": {}
    }
    draft.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote reviewable draft: {draft}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
