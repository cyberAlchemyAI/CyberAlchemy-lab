"""Rebuild and replay the K02 captured owned qualifier lookup candidate; never accept or discharge it."""
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
    dependencies = [BASE / "v3/e00/ExpressionSemantics.lean",
                    SUCCESSOR / "SharedSemantics.lean",
                    HERE.parent / "K00/ActsForCandidate.lean",
                    HERE.parent / "K02/IntentAddressingCandidate.lean",
                    HERE.parent / "K02-source/TokenResolution.lean",
                    HERE.parent / "K02-source/RawIntentPayload.lean",
                    HERE.parent / "K02-outer/IntentRecordShape.lean",
                    HERE.parent / "K02-catalog/FiniteSourceCatalog.lean",
                    HERE.parent / "K02-catalog/GuardedIntentPayload.lean",
                    HERE.parent / "K02-json/ClosedJsonObject.lean",
                    HERE.parent / "K02-json/JsonElements.lean",
                    HERE.parent / "K02-json/JsonReference.lean",
                    HERE.parent / "K02-json/JsonPayload.lean",
                    HERE.parent / "K02-json/JsonRecord.lean",
                    HERE.parent / "K02-source/SourceFixture.lean",
                    HERE.parent / "K02-catalog/CatalogFixtures.lean",
                    HERE.parent / "K02-json/JsonEncoding.lean",
                    HERE.parent / "K02-json/JsonFixture.lean"]
    dependencies += [HERE.parent / "K02/IntentAddressingCheck.lean",
                     HERE.parent / "K02-metadata/CapturedMetadata.lean",
                     HERE.parent / "K02-metadata/MetadataSource.lean",
                     HERE.parent / "K02-metadata/MetadataProjection.lean",
                     HERE.parent / "K02-metadata/MetadataFixture.lean"]
    dependencies += [HERE.parent / "K02-source-contract/IntentQualifiers.lean",
                     HERE.parent / "K02-source-contract/FramedIntentJoin.lean",
                     HERE.parent / "K02-source-contract/SourcePolicyContract.lean",
                     HERE.parent / "K02-source-contract/FramedJoinFixture.lean"]
    new_sources = [HERE / name for name in ["OwnedBindingCatalog.lean", "JointBindingRevisions.lean", "OwnedIntentQualifierCheck.lean",
                   "OwnedQualifierFixture.lean", "OwnedQualifierControls.lean", "OwnedQualifierBranches.lean"]]
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
            elif ended:
                namespace.pop()
            elif theorem:
                declarations.append(".".join(namespace + [theorem.group(1)]))
    context = json.loads((HERE / "context-pack.json").read_text())
    for item in context["selected_sources"]:
        assert binding(ROOT / item["path"])["sha256"] == item["sha256"], item["path"]
    capture_path = HERE / "source-capture.json"
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
            records.append(record)
            (HERE / "verification-in-progress.json").write_text(
                json.dumps(records, indent=2) + "\n")
            print(phase, source.stem, result.returncode, record["seconds"], flush=True)
            assert result.returncode == 0, result.stdout
            assert "warning:" not in result.stdout, result.stdout
            assert count == expected, (source, count, expected)
            assert set(axioms) <= allowed, axioms
    assert captured == [binding(source) for source in sources]
    report = {"task": "N01", "unit": "K02-owned-qualifiers", "result": "candidate-fragment-pass",
              "method": "fresh pinned Lean compilation and separate fresh replay",
              "toolchain_lock": binding(lock_path), "compiler": binding(lean),
              "kernel_library": binding(kernel), "driver": binding(Path(__file__)),
              "context_pack": binding(HERE / "context-pack.json"),
              "sources": captured, "records": records, "new_declarations": declarations,
              "new_declaration_count": len(declarations), "allowed_axioms": sorted(allowed),
              "claim_scope": "Captured full revisioned qualifier binding denotations and executable resolver/checker equivalence; functional tokens, global record/target non-equivocation across aliases and roots, distinct consistent approvals, fixed source/Selection/full-frame joins and six synthetic typed branches. Authentication, binding-record byte parsing, whole source/theory refinement and independent closure remain open.",
              "source_capture": binding(capture_path),
              "captured_qualifier_binding_proved": True,
              "qualifier_source_selection_join_proved": True,
              "authenticated_qualifier_policy_realization_proved": False,
              "raw_binding_record_parser_proved": False,
              "byte_parser_proved": False,
              "candidate_parser_profile_owner_accepted": False,
              "authenticated_capture_proved": False,
              "raw_source_refinement_proved": False, "whole_K02_source_refinement_proved": False,
              "whole_rule_protected_state_closure_proved": False, "independent_checker_run": False,
              "inherited_discharges": 0, "N01_accepted": False, "authority_effect": "none"}
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
