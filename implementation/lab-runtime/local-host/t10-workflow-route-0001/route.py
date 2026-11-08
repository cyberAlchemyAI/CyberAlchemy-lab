#!/usr/bin/env python3
"""Cold, local W08 design routes and bounded original candidate run evidence."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
MATRIX = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json"
MATRIX_SHA = "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"
T31_1 = "implementation/lab-runtime/local-host/t31-workflow-stream-0001"
T31_2 = "implementation/lab-runtime/local-host/t31-workflow-stream-0002"
T31_1_RESULT_SHA = "308cad743f9d31773a8f709a7e0804701e0622ea803627369c01031a558cb6d7"
T31_2_RESULT_SHA = "c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445"
T31_CODE = {
    T31_1 + "/verify.py": "4c8b38b2be9a7a3827f7fbb968144ee481a7ae3970679f2e2c704bb420c78d2c",
    T31_1 + "/run.py": "aed2edbe77a1743189c11ccf9510b18bde85edc94f73a0a21e3c7466e9303b23",
    T31_1 + "/inventory.py": "fe87732f8b04ab3ec49f389d1bb3f0d5be9cf8b6a176c47b7712d8ff93c67ba3",
    T31_1 + "/worker.py": "55fe5511a77890f81c16778df875dde6a881e7372cbefaf1c6a54195e743ed33",
    T31_2 + "/stream.py": "7f6485517701ebbddf157404a1a7ac7ab0ac9fb56bbe0cb054f1a4ee9a468594",
    "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_contracts.py":
        "b2bf4e4a7e8e705a1c796b113bf73fd94af0cef831c44ec7ebeb1db434eb7cfa",
    "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_registry.py":
        "8e3a35b1c1d06d4b9d8e343ecc4e4dcee2267f0c695d37c2a4cdd3542673c763",
    "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/carrier-catalog.json":
        "b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8",
}
OBSERVED = {"engineering": 6, "research": 12}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def relative(name: str) -> Path:
    need(type(name) is str and name and not name.startswith("/") and "\\" not in name,
         "unsafe binding path")
    path = PurePosixPath(name)
    need(path.as_posix() == name and all(part not in ("", ".", "..") for part in path.parts),
         "unsafe binding path")
    return Path(*path.parts)


def exact(root: Path, binding: dict) -> bytes:
    need(type(binding) is dict and set(binding) >= {"path", "sha256"}, "invalid exact binding")
    rel = relative(binding["path"])
    parent = root
    for part in rel.parts[:-1]:
        parent /= part
        need(stat.S_ISDIR(parent.lstat().st_mode), "unsafe parent: " + binding["path"])
    path = root / rel
    need(stat.S_ISREG(path.lstat().st_mode), "unsafe file: " + binding["path"])
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        need(stat.S_ISREG(os.fstat(descriptor).st_mode), "unsafe file: " + binding["path"])
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            raw = source.read()
    finally:
        os.close(descriptor)
    need(digest(raw) == binding["sha256"], "changed selected bytes: " + binding["path"])
    if "size_bytes" in binding:
        need(len(raw) == binding["size_bytes"], "changed selected size: " + binding["path"])
    return raw


def body(root: Path, binding: dict) -> dict:
    return json.loads(exact(root, binding))


def validate_relation(signature: dict, relation: dict) -> None:
    payload = relation["payload"]
    need(relation["kind"] == "relation-kind" and
         signature["relation_kind_ref"] == relation["node_id"] == payload["relation_kind_id"] and
         signature["axis_id"] == payload["axis_id"] and
         signature["qualifier_contract"] == payload["qualifier_contract"] and
         {"source_kind": signature["source_kind"], "target_kind": signature["target_kind"]}
         in payload["allowed_endpoint_pairs"],
         "wrong relation kind, direction, counterpart or qualifier")


def validate_design(row: dict, original: dict, disposition: dict, choice: dict,
                    w08: dict, definition: dict, selected: dict) -> dict:
    index = row["index"]
    name = row["member_ref"].removeprefix("protocol:W08:workflow:")
    need(index in range(4, 14) and row["member_ref"] == "protocol:W08:workflow:" + name and
         row["original_class"] == "workflow-transition-protocol" and
         row["candidate_route"] == "workflow-transition-design",
         "wrong W08 member kind")
    need(original["kind"] == "governed-model" and original["lifecycle_state"] == "candidate" and
         original["relation_refs"] == [] and original["authority_effect"] == "none" and
         original["payload"]["contract_ref"] == row["original_target_bindings"][0]["path"],
         "original refused model meaning differs")
    need(disposition["original_index"] == index and disposition["member_ref"] == row["member_ref"] and
         disposition["original_body_binding"] == row["original_body_binding"] and
         disposition["status"] == "EXACT-MEMBER-REQUIRES-INDIVIDUAL-DESIGN-DISPOSITION" and
         disposition["supported_model_relation"] is None and
         disposition["admission_or_runtime_use_allowed"] is False and
         disposition["actual_owner_outcome"] is None,
         "original refusal or disposition differs")
    facts = choice["specific_source_facts"]
    need(choice["original_index"] == index and choice["member_ref"] == row["member_ref"] and
         choice["semantic_category"] == "workflow-transition-design" and
         choice["original_disposition_binding"] == {
             key: row["original_disposition_binding"][key] for key in ("path", "sha256")} and
         choice["actual_owner_outcome"] is None and
         choice["admission_or_runtime_use_allowed"] is False and
         facts["workflow"] == name and facts["original_executable"] is False and
         facts["per_run_bindings_required"] is True,
         "review choice or execution ceiling differs")
    need(w08 == selected and w08["name"] == name and w08["executable"] is False and
         w08["authority_effect"] == "none" and w08["single_goal_coordination"] is True and
         w08["workflow_type_ref"] == definition["workflow_type_ref"] == "workflow:" + name + ":v1-candidate" and
         w08["source_binding"] == row["original_target_bindings"][1],
         "W08 selected design or original definition differs")
    need(w08["states"] == facts["states"] == definition["states"] and
         w08["initial_state"] == facts["initial_state"] == definition["initial_state"] and
         w08["terminal_states"] == facts["terminal_states"] == definition["terminal_states"],
         "workflow states differ")
    steps = w08["transitions"]
    need(len(steps) == len(definition["transitions"]) == len(facts["transition_refs"]) and
         [item["transition_ref"] for item in steps] == facts["transition_refs"] and
         len(set(facts["transition_refs"])) == len(steps), "transition inventory differs")
    original_fields = set(definition["transitions"][0])
    for actual, source in zip(steps, definition["transitions"]):
        need({key: actual[key] for key in original_fields} == source and
             actual["transition_ref"].startswith("transition:" + name + ":") and
             actual["from_state"] in w08["states"] and actual["to_state"] in w08["states"] and
             actual["actor_contract"]["binding_status"] == "required-per-run; not assigned by design" and
             actual["authority_requirement_refs"] and actual["satisfaction_check_refs"],
             "transition semantics or per-run guard differs")
        for field, carriers in (("input_bindings_required", "input_carriers"),
                                ("output_bindings_required", "output_carriers")):
            need([item["carrier_ref"] for item in actual[field]] == actual[carriers],
                 "carrier bindings or order differ")
    return {"index": index, "member_ref": row["member_ref"],
            "route_kind": "task-local-workflow-transition-design",
            "original_body_binding": row["original_body_binding"],
            "original_disposition_binding": row["original_disposition_binding"],
            "review_choice_binding": row["review_choice_binding"],
            "w08_design_binding": row["original_target_bindings"][0],
            "original_definition_binding": row["original_target_bindings"][1],
            "workflow_type_ref": w08["workflow_type_ref"],
            "initial_state": w08["initial_state"], "terminal_states": w08["terminal_states"],
            "transition_refs": facts["transition_refs"],
            "selected_original_relation": None, "admitted_or_executable": False}


def design_routes(root: Path = ROOT) -> list[dict]:
    matrix = json.loads(exact(root, {"path": MATRIX, "sha256": MATRIX_SHA}))
    rows = matrix["rows"]
    need(len(rows) == 29 and [row["index"] for row in rows] == list(range(29)) and
         matrix["T10_complete"] is False and matrix["semantically_grounded_selected_representations"] == 0,
         "29-member matrix or claim ceiling differs")
    routes = []
    seen = set()
    for row in rows[4:14]:
        original = body(root, row["original_body_binding"])
        disposition = body(root, row["original_disposition_binding"])
        choice = body(root, row["review_choice_binding"])
        w08 = body(root, row["original_target_bindings"][0])
        definition = body(root, row["original_target_bindings"][1])
        for binding in row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
            exact(root, binding)
        pointer = choice["original_scope"]["source_selection"]
        parent = body(root, pointer["parent_binding"])
        position = int(pointer["json_pointer"].removeprefix("/workflows/"))
        need(pointer["json_pointer"] == "/workflows/" + str(position) and
             parent["workflows"][position] == w08, "W08 parent selection differs")
        for step in w08["transitions"]:
            for field in ("input_bindings_required", "output_bindings_required"):
                for item in step[field]:
                    exact(root, item["schema_binding"])
            for relation in step["selected_relation_signatures"]:
                validate_relation(relation, body(root, relation["relation_binding"]))
        route = validate_design(row, original, disposition, choice, w08, definition,
                                parent["workflows"][position])
        need(route["member_ref"] not in seen, "duplicate W08 route")
        seen.add(route["member_ref"])
        routes.append(route)
    need(len(routes) == 10 and len({ref for route in routes for ref in route["transition_refs"]}) == 28,
         "ten W08 designs or 28 transitions missing")
    return routes


def verify_t31(root: Path, run1: Path, run2: Path) -> tuple[dict, dict]:
    for path, sha in T31_CODE.items():
        exact(root, {"path": path, "sha256": sha})
    expected = ((T31_1 + "/verify.py", run1, {"result": "PASS", "observed": 2, "remaining": 26}),
                (T31_2 + "/stream.py", run2,
                 {"result": "PASS-local-candidate-only", "new": 2, "cumulative": 4, "remaining": 24}))
    for script, run, wanted in expected:
        command = [sys.executable, "-B", str(root / script)]
        if script.endswith("stream.py"):
            command.append("verify")
        command.append(str(run))
        process = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                 timeout=120, check=False)
        need(process.returncode == 0 and json.loads(process.stdout) == wanted,
             "actual T31 producer/consumer replay refused: " + script)
    first = json.loads((run1 / "RESULT.json").read_bytes())
    second = json.loads((run2 / "RESULT.json").read_bytes())
    need(digest((run1 / "RESULT.json").read_bytes()) == T31_1_RESULT_SHA and
         digest((run2 / "RESULT.json").read_bytes()) == T31_2_RESULT_SHA,
         "selected T31 result bytes differ")
    return first, second


def actual_routes(root: Path, routes: list[dict], first: dict, second: dict) -> list[dict]:
    by_name = {route["workflow_type_ref"].split(":")[1]: route for route in routes}
    need(set(OBSERVED) <= set(by_name), "observed workflow route missing")
    rows = first["observed_terminal_output_transitions"] + second["new_output_transitions"]
    need(len(rows) == 4 and len({row["transition_ref"] for row in rows}) == 4,
         "four distinct actual transition refs required")
    result = []
    for name, index in OBSERVED.items():
        route = by_name[name]
        need(route["index"] == index, "wrong observed member index")
        selected = [row for row in rows if row["transition_ref"].startswith("transition:" + name + ":")]
        need(len(selected) == 2 and all(row["transition_ref"] in route["transition_refs"] for row in selected),
             "actual transition not in W08 design")
        w08 = json.loads(exact(root, route["w08_design_binding"]))
        steps = {step["transition_ref"]: step for step in w08["transitions"]}
        for row in selected:
            need([item["carrier_ref"] for item in row["output_artifact_refs"]] ==
                 steps[row["transition_ref"]]["output_carriers"],
                 "actual output kind differs from W08 transition")
            need(row["output_original_paths"] and
                 (row.get("later_consumer") or row.get("later_consumers")),
                 "actual output producer or later consumer missing")
        result.append({"member_index": index, "member_ref": route["member_ref"],
                       "observed_transition_refs": sorted(row["transition_ref"] for row in selected),
                       "unobserved_transition_refs": sorted(set(route["transition_refs"]) -
                                                            {row["transition_ref"] for row in selected}),
                       "producer_consumer_receipt_bindings": [
                           {"path": T31_1 + "/run-0001/RESULT.json", "sha256": T31_1_RESULT_SHA},
                           {"path": T31_2 + "/run-0001/RESULT.json", "sha256": T31_2_RESULT_SHA}],
                       "qualification": "isolated-original-candidate-only"})
    return result


def receipt(root: Path = ROOT, run1: Path | None = None, run2: Path | None = None) -> dict:
    run1 = run1 or root / T31_1 / "run-0001"
    run2 = run2 or root / T31_2 / "run-0001"
    routes = design_routes(root)
    first, second = verify_t31(root, run1, run2)
    actual = actual_routes(root, routes, first, second)
    return {"schema_version": "lab-T10-local-W08-design-route/v1",
            "route_source_sha256": digest(Path(__file__).read_bytes()),
            "matrix_binding": {"path": MATRIX, "sha256": MATRIX_SHA},
            "selected_t31_code_bindings": [
                {"path": path, "sha256": sha} for path, sha in sorted(T31_CODE.items())],
            "design_routes": routes, "design_route_count": 10,
            "design_transition_count": 28,
            "actual_candidate_routes": actual, "actual_candidate_member_count": 2,
            "actual_candidate_transition_count": 4,
            "unobserved_w08_member_indices": [4, 5, 7, 8, 9, 10, 11, 13],
            "selected_governed_model_representations": 0,
            "authority_effect": "none", "T10_complete": False,
            "claim_ceiling": "Ten exact W08 transition designs have local read-only contract routes. Only members 06 and 12 have four isolated original candidate producer/later-consumer transitions; their other two transitions and all other W08 runs remain unobserved here. No model relation, semantic selection, owner outcome, admission, signed native output journal or full 29-member T10 completion is claimed."}


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


if __name__ == "__main__":
    saved = Path(__file__).with_name("RESULT-0002.json")
    expected = canonical(receipt())
    if sys.argv[1:] == ["--write"]:
        need(not saved.exists(), "result already exists; use a versioned successor")
        saved.write_bytes(expected)
    elif sys.argv[1:] == ["--verify"]:
        need(saved.read_bytes() == expected, "retained T10 result or selected inputs differ")
    else:
        raise SystemExit("usage: route.py --write|--verify")
    print(json.dumps({"result": "PASS-local-candidate-only", "design_routes": 10,
                      "actual_candidate_members": 2, "actual_candidate_transitions": 4}, sort_keys=True))
