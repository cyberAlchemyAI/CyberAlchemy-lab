#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import followups


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
SOURCE = Path(
    os.environ.get("CAV2_SOURCE_ROOT", LAB.parent / "domainspec-core/cyberAlchemy-v2")
).resolve()
PREDECESSOR = ROOT.parent / "0002-admitted-foundation-alignment"

DEFINITIONS_PATH = SOURCE / "authority/definitions/DEFINITIONS.md"
NORMALIZATION_PATH = LAB / "docs/normalizations/0001-definition-migration-model/normalization.json"
NORMALIZATION_DECISION_PATH = LAB / "docs/decisions/0012-normalize-01-defaults/decision.json"
LAB_DEFINITION_REGISTRY_PATH = LAB / "authority/definitions/registry.json"
LAB_ARTIFACT_TYPE_REGISTRY_PATH = (
    LAB / "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"
)
DEFINE_PROFILE_PATH = SOURCE / "define/profile.json"
DEFINE_DEFINITIONS_PATH = SOURCE / "define/definitions.json"
DEFINE_HANDLED_PATH = SOURCE / "define/handled-definitions.json"
DEFINE_SCHEMA_PATH = SOURCE / "define/schemas/define-package.schema.json"

NORMALIZATION_SOURCE_COMMIT = "eabbbdf1b9df4a4f984a476dfc49a930f4ccbc06"
NORMALIZATION_SOURCE_SHA256 = "68d40e441ff53e16a0222aca3628c3e9d2c932933e89222292ea5c27b6555a2b"
EXPECTED_CHANGED_DEFINITION_IDS = ["CAV2-D65"]

CATALOGS = [
    ("semantic", "semantic_concepts", "concept_id", "term"),
    ("artifact-type", "artifact_types", "artifact_type_id", "name"),
    ("profile", "profiles", "profile_id", "name"),
    ("relation-kind", "relation_kinds", "relation_kind_id", "relation_kind_id"),
    ("derived-surface", "derived_surfaces", "derived_surface_id", "name"),
]


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def git_blob(commit: str, source_relative_path: str) -> bytes:
    repository = SOURCE.parent
    repository_path = f"cyberAlchemy-v2/{source_relative_path}"
    return subprocess.run(
        ["git", "show", f"{commit}:{repository_path}"],
        cwd=repository,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def extract_definitions(text: str) -> list[dict]:
    matches = list(re.finditer(r"(?m)^## CAV2-D(\d+): (.+)$", text))
    records = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else text.find(
            "\n## Withdrawn Definition IDs", match.end()
        )
        if end < 0:
            end = len(text)
        section = text[match.start():end].rstrip() + "\n"
        records.append(
            {
                "definition_id": f"CAV2-D{int(match.group(1))}",
                "number": int(match.group(1)),
                "term": match.group(2).strip(),
                "heading": match.group(0),
                "start_line": text.count("\n", 0, match.start()) + 1,
                "raw_section_sha256": digest_bytes(section.encode("utf-8")),
            }
        )
    return records


def current_lab_definitions() -> tuple[dict[str, list[dict]], list[dict]]:
    registry = load(LAB_DEFINITION_REGISTRY_PATH)
    by_term: dict[str, list[dict]] = defaultdict(list)
    current_entries = []
    for entry in registry["entries"]:
        exact_ref = f'{entry["definition_id"]}@{entry["version"]}'
        if registry["current_lookup"].get(entry["definition_id"]) != exact_ref:
            continue
        artifact_path = LAB / entry["path"]
        current = {
            "definition_ref": exact_ref,
            "definition_id": entry["definition_id"],
            "term": entry["term"],
            "path": entry["path"],
            "sha256": entry["sha256"],
            "actual_sha256": digest_path(artifact_path),
            "lifecycle_state": entry["lifecycle_state"],
            "admission_decision_ref": entry["admission_decision_ref"],
        }
        current_entries.append(current)
        by_term[entry["term"].casefold()].append(current)
    return by_term, current_entries


def current_lab_artifact_types() -> tuple[dict[str, list[dict]], list[dict]]:
    registry = load(LAB_ARTIFACT_TYPE_REGISTRY_PATH)
    by_semantic_kind: dict[str, list[dict]] = defaultdict(list)
    entries = []
    for entry in registry["entries"]:
        if entry["lifecycle_state"] != "admitted-current":
            continue
        artifact_path = LAB / entry["artifact_path"]
        current = {
            "artifact_type_ref": entry["artifact_type_ref"],
            "semantic_kind": entry["semantic_kind"],
            "path": entry["artifact_path"],
            "sha256": entry["artifact_sha256"],
            "actual_sha256": digest_path(artifact_path),
            "lifecycle_state": entry["lifecycle_state"],
            "admission_decision_ref": entry["admission_decision_ref"],
            "registry_posture": "decision-admitted-entry-in-unadmitted-successor-postimage",
        }
        entries.append(current)
        by_semantic_kind[entry["semantic_kind"]].append(current)
    return by_semantic_kind, entries


def iter_declared_strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_declared_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_declared_strings(child)
    elif isinstance(value, str):
        yield value


def resolve_declared_file(profile_path: Path, value: str) -> Path | None:
    clean = value.split("#", 1)[0]
    if not clean or not re.search(r"\.(?:json|jsonl|md|py|mjs)$", clean, re.IGNORECASE):
        return None
    if clean.startswith("cyberAlchemy-v2/"):
        candidate = SOURCE / clean.removeprefix("cyberAlchemy-v2/")
    else:
        candidate = profile_path.parent / clean
        if not candidate.exists():
            candidate = SOURCE / clean
    try:
        candidate.resolve().relative_to(SOURCE)
    except (ValueError, OSError):
        return None
    return candidate.resolve() if candidate.is_file() else None


def ontology_materials(profile_path: Path, profile: dict) -> list[Path]:
    materials = {profile_path.resolve()}
    for candidate in profile_path.parent.iterdir():
        if candidate.is_file() and candidate.suffix.casefold() in {
            ".json", ".jsonl", ".md", ".py", ".mjs"
        }:
            materials.add(candidate.resolve())
    for value in iter_declared_strings(profile):
        resolved = resolve_declared_file(profile_path, value)
        if resolved:
            materials.add(resolved)
    receipt_glob = profile.get("inventory_contract", {}).get("receipt_glob")
    if receipt_glob:
        materials.update(
            path.resolve() for path in profile_path.parent.glob(receipt_glob) if path.is_file()
        )
    return sorted(materials)


def count_named_lists(value, counts: Counter) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in {
                "nodes", "relations", "sources", "definitions", "views"
            } and isinstance(child, list):
                counts[key.casefold()] += len(child)
            count_named_lists(child, counts)
    elif isinstance(value, list):
        for child in value:
            count_named_lists(child, counts)


def build_ontology_inventory() -> dict:
    profiles = sorted((SOURCE / "ontology").rglob("profile.json"))
    profiles.extend(
        [
            SOURCE / "define/profile.json",
            SOURCE / "define/business-ontology/PROFILE.json",
            SOURCE / "define/system-ontology/PROFILE.json",
        ]
    )
    seen = set()
    packages = []
    for profile_path in profiles:
        profile_path = profile_path.resolve()
        if profile_path in seen:
            continue
        seen.add(profile_path)
        profile = load(profile_path)
        materials = ontology_materials(profile_path, profile)
        selectors = set()
        counts: Counter = Counter()
        material_records = []
        for path in materials:
            data = path.read_bytes()
            text = data.decode("utf-8", errors="replace")
            selectors.update(re.findall(r"CAV2-D\d+", text))
            if path.suffix.casefold() == ".json":
                try:
                    count_named_lists(json.loads(text), counts)
                except json.JSONDecodeError:
                    pass
            material_records.append({"path": rel(path, SOURCE), "sha256": digest_bytes(data)})
        profile_ref = rel(profile_path, SOURCE)
        is_domainspec = profile_ref.startswith("ontology/domainspec-v2/")
        packages.append(
            {
                "ontology_id": profile.get("ontology_id") or profile.get("package_id") or profile_ref,
                "profile_path": profile_ref,
                "ontology_type": profile.get("ontology_type")
                or (
                    "business-system-bridge"
                    if profile.get("business_ontology_ref")
                    and profile.get("system_ontology_ref")
                    else "unspecified-in-source-profile"
                ),
                "ontology_type_source": "source-profile"
                if profile.get("ontology_type")
                else (
                    "candidate-inference-from-explicit-business-and-system-refs"
                    if profile.get("business_ontology_ref")
                    and profile.get("system_ontology_ref")
                    else "not-selected"
                ),
                "branch": profile.get("branch", "none"),
                "owner_route": profile.get("owner_route")
                or profile.get("package_owner")
                or "unresolved",
                "visibility": profile.get("visibility", "private"),
                "source_status": profile.get("status")
                or profile.get("candidate_status")
                or profile.get("current_lifecycle_state")
                or "unspecified",
                "authority_effect": profile.get("authority_effect", "none"),
                "counts": {
                    key: counts.get(key, 0)
                    for key in ("nodes", "relations", "sources", "definitions", "views")
                },
                "definition_selectors": sorted(
                    selectors, key=lambda item: int(item.split("D")[1])
                ),
                "materials": material_records,
                "review_posture": "route-to-craft-lineage-review"
                if is_domainspec
                else "semantic-package-review",
                "copy_posture": "reference-only-do-not-copy",
            }
        )

    groups: dict[str, list[dict]] = defaultdict(list)
    for package in packages:
        group_id = (
            "domainspec-v2-lineage"
            if package["profile_path"].startswith("ontology/domainspec-v2/")
            else package["ontology_id"]
        )
        groups[group_id].append(package)
    review_groups = []
    for group_id, members in groups.items():
        canonical = [
            item["profile_path"] for item in members if item["source_status"] == "canonical"
        ]
        group = {
            "group_id": group_id,
            "profile_paths": [item["profile_path"] for item in members],
            "ontology_ids": sorted({item["ontology_id"] for item in members}),
            "canonical_profile_paths": canonical,
            "lineage_conflict": len(canonical) > 1,
            "review_posture": "resolve-current-lineage-before-reconstruction"
            if len(members) > 1
            else "review-semantic-package",
        }
        if group_id == "domainspec-v2-lineage":
            group["successor_route"] = {
                "product_id": "craft",
                "target_surface": "craft/",
                "legacy_identity_posture": "preserve-domainspec-identifiers-as-lineage-aliases",
                "decision_ref": "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS#NORM-OQ-5",
            }
        review_groups.append(group)
    review_groups.sort(
        key=lambda item: (item["group_id"] != "cav2.define", item["group_id"])
    )
    return {
        "schema_version": "cyberalchemy-lab-source-ontology-inventory/v2",
        "inventory_id": "CAL-CAV2-ONTOLOGY-REVIEW-INVENTORY-0002",
        "source_repository_id": "cyberalchemy-v2-source",
        "package_count": len(packages),
        "packages": packages,
        "review_group_count": len(review_groups),
        "review_groups": review_groups,
        "sequencing_rule": "source-ontology-review-may-follow-target-prototype-authorship;ontology-reconstruction-remains-after-target-realization-closure",
        "authority_effect": "none",
        "copy_posture": "reference-only-do-not-copy",
    }


def source_binding(repository_id: str, path: Path, repository_root: Path) -> dict:
    return {
        "kind": "file",
        "repository_id": repository_id,
        "path": rel(path, repository_root),
        "sha256": digest_path(path),
    }


def render_candidate(candidate: dict) -> str:
    counts = candidate["target_counts"]
    return f'''<!-- GENERATED FILE: canonical data is candidate.json. -->

# Normalized-Target CyberAlchemy-v2 Reconstruction

- Candidate: `{candidate["candidate_id"]}`
- Status: `{candidate["status"]}`
- Strategy: `{candidate["strategy"]}`
- Authority effect: `{candidate["authority_effect"]}`

## Preserved decision baseline

`CAL-NORMALIZE-01` and `CAL-DECISION-0012-NORMALIZE-01-DEFAULTS` remain the selected planning baseline. The candidate does not reopen D1-D69. Sixty-eight source definitions are unchanged; D65 alone has later source drift.

## Realization scope

The ledger covers `{counts["total"]}` normalized targets: `{counts["semantic"]}` semantic concepts, `{counts["artifact-type"]}` artifact types, `{counts["profile"]}` profiles, `{counts["relation-kind"]}` relation kinds, and `{counts["derived-surface"]}` derived surfaces.

## Current frontier

{candidate["product_construction"]["frontier"]}

The non-D65 prototype scaffolds and ontology routing reviews are authored. The D65-derived successor is proposed, and all three independent planning decisions now wait at the configured final workflow checkpoint.

## Approval boundary

One decision request is presented only after target realization and ontology review are complete. Independent decisions remain distinct inside that one request set.

## Claim ceiling

{candidate["claim_ceiling"]}
'''


def render_definition_inventory(inventory: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is definition-inventory.json. -->

# Accepted Definition Decision Inventory

- Accepted decisions: `{inventory["accepted_decision_count"]}`
- Unchanged after selection: `{inventory["drift"]["unchanged_count"]}`
- Changed after selection: `{", ".join(inventory["drift"]["changed_definition_ids"])}`
- Withdrawals preserved: `{len(inventory["withdrawn_definitions"])}`

The D1-D69 dispositions remain selected planning decisions. Only D65 requires successor normalization because its source section changed after that selection.
'''


def render_realization_ledger(ledger: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is realization-ledger.json. -->",
        "",
        "# Normalized Target Realization Ledger",
        "",
        f'- Targets: `{ledger["target_count"]}`',
        f'- Realized through exact admitted current evidence: `{ledger["state_counts"].get("realized-admitted-current", 0)}`',
        f'- Unresolved: `{ledger["state_counts"].get("unresolved-no-canonical-match", 0)}`',
        f'- Blocked by D65 source drift: `{ledger["state_counts"].get("blocked-source-drift", 0)}`',
        "",
        "| Target | Family | State | Define disposition | Evidence |",
        "|---|---|---|---|---:|",
    ]
    for target in ledger["targets"]:
        lines.append(
            f'| `{target["target_id"]}` | `{target["family"]}` | '
            f'`{target["realization_state"]}` | `{target["define_disposition"]}` | '
            f'{len(target["realization_refs"])} |'
        )
    lines.append("")
    return "\n".join(lines)


def render_definition_pack(pack: dict) -> str:
    counts = Counter(item["current_disposition"] for item in pack["concepts"])
    lines = [
        "<!-- GENERATED FILE: canonical data is definition-pack.json. -->",
        "",
        "# Define Migration Definition Pack",
        "",
        f'- Pack: `{pack["pack_id"]}`',
        f'- Required targets: `{len(pack["required_concept_ids"])}`',
        f'- Reuse: `{counts.get("reuse", 0)}`',
        f'- Propose: `{counts.get("propose", 0)}`',
        f'- Open: `{counts.get("open", 0)}`',
        "",
        "The Define disposition is independent from the accepted migration disposition. This pack is a migration-local projection of the CAV2 Define method and is not inserted into its handled-definition registry.",
        "",
        "## Open questions",
        "",
    ]
    for question in pack["open_questions"]:
        lines.append(f'- `{question["question_id"]}` — {question["question"]}')
    lines.append("")
    return "\n".join(lines)


def render_ontology_inventory(inventory: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is ontology-inventory.json. -->",
        "",
        "# Ontology Review Inventory",
        "",
        f'- Packages: `{inventory["package_count"]}`',
        f'- Review groups: `{inventory["review_group_count"]}`',
        f'- Sequencing: `{inventory["sequencing_rule"]}`',
        "",
        "| Group | Members | Posture | Successor |",
        "|---|---:|---|---|",
    ]
    for group in inventory["review_groups"]:
        successor = group.get("successor_route", {}).get("product_id", "—")
        lines.append(
            f'| `{group["group_id"]}` | {len(group["profile_paths"])} | '
            f'`{group["review_posture"]}` | `{successor}` |'
        )
    lines.append("")
    return "\n".join(lines)


def render_queue(queue: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is review-queue.json. -->",
        "",
        "# Normalized Target Realization Queue",
        "",
        f'- Ready realization units: `{queue["ready_count"]}`',
        f'- D65-blocked realization units: `{queue["blocked_count"]}`',
        f'- Authored prototype scaffolds: `{queue.get("authored_count", 0)}`',
        f'- Authored ontology reviews: `{queue.get("authored_ontology_review_count", 0)}`',
        "",
        "Settled D1-D69 decisions are not review units. Prototype authorship does not imply realization or admission; the queue records what was authored for the single final planning checkpoint.",
        "",
        "| Seq | Target | Family | Status |",
        "|---:|---|---|---|",
    ]
    for unit in queue["realization_units"]:
        lines.append(
            f'| {unit["sequence"]} | `{unit["target_id"]}` | '
            f'`{unit["family"]}` | `{unit["status"]}` |'
        )
    lines.append("")
    return "\n".join(lines)


def render_review(review: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is review.json. -->

# Review 0001: CAV2-D65 Source Drift

- Status: `{review["status"]}`
- Baseline section SHA-256: `{review["baseline_source_ref"]["raw_section_sha256"]}`
- Current section SHA-256: `{review["current_source_ref"]["raw_section_sha256"]}`

## Finding

The selected D65 split predates the prototype-first revision. Its six target relations cannot be assumed current. The other 68 D1-D69 decisions remain preserved because their source sections did not change.

## Required successor decision

{review["open_question"]}

No outcome is selected here. The answer is accumulated with the completed migration-chain approval request.
'''


def render_manifest(manifest: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is manifest.json. -->

# Candidate Manifest

- Manifest: `{manifest["manifest_id"]}`
- Candidate materials: `{len(manifest["materials"])}`
- Exact source bindings: `{len(manifest["source_bindings"])}`
- Authority effect: `{manifest["authority_effect"]}`

All paths are repository-relative and paired with an explicit repository identity.
'''


def main() -> None:
    normalization = load(NORMALIZATION_PATH)
    decision = load(NORMALIZATION_DECISION_PATH)
    current_text = DEFINITIONS_PATH.read_text(encoding="utf-8")
    baseline_bytes = git_blob(
        NORMALIZATION_SOURCE_COMMIT, "authority/definitions/DEFINITIONS.md"
    )
    baseline_definitions = {
        item["definition_id"]: item
        for item in extract_definitions(baseline_bytes.decode("utf-8"))
    }
    current_definitions = {
        item["definition_id"]: item for item in extract_definitions(current_text)
    }
    expected_ids = {f"CAV2-D{i}" for i in range(1, 70)}
    if set(current_definitions) != expected_ids or set(baseline_definitions) != expected_ids:
        raise SystemExit("Expected active CAV2-D1 through CAV2-D69")
    changed_ids = sorted(
        definition_id
        for definition_id in current_definitions
        if current_definitions[definition_id]["raw_section_sha256"]
        != baseline_definitions[definition_id]["raw_section_sha256"]
    )

    decisions_by_source = {
        item["legacy_id"]: item for item in normalization["migration_decisions"]
    }
    sources_by_target: dict[str, list[dict]] = defaultdict(list)
    for item in normalization["migration_decisions"]:
        for target in item["targets"]:
            sources_by_target[target].append(
                {
                    "legacy_id": item["legacy_id"],
                    "legacy_term": item["legacy_term"],
                    "decision": item["decision"],
                }
            )

    definition_inventory = {
        "schema_version": "cyberalchemy-lab-accepted-definition-decision-inventory/v2",
        "inventory_id": "CAL-CAV2-DEFINITION-DECISION-INVENTORY-0002",
        "normalization_binding": {
            "normalization_id": normalization["normalization_id"],
            "path": rel(NORMALIZATION_PATH, LAB),
            "sha256": digest_path(NORMALIZATION_PATH),
            "decision_posture": normalization["decision_posture"],
        },
        "owner_decision_binding": {
            "decision_id": decision["decision_id"],
            "path": rel(NORMALIZATION_DECISION_PATH, LAB),
            "sha256": digest_path(NORMALIZATION_DECISION_PATH),
            "selected_option": decision["selection"]["option_id"],
            "accepted_normalization_sha256": decision["accepted_candidate"]["sha256"],
            "authority_effect": decision["authority_effect"],
        },
        "source_baseline": {
            "repository_id": "domainspec-core",
            "git_commit": NORMALIZATION_SOURCE_COMMIT,
            "path": "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
            "sha256": digest_bytes(baseline_bytes),
        },
        "source_current": {
            "repository_id": "cyberalchemy-v2-source",
            "path": "authority/definitions/DEFINITIONS.md",
            "sha256": digest_path(DEFINITIONS_PATH),
        },
        "accepted_decision_count": len(normalization["migration_decisions"]),
        "decisions": [
            {
                **item,
                "source_drift_state": "changed-after-selection"
                if item["legacy_id"] in changed_ids
                else "unchanged-after-selection",
                "realization_eligibility": "blocked-pending-successor-normalization"
                if item["legacy_id"] in changed_ids
                else "accepted-baseline-current",
            }
            for item in normalization["migration_decisions"]
        ],
        "drift": {
            "changed_definition_ids": changed_ids,
            "expected_changed_definition_ids": EXPECTED_CHANGED_DEFINITION_IDS,
            "changed_count": len(changed_ids),
            "unchanged_count": len(normalization["migration_decisions"]) - len(changed_ids),
            "scope_rule": "reconcile-changed-sections-only; do-not-reopen-unchanged-owner-selections",
        },
        "withdrawn_definitions": normalization["withdrawn_ids"],
        "authority_effect": "none",
    }

    definitions_by_term, _ = current_lab_definitions()
    artifact_types_by_kind, _ = current_lab_artifact_types()
    targets = []
    family_counts = Counter()
    for family, catalog_key, id_key, name_key in CATALOGS:
        for source_target in normalization[catalog_key]:
            target_id = source_target[id_key]
            term = source_target[name_key]
            family_counts[family] += 1
            source_decisions = sources_by_target.get(target_id, [])
            affected_by_d65 = any(
                item["legacy_id"] == "CAV2-D65" for item in source_decisions
            )
            realization_refs = []
            if family == "semantic":
                realization_refs = definitions_by_term.get(term.casefold(), [])
            elif family == "artifact-type":
                realization_refs = artifact_types_by_kind.get(
                    target_id.split(".", 1)[1], []
                )
            if affected_by_d65:
                state = "blocked-source-drift"
                define_disposition = "open"
                next_action = (
                    "select a successor D65 normalization at the final decision checkpoint"
                )
            elif realization_refs:
                state = "realized-admitted-current"
                define_disposition = "reuse"
                next_action = "verify exact consumer bindings and retain current admission"
            else:
                state = "unresolved-no-canonical-match"
                define_disposition = "propose"
                next_action = (
                    "author a machine-canonical Lab candidate from zero in its owning surface"
                )
            targets.append(
                {
                    "target_id": target_id,
                    "term": term,
                    "family": family,
                    "normalized_record": source_target,
                    "accepted_source_decisions": source_decisions,
                    "source_drift_state": "affected-by-CAV2-D65"
                    if affected_by_d65
                    else "current-or-supporting-target",
                    "realization_state": state,
                    "realization_refs": realization_refs,
                    "define_disposition": define_disposition,
                    "next_action": next_action,
                    "authority_effect": "none",
                }
            )

    state_counts = Counter(item["realization_state"] for item in targets)
    disposition_counts = Counter(item["define_disposition"] for item in targets)
    realization_ledger = {
        "schema_version": "cyberalchemy-lab-normalized-target-realization-ledger/v1",
        "ledger_id": "CAL-CAV2-NORMALIZED-TARGET-REALIZATION-0001",
        "normalization_ref": "CAL-NORMALIZE-01",
        "owner_decision_ref": "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS",
        "matching_policy": {
            "semantic": "case-insensitive exact term match against current owner-admitted Definition registry entries",
            "artifact_type": "exact normalized suffix match against decision-admitted current semantic_kind entries",
            "other": "no admission inferred from paths, labels, schemas, or consumer references",
            "claim_limit": "realized means exact current admission evidence was resolved; all other observations remain non-authoritative",
        },
        "target_count": len(targets),
        "family_counts": dict(family_counts),
        "state_counts": dict(state_counts),
        "define_disposition_counts": dict(disposition_counts),
        "targets": targets,
        "authority_effect": "none",
    }

    d65_target_ids = [
        item["target_id"]
        for item in targets
        if item["source_drift_state"] == "affected-by-CAV2-D65"
    ]
    definition_pack = {
        "schema_version": "cav2-define-definition-pack/v1-candidate",
        "pack_id": "DEFINE-PACK-CAL-CAV2-NORMALIZED-TARGET-REALIZATION-001",
        "status": "candidate",
        "define_method_binding": {
            "profile_ref": "cyberalchemy-v2-source:define/profile.json",
            "definitions_ref": "cyberalchemy-v2-source:define/definitions.json",
            "handled_registry_ref": "cyberalchemy-v2-source:define/handled-definitions.json",
            "application": "migration-local-target-disposition-projection",
            "registry_effect": "none; records are not inserted into the CAV2 Define registry",
            "disposition_axis": ["reuse", "specialize", "propose", "open"],
            "orthogonality_rule": "Define disposition does not replace revise, reclassify, split, collapse, or drop migration decisions.",
        },
        "goal": "Realize the accepted CAL-NORMALIZE-01 target model in CyberAlchemy-lab without reopening settled source-definition decisions.",
        "original_intent": "Review source semantics one-by-one, preserve orthogonality, author canonical machine artifacts from zero, and accumulate one approval request at the end.",
        "context": {
            "context_id": "CAL-CYBERALCHEMY-V2-TO-LAB-NORMALIZED-REALIZATION",
            "name": "CyberAlchemy-v2 to CyberAlchemy-lab normalized reconstruction",
            "statement": "Migration-local semantic handling for 195 accepted normalized targets and one bounded D65 drift.",
        },
        "consumer": {
            "consumer_id": "CAL-MIGRATION-REALIZATION-AUTHOR",
            "intended_use": "Input for authoring missing Lab candidates and later ontology review; no authority is conveyed.",
        },
        "required_concept_ids": [item["target_id"] for item in targets],
        "concepts": [
            {
                "concept_id": item["target_id"],
                "term": item["term"],
                "family": item["family"],
                "source_definition_refs": [
                    source["legacy_id"] for source in item["accepted_source_decisions"]
                ],
                "accepted_migration_dispositions": [
                    source["decision"] for source in item["accepted_source_decisions"]
                ],
                "current_disposition": item["define_disposition"],
                "realization_state": item["realization_state"],
                "realization_refs": item["realization_refs"],
                "next_action": item["next_action"],
            }
            for item in targets
        ],
        "open_questions": [
            {
                "question_id": "CAL-CAV2-D65-DRIFT-001",
                "question": "Which normalized targets succeed the selected D65 split after the prototype-first 2026-09-03 source revision?",
                "affected_target_ids": d65_target_ids,
                "decision_timing": "accumulate-until-end-of-complete-chain",
                "stop_scope": "D65-derived targets only",
            }
        ],
        "authority_effect": "none",
        "claim_ceiling": "This migration-local Definition Pack applies the CAV2 Define disposition method to normalized targets. It does not alter the CAV2 handled-definition registry, promote definitions, admit artifacts, approve the migration, or authorize implementation, publication, release, or deployment.",
    }

    ontology_inventory = build_ontology_inventory()
    unresolved = [
        item
        for item in targets
        if item["realization_state"] != "realized-admitted-current"
    ]
    realization_units = []
    for sequence, item in enumerate(unresolved, 1):
        status = (
            "blocked-by-D65-successor-normalization"
            if item["realization_state"] == "blocked-source-drift"
            else "ready-for-candidate-authorship"
        )
        realization_units.append(
            {
                "sequence": sequence,
                "unit_id": f"CAL-NORMALIZED-TARGET-REALIZATION-{sequence:04d}",
                "target_id": item["target_id"],
                "family": item["family"],
                "status": status,
                "define_disposition": item["define_disposition"],
                "next_action": item["next_action"],
            }
        )
    review_queue = {
        "schema_version": "cyberalchemy-lab-normalized-target-realization-queue/v2",
        "queue_id": "CAL-CAV2-NORMALIZED-REALIZATION-QUEUE-0002",
        "settled_definition_decisions": {
            "count": 68,
            "posture": "preserved-not-queued",
            "source_ref": "CAL-NORMALIZE-01",
        },
        "definition_drift_units": [
            {
                "unit_id": "CAL-CAV2-D65-DRIFT-REVIEW-0001",
                "source_definition_id": "CAV2-D65",
                "status": "open-accumulated-for-final-checkpoint",
                "affected_target_ids": d65_target_ids,
            }
        ],
        "realization_units": realization_units,
        "ready_count": sum(
            item["status"] == "ready-for-candidate-authorship"
            for item in realization_units
        ),
        "blocked_count": sum(
            item["status"].startswith("blocked") for item in realization_units
        ),
        "ontology_units": [
            {
                "sequence": len(realization_units) + sequence,
                "unit_id": f"CAL-CAV2-ONTOLOGY-REVIEW-{sequence:04d}",
                "group_id": group["group_id"],
                "profile_paths": group["profile_paths"],
                "status": "queued-after-normalized-target-realization",
                "review_posture": group["review_posture"],
                "successor_route": group.get("successor_route"),
            }
            for sequence, group in enumerate(ontology_inventory["review_groups"], 1)
        ],
        "decision_boundary": {
            "checkpoint": "end-of-complete-realization-and-ontology-review-chain",
            "approval_requests_before_checkpoint": 0,
            "final_request_shape": "one-request-set-with-distinct-decisions",
        },
        "withdrawal_preservation": {
            "records": normalization["withdrawn_ids"],
            "rule": "never-reuse",
        },
        "authority_effect": "none",
    }

    d65_baseline = baseline_definitions["CAV2-D65"]
    d65_current = current_definitions["CAV2-D65"]
    review = {
        "schema_version": "cyberalchemy-lab-definition-source-drift-review/v2",
        "review_id": "CAL-CAV2-D65-DRIFT-REVIEW-0001",
        "source_definition_id": "CAV2-D65",
        "status": "open-source-drift",
        "accepted_normalization_decision": decisions_by_source["CAV2-D65"],
        "baseline_source_ref": {
            "git_commit": NORMALIZATION_SOURCE_COMMIT,
            "heading": d65_baseline["heading"],
            "raw_section_sha256": d65_baseline["raw_section_sha256"],
        },
        "current_source_ref": {
            "path": "authority/definitions/DEFINITIONS.md",
            "heading": d65_current["heading"],
            "start_line": d65_current["start_line"],
            "raw_section_sha256": d65_current["raw_section_sha256"],
        },
        "finding": "the accepted D65 normalization predates the prototype-first source revision",
        "open_question": "Select whether to retain, revise, split, collapse, or replace the six accepted D65 target relations under the current prototype-first invariant.",
        "decision_timing": "accumulate-until-end-of-complete-chain",
        "normalization_successor_required": True,
        "unaffected_decision_count": 68,
        "authority_effect": "none",
    }

    followup_result = followups.materialize(
        ROOT,
        targets,
        ontology_inventory,
        current_definitions,
        realization_ledger,
        definition_pack,
    )
    for unit in review_queue["realization_units"]:
        if unit["status"] == "ready-for-candidate-authorship":
            unit["status"] = "prototype-scaffold-authored-awaiting-refinement"
        else:
            unit["status"] = "blocked-pending-successor-selection-proposal-authored"
    for unit in review_queue["ontology_units"]:
        unit["status"] = "review-authored-awaiting-final-decision"
    review_queue["definition_drift_units"][0]["status"] = (
        "successor-proposal-authored-awaiting-final-checkpoint"
    )
    review_queue["ready_count"] = 0
    review_queue["authored_count"] = followup_result["target_candidate_count"]
    review_queue["blocked_count"] = sum(
        item["status"].startswith("blocked")
        for item in review_queue["realization_units"]
    )
    review_queue["authored_ontology_review_count"] = followup_result[
        "ontology_review_count"
    ]
    review_queue["decision_boundary"].update(
        {
            "status": followup_result["decision_request_status"],
            "request_path": "decision-request.json",
            "approval_token": followup_result["approval_token"],
        }
    )

    predecessor_manifest_sha = digest_path(PREDECESSOR / "manifest.json")
    predecessor_receipt_sha = digest_path(PREDECESSOR / "receipts/validation.json")
    candidate = {
        "schema_version": "cyberalchemy-lab-normalized-reconstruction-candidate/v2",
        "candidate_id": "CAL-CYBERALCHEMY-V2-TO-LAB-RECONSTRUCTION-0003",
        "status": "planning-candidate-ready-for-final-owner-review",
        "strategy": "accepted-normalization-to-realization-never-bulk-copy",
        "accepted_baseline": {
            "normalization_ref": "CAL-NORMALIZE-01",
            "decision_ref": "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS",
            "unchanged_definition_decisions_preserved": 68,
            "changed_definition_decisions_requiring_successor": 1,
        },
        "target_counts": {**dict(family_counts), "total": len(targets)},
        "realization_counts": dict(state_counts),
        "define_disposition_counts": dict(disposition_counts),
        "predecessor": {
            "candidate_id": "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0002",
            "manifest_sha256": predecessor_manifest_sha,
            "validation_receipt_sha256": predecessor_receipt_sha,
            "disposition": "preserved-as-tested-history-not-authorized-for-execution",
        },
        "principles": [
            "accepted definition decisions are not reopened without exact source drift",
            "source bytes are read-only evidence and are never bulk-copied",
            "the migration disposition and Define handling disposition are orthogonal axes",
            "machine records are canonical and every human view is generated",
            "file placement and labels never imply admission",
            "source ontology review may follow prototype authorship while ontology reconstruction remains downstream of target realization closure",
            "DomainSpec-v2 ontology identity routes to Craft with legacy aliases preserved",
            "withdrawn definition identifiers remain withdrawn",
        ],
        "decision_preferences": {
            "interaction_boundary": "configurable-workflow-checkpoint",
            "current_checkpoint": "end-of-complete-realization-and-ontology-review-chain",
            "approval_requests_before_checkpoint": 0,
            "independent_decisions_remain_distinct": True,
        },
        "product_construction": {
            "frontier": "Review the complete prototype-scaffold, ontology-routing, and D65-successor chain at the configured single final checkpoint; if selected, refine and test the target families from shared mechanics outward.",
            "runnable_now": ["owner-review-exact-composite-decision-request"],
            "causal_blockers": [
                {
                    "blocker": "CAV2-D65 changed after CAL-NORMALIZE-01 selection",
                    "affected_scope": d65_target_ids,
                    "unaffected_work_continues": True,
                }
            ],
        },
        "followup_construction": {
            "target_candidate_count": followup_result["target_candidate_count"],
            "target_family_counts": followup_result["family_counts"],
            "ontology_review_count": followup_result["ontology_review_count"],
            "d65_successor_status": followup_result["d65_successor_status"],
            "decision_request_status": followup_result["decision_request_status"],
            "approval_token": followup_result["approval_token"],
        },
        "operational_support": [
            {
                "task": "Retire the 0002 bulk-copy execution path from future consideration without deleting its evidence.",
                "owner": "role:repository-migration-owner",
                "affected_stage": None,
                "state": "recorded-as-residue",
                "blocks_frontier": False,
            }
        ],
        "canonical_machine_artifacts": [
            "candidate.json",
            "definition-inventory.json",
            "realization-ledger.json",
            "definition-pack.json",
            "ontology-inventory.json",
            "review-queue.json",
            "reviews/0001-definition/review.json",
            *followup_result["machine_paths"],
            "manifest.json",
            "receipts/validation.json",
        ],
        "generated_human_projections": [
            "CANDIDATE.md",
            "DEFINITION-INVENTORY.md",
            "REALIZATION-LEDGER.md",
            "DEFINITION-PACK.md",
            "ONTOLOGY-INVENTORY.md",
            "REVIEW-QUEUE.md",
            "reviews/0001-definition/REVIEW.md",
            *followup_result["human_paths"],
            "MANIFEST.md",
            "receipts/VALIDATION.md",
        ],
        "authority_effect": "none",
        "claim_ceiling": "This candidate maps accepted normalization targets to exact current evidence, authors non-authoritative prototype scaffolds, reviews ontology routing, and proposes a D65 successor. It does not select the D65 successor or review dispositions, refine or admit the target artifacts, alter CAV2 Define, approve or execute migration, activate a runtime, commit, push, publish, release, or deploy.",
    }

    machine_outputs = {
        "candidate.json": candidate,
        "definition-inventory.json": definition_inventory,
        "realization-ledger.json": realization_ledger,
        "definition-pack.json": definition_pack,
        "ontology-inventory.json": ontology_inventory,
        "review-queue.json": review_queue,
        "reviews/0001-definition/review.json": review,
    }
    for path, value in machine_outputs.items():
        dump(ROOT / path, value)
    projections = {
        "CANDIDATE.md": render_candidate(candidate),
        "DEFINITION-INVENTORY.md": render_definition_inventory(definition_inventory),
        "REALIZATION-LEDGER.md": render_realization_ledger(realization_ledger),
        "DEFINITION-PACK.md": render_definition_pack(definition_pack),
        "ONTOLOGY-INVENTORY.md": render_ontology_inventory(ontology_inventory),
        "REVIEW-QUEUE.md": render_queue(review_queue),
        "reviews/0001-definition/REVIEW.md": render_review(review),
    }
    for path, text in projections.items():
        output = ROOT / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")

    source_bindings = [
        source_binding("cyberalchemy-lab", NORMALIZATION_PATH, LAB),
        source_binding("cyberalchemy-lab", NORMALIZATION_DECISION_PATH, LAB),
        source_binding("cyberalchemy-lab", LAB_DEFINITION_REGISTRY_PATH, LAB),
        source_binding("cyberalchemy-lab", LAB_ARTIFACT_TYPE_REGISTRY_PATH, LAB),
        source_binding("cyberalchemy-lab", PREDECESSOR / "manifest.json", LAB),
        source_binding("cyberalchemy-lab", PREDECESSOR / "receipts/validation.json", LAB),
        source_binding("cyberalchemy-v2-source", DEFINITIONS_PATH, SOURCE),
        source_binding("cyberalchemy-v2-source", DEFINE_PROFILE_PATH, SOURCE),
        source_binding("cyberalchemy-v2-source", DEFINE_DEFINITIONS_PATH, SOURCE),
        source_binding("cyberalchemy-v2-source", DEFINE_HANDLED_PATH, SOURCE),
        source_binding("cyberalchemy-v2-source", DEFINE_SCHEMA_PATH, SOURCE),
    ]
    bound_keys = {(item["repository_id"], item["path"]) for item in source_bindings}
    for package in ontology_inventory["packages"]:
        for material in package["materials"]:
            key = ("cyberalchemy-v2-source", material["path"])
            if key not in bound_keys:
                source_bindings.append(
                    {
                        "kind": "file",
                        "repository_id": key[0],
                        "path": key[1],
                        "sha256": material["sha256"],
                    }
                )
                bound_keys.add(key)
    source_bindings.append(
        {
            "kind": "git-blob",
            "repository_id": "domainspec-core",
            "git_commit": NORMALIZATION_SOURCE_COMMIT,
            "path": "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
            "sha256": digest_bytes(baseline_bytes),
        }
    )
    material_paths = [
        "author.py",
        "followups.py",
        "validate.py",
        *machine_outputs.keys(),
        *projections.keys(),
        *followup_result["all_paths"],
    ]
    manifest = {
        "schema_version": "cyberalchemy-lab-normalized-reconstruction-manifest/v2",
        "manifest_id": "CAL-CAV2-RECONSTRUCTION-MANIFEST-0003",
        "materials": [
            {"path": path, "sha256": digest_path(ROOT / path)} for path in material_paths
        ],
        "source_bindings": source_bindings,
        "repository_roots": {
            "cyberalchemy-lab": "candidate-runtime-repository-root",
            "cyberalchemy-v2-source": "configured-by-CAV2_SOURCE_ROOT-or-sibling-default",
            "domainspec-core": "parent-of-cyberalchemy-v2-source",
        },
        "authority_effect": "none",
    }
    dump(ROOT / "manifest.json", manifest)
    (ROOT / "MANIFEST.md").write_text(render_manifest(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
