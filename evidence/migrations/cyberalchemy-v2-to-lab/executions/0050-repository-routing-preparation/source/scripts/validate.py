#!/usr/bin/env python3
"""Validate the CyberAlchemy-v2-only repository route package."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parent.parent  # logical local citation base, not the umbrella
_LAYOUT_SPEC = importlib.util.spec_from_file_location("router_layout", PACKAGE_ROOT / "scripts/layout.py")
_LAYOUT_MODULE = importlib.util.module_from_spec(_LAYOUT_SPEC)
_LAYOUT_SPEC.loader.exec_module(_LAYOUT_MODULE)
LAYOUT = _LAYOUT_MODULE.Layout()
resolve_ref = LAYOUT.resolve_ref
SCHEMA_PATH = PACKAGE_ROOT / "schemas/agent-router.schema.json"
ROUTES_PATH = PACKAGE_ROOT / "routes.json"
AGENTS_PATH = resolve_ref(LAYOUT.agents_ref)
SOURCE_MAP_PATH = resolve_ref("cyberAlchemy-v2/SOURCE-MAP.md")

EXPECTED_ROUTE_IDS = {
    "CA2-ROUTE-ENTRY",
    "CA2-ROUTE-LOCATE",
    "CA2-ROUTE-DOMAINSPEC-CORE",
    "CA2-ROUTE-RECENT",
    "CA2-ROUTE-UNDERSTAND",
    "CA2-ROUTE-RESEARCH",
    "CA2-ROUTE-DEFINE",
    "CA2-ROUTE-PLAN",
    "CA2-ROUTE-IMPLEMENT",
    "CA2-ROUTE-DEFINITIONS",
    "CA2-ROUTE-GOVERNANCE",
    "CA2-ROUTE-VALIDATE",
    "CA2-ROUTE-ONTOLOGY",
    "CA2-ROUTE-DELEGATE",
    "CA2-ROUTE-SESSION",
    "CA2-ROUTE-PUBLISH",
    "CA2-ROUTE-PREVIEW",
    "CA2-ROUTE-AMBIGUOUS",
}

FORBIDDEN_ROOT_ROUTE_PATTERNS = {
    "legacy intent lifecycle route": r"\binvoke\b",
    "legacy bounded execution route": r"\btask-session\b",
    "legacy dispatch specification route": r"\bdispatch-spec\b",
    "legacy orchestration route": r"\borchestrate\b",
    "legacy definitions route": r"\bdefinitions-governance\b",
    "legacy preview route": r"\bhtml-preview-server\b",
    "legacy session route": r"\bclose-session\b",
    "legacy registration route": r"\bregister-dispatch\b",
    "legacy delegation strategy route": r"\bdomainspec-subagents-strategy\b",
    "legacy decision route": r"\bdecision-gate\b",
    "legacy constitution route": r"\bconstitution-governance\b",
    "legacy discipline route": r"\bdiscipline-governance\b",
    "legacy ontology route": r"\bontology-vault\b",
    "legacy UX evidence route": r"\bux-evidence-validator\b",
    "generated Codex skill route": r"\.agents/skills",
    "generated Claude skill route": r"\.claude/skills",
    "legacy command resolver": r"tools/arcanum",
}

EXPECTED_SEMANTIC_BINDING_IDS = {
    "CA2-ROUTING-BIND-CAV2-D65",
    "CA2-ROUTING-BIND-CAV2-D67",
    "CA2-ROUTING-BIND-PRODUCT-CAPABILITY",
    "CA2-ROUTING-BIND-BUSINESS-ONTOLOGY",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def schema_errors(instance: Any, schema: dict[str, Any], ref: str, label: str) -> list[str]:
    wrapper = copy.deepcopy(schema)
    wrapper["$ref"] = ref
    return [
        f"{label}.{'.'.join(str(part) for part in error.path) or '$'}: {error.message}"
        for error in sorted(Draft202012Validator(wrapper).iter_errors(instance), key=lambda item: list(item.path))
    ]


def heading_section_bytes(path: Path, selector: str) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.rstrip("\r\n") == selector), None)
    if start is None:
        raise ValueError(f"selector not found: {selector}")
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return "".join(lines[start:end]).encode()


def validate_semantic_bindings(errors: list[str]) -> list[dict[str, Any]]:
    node = load_json(PACKAGE_ROOT / "domainspec/nodes/cyberalchemy-route-resolution.json")
    bindings = node.get("body", {}).get("semantic_bindings", [])
    if not isinstance(bindings, list):
        errors.append("DomainSpec route rule semantic bindings must be an array")
        return []
    ids = [item.get("id") for item in bindings if isinstance(item, dict)]
    if set(ids) != EXPECTED_SEMANTIC_BINDING_IDS or len(ids) != len(EXPECTED_SEMANTIC_BINDING_IDS):
        errors.append("DomainSpec route rule must bind the exact D65, D67, Product Capability, and business ontology inputs")
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        binding_id = str(binding.get("id"))
        try:
            path = resolve_ref(str(binding.get("path", "")))
            path.relative_to(LAYOUT.local_root)
        except ValueError:
            errors.append(f"semantic binding escapes the repository: {binding_id}")
            continue
        try:
            if binding.get("scope_kind") == "whole-file" and binding.get("selector") is None:
                selected = path.read_bytes()
            elif binding.get("scope_kind") == "heading-section" and isinstance(binding.get("selector"), str):
                selected = heading_section_bytes(path, binding["selector"])
            else:
                errors.append(f"semantic binding scope is invalid: {binding_id}")
                continue
        except (OSError, ValueError) as exc:
            errors.append(f"semantic binding is not evaluable: {binding_id}: {exc}")
            continue
        actual = sha256_bytes(selected)
        if actual != binding.get("sha256"):
            errors.append(f"semantic binding drift: {binding_id}: expected {binding.get('sha256')}, got {actual}")
    return bindings


def validate_product_capability(record: dict[str, Any], ontology: dict[str, Any], errors: list[str]) -> None:
    schema = copy.deepcopy(load_json(resolve_ref("cyberAlchemy-v2/capability/schemas/capability.schema.json")))
    schema["$defs"]["productCapability"]["properties"]["schema_ref"]["const"] = (
        "../capability/schemas/capability.schema.json#/$defs/productCapability"
    )
    errors.extend(schema_errors(record, schema, "#/$defs/productCapability", "product capability"))

    support = load_json(PACKAGE_ROOT / "product-capability-support.json")
    support_ids = {item.get("id") for item in support.get("records", []) if isinstance(item, dict)}
    referenced = set(record.get("input_contract_refs", []))
    referenced |= set(record.get("output_contract_refs", []))
    referenced |= set(record.get("context_policy_refs", []))
    referenced |= set(record.get("realization_binding_refs", []))
    referenced.add(record.get("obligation_registry_ref"))
    missing_support = sorted(ref for ref in referenced if ref not in support_ids)
    if missing_support:
        errors.append(f"product capability support refs do not resolve: {missing_support}")

    residue_ids = {item.get("id") for item in support.get("residue", []) if isinstance(item, dict)}
    missing_residue = sorted(
        ref for ref in record.get("lifecycle_posture", {}).get("residue_refs", []) if ref not in residue_ids
    )
    if missing_residue:
        errors.append(f"product capability residue refs do not resolve: {missing_residue}")

    node_ids = {item.get("id") for item in ontology.get("nodes", []) if isinstance(item, dict)}
    business_refs = {
        record.get("product_ref"),
        record.get("business_ontology_ref"),
        *record.get("outcome_refs", []),
        *record.get("participant_refs", []),
        *record.get("consumer_refs", []),
    }
    missing_business = sorted(ref for ref in business_refs if ref not in node_ids)
    if missing_business:
        errors.append(f"product capability business refs do not resolve: {missing_business}")

    evidence_refs = set(record.get("evidence_refs", []))
    owner_refs = {
        ref
        for owner_route in record.get("owner_routes", [])
        if isinstance(owner_route, dict)
        for ref in owner_route.get("source_refs", [])
    }
    if not owner_refs.issubset(evidence_refs):
        errors.append(f"owner routes contain unregistered evidence refs: {sorted(owner_refs - evidence_refs)}")


def validate_ontology(ontology: dict[str, Any], errors: list[str]) -> None:
    node_ids = [item.get("id") for item in ontology.get("nodes", []) if isinstance(item, dict)]
    if len(node_ids) != len(set(node_ids)):
        errors.append("business ontology node ids must be unique")
    relation_ids: set[str] = set()
    known = set(node_ids)
    for relation in ontology.get("relations", []):
        if not isinstance(relation, dict):
            continue
        relation_id = str(relation.get("id"))
        if relation_id in relation_ids:
            errors.append(f"duplicate business ontology relation id: {relation_id}")
        relation_ids.add(relation_id)
        if relation.get("source") not in known or relation.get("target") not in known:
            errors.append(f"business ontology relation endpoint does not resolve: {relation_id}")


def validate_root_agents(text: str, errors: list[str], mode: str | None = None) -> None:
    mode = mode or LAYOUT.mode
    required = [
        "# CyberAlchemy-v2 Agent Entry Router",
        "Every request begins at `CA2-ROUTE-ENTRY`",
        "cyberAlchemy-v2/agent-routing/routes.json",
        "Ontology-runtime enforcement suspension",
        "not a mandatory repository prerequisite",
        "fallbacks",
        "CAV2-D65",
        "CA2-ROUTE-LOCATE",
        "cyberAlchemy-v2/agent-routing/project-index.json",
        "CA2-ROUTE-RECENT",
    ]
    if mode == "sibling":
        required = [marker.replace("# CyberAlchemy-v2 Agent Entry Router", "# CyberAlchemy v2 Agent Instructions")
                    .replace("cyberAlchemy-v2/agent-routing/", "agent-routing/") for marker in required]
        required.append("CA2-ROUTE-DOMAINSPEC-CORE")
        required.extend(["are.mjs decide route", "agent-routing/capabilities/are-cli/README.md"])
    for marker in required:
        if marker not in text:
            errors.append(f"root AGENTS.md is missing required router marker: {marker}")
    # Local authority-map references are evidence, not route directives. Keep
    # instruction injection checks on every line except the exact read-model link.
    checked_text = text
    if mode == "sibling":
        checked_text = checked_text.replace(
            "- Treat [../.arcanum/inventory/](../.arcanum/inventory/) and\n"
            "  [../.arcanum/ontology-vault/](../.arcanum/ontology-vault/) as read models and\n"
            "  candidate maps, not promoted authority.", "read-model declaration", 1
        )
    for label, pattern in FORBIDDEN_ROOT_ROUTE_PATTERNS.items():
        if re.search(pattern, checked_text, flags=re.IGNORECASE):
            errors.append(f"root AGENTS.md contains forbidden {label}")


def validate_source_map(text: str, errors: list[str]) -> None:
    match = re.search(r"(?ms)^## First Extraction Targets\n(.*?)(?=^## )", text)
    if match is None:
        errors.append("CyberAlchemy-v2 SOURCE-MAP lacks the First Extraction Targets section")
        return
    section = match.group(1)
    if "cyberAlchemy-v2/agent-routing/routes.json" not in section:
        errors.append("CyberAlchemy-v2 SOURCE-MAP does not bind owner routes to the route registry")
    if "Mandatory ontology-runtime gating is suspended" not in section:
        errors.append("CyberAlchemy-v2 SOURCE-MAP does not record the ontology enforcement suspension")
    for label, pattern in FORBIDDEN_ROOT_ROUTE_PATTERNS.items():
        if re.search(pattern, section, flags=re.IGNORECASE):
            errors.append(f"CyberAlchemy-v2 SOURCE-MAP owner routes contain forbidden {label}")


def validate_routes(registry: dict[str, Any], errors: list[str]) -> None:
    routes = registry.get("routes", [])
    if not isinstance(routes, list):
        return
    route_ids = [item.get("route_id") for item in routes if isinstance(item, dict)]
    if set(route_ids) != EXPECTED_ROUTE_IDS or len(route_ids) != len(EXPECTED_ROUTE_IDS):
        errors.append("route registry must contain the exact non-duplicated CyberAlchemy-v2 objective set")
    if route_ids and route_ids[0] != "CA2-ROUTE-ENTRY":
        errors.append("CA2-ROUTE-ENTRY must be the first route")

    objectives: set[str] = set()
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_id = str(route.get("route_id"))
        objective = str(route.get("objective"))
        if objective in objectives:
            errors.append(f"duplicate route objective: {objective}")
        objectives.add(objective)
        if route.get("fallback_route") is not None:
            errors.append(f"route fallback must remain null: {route_id}")
        authority_root = str(route.get("authority_root", ""))
        if authority_root != "cyberAlchemy-v2" and not authority_root.startswith("cyberAlchemy-v2/"):
            errors.append(f"route authority is outside CyberAlchemy-v2: {route_id}")
        try:
            if not resolve_ref(authority_root).is_dir():
                errors.append(f"route authority root does not exist: {route_id}: {authority_root}")
        except ValueError as exc:
            errors.append(f"unsafe route authority root: {route_id}: {exc}")
        for path_text in route.get("read_first", []):
            if path_text.startswith(("arcanum/", ".agents/", ".claude/")):
                errors.append(f"route read_first contains a forbidden routing surface: {route_id}: {path_text}")
            try:
                if not resolve_ref(path_text).is_file():
                    errors.append(f"route read_first target does not exist: {route_id}: {path_text}")
            except ValueError as exc:
                errors.append(f"unsafe route read_first target: {route_id}: {exc}")
        if route.get("execution_mode") == "blocked-until-capability" and route.get("lifecycle_state") != "blocked":
            errors.append(f"blocked execution mode must remain lifecycle blocked: {route_id}")
        if route.get("lifecycle_state") == "blocked" and not route.get("blockers"):
            errors.append(f"blocked route must name a causal blocker: {route_id}")

    ontology_routes = [item for item in routes if isinstance(item, dict) and item.get("route_id") == "CA2-ROUTE-ONTOLOGY"]
    if len(ontology_routes) != 1:
        errors.append("direct ontology runtime route must occur exactly once")
    else:
        route = ontology_routes[0]
        if route.get("authority_root") != "cyberAlchemy-v2/implementation/ontology-runtime":
            errors.append("direct ontology route authority root is not the ontology runtime")
        expected_reads = {
            "cyberAlchemy-v2/implementation/ontology-runtime/profile.json",
            "cyberAlchemy-v2/implementation/ontology-runtime/registry.json",
            "cyberAlchemy-v2/implementation/ontology-runtime/README.md",
        }
        if set(route.get("read_first", [])) != expected_reads:
            errors.append("direct ontology route read_first set is not exact")
        if route.get("write_ceiling") != "none; direct runtime operations are read-only and emit JSON to stdout":
            errors.append("direct ontology route exceeds its read-only write ceiling")
    route_by_id = {
        item.get("route_id"): item for item in routes if isinstance(item, dict)
    }
    if "CA2-ROUTE-ONTOLOGY" not in " ".join(route_by_id.get("CA2-ROUTE-UNDERSTAND", {}).get("excludes", [])):
        errors.append("understand route does not exclude direct registered ontology operations")
    if "CA2-ROUTE-ONTOLOGY" not in " ".join(route_by_id.get("CA2-ROUTE-VALIDATE", {}).get("excludes", [])):
        errors.append("validate route does not exclude registered ontology validation")
    sibling = route_by_id.get("CA2-ROUTE-DOMAINSPEC-CORE", {})
    if sibling.get("read_first") != ["cyberAlchemy-v2/agent-routing/DOMAINSPEC-CORE-INDEX.md"]:
        errors.append("domainspec-core route must read its exact local inventory")
    if sibling.get("authority_root") != "cyberAlchemy-v2/agent-routing" or sibling.get("execution_mode") != "native-inline":
        errors.append("domainspec-core lookup must retain local routing authority and inline execution")
    if sibling.get("write_ceiling") != "none; read-only navigation in the exact ../domainspec-core checkout; no submodule initialization or runtime effects":
        errors.append("domainspec-core lookup exceeds its read-only boundary")
    if "CA2-ROUTE-DOMAINSPEC-CORE" not in " ".join(route_by_id.get("CA2-ROUTE-LOCATE", {}).get("excludes", [])):
        errors.append("local lookup must exclude explicit domainspec-core scope")
    lookup = route_by_id.get("CA2-ROUTE-LOCATE", {})
    if lookup.get("read_first") != [
        "cyberAlchemy-v2/agent-routing/project-index.json",
        "cyberAlchemy-v2/agent-routing/PROJECT-LOOKUP.md",
    ]:
        errors.append("project lookup read_first set is not exact")
    if lookup.get("write_ceiling") != "none; source-location lookup only" or lookup.get("execution_mode") != "native-inline":
        errors.append("project lookup must remain read-only native lookup")
    for route_id in ["CA2-ROUTE-UNDERSTAND", "CA2-ROUTE-RESEARCH"]:
        if "CA2-ROUTE-LOCATE" not in " ".join(route_by_id.get(route_id, {}).get("excludes", [])):
            errors.append(f"{route_id} does not exclude source-location lookup")


def validate_project_index(errors: list[str]) -> None:
    spec = importlib.util.spec_from_file_location("project_citation_lookup", PACKAGE_ROOT / "scripts/locate.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors.extend(module.index_errors(load_json(PACKAGE_ROOT / "project-index.json")))


CONSTRUCTION_FILES = [
    "DOMAINSPEC-CORE-INDEX.md", "scripts/layout.py", "package.json", "package-lock.json",
    "tests/test_domainspec_core_route.py", "tests/test_layout.py", "LAYOUT.md",
    "README.md", "ROUTER.md", "schemas/agent-router.schema.json",
    "tests/test_negative_mutations.py", "tests/test_project_lookup.py",
    "capabilities/are-cli/PLAN.md",
    "capabilities/are-cli/EVENT-BINDING.md",
    "capabilities/are-cli/GATEWAY-CONTINUITY.md",
    "capabilities/are-cli/NATIVE-GATEWAY.md",
    "../implementation/agent-reasoning-engine/src/hook-callback-bridge.mjs",
    "../implementation/agent-reasoning-engine/test/hook-callback-bridge.test.mjs",
    "../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/backend.mjs",
    "../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/test/gateway.test.mjs",
    "../implementation/agent-reasoning-engine/src/gateway-session-client.mjs",
    "../implementation/agent-reasoning-engine/test/gateway-session-client.test.mjs",
    "../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/src/gateway-client.mjs",
    "../implementation/agent-reasoning-engine/src/hook-event-session.mjs",
    "../implementation/agent-reasoning-engine/test/hook-event-session.test.mjs",
    "capabilities/are-cli/NATIVE-HOST-TEST.md",
    "../implementation/agent-reasoning-engine/scripts/test-native-prompt-hook.mjs",
    "capabilities/are-cli/HOOKS.md",
    "../implementation/agent-reasoning-engine/src/prompt-hook.mjs",
    "../implementation/agent-reasoning-engine/bin/are-hook.mjs",
    "../implementation/agent-reasoning-engine/test/prompt-hook.test.mjs",
    "tests/test_are_cli.py",
    "../implementation/agent-reasoning-engine/product.json",
    "../implementation/agent-reasoning-engine/test/product.test.mjs",
    "capabilities/are-cli/README.md",
    "capabilities/are-cli/ontology.json",
    "capabilities/are-cli/request.schema.json",
    "capabilities/are-cli/result.schema.json",
    "capabilities/are-cli/route.example.json",
    "capabilities/are-cli/session-example.mjs",
    "../implementation/agent-reasoning-engine/src/decision-cli.mjs",
    "../implementation/agent-reasoning-engine/bin/are-decide.mjs",
    "../implementation/agent-reasoning-engine/bin/are.mjs",
    "../implementation/agent-reasoning-engine/test/decision-cli.test.mjs",
    "../implementation/agent-reasoning-engine/README.md",
    "../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/profiles/repository-v1.json",
    "../implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/profiles/interaction-learning-canary-v1.json",
]

RECENT_FILES = [
    "profile.json", "README.md", "definitions.json", "capability.json", "ontology.json",
    "recent-context.alch", "build.ts", "recent.py", "validate.py", "test_recent.py", "model.test.ts",
    "hooks.py", "test_hooks.py", "hooks-contract.json",
    "generated/build-receipt.json",
]


def validate_recent_context(registry: dict[str, Any], errors: list[str]) -> None:
    root = PACKAGE_ROOT / "capabilities/recent-context"
    route = next((r for r in registry.get("routes", []) if r.get("route_id") == "CA2-ROUTE-RECENT"), {})
    if route.get("read_first") != [
        "cyberAlchemy-v2/agent-routing/capabilities/recent-context/profile.json",
        "cyberAlchemy-v2/agent-routing/capabilities/recent-context/README.md",
        "cyberAlchemy-v2/agent-routing/project-index.json",
    ]:
        errors.append("recent-context route read_first set is not exact")
    if route.get("write_ceiling") != "none; recent-context query emits metadata to stdout only" or route.get("execution_mode") != "native-inline":
        errors.append("recent-context route must remain read-only query")
    if route.get("requires_user_authorization") is not False:
        errors.append("read-only recent-context query must not require mutation authority")
    session = next((r for r in registry.get("routes", []) if r.get("route_id") == "CA2-ROUTE-SESSION"), {})
    if session.get("lifecycle_state") != "blocked":
        errors.append("recent context cannot unblock durable session lifecycle")
    spec = importlib.util.spec_from_file_location("validate_recent_context", root / "validate.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors.extend(module.model_errors())


def validate_generated(errors: list[str], semantic_bindings: list[dict[str, Any]]) -> None:
    project = load_json(PACKAGE_ROOT / "domainspec/project.json")
    profile_path = PACKAGE_ROOT / "domainspec/development-profile.json"
    if project.get("language", {}).get("profile", {}).get("digest") != sha256_file(profile_path):
        errors.append("DomainSpec development profile digest drift")

    generated = PACKAGE_ROOT / "domainspec/generated"
    required = {
        "graph.json",
        "source-manifest.json",
        "SPEC.md",
        "markdown-view.json",
        "build-receipt.json",
        "system-ontology.json",
        "system-ontology-receipt.json",
    }
    missing = sorted(name for name in required if not (generated / name).is_file())
    if missing:
        errors.append(f"generated DomainSpec artifacts are missing: {missing}")
        return

    graph_path = generated / "graph.json"
    system_path = generated / "system-ontology.json"
    build_receipt = load_json(generated / "build-receipt.json")
    system = load_json(system_path)
    projection = load_json(generated / "system-ontology-receipt.json")
    contract = system.get("implementation_contract", {})
    if system.get("construction_inputs") != semantic_bindings:
        errors.append("generated system ontology does not preserve the exact semantic construction inputs")
    if build_receipt.get("source_set_digest") != system.get("source_set_digest"):
        errors.append("generated system ontology source-set binding drift")
    if system.get("source_graph_digest") != sha256_file(graph_path):
        errors.append("generated system ontology graph binding drift")
    if system.get("compiler", {}).get("projection_builder_sha256") != sha256_file(PACKAGE_ROOT / "scripts/build.ts"):
        errors.append("generated system ontology projection-builder binding drift")
    if contract.get("route_registry_sha256") != sha256_file(ROUTES_PATH):
        errors.append("generated system ontology route-registry binding drift")
    if contract.get("ontology_enforcement") != "suspended-pending-governed-rust-binding":
        errors.append("generated system ontology does not preserve the ontology enforcement suspension")
    if contract.get("validator_sha256") != sha256_file(Path(__file__).resolve()):
        errors.append("generated system ontology validator binding drift")
    if contract.get("root_instruction_sha256") != sha256_file(AGENTS_PATH):
        errors.append("generated system ontology root-instruction binding drift")
    if contract.get("source_map_sha256") != sha256_file(SOURCE_MAP_PATH):
        errors.append("generated system ontology source-map binding drift")
    if contract.get("fallback_policy") != "forbidden":
        errors.append("generated system ontology permits a routing fallback")
    expected_construction = {name: sha256_file(PACKAGE_ROOT / name) for name in CONSTRUCTION_FILES}
    if contract.get("construction_sources") != expected_construction:
        errors.append("generated system ontology construction-source bindings drift")
    if contract.get("root_instruction_ref") != LAYOUT.agents_ref or contract.get("checkout_layout") != LAYOUT.mode:
        errors.append("generated system ontology checkout layout binding drift")
    for field in ["compiler", "views"]:
        ref = f"projects/domainspec-v2/impl/tools/minted-project/{field}.ts"
        if system.get("compiler", {}).get(f"{field}_path") != ref or system.get("compiler", {}).get(f"{field}_sha256") != sha256_file(resolve_ref(ref)):
            errors.append(f"generated system ontology selected {field} binding drift")
    expected_recent = {name: sha256_file(PACKAGE_ROOT / "capabilities/recent-context" / name) for name in RECENT_FILES}
    if contract.get("recent_context_sources") != expected_recent:
        errors.append("generated system ontology recent-context source bindings drift")
    for field, relative in {
        "project_index_sha256": "project-index.json",
        "project_lookup_sha256": "scripts/locate.py",
        "project_lookup_contract_sha256": "PROJECT-LOOKUP.md",
    }.items():
        if contract.get(field) != sha256_file(PACKAGE_ROOT / relative):
            errors.append(f"generated system ontology project-lookup binding drift: {relative}")
    if projection.get("deterministic_runs") != 2 or not projection.get("equal_graph_bytes") or not projection.get("equal_system_ontology_bytes"):
        errors.append("generated system ontology lacks two-run determinism evidence")
    if projection.get("source_graph_digest") != sha256_file(graph_path):
        errors.append("projection receipt graph digest drift")
    if projection.get("system_ontology_digest") != sha256_file(system_path):
        errors.append("projection receipt system-ontology digest drift")
    if projection.get("status") != "candidate" or projection.get("profile_release_admission") != "not-granted":
        errors.append("unadmitted DomainSpec projection must remain an explicit candidate")


def verify_materialized_build(errors: list[str]) -> None:
    command = ["node", "--import", "tsx", str(PACKAGE_ROOT / "scripts/build.ts"), "--emit-json"]
    first = subprocess.run(command, cwd=PACKAGE_ROOT, capture_output=True, text=True, check=False)
    second = subprocess.run(command, cwd=PACKAGE_ROOT, capture_output=True, text=True, check=False)
    if first.returncode != 0 or second.returncode != 0:
        diagnostics = (first.stderr or second.stderr).strip().splitlines()
        errors.append(f"DomainSpec build replay failed: {diagnostics[-1] if diagnostics else 'unknown error'}")
        return
    if first.stdout != second.stdout:
        errors.append("DomainSpec build replay is non-deterministic")
        return
    try:
        artifacts = json.loads(first.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"DomainSpec build replay did not return JSON: {exc}")
        return
    generated = PACKAGE_ROOT / "domainspec/generated"
    expected_names = {"graph.json", "source-manifest.json", "SPEC.md", "markdown-view.json",
                      "build-receipt.json", "system-ontology.json", "system-ontology-receipt.json"}
    if not isinstance(artifacts, dict) or set(artifacts) != expected_names:
        errors.append("DomainSpec build replay artifact set is not exact")
        return
    for name, content in artifacts.items():
        if not (generated / name).is_file() or (generated / name).read_text(encoding="utf-8") != content:
            errors.append(f"materialized DomainSpec artifact is stale: {name}")


def material_digest() -> str:
    paths = [
        AGENTS_PATH,
        SOURCE_MAP_PATH,
        PACKAGE_ROOT / "README.md",
        PACKAGE_ROOT / "ROUTER.md",
        PACKAGE_ROOT / "profile.json",
        PACKAGE_ROOT / "routes.json",
        PACKAGE_ROOT / "project-index.json",
        PACKAGE_ROOT / "PROJECT-LOOKUP.md",
        PACKAGE_ROOT / "scripts/locate.py",
        PACKAGE_ROOT / "tests/test_project_lookup.py",
        PACKAGE_ROOT / "product-capability.json",
        PACKAGE_ROOT / "product-capability-support.json",
        PACKAGE_ROOT / "ontology.json",
        PACKAGE_ROOT / "schemas/agent-router.schema.json",
        PACKAGE_ROOT / "scripts/build.ts",
        PACKAGE_ROOT / "scripts/validate.py",
        PACKAGE_ROOT / "tests/test_negative_mutations.py",
        PACKAGE_ROOT / "domainspec/project.json",
        PACKAGE_ROOT / "domainspec/feature.json",
        PACKAGE_ROOT / "domainspec/development-profile.json",
        PACKAGE_ROOT / "domainspec/nodes/repository-agent-route.json",
        PACKAGE_ROOT / "domainspec/nodes/cyberalchemy-route-resolution.json",
        PACKAGE_ROOT / "domainspec/generated/graph.json",
        PACKAGE_ROOT / "domainspec/generated/source-manifest.json",
        PACKAGE_ROOT / "domainspec/generated/build-receipt.json",
        PACKAGE_ROOT / "domainspec/generated/system-ontology.json",
        PACKAGE_ROOT / "domainspec/generated/system-ontology-receipt.json",
    ]
    paths.extend(PACKAGE_ROOT / "capabilities/recent-context" / name for name in RECENT_FILES)
    paths.extend(PACKAGE_ROOT / name for name in CONSTRUCTION_FILES)
    payload = b"".join(("AGENTS.md" if path == AGENTS_PATH and LAYOUT.mode == "umbrella" else path.relative_to(REPOSITORY_ROOT).as_posix()).encode() + b"\0" + path.read_bytes() for path in paths if path.is_file())
    return sha256_bytes(payload)


def evaluate(
    registry: dict[str, Any] | None = None,
    *,
    agents_text: str | None = None,
    verify_generated_artifacts: bool = True,
    verify_build: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    schema = load_json(SCHEMA_PATH)
    profile = load_json(PACKAGE_ROOT / "profile.json")
    routes = registry if registry is not None else load_json(ROUTES_PATH)
    ontology = load_json(PACKAGE_ROOT / "ontology.json")
    product_capability = load_json(PACKAGE_ROOT / "product-capability.json")

    errors.extend(schema_errors(profile, schema, "#/$defs/profile", "profile"))
    errors.extend(schema_errors(routes, schema, "#/$defs/routeRegistry", "route registry"))
    errors.extend(schema_errors(ontology, schema, "#/$defs/businessOntology", "business ontology"))
    validate_routes(routes, errors)
    validate_project_index(errors)
    validate_recent_context(routes, errors)
    validate_ontology(ontology, errors)
    validate_product_capability(product_capability, ontology, errors)
    semantic_bindings = validate_semantic_bindings(errors)
    validate_root_agents(agents_text if agents_text is not None else AGENTS_PATH.read_text(encoding="utf-8"), errors)
    validate_source_map(SOURCE_MAP_PATH.read_text(encoding="utf-8"), errors)
    if verify_generated_artifacts:
        validate_generated(errors, semantic_bindings)
    if verify_build and not errors:
        verify_materialized_build(errors)

    route_items = routes.get("routes", []) if isinstance(routes, dict) else []
    blocked = sorted(
        item.get("route_id") for item in route_items if isinstance(item, dict) and item.get("lifecycle_state") == "blocked"
    )
    return {
        "schema_version": "cav2-agent-router-validation/v1",
        "status": "PASS" if not errors else "BLOCK",
        "route_count": len(route_items) if isinstance(route_items, list) else 0,
        "entry_route_id": routes.get("entry_route_id") if isinstance(routes, dict) else None,
        "blocked_routes": blocked,
        "fallback_policy": "forbidden",
        "ontology_enforcement": "suspended-pending-governed-rust-binding",
        "direct_public_subsystem_route_count": 0 if not any("forbidden" in item for item in errors) else None,
        "construction_status": "candidate",
        "domainspec_profile_admission": "not-granted",
        "authority_effect": "none",
        "material_digest": material_digest() if verify_generated_artifacts and not errors else None,
        "errors": errors,
        "claim_ceiling": "Local CyberAlchemy-v2 route closure only; no complete runtime replacement, DomainSpec or system-ontology admission, conformance, publication, release, deployment, or external effect.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-build", action="store_true")
    args = parser.parse_args()
    try:
        result = evaluate(verify_build=args.verify_build)
    except (OSError, ValueError) as exc:
        result = {
            "schema_version": "cav2-agent-router-validation/v1",
            "status": "BLOCK",
            "authority_effect": "none",
            "errors": [f"agent router package unavailable: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
