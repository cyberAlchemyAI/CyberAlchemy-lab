"""Fresh compilation and replay of the N00 model; no inherited discharge."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[3]
PROPOSAL = ROOT / "docs/plans/relational-theorem-checker/reviews/2026-10-10-extension-integration-semantic-completion"
OUT = HERE / "execution/n00"


def binding(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run() -> None:
    lock_path = BASE / "v1/formal/toolchain-lock.json"
    lock = json.loads(lock_path.read_text())
    runtime = BASE / "v1/formal/.toolcache/lean-4.33.1-linux"
    lean, kernel = runtime / "bin/lean", runtime / "lib/lean/libleanshared.so"
    assert binding(lean)["sha256"] == lock["lean_binary_sha256"]
    assert binding(kernel)["sha256"] == lock["lean_shared_library_sha256"]
    sources = [BASE / "v3/e00/ExpressionSemantics.lean"] + [HERE / (n + ".lean") for n in
        ["SharedSemantics", "CoverageSemantics", "N00Witnesses", "InheritedInventory"]]
    source_bindings = [binding(s) for s in sources]
    records = []
    allowed = {"propext", "Quot.sound", "Classical.choice"}
    new_declarations = []
    for src in sources[1:]:
        names = re.findall(r"^theorem\s+(\w+)", src.read_text(), re.M)
        inspected = re.findall(r"^#print axioms\s+(\w+)", src.read_text(), re.M)
        assert names == inspected, (src, names, inspected)
        assert not re.search(r"\b(sorry|admit|native_decide|axiom)\b", "\n".join(
            line for line in src.read_text().splitlines() if not line.lstrip().startswith("--")))
        new_declarations.extend(names)
    for phase in ["compile", "replay"]:
        build = OUT / phase
        build.mkdir(parents=True, exist_ok=True)
        # No previous olean is an input to this build. Imports use this phase's
        # fresh outputs and the pinned compiler's core library.
        for generated in build.glob("*.olean"):
            generated.unlink()
        for src in sources:
            assert binding(src) in source_bindings, "source drift during replay"
            output = build / (src.stem + ".olean")
            log = build / (src.stem + ".log")
            argv = [str(lean), "-o", str(output), str(src)]
            env = dict(os.environ, LEAN_PATH=str(build))
            start = time.monotonic()
            result = subprocess.run(argv, cwd=src.parent, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
            log.write_text(result.stdout)
            axiom_sets = re.findall(r"depends on axioms: \[([^]]*)\]", result.stdout)
            axioms = sorted({a.strip() for group in axiom_sets for a in group.split(",") if a.strip()})
            inspected_count = len(re.findall(r"(?:depends on axioms:|does not depend on any axioms)", result.stdout))
            expected = len(re.findall(r"^#print axioms ", src.read_text(), re.M))
            record = {"phase": phase, "source": binding(src), "argv": argv, "cwd": str(src.parent),
                      "LEAN_PATH": str(build), "seconds": round(time.monotonic() - start, 3),
                      "exit_code": result.returncode, "log": binding(log), "axioms": axioms,
                      "inspected_declarations": inspected_count}
            if output.exists():
                record["olean"] = binding(output)
            records.append(record)
            (OUT / "verification-in-progress.json").write_text(json.dumps(records, indent=2) + "\n")
            print(phase, src.stem, result.returncode, record["seconds"], flush=True)
            assert result.returncode == 0, result.stdout
            assert inspected_count == expected, (src, inspected_count, expected)
            assert set(axioms) <= allowed, axioms
            assert "warning:" not in result.stdout, result.stdout
    assert source_bindings == [binding(s) for s in sources]
    inventory = json.loads((PROPOSAL / "inherited-obligations.json").read_text())
    report = {"task": "N00", "result": "pass", "method": "fresh pinned Lean compilation and separate fresh replay",
              "toolchain_lock": binding(lock_path), "compiler": binding(lean), "kernel_library": binding(kernel),
              "sources": source_bindings, "driver": binding(Path(__file__)), "records": records,
              "shared_universal_theorems": 19, "coverage_universal_theorems": 14,
              "synthetic_witness_theorems": 12, "inventory_theorems": 2,
              "new_declarations": new_declarations, "allowed_axioms": sorted(allowed),
              "inherited_inventory": binding(PROPOSAL / "inherited-obligations.json"),
              "exact_inherited_ids": len(inventory["obligations"]), "inherited_discharges": 0,
              "authentic_owner_approvals_established": False, "independent_checker_run": False,
              "authority_effect": "none"}
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
