#!/usr/bin/env python3
"""Build successor 0002 using the tested migration mechanics from predecessor 0001."""

from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
PREDECESSOR_BUILD = ROOT.parent / "0001-full-migration-architecture/build.py"
spec = importlib.util.spec_from_file_location("migration_candidate_0001_build", PREDECESSOR_BUILD)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
module.ROOT = ROOT
module.OWNED_PREFIXES = (
    ROOT.relative_to(module.LAB).as_posix() + "/",
    module.DEFINITION_ROOT.relative_to(module.LAB).as_posix() + "/",
    module.TYPE_ROOT.relative_to(module.LAB).as_posix() + "/",
)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_successor():
    inventory = module.load(ROOT / "source-inventory.json")
    inventory["inventory_id"] = "CAL-CAV2-SOURCE-INVENTORY-0002"
    dump(ROOT / "source-inventory.json", inventory)

    exclusions = module.load(ROOT / "exclusion-inventory.json")
    exclusions["inventory_id"] = "CAL-CAV2-EXCLUSION-INVENTORY-0002"
    dump(ROOT / "exclusion-inventory.json", exclusions)

    baseline = module.load(ROOT / "target-baseline.json")
    baseline["baseline_id"] = "CAL-LAB-TARGET-BASELINE-0002"
    dump(ROOT / "target-baseline.json", baseline)

    allowlist = module.load(ROOT / "copy-allowlist.json")
    allowlist["allowlist_id"] = "CAL-CAV2-COPY-ALLOWLIST-0002"
    destination_set = {item["target_path"] for item in allowlist["entries"]}
    baseline["scope"] = "allowlisted-destination-preimage-only"
    baseline["entries"] = [item for item in baseline["entries"] if item["path"] in destination_set]
    baseline["entry_count"] = len(baseline["entries"])
    baseline["root_sha256"] = module.root_digest(baseline["entries"])
    baseline["claim_ceiling"] = "Exact preimage of allowlisted migration destinations only; unrelated Lab work is outside this migration dependency set and grants no write authority."
    dump(ROOT / "target-baseline.json", baseline)
    allowlist["source_inventory_sha256"] = module.sha(ROOT / "source-inventory.json")
    allowlist["target_baseline_sha256"] = module.sha(ROOT / "target-baseline.json")
    dump(ROOT / "copy-allowlist.json", allowlist)

    expected = module.load(ROOT / "expected-postimage.json")
    expected["postimage_id"] = "CAL-CAV2-TO-LAB-POSTIMAGE-0002"
    expected["allowlist_sha256"] = module.sha(ROOT / "copy-allowlist.json")
    expected["target_baseline_sha256"] = module.sha(ROOT / "target-baseline.json")
    dump(ROOT / "expected-postimage.json", expected)

    rollback = module.load(ROOT / "rollback.json")
    rollback["rollback_id"] = "CAL-CAV2-TO-LAB-ROLLBACK-0002"
    rollback["allowlist_sha256"] = module.sha(ROOT / "copy-allowlist.json")
    dump(ROOT / "rollback.json", rollback)

    migration = module.load(ROOT / "migration.json")
    migration["migration_manifest_id"] = "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-MANIFEST-0002"
    migration["version"] = "1.0.0-test-candidate.2"
    migration["source_repository"]["inventory"]["sha256"] = module.sha(ROOT / "source-inventory.json")
    migration["target_repository"]["baseline"]["sha256"] = module.sha(ROOT / "target-baseline.json")
    migration["exclusion_inventory"]["sha256"] = module.sha(ROOT / "exclusion-inventory.json")
    migration["copy_allowlist"]["sha256"] = module.sha(ROOT / "copy-allowlist.json")
    migration["expected_postimage"]["sha256"] = module.sha(ROOT / "expected-postimage.json")
    migration["rollback_ref"]["sha256"] = module.sha(ROOT / "rollback.json")
    dump(ROOT / "migration.json", migration)
    module.write(ROOT / "MIGRATION.md", module.render_migration(migration))

    candidate = module.load(ROOT / "candidate.json")
    module.write(ROOT / "CANDIDATE.md", module.render_candidate(candidate))
    manifest = {
        "schema_version": "cyberalchemy-lab-candidate-byte-manifest/v1",
        "manifest_id": "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-CANDIDATE-MANIFEST-0002",
        "candidate_id": candidate["candidate_id"],
        "status": "candidate-digest-closure",
        "authority_effect": "none",
        "predecessor_manifest_sha256": candidate["predecessor"]["manifest_sha256"],
        "materials": [{"path": path.relative_to(module.LAB).as_posix(), "sha256": module.sha(path)} for path in module.material_paths()],
        "source_inventory_sha256": module.sha(ROOT / "source-inventory.json"),
        "target_baseline_sha256": module.sha(ROOT / "target-baseline.json"),
        "copy_allowlist_sha256": module.sha(ROOT / "copy-allowlist.json"),
        "expected_postimage_sha256": module.sha(ROOT / "expected-postimage.json"),
        "rollback_sha256": module.sha(ROOT / "rollback.json"),
        "source_direction": {"canonical": "manifest.json", "human_projection": "MANIFEST.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": "Immutable successor candidate review envelope only; it does not approve, admit, activate, execute, delete, overwrite, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "manifest.json", manifest)
    module.write(ROOT / "MANIFEST.md", "\n".join(["<!-- GENERATED FILE: canonical data is manifest.json. -->", "", "# Migration Successor Candidate Manifest", "", f"- Manifest: `{manifest['manifest_id']}`", f"- Materials: `{len(manifest['materials'])}`", f"- Predecessor manifest: `{manifest['predecessor_manifest_sha256']}`", "", "## Claim ceiling", "", manifest["claim_ceiling"]]))
    receipt = module.load(ROOT / "receipts/build.json")
    receipt["materials"] = {"manifest_sha256": module.sha(ROOT / "manifest.json"), "source_inventory_sha256": module.sha(ROOT / "source-inventory.json"), "copy_allowlist_sha256": module.sha(ROOT / "copy-allowlist.json")}
    dump(ROOT / "receipts/build.json", receipt)

if __name__ == "__main__":
    try:
        module.main()
    except SystemExit as result:
        if result.code not in (None, 0):
            raise
    normalize_successor()
    print("MIGRATION_SUCCESSOR_NORMALIZATION=PASS")
    print(f"MANIFEST_SHA256={module.sha(ROOT / 'manifest.json')}")
