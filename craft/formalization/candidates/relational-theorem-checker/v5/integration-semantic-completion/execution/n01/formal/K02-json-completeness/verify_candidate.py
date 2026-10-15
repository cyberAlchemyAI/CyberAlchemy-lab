"""Rebuild and replay the K02 complete JSON grammar refinement candidate; never accept or discharge it."""
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
    dependencies = [HERE.parent / name for name in ['K02-json/ClosedJsonObject.lean','K02-numeric/DecimalMeaning.lean','K02-numeric/DecimalEpochCheck.lean','K02-numeric/DecimalGrammar.lean','K02-number-parser/NumberDigitScan.lean','K02-number-parser/NumberTokenParser.lean','K02-number-parser/NumberGrammarComplete.lean','K02-json-bytes/Utf8Meaning.lean','K02-json-bytes/Utf8Prefix.lean','K02-json-bytes/Utf8Stream.lean','K02-json-bytes/JsonDocumentMeaning.lean','K02-json-tokens/TokenMeaning.lean','K02-json-tokens/PrefixScan.lean','K02-json-tokens/LiteralDecoder.lean','K02-json-tokens/NumberPrefixDecoder.lean','K02-json-strings/StringEscapes.lean','K02-json-strings/StringUnitDecoder.lean','K02-json-strings/QuotedStringDecoder.lean','K02-json-parser/ParserMeaning.lean','K02-json-parser/PrimitiveDecoder.lean','K02-json-parser/RecursiveJsonParser.lean','K02-json-soundness/GrammarReconstruction.lean','K02-json-soundness/RecursiveSoundness.lean','K02-json-soundness/DocumentSoundness.lean']]
    new_sources = [HERE / name for name in ['GrammarStarts.lean','CompletenessInterfaces.lean','RecursiveCompleteness.lean','DocumentExactness.lean']]
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
    report = {"task": "N01", "unit": "K02-json-completeness", "result": "candidate-fragment-pass",
              "method": "fresh pinned Lean compilation and separate fresh replay",
              "toolchain_lock": binding(lock_path), "compiler": binding(lean),
              "kernel_library": binding(kernel), "driver": binding(Path(__file__)),
              "context_pack": binding(HERE / "context-pack.json"),
              "sources": captured, "records": records, "new_declarations": declarations,
              "new_declaration_count": len(declarations), "allowed_axioms": sorted(allowed),
              "claim_scope": "Full raw JSON grammar-derived recursive value/items/members completeness under an explicit consumed-word fuel bound; actual wrapper budget sufficiency; exact value/document and UTF-8 byte-document refinement, unique independent meanings and none iff no meaning. Completeness covers all thirteen pre-existing mutual grammar constructors, including ordered duplicate keys, original numeric lexemes and unpaired escaped UTF-16 units. Existing scalar-AST/source/authentication/standard/Schema/resources and mandatory independent closure remain open.",
              "source_capture": binding(capture_path),
              "complete_JSON_grammar_refinement_proved": True,
              "grammar_only_start_whitespace_lemmas_proved": True,
              "recursive_value_grammar_completeness_proved": True,
              "recursive_items_grammar_completeness_proved": True,
              "recursive_members_grammar_completeness_proved": True,
              "consumed_word_fuel_bound_proved": True,
              "recursion_budget_sufficiency_proved": True,
              "complete_JSON_parser_implemented": True,
              "complete_JSON_parser_soundness_proved": True,
              "complete_JSON_parser_completeness_proved": True,
              "complete_JSON_parser_proved": True,
              "wrapped_value_exactness_proved": True,
              "document_exactness_proved": True,
              "UTF8_byte_document_exactness_proved": True,
              "independent_meaning_uniqueness_proved": True,
              "none_iff_no_meaning_proved": True,
              "existing_scalar_AST_conversion_proved": False,
              "original_capture_to_AST_bridge_proved": False,
              "grammar_standard_translation_proved": False,
              "supported_resource_envelope_measured": False,
              "complete_frame_AST_proved": False,
              "complete_binding_record_AST_proved": False,
              "binding_record_AST_decoder_proved": False,
              "field_preserving_binding_record_AST_proved": False,
              "JSON_schema_semantics_interpreter_proved": False,
              "authenticated_full_source_policy_realization_proved": False,
              "binding_schema_AST_correspondence_proved": False,
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
