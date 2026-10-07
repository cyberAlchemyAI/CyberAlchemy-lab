#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
SOURCE_REPO = LAB.parent / "cyberAlchemy-v2"
SOURCE_DEFINITIONS = SOURCE_REPO / "authority/definitions/DEFINITIONS.md"
DECISION_ID = "CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION"
SOURCE_ADMISSION_ROOT = Path("authority/decisions/source-admission/full-definition-queue/v1")

QUEUE_ROOTS = [
    Path("authority/definitions/candidates"),
    Path("evidence/migrations/cyberalchemy-v2-to-lab/candidates"),
]

PACKAGE_INPUTS = [
    "authority/definitions/candidates/0003-single-decision-checkpoint/candidate.json",
    "authority/definitions/candidates/0003-single-decision-checkpoint/receipts/validation.json",
    "authority/definitions/candidates/0009-artifact-surface-foundation/candidate.json",
    "authority/definitions/candidates/0009-artifact-surface-foundation/receipts/validation.json",
    "authority/definitions/candidates/0010-artifact-surface-foundation-revision/candidate.json",
    "authority/definitions/candidates/0010-artifact-surface-foundation-revision/receipts/validation.json",
    "authority/definitions/candidates/0011-repository-migration-manifest/candidate.json",
    "authority/definitions/candidates/0011-repository-migration-manifest/receipts/validation.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/candidate.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/manifest.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/candidate.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/manifest.json",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(relative: str) -> dict:
    path = LAB / relative
    return {"path": relative, "sha256": sha(path)}


def postimage(relative: str) -> Path:
    return HERE / "postimages" / relative


def version_key(version: str) -> tuple:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-candidate\.(\d+))?", version)
    if not match:
        return (version,)
    major, minor, patch, candidate = match.groups()
    return (int(major), int(minor), int(patch), int(candidate or 10**9))


def markdown_h2_section(path: Path, selector: str) -> tuple[bytes, int, int]:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^## CAV2-D(\d+): (.+)$", text))
    positions = [index for index, match in enumerate(matches) if match.group(0) == selector]
    if len(positions) != 1:
        raise ValueError(f"missing source selector: {selector}")
    index = positions[0]
    start_offset = matches[index].start()
    end_offset = matches[index + 1].start() if index + 1 < len(matches) else text.find("\n## Withdrawn Definition IDs", matches[index].end())
    if end_offset < 0:
        end_offset = len(text)
    selected = (text[start_offset:end_offset].rstrip() + "\n").encode("utf-8")
    start_line = text[:start_offset].count("\n") + 1
    end_line = start_line + len(selected.splitlines()) - 1
    return selected, start_line, end_line


def historical_v2_selection(selector: str, expected: str) -> tuple[Path, bytes, int, int] | None:
    snapshot_root = LAB / "evidence/migrations/cyberalchemy-v2-to-lab/executions"
    for path in sorted(snapshot_root.rglob("DEFINITIONS.md")):
        try:
            selected, start, end = markdown_h2_section(path, selector)
        except ValueError:
            continue
        if hashlib.sha256(selected).hexdigest() == expected:
            return path, selected, start, end
    return None


def render_index(registry: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run the bound admission builder. -->",
        "", "# CyberAlchemy Lab Definition Index", "",
        f"- Status: `{registry['status']}`",
        f"- Admission decision: `{registry['admission_decision_ref']}`", "",
        "| ID | Version | Term | Lifecycle | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in registry["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |")
    lines.extend(["", "## Current lookup", ""])
    lines.extend(f"- `{key}` -> `{value}`" for key, value in registry["current_lookup"].items())
    lines.extend(["", "## Claim ceiling", "", registry["claim_ceiling"]])
    return "\n".join(lines)


def render_drift(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit.json through its bound admission builder. -->",
        "", "# Full Definition Queue Drift Audit", "",
        "> Post-admission explanatory projection; machine JSON is canonical.", "",
    ]
    for item in data["findings"]:
        lines.extend([
            f"## {item['finding_id']} — {item['status']}", "",
            item["condition"], "", f"Remediation: {item['remediation']}", "",
        ])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_source_admissions(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: admissions.json is canonical. -->", "",
        "# Full Definition Queue Source Admissions", "",
        f"- Status: `{data['status']}`",
        f"- Decision: `{data['admission_decision_ref']}`",
        f"- Exact selections: `{len(data['admissions'])}`", "",
        "| Admission | Source | Selector | Uses | Digest |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in data["admissions"]:
        lines.append(
            f"| `{item['admission_id']}` | `{item['source_ref']}` | {item['selector']} | "
            f"{len(item['target_definition_refs'])} | `{item['selected_sha256']}` |"
        )
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_bundle(bundle: dict, receipt: dict) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: bundle.json is canonical. -->", "",
        "# Full Definition Queue v1 admission bundle", "",
        f"- Bundle: `{bundle['bundle_id']}`",
        f"- Prospective decision: `{bundle['prospective_decision_id']}`",
        f"- Validation: `{receipt['result']}`",
        f"- Definition versions: `{bundle['counts']['definition_versions']}`",
        f"- Definition identities: `{bundle['counts']['definition_identities']}`",
        f"- Reconstructed versions: `{bundle['counts']['reconstructed_versions']}`",
        f"- Source selections: `{bundle['counts']['source_selections']}`", "",
        "## Decision boundary", "", bundle["decision_boundary"]["resolution_basis"], "",
        "## Excluded effects", "", *[f"- {item}" for item in bundle["excluded_effects"]], "",
        "## Claim ceiling", "", bundle["claim_ceiling"],
    ])


def main() -> int:
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    live_registry_path = LAB / "authority/definitions/registry.json"
    live_index_path = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
    live_drift_path = LAB / "authority/definitions/drift-audit.json"
    live_drift_view_path = LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md"
    live = load(live_registry_path)
    admitted = {(item["definition_id"], item["version"]) for item in live["entries"]}

    queue: list[tuple[Path, dict]] = []
    for root in QUEUE_ROOTS:
        for path in sorted((LAB / root).rglob("definition.json")):
            value = load(path)
            key = (value.get("definition_id"), value.get("version"))
            if all(key) and key not in admitted:
                queue.append((path, value))

    identities = defaultdict(list)
    for path, value in queue:
        identities[value["definition_id"]].append((path, value))
    authority_count = sum(path.is_relative_to(LAB / "authority/definitions/candidates") for path, _ in queue)
    reconstructed_count = len(queue) - authority_count
    duplicate_identities = {key: [item[1]["version"] for item in values] for key, values in identities.items() if len(values) > 1}
    check("exact-full-queue", len(queue) == 85 and len(identities) == 81, {"versions": len(queue), "identities": len(identities)})
    check("authority-and-reconstructed-split", authority_count == 15 and reconstructed_count == 70, {"authority": authority_count, "reconstructed": reconstructed_count})
    check("four-successor-pairs", len(duplicate_identities) == 4 and all(sorted(values) == ["1.0.0-candidate.1", "1.0.0-candidate.2"] for values in duplicate_identities.values()), duplicate_identities)
    check("new-identities-not-current", not (set(identities) & set(live["current_lookup"])), sorted(set(identities) & set(live["current_lookup"])))

    schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
    generator_path = LAB / "authority/artifact-types/definition/v1/generator.py"
    schema = load(schema_path)
    validator = Draft202012Validator(schema)
    spec = importlib.util.spec_from_file_location("definition_generator_full_queue", generator_path)
    generator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(generator)

    failures = []
    definition_inputs = []
    by_ref = {}
    for path, value in queue:
        relative = str(path.relative_to(LAB))
        projection = path.parent / "DEFINITION.md"
        errors = sorted(error.message for error in validator.iter_errors(value))
        projection_ok = projection.is_file() and projection.read_text(encoding="utf-8") == generator.render(value)
        digests_ok = value["schema_digest"] == sha(schema_path) and value["source_direction"]["generator_sha256"] == sha(generator_path)
        if errors or not projection_ok or not digests_ok:
            failures.append({"definition": f"{value['definition_id']}@{value['version']}", "schema_errors": errors, "projection_ok": projection_ok, "digests_ok": digests_ok})
        definition_inputs.extend([binding(relative), binding(str(projection.relative_to(LAB)))])
        by_ref[f"{value['definition_id']}@{value['version']}"] = (path, value)
    check("all-definitions-schema-and-projection-valid", not failures, {"validated": len(queue), "failures": failures})

    package_results = []
    for relative in PACKAGE_INPUTS:
        value = load(LAB / relative)
        if relative.endswith("receipts/validation.json"):
            package_results.append({"path": relative, "result": value.get("result")})
    check("candidate-receipts-pass", len(package_results) == 6 and all(item["result"] == "PASS" for item in package_results), package_results)

    workflow_ref = live["current_lookup"].get("DS-D1.9")
    workflow_entry = next((item for item in live["entries"] if f"{item['definition_id']}@{item['version']}" == workflow_ref), None)
    check("single-checkpoint-workflow-dependency-resolved", workflow_ref == "DS-D1.9@1.0.0-candidate.1" and workflow_entry is not None and workflow_entry["lifecycle_state"] == "admitted", workflow_ref)

    source_uses: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for _, value in queue:
        target_ref = f"{value['definition_id']}@{value['version']}"
        for source in value["source_refs"]:
            if source["admission_posture"] == "candidate-unadmitted":
                source_uses[(source["source_ref"], source["selector"], source["content_sha256"])].add(target_ref)

    admissions = []
    source_failures = []
    source_file_sha = sha(SOURCE_DEFINITIONS)
    for index, ((source_ref, selector, expected), targets) in enumerate(sorted(source_uses.items()), 1):
        if source_ref.startswith("cyberalchemy-v2:"):
            selected, start, end = markdown_h2_section(SOURCE_DEFINITIONS, selector)
            actual = hashlib.sha256(selected).hexdigest()
            source_path = "authority/definitions/DEFINITIONS.md"
            repository_id = "cyberalchemy-v2"
            file_digest = source_file_sha
            source_state = "current-source"
            if actual != expected:
                historical = historical_v2_selection(selector, expected)
                if historical is not None:
                    historical_path, selected, start, end = historical
                    actual = hashlib.sha256(selected).hexdigest()
                    source_path = str(historical_path.relative_to(LAB))
                    repository_id = "cyberalchemy-v2-snapshot-in-lab"
                    file_digest = sha(historical_path)
                    source_state = "historical-snapshot"
        else:
            source_path_obj, _ = by_ref[source_ref]
            selected = source_path_obj.read_bytes()
            actual = hashlib.sha256(selected).hexdigest()
            start = end = None
            source_path = str(source_path_obj.relative_to(LAB))
            repository_id = "cyberalchemy-lab"
            file_digest = actual
            source_state = "concurrent-definition-predecessor"
        if actual != expected:
            source_failures.append({"source_ref": source_ref, "selector": selector, "expected": expected, "actual": actual})
        admissions.append({
            "admission_id": f"CAL-SOURCE-FULL-DEFINITION-QUEUE-{index:03d}",
            "status": "admitted-for-definition-use",
            "decision_ref": DECISION_ID,
            "repository_id": repository_id,
            "source_state": source_state,
            "source_ref": source_ref,
            "source_path": source_path,
            "source_file_sha256_at_admission": file_digest,
            "selector": selector,
            "start_line": start,
            "end_line": end,
            "selected_sha256": expected,
            "target_definition_refs": sorted(targets),
        })
    check("all-pending-source-selections-current", len(admissions) == 58 and not source_failures, {"selections": len(admissions), "failures": source_failures, "source_file_sha256": source_file_sha})

    source_record = {
        "schema_version": "cyberalchemy-lab-source-admissions/v1",
        "record_id": "CAL-SOURCE-ADMISSIONS-FULL-DEFINITION-QUEUE-V1",
        "status": "owner-admitted",
        "authority_effect": "exact-source-selection-admission-for-definition-use",
        "owner_principal_ref": "person:<vrondelli>",
        "admission_decision_ref": DECISION_ID,
        "admissions": admissions,
        "source_direction": {"canonical": "admissions.json", "human_projection": "SOURCE-ADMISSIONS.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.full-definition-queue-admission/v1"},
        "claim_ceiling": "These exact source selections are admitted only as provenance for the 85 Definition versions named by CAL-DECISION-0053. They do not admit carriers, activate consumers, or grant migration, publication, release, or deployment authority.",
    }
    source_json = postimage(str(SOURCE_ADMISSION_ROOT / "admissions.json"))
    source_md = postimage(str(SOURCE_ADMISSION_ROOT / "SOURCE-ADMISSIONS.md"))
    source_receipt = postimage(str(SOURCE_ADMISSION_ROOT / "receipts/validation.json"))
    dump(source_json, source_record)
    write(source_md, render_source_admissions(source_record))
    source_validation = {
        "schema_version": "cyberalchemy-lab-source-admission-validation/v1",
        "subject": source_record["record_id"],
        "result": "PASS" if not source_failures and len(admissions) == 58 else "BLOCK",
        "authority_effect": "evidence-only",
        "checks": [
            {"check_id": "exact-selection-count", "result": "PASS" if len(admissions) == 58 else "BLOCK", "detail": len(admissions)},
            {"check_id": "selected-bytes-current", "result": "PASS" if not source_failures else "BLOCK", "detail": source_failures},
        ],
        "summary": {"source_selections": len(admissions), "v2_sections": sum(item["repository_id"].startswith("cyberalchemy-v2") for item in admissions), "current_v2_sections": sum(item["source_state"] == "current-source" for item in admissions), "historical_v2_snapshots": sum(item["source_state"] == "historical-snapshot" for item in admissions), "definition_predecessors": sum(item["repository_id"] == "cyberalchemy-lab" for item in admissions)},
        "claim_ceiling": "PASS proves the exact selected bytes used by this Definition admission transaction. It does not validate or activate downstream consumers.",
    }
    dump(source_receipt, source_validation)

    registry = deepcopy(live)
    selected_definitions = []
    for path, value in queue:
        relative = str(path.relative_to(LAB))
        ref = f"{value['definition_id']}@{value['version']}"
        registry["entries"].append({
            "admission_decision_ref": DECISION_ID,
            "definition_id": value["definition_id"],
            "lifecycle_state": "admitted",
            "path": relative,
            "sha256": sha(path),
            "term": value["term"],
            "version": value["version"],
        })
        selected_definitions.append({"definition_ref": ref, "path": relative, "sha256": sha(path), "term": value["term"], "origin": "reconstructed-migration" if relative.startswith("evidence/") else "authority-candidate"})
    registry["entries"].sort(key=lambda item: (item["definition_id"], version_key(item["version"])))
    for definition_id, values in identities.items():
        chosen = max((value for _, value in values), key=lambda value: version_key(value["version"]))
        registry["current_lookup"][definition_id] = f"{definition_id}@{chosen['version']}"
    registry["current_lookup"] = dict(sorted(registry["current_lookup"].items()))
    registry["status"] = "owner-admitted"
    registry["authority_effect"] = "one-hundred-eighteen-exact-definition-versions-canonical"
    registry["admission_decision_ref"] = DECISION_ID
    registry["predecessor"] = {"path": "authority/definitions/registry.json", "sha256": sha(live_registry_path), "entry_count": len(live["entries"]), "current_count": len(live["current_lookup"]), "admission_decision_ref": live["admission_decision_ref"]}
    registry["source_direction"] = {"canonical": "registry.json", "human_projection": "DEFINITIONS-INDEX.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.full-definition-queue-admission/v1"}
    registry["claim_ceiling"] = "This registry admits the complete 85-version pending Definition queue, including 70 reconstructed migration versions, through CAL-DECISION-0053 while preserving all 33 predecessor versions. It does not admit carriers, activate consumers, or promote the unresolved generic ledger primitive."
    registry_path = postimage("authority/definitions/registry.json")
    index_path = postimage("authority/definitions/DEFINITIONS-INDEX.md")
    dump(registry_path, registry)
    write(index_path, render_index(registry))
    promoted = [item for item in registry["entries"] if item.get("admission_decision_ref") == DECISION_ID]
    check("registry-closure", len(registry["entries"]) == 118 and len(registry["current_lookup"]) == 112 and len(promoted) == 85, {"versions": len(registry["entries"]), "current": len(registry["current_lookup"]), "promoted": len(promoted)})
    check("successors-selected-current", all(registry["current_lookup"][key].endswith("@1.0.0-candidate.2") for key in duplicate_identities), {key: registry["current_lookup"][key] for key in duplicate_identities})

    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1",
        "record_id": "CAL-DEFINITION-DRIFT-AUDIT-FULL-QUEUE-V1",
        "artifact_type_ref": "cal.artifact-type.drift-audit/v1",
        "status": "current-evidence",
        "authority_effect": "definition-drift-evidence-only",
        "owner_ref": "role:evidence-conformance-owner",
        "registry_ref": "authority/definitions/registry.json",
        "registry_sha256": sha(registry_path),
        "admission_decision_ref": DECISION_ID,
        "findings": [
            {"finding_id": "FULLQ-POST-001", "severity": "resolved", "status": "admitted", "target": "definition-queue:85-versions", "condition": "All 85 Definition versions that were pending in the authority and migration candidate trees are admitted by one exact decision overlay.", "remediation": "Use the live registry and current lookup for canonical resolution."},
            {"finding_id": "FULLQ-POST-002", "severity": "resolved", "status": "admitted", "target": "migration-reconstruction:70-versions", "condition": "All 70 reconstructed CyberAlchemy v2 Definition versions are admitted with their exact projections and source selectors preserved.", "remediation": "Retain the reconstruction evidence and source-admission overlay with the admitted registry."},
            {"finding_id": "FULLQ-POST-003", "severity": "resolved", "status": "successor-selected", "target": "artifact-surface-foundation:four-identities", "condition": "Four identities retain candidate.1 as admitted history and select their corrected candidate.2 versions as current.", "remediation": "Resolve these identities through current_lookup unless an exact historical version is required."},
            {"finding_id": "FULLQ-POST-004", "severity": "resolved", "status": "dependency-satisfied", "target": "DS-D1.9@1.0.0-candidate.1", "condition": "The formerly open Workflow dependency for the single-checkpoint definitions is satisfied by the already admitted Craft/DomainSpec Workflow definition.", "remediation": "Keep the Workflow definition current or re-evaluate dependent definitions when it is superseded."},
            {"finding_id": "FULLQ-POST-005", "severity": "definition-boundary", "status": "deferred", "target": "generic-ledger-primitive", "condition": "Append-Only Event Ledger is admitted as a specific pattern; the broader generic ledger primitive remains intentionally unresolved and has no queued Definition artifact.", "remediation": "Use the admitted append-only pattern where it applies; create and review a separate generic-ledger Definition only if a real cross-domain need emerges."},
            {"finding_id": "FULLQ-POST-006", "severity": "consumer-residue", "status": "open", "target": "definition-consumers", "condition": "Definition admission does not admit proposed carriers or activate Artifact Types, profiles, relation kinds, derived surfaces, migrations, or runtimes.", "remediation": "Validate and authorize each downstream consumer through its own authority route."},
            {"finding_id": "FULLQ-POST-007", "severity": "source-history", "status": "historical-snapshot-bound", "target": "cyberalchemy-v2:CAV2-D53", "condition": "The reconstructed Axiom Definition binds the exact D53 bytes preserved in migration execution 0044. The current v2 D53 section has evolved, so this admitted candidate is historical reconstruction rather than a projection of the latest v2 text.", "remediation": "Author a successor Axiom Definition if the current v2 D53 semantics should replace the admitted reconstructed version."},
        ],
        "summary": {"definition_versions": 118, "current_definition_terms": 112, "new_definition_versions_admitted": 85, "new_definition_identities": 81, "reconstructed_versions_admitted": 70, "authority_candidate_versions_admitted": 15, "source_selections_admitted_for_use": 58, "historical_source_snapshot_selections": 1, "remaining_unadmitted_definition_versions_in_indexed_queue": 0, "undefined_critical_terms_in_admitted_queue": 0, "conflicting_consumers": 0, "generic_ledger_primitive": "deferred-outside-queue", "consumer_activation": "not-applied"},
        "source_direction": {"canonical": "drift-audit.json", "human_projection": "DEFINITION-DRIFT-AUDIT.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.full-definition-queue-admission/v1"},
        "claim_ceiling": "This audit establishes Definition registry closure for the indexed 85-version queue and records remaining semantic boundaries. It does not establish carrier conformance, consumer activation, migration execution, publication, release, or deployment.",
    }
    drift_path = postimage("authority/definitions/drift-audit.json")
    drift_view_path = postimage("authority/definitions/DEFINITION-DRIFT-AUDIT.md")
    dump(drift_path, drift)
    write(drift_view_path, render_drift(drift))

    candidate_inputs = [binding(path) for path in PACKAGE_INPUTS]
    candidate_inputs.extend(definition_inputs)
    candidate_inputs.extend([binding("authority/artifact-types/definition/v1/schema.json"), binding("authority/artifact-types/definition/v1/generator.py")])
    unique_inputs = {item["path"]: item for item in candidate_inputs}
    candidate_inputs = [unique_inputs[key] for key in sorted(unique_inputs)]
    live_preimages = [binding(path) for path in ["authority/definitions/registry.json", "authority/definitions/DEFINITIONS-INDEX.md", "authority/definitions/drift-audit.json", "authority/definitions/DEFINITION-DRIFT-AUDIT.md"]]
    absent_preimages = [str(SOURCE_ADMISSION_ROOT / "admissions.json"), str(SOURCE_ADMISSION_ROOT / "SOURCE-ADMISSIONS.md"), str(SOURCE_ADMISSION_ROOT / "receipts/validation.json")]
    check("source-admission-targets-absent", all(not (LAB / path).exists() for path in absent_preimages), absent_preimages)

    postimage_paths = [
        str(SOURCE_ADMISSION_ROOT / "admissions.json"),
        str(SOURCE_ADMISSION_ROOT / "SOURCE-ADMISSIONS.md"),
        str(SOURCE_ADMISSION_ROOT / "receipts/validation.json"),
        "authority/definitions/registry.json",
        "authority/definitions/DEFINITIONS-INDEX.md",
        "authority/definitions/drift-audit.json",
        "authority/definitions/DEFINITION-DRIFT-AUDIT.md",
    ]
    bundle = {
        "schema_version": "cyberalchemy-lab-definition-admission-bundle/v1",
        "bundle_id": "CAL-FULL-DEFINITION-QUEUE-V1-ADMISSION-BUNDLE",
        "status": "candidate-ready-for-bound-decision",
        "authority_effect": "none-until-applied",
        "prospective_decision_id": DECISION_ID,
        "decision_boundary": {
            "mode": "single-checkpoint",
            "principal_ref": "person:<vrondelli>",
            "selection_source": "explicit-user-command",
            "verbatim_sequence": ["we need to admiddit and add this", "we need the full queue", "and reconstructed"],
            "resolution_basis": "The user expanded the admission request to the complete pending Definition queue and explicitly included reconstructed definitions.",
        },
        "counts": {"definition_versions": 85, "definition_identities": 81, "authority_candidate_versions": 15, "reconstructed_versions": 70, "source_selections": 58, "historical_snapshot_selections": 1, "successor_pairs": 4},
        "definition_selection": sorted(selected_definitions, key=lambda item: (item["definition_ref"], item["path"])),
        "candidate_inputs": candidate_inputs,
        "live_preimages": live_preimages,
        "absent_preimages": absent_preimages,
        "postimage_targets": postimage_paths,
        "decision_requests": [
            {"request_id": "FULLQ-SOURCE-ADMISSION", "owner_role": "source-admission-owner", "requested_effect": "Admit 58 exact source selections for the selected Definition versions."},
            {"request_id": "FULLQ-DEFINITION-ADMISSION", "owner_role": "definition-owner", "requested_effect": "Admit 85 exact Definition versions and select current versions for 81 identities."},
        ],
        "rollback_policy": "Restore the four bound live preimages and remove the three newly created source-admission files if any write or post-write verification fails.",
        "excluded_effects": [
            "No Artifact Type, profile, relation kind, derived surface, carrier, migration consumer, or runtime is admitted or activated.",
            "The unresolved generic ledger primitive is not created or promoted.",
            "No commit, push, publication, release, or deployment is authorized.",
        ],
        "claim_ceiling": "This bundle binds the complete 85-version indexed Definition queue, including 70 reconstructed versions, 58 exact source selections, and seven authority postimages. It has no authority effect until the exact transaction is applied.",
    }
    dump(HERE / "bundle.json", bundle)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    manifest = {
        "schema_version": "cyberalchemy-lab-definition-admission-manifest/v1",
        "manifest_id": "CAL-FULL-DEFINITION-QUEUE-V1-ADMISSION-MANIFEST",
        "status": "candidate-ready-for-bound-decision" if not blocked else "blocked",
        "authority_effect": "none",
        "bundle": {"path": str((HERE / "bundle.json").relative_to(LAB)), "sha256": sha(HERE / "bundle.json")},
        "builder": {"path": str((HERE / "build.py").relative_to(LAB)), "sha256": sha(HERE / "build.py")},
        "prospective_decision_id": DECISION_ID,
        "decision_boundary": bundle["decision_boundary"],
        "decision_requests": bundle["decision_requests"],
        "counts": bundle["counts"],
        "definition_selection": bundle["definition_selection"],
        "candidate_inputs": candidate_inputs,
        "live_preimages": live_preimages,
        "absent_preimages": absent_preimages,
        "postimages": [{"path": f"postimages/{path}", "target_path": path, "sha256": sha(postimage(path))} for path in postimage_paths],
        "rollback_policy": bundle["rollback_policy"],
        "excluded_effects": bundle["excluded_effects"],
        "claim_ceiling": "This immutable manifest binds the full Definition queue transaction. It does not itself admit, activate, publish, release, or deploy anything.",
    }
    dump(HERE / "manifest.json", manifest)
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-admission-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "promotion_eligibility": "selected-by-explicit-user-instruction" if not blocked else "blocked",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"bundle_sha256": sha(HERE / "bundle.json"), "manifest_sha256": sha(HERE / "manifest.json"), "source_admissions_sha256": sha(source_json), "registry_postimage_sha256": sha(registry_path), "drift_postimage_sha256": sha(drift_path)},
        "claim_ceiling": "PASS proves exact current candidate bytes, Definition structure and projections, selected source bytes, dependency resolution, and deterministic postimages. It does not itself apply the authority transaction.",
    }
    dump(HERE / "receipts/validation.json", receipt)
    write(HERE / "BUNDLE.md", render_bundle(bundle, receipt))

    authorization = {
        "schema_version": "cyberalchemy-lab-definition-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-FULL-DEFINITION-QUEUE-V1",
        "prospective_decision_id": DECISION_ID,
        "status": "authorized" if not blocked else "blocked",
        "principal_id": "person:<vrondelli>",
        "selected_roles": ["source-admission-owner", "definition-owner"],
        "selection_source": bundle["decision_boundary"],
        "selection_token": "admit full queue including reconstructed definitions",
        "manifest": {"path": str((HERE / "manifest.json").relative_to(LAB)), "sha256": sha(HERE / "manifest.json")},
        "validation_receipt": {"path": str((HERE / "receipts/validation.json").relative_to(LAB)), "sha256": sha(HERE / "receipts/validation.json"), "required_result": "PASS"},
        "decision_separation": "This authorization admits exact source selections and Definition versions only; all downstream carrier and consumer effects remain separately governed.",
        "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "claim_ceiling": "Authorization is limited to the exact manifest and its seven postimages. It grants no commit, push, publication, release, deployment, migration execution, or consumer activation.",
    }
    decision_root = LAB / "docs/decisions/0053-full-definition-queue-admission"
    dump(decision_root / "authorization.json", authorization)
    write(decision_root / "AUTHORIZATION.md", "\n".join([
        "<!-- GENERATED FILE: authorization.json is canonical. -->", "", "# Full Definition Queue Admission Authorization", "",
        f"- Status: `{authorization['status']}`", f"- Principal: `{authorization['principal_id']}`", f"- Selection: `{authorization['selection_token']}`", "",
        "## Scope", "", bundle["decision_boundary"]["resolution_basis"], "", "## Separation", "", authorization["decision_separation"], "", "## Claim ceiling", "", authorization["claim_ceiling"],
    ]))
    print(f"FULL_DEFINITION_QUEUE_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"DEFINITIONS={len(queue)}")
    print(f"RECONSTRUCTED={reconstructed_count}")
    print(f"SOURCE_SELECTIONS={len(admissions)}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
