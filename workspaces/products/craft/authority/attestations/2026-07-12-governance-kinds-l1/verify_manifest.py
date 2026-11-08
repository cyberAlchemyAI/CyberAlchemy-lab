#!/usr/bin/env python3
"""Verify the private DomainSpec v2 governance-kind manifest and its L1 seal."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
DOMAIN_ROOT = HERE.parents[2]
REPO_ROOT = HERE.parents[4]
ATTEST_IMPL = REPO_ROOT / "cyberAlchemy-v2/development/attestation-capability/attest.py"
EXPECTED_KINDS = [
    "Validation governance",
    "Layering governance",
    "Drift governance",
]
EXPECTED_RELATION = {
    "from": "authority/decisions/2026-06-29-mint.md",
    "kind": "proposes-then-ratifies",
    "to": "authority/decisions/2026-06-29-ratify-governance-kinds.md",
}


def load_attest_impl():
    spec = importlib.util.spec_from_file_location("attest_impl", ATTEST_IMPL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load attestation implementation: {ATTEST_IMPL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_sources(manifest: dict, attest_impl) -> tuple[bool, list[dict]]:
    results = []
    seen_roles = []
    for source in manifest.get("sources", []):
        source_path = DOMAIN_ROOT / source["path"]
        raw = source_path.read_bytes()
        actual = attest_impl._sha(attest_impl.canonicalize(raw))
        text = raw.decode("utf-8")
        missing_kinds = [kind for kind in EXPECTED_KINDS if kind not in text]
        ok = actual == source["canonical_sha256"] and not missing_kinds
        results.append(
            {
                "actual_canonical_sha256": actual,
                "expected_canonical_sha256": source["canonical_sha256"],
                "kind_names_present": not missing_kinds,
                "ok": ok,
                "path": source["path"],
                "role": source["role"],
            }
        )
        seen_roles.append(source["role"])
    shape_ok = (
        manifest.get("canon_version") == attest_impl.CANON_VERSION
        and manifest.get("ratified_kinds") == EXPECTED_KINDS
        and manifest.get("relation") == EXPECTED_RELATION
        and seen_roles == ["proposal", "ratification"]
    )
    return shape_ok and all(item["ok"] for item in results), results


def main() -> int:
    manifest_path = (Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "manifest.json").resolve()
    attestation_path = (Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "attestation.json").resolve()
    manifest = json.loads(manifest_path.read_text())
    attest_impl = load_attest_impl()
    sources_ok, source_results = verify_sources(manifest, attest_impl)
    seal_verdict = "not-run"
    if attestation_path.exists():
        attestation = json.loads(attestation_path.read_text())
        seal_verdict = attest_impl.verify(attestation, str(manifest_path))
    result = {
        "canon_version": attest_impl.CANON_VERSION,
        "manifest": str(manifest_path.relative_to(REPO_ROOT)),
        "seal_verdict": seal_verdict,
        "source_results": source_results,
        "sources_ok": sources_ok,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if sources_ok and seal_verdict in {"valid", "not-run"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
