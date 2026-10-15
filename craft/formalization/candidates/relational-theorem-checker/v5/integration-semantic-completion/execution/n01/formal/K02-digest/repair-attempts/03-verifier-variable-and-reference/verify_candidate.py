"""Rebuild and replay the exact-byte digest candidate; never accept or discharge it."""
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
    dependencies = [BASE/'v3/e00/ExpressionSemantics.lean', SUCCESSOR/'SharedSemantics.lean']
    new_sources = [HERE/name for name in ['DigestMeaning.lean', 'DigestEvaluator.lean', 'DigestRefinement.lean', 'DigestProfile.lean', 'DigestControls.lean', 'DigestRuntimeControls.lean']]
    sources = dependencies + new_sources
    captured = [binding(source) for source in sources]
    allowed = {"propext", "Quot.sound", "Classical.choice"}
    declarations = []
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
            elif re.match(r"^(mutual|section(?: [\w.]+)?)$", line):
                namespace.append(None)
            elif ended:
                namespace.pop()
            elif theorem:
                declarations.append(".".join([part for part in namespace if part is not None] + [theorem.group(1)]))
    context = json.loads((HERE / "context-pack.json").read_text())
    for item in context["selected_sources"]:
        assert binding(ROOT / item["path"])["sha256"] == item["sha256"], item["path"]
    capture_path = HERE / "source-capture.json"
    capture = json.loads(capture_path.read_text())
    def check_bindings(value):
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                assert binding(ROOT / value["path"]) == value
            for child in value.values():
                check_bindings(child)
        elif isinstance(value, list):
            for child in value:
                check_bindings(child)
    check_bindings(capture)
    controls = json.loads((HERE/'runtime-control-index.json').read_text())
    runtime_source = (HERE/'DigestRuntimeControls.lean').read_text()
    for i,case in enumerate(controls['cases']):
        match=re.search(r'^def bytes'+str(i)+r' : Bytes := \[(.*?)\]$',runtime_source,re.M)
        assert match
        data=bytes(int(x) for x in match.group(1).split(',') if x.strip())
        assert data.hex()==case['input_hex'] and len(data)==case['byte_length']
        assert hashlib.sha256(data).hexdigest()==case['expected_sha256']
        if case.get('original_bytes'):assert data==(ROOT/case['original_bytes']['path']).read_bytes()

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
            try:
                result = subprocess.run(argv, cwd=source.parent,
                                        env=dict(os.environ, LEAN_PATH=str(build)),
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, timeout=240)
            except subprocess.TimeoutExpired as error:
                partial = error.stdout or ""
                if isinstance(partial, bytes):
                    partial = partial.decode("utf-8", errors="replace")
                log.write_text(partial)
                failure = {"phase": phase, "source": binding(source), "argv": argv,
                           "timeout_seconds": 240, "terminal": True,
                           "result": "timeout-not-verified", "log": binding(log),
                           "successful_invocations": len(records),
                           "driver": binding(Path(__file__)), "inherited_discharges": 0}
                (HERE / "verification-failure.json").write_text(
                    json.dumps(failure, indent=2) + "\n")
                print(phase, source.stem, "timeout-not-verified", flush=True)
                raise
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
            if source.stem=='DigestRuntimeControls':
                lines=result.stdout.strip().splitlines()
                expected=[json.dumps(c['expected_sha256']) for c in controls['cases']]+[c['expected'] for c in controls['refusal_cases']]
                assert lines==expected, (lines,expected)
                record['runtime_digest_cases']=len(controls['cases'])
                record['runtime_submitted_capture_cases']=len(controls['refusal_cases'])
            records.append(record)
            (HERE / "verification-in-progress.json").write_text(
                json.dumps(records, indent=2) + "\n")
            print(phase, source.stem, result.returncode, record["seconds"], flush=True)
            assert result.returncode == 0, result.stdout
            assert "warning:" not in result.stdout, result.stdout
            assert count == expected, (source, count, expected)
            assert set(axioms) <= allowed, axioms
    assert captured == [binding(source) for source in sources]
    report = {"task":"N01","unit":"K02-digest","result":"candidate-fragment-pass",
      "method":"fresh pinned Lean compilation and separate fresh same-kernel replay; differential runtime cases against Python hashlib",
      "toolchain_lock":binding(lock_path),"compiler":binding(lean),"kernel_library":binding(kernel),
      "driver":binding(Path(__file__)),"context_pack":binding(HERE/'context-pack.json'),"source_capture":binding(capture_path),
      "sources":captured,"records":records,"new_declarations":declarations,"new_declaration_count":len(declarations),
      "new_general_declarations":48,"new_worked_control_declarations":13,"allowed_axioms":sorted(allowed),
      "digest_algorithm_realized":True,"digest_independent_meaning_exactness_proved":True,
      "digest_algorithm_domain_totality_proved":True,"digest_hex_representation_proved":True,
      "digest_full_profile_ref_equality_proved":True,"digest_outcome_exactness_proved":True,
      "runtime_digest_cases":len(controls['cases']),"runtime_submitted_capture_cases":len(controls['refusal_cases']),
      "runtime_control_index":binding(HERE/'runtime-control-index.json'),
      "claim_scope":"SHA-256 byte-domain padding, ordered lossless block partition, 64-word schedule, 64-round compression, ordered message chain and exact lowercase full digest. Complete submitted RevisionRef equality and budget/profile/digest outcomes. External standard translation and authentic profile selection remain pending.",
      "digest_capture_pipeline_composed":False,"authenticated_digest_profile_selection_proved":False,
      "authenticated_capture_proved":False,"whole_K02_source_refinement_proved":False,
      "raw_source_refinement_proved":False,"independent_checker_run":False,
      "external_standard_translation_reviewed":False,"NIST_FIPS_validated":False,
      "collision_freedom_proved":False,"supported_resource_envelope_measured":False,
      "inherited_discharges":0,"N01_accepted":False,"authority_effect":"none"}
    assert len(declarations)==61
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
