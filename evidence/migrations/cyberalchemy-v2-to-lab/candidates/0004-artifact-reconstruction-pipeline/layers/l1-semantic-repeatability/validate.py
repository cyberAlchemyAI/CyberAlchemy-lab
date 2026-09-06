#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

import author


ROOT = Path(__file__).resolve().parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(author.canonical_bytes(value))


def authority_effects(value) -> list:
    results = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "authority_effect":
                results.append(child)
            results.extend(authority_effects(child))
    elif isinstance(value, list):
        for child in value:
            results.extend(authority_effects(child))
    return results


def render_receipt(value: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is validation.json. -->", "", "# L1 Semantic Repeatability Validation", "",
        f'- Result: `{value["result"]}`', f'- Checks: `{value["summary"]["passed"]}/{value["summary"]["total"]}`',
        f'- Definitions: `{value["summary"]["definitions"]}`', f'- Authority effect: `{value["authority_effect"]}`', "",
        "| Check | Result | Detail |", "|---|---|---|",
    ]
    lines.extend(f'| `{item["check_id"]}` | `{item["result"]}` | {item["detail"]} |' for item in value["checks"])
    lines.extend(["", "## Claim ceiling", "", value["claim_ceiling"], ""])
    return "\n".join(lines)


def main() -> None:
    checks = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "BLOCK", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    registry = load(ROOT / "registry.json")
    batches_record = load(ROOT / "batches.json")
    drift = load(ROOT / "drift-audit.json")
    manifest = load(ROOT / "manifest.json")
    target_index = load(author.TARGET_INDEX)
    admitted_registry = load(author.ADMITTED_REGISTRY)
    schema = load(author.DEFINITION_SCHEMA)
    renderer = author.module(author.DEFINITION_GENERATOR, "l1_definition_validation")
    sections = author.extract_source_sections()
    scaffolds = author.semantic_scaffolds()
    scaffold_by_target = {item[1]["target_id"]: item for item in scaffolds}
    semantic_targets = [item["target_id"] for item in target_index["entries"] if item["family"] == "semantic"]
    definition_paths = sorted((ROOT / "definitions").glob("*/v1/definition.json"))
    definitions = [load(path) for path in definition_paths]

    l0_receipt = load(author.L0_RECEIPT)
    check(
        "l0-predecessor-current",
        l0_receipt["result"] == "PASS"
        and candidate["predecessor_layer"]["manifest_sha256"] == sha(author.L0_MANIFEST)
        and candidate["predecessor_layer"]["receipt_sha256"] == sha(author.L0_RECEIPT),
        "The exact passing L0 manifest and receipt remain current.",
    )
    registry_targets = [item["target_id"] for item in registry["entries"]]
    check(
        "semantic-target-closure",
        len(semantic_targets) == len(registry_targets) == len(definitions) == 69
        and set(semantic_targets) == set(registry_targets),
        "All 69 remaining semantic targets are represented exactly once.",
    )
    check(
        "candidate-identity-uniqueness",
        len({item["definition_id"] for item in definitions}) == 69
        and len({item["index_entry"]["entry_id"] for item in definitions}) == 69
        and len({item["proposed_home"] for item in registry["entries"]}) == 69,
        "Definition identities, versioned entries, and proposed homes are unique.",
    )
    check(
        "admitted-registry-noncollision",
        not ({item["definition_id"] for item in definitions} & set(admitted_registry["current_lookup"])),
        "No L1 candidate silently succeeds an admitted Lab Definition identity.",
    )

    schema_errors = {path.as_posix(): list(Draft202012Validator(schema).iter_errors(value)) for path, value in zip(definition_paths, definitions)}
    check("definition-v1-conformance", all(not errors for errors in schema_errors.values()), "Every candidate conforms independently to the admitted Definition/v1 schema.")
    check(
        "three-voice-closure",
        all(set(item["voices"]) == {"scientific_formal", "plain_language", "domain_context"} for item in definitions)
        and all(item["voices"]["plain_language"]["normative"] is False and item["voices"]["domain_context"]["normative"] is False for item in definitions),
        "Every Definition colocates formal, non-normative plain, and non-normative Lab-context voices.",
    )
    check(
        "domain-context-locality",
        all(item["voices"]["domain_context"]["workspace_ref"] == str(author.LAB) for item in definitions),
        "Every domain-context voice is anchored to CyberAlchemy-lab.",
    )
    check(
        "projection-parity",
        all(path.with_name("DEFINITION.md").read_text(encoding="utf-8") == renderer.render(value) for path, value in zip(definition_paths, definitions)),
        "All 69 human views are exact generated projections of canonical JSON.",
    )
    check(
        "source-semantic-preservation",
        all("Bound source-semantic basis:" in item["voices"]["scientific_formal"]["normative_statement"] for item in definitions)
        and all(
            author.subsection(sections[source["source_ref"].split(":")[-1]]["section"], "Normative Definition")
            in item["voices"]["scientific_formal"]["normative_statement"]
            for item in definitions for source in item["source_refs"]
        ),
        "Normalized identity and exact source normative meaning remain colocated without copying source files.",
    )

    expected_sources = {source["definition_id"]: source["section_sha256"] for _, scaffold in scaffolds for source in scaffold["source_refs"] if "definition_id" in source}
    check(
        "source-section-currentness",
        drift["result"] == "PASS" and drift["source_count"] == drift["current_count"] == 53
        and all(sections[legacy]["sha256"] == digest for legacy, digest in expected_sources.items()),
        "All 53 exact CyberAlchemy-v2 source sections match their accepted normalization digests.",
    )
    check(
        "source-binding-parity",
        all(
            source["content_sha256"] == expected_sources[source["source_ref"].split(":")[-1]]
            for item in definitions for source in item["source_refs"]
        ),
        "Every Definition carries its accepted source selector and exact section digest.",
    )

    source_to_targets: dict[str, list[str]] = defaultdict(list)
    for _, scaffold in scaffolds:
        for source in scaffold["source_refs"]:
            if "definition_id" in source:
                source_to_targets[source["definition_id"]].append(scaffold["target_id"])
    definition_by_target = {item["definition_id"].replace("cal.definition.", "semantic.", 1): item for item in definitions}
    split_sources = {legacy: targets for legacy, targets in source_to_targets.items() if len(targets) > 1}
    shared_source_targets = {target for targets in split_sources.values() for target in targets}
    check(
        "split-target-noncollapse",
        all(
            all(sibling in " ".join(definition_by_target[target]["boundaries"]) for sibling in targets if sibling != target)
            for legacy, targets in split_sources.items() for target in targets
        ),
        "Every target sharing a split source explicitly excludes absorption of its sibling identities.",
    )
    check(
        "split-target-specific-meaning",
        shared_source_targets == set(author.TARGET_SPECIFIC_MEANINGS)
        and all(
            "Target-specific normative meaning:" in definition_by_target[target]["voices"]["scientific_formal"]["normative_statement"]
            for target in shared_source_targets
        )
        and all(
            len({definition_by_target[target]["voices"]["plain_language"]["explanation"] for target in targets}) == len(targets)
            for targets in split_sources.values()
        ),
        "All 29 shared-source targets carry explicit, mutually distinct normative and plain-language meanings.",
    )
    check(
        "source-target-identity-separation",
        all(item["definition_id"].startswith("cal.definition.") for item in definitions)
        and all(source["source_ref"].startswith("cyberalchemy-v2:CAV2-D") for item in definitions for source in item["source_refs"]),
        "Lab target identities remain distinct from CyberAlchemy-v2 source identities.",
    )

    derived_edges, derived_residue = author.dependency_model(scaffolds, sections)
    recorded_edges = [(item["dependency_target_id"], item["consumer_target_id"]) for item in batches_record["edges"]]
    check("dependency-derivation", recorded_edges == derived_edges, "All semantic edges are deterministically derived from exact source-section CAV2-D references.")
    check("legacy-reference-residue", drift["legacy_reference_residue"] == derived_residue, "Unmapped legacy references are explicit source-lineage residue, never silently inferred as Lab dependencies.")
    batches = batches_record["batches"]
    target_batch = {target: batch["dependency_level"] for batch in batches for target in batch["target_ids"]}
    check(
        "batch-topology",
        len(target_batch) == 69 and all(target_batch[source] <= target_batch[target] for source, target in derived_edges)
        and all(item["decision_question"].startswith("After this batch, we know whether") for item in batches),
        "Dependency batches are complete, topologically ordered, and decision-bounded.",
    )
    check(
        "registry-batch-parity",
        all(item["batch_id"] == f'L1-B{target_batch[item["target_id"]] + 1:02d}' for item in registry["entries"]),
        "Every candidate registry entry names its derived dependency batch.",
    )

    siblings: dict[str, list[str]] = defaultdict(list)
    consumers: dict[str, list[str]] = defaultdict(list)
    for _, scaffold in scaffolds:
        for source in scaffold["source_refs"]:
            if "definition_id" in source:
                siblings[source["definition_id"]].append(scaffold["target_id"])
    for dependency, consumer in derived_edges:
        consumers[dependency].append(consumer)
    reproduced = []
    for scaffold_path, scaffold in sorted(scaffolds, key=lambda item: item[1]["target_id"], reverse=True):
        expected = author.definition_record(scaffold_path, scaffold, sections, siblings, consumers)
        actual = definition_by_target[scaffold["target_id"]]
        reproduced.append(author.canonical_bytes(expected) == author.canonical_bytes(actual))
    check("reverse-order-repeatability", all(reproduced) and len(reproduced) == 69, "Every Definition reproduces byte-exactly when evaluated in reverse target order.")

    fixtures = sorted((ROOT / "fixtures/invalid").glob("*.json"))
    check(
        "hostile-fixtures",
        len(fixtures) == 3 and all(list(Draft202012Validator(schema).iter_errors(load(path))) for path in fixtures),
        "Definition/v1 rejects missing voice, invalid source digest, and inferred authority fields.",
    )
    check(
        "registry-digest-closure",
        all((author.LAB / item["path"]).is_file() and sha(author.LAB / item["path"]) == item["sha256"] for item in registry["entries"]),
        "The candidate registry binds every Definition to exact bytes.",
    )
    check(
        "admitted-registry-unchanged",
        any(item["path"] == author.rel(author.ADMITTED_REGISTRY) and item["sha256"] == sha(author.ADMITTED_REGISTRY) for item in manifest["source_bindings"]),
        "The admitted Definition registry is input-bound and remains outside the candidate write surface.",
    )
    check(
        "top-level-projections",
        (ROOT / "CANDIDATE.md").read_text(encoding="utf-8") == author.render_candidate(candidate)
        and (ROOT / "REGISTRY.md").read_text(encoding="utf-8") == author.render_registry(registry)
        and (ROOT / "BATCHES.md").read_text(encoding="utf-8") == author.render_batches(batches_record)
        and (ROOT / "DRIFT-AUDIT.md").read_text(encoding="utf-8") == author.render_drift(drift)
        and (ROOT / "MANIFEST.md").read_text(encoding="utf-8") == author.render_manifest(manifest),
        "Every top-level human surface is generated from canonical machine data.",
    )
    check(
        "manifest-material-closure",
        all((ROOT / item["path"]).is_file() and sha(ROOT / item["path"]) == item["sha256"] for item in manifest["materials"]),
        "Every L1 candidate material matches its manifest digest.",
    )
    source_roots = {"cyberalchemy-lab": author.LAB, "cyberalchemy-v2-source": author.SOURCE}
    check(
        "manifest-source-closure",
        all((source_roots[item["repository_id"]] / item["path"]).is_file() and sha(source_roots[item["repository_id"]] / item["path"]) == item["sha256"] for item in manifest["source_bindings"]),
        "Every selected Lab and CyberAlchemy-v2 source binding is current.",
    )
    check(
        "candidate-only-authority",
        set(authority_effects({"candidate": candidate, "registry": registry, "batches": batches_record, "drift": drift, "manifest": manifest})) == {"none"}
        and all(item["classification"]["lifecycle_posture_ref"] == "candidate:artifact-reconstruction-l1/v1" for item in definitions),
        "All package effects remain none and all Definition lifecycles remain candidate-only.",
    )
    check(
        "claim-ceiling",
        candidate["status"] == "prototype-construction-candidate" and "does not admit definitions" in candidate["claim_ceiling"],
        "L1 validation cannot admit definitions, synchronize the live registry, or execute migration.",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-l1-semantic-repeatability-validation/v1", "candidate_id": candidate["candidate_id"],
        "result": result, "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "total": len(checks), "definitions": len(definitions), "source_sections": drift["source_count"], "dependency_edges": len(recorded_edges), "batches": len(batches), "legacy_reference_residue": len(drift["legacy_reference_residue"])},
        "authority_effect": "none", "claim_ceiling": "PASS proves the exact L1 semantic-family reconstruction candidate is complete, source-current, independently reproducible, schema-valid, and projection-exact. It does not admit definitions, alter the live registry, execute migration, commit, push, publish, release, deploy, or authorize external effects.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    (ROOT / "receipts/VALIDATION.md").write_text(render_receipt(receipt), encoding="utf-8")
    print(f"L1_SEMANTIC_REPEATABILITY={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"DEFINITIONS={receipt['summary']['definitions']}")
    if result != "PASS":
        for item in checks:
            if item["result"] != "PASS":
                print(f"BLOCK {item['check_id']}: {item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
