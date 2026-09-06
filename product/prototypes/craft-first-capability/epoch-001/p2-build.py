#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def selected_bytes(path: Path, selector: str) -> bytes:
    if selector == "whole-file":
        return path.read_bytes()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if selector.startswith("yaml-member:id=DS-D1.1"):
        out: list[str] = []
        active = False
        for line in lines:
            if line.startswith("  - id: DS-D1.1"):
                active = True
            elif active and line.startswith("  - id: DS-D1.2"):
                break
            if active:
                out.append(line)
        if not out:
            raise ValueError("DS-D1.1 YAML selector did not resolve")
        return "".join(out).encode("utf-8")
    if selector.startswith("heading:## DS-D1.1"):
        out = []
        active = False
        for line in lines:
            if line.startswith("## DS-D1.1 · Entity"):
                active = True
            elif active and line.startswith("## "):
                break
            if active:
                out.append(line)
        if not out:
            raise ValueError("DS-D1.1 Markdown selector did not resolve")
        return "".join(out).encode("utf-8")
    raise ValueError(f"unsupported selector: {selector}")


def render_record(title: str, data: dict[str, Any], canonical_name: str) -> str:
    lines = [
        f"<!-- GENERATED FILE: edit {canonical_name} or its declared upstream source and run p2-build.py. -->",
        "",
        f"# {title}",
        "",
        "> Generated human projection. The machine JSON remains canonical within this prototype epoch.",
        "",
    ]
    for key in ("capability_id", "ontology_id", "specification_id", "graph_id", "system_ontology_id", "implementation_id", "evidence_id", "stage_id", "status", "result", "authority_effect"):
        if key in data:
            lines.append(f"- {key.replace('_', ' ').title()}: `{data[key]}`")
    lines += ["", "## Machine projection", "", "```json", json.dumps(data, indent=2, sort_keys=True), "```"]
    if data.get("claim_ceiling"):
        lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_receipt(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: run p2-build.py. -->",
        "",
        "# CML09-P2 Validation",
        "",
        f"- Result: `{data['result']}`",
        f"- Stage state: `{data['required_stage_state']}`",
        f"- Checks: `{data['summary']['passed']}/{data['summary']['total']}`",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    lines += [f"| `{item['check_id']}` | `{item['result']}` |" for item in data["checks"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def run_cargo(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="cal-p2-cargo-") as target:
        env["CARGO_TARGET_DIR"] = target
        return subprocess.run(
            ["cargo", *args, "--manifest-path", str(ROOT / "implementation/Cargo.toml"), "--locked", "--offline"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )


def main() -> int:
    capability_path = ROOT / "product/product-capability.json"
    business_path = ROOT / "business/business-ontology.json"
    project_path = ROOT / "domainspec/project.json"
    capability = load(capability_path)
    business = load(business_path)
    project = load(project_path)

    graph = {
        "schema_version": "cyberalchemy-lab-compiled-graph-prototype/v1",
        "graph_id": "CAL-P2-GRAPH-DEFINITION-SNAPSHOT-CONSTRUCTION",
        "artifact_type": "compiled-graph-prototype",
        "prototype_epoch": "epoch-001",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "generated_from": {"path": "domainspec/project.json", "sha256": sha(project_path)},
        "nodes": [
            {"node_id": "CAL-P2-NODE-CAPABILITY", "kind": "product-capability-prototype", "ref": capability["capability_id"], "source_sha256": sha(capability_path)},
            {"node_id": "CAL-P2-NODE-BUSINESS-ONTOLOGY", "kind": "business-ontology-prototype", "ref": business["ontology_id"], "source_sha256": sha(business_path)},
            {"node_id": "CAL-P2-NODE-SOURCE-DS-D1-1", "kind": "selected-external-source", "ref": "DS-D1.1", "source_sha256": project["source_selections"][0]["selected_bytes_sha256"]},
            {"node_id": "CAL-P2-NODE-DEFINITION-WITNESS", "kind": "craft-definition-snapshot-witness", "ref": "DS-D1.1", "source_sha256": object_sha(project["definition_snapshot_witness"])},
        ],
        "relations": [
            {"source_ref": "CAL-P2-NODE-CAPABILITY", "relation_type": "requires_meaning_from", "target_ref": "CAL-P2-NODE-BUSINESS-ONTOLOGY", "posture": "compiled-prototype-relation"},
            {"source_ref": "CAL-P2-NODE-CAPABILITY", "relation_type": "selects_source", "target_ref": "CAL-P2-NODE-SOURCE-DS-D1-1", "posture": "compiled-prototype-relation"},
            {"source_ref": "CAL-P2-NODE-SOURCE-DS-D1-1", "relation_type": "materializes_as", "target_ref": "CAL-P2-NODE-DEFINITION-WITNESS", "posture": "compiled-prototype-relation"},
        ],
        "canonicality": "generated-prototype",
        "authority_effect": "none",
        "source_direction": {"canonical_upstream": "domainspec/project.json", "human_projection": "GRAPH.md", "generator": "p2-build.py"},
        "claim_ceiling": "Generated P2 graph evidence only; it is not an authored specification, semantic admission, or runtime authority.",
    }
    graph_path = ROOT / "compiled/graph.json"
    dump(graph_path, graph)

    system = {
        "schema_version": "cyberalchemy-lab-system-ontology-prototype/v1",
        "system_ontology_id": "CAL-P2-SYSTEM-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION",
        "artifact_type": "system-ontology-prototype",
        "prototype_epoch": "epoch-001",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "generated_from": {"path": "compiled/graph.json", "sha256": sha(graph_path)},
        "obligations": [
            {"obligation_id": "CAL-P2-OBLIGATION-STABLE-ID", "trace_ref": "CAL-P2-NODE-DEFINITION-WITNESS", "required_behavior": "Output preserves DS-D1.1 without renumbering."},
            {"obligation_id": "CAL-P2-OBLIGATION-EXACT-SOURCE", "trace_ref": "CAL-P2-NODE-SOURCE-DS-D1-1", "required_behavior": "Execution binds the selected DS-D1.1 source digest."},
            {"obligation_id": "CAL-P2-OBLIGATION-ENTITY-CRITERION", "trace_ref": "CAL-P2-NODE-DEFINITION-WITNESS", "required_behavior": "Output identifies Entity and its identity plus typedness criterion."},
            {"obligation_id": "CAL-P2-OBLIGATION-NO-AUTHORITY", "trace_ref": "CAL-P2-NODE-CAPABILITY", "required_behavior": "Output reports authority_effect none."},
        ],
        "implementation_contract": {
            "language": "Rust",
            "crate": "craft-p2-definition-snapshot",
            "expected_result_kind": "definition_snapshot_witness",
            "expected_legacy_id": "DS-D1.1",
            "expected_term": "Entity",
            "expected_authority_effect": "none"
        },
        "canonicality": "generated-prototype",
        "authority_effect": "none",
        "source_direction": {"canonical_upstream": "compiled/graph.json", "human_projection": "SYSTEM-ONTOLOGY.md", "generator": "p2-build.py"},
        "claim_ceiling": "Generated P2 system obligations only; validation proves only the selected smoke behavior and grants no conformance or operational authority.",
    }
    system_path = ROOT / "compiled/system-ontology.json"
    dump(system_path, system)
    system_digest = sha(system_path)

    expected_payload = {
        "authority_effect": "none",
        "capability_id": capability["capability_id"],
        "legacy_id": "DS-D1.1",
        "result_kind": "definition_snapshot_witness",
        "system_ontology_sha256": system_digest,
        "term": "Entity",
    }
    payload_text = json.dumps(expected_payload, sort_keys=True, separators=(",", ":"))
    obligations = [item["obligation_id"] for item in system["obligations"]]
    generated_contract = "\n".join([
        "// GENERATED FILE: edit upstream JSON and run ../p2-build.py.",
        f"pub const SYSTEM_ONTOLOGY_SHA256: &str = \"{system_digest}\";",
        f"pub const SMOKE_PAYLOAD: &str = r#\"{payload_text}\"#;",
        "pub const SYSTEM_ONTOLOGY: &str = include_str!(\"../../compiled/system-ontology.json\");",
        "",
        "pub fn verify_contract() -> bool {",
        f"    SYSTEM_ONTOLOGY.contains(\"{system['system_ontology_id']}\")",
        *[f"        && SYSTEM_ONTOLOGY.contains(\"{item}\")" for item in obligations],
        "        && SYSTEM_ONTOLOGY.contains(\"\\\"authority_effect\\\": \\\"none\\\"\")",
        "}",
        "",
        "pub fn smoke_payload() -> &'static str {",
        "    SMOKE_PAYLOAD",
        "}",
        "",
    ])
    generated_path = ROOT / "implementation/src/generated_contract.rs"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(generated_contract, encoding="utf-8")

    rustc_version = subprocess.run(["rustc", "--version"], text=True, capture_output=True, check=True).stdout.strip()
    cargo_version = subprocess.run(["cargo", "--version"], text=True, capture_output=True, check=True).stdout.strip()
    manifest = {
        "schema_version": "cyberalchemy-lab-implementation-prototype/v1",
        "implementation_id": "CAL-P2-RUST-DEFINITION-SNAPSHOT-CONSTRUCTION",
        "artifact_type": "implementation-prototype",
        "prototype_epoch": "epoch-001",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "status": "prototype",
        "input_binding": {"path": "compiled/system-ontology.json", "sha256": system_digest},
        "source_files": [
            {"path": "implementation/src/main.rs", "sha256": sha(ROOT / "implementation/src/main.rs"), "posture": "authored-implementation"},
            {"path": "implementation/src/generated_contract.rs", "sha256": sha(generated_path), "posture": "generated-system-binding"},
            {"path": "implementation/Cargo.toml", "sha256": sha(ROOT / "implementation/Cargo.toml"), "posture": "authored-package-manifest"},
            {"path": "implementation/Cargo.lock", "sha256": sha(ROOT / "implementation/Cargo.lock"), "posture": "locked-dependency-closure"},
        ],
        "tool_profile": {
            "posture": "provisional-host-toolchain",
            "rustc": rustc_version,
            "cargo": cargo_version,
            "dependencies": "rust-standard-library-only",
            "network": "forbidden",
            "platform_profile_formalization": "deferred-operational-support"
        },
        "obligation_refs": obligations,
        "runtime_activation": "not-requested",
        "authority_effect": "none",
        "source_direction": {"canonical": "manifest.json", "human_projection": "IMPLEMENTATION.md", "projection_policy": "generated-only", "generator": "../p2-build.py"},
        "claim_ceiling": "This Rust crate is a local P2 implementation prototype and smoke witness. It is not an activated Craft runtime, a conformance provider, a release, or operational authority.",
    }
    manifest_path = ROOT / "implementation/manifest.json"
    dump(manifest_path, manifest)

    cargo_test = run_cargo(["test", "--quiet"])
    cargo_run = run_cargo(["run", "--quiet"])
    stdout = cargo_run.stdout.strip()
    smoke_result = "PASS" if cargo_test.returncode == 0 and cargo_run.returncode == 0 and stdout == payload_text else "FAIL"
    smoke = {
        "schema_version": "cyberalchemy-lab-smoke-test-evidence/v1",
        "evidence_id": "CAL-P2-EVIDENCE-RUST-SMOKE",
        "artifact_type": "prototype-smoke-test-evidence",
        "prototype_epoch": "epoch-001",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "result": smoke_result,
        "system_ontology_binding": {"path": "compiled/system-ontology.json", "sha256": system_digest},
        "implementation_binding": {"path": "implementation/manifest.json", "sha256": sha(manifest_path)},
        "commands": ["cargo test --locked --offline --quiet", "cargo run --locked --offline --quiet"],
        "cargo_test_exit_code": cargo_test.returncode,
        "cargo_run_exit_code": cargo_run.returncode,
        "observed_stdout": stdout,
        "expected_stdout": payload_text,
        "observable_result": expected_payload,
        "network_effect": "none",
        "filesystem_effect": "temporary build target only; removed after each command",
        "authority_effect": "none",
        "source_direction": {"canonical": "smoke-test.json", "human_projection": "SMOKE-TEST.md", "projection_policy": "generated-only", "generator": "../p2-build.py"},
        "claim_ceiling": "PASS proves only that the exact local Rust prototype checks and reports the selected system obligations. It does not establish broad runtime conformance, product approval, activation, migration, or release readiness.",
    }
    smoke_path = ROOT / "evidence/smoke-test.json"
    dump(smoke_path, smoke)

    projections = {
        ROOT / "product/PRODUCT-CAPABILITY.md": render_record("Definition Snapshot Construction Product Capability Prototype", capability, "product-capability.json"),
        ROOT / "business/BUSINESS-ONTOLOGY.md": render_record("Definition Snapshot Construction Business Ontology Prototype", business, "business-ontology.json"),
        ROOT / "domainspec/PROJECT.md": render_record("Craft Definition Snapshot Construction Specification Prototype", project, "project.json"),
        ROOT / "compiled/GRAPH.md": render_record("Compiled Graph Prototype", graph, "graph.json"),
        ROOT / "compiled/SYSTEM-ONTOLOGY.md": render_record("System Ontology Prototype", system, "system-ontology.json"),
        ROOT / "implementation/IMPLEMENTATION.md": render_record("Rust Implementation Prototype", manifest, "manifest.json"),
        ROOT / "evidence/SMOKE-TEST.md": render_record("Rust Smoke-Test Evidence", smoke, "smoke-test.json"),
    }
    for path, content in projections.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    checks: list[dict[str, Any]] = []
    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("p1-receipt-current-and-passing", sha(LAB / capability["p1_binding"]["receipt_path"]) == capability["p1_binding"]["receipt_sha256"] and load(LAB / capability["p1_binding"]["receipt_path"])["result"] == "PASS", capability["p1_binding"])
    check("craft-product-binding-current", sha(Path(capability["product_binding"]["repository"]) / capability["product_binding"]["path"]) == capability["product_binding"]["sha256"], capability["product_binding"])
    check("product-feature-distinct-and-current", capability["capability_id"] != capability["product_feature_relation"]["feature_id"] and sha(Path(capability["product_feature_relation"]["repository"]) / capability["product_feature_relation"]["path"]) == capability["product_feature_relation"]["sha256"], capability["product_feature_relation"])
    check("explicit-no-context-posture", capability["context_posture"]["kind"] == project["context_posture"]["kind"] == "explicit-no-context" and project["context_posture"]["bounded_context_ref"] is None, project["context_posture"])
    check("business-capability-digest-closure", business["capability_binding"]["sha256"] == sha(capability_path), business["capability_binding"])
    input_results = [{"role": item["role"], "current": sha((ROOT / item["path"]) if (ROOT / item["path"]).is_file() else (LAB / item["path"])) == item["sha256"]} for item in project["input_bindings"]]
    check("specification-input-digest-closure", all(item["current"] for item in input_results), input_results)
    source_results = []
    for item in project["source_selections"]:
        path = Path(item["repository"]) / item["path"]
        selected = hashlib.sha256(selected_bytes(path, item["selector"])).hexdigest()
        whole = sha(path)
        source_results.append({"source_id": item["source_id"], "selected_current": selected == item["selected_bytes_sha256"], "whole_current": whole == item["whole_file_sha256"], "selected_actual": selected, "whole_actual": whole})
    check("exact-source-selection-currentness", all(item["selected_current"] and item["whole_current"] for item in source_results), source_results)
    check("recursion-stop-is-one-witness", project["recursion_stop"]["value"] == 1 and business["closure"]["selected_legacy_ids"] == ["DS-D1.1"], {"recursion_stop": project["recursion_stop"], "selected": business["closure"]["selected_legacy_ids"]})
    check("compiled-graph-traces-authored-specification", graph["generated_from"]["sha256"] == sha(project_path), graph["generated_from"])
    check("system-ontology-traces-graph", system["generated_from"]["sha256"] == sha(graph_path), system["generated_from"])
    check("implementation-traces-system-obligations", manifest["input_binding"]["sha256"] == system_digest and set(manifest["obligation_refs"]) == set(obligations) and system_digest in generated_contract, manifest["input_binding"])
    check("rust-tests-pass-offline-locked", cargo_test.returncode == 0, {"exit_code": cargo_test.returncode, "stderr": cargo_test.stderr})
    check("rust-smoke-result", smoke_result == "PASS", {"exit_code": cargo_run.returncode, "observed": stdout, "expected": payload_text, "stderr": cargo_run.stderr})
    records = [capability, business, project, graph, system, manifest, smoke]
    check("all-prototype-records-zero-authority", all(item.get("authority_effect") == "none" for item in records), [item.get("artifact_type") for item in records])
    projection_results = [{"path": str(path.relative_to(ROOT)), "current": path.read_text(encoding="utf-8") == content} for path, content in projections.items()]
    check("generated-human-projection-parity", all(item["current"] for item in projection_results), projection_results)

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-prototype-stage-validation/v1",
        "subject": "CAL-P2-DEFINITION-SNAPSHOT-CONSTRUCTION-VERTICAL",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "result": result,
        "required_stage_state": "TESTED_PROTOTYPE" if result == "PASS" else "NOT_EVALUABLE",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "product_capability_sha256": sha(capability_path),
            "business_ontology_sha256": sha(business_path),
            "authored_specification_sha256": sha(project_path),
            "compiled_graph_sha256": sha(graph_path),
            "system_ontology_sha256": system_digest,
            "implementation_manifest_sha256": sha(manifest_path),
            "smoke_test_sha256": sha(smoke_path),
            "projection_sha256": {str(path.relative_to(ROOT)): sha(path) for path in projections},
        },
        "product_construction_frontier": {
            "completed_evidence_stage": "product_business_domainspec_compiled_system_implementation_prototypes" if result == "PASS" else "ontology_scaffolds",
            "next_frontier_candidate": "tested_prototypes" if result == "PASS" else "product_business_domainspec_compiled_system_implementation_prototypes",
            "next_stage_id": "CML10-P3-ITERATE-AND-TEST-PROTOTYPE-SPINE" if result == "PASS" else "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
            "continuation_status": "runnable" if result == "PASS" else "blocked-by-p2-validation",
            "current_causal_blockers": [],
        },
        "operational_support": [
            {"task_id": "CAL-OP-FORMALIZE-RUST-PLATFORM-PROFILE", "state": "deferred", "owner_route": "role:platform-environment-owner", "applies_to_stage": "CML10-P3-ITERATE-AND-TEST-PROTOTYPE-SPINE", "blocking_basis": "not-required-for-local-p2-standard-library-proof"},
            {"task_id": "CAL-OP-TRACK-P2-IN-GIT", "state": "deferred", "owner_route": "CA2-ROUTE-PUBLISH", "applies_to_stage": None, "blocking_basis": "none"},
            {"task_id": "CAL-OP-MIGRATE-REMAINING-BACKEND-DEFINITIONS", "state": "deferred-product-construction", "owner_route": "role:craft-project-owner", "applies_to_stage": "CML10-P3-ITERATE-AND-TEST-PROTOTYPE-SPINE", "blocking_basis": "outside-minimum-p2-proof"},
        ],
        "claim_ceiling": "PASS proves one exact P2 end-to-end prototype from a selected DS-D1.1 source witness through capability, business meaning, authored Craft specification, generated graph, generated system obligations, and offline Rust smoke behavior. It does not admit definitions or ontology, select final context placement, prove the remaining twelve definitions, establish broad conformance, approve a product, activate a runtime, migrate consumers, or grant operational authority.",
    }
    receipt_path = ROOT / "receipts/p2-validation.json"
    dump(receipt_path, receipt)
    (ROOT / "receipts/P2-VALIDATION.md").write_text(render_receipt(receipt), encoding="utf-8")
    print(f"CML09_P2_THIN_VERTICAL={result}")
    print(f"STAGE_STATE={receipt['required_stage_state']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_STAGE={receipt['product_construction_frontier']['next_stage_id']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
