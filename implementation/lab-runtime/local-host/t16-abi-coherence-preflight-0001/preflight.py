"""Read-only API53/legacy/current-family ABI contradiction preflight.

This diagnostic does not run a test method or modify selected source bytes.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
API = "product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001"
ADAPTER = "product/lab/release-candidates/v1/interface/current-source-adapter-v2-action-0148"
FAMILY = "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5"
INSTALL = ROOT / "implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/working/installation-0001"
EXPECTED = {
    API + "/source-manifest.json": "7944431236ce9437516104b33ed04024994e0d9d45a2c2152eacf71612fd09ff",
    API + "/guard.py": "c6cb6ceebd658dcb21d7e629455da9aba20569dd9128beddcad526b52cd0612d",
    ADAPTER + "/source-manifest.json": "dd12b28311ac0e94eaeaf459560d855134404d94adf80f96be53868438b123c3",
    ADAPTER + "/boundary.py": "6a505d2c0877ef24ca21a2f7f8069a6559af777d5e43e2a2f0ab9a6a5ab682c2",
    FAMILY + "/source/source-manifest.json": "0dc869f614e4d1f4be29c4b85f60dd5abd8f25b9fe84e1dc779932aee90c50d4",
    FAMILY + "/reader/source-manifest.json": "b3461a1e68a5da06ad6c47966eb4ed448e67f2318baf5e7e956937d15f007877",
    FAMILY + "/context/source-manifest.json": "07fd3184fc4d68c955886dca2f787e8bc8f82c46b6f892e2cebdc02a09e667ec",
    "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json": "2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835",
    "implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/installation-receipt.json": "7f32ee98bfff06ae68c5c90e5874816b405acfb1d076d5edf33a220f059d54b5",
    "implementation/lab-runtime/local-host/t16-api53-selected-abi-regression-0003/RUNNER-SELECTION-0003.json": "c31f50e903dc59e1a5061880fc9ce7f9e83e7badb4d3b2c23dd7b7fba3b8250c",
}


def selected_bytes(relative):
    path = ROOT / relative
    if path.is_symlink() or not path.is_file() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError("selected path is not a regular unlinked file: " + relative)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED[relative]:
        raise ValueError("selected file changed: " + relative)
    return raw


def run():
    values = {name: selected_bytes(name) for name in EXPECTED}
    api = json.loads(values[API + "/source-manifest.json"])
    adapter = json.loads(values[ADAPTER + "/source-manifest.json"])
    family = {role: json.loads(values[FAMILY + "/" + role + "/source-manifest.json"])
              for role in ("source", "reader", "context")}
    deps = json.loads(values["docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json"])
    runner = json.loads(values["implementation/lab-runtime/local-host/t16-api53-selected-abi-regression-0003/RUNNER-SELECTION-0003.json"])
    api_env = api["environment"]
    old_env = adapter["environment"]
    family_envs = {role: item["environment"] for role, item in family.items()}
    if (api_env != {"python": "3.14.4", "jsonschema": "4.19.2", "cryptography": "46.0.5"}
            or old_env != {"python": "3.14.4", "jsonschema": "4.23.0", "cryptography": "46.0.5"}
            or any(item != api_env for item in family_envs.values())
            or deps["versions"]["jsonschema"] != old_env["jsonschema"]
            or runner["source_sha256"] != EXPECTED[API + "/source-manifest.json"]
            or runner["dependency_selection_sha256"] != EXPECTED["docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json"]):
        raise ValueError("selected environment or runner binding differs")
    guard_row = next(row for row in api["files"] if row["path"] == API + "/guard.py")
    if guard_row["sha256"] != EXPECTED[API + "/guard.py"]:
        raise ValueError("API53 guard is not selected by its manifest")

    coordinator = ROOT / "implementation/lab-runtime/local-host/t16-api53-selected-abi-regression-0003/run_all.py"
    dry = subprocess.run([sys.executable, "-B", str(coordinator), "--dry-run", "--selection-sha256",
                          EXPECTED["implementation/lab-runtime/local-host/t16-api53-selected-abi-regression-0003/RUNNER-SELECTION-0003.json"]],
                         cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, timeout=60, check=False)
    if dry.returncode or dry.stderr:
        raise ValueError("selected ABI closure dry run failed: " + dry.stderr.decode(errors="replace")[:300])
    dry_observation = json.loads(dry.stdout)
    if dry_observation["buckets"] != 21 or dry_observation["cases"] != 345:
        raise ValueError("selected ABI inventory differs")

    script = (
        "import hashlib,importlib.metadata,importlib.util,json,pathlib,sys; "
        "sys.path.insert(0,sys.argv[1]); "
        "p=pathlib.Path(sys.argv[2]); s=importlib.util.spec_from_file_location('selected_api53_guard',p); "
        "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        "result={'installed_jsonschema':importlib.metadata.version('jsonschema')}; "
        "\ntry: m.verify(sys.argv[3])\n"
        "except ValueError as error: result['guard_refusal']=str(error)\n"
        "else: result['guard_refusal']=None\n"
        "print(json.dumps(result,sort_keys=True))"
    )
    command = [str(INSTALL / "lib/abi/ld-linux-x86-64.so.2"), "--inhibit-cache", "--library-path",
               str(INSTALL / "lib/abi"), str(INSTALL / "bin/python"), "-I", "-B", "-S", "-c", script,
               str(INSTALL / "deps"), str(ROOT / API / "guard.py"), EXPECTED[API + "/source-manifest.json"]]
    child = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=30, check=False)
    if child.returncode or child.stderr:
        raise ValueError("selected ABI child refused before a diagnostic: " + child.stderr.decode(errors="replace")[:300])
    observation = json.loads(child.stdout)
    if observation != {"installed_jsonschema": "4.23.0", "guard_refusal": "API environment differs"}:
        raise ValueError("selected guard did not reproduce the expected causal refusal")

    # Probe the two source boundaries in one fresh process of that same
    # installed ABI. The historical boundary performs its actual selected
    # setup; the current family's unchanged verifier must fail at its own
    # environment check. No selected bytes or periods are rewritten.
    source_script = (
        "import importlib,importlib.util,json,pathlib,sys; "
        "sys.path.insert(0,sys.argv[1]); root=pathlib.Path(sys.argv[2]); results={}; "
        "\ndef package(name,path):\n"
        " spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)]); "
        "module=importlib.util.module_from_spec(spec); sys.modules[name]=module; spec.loader.exec_module(module)\n"
        "\ndef probe(name,action):\n"
        " try: action(); results[name]={'result':'PASS'}\n"
        " except ValueError as error: results[name]={'result':'REFUSED','reason':str(error)}\n"
        "\ndef old():\n"
        f" package('t16_old_boundary',root/'{ADAPTER}'); "
        "boundary=importlib.import_module('t16_old_boundary.boundary'); "
        f"boundary.boundary('{EXPECTED[ADAPTER + '/source-manifest.json']}',boundary.SOURCE_PIN,boundary.PACKAGE_PIN)\n"
        "\ndef current():\n"
        f" package('t16_current_source',root/'{FAMILY}/source'); "
        "source=importlib.import_module('t16_current_source.base'); "
        f"source.verify_source('{EXPECTED[FAMILY + '/source/source-manifest.json']}')\n"
        "probe('historical_adapter_boundary',old); probe('current_family_source',current); "
        "print(json.dumps(results,sort_keys=True))"
    )
    source_command = [*command[:9], source_script, str(INSTALL / "deps"), str(ROOT)]
    source_child = subprocess.run(source_command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=60, check=False)
    if source_child.returncode or source_child.stderr:
        raise ValueError("source boundary child failed: " + source_child.stderr.decode(errors="replace")[:300])
    source_observation = json.loads(source_child.stdout)
    if source_observation != {
            "historical_adapter_boundary": {"result": "PASS"},
            "current_family_source": {"result": "REFUSED", "reason": "selected source environment differs"}}:
        raise ValueError("source boundary diagnostic differs")
    return {
        "schema_version": "lab-t16-api53-abi-coherence-preflight/v1",
        "result": "BLOCKED-COHERENT-API-SOURCE-RECUT-REQUIRED",
        "authority_effect": "none",
        "methods_executed": 0,
        "selected_sha256": EXPECTED,
        "api53_environment": api_env,
        "historical_adapter_environment": old_env,
        "current_fixture_environments": family_envs,
        "selected_abi_closure": dry_observation,
        "selected_abi_observation": observation,
        "selected_abi_source_boundary_observation": source_observation,
        "first_runtime_refusal": "API53 guard.verify rejects pinned 4.23.0 ABI before an inherited method",
        "next_concrete_recut": [
            API + "/source-manifest.json and its selected source/profile/runner bindings",
            FAMILY + "/{source,reader,context}/source-manifest.json as a fresh signed 4.23.0 family",
            API + "/source_bridge.py current-family paths, delivery pin and source/package bindings",
        ],
        "claim_ceiling": "Read-only public/candidate preflight; no fixture re-sign, inherited method, protected Source8, or T16 qualification.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    if args.output is not None:
        target = args.output.resolve()
        if target.parent != Path(__file__).resolve().parent:
            raise ValueError("output must be in the disjoint preflight directory")
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    print(json.dumps({"result": result["result"], "methods_executed": 0,
                      "selected_abi_observation": result["selected_abi_observation"]}, sort_keys=True))


if __name__ == "__main__":
    main()
