"""Safe synthetic review; no private copy, native launch or Docker mutation."""
import ast
import contextlib
import copy
import io
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
BASE = LOCAL / "mapper-only-docker-release-0003"
FREEZE = "60a560bc9811962f5d8e40ea8d63fbcf4dab828e905e261952a4da43a00d844c"
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

def make_output(attempt, selected, wrong_result=False, wrong_package=False, wrong_manifest=False):
    package = attempt / "root" / c.MAPPER / "packages/0001"
    package.mkdir(parents=True,mode=0o700)
    names = selected["copy_and_mount_plan"]["expected_package_members"]
    def put(name, value):
        path=package/name
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        path.write_bytes(c.canonical(value));path.chmod(0o600)
    for name in names:
        if name!="manifest.json": put(name,{})
    value=dict(original_result)
    if wrong_result: value["source_sha256"]=selected["manifest"]["original_source_binding"]["sha256"]
    put("build-result.json",value)
    package_binding=dict(selected["manifest"]["original_package_binding"])
    if wrong_package: package_binding["sha256"]=selected["mapper_manifest_sha256"]
    put("mapping.json",{"native_seal_processes":2,"actual_cold_native_read_processes":2,
        "native_domain_mapping_supplied":True,"context_or_ontology_view_carriers_generated":False,
        "authority_effect":"none","actual_owner_outcome":None,"source_package_binding":package_binding})
    put("native-output.json",{"authority_effect":"none","cut":{"semantic_cursor":25},
        "governance_cursor":25,"governed_nodes":[{}]*15})
    put("manifest.json",{"schema_version":"lab-mapped-context-package/v1-candidate",
        "files":[{"path":c.MAPPER+"/packages/0001/"+name,
                  "sha256":c.sha((package/name).read_bytes())}
                 for name in sorted(set(names)-{"manifest.json"})],
        "source_manifest_binding":{"path":c.MAPPER+"/source-manifest.json",
            "sha256":selected["manifest"]["original_source_binding"]["sha256"] if wrong_manifest else selected["mapper_manifest_sha256"]},
        "authority_effect":"none","actual_owner_outcome":None})

cases=[]
for options in ({},{"wrong_result":True},{"wrong_package":True},{"wrong_manifest":True}):
    with tempfile.TemporaryDirectory(prefix="mapper3-output-review-") as tmp:
        attempt=Path(tmp)
        make_output(attempt,selection,**options)
        with mock.patch.object(c,"ATTEMPT",attempt):
            if options:
                try: c.verify_mapped_output(selection)
                except ValueError as error:
                    if str(error)!="Mapper output manifest or bounded result differs": raise
                else: raise RuntimeError("WRONG_PIN_ACCEPTED")
                cases.append({"mutation":options,"refused":True})
            else:
                positive=c.verify_mapped_output(selection)
                if positive["files"]!=55:raise RuntimeError("COUNT")
                cases.append({"positive":positive})
observations["R03"]={"closed":True,"builder":str(build_path),"builder_sha256":expected_sha,
    "exact_AST_line":assignment.lineno,"result_pin":original_result["source_sha256"],
    "source_package_binding":selection["manifest"]["original_package_binding"],"cases":cases}

# Full selected controller + production protocol + real output gate. Only private
# preparation, provenance/currentness inputs and Docker transport are fixture seams.
composed=[]
for wrong in (False,True):
    with tempfile.TemporaryDirectory(prefix="mapper3-composed-review-") as tmp:
        attempt=Path(tmp)/"attempt"
        selected=copy.deepcopy(selection)
        old=selected["fresh_attempt"]
        selected["fresh_attempt"]=str(attempt)
        selected["copy_to"]=str(attempt/"root")
        plan=selected["copy_and_mount_plan"]
        plan["output_package_host"]=plan["output_package_host"].replace(old,str(attempt))
        for row in plan["container_mounts"]:
            if "source" in row: row["source"]=row["source"].replace(old,str(attempt))
        def prepare(*args):
            attempt.mkdir(mode=0o700)
            make_output(attempt,selected,wrong_result=wrong)
            return {"attempt":str(attempt),"stage_files":986,"projected_mapper_files":5,
                    "native_sha256":"f"*64,"entrypoint_sha256":"e"*64,"source_stage_modified":False}
        fake=t.SelectedResponseDocker()
        with contextlib.ExitStack() as stack:
            for name,value in (("ATTEMPT",attempt),):stack.enter_context(mock.patch.object(c,name,value))
            stack.enter_context(mock.patch.object(c,"trusted_selection",return_value=selected))
            stack.enter_context(mock.patch.object(c,"release_freeze_gate",return_value={"freeze_sha256":"a"*64,"entrypoint_sha256":"e"*64}))
            for name in ("release_authorization_gate","stage_metadata_gate","copy_plan","source_predecessor_gate","reader_predecessor_gate","native_load_gate","docker_absence_observation_gate"):
                stack.enter_context(mock.patch.object(c,name))
            stack.enter_context(mock.patch.object(c,"exact_stage_plan",return_value={"files":[]}))
            stack.enter_context(mock.patch.object(c,"prepare_exact_attempt",side_effect=prepare))
            stack.enter_context(mock.patch.object(c.secrets,"token_hex",return_value=t.LABEL))
            stack.enter_context(mock.patch.object(p,"SubprocessDocker",return_value=fake))
            with contextlib.redirect_stdout(io.StringIO()):
                if wrong:
                    try:c.execute_reviewed_one_shot()
                    except ValueError as error:
                        if str(error)!="Mapper output manifest or bounded result differs":raise
                    else:raise RuntimeError("COMPOSED_WRONG_PIN_ACCEPTED")
                else:c.execute_reviewed_one_shot()
        final=json.loads((attempt/"evidence/final.json").read_bytes())
        if final["overall"] != ("UNKNOWN" if wrong else "PASS"):raise RuntimeError("FALSE_FINAL")
        if not fake.removed or fake.create_calls!=1:raise RuntimeError("CLEANUP")
        composed.append({"wrong_result":wrong,"final":final,"fixture_container_removed":fake.removed})
observations["full_real_output_gate_composition"]=composed
print(json.dumps({"inherited_tests":result.testsRun,"inherited_pass":True,
    "observations":observations,"optimized":sys.flags.optimize,"members_pre_post":verify(),
    "private_archive_read":False,"mapper_effect":False,"temporary_fixture_cleanup":"COMPLETE"},sort_keys=True))
