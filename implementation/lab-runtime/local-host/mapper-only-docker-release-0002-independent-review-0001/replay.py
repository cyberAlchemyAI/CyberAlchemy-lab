"""Safe synthetic review; no private copy, native launch or Docker mutation."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

REPO = Path("/home/vlad_/projects/CyberAlchemy-lab")
LOCAL = REPO / "implementation/lab-runtime/local-host"
BASE = LOCAL / "mapper-only-docker-release-0002"
FREEZE = "03aa1bc26c03700240b00117845f9f9fcc110863b6c1ad9e0512ce80c097cb08"
def verify():
    raw = (BASE / "freeze.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != FREEZE:
        raise RuntimeError("FREEZE_DRIFT")
    rows = json.loads(raw)["file_bindings"]
    for row in rows:
        raw = (BASE / row["path"]).read_bytes()
        if len(raw) != row["size"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise RuntimeError("MEMBER_DRIFT")
    return len(rows)
verify()
sys.path.insert(0, str(BASE))
import controller as c
import docker_protocol as p
import test_release_static as t

suite = unittest.defaultTestLoader.loadTestsFromModule(t)
result = unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
selection = c.trusted_selection()
observations = {}
with tempfile.TemporaryDirectory(prefix="mapper2-terminal-review-") as tmp:
    root = Path(tmp)
    terminal = p.reconcile_once(t.FakeDocker(),
        c.docker_create_argv(selection, label=t.LABEL),
        image=c.IMAGE,label=t.LABEL,name=t.NAME,evidence_dir=root)
    raw = (root / "terminal.json").read_bytes()
    digest = c.sha(p.evidence_json_bytes(terminal))
    if raw != p.evidence_json_bytes(terminal):
        raise RuntimeError("R01_NOT_FIXED")
    c.bounded_nofollow_bytes(root / "terminal.json", digest, 1024 * 1024)
    observations["R01"] = {"closed": True, "exact_original_sha256": digest}
old = LOCAL / "mapper-only-docker-release-0001-independent-review-0001"
stdout = (old / "absent.stdout").read_bytes()
stderr = (old / "absent.stderr").read_bytes()
selected = json.loads((BASE / "docker-absence-observation.json").read_bytes())
if stdout.decode() != selected["inspect_stdout"] or stderr.decode() != selected["inspect_stderr"]:
    raise RuntimeError("OBSERVATION_DRIFT")
driver = p.SubprocessDocker()
with mock.patch.object(driver, "_run", return_value=subprocess.CompletedProcess(
        selected["inspect_argv"],1,stdout,stderr)):
    if driver.absent("0"*64, deadline=time.monotonic()+10) is not True:
        raise RuntimeError("R02_NOT_FIXED")
observations["R02"] = {"closed": True, "prior_actual_cli_originals_equal_selected_observation":True}

# Execute only the pinned historical builder's result-dictionary assignment.
# Do not import its module or call build(), Source, Reader, or native.
build_path = c.V3 / "generated" / c.MAPPER / "build.py"
raw = build_path.read_bytes()
expected_sha = c.selected_projected_files(selection)[c.MAPPER + "/build.py"]
if c.sha(raw) != expected_sha:
    raise RuntimeError("BUILDER_PIN_DRIFT")
tree = ast.parse(raw)
build = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="build")
assignment = next(n for n in build.body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=="result" for t in n.targets))
scope = {"pin":selection["mapper_manifest_sha256"], "started":0,
         "time":types.SimpleNamespace(monotonic=lambda:1)}
exec(compile(ast.Module(body=[assignment],type_ignores=[]),str(build_path),"exec"),scope)
original_result = scope["result"]
with tempfile.TemporaryDirectory(prefix="mapper2-output-review-") as tmp:
    attempt = Path(tmp)
    package = attempt / "root" / c.MAPPER / "packages/0001"
    package.mkdir(parents=True,mode=0o700)
    names = selection["copy_and_mount_plan"]["expected_package_members"]
    def put(name, value):
        path=package/name
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        path.write_bytes(c.canonical(value));path.chmod(0o600)
    for name in names:
        if name!="manifest.json": put(name,{})
    put("build-result.json",original_result)
    put("mapping.json",{"native_seal_processes":2,"actual_cold_native_read_processes":2,
        "native_domain_mapping_supplied":True,"context_or_ontology_view_carriers_generated":False,
        "authority_effect":"none","actual_owner_outcome":None})
    put("native-output.json",{"authority_effect":"none","cut":{"semantic_cursor":25},
        "governance_cursor":25,"governed_nodes":[{}]*15})
    def manifest():
        put("manifest.json",{"schema_version":"lab-mapped-context-package/v1-candidate",
            "files":[{"path":c.MAPPER+"/packages/0001/"+name,
                      "sha256":c.sha((package/name).read_bytes())}
                     for name in sorted(set(names)-{"manifest.json"})],
            "source_manifest_binding":{"path":c.MAPPER+"/source-manifest.json",
                                      "sha256":selection["mapper_manifest_sha256"]},
            "authority_effect":"none","actual_owner_outcome":None})
    manifest()
    with mock.patch.object(c,"ATTEMPT",attempt):
        try:c.verify_mapped_output(selection)
        except ValueError as error:
            if str(error)!="Mapper output manifest or bounded result differs":raise
            refusal=str(error)
        else:raise RuntimeError("R03_COUNTEREXAMPLE_NOT_REPRODUCED")
        # Separating control: only this result field and its manifest digest
        # change. Everything else goes through the same production verifier.
        changed=dict(original_result,source_sha256=selection["manifest"]["original_source_binding"]["sha256"])
        put("build-result.json",changed);manifest()
        positive=c.verify_mapped_output(selection)
        if positive["result"]!="PASS_CANDIDATE_OUTPUT_ONLY":raise RuntimeError("CONTROL_FAILED")
    observations["R03"]={"builder":str(build_path),"builder_sha256":expected_sha,
        "exact_AST_line":assignment.lineno,"original_mapper_pin":original_result["source_sha256"],
        "controller_demands_source_pin":changed["source_sha256"],"refusal":refusal,
        "single_field_changed_control":positive,"leaves":len(names),
        "claim_ceiling":"Only selected result assignment and output verifier; event bodies inert, no builder/Source/Reader/native execution"}
print(json.dumps({"inherited_tests":result.testsRun,"inherited_pass":True,
                  "observations":observations,"optimized":sys.flags.optimize,
                  "members_pre_post":verify(),"private_archive_read":False,
                  "mapper_effect":False,"temporary_fixture_cleanup":"COMPLETE"},sort_keys=True))
