#!/usr/bin/env python3
"""Build generated views and exact-byte closure for successor candidate 0002."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
PREDECESSOR = LAB / "authority/artifact-types/candidates/0001-artifact-surface-foundation"
DEFINITIONS = LAB / "authority/definitions/candidates/0010-artifact-surface-foundation-revision"
TYPE_ROOTS = [LAB / f"authority/artifact-types/{name}/v1/candidates/0002-executable-surface" for name in ["artifact-type-registry", "artifact-type-request", "canonical-package-manifest"]]
VALIDATOR = LAB / "tooling/validators/artifact_surface_candidate_2.py"
GENERATOR = LAB / "tooling/generators/artifact_surface.py"
SUITE = LAB / "tests/conformance/artifact-surface-foundation/revision-0002/suite.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def render_candidate(candidate: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is candidate.json. -->", "",
        "# Artifact Surface Foundation successor candidate 0002", "",
        f"- Candidate: `{candidate['candidate_id']}`",
        f"- Version: `{candidate['version']}`",
        f"- Status: `{candidate['status']}`",
        f"- Authority effect: `{candidate['authority_effect']}`", "",
        "## Review defects closed", "",
    ]
    lines.extend(f"- {item}" for item in candidate["review_defects"])
    lines.extend(["", "## Product-construction frontier", "", candidate["construction"]["product_frontier"], "", "## Runnable product work", ""])
    lines.extend(f"- {item}" for item in candidate["construction"]["runnable_product_work"])
    lines.extend(["", "## Operational support", ""])
    for item in candidate["construction"]["operational_support"]:
        lines.append(f"- `{item['owner_ref']}` — {item['task']} Stage: {item['affected_stage']}; blocks frontier: `{str(item['blocks_current_frontier']).lower()}`.")
    lines.extend(["", "## Causal blockers", ""])
    lines.extend(f"- {item}" for item in candidate["construction"]["causal_blockers"])
    lines.extend(["", "## Deferred operational residue", ""])
    lines.extend(f"- {item}" for item in candidate["construction"]["deferred_operational_residue"])
    lines.extend(["", "## Claim ceiling", "", candidate["claim_ceiling"]])
    return "\n".join(lines)


def render_manifest(manifest: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is manifest.json. -->", "",
        "# Artifact Surface Foundation successor manifest", "",
        f"- Manifest: `{manifest['manifest_id']}`",
        f"- Candidate: `{manifest['candidate_id']}`",
        f"- Materials: `{len(manifest['materials'])}`", "",
        "| Path | SHA-256 |", "| --- | --- |",
    ]
    lines.extend(f"| `{item['path']}` | `{item['sha256']}` |" for item in manifest["materials"])
    lines.extend(["", "## Claim ceiling", "", manifest["claim_ceiling"]])
    return "\n".join(lines)


def material_paths() -> list[Path]:
    paths: list[Path] = []
    for base in [DEFINITIONS, *TYPE_ROOTS]:
        for path in base.rglob("*"):
            if path.is_file() and "receipts" not in path.parts and "__pycache__" not in path.parts:
                paths.append(path)
    paths.extend([VALIDATOR, GENERATOR, SUITE])
    for name in ["author.py", "build.py", "validate.py", "candidate.json", "CANDIDATE.md", "audit-plan.json", "audit.json", "AUDIT.md", "registry.json", "REGISTRY.md"]:
        paths.append(ROOT / name)
    return sorted(set(paths), key=lambda path: str(path.relative_to(LAB)))


def main() -> None:
    generator = import_path("artifact_surface_generator", GENERATOR)
    validator = import_path("artifact_surface_validator_c2", VALIDATOR)

    registry = load(PREDECESSOR / "registry.json")
    registry["registry_id"] = "cal.registry.artifact-types/v1-candidate.2"
    registry["version"] = "1.0.0-test-candidate.2"
    registry["source_direction"]["generator_ref"] = "cal.generator.artifact-surface/v1"
    registry["claim_ceiling"] = "Successor candidate postimage preserving the same 25 exact decision-admitted Artifact Type versions. It is not live and changes no lifecycle state."
    dump(ROOT / "registry.json", registry)
    write(ROOT / "REGISTRY.md", generator.render_registry(registry))

    plan = load(ROOT / "audit-plan.json")
    audit = validator.audit(registry, plan)
    dump(ROOT / "audit.json", audit)
    write(ROOT / "AUDIT.md", generator.render_audit(audit))
    candidate = load(ROOT / "candidate.json")
    write(ROOT / "CANDIDATE.md", render_candidate(candidate))

    manifest = {
        "schema_version": "cyberalchemy-lab-candidate-byte-manifest/v1",
        "manifest_id": "CAL-ARTIFACT-SURFACE-FOUNDATION-MANIFEST-0002",
        "candidate_id": candidate["candidate_id"],
        "status": "candidate-digest-closure",
        "authority_effect": "none",
        "predecessor_manifest_sha256": candidate["predecessor"]["manifest_sha256"],
        "materials": [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in material_paths()],
        "source_direction": {"canonical": "manifest.json", "human_projection": "MANIFEST.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": "Digest closure for successor candidate review only. It does not approve, admit, activate, migrate, commit, push, publish, release, or deploy any material.",
    }
    dump(ROOT / "manifest.json", manifest)
    write(ROOT / "MANIFEST.md", render_manifest(manifest))
    print(f"ARTIFACT_SURFACE_SUCCESSOR_BUILD=PASS")
    print(f"MATERIALS={len(manifest['materials'])}")


if __name__ == "__main__":
    main()
