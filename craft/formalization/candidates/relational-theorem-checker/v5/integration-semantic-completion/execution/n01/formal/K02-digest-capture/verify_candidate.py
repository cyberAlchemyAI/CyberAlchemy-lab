"""Rebuild and replay digest-checked byte capture/catalog composition; never accept or discharge it."""
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
    dependencies = [(HERE.parent/name).resolve() for name in ['../../../../../v3/e00/ExpressionSemantics.lean', '../../../SharedSemantics.lean', 'K00/ActsForCandidate.lean', 'K02/IntentAddressingCandidate.lean', 'K02-source/TokenResolution.lean', 'K02-catalog/FiniteSourceCatalog.lean', 'K02-owned-qualifiers/OwnedBindingCatalog.lean', 'K02-json/ClosedJsonObject.lean', 'K02-json/JsonElements.lean', 'K02-binding-ast/BindingAstCombinators.lean', 'K02-binding-ast/BindingReferences.lean', 'K02-binding-ast/BindingTargets.lean', 'K02-numeric/DecimalMeaning.lean', 'K02-numeric/DecimalEpochCheck.lean', 'K02-numeric/DecimalGrammar.lean', 'K02-number-parser/NumberDigitScan.lean', 'K02-number-parser/NumberTokenParser.lean', 'K02-number-parser/NumberGrammarComplete.lean', 'K02-number-parser/NumberEpochAst.lean', 'K02-binding-records/BindingFrame.lean', 'K02-binding-records/BindingRecord.lean', 'K02-binding-capture/CaptureEnvelope.lean', 'K02-binding-capture/CapturePolicies.lean', 'K02-binding-capture/CaptureCatalog.lean', 'K02-binding-capture/CaptureControls.lean', 'K02-json-bytes/Utf8Meaning.lean', 'K02-json-bytes/Utf8Prefix.lean', 'K02-json-bytes/Utf8Stream.lean', 'K02-json-bytes/JsonDocumentMeaning.lean', 'K02-json-tokens/TokenMeaning.lean', 'K02-json-tokens/PrefixScan.lean', 'K02-json-tokens/LiteralDecoder.lean', 'K02-json-tokens/NumberPrefixDecoder.lean', 'K02-json-strings/StringEscapes.lean', 'K02-json-strings/StringUnitDecoder.lean', 'K02-json-strings/QuotedStringDecoder.lean', 'K02-json-parser/ParserMeaning.lean', 'K02-json-parser/PrimitiveDecoder.lean', 'K02-json-parser/RecursiveJsonParser.lean', 'K02-json-soundness/GrammarReconstruction.lean', 'K02-json-soundness/RecursiveSoundness.lean', 'K02-json-soundness/DocumentSoundness.lean', 'K02-json-completeness/GrammarStarts.lean', 'K02-json-completeness/CompletenessInterfaces.lean', 'K02-json-completeness/RecursiveCompleteness.lean', 'K02-json-completeness/DocumentExactness.lean', 'K02-scalar-conversion/ScalarStringMeaning.lean', 'K02-scalar-conversion/ScalarStringDecoder.lean', 'K02-scalar-conversion/ScalarValueMeaning.lean', 'K02-scalar-conversion/ScalarValueDecoder.lean', 'K02-scalar-conversion/ScalarDocumentComposition.lean', 'K02-scalar-conversion/ScalarConversionControls.lean', 'K02-binding-bytes/BindingRecordBytes.lean', 'K02-binding-bytes/BindingBytesOutcomes.lean', 'K02-binding-bytes/CaptureBytes.lean', 'K02-binding-bytes/CaptureByteOutcomes.lean', 'K02-binding-bytes/CaptureBytesCatalog.lean', 'K02-binding-bytes/OriginalByteControls.lean', 'K02-binding-bytes/ByteCaptureControls.lean', 'K02-digest/DigestMeaning.lean', 'K02-digest/DigestEvaluator.lean', 'K02-digest/DigestRefinement.lean', 'K02-digest/DigestProfile.lean', 'K02-digest/DigestControls.lean']]
    new_sources = [HERE/name for name in ['DigestCapture.lean', 'DigestCapturePolicies.lean', 'DigestCaptureOutcomes.lean', 'DigestCaptureCatalog.lean', 'DigestCaptureControls.lean', 'DigestCaptureRuntimeControls.lean']]
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
    controls=json.loads((HERE/'control-index.json').read_text())
    literal_source=(HERE.parent/'K02-binding-bytes/OriginalByteControls.lean').read_text()
    fixture_source=(HERE/'DigestCaptureControls.lean').read_text()
    runtime_source=(HERE/'DigestCaptureRuntimeControls.lean').read_text()
    for row in controls['original_fixtures']:
        name=row['kind']
        match=re.search(r'^def '+name+r'Bytes : CandidateJsonBytes.Bytes := \[(.*?)\]$',literal_source,re.M)
        assert match
        data=bytes(int(x) for x in match.group(1).split(',') if x.strip())
        assert data==(ROOT/row['original_bytes']['path']).read_bytes()
        assert len(data)==row['byte_count'] and hashlib.sha256(data).hexdigest()==row['computed_sha256']
        expected='def '+name+'Capture : CandidateBindingCapture.Envelope := ⟨'+name+'Bytes,'+str(row['byte_count'])+',profile.ref,'+json.dumps(row['computed_sha256'])+'⟩'
        assert expected in fixture_source
    actual_expressions=re.findall(r'^#eval (.*)$',runtime_source,re.M)
    assert actual_expressions==[row['expression'] for row in controls['runtime_cases']]

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
            if source.stem=='DigestCaptureRuntimeControls':
                expected_runtime=[row['expected_json'] for row in controls['runtime_cases']]
                assert result.stdout.strip().splitlines()==expected_runtime, source.stem
                record['runtime_composed_cases']=len(controls['runtime_cases'])
            records.append(record)
            (HERE / "verification-in-progress.json").write_text(
                json.dumps(records, indent=2) + "\n")
            print(phase, source.stem, result.returncode, record["seconds"], flush=True)
            assert result.returncode == 0, result.stdout
            assert "warning:" not in result.stdout, result.stdout
            assert count == expected, (source, count, expected)
            assert set(axioms) <= allowed, axioms
    assert captured == [binding(source) for source in sources]
    report={"task":"N01","unit":"K02-digest-capture","result":"candidate-fragment-pass",
      "method":"fresh isolated pinned Lean compilation and separate fresh same-kernel replay; exact computed-fixture byte and runtime outcome comparisons",
      "toolchain_lock":binding(lock_path),"compiler":binding(lean),"kernel_library":binding(kernel),
      "driver":binding(Path(__file__)),"context_pack":binding(HERE/'context-pack.json'),"source_capture":binding(capture_path),
      "sources":captured,"records":records,"new_declarations":declarations,"new_declaration_count":len(declarations),
      "new_general_declarations":49,"new_worked_control_declarations":12,"allowed_axioms":sorted(allowed),
      "control_index":binding(HERE/'control-index.json'),"runtime_composed_cases":len(controls['runtime_cases']),
      "digest_capture_pipeline_composed":True,"digest_capture_exactness_proved":True,
      "digest_capture_all_input_catalog_exactness_proved":True,"digest_capture_envelope_order_retention_proved":True,
      "digest_capture_direct_refusal_meanings_proved":True,"capture_parse_digest_policy_adapters_implemented":True,
      "capture_remaining_policies_unchanged_proved":True,"capture_conditional_authentication_bridge_proved":True,
      "configured_catalog_resource_guards_proved":True,"whole_original_fixture_runtime_composition_checked":True,
      "original_positive_kernel_hash_controls":False,"profile_and_owner_review_roots_synthetic":True,
      "claim_scope":"Exact candidate SHA-256/profile/resource and original bytes-to-binding/frame capture composition, lossless ordered all-input records and roots, existing structural catalog meaning, explicit aggregate/count budgets and independent direct refusal meanings. Parse/digest policy adapter implemented; authentic profile ownership, Schema and review remain separate premises.",
      "authenticated_digest_profile_selection_proved":False,"authenticated_capture_proved":False,
      "authenticated_full_source_policy_realization_proved":False,"JSON_schema_semantics_interpreter_proved":False,
      "whole_K02_source_refinement_proved":False,"raw_source_refinement_proved":False,"independent_checker_run":False,
      "external_standard_translation_reviewed":False,"collision_freedom_proved":False,
      "supported_resource_envelope_measured":False,"public_outcome_classification_implemented":False,
      "inherited_discharges":0,"N01_accepted":False,"authority_effect":"none"}
    assert len(declarations)==61
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    run()
