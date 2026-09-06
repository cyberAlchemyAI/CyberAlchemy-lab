#!/usr/bin/env python3
from __future__ import annotations

if __name__ == "__main__":
    import runpy

    runpy.run_path(
        str(__import__("pathlib").Path(__file__).with_name("validate-w6-conformance.py")),
        run_name="__main__",
    )

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
PACKAGE = SCRIPT.parent.parent
LAB = PACKAGE.parent
DOMAINSPEC_IMPL = LAB.parent / "domainspec-core" / "projects" / "domainspec-v2" / "impl"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def command(arguments: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**__import__("os").environ, "TMPDIR": "/tmp", "NODE_NO_WARNINGS": "1"},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", default=shutil.which("node"))
    args = parser.parse_args()
    checks: list[dict[str, object]] = []

    def record(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    business = load(PACKAGE / "business-ontology.json")
    assert isinstance(business, dict)
    concept_ids = [entry["id"] for entry in business["concepts"]]
    relation_ids = [entry["id"] for entry in business["relationships"]]
    endpoints = {
        endpoint
        for relation in business["relationships"]
        for endpoint in (relation["from"], relation["to"])
    }
    record(
        "business-ontology-closure",
        len(concept_ids) == len(set(concept_ids)) == 15
        and len(relation_ids) == len(set(relation_ids)) == 16
        and endpoints <= set(concept_ids),
        {"concepts": len(concept_ids), "relationships": len(relation_ids), "endpoint_count": len(endpoints)},
    )

    definition_pack_path = LAB / "docs/definition-packs/0001-ontology-lifecycle-semantic-predecessors/definition-pack.json"
    definition_pack = load(definition_pack_path)
    assert isinstance(definition_pack, dict)
    source_drift = []
    for source in definition_pack["source_refs"]:
        path = (definition_pack_path.parent / source["path"]).resolve()
        actual = digest(path)
        if actual != source["sha256"]:
            source_drift.append({"source_id": source["source_id"], "expected": source["sha256"], "actual": actual})
    record("definition-source-currentness", not source_drift, source_drift or "all seven exact source digests match")

    graph_path = PACKAGE / "domainspec/.domainspec/generated/graph.json"
    graph = load(graph_path)
    assert isinstance(graph, dict)
    graph_node_ids = {entry["node_id"] for entry in graph["nodes"]}
    graph_edge_ids = {entry["edge_id"] for entry in graph["edges"]}
    record(
        "compiled-graph-closure",
        len(graph_node_ids) == 15 and len(graph_edge_ids) == 16,
        {"nodes": len(graph_node_ids), "edges": len(graph_edge_ids), "sha256": digest(graph_path)},
    )

    profile_path = PACKAGE / "domainspec/development-profile.json"
    profile = load(profile_path)
    assert isinstance(profile, dict)
    profile_source = PACKAGE / "domainspec/development-profile-source.json"
    relationships = PACKAGE / "domainspec/relationship-registry.json"
    profile_bindings_pass = (
        profile["profile_binding"]["sha256"] == digest(profile_source)
        and profile["profile_binding"]["semantic_digest"] == digest(profile_source)
        and profile["registry_bindings"]["relationships"]["sha256"] == digest(relationships)
    )
    project = load(PACKAGE / "domainspec/project.json")
    assert isinstance(project, dict)
    profile_bindings_pass = profile_bindings_pass and project["language"]["profile"]["digest"] == digest(profile_path)
    record("development-profile-bindings", profile_bindings_pass, {"profile_sha256": digest(profile_path)})

    binding_path = PACKAGE / "conformance/construction-binding.json"
    binding = load(binding_path)
    assert isinstance(binding, dict)
    digest_failures: list[dict[str, str]] = []
    for entry in binding["semantic_sources"]:
        path = binding_path.parent / entry["path"]
        actual = digest(path.resolve())
        if actual != entry["sha256"]:
            digest_failures.append({"path": entry["path"], "expected": entry["sha256"], "actual": actual})
    for container, pairs in (
        (binding["domainspec"], [("project_ref", "project_sha256"), ("profile_ref", "profile_sha256"), ("relationship_registry_ref", "relationship_registry_sha256"), ("compiled_graph_ref", "compiled_graph_sha256"), ("build_receipt_ref", "build_receipt_sha256"), ("system_profile_ref", "system_profile_sha256")]),
        (binding["implementation"], [("package_ref", "package_sha256"), ("lock_ref", "lock_sha256"), ("library_ref", "library_sha256"), ("cli_ref", "cli_sha256"), ("test_ref", "test_sha256")]),
        (binding["validation"], [("tool_ref", "tool_sha256"), ("relationship_fixture_ref", "relationship_fixture_sha256")]),
    ):
        for path_key, digest_key in pairs:
            path = (binding_path.parent / container[path_key]).resolve()
            actual = digest(path)
            if actual != container[digest_key]:
                digest_failures.append({"path": container[path_key], "expected": container[digest_key], "actual": actual})
    record("construction-binding-digests", not digest_failures, digest_failures or "all exact file digests match")

    bound_graph_nodes = {entry["graph_node_id"] for entry in binding["symbol_bindings"]}
    record(
        "construction-binding-node-coverage",
        bound_graph_nodes == graph_node_ids,
        {"graph_nodes": len(graph_node_ids), "bound_nodes": len(bound_graph_nodes)},
    )
    library_text = (PACKAGE / "runtime/src/lib.rs").read_text(encoding="utf-8")
    absent_symbols = []
    for entry in binding["symbol_bindings"]:
        for symbol in entry["symbols"]:
            leaf = symbol.split("::")[-1]
            if leaf not in library_text:
                absent_symbols.append(symbol)
    record("implementation-symbol-presence", not absent_symbols, absent_symbols or "all named symbols present")

    if not args.node:
        record("domainspec-two-run-check", False, "No Node binary supplied; pass --node PATH")
        node_version = "not_evaluable"
    else:
        version = command([args.node, "--version"], DOMAINSPEC_IMPL)
        node_version = version.stdout.strip()
        runs = [
            command(
                [args.node, "--import", "tsx", str(PACKAGE / "scripts/compile-domainspec.ts"), "--check"],
                DOMAINSPEC_IMPL,
            )
            for _ in range(2)
        ]
        run_payloads = []
        for run in runs:
            try:
                run_payloads.append(json.loads(run.stdout))
            except json.JSONDecodeError:
                run_payloads.append({"invalid_output": run.stdout})
        compile_pass = all(run.returncode == 0 for run in runs) and all(payload.get("status") == "PASS" for payload in run_payloads)
        compile_pass = compile_pass and run_payloads[0] == run_payloads[1]
        record("domainspec-two-run-check", compile_pass, run_payloads)
        relationship_run = command(
            [args.node, "--import", "tsx", str(PACKAGE / "scripts/test-domainspec-relationships.ts")],
            DOMAINSPEC_IMPL,
        )
        try:
            relationship_payload = json.loads(relationship_run.stdout)
        except json.JSONDecodeError:
            relationship_payload = {"invalid_output": relationship_run.stdout}
        relationship_pass = (
            relationship_run.returncode == 0
            and relationship_payload.get("status") == "PASS"
            and relationship_payload.get("positive") == {"nodes": 15, "edges": 16}
            and [entry.get("observed_code") for entry in relationship_payload.get("negative", [])]
            == ["EDGE_ENDPOINT_KIND_MISMATCH", "EDGE_TYPE_UNKNOWN"]
        )
        record("domainspec-relationship-fixtures", relationship_pass, relationship_payload)

    cargo = shutil.which("cargo")
    if cargo is None:
        record("rust-conformance", False, "cargo not found")
        cargo_version = "not_evaluable"
    else:
        cargo_version = command([cargo, "--version"], PACKAGE / "runtime").stdout.strip()
        formatting = command([cargo, "fmt", "--check"], PACKAGE / "runtime")
        compile_check = command([cargo, "check", "--locked", "--all-targets"], PACKAGE / "runtime")
        test = command([cargo, "test", "--locked"], PACKAGE / "runtime")
        record(
            "rust-conformance",
            formatting.returncode == 0
            and compile_check.returncode == 0
            and test.returncode == 0
            and "12 passed; 0 failed" in test.stdout,
            {
                "format_exit_code": formatting.returncode,
                "compile_check_exit_code": compile_check.returncode,
                "test_exit_code": test.returncode,
                "expected": "12 passed; 0 failed",
                "clippy": "not_evaluable: component is not installed in the current Rust toolchain",
            },
        )

    passed = all(check["result"] == "PASS" for check in checks)
    output = {
        "schema_version": "cal-ontology-lifecycle-verification/v1",
        "status": "PASS" if passed else "BLOCK",
        "checks": checks,
        "runtime": {"node": node_version, "cargo": cargo_version},
        "authority_effect": "none",
        "claim_ceiling": "Candidate deterministic compilation and focused conformance only; final human verification and admission remain separate."
    }
    print(json.dumps(output, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
