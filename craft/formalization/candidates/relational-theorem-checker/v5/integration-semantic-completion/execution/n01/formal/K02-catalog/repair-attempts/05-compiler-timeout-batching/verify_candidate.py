"""Rebuild and replay the K02 finite source catalog candidate; never accept or discharge it."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
SUCCESSOR = HERE.parents[3]
BASE = SUCCESSOR.parents[1]
ROOT = BASE.parents[3]


def binding(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run() -> None:
    lock_path = BASE / "v1/formal/toolchain-lock.json"
    lock = json.loads(lock_path.read_text())
    runtime = BASE / "v1/formal/.toolcache/lean-4.33.1-linux"
    lean = runtime / "bin/lean"
    kernel = runtime / "lib/lean/libleanshared.so"
    assert binding(lean)["sha256"] == lock["lean_binary_sha256"]
    assert binding(kernel)["sha256"] == lock["lean_shared_library_sha256"]
    sources = [BASE / "v3/e00/ExpressionSemantics.lean",
               SUCCESSOR / "SharedSemantics.lean",
               HERE.parent / "K00/ActsForCandidate.lean",
               HERE.parent / "K02/IntentAddressingCandidate.lean",
               HERE.parent / "K02-source/TokenResolution.lean",
               HERE.parent / "K02-source/RawIntentPayload.lean",
               HERE.parent / "K02-source/SourceFixture.lean",
               HERE / "FiniteSourceCatalog.lean", HERE / "GuardedIntentPayload.lean",
               HERE / "CatalogExamples.lean"]
    captured = [binding(source) for source in sources]
    allowed = {"propext", "Quot.sound", "Classical.choice"}
    declarations = []
    new_sources = [HERE / name for name in ["FiniteSourceCatalog.lean",
                  "GuardedIntentPayload.lean", "CatalogExamples.lean"]]
    for source in new_sources:
        text = source.read_text()
        names = re.findall(r"^theorem\s+(\w+)", text, re.M)
        inspected = [name.split(".")[-1] for name in re.findall(r"^#print axioms\s+([\w.]+)", text, re.M)]
        assert names == inspected, (source, names, inspected)
        code = "\n".join(line for line in text.splitlines()
                         if not line.lstrip().startswith("--"))
        assert not re.search(r"\b(sorry|admit|native_decide|axiom)\b", code)
        namespace = []
        for line in text.splitlines():
            entered = re.match(r"^namespace ([\w.]+)$", line)
            ended = re.match(r"^end(?: [\w.]+)?$", line)
            theorem = re.match(r"^theorem (\w+)", line)
            if entered:
                namespace.append(entered.group(1))
            elif ended:
                namespace.pop()
            elif theorem:
                declarations.append(".".join(namespace + [theorem.group(1)]))
    context = json.loads((HERE / "context-pack.json").read_text())
    for item in context["selected_sources"]:
        assert binding(ROOT / item["path"])["sha256"] == item["sha256"], item["path"]
    capture_path = HERE.parent / "K02-source/source-capture.json"
    capture = json.loads(capture_path.read_text())
    for value in capture.values():
        if isinstance(value, dict) and "path" in value and "sha256" in value:
            assert binding(ROOT / value["path"]) == value
    records = []
    for phase in ["compile", "replay"]:
        build = HERE / phase
        build.mkdir(exist_ok=True)
        for output in build.glob("*.olean"):
            output.unlink()
        for source in sources:
            assert binding(source) in captured, "source drift during compilation"
            output = build / (source.stem + ".olean")
            log = build / (source.stem + ".log")
            argv = [str(lean), "-o", str(output), str(source)]
            start = time.monotonic()
            result = subprocess.run(argv, cwd=source.parent,
                                    env=dict(os.environ, LEAN_PATH=str(build)),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, timeout=240)
            log.write_text(result.stdout)
            sets = re.findall(r"depends on axioms: \[([^]]*)\]", result.stdout)
            axioms = sorted({a.strip() for group in sets
                             for a in group.split(",") if a.strip()})
            count = len(re.findall(r"(?:depends on axioms:|does not depend on any axioms)",
                                   result.stdout))
            expected = len(re.findall(r"^#print axioms ", source.read_text(), re.M))
            record = {"phase": phase, "source": binding(source), "argv": argv,
                      "cwd": str(source.parent), "LEAN_PATH": str(build),
                      "seconds": round(time.monotonic() - start, 3),
                      "exit_code": result.returncode, "log": binding(log),
                      "axioms": axioms, "inspected_declarations": count}
            if output.exists():
                record["olean"] = binding(output)
            records.append(record)
            (HERE / "verification-in-progress.json").write_text(
                json.dumps(records, indent=2) + "\n")
            print(phase, source.stem, result.returncode, record["seconds"], flush=True)
            assert result.returncode == 0, result.stdout
            assert "warning:" not in result.stdout, result.stdout
            assert count == expected, (source, count, expected)
            assert set(axioms) <= allowed, axioms
    assert captured == [binding(source) for source in sources]
    report = {"task": "N01", "unit": "K02-catalog", "result": "candidate-fragment-pass",
              "method": "fresh pinned Lean compilation and separate fresh replay",
              "toolchain_lock": binding(lock_path), "compiler": binding(lean),
              "kernel_library": binding(kernel), "driver": binding(Path(__file__)),
              "context_pack": binding(HERE / "context-pack.json"),
              "sources": captured, "records": records, "new_declarations": declarations,
              "new_declaration_count": len(declarations), "allowed_axioms": sorted(allowed),
              "claim_scope": "Finite catalog structural invariant over full artifact/approval records, functional role/token bindings, exact captured frames, consistent alias resolution, and invariant-guarded K02 payload projection. Authentic capture, bytes/body correspondence, outer metadata/qualifier/Selection adapters and complete source/theory remain unproved.",
              "source_capture": binding(capture_path),
              "finite_catalog_invariant_proved": True,
              "guarded_payload_projection_proved": True,
              "authenticated_capture_proved": False,
              "raw_source_refinement_proved": False, "whole_K02_source_refinement_proved": False,
              "whole_rule_protected_state_closure_proved": False, "independent_checker_run": False,
              "inherited_discharges": 0, "N01_accepted": False, "authority_effect": "none"}
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
