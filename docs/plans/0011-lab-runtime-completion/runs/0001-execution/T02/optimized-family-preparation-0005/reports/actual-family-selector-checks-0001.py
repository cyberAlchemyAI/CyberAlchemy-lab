"""Independent AST/hash/metadata review; never imports a Lab runtime module."""
import ast
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[6]
FAMILY = PACKAGE / "instances/optimized-0005"
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v17"
ROLE_FIELDS = {
    "source_binding": "source/source-manifest.json",
    "source_package_binding": "source/packages/0001/manifest.json",
    "reader_binding": "reader/source-manifest.json",
    "mapper_binding": "mapped/source-manifest.json",
    "mapper_package_binding": "mapped/packages/0001/manifest.json",
    "context_source_binding": "context/source-manifest.json",
    "context_package_binding": "context/packages/0001/manifest.json",
    "implementation_binding": "context/implementation-binding.json",
    "period_binding": "source/packages/0001/period.json",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def capture(row):
    assert set(row) >= {"path", "sha256"}
    path = Path(row["path"])
    if not path.is_absolute():
        path = ROOT / path
    assert not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
    flags = os.O_RDONLY | os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        assert stat.S_ISREG(before.st_mode)
        chunks = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        current = os.stat(path, follow_symlinks=False)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        assert identity(before) == identity(after) == identity(current)
        raw = b"".join(chunks)
        assert sha(raw) == row["sha256"]
        if "required_mode" in row:
            assert stat.S_IMODE(before.st_mode) == row["required_mode"]
        return raw
    finally:
        os.close(fd)

def binding(name, expected):
    return json.loads(capture({"path": (PACKAGE / name).relative_to(ROOT).as_posix(), "sha256": expected}))

selection = binding("root-actual-family-selection-0001.json", "73a6c61200f4a3489b43d3c6262a675478a752f90da10cdc5d0e62fd9b8b8aa4")
runtime = binding("instances/optimized-0005/runtime/runtime-selection.json", "589d36bce32cfef590e0a01c9fd9ea8873cc16eede8f20e9adb1686f1423deff")
overlay = binding("instances/optimized-0005/runtime/selector-postimages.json", "e6b53f3a21f7f2d8e1258e992d83dfde50232ec661c57244730c15104afb4b98")
baseline = binding("preparation-baseline.json", "95a73902cc5b584f0185a0b16df5ad4213816d57a0356e8fc3bc62c86fba0067")
assert selection["instance"] == runtime["instance"] == "optimized-0005"
assert runtime["actual_family_selection_binding"]["sha256"] == "73a6c61200f4a3489b43d3c6262a675478a752f90da10cdc5d0e62fd9b8b8aa4"
assert set(selection["family_bindings"]) == set(ROLE_FIELDS)
for key, suffix in ROLE_FIELDS.items():
    row = selection["family_bindings"][key]
    assert row["path"] == (FAMILY / suffix).relative_to(ROOT).as_posix()
    capture(row)
    assert runtime[key] == row
construction = json.loads(capture(selection["construction_binding"]))
assert construction["optimized_recipe_declaration_mapping"] == baseline["declaration_mapping"]
assert len(baseline["original_recipe_declarations"]) == 349
snapshots = [r["snapshot_binding"] for r in baseline["mutable_snapshot_pairs"]]
assert len(snapshots) == 6
for row in snapshots:
    capture(row)
forbidden = {
    (API / name).relative_to(ROOT).as_posix()
    for name in ["source-manifest.json", "contract-profile.json", "SCHEMA-EXECUTION-DEPENDENCIES.json", "INPUT-ACCOUNTING.json",
                 "authentication.schema.json", "source_bridge.py", "current_context_sessions.py", "current_machine_context_scope.py", "machine_auth_scope.py"]
}
row_occurrences = 0
role_counts = {}
for role in ["source", "reader", "mapped", "context"]:
    manifest = json.loads((FAMILY / role / "source-manifest.json").read_text())
    rows = manifest["files"]
    for row in rows:
        capture(row)
    normalized = {str(Path(r["path"]).relative_to(ROOT)) if Path(r["path"]).is_absolute() else r["path"] for r in rows}
    assert not normalized & forbidden
    assert all(row in rows for row in snapshots)
    role_counts[role] = len(rows)
    row_occurrences += len(rows)
for role in ["source", "mapped", "context"]:
    manifest = json.loads((FAMILY / role / "packages/0001/manifest.json").read_text())
    for row in manifest["files"]:
        capture(row)
    role_counts[role + "_package"] = len(manifest["files"])
    row_occurrences += len(manifest["files"])
assert row_occurrences == 8191
preview = json.loads((FAMILY / "source-closure-preview.json").read_text())
assert preview["source_manifest_value"] == json.loads((FAMILY / "source/source-manifest.json").read_text())
period = json.loads(capture(selection["family_bindings"]["period_binding"]))
dt = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
assert (dt(period["expires_at"]) - dt(period["not_before"])).total_seconds() == 86400
assert period["actual_owner_outcome"] is None and period["authority_effect"] == "none"
capture(period["original_expired_period_binding"])
native = json.loads((FAMILY / "mapped/source-manifest.json").read_text())["native_executable_binding"]
capture(native)
assert native["sha256"] == "fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c" and native["required_mode"] == 0o755
phases = []
for phase_row in selection["phase_reports"]:
    report = json.loads(capture(phase_row))
    assert report["result"] == "PASS" and report["error"] is None and report["instance"] == "optimized-0005"
    phases.append(report["phase"])
assert phases == ["source", "cold", "reader", "mapped", "context"]
build = json.loads((FAMILY / "context/packages/0001/build-result.json").read_text())
assert build["result"] == "PASS" and build["actual_generated_artifact_carriers"] == 40
for key in ["actual_original_schema_validation", "real_nonce_transport_authentication", "owned_host_policy_and_transport_key_removed", "source_and_native_cuts_distinct"]:
    assert build[key] is True
assert build["active_Agents_created"] == build["public_API_operations_added"] == 0
assert not Path(build["owned_host_root"]).exists()

# Execute only the captured, previously reviewed pure text transform; never stage().
stager_path = PACKAGE / "stage_runtime_optimized_v5.py"
stager_raw = capture({"path": stager_path.relative_to(ROOT).as_posix(), "sha256": "44116401b67a49f6429fc39bef2c5af9ce5024dec054e70cb1055b707deddd04"})
stager_ast = ast.parse(stager_raw)
nodes = [n for n in stager_ast.body if isinstance(n, ast.FunctionDef) and n.name == "transform"]
old_family = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0002/instances/optimized-0002"
new_family = FAMILY.relative_to(ROOT).as_posix()
namespace = {"ast": ast, "json": json, "OLD_FAMILY": old_family, "OLD_PUBLIC": "completion-current-participation:optimized-0002", "NEW_PUBLIC": "completion-current-participation:optimized-0005"}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(stager_path), "exec"), namespace)
old_descriptor = json.loads(capture(baseline["fixed_runtime_descriptor_binding"]))
mapping = {old_family: new_family, "completion-current-participation:optimized-0002": "completion-current-participation:optimized-0005",
           "completion-optimized-source8-0002-optimized-0002": "completion-optimized-source8-0005-optimized-0005",
           "_cal_api17_current_source8_optimized_0002": "_cal_api17_current_source8_optimized_0005"}
changed = []
same = []
for row in overlay["rows"]:
    name = Path(row["original"]["path"]).name
    old_raw = capture(row["snapshot"])
    assert capture(row["original"]) == old_raw
    new_raw = capture(row["postimage"])
    fields = ["context_source_binding"] if name in ["source_bridge.py", "machine_auth_scope.py"] else ["context_source_binding", "mapper_package_binding"] if name == "current_context_sessions.py" else []
    replacements = {**mapping, **{old_descriptor[key]["sha256"]: runtime[key]["sha256"] for key in fields}}
    assert namespace["transform"](old_raw.decode(), name, old_descriptor, runtime, new_family).encode() == new_raw
    if name.endswith(".py"):
        before = ast.parse(old_raw)
        after = ast.parse(new_raw)
        allowed = {new: old for old, new in replacements.items()}
        class Undo(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    for new, old in allowed.items():
                        node.value = node.value.replace(new, old)
                return node
        after = Undo().visit(after)
        assert ast.dump(before, include_attributes=False) == ast.dump(after, include_attributes=False), name
    else:
        def undo(value):
            if isinstance(value, dict):
                return {k: undo(v) for k, v in value.items()}
            if isinstance(value, list):
                return [undo(v) for v in value]
            return value.replace(mapping["completion-current-participation:optimized-0002"], "completion-current-participation:optimized-0002") if isinstance(value, str) else value
        assert json.loads(old_raw) == undo(json.loads(new_raw))
        assert new_raw.count(b"completion-current-participation:optimized-0005") == 4
    (same if old_raw == new_raw else changed).append(name)
assert len(changed) == 4 and same == ["current_machine_context_scope.py"]
assert all(not json.loads((FAMILY / role / "source-manifest.json").read_text()).get("shared_API_qualified", False) for role in ["source", "reader", "mapped", "context"])
assert runtime["actual_human_review"] is False and runtime["actual_owner_outcome"] is None and runtime["shared_API_qualified"] is False
result = {"schema_version": "lab-T02-independent-actual-family-selector-controls/v1-candidate", "result": "PASS",
          "role_and_package_row_occurrences_freshly_verified": row_occurrences, "row_counts": role_counts,
          "all_six_historical_snapshots_in_each_role": True, "nine_live_mutable_API_inputs_absent_in_each_role": True,
          "actual_Source_equals_preconstruction_preview": True, "native_exact_sha_and_mode": True,
          "actual_five_phase_metadata_PASS": phases, "fixed_source_period_seconds": 86400,
          "actual_Context_carriers": 40, "owned_Context_host_root_removed": True,
          "selector_transform_exact_byte_matches": 5, "python_algorithms_AST_conserved": 4,
          "authentication_schema_only_four_source_name_sites": True, "changed_selectors": changed, "unchanged_selectors": same,
          "current_API_or_900_second_learning_qualified": False, "historical_Context_is_later_permission": False,
          "private_original_bodies_exported": False, "Lab_or_native_or_live_guard_executed": False}
with (HERE / "actual-family-selector-checks-0001.json").open("x") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(result))
