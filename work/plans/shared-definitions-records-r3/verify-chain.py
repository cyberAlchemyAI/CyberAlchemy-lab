from hashlib import sha256
import json
from pathlib import Path

PLAN = Path(__file__).resolve().parent
ROOT = PLAN.parents[2]

def read(path):
    return json.loads(path.read_text())

def bind(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(raw).hexdigest(), "bytes": len(raw)}

def write(name, value):
    (PLAN / name).write_text(json.dumps(value, indent=2) + chr(10))

planning = read(PLAN / "DESIGN-VERIFICATION.json")
contracts = read(PLAN / "CONTRACT-VERIFICATION.json")
build = read(PLAN / "alchlang/.local/BUILD.json")
assert planning["status"] == contracts["status"] == "PASS"
assert build["source"] == planning["source"]
generated = Path(build["output"])
assert bind(generated / "manifest.json")["sha256"] == planning["manifest_sha256"]

prior = read(PLAN.with_name("shared-definitions-records-r2") / "DESIGN-VERIFICATION.json")
assert set(prior["checks"]) <= set(planning["checks"])
join_table = read(PLAN / "JOIN-TRANSITIONS.json")
outcomes = ("Unobserved", "Committed", "Replayed", "Unknown", "Refused", "NotDispatched")
join_checks = {
    f"join-outcome-{edge['phase']}-{edge['signal']}-{outcome}"
    for edge in join_table["edges"] for outcome in outcomes
}
assert join_checks <= set(planning["checks"])
required = {
    "A01": ["regression-rejects-publication-index", "publication-rejects-reviews-from-another-cut", "publication-refuses-unbound-historical-receipt", "publication-needs-separate-canonical-authorization", "publication-rebases-on-stale-source-selector"],
    "A02": ["regression-rejects-compatibility-schema", "upgrade-rejects-unrelated-owner-scope-cut", "retained-read-rejects-a-different-body", "upgrade-refuses-dropped-exact-relation-edge"],
    "A03": ["lifecycle-refuses-unreviewed-successor", "withdrawal-needs-complete-consumer-impact"],
    "A04": ["regression-rejects-commit-with-unknown-outcome", "completed-join-preserves-history", "native-unknown-can-resolve-to-proven-refusal", "join-refuses-unknown-as-proven-refusal", "join-refuses-another-operation-observation"],
    "A05": ["regression-rejects-construction-executor", "entry-check-specification-cannot-be-empty", "completion-refuses-mismatched-entry-receipt", "completion-refuses-assessment-from-another-entry"],
    "A06": ["snapshot-refuses-local-authority-effect", "snapshot-refuses-unqualified-readers"],
    "A07": ["accepted-fixture-does-not-create-an-owner-decision", "native-unknown-inspect-before-redispatch", "matching-native-commit-produces-publication-plan-only"],
    "A08": ["join-accepts-correlated-transition-plan", "join-refuses-stale-revision", "join-refuses-unrelated-transition-evidence"],
    "A09": ["snapshot-refuses-mismatched-migration-postimage"],
    "A10": ["construction-supports-full-46-target-selection", "construction-refuses-omitted-selected-definitions", "construction-refuses-overlapping-selection-partitions"],
}
bridge = read(PLAN / "BRIDGE.json")["mappings"]
assert set(required) == {row["obligation"] for row in bridge}
coverage = []
for row in bridge:
    finding = row["obligation"]
    checks = required[finding]
    assert set(checks) <= set(planning["checks"]), finding
    coverage.append({**row, "planning_checks": checks, "review_standing": "candidate", "contract_verification": bind(PLAN / "CONTRACT-VERIFICATION.json")})
write("COVERAGE.json", {"findings": coverage, "scope":"Exact contract and pure planning design evidence. Real owner outcomes, adapters and effects require separate qualification."})

language_sources = [PLAN / "alchlang" / name for name in [
    "contracts.alch", "semantics.alch", "design.alch", "profile.json",
    "sources.json", "build.mjs", "verified-projection.mjs", "verify-design.mjs", "contracts/bounds.json", "contracts/transactions.json"
]]
write("GENERATION-RECEIPT.json", {
    "status":"PASS",
    "source_fingerprint":planning["source"],
    "generated_manifest":bind(generated / "manifest.json"),
    "source_bindings":[bind(path) for path in language_sources],
    "planning_checks":planning["check_count"],
    "retained_planning_checks":prior["check_count"],
    "join_outcome_checks":len(join_checks),
    "second_audit_regressions":4,
    "contract_checks":contracts["check_count"],
    "toolchain":build["toolchain"],
    "scope":"Candidate compilation and synthetic pure planning. Actual owner dispositions and persistence/effect realization remain external."
})
stages = [
    ("definitions", [PLAN / "DEFINITIONS.json"]),
    ("artifacts", [PLAN / "CONTRACTS.json", PLAN / "contracts/verification-ports.schema.json", PLAN / "VERIFIED-PROJECTION.json"]),
    ("ontology", [PLAN / "ONTOLOGY.json"]),
    ("business-system-bridge-ontology", [PLAN / "BRIDGE.json", PLAN / "COVERAGE.json"]),
    ("system-ontology", [PLAN / "SYSTEM.json", PLAN / "JOIN-TRANSITIONS.json"]),
    ("AlchLang", language_sources),
    ("generation", [PLAN / "DESIGN-VERIFICATION.json", PLAN / "GENERATION-RECEIPT.json"]),
]
write("CHAIN-HANDOFFS.json", {
    "standing":"candidate technical design evidence",
    "handoffs":[{
        "from":left, "to":right,
        "inputs":[bind(path) for path in inputs],
        "outputs":[bind(path) for path in outputs],
        "obligations":list(required),
        "coverage":bind(PLAN / "COVERAGE.json")
    } for (left, inputs), (right, outputs) in zip(stages, stages[1:])]
})
files = sorted(path for path in PLAN.rglob("*") if path.is_file() and ".local" not in path.relative_to(PLAN).parts and path.name != "MANIFEST.json")
write("MANIFEST.json", {"files":[bind(path) for path in files]})
print(f"Verified {len(coverage)} findings, six adjacent handoffs and {len(files)} retained successor files")
