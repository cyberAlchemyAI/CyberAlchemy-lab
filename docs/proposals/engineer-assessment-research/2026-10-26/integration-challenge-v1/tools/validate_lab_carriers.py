"""Check candidate local records against selected Lab carrier schemas.

This is structural validation only. It neither admits a record nor proves that
its referenced identities exist in current Lab Project State.
"""

from pathlib import Path
import json
import os

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LAB = Path(os.environ.get("CYBERALCHEMY_LAB_ROOT", str(ROOT.parent / "CyberAlchemy-lab")))
TYPES = LAB / "authority/artifact-types"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


pairs = [
    (ROOT / "product/product.json", "product-identity", "v2"),
    (ROOT / "model/lab-records/project-identity.json", "project-identity", "v1"),
    (ROOT / "model/lab-records/research-inquiry.json", "research-inquiry", "v1"),
    (ROOT / "model/lab-records/experiment-design.json", "experiment-design", "v1"),
]
pairs.extend((path, "goal", "v1") for path in sorted((ROOT / "model/lab-records").glob("goal-*.json")))
pairs.extend((path, "product-thesis", "v1") for path in sorted((ROOT / "model/lab-records").glob("product-thesis*.json")))
pairs.extend((path, "product-capability", "v1") for path in sorted((ROOT / "model/lab-records").glob("capability-*.json")))
pairs.extend((path, "experiment-design", "v1") for path in sorted((ROOT / "model/lab-records").glob("experiment-design-e*.json")))
pairs.extend((path, "research-inquiry", "v1") for path in sorted((ROOT / "model/lab-records").glob("research-inquiry-rq*.json")))
pairs.extend((path, "hypothesis", "v1") for path in sorted((ROOT / "model/lab-records").glob("hypothesis-*.json")))
pairs.extend((path, "definition", "v1") for path in sorted((ROOT / "model/definition-records").glob("*/definition.json")))
pairs.append((ROOT / "model/carriers/criterion-rating/v1/request.json", "artifact-type-request", "v1"))
pairs.extend((path, "role", "v1") for path in sorted((ROOT / "model/lab-records/roles").glob("*.json")))
pairs.extend((path, "artifact-type-request", "v1") for path in sorted((ROOT / "model/carriers").glob("*/v1/request.json")) if "criterion-rating" not in str(path))
pairs.append((ROOT / "model/lab-records/integration-choice-challenge-contract.json", "challenge-contract", "v1"))

for path, kind, version in pairs:
    schema_path = TYPES / kind / version / "schema.json"
    schema = load(schema_path)
    record = load(path)
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: str(e.path))
    if errors:
        details = "; ".join(f"{list(error.path)}: {error.message}" for error in errors)
        raise AssertionError(f"{path.relative_to(ROOT)} does not conform to {kind}/{version}: {details}")

for path, keys in [
    (ROOT / "product/product.json", ("evidence_refs",)),
    (ROOT / "model/lab-records/project-identity.json", ("evidence_refs",)),
    (ROOT / "model/lab-records/research-inquiry.json", ("source_refs",)),
    (ROOT / "model/lab-records/experiment-design.json", ("protocol_ref",)),
]:
    record = load(path)
    for key in keys:
        for ref in record[key] if isinstance(record[key], list) else [record[key]]:
            local_path = ROOT / ref.split("#", 1)[0]
            assert local_path.is_file(), (path.relative_to(ROOT), key, ref)

print(f"PASS: {len(pairs)} candidate records conform structurally to selected Lab carrier schemas; local source refs resolve")
