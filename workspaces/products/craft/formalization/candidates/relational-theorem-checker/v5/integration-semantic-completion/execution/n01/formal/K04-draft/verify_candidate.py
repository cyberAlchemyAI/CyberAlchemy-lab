#!/usr/bin/env python3
"""Verify only this candidate; never change acceptance, plan or discharge state."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "authority/artifact-types").is_dir())
BASE = ROOT / "craft/formalization/candidates/relational-theorem-checker"
N = HERE.parent.parent
H = N.parent.parent
LEAN = BASE / "v1/formal/.toolcache/lean-4.33.1-linux/bin/lean"
LOCK = BASE / "v1/formal/toolchain-lock.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}

def run(command, workdir, env):
    result = subprocess.run(command, cwd=workdir, env=env, text=True,
                            capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not result.stderr.strip(), result.stderr
    assert "warning:" not in result.stdout, result.stdout
    return result.stdout

lock = json.loads(LOCK.read_text())
assert sha(LEAN) == lock["lean_binary_sha256"]
kernel = LEAN.parent.parent / "lib/lean/libleanshared.so"
assert sha(kernel) == lock["lean_shared_library_sha256"]
request = json.loads((N / "K04-assessment-request.json").read_text())
assert request["status"] == "pending-actual-response" and request["actual_response"] is None
sources = [request[k] for k in ["definition", "brief", "explanation", "source_declaration"]]
sources += request["source_shapes"]
for item in sources:
    assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
seq = json.loads((N / "sequential-review.json").read_text())
assert seq["current_unit"] == "K04"
accepted = [u["unit"] for u in seq["units"] if u.get("actual_assessment")]
assert accepted == ["K00", "K01", "K02", "K03"], accepted

protected_paths = [N / "sequential-review.json", N / "decision-gate.json",
                   N / "K04-assessment-request.json", H / "execution/plan.json",
                   BASE / "v4/gate-closure/execution/closure-completion.json"]
protected = [binding(path) for path in protected_paths]
assert protected[-1]["sha256"] == "1285904666f64cae5e586eb8a556c6e4e6e1be4aeb5d14af71e3a8c0effbfc04"
modules = ["LessonUseCandidate", "LessonUseControls"]
theorems = []
for module in modules:
    source = (HERE / f"{module}.lean").read_text()
    assert not re.search(r"\b(sorry|admit|axiom|native_decide|unsafe)\b", source)
    prefix = "CandidateLessonUse.Controls" if module.endswith("Controls") else "CandidateLessonUse"
    theorems.extend(f"{prefix}.{name}" for name in re.findall(r"^theorem (\w+)", source, re.M))
assert len(theorems) == len(set(theorems))
phases = []
with tempfile.TemporaryDirectory(prefix="k04-candidate-") as temporary:
    for phase in ["compile", "replay"]:
        workdir = Path(temporary) / phase
        workdir.mkdir()
        for module in modules:
            (workdir / f"{module}.lean").write_bytes((HERE / f"{module}.lean").read_bytes())
        env = {**os.environ, "LEAN_PATH": str(workdir)}
        imports = []
        for module in modules:
            deps = run([str(LEAN), "--deps", f"{module}.lean"], workdir, env)
            for line in deps.splitlines():
                path = Path(line.strip()).resolve()
                assert path.is_relative_to(workdir) or path.is_relative_to(LEAN.parent.parent / "lib/lean"), str(path)
                imports.append(str(path))
            output = run([str(LEAN), "-o", f"{module}.olean", f"{module}.lean"], workdir, env)
            assert not output.strip(), output
        probe = workdir / "Audit.lean"
        probe.write_text("import LessonUseControls\n" + "\n".join(
            f"#print axioms {name}" for name in theorems) + "\n")
        axioms = run([str(LEAN), str(probe)], workdir, env)
        inspections = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", axioms, re.S)
        assert len(inspections) == len(theorems), axioms
        assert {name for name, _ in inspections} == set(theorems)
        for _, listed in inspections:
            assert set(re.findall(r"[A-Za-z][A-Za-z0-9_.]*", listed)) <= {"propext", "Quot.sound", "Classical.choice"}, listed
        (HERE / f"{phase}-axioms.txt").write_text(axioms)
        phases.append({"phase": phase, "fresh_module_compilations": len(modules),
                       "axiom_inspections": len(inspections), "import_paths": imports,
                       "axiom_log": binding(HERE / f"{phase}-axioms.txt")})
for item in protected + sources:
    assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
report = {
    "schema": "relational.k04-candidate-verification/v1", "result": "pass",
    "unit": "K04", "status": "candidate-awaiting-owner-assessment",
    "source_bindings": sources, "protected_bindings": protected,
    "module_bindings": [binding(HERE / f"{module}.lean") for module in modules],
    "verifier": binding(Path(__file__).resolve()), "toolchain_lock": binding(LOCK),
    "lean_binary_sha256": sha(LEAN), "kernel_sha256": sha(kernel),
    "phases": phases, "candidate_declarations": len(theorems), "theorems": theorems,
    "general_theorems": sum(not name.startswith("CandidateLessonUse.Controls.") for name in theorems),
    "worked_controls": sum(name.startswith("CandidateLessonUse.Controls.") for name in theorems),
    "checked": ["independent finite meaning", "checker and diagnostics equivalence",
                "exact qualifier joins", "use and deliberate non-use witnesses",
                "selection and presentation refusal", "captured disposition required",
                "conflict and override retention", "qualified recording and protected-state preservation"],
    "not_established": ["actual semantic-owner acceptance", "global D03/D04 acceptance",
        "authenticated catalogs", "complete original-body decoding and source refinement",
        "policy-code provider", "admitted schemas or instances", "complete pinned-theory countermodels",
        "public API integration", "independent checker", "N01 completion"],
    "registered_in_main_preparation_index": False,
    "independent_verification": False, "raw_source_refinement": False,
    "inherited_discharges": 0, "N01_accepted": False, "goal_complete": False,
    "pending_ids": request["pending_ids"], "authority_effect": "none"
}
(HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: report[key] for key in ["result", "candidate_declarations",
      "general_theorems", "worked_controls", "inherited_discharges", "N01_accepted"]}))
