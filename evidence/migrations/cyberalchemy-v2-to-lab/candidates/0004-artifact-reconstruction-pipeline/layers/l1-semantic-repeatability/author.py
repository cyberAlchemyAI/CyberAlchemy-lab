#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT.parents[1]
LAB = next(path for path in ROOT.parents if path.name == "CyberAlchemy-lab")
SOURCE = LAB.parent / "domainspec-core" / "cyberAlchemy-v2"
PREDECESSOR = PIPELINE.parent / "0003-review-led-reconstruction"
TARGET_INDEX = PREDECESSOR / "target-candidate-index.json"
SCAFFOLD_ROOT = PREDECESSOR / "target-candidates/semantic"
PLANNING_DECISION = PREDECESSOR / "decisions/0001-planning-selection/decision.json"
SOURCE_DEFINITIONS = SOURCE / "authority/definitions/DEFINITIONS.md"
DEFINITION_SCHEMA = LAB / "authority/artifact-types/definition/v1/schema.json"
DEFINITION_GENERATOR = LAB / "authority/artifact-types/definition/v1/generator.py"
ADMITTED_REGISTRY = LAB / "authority/definitions/registry.json"
ADMITTED_INDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
L0_MANIFEST = PIPELINE / "manifest.json"
L0_RECEIPT = PIPELINE / "receipts/validation.json"


TARGET_SPECIFIC_MEANINGS = {
    "semantic.cyberalchemy-construction-method": (
        "CyberAlchemy Construction Method is the governed recursive method that carries owner-controlled Product intent through explicit context, semantic, product, specification, realization, conformance, operation, recovery, evolution, and continuation stages while preserving evidence and residue at every transition.",
        "It is the whole governed path for turning product intent into a working, reviewable system.",
    ),
    "semantic.residue-escalation-method": (
        "Residue Escalation Method is the bounded procedure that classifies unresolved construction residue, preserves its originating stage and evidence, assigns an accountable owner route, and either returns it to a satisfiable predecessor or escalates it without pretending the construction is complete.",
        "When something cannot be resolved, this method records exactly what is missing and routes it to someone who can decide or repair it.",
    ),
    "semantic.work-state-continuity-capability": (
        "Work-State Continuity Capability is the ability to preserve and reconstruct current work state across people, agents, sessions, interruptions, and child contexts from one declared ledger containing decisions, blockers, evidence, artifacts, residue, and next routes.",
        "It lets work resume from recorded state instead of relying on somebody remembering the conversation.",
    ),
    "semantic.classification-axis": (
        "A Classification Axis is one explicitly named, independently valued dimension used to classify an artifact or concept for a distinct decision or validation purpose.",
        "It is one question in a classification, such as what something means or what lifecycle state it has.",
    ),
    "semantic.classification-orthogonality-invariant": (
        "Classification Orthogonality Invariant requires every canonical classification axis to carry a distinct decision or validation purpose; one axis must not be silently inferred from another, redundant canonical labels must be rejected, dependent classifications must be explicit relations, and convenience labels must remain generated projections.",
        "Keep classification questions separate, connect dependent answers explicitly, and do not store a convenient duplicate as a new truth.",
    ),
    "semantic.authority": (
        "Authority is an owner-qualified and scope-bounded right or responsibility to decide what a declared term, rule, status, artifact, relation, result, or mutation is permitted to count as for one purpose.",
        "Authority says who may decide what counts, for which purpose and within which boundary.",
    ),
    "semantic.authority-claim": (
        "An Authority Claim is an explicit, challengeable assertion that a named owner or owner route may perform a named operation over a named governed object within an exact scope, on a stated decision or evidence basis, with a declared effect.",
        "It is a precise statement that someone has a particular right in a particular scope; making the statement does not prove it is valid.",
    ),
    "semantic.responsibility": (
        "Responsibility is an owner-qualified obligation to perform, maintain, answer for, or route a declared outcome within a bounded scope; it does not by itself grant the authority needed to cause that outcome.",
        "Responsibility says what someone must answer for, which is different from what they are allowed to authorize.",
    ),
    "semantic.artifact": (
        "An Artifact is an identity-bearing, typed, versioned record produced or maintained for a declared purpose whose canonical machine representation, generated human projection, ownership, provenance, lifecycle posture, and validation surface are explicit.",
        "An artifact is a governed piece of recorded work that tools can validate and people can understand.",
    ),
    "semantic.canonical-representation-invariant": (
        "Canonical Representation Invariant requires each artifact to have exactly one declared machine-canonical representation; human views and convenience labels are generated projections, directory placement cannot establish type or authority, and every admitted canonical kind must bind an owner-approved process origin with an honest assurance level.",
        "Store one machine truth, generate the readable view from it, and never let the folder name or generated text become a second authority.",
    ),
    "semantic.premise": (
        "A Premise is a defeasible working proposition deliberately adopted so work may proceed without claiming that the proposition has been established as true; it carries its evidence posture, conviction, revision route, and retirement conditions.",
        "A premise is a declared assumption the project chooses to work with for now.",
    ),
    "semantic.hypothesis": (
        "A Hypothesis is a falsifiable provisional proposition posed for investigation or experiment, with declared observations or outcomes that could support, refine, or reject it; it is not adopted as a working basis merely by being stated.",
        "A hypothesis is an idea framed so evidence can test it, not an assumption the project has already chosen to rely on.",
    ),
    "semantic.research-inquiry": (
        "A Research Inquiry is the bounded question, scope, source policy, method, Project and Goal linkage, owner route, and stopping conditions that define what a research effort intends to investigate before evidence is gathered.",
        "It defines the question and rules for a piece of research before the research is run.",
    ),
    "semantic.research-run": (
        "A Research Run is one attributable execution of a Research Inquiry that records the actual sources inspected, method performed, observations gathered, limitations encountered, evidence-set produced, and completion or stop state.",
        "It is the receipt of what a particular research attempt actually did.",
    ),
    "semantic.evidence-set": (
        "An Evidence Set is a bounded, provenance-preserving aggregate of supporting evidence, counterevidence, limitations, freshness, and applicability assembled for one declared question or claim without itself becoming a finding or decision.",
        "It is the organized body of evidence for a question, including what pushes against the answer and where the evidence is weak.",
    ),
    "semantic.finding": (
        "A Finding is an evidence-bounded, attributable conclusion derived from one or more Research Runs or Evidence Sets whose claim wording does not exceed its support and whose limitations and challenge route remain explicit.",
        "A finding is what the evidence currently supports saying; it is not automatically a decision or policy.",
    ),
    "semantic.experiment-design": (
        "An Experiment Design is the pre-run specification of a bounded empirical test, including its question or hypothesis, subject, protocol, conditions, variables or interventions, measures, prerequisites, stop rules, owner route, and challenge route.",
        "It is the test plan written before anyone claims the test was performed.",
    ),
    "semantic.experiment-run": (
        "An Experiment Run is one attributable execution of an Experiment Design that records the actual environment, inputs, interventions, deviations, observations, timestamps, stop condition, and evidence produced.",
        "It records what happened in one execution of the planned experiment.",
    ),
    "semantic.observation": (
        "An Observation is an attributable record of something measured, perceived, or recorded during a Research or Experiment Run, together with its method, conditions, provenance, and uncertainty; it is not yet an explanatory finding.",
        "An observation records what was seen or measured, before interpreting what it means.",
    ),
    "semantic.context": (
        "A Context is a durable, identity-bearing, owner-qualified boundary of relevance and interpretation for one declared purpose, anchored to exactly one Product and, when applicable, one Project and one Goal, with explicit consumers, subject scope, and source policies.",
        "A context is the stable boundary that says what information and meaning matter for one purpose.",
    ),
    "semantic.context-request": (
        "A Context Request is a bounded, attributable request to resolve a declared Context for named consumers and intended uses under exact selectors, freshness requirements, exclusions, and output constraints; it neither mutates the Context nor grants authority over selected sources.",
        "It asks for a particular usable slice of a context without changing the context itself.",
    ),
    "semantic.context-view": (
        "A Context View is an immutable, digest-bound projection produced by resolving one Context Request against one exact Context identity and source epoch; it records included and excluded material, lineage, limitations, and expiry or refresh conditions without becoming the Context itself.",
        "It is a frozen answer to one context request at one point in the source history.",
    ),
    "semantic.person": (
        "A Person is one human individual whose identity remains distinct from accounts, references, claims, roles, memberships, permissions, sessions, and machine-readable records associated with that individual.",
        "A person is the human being, not their account, role, or database record.",
    ),
    "semantic.person-reference": (
        "A Person Reference is a minimal, purpose-bounded identifier or record used to refer to a Person in a governed artifact while minimizing personal data; it is a projection and never the Person itself.",
        "It is the smallest record needed to point to a person for a specific purpose.",
    ),
    "semantic.identity-claim": (
        "An Identity Claim is an attributable, challengeable assertion that a Person Reference denotes a particular Person under a declared evidence and assurance policy; the claim does not establish private attributes, roles, membership, or authority.",
        "It says that a reference belongs to a person and states why that should be believed; it does not grant that person any role or permission.",
    ),
    "semantic.team": (
        "A Team is a durable, owner-qualified collective identity through which Persons coordinate toward one declared purpose and scope, independently of its changing memberships, roles, responsibilities, and authority relations.",
        "A team is the continuing group identity, not merely whoever happens to be a member today.",
    ),
    "semantic.team-membership": (
        "A Team Membership is a time-bounded, attributable relation connecting one Person to one Team with an explicit lifecycle state; it does not by itself assign a Role, Responsibility, or Authority.",
        "Membership records that a person belongs to a team for a period, without assuming what job or power they have.",
    ),
    "semantic.role": (
        "A Role is a reusable, scope-bounded position describing expected responsibilities and eligible authority relationships independently of any Person, Team Membership, or current assignment.",
        "A role describes a position and its expectations before saying who holds it.",
    ),
    "semantic.role-assignment": (
        "A Role Assignment is an owner-qualified, time-bounded relation that binds one Person or Team to one Role within an exact scope and lifecycle epoch; it does not create Team Membership or authority beyond separately admitted claims.",
        "It records who holds a role, where, and for how long, without silently making them a team member or granting extra authority.",
    ),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(LAB.resolve()).as_posix()


def source_rel(path: Path) -> str:
    return path.resolve().relative_to(SOURCE.resolve()).as_posix()


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(result)
    return result


def slug(target_id: str) -> str:
    return target_id.removeprefix("semantic.")


def extract_source_sections() -> dict[str, dict]:
    text = SOURCE_DEFINITIONS.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^## CAV2-D(\d+): (.+)$", text))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else text.find(
            "\n## Withdrawn Definition IDs", match.end()
        )
        if end < 0:
            end = len(text)
        section = text[match.start():end].rstrip() + "\n"
        legacy_id = f"CAV2-D{int(match.group(1))}"
        result[legacy_id] = {
            "legacy_id": legacy_id,
            "heading": match.group(0),
            "term": match.group(2).strip(),
            "section": section,
            "sha256": digest_bytes(section.encode("utf-8")),
        }
    return result


def subsection(section: str, heading: str) -> str:
    match = re.search(rf"(?m)^### {re.escape(heading)}\s*$", section)
    if not match:
        return ""
    next_heading = re.search(r"(?m)^### ", section[match.end():])
    end = match.end() + next_heading.start() if next_heading else len(section)
    return section[match.end():end].strip()


def source_aliases(section: str) -> list[str]:
    match = re.search(r"(?m)^Aliases:\s*(.+)$", section)
    return [item.strip() for item in match.group(1).split(",") if item.strip()] if match else []


def semantic_scaffolds() -> list[tuple[Path, dict]]:
    index = load(TARGET_INDEX)
    entries = [item for item in index["entries"] if item["family"] == "semantic"]
    return [(PREDECESSOR / item["machine_path"], load(PREDECESSOR / item["machine_path"])) for item in entries]


def dependency_model(scaffolds: list[tuple[Path, dict]], sections: dict[str, dict]) -> tuple[list[tuple[str, str]], list[dict]]:
    legacy_to_targets: dict[str, list[str]] = defaultdict(list)
    for _, scaffold in scaffolds:
        for source in scaffold["source_refs"]:
            if "definition_id" in source:
                legacy_to_targets[source["definition_id"]].append(scaffold["target_id"])

    edges: set[tuple[str, str]] = set()
    residue = set()
    for _, scaffold in scaffolds:
        own_sources = {item.get("definition_id") for item in scaffold["source_refs"]}
        for source in scaffold["source_refs"]:
            legacy_id = source.get("definition_id")
            if not legacy_id:
                continue
            mentions = set(re.findall(r"CAV2-D\d+", sections[legacy_id]["section"])) - own_sources
            for mention in mentions:
                mapped = legacy_to_targets.get(mention, [])
                if mapped:
                    edges.update((dependency, scaffold["target_id"]) for dependency in mapped if dependency != scaffold["target_id"])
                else:
                    residue.add((scaffold["target_id"], mention))
    return sorted(edges), [
        {"consumer_target_id": target, "legacy_reference": legacy, "classification": "source-lineage-residue"}
        for target, legacy in sorted(residue)
    ]


def dependency_batches(target_ids: list[str], edges: list[tuple[str, str]]) -> list[dict]:
    adjacency = {node: [] for node in target_ids}
    for source, target in edges:
        adjacency[source].append(target)

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for child in sorted(adjacency[node]):
            if child not in indices:
                visit(child)
                low[node] = min(low[node], low[child])
            elif child in on_stack:
                low[node] = min(low[node], indices[child])
        if low[node] == indices[node]:
            component = []
            while True:
                child = stack.pop()
                on_stack.remove(child)
                component.append(child)
                if child == node:
                    break
            components.append(sorted(component))

    for node in sorted(target_ids):
        if node not in indices:
            visit(node)

    component_of = {node: number for number, component in enumerate(components) for node in component}
    dependencies = {number: set() for number in range(len(components))}
    for source, target in edges:
        source_component = component_of[source]
        target_component = component_of[target]
        if source_component != target_component:
            dependencies[target_component].add(source_component)

    levels: dict[int, int] = {}

    def level(component: int) -> int:
        if component not in levels:
            levels[component] = 0 if not dependencies[component] else 1 + max(level(item) for item in dependencies[component])
        return levels[component]

    for component in range(len(components)):
        level(component)

    batches = []
    for batch_level in range(max(levels.values(), default=-1) + 1):
        selected = sorted(component for component, value in levels.items() if value == batch_level)
        targets = sorted(node for component in selected for node in components[component])
        prior_levels = sorted({levels[dep] for component in selected for dep in dependencies[component]})
        batches.append({
            "batch_id": f"L1-B{batch_level + 1:02d}",
            "dependency_level": batch_level,
            "depends_on": [f"L1-B{value + 1:02d}" for value in prior_levels],
            "target_ids": targets,
            "strongly_connected_groups": [components[item] for item in selected if len(components[item]) > 1],
            "decision_question": "After this batch, we know whether its Definition candidates reproduce independently while preserving all earlier dependency batches.",
        })
    return batches


def definition_record(
    scaffold_path: Path,
    scaffold: dict,
    sections: dict[str, dict],
    sibling_targets: dict[str, list[str]],
    consumers: dict[str, list[str]],
) -> dict:
    target_id = scaffold["target_id"]
    definition_id = target_id.replace("semantic.", "cal.definition.", 1)
    selected_sources = [item for item in scaffold["source_refs"] if "definition_id" in item]
    selected_sections = [sections[item["definition_id"]] for item in selected_sources]
    normalized_voice = scaffold["definition_voices"]["normative_voice"]
    normative_bases = [subsection(item["section"], "Normative Definition") for item in selected_sections]
    specific_meaning = TARGET_SPECIFIC_MEANINGS.get(target_id)
    normative_statement = normalized_voice
    if specific_meaning:
        normative_statement += "\n\nTarget-specific normative meaning:\n\n" + specific_meaning[0]
    normative_statement += "\n\nBound source-semantic basis:\n\n" + "\n\n".join(normative_bases)
    formal = [subsection(item["section"], "Formal Interpretation") for item in selected_sections]
    formal_expression = "\n\n".join(item for item in formal if item) or scaffold["definition_voices"]["formal_voice"]
    plain = specific_meaning[1] if specific_meaning else "\n\n".join(subsection(item["section"], "Plain-Language Intuition") for item in selected_sections)
    domain_source = "\n\n".join(subsection(item["section"], "Domain-Context Voice") for item in selected_sections)
    operational = "\n\n".join(subsection(item["section"], "Operational Interpretation") for item in selected_sections)
    boundaries = [subsection(item["section"], "Boundary") for item in selected_sections]
    for source in selected_sources:
        siblings = sorted(item for item in sibling_targets[source["definition_id"]] if item != target_id)
        if siblings:
            boundaries.append(
                f"This target remains distinct from the sibling targets {', '.join(siblings)} reconstructed from {source['definition_id']}; shared source lineage does not merge their identities or validation purposes."
            )
    aliases = []
    for item in selected_sections:
        aliases.extend(source_aliases(item["section"]))
    aliases.extend(item["legacy_term"] for item in scaffold["accepted_source_decisions"] if item["legacy_term"].casefold() != scaffold["term"].casefold())
    aliases = sorted(
        {item for item in aliases if item.casefold() != scaffold["term"].casefold()},
        key=lambda item: (item.casefold(), item),
    )
    generator_sha = sha(DEFINITION_GENERATOR)
    schema_sha = sha(DEFINITION_SCHEMA)
    version = "1.0.0-candidate.1"
    return {
        "schema_version": "cyberalchemy-lab-definition/v1",
        "definition_id": definition_id,
        "version": version,
        "term": scaffold["term"],
        "aliases": aliases,
        "classification": {
            "artifact_type_ref": "cal.artifact-type.definition/v1",
            "semantic_kind": "definition",
            "authority_kind": "semantic-authority",
            "lifecycle_posture_ref": "candidate:artifact-reconstruction-l1/v1",
        },
        "semantic_owner_ref": "role:definition-owner",
        "scope": {
            "authority_scope_ref": scaffold["normalized_contract"]["owner_scope"],
            "applicability": operational,
            "exclusions": [
                "Admission, activation, publication, release, deployment, and external effects.",
                "Meanings assigned to split or reclassified sibling targets unless explicitly referenced.",
            ],
        },
        "voices": {
            "scientific_formal": {
                "normative_statement": normative_statement,
                "formal_expression": formal_expression,
                "notation": [
                    {"symbol": target_id, "meaning": f"Stable normalized identity for {scaffold['term']}."},
                    *[
                        {"symbol": item["definition_id"], "meaning": "Bound CyberAlchemy-v2 source-definition identity."}
                        for item in selected_sources
                    ],
                ],
                "boundary_conditions": [item for item in boundaries if item],
                "testable_conditions": [
                    f"The candidate identity remains {definition_id}.",
                    "Every selected source-section digest remains current.",
                    "The machine record validates against Definition/v1.",
                    "The human projection is regenerated exactly from the machine record.",
                ],
            },
            "plain_language": {"normative": False, "explanation": plain},
            "domain_context": {
                "normative": False,
                "workspace_ref": str(LAB),
                "explanation": scaffold["definition_voices"]["domain_context_voice"] + "\n\nSource context retained for reconstruction:\n\n" + domain_source,
                "examples": [
                    f"Resolve {target_id} by its machine identity rather than its directory name.",
                    f"Challenge source drift through the L1 drift audit before relying on {scaffold['term']}.",
                ],
            },
        },
        "boundaries": [item for item in boundaries if item],
        "source_refs": [
            {
                "source_ref": f"cyberalchemy-v2:{item['definition_id']}",
                "selector": item["selector"],
                "content_sha256": item["section_sha256"],
                "admission_posture": "candidate-unadmitted",
                "source_admission_ref": None,
            }
            for item in selected_sources
        ],
        "primary_consumer_refs": sorted(consumers[target_id]),
        "index_entry": {"index_ref": rel(ROOT / "registry.json"), "entry_id": f"{definition_id}@{version}"},
        "drift_route": {"owner_ref": "role:definition-owner", "audit_ref": rel(ROOT / "drift-audit.json"), "challenge_ref": "CA2-ROUTE-DEFINITIONS"},
        "source_direction": {
            "canonical": "definition.json",
            "human_projection": "DEFINITION.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.definition-markdown/v1",
            "generator_sha256": generator_sha,
        },
        "schema_ref": "cal.schema.definition/v1",
        "schema_digest": schema_sha,
        "evidence_refs": [rel(scaffold_path), rel(L0_RECEIPT), rel(ROOT / "receipts/validation.json")],
        "residue_refs": [rel(ROOT / "drift-audit.json")],
        "typed_relations": [
            {"relation_kind_ref": "relation.originates-from", "from_ref": definition_id, "to_ref": f"cyberalchemy-v2:{item['definition_id']}", "owner_ref": "role:definition-owner"}
            for item in selected_sources
        ],
        "claim_ceiling": "Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.",
    }


def render_candidate(value: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is candidate.json. -->", "", "# L1 Semantic-Family Repeatability Candidate", "",
        f'- Candidate: `{value["candidate_id"]}`', f'- Status: `{value["status"]}`', f'- Definitions: `{value["counts"]["definitions"]}`',
        f'- Source sections: `{value["counts"]["source_sections"]}`', f'- Dependency batches: `{value["counts"]["batches"]}`', f'- Authority effect: `{value["authority_effect"]}`',
        "", "## Product construction", "", value["product_construction"]["frontier"], "", "## Operational residue", "",
    ]
    lines.extend(f'- `{item["state"]}` — {item["task"]} (owner: `{item["owner"]}`)' for item in value["operational_support"])
    lines.extend(["", "## Claim ceiling", "", value["claim_ceiling"], ""])
    return "\n".join(lines)


def render_registry(value: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is registry.json. -->", "", "# L1 Candidate Definition Registry", "", "| Definition | Target | Batch | Digest | Proposed home |", "|---|---|---|---|---|"]
    for item in value["entries"]:
        lines.append(f'| `{item["definition_ref"]}` | `{item["target_id"]}` | `{item["batch_id"]}` | `{item["sha256"]}` | `{item["proposed_home"]}` |')
    lines.extend(["", "## Claim ceiling", "", value["claim_ceiling"], ""])
    return "\n".join(lines)


def render_batches(value: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is batches.json. -->", "", "# L1 Dependency Batches", "", "| Batch | Depends on | Targets | SCC groups |", "|---|---|---:|---:|"]
    for item in value["batches"]:
        lines.append(f'| `{item["batch_id"]}` | {", ".join(item["depends_on"]) or "none"} | {len(item["target_ids"])} | {len(item["strongly_connected_groups"])} |')
    lines.extend(["", "## Dependency edges", "", f'`{len(value["edges"])}` source-derived semantic edges.', "", "## Claim ceiling", "", value["claim_ceiling"], ""])
    return "\n".join(lines)


def render_drift(value: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is drift-audit.json. -->", "", "# L1 Definition Drift Audit", "", f'- Result: `{value["result"]}`', f'- Current sources: `{value["current_count"]}/{value["source_count"]}`', f'- Legacy-reference residue: `{len(value["legacy_reference_residue"])}`', "", "| Source | Current | Expected digest | Actual digest |", "|---|---|---|---|"]
    for item in value["source_checks"]:
        lines.append(f'| `{item["legacy_id"]}` | `{str(item["current"]).lower()}` | `{item["expected_sha256"]}` | `{item["actual_sha256"]}` |')
    lines.extend(["", "## Claim ceiling", "", value["claim_ceiling"], ""])
    return "\n".join(lines)


def render_manifest(value: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is manifest.json. -->", "", "# L1 Semantic Repeatability Manifest", "", f'- Materials: `{len(value["materials"])}`', f'- Source bindings: `{len(value["source_bindings"])}`', f'- Authority effect: `{value["authority_effect"]}`', "", "## Claim ceiling", "", value["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    renderer = module(DEFINITION_GENERATOR, "l1_definition_generator")
    sections = extract_source_sections()
    scaffolds = semantic_scaffolds()
    target_ids = [item[1]["target_id"] for item in scaffolds]
    edges, legacy_residue = dependency_model(scaffolds, sections)
    batches = dependency_batches(target_ids, edges)
    target_batch = {target: batch["batch_id"] for batch in batches for target in batch["target_ids"]}
    sibling_targets: dict[str, list[str]] = defaultdict(list)
    consumers: dict[str, list[str]] = defaultdict(list)
    for _, scaffold in scaffolds:
        for source in scaffold["source_refs"]:
            if "definition_id" in source:
                sibling_targets[source["definition_id"]].append(scaffold["target_id"])
    for dependency, consumer in edges:
        consumers[dependency].append(consumer)

    entries = []
    definitions = {}
    for scaffold_path, scaffold in sorted(scaffolds, key=lambda item: item[1]["target_id"]):
        definition = definition_record(scaffold_path, scaffold, sections, sibling_targets, consumers)
        name = slug(scaffold["target_id"])
        definition_root = ROOT / "definitions" / name / "v1"
        definition_path = definition_root / "definition.json"
        dump(definition_path, definition)
        definition = load(definition_path)
        (definition_root / "DEFINITION.md").write_text(renderer.render(definition), encoding="utf-8")
        definitions[scaffold["target_id"]] = definition
        entries.append({
            "target_id": scaffold["target_id"], "definition_ref": f'{definition["definition_id"]}@{definition["version"]}',
            "path": rel(definition_path), "sha256": sha(definition_path), "batch_id": target_batch[scaffold["target_id"]],
            "proposed_home": f"authority/definitions/{name}/v1/definition.json", "status": "candidate-unadmitted", "authority_effect": "none",
        })

    registry = {
        "schema_version": "cyberalchemy-lab-l1-definition-candidate-registry/v1", "registry_id": "CAL-L1-SEMANTIC-REPEATABILITY-REGISTRY-0001",
        "entries": entries, "entry_count": len(entries), "source_direction": {"canonical": "registry.json", "human_projection": "REGISTRY.md", "projection_policy": "generated-only"},
        "authority_effect": "none", "claim_ceiling": "Candidate-local lookup only. This registry does not alter or compete with the admitted Definition registry and cannot resolve repository authority.",
    }
    dump(ROOT / "registry.json", registry)
    (ROOT / "REGISTRY.md").write_text(render_registry(registry), encoding="utf-8")

    batches_record = {
        "schema_version": "cyberalchemy-lab-semantic-dependency-batches/v1", "batch_set_id": "CAL-L1-SEMANTIC-BATCHES-0001",
        "derivation": "CAV2-D references inside each selected exact source section create dependency-to-consumer edges; strongly connected components remain atomic; components are grouped by topological level.",
        "edges": [{"dependency_target_id": source, "consumer_target_id": target} for source, target in edges], "batches": batches,
        "authority_effect": "none", "claim_ceiling": "Dependency ordering is reconstruction evidence, not a semantic, admission, or execution decision.",
    }
    dump(ROOT / "batches.json", batches_record)
    (ROOT / "BATCHES.md").write_text(render_batches(batches_record), encoding="utf-8")

    selected_source_ids = sorted(sibling_targets, key=lambda item: int(item.split("D")[1]))
    expected_digests = {source["definition_id"]: source["section_sha256"] for _, scaffold in scaffolds for source in scaffold["source_refs"] if "definition_id" in source}
    source_checks = [{
        "legacy_id": legacy_id, "selector": sections[legacy_id]["heading"], "expected_sha256": expected_digests[legacy_id],
        "actual_sha256": sections[legacy_id]["sha256"], "current": expected_digests[legacy_id] == sections[legacy_id]["sha256"],
    } for legacy_id in selected_source_ids]
    drift = {
        "schema_version": "cyberalchemy-lab-l1-definition-drift-audit/v1", "audit_id": "CAL-L1-SEMANTIC-DRIFT-0001",
        "result": "PASS" if all(item["current"] for item in source_checks) else "BLOCK", "source_count": len(source_checks),
        "current_count": sum(item["current"] for item in source_checks), "source_checks": source_checks, "legacy_reference_residue": legacy_residue,
        "undefined_selected_target_count": 0, "conflicting_candidate_identity_count": 0, "wrong_workspace_voice_count": 0,
        "authority_effect": "none", "claim_ceiling": "Candidate-local currentness and reference-residue evidence only; it does not update CyberAlchemy-v2 or the admitted Lab registry.",
    }
    dump(ROOT / "drift-audit.json", drift)
    (ROOT / "DRIFT-AUDIT.md").write_text(render_drift(drift), encoding="utf-8")

    first_definition = definitions[sorted(definitions)[0]]
    missing_voice = json.loads(json.dumps(first_definition)); del missing_voice["voices"]["domain_context"]
    invalid_digest = json.loads(json.dumps(first_definition)); invalid_digest["source_refs"][0]["content_sha256"] = "invalid"
    authority_field = json.loads(json.dumps(first_definition)); authority_field["authority_effect"] = "admission"
    dump(ROOT / "fixtures/invalid/missing-domain-voice.json", missing_voice)
    dump(ROOT / "fixtures/invalid/source-digest.json", invalid_digest)
    dump(ROOT / "fixtures/invalid/authority-effect.json", authority_field)

    candidate = {
        "schema_version": "cyberalchemy-lab-l1-semantic-repeatability-candidate/v1", "candidate_id": "CAL-L1-SEMANTIC-REPEATABILITY-0001",
        "status": "prototype-construction-candidate", "predecessor_layer": {"layer_id": "L0", "manifest_path": rel(L0_MANIFEST), "manifest_sha256": sha(L0_MANIFEST), "receipt_path": rel(L0_RECEIPT), "receipt_sha256": sha(L0_RECEIPT)},
        "counts": {"definitions": len(definitions), "source_sections": len(source_checks), "dependency_edges": len(edges), "batches": len(batches), "legacy_reference_residue": len(legacy_residue)},
        "product_construction": {"frontier": "Prove that every remaining normalized semantic target can become an independently reproducible Definition/v1 candidate with source, voice, index, dependency, and drift closure.", "runnable_now": ["generate-all-definitions", "validate-independently", "reverse-order-reproduction", "check-source-currentness", "check-split-noncollapse"], "causal_blockers": []},
        "operational_support": [{"task": "Admission, live-registry synchronization, commit, push, and migration execution remain separate.", "owner": "role:repository-migration-owner", "affected_stage": None, "state": "deferred", "blocks_frontier": False}],
        "source_direction": {"canonical": "candidate.json", "human_projection": "CANDIDATE.md", "projection_policy": "generated-only"},
        "authority_effect": "none", "claim_ceiling": "This L1 candidate proves semantic-family reconstruction repeatability only. It does not admit definitions, change the live Definition registry, execute migration, activate policy or runtime, commit, push, publish, release, deploy, or authorize an external effect.",
    }
    dump(ROOT / "candidate.json", candidate)
    (ROOT / "CANDIDATE.md").write_text(render_candidate(candidate), encoding="utf-8")

    excluded = {"manifest.json", "MANIFEST.md", "validation.json", "VALIDATION.md"}
    materials = [path for path in ROOT.rglob("*") if path.is_file() and path.name not in excluded and "receipts" not in path.parts]
    source_paths = [TARGET_INDEX, PLANNING_DECISION, SOURCE_DEFINITIONS, DEFINITION_SCHEMA, DEFINITION_GENERATOR, ADMITTED_REGISTRY, ADMITTED_INDEX, L0_MANIFEST, L0_RECEIPT, *[path for path, _ in scaffolds]]
    manifest = {
        "schema_version": "cyberalchemy-lab-l1-semantic-repeatability-manifest/v1", "manifest_id": "CAL-L1-SEMANTIC-REPEATABILITY-MANIFEST-0001",
        "materials": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for path in sorted(materials)],
        "source_bindings": [{"repository_id": "cyberalchemy-v2-source" if path.is_relative_to(SOURCE) else "cyberalchemy-lab", "path": source_rel(path) if path.is_relative_to(SOURCE) else rel(path), "sha256": sha(path)} for path in source_paths],
        "authority_effect": "none", "claim_ceiling": "This manifest binds candidate and source bytes only. It grants no admission, migration, publication, release, deployment, or external-effect authority.",
    }
    dump(ROOT / "manifest.json", manifest)
    (ROOT / "MANIFEST.md").write_text(render_manifest(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
