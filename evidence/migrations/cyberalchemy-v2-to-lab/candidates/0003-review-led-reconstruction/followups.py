#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def owner_route(target: dict) -> str:
    normalized = target["normalized_record"]
    if target["family"] == "semantic":
        return normalized.get("owner_scope", "scope.shared-authority")
    if target["family"] in {"artifact-type", "relation-kind"}:
        return "role:shared-authority-owner"
    if target["family"] == "profile":
        return "role:profile-owner"
    return "role:projection-owner"


def source_refs(target: dict, current_definitions: dict[str, dict]) -> list[dict]:
    refs = []
    for source in target["accepted_source_decisions"]:
        definition = current_definitions[source["legacy_id"]]
        refs.append(
            {
                "repository_id": "cyberalchemy-v2-source",
                "path": "authority/definitions/DEFINITIONS.md",
                "selector": definition["heading"],
                "definition_id": source["legacy_id"],
                "section_sha256": definition["raw_section_sha256"],
                "accepted_migration_disposition": source["decision"],
            }
        )
    if not refs:
        refs.append(
            {
                "repository_id": "cyberalchemy-lab",
                "path": "docs/normalizations/0001-definition-migration-model/normalization.json",
                "selector": target["target_id"],
                "role": "normalization-supporting-target",
            }
        )
    return refs


def four_facets(target: dict) -> dict:
    normalized = target["normalized_record"]
    family = target["family"]
    classification = {
        "family": family,
        "semantic_kind": normalized.get("semantic_kind"),
        "carrier_ref": normalized.get("carrier_ref"),
        "owner_scope": normalized.get("owner_scope"),
    }
    schema = {
        "candidate_shape": sorted(normalized),
        "admitted_schema_ref": None,
        "schema_state": "prototype-only-needs-family-specific-schema"
        if family != "semantic"
        else "definition-voice-shape-prototyped",
    }
    projection = {
        "machine": "artifact.json",
        "human": "ARTIFACT.md",
        "direction": "machine-to-generated-human",
    }
    checks = [
        "stable-target-identity",
        "normalization-source-closure",
        "owner-route-present",
        "authority-effect-none",
        "generated-human-projection-exact",
    ]
    if family == "semantic":
        checks.append("formal-plain-and-domain-voices-present")
    return {
        "classification": classification,
        "schema": schema,
        "projection": projection,
        "machine_checkable": checks,
    }


def target_candidate(target: dict, current_definitions: dict[str, dict]) -> dict:
    normalized = target["normalized_record"]
    candidate = {
        "schema_version": "cyberalchemy-lab-normalized-target-prototype/v1",
        "candidate_id": f'CAL-NORMALIZED-TARGET-{slug(target["target_id"]).upper()}-V1',
        "target_id": target["target_id"],
        "term": target["term"],
        "family": target["family"],
        "status": "prototype-scaffold",
        "authority_effect": "none",
        "normalization_ref": "CAL-NORMALIZE-01",
        "owner_decision_ref": "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS",
        "accepted_source_decisions": target["accepted_source_decisions"],
        "source_refs": source_refs(target, current_definitions),
        "normalized_contract": normalized,
        "owner_route": owner_route(target),
        "four_facets": four_facets(target),
        "validation_purpose": normalized.get(
            "distinct_validation_purpose",
            f'Preserve the normalized {target["family"]} identity and its declared relations without inferring admission.',
        ),
        "gaps": [
            "No owner admission is attached to this prototype.",
            "A family-specific admitted Artifact Type and schema must exist before canonical promotion.",
            "Consumer bindings and negative fixtures remain separate implementation work.",
        ],
        "claim_ceiling": "This is a generated prototype scaffold authored from the accepted normalization and exact source selectors. It is not a canonical Definition, admitted Artifact Type, selected profile, adopted relation kind, activated projection, implementation, approval, or migration authority.",
    }
    if target["family"] == "semantic":
        kind = normalized["semantic_kind"]
        carrier = normalized["carrier_ref"]
        scope = normalized["owner_scope"]
        sources = ", ".join(
            item["legacy_id"] for item in target["accepted_source_decisions"]
        ) or "the normalization supporting catalog"
        candidate["definition_voices"] = {
            "normative_voice": f'{target["term"]} is the normalized {kind} identified by {target["target_id"]}, owned within {scope}, and carried by {carrier}. Any canonical instance must preserve that classification and the accepted source relations to {sources} without silently merging it with another target.',
            "formal_voice": f'{target["target_id"]} := (semantic_kind={kind}, carrier={carrier}, owner_scope={scope}, source_set={{{sources}}}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.',
            "plain_language_voice": f'{target["term"]} has its own explicit place in the new model so people and tools do not have to guess its kind, owner, or source.',
            "domain_context_voice": f'In CyberAlchemy-lab migration work, {target["term"]} is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.',
            "boundary": "These voices explain the normalized prototype only. They do not replace the complete source meaning, settle D65 drift, or grant semantic authority.",
        }
    return candidate


def render_target(candidate: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is artifact.json. -->",
        "",
        f'# {candidate["term"]}',
        "",
        f'- Target: `{candidate["target_id"]}`',
        f'- Family: `{candidate["family"]}`',
        f'- Status: `{candidate["status"]}`',
        f'- Owner route: `{candidate["owner_route"]}`',
        f'- Authority effect: `{candidate["authority_effect"]}`',
        "",
    ]
    voices = candidate.get("definition_voices")
    if voices:
        lines.extend(
            [
                "## Normative voice",
                "",
                voices["normative_voice"],
                "",
                "## Formal voice",
                "",
                voices["formal_voice"],
                "",
                "## Plain-language voice",
                "",
                voices["plain_language_voice"],
                "",
                "## CyberAlchemy-lab context",
                "",
                voices["domain_context_voice"],
                "",
                "## Boundary",
                "",
                voices["boundary"],
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Validation purpose",
                "",
                candidate["validation_purpose"],
                "",
                "## Normalized contract",
                "",
                "The complete normalized contract is canonical in `artifact.json`; this view does not redefine it.",
                "",
            ]
        )
    lines.extend(["## Claim ceiling", "", candidate["claim_ceiling"], ""])
    return "\n".join(lines)


def ontology_type_for(
    group: dict, packages_by_profile: dict[str, dict]
) -> tuple[str, list[str], str, bool]:
    types = sorted(
        {
            packages_by_profile[path].get("ontology_type", "unknown")
            for path in group["profile_paths"]
        }
    )
    sources = {
        packages_by_profile[path].get("ontology_type_source", "not-selected")
        for path in group["profile_paths"]
    }
    selected_type = types[0] if len(types) == 1 else "mixed-source-profile-types"
    if sources == {"source-profile"} and selected_type != "mixed-source-profile-types":
        return selected_type, types, "source-profile", False
    if sources == {"candidate-inference-from-explicit-business-and-system-refs"}:
        return (
            selected_type,
            types,
            "candidate-proposal-from-explicit-business-and-system-refs",
            True,
        )
    return selected_type, types, "candidate-unresolved", True


def review_disposition(group_id: str) -> str:
    if group_id == "domainspec-v2-lineage":
        return "route-lineage-to-craft-and-preserve-legacy-aliases"
    if group_id == "cav2.define":
        return "retain-as-cav2-source-method-and-reconstruct-only-required-lab-consumers"
    if group_id.startswith("cav2.define."):
        return "retain-as-define-source-model-and-map-required-claims-after-target-closure"
    if "governance" in group_id:
        return "map-owned-meaning-to-governance-context-without-runtime-enforcement"
    if "product" in group_id:
        return "map-owned-meaning-to-product-context-without-claiming-market-or-runtime-proof"
    return "retain-as-source-evidence-pending-context-owned-reconstruction"


def ontology_review(
    sequence: int,
    group: dict,
    packages_by_profile: dict[str, dict],
) -> dict:
    packages = [packages_by_profile[path] for path in group["profile_paths"]]
    ontology_type, viable_types, type_source, type_selection_required = ontology_type_for(
        group, packages_by_profile
    )
    material_count = sum(len(item["materials"]) for item in packages)
    selector_count = len(
        {selector for item in packages for selector in item["definition_selectors"]}
    )
    statuses = sorted({item["source_status"] for item in packages})
    branches = sorted({str(item.get("branch", "none")) for item in packages})
    findings = [
        {
            "finding_id": f"CAL-ONTOLOGY-REVIEW-{sequence:02d}-SOURCE-POSTURE",
            "kind": "observed-evidence",
            "statement": f'{len(packages)} package profile(s), {material_count} exact material bindings, and {selector_count} distinct CAV2 Definition selectors were observed.',
            "evidence_confidence": "high",
            "commitment_confidence": "not-selected",
        },
        {
            "finding_id": f"CAL-ONTOLOGY-REVIEW-{sequence:02d}-AUTHORITY",
            "kind": "authority-boundary",
            "statement": "The reviewed package records are source evidence or scaffolds; this review grants no ontology admission, runtime conformance, or migration authority.",
            "evidence_confidence": "high",
            "commitment_confidence": "not-selected",
        },
    ]
    blockers = [
        {
            "blocker_id": "NORMALIZED-TARGET-REALIZATION-INCOMPLETE",
            "scope": "ontology reconstruction",
            "effect": "Review disposition may be selected, but ontology reconstruction remains downstream of normalized-target realization closure.",
        }
    ]
    if group.get("lineage_conflict"):
        findings.append(
            {
                "finding_id": f"CAL-ONTOLOGY-REVIEW-{sequence:02d}-LINEAGE-CONFLICT",
                "kind": "contradiction",
                "statement": f'{len(group["canonical_profile_paths"])} profiles declare canonical status for one ontology identity; neither is silently selected.',
                "evidence_confidence": "high",
                "commitment_confidence": "not-selected",
            }
        )
        blockers.append(
            {
                "blocker_id": "MULTIPLE-CANONICAL-LINEAGE-CLAIMS",
                "scope": group["canonical_profile_paths"],
                "effect": "Craft lineage selection must resolve the current source epoch before reconstruction.",
            }
        )
    return {
        "schema_version": "cyberalchemy-lab-ontology-group-review/v1",
        "review_id": f"CAL-CAV2-ONTOLOGY-GROUP-REVIEW-{sequence:02d}",
        "group_id": group["group_id"],
        "status": "reviewed-routing-candidate",
        "mode": "map-and-validate",
        "materialization": "single-artifact-allowed",
        "ontology_type": ontology_type,
        "ontology_type_selection": {
            "source": type_source,
            "confidence": "exact"
            if type_source == "source-profile"
            else "candidate",
            "viable_types": viable_types,
            "user_selection_required": type_selection_required,
        },
        "branches": branches,
        "source_statuses": statuses,
        "source_packages": [
            {
                "ontology_id": item["ontology_id"],
                "profile_path": item["profile_path"],
                "profile_sha256": next(
                    material["sha256"]
                    for material in item["materials"]
                    if material["path"] == item["profile_path"]
                ),
                "material_count": len(item["materials"]),
                "authority_effect": item["authority_effect"],
            }
            for item in packages
        ],
        "findings": findings,
        "recommended_disposition": review_disposition(group["group_id"]),
        "successor_route": group.get("successor_route"),
        "blockers": blockers,
        "traceability_gaps": [
            "No bridge alignment is claimed without evidence from both business and system branches.",
            "Target-context ownership and admission remain downstream decisions.",
        ],
        "authority_effect": "none",
        "claim_ceiling": "This review maps exact source-package structure, lineage, and routing. It does not promote confidence, choose a canonical conflicting epoch, admit an ontology, prove implementation alignment, activate a runtime, or authorize migration.",
    }


def render_ontology_review(review: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is review.json. -->",
        "",
        f'# Ontology review: {review["group_id"]}',
        "",
        f'- Status: `{review["status"]}`',
        f'- Ontology type: `{review["ontology_type"]}`',
        f'- Type selection: `{review["ontology_type_selection"]["source"]}`',
        f'- Materialization: `{review["materialization"]}`',
        f'- Recommended disposition: `{review["recommended_disposition"]}`',
        "",
        "## Findings",
        "",
    ]
    for finding in review["findings"]:
        lines.append(f'- `{finding["kind"]}` — {finding["statement"]}')
    lines.extend(["", "## Blockers", ""])
    for blocker in review["blockers"]:
        lines.append(f'- `{blocker["blocker_id"]}` — {blocker["effect"]}')
    lines.extend(["", "## Claim ceiling", "", review["claim_ceiling"], ""])
    return "\n".join(lines)


def d65_successor_proposal() -> dict:
    return {
        "schema_version": "cyberalchemy-lab-d65-normalization-successor-proposal/v1",
        "proposal_id": "CAL-CAV2-D65-NORMALIZATION-SUCCESSOR-0001",
        "status": "candidate-awaiting-final-checkpoint",
        "authority_effect": "none",
        "predecessor": {
            "source_definition_id": "CAV2-D65",
            "accepted_decision": "split",
            "accepted_targets": [
                "semantic.craft-governed-construction-invariant",
                "type.construction-profile",
                "type.construction-binding",
                "type.implementation-binding",
                "profile.construction-evaluation",
                "profile.capability-conformance",
            ],
        },
        "current_source_term": "Prototype-First DomainSpec Construction Invariant",
        "recommended_disposition": "revise-split-with-minimal-new-axes",
        "recommended_targets": [
            {
                "target_id": "semantic.prototype-first-domainspec-construction-invariant",
                "change": "replace",
                "predecessor_target": "semantic.craft-governed-construction-invariant",
                "reason": "The invariant now governs prototype learning and a tested-product boundary before any authority request.",
            },
            {
                "target_id": "type.construction-profile",
                "change": "retain",
                "reason": "The stage vocabulary remains owner-selectable configuration rather than stable semantic identity.",
            },
            {
                "target_id": "type.construction-binding",
                "change": "retain",
                "reason": "The current formal definition still names ConstructionBinding as the exact chain carrier.",
            },
            {
                "target_id": "type.implementation-binding",
                "change": "retain",
                "reason": "Implementation-to-model binding remains distinct from construction-chain identity.",
            },
            {
                "target_id": "profile.prototype-construction-evaluation",
                "change": "replace",
                "predecessor_target": "profile.construction-evaluation",
                "reason": "Evaluation must permit iterative prototype epochs and freeze only the testable candidate boundary.",
            },
            {
                "target_id": "profile.product-candidate-evaluation",
                "change": "replace",
                "predecessor_target": "profile.capability-conformance",
                "reason": "D65 now requires current product-test evidence and product approval eligibility rather than broad capability conformance.",
            },
        ],
        "reused_normalized_relations": [
            "relation.derives-from",
            "relation.compiles-to",
            "relation.binds-implementation",
            "relation.evaluates",
            "relation.authorizes",
            "relation.adopts",
        ],
        "new_axis_rejections": [
            "Do not mint one Artifact Type for every prototype stage before distinct validation closure is demonstrated.",
            "Do not encode product approval as lifecycle state on a construction artifact.",
            "Do not collapse product approval with post-approval authority decisions.",
        ],
        "rollback": "Retain the accepted CAL-NORMALIZE-01 D65 mapping unchanged if this proposal is rejected; keep all six affected realization units open.",
        "claim_ceiling": "This is a successor normalization proposal for final owner review. It does not change CAV2-D65, rewrite CAL-NORMALIZE-01, select the successor mapping, admit target types or profiles, or authorize construction or migration.",
    }


def render_d65(proposal: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is d65-successor.json. -->",
        "",
        "# CAV2-D65 Normalization Successor Proposal",
        "",
        f'- Status: `{proposal["status"]}`',
        f'- Recommendation: `{proposal["recommended_disposition"]}`',
        "",
        "| Target | Change | Reason |",
        "|---|---|---|",
    ]
    for item in proposal["recommended_targets"]:
        lines.append(
            f'| `{item["target_id"]}` | `{item["change"]}` | {item["reason"]} |'
        )
    lines.extend(["", "## Claim ceiling", "", proposal["claim_ceiling"], ""])
    return "\n".join(lines)


def render_index(title: str, canonical: str, entries: list[dict]) -> str:
    lines = [
        f"<!-- GENERATED FILE: canonical data is {canonical}. -->",
        "",
        f"# {title}",
        "",
        f'- Entries: `{len(entries)}`',
        "",
        "| ID | Machine | SHA-256 |",
        "|---|---|---|",
    ]
    for entry in entries:
        identity = entry.get("target_id") or entry.get("group_id")
        lines.append(
            f'| `{identity}` | `{entry["machine_path"]}` | `{entry["machine_sha256"]}` |'
        )
    lines.append("")
    return "\n".join(lines)


def decision_request(
    target_index_sha: str,
    ontology_index_sha: str,
    d65_sha: str,
    ledger_sha: str,
    pack_sha: str,
) -> dict:
    return {
        "schema_version": "cyberalchemy-lab-composite-decision-request/v1",
        "request_id": "CAL-CAV2-LAB-RECONSTRUCTION-0003-FINAL-DECISION",
        "status": "ready-for-owner-review",
        "approval_boundary": "end-of-complete-candidate-chain",
        "approval_token": "APPROVE-CAV2-LAB-RECONSTRUCTION-0003",
        "alternative_tokens": [
            "REVISE-CAV2-LAB-RECONSTRUCTION-0003",
            "DEFER-CAV2-LAB-RECONSTRUCTION-0003",
            "STOP-CAV2-LAB-RECONSTRUCTION-0003",
        ],
        "exact_subjects": [
            {"path": "target-candidate-index.json", "sha256": target_index_sha},
            {"path": "ontology-review-index.json", "sha256": ontology_index_sha},
            {"path": "d65-successor.json", "sha256": d65_sha},
            {"path": "realization-ledger.json", "sha256": ledger_sha},
            {"path": "definition-pack.json", "sha256": pack_sha},
        ],
        "distinct_decisions": [
            {
                "decision_id": "CAL-RECON-0003-D65-SUCCESSOR",
                "selection_if_approved": "accept-d65-successor-as-normalization-planning-baseline",
                "effect": "closes the D65 normalization question for later candidate authoring only",
            },
            {
                "decision_id": "CAL-RECON-0003-TARGET-SCAFFOLDS",
                "selection_if_approved": "accept-176-prototype-scaffolds-as-refinement-baseline",
                "effect": "permits family-by-family refinement and testing; grants no admission",
            },
            {
                "decision_id": "CAL-RECON-0003-ONTOLOGY-ROUTES",
                "selection_if_approved": "accept-10-review-dispositions-and-the-two-explicit-dual-ref-business-system-bridge-type-proposals-as-migration-routing-baseline",
                "effect": "routes later context-owned reconstruction and settles candidate typing for the two untyped source profiles; admits no ontology",
            },
        ],
        "atomicity": "One response selects all three explicitly enumerated planning decisions against the exact subject digests; none is inferred from another.",
        "next_construction_frontier_if_approved": "refine and test target candidates family-by-family, starting with shared artifact mechanics and semantic-authority carriers",
        "authority_effect": "planning-selection-only-if-owner-approves",
        "non_effects": [
            "no Definition promotion",
            "no Artifact Type admission",
            "no ontology admission or activation",
            "no runtime conformance",
            "no migration execution or source deletion",
            "no commit, push, publication, release, or deployment",
        ],
        "claim_ceiling": "This request creates no decision by itself. The approval token would accept only the three exact planning baselines enumerated here and would grant no canonical, operational, publication, release, deployment, or external-effect authority.",
    }


def render_decision_request(request: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is decision-request.json. -->",
        "",
        "# Final Reconstruction Decision Request",
        "",
        f'- Status: `{request["status"]}`',
        f'- Approval token: `{request["approval_token"]}`',
        f'- Exact subjects: `{len(request["exact_subjects"])}`',
        "",
        "## Distinct decisions selected by the one token",
        "",
    ]
    for decision in request["distinct_decisions"]:
        lines.append(
            f'- `{decision["decision_id"]}` — {decision["selection_if_approved"]}; {decision["effect"]}.'
        )
    lines.extend(["", "## Claim ceiling", "", request["claim_ceiling"], ""])
    return "\n".join(lines)


def materialize(
    root: Path,
    targets: list[dict],
    ontology_inventory: dict,
    current_definitions: dict[str, dict],
    realization_ledger: dict,
    definition_pack: dict,
) -> dict:
    machine_paths = []
    human_paths = []
    target_entries = []
    for target in targets:
        if target["realization_state"] != "unresolved-no-canonical-match":
            continue
        base = Path("target-candidates") / target["family"] / slug(target["target_id"]) / "v1"
        machine_path = base / "artifact.json"
        human_path = base / "ARTIFACT.md"
        candidate = target_candidate(target, current_definitions)
        human = render_target(candidate)
        dump(root / machine_path, candidate)
        (root / human_path).write_text(human, encoding="utf-8")
        machine_paths.append(machine_path.as_posix())
        human_paths.append(human_path.as_posix())
        target_entries.append(
            {
                "target_id": target["target_id"],
                "family": target["family"],
                "machine_path": machine_path.as_posix(),
                "machine_sha256": digest_path(root / machine_path),
                "human_path": human_path.as_posix(),
                "human_sha256": digest_path(root / human_path),
                "status": candidate["status"],
                "authority_effect": "none",
            }
        )
    target_index = {
        "schema_version": "cyberalchemy-lab-normalized-target-prototype-index/v1",
        "index_id": "CAL-CAV2-NORMALIZED-TARGET-PROTOTYPES-0001",
        "entry_count": len(target_entries),
        "entries": target_entries,
        "source_realization_ledger_sha256": digest_bytes(canonical_bytes(realization_ledger)),
        "authority_effect": "none",
        "claim_ceiling": "The index binds prototype scaffolds only; it is not an Artifact Type or Definition registry and grants no admission.",
    }
    dump(root / "target-candidate-index.json", target_index)
    target_index_human = render_index(
        "Normalized Target Prototype Index", "target-candidate-index.json", target_entries
    )
    (root / "TARGET-CANDIDATE-INDEX.md").write_text(
        target_index_human, encoding="utf-8"
    )
    machine_paths.append("target-candidate-index.json")
    human_paths.append("TARGET-CANDIDATE-INDEX.md")

    packages_by_profile = {
        item["profile_path"]: item for item in ontology_inventory["packages"]
    }
    ontology_entries = []
    for sequence, group in enumerate(ontology_inventory["review_groups"], 1):
        base = Path("ontology-reviews") / f'{sequence:02d}-{slug(group["group_id"])}'
        machine_path = base / "review.json"
        human_path = base / "REVIEW.md"
        review = ontology_review(sequence, group, packages_by_profile)
        human = render_ontology_review(review)
        dump(root / machine_path, review)
        (root / human_path).write_text(human, encoding="utf-8")
        machine_paths.append(machine_path.as_posix())
        human_paths.append(human_path.as_posix())
        ontology_entries.append(
            {
                "group_id": group["group_id"],
                "machine_path": machine_path.as_posix(),
                "machine_sha256": digest_path(root / machine_path),
                "human_path": human_path.as_posix(),
                "human_sha256": digest_path(root / human_path),
                "recommended_disposition": review["recommended_disposition"],
                "blocker_count": len(review["blockers"]),
                "authority_effect": "none",
            }
        )
    ontology_index = {
        "schema_version": "cyberalchemy-lab-ontology-group-review-index/v1",
        "index_id": "CAL-CAV2-ONTOLOGY-GROUP-REVIEWS-0001",
        "entry_count": len(ontology_entries),
        "entries": ontology_entries,
        "authority_effect": "none",
        "claim_ceiling": "This index binds ten review artifacts. It does not select their recommendations or admit source or target ontologies.",
    }
    dump(root / "ontology-review-index.json", ontology_index)
    (root / "ONTOLOGY-REVIEW-INDEX.md").write_text(
        render_index(
            "Ontology Group Review Index", "ontology-review-index.json", ontology_entries
        ),
        encoding="utf-8",
    )
    machine_paths.append("ontology-review-index.json")
    human_paths.append("ONTOLOGY-REVIEW-INDEX.md")

    d65 = d65_successor_proposal()
    dump(root / "d65-successor.json", d65)
    (root / "D65-SUCCESSOR.md").write_text(render_d65(d65), encoding="utf-8")
    machine_paths.append("d65-successor.json")
    human_paths.append("D65-SUCCESSOR.md")

    request = decision_request(
        digest_path(root / "target-candidate-index.json"),
        digest_path(root / "ontology-review-index.json"),
        digest_path(root / "d65-successor.json"),
        digest_bytes(canonical_bytes(realization_ledger)),
        digest_bytes(canonical_bytes(definition_pack)),
    )
    dump(root / "decision-request.json", request)
    (root / "DECISION-REQUEST.md").write_text(
        render_decision_request(request), encoding="utf-8"
    )
    machine_paths.append("decision-request.json")
    human_paths.append("DECISION-REQUEST.md")

    return {
        "target_candidate_count": len(target_entries),
        "ontology_review_count": len(ontology_entries),
        "d65_successor_status": d65["status"],
        "decision_request_status": request["status"],
        "approval_token": request["approval_token"],
        "machine_paths": machine_paths,
        "human_paths": human_paths,
        "all_paths": [*machine_paths, *human_paths],
        "family_counts": dict(Counter(item["family"] for item in target_entries)),
    }
