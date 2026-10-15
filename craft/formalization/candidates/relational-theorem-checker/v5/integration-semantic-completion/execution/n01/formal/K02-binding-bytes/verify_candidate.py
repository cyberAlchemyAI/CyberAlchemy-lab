"""Rebuild and replay the K02 original byte-record/capture/catalog candidate; never accept or discharge it."""
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
    dependencies = [(HERE.parent / name).resolve() for name in ['../../../../../v3/e00/ExpressionSemantics.lean', '../../../SharedSemantics.lean', 'K00/ActsForCandidate.lean', 'K02/IntentAddressingCandidate.lean', 'K02-source/TokenResolution.lean', 'K02-catalog/FiniteSourceCatalog.lean', 'K02-owned-qualifiers/OwnedBindingCatalog.lean', 'K02-json/ClosedJsonObject.lean', 'K02-json/JsonElements.lean', 'K02-binding-ast/BindingAstCombinators.lean', 'K02-binding-ast/BindingReferences.lean', 'K02-binding-ast/BindingTargets.lean', 'K02-numeric/DecimalMeaning.lean', 'K02-numeric/DecimalEpochCheck.lean', 'K02-numeric/DecimalGrammar.lean', 'K02-number-parser/NumberDigitScan.lean', 'K02-number-parser/NumberTokenParser.lean', 'K02-number-parser/NumberGrammarComplete.lean', 'K02-number-parser/NumberEpochAst.lean', 'K02-binding-records/BindingFrame.lean', 'K02-binding-records/BindingRecord.lean', 'K02-binding-capture/CaptureEnvelope.lean', 'K02-binding-capture/CapturePolicies.lean', 'K02-binding-capture/CaptureCatalog.lean', 'K02-binding-capture/CaptureControls.lean', 'K02-json-bytes/Utf8Meaning.lean', 'K02-json-bytes/Utf8Prefix.lean', 'K02-json-bytes/Utf8Stream.lean', 'K02-json-bytes/JsonDocumentMeaning.lean', 'K02-json-tokens/TokenMeaning.lean', 'K02-json-tokens/PrefixScan.lean', 'K02-json-tokens/LiteralDecoder.lean', 'K02-json-tokens/NumberPrefixDecoder.lean', 'K02-json-strings/StringEscapes.lean', 'K02-json-strings/StringUnitDecoder.lean', 'K02-json-strings/QuotedStringDecoder.lean', 'K02-json-parser/ParserMeaning.lean', 'K02-json-parser/PrimitiveDecoder.lean', 'K02-json-parser/RecursiveJsonParser.lean', 'K02-json-soundness/GrammarReconstruction.lean', 'K02-json-soundness/RecursiveSoundness.lean', 'K02-json-soundness/DocumentSoundness.lean', 'K02-json-completeness/GrammarStarts.lean', 'K02-json-completeness/CompletenessInterfaces.lean', 'K02-json-completeness/RecursiveCompleteness.lean', 'K02-json-completeness/DocumentExactness.lean', 'K02-scalar-conversion/ScalarStringMeaning.lean', 'K02-scalar-conversion/ScalarStringDecoder.lean', 'K02-scalar-conversion/ScalarValueMeaning.lean', 'K02-scalar-conversion/ScalarValueDecoder.lean', 'K02-scalar-conversion/ScalarDocumentComposition.lean', 'K02-scalar-conversion/ScalarConversionControls.lean']]
    new_sources = [HERE / name for name in ['BindingRecordBytes.lean', 'BindingBytesOutcomes.lean', 'CaptureBytes.lean', 'CaptureByteOutcomes.lean', 'CaptureBytesCatalog.lean', 'OriginalByteControls.lean', 'ByteCaptureControls.lean']]
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
    # Match kernel-input UInt8 literals to exact original files, not supplied ASTs.
    original_control = (HERE / "OriginalByteControls.lean").read_text()
    for fixture in capture["original_fixtures"]:
        kind = fixture["kind"]
        match = re.search(r"^def " + kind + r"Bytes : CandidateJsonBytes.Bytes := \[(.*?)\]$", original_control, re.M)
        assert match, kind
        actual = bytes(int(token) for token in match.group(1).split(",") if token.strip())
        original = ROOT / fixture["original_bytes"]["path"]
        assert actual == original.read_bytes()
        assert len(actual) == fixture["byte_length"]

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
    report = {"task": "N01", "unit": "K02-binding-bytes", "result": "candidate-fragment-pass",
              "method": "fresh pinned Lean compilation and separate fresh replay",
              "toolchain_lock": binding(lock_path), "compiler": binding(lean),
              "kernel_library": binding(kernel), "driver": binding(Path(__file__)),
              "context_pack": binding(HERE / "context-pack.json"),
              "sources": captured, "records": records, "new_declarations": declarations,
              "new_declaration_count": len(declarations), "allowed_axioms": sorted(allowed),
              "claim_scope": "Exact independent original byte-to-complete-binding-record and retained-envelope/frame/list/catalog preparation, with distinct raw syntax, unsupported scalar, record shape, envelope and stale-frame meanings. Forty-four general results plus twenty-eight kernel controls, including original resolution/role byte fixture parsing and old unrelated-AST versus new byte-interface regression. Capture parse predicate is implemented; remaining digest/owned-profile/Schema/review providers and nineteen complete source policies are not realized or authenticated.",
              "source_capture": binding(capture_path),
              "new_general_declarations": 44,
              "new_worked_control_declarations": 28,
              "byte_record_and_capture_refinement_proved": True,
              "raw_binding_record_parser_proved": True,
              "binding_record_bytes_exactness_proved": True,
              "binding_record_all_fields_preserved": True,
              "original_capture_to_AST_bridge_proved": True,
              "original_binding_fixture_bytes_kernel_checked": True,
              "original_binding_fixture_count": 2,
              "byte_parser_proved": True,
              "retained_byte_envelope_frame_exactness_proved": True,
              "byte_catalog_staging_exactness_proved": True,
              "ordered_all_input_capture_meaning_proved": True,
              "record_outcome_exactness_proved": True,
              "capture_outcome_exactness_proved": True,
              "capture_direct_independent_refusal_meanings_proved": True,
              "capture_parser_policy_adapter_implemented": True,
              "remaining_capture_policies_unchanged_proved": True,
              "conditional_capture_evidence_bridge_proved": True,
              "unrelated_AST_byte_regression_refused": True,
              "existing_scalar_AST_conversion_proved": True,
              "composed_scalar_byte_parser_proved": True,
              "complete_JSON_parser_proved": True,
              "representation_outcome_classification_implemented": True,
              "record_capture_outcome_classification_implemented": True,
              "public_outcome_classification_implemented": False,
              "digest_algorithm_realized": False,
              "authenticated_capture_proved": False,
              "authenticated_full_source_policy_realization_proved": False,
              "JSON_schema_semantics_interpreter_proved": False,
              "binding_schema_AST_correspondence_proved": False,
              "grammar_standard_translation_proved": False,
              "candidate_parser_profile_owner_accepted": False,
              "supported_resource_envelope_measured": False,
              "raw_source_refinement_proved": False,
              "whole_K02_source_refinement_proved": False,
              "whole_rule_protected_state_closure_proved": False,
              "independent_checker_run": False,
              "inherited_discharges": 0, "N01_accepted": False, "authority_effect": "none"}
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
