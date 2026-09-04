#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE = LAB / "product/products/ontology/v1/fixtures/valid/ontology-package.json"
VALID = ROOT / "fixtures/valid/ontology-package.json"
INVALID = ROOT / "fixtures/invalid"


def write(value: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    VALID.parent.mkdir(parents=True, exist_ok=True)
    INVALID.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, VALID)
    valid = json.loads(VALID.read_text(encoding="utf-8"))

    authority = dict(valid)
    authority["authority_effect"] = "admit"
    write(authority, INVALID / "authority-effect.json")

    missing = dict(valid)
    missing.pop("source_binding")
    write(missing, INVALID / "missing-source-binding.json")

    unknown = dict(valid)
    unknown["repository_path"] = "product/products/ontology"
    write(unknown, INVALID / "unknown-field.json")


if __name__ == "__main__":
    main()
