"""Build the fresh verifier with canonical paths for formal dependencies across versions."""
from pathlib import Path
import json,re,os
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];F=HERE.parent;OLD=F/'K02-scalar-conversion'
def run():
    paths=[]
    for pkg in ['K02-binding-capture','K02-scalar-conversion']:
        for item in json.loads((F/pkg/'verification.json').read_text())['sources']:
            file=ROOT/item['path']
            if file not in paths:paths.append(file)
    assert len(paths)==52
    newNames=['BindingRecordBytes.lean','BindingBytesOutcomes.lean','CaptureBytes.lean','CaptureByteOutcomes.lean','CaptureBytesCatalog.lean','OriginalByteControls.lean','ByteCaptureControls.lean']
    s=(OLD/'verify_candidate.py').read_text()
    s=re.sub(r'^    dependencies = .*$', '    dependencies = [(HERE.parent / name).resolve() for name in '+repr([os.path.relpath(x,F) for x in paths])+']',s,flags=re.M)
    s=re.sub(r'^    new_sources = .*$', '    new_sources = [HERE / name for name in '+repr(newNames)+']',s,flags=re.M)
    s=s.replace('K02 scalar representation and byte composition candidate','K02 original byte-record/capture/catalog candidate').replace('"unit": "K02-scalar-conversion"','"unit": "K02-binding-bytes"')
    marker='    check_bindings(capture)';assert s.count(marker)==1
    s=s.replace(marker,marker+'''
    # Match kernel-input UInt8 literals to exact original files, not supplied ASTs.
    original_control = (HERE / "OriginalByteControls.lean").read_text()
    for fixture in capture["original_fixtures"]:
        kind = fixture["kind"]
        match = re.search(r"^def " + kind + r"Bytes : CandidateJsonBytes.Bytes := \\[(.*?)\\]$", original_control, re.M)
        assert match, kind
        actual = bytes(int(token) for token in match.group(1).split(",") if token.strip())
        original = ROOT / fixture["original_bytes"]["path"]
        assert actual == original.read_bytes()
        assert len(actual) == fixture["byte_length"]
''')
    a=s.index('              "claim_scope":');z=s.index('    (HERE / "verification.json").write_text',a)
    block='''              "claim_scope": "Exact independent original byte-to-complete-binding-record and retained-envelope/frame/list/catalog preparation, with distinct raw syntax, unsupported scalar, record shape, envelope and stale-frame meanings. Forty-four general results plus twenty-eight kernel controls, including original resolution/role byte fixture parsing and old unrelated-AST versus new byte-interface regression. Capture parse predicate is implemented; remaining digest/owned-profile/Schema/review providers and nineteen complete source policies are not realized or authenticated.",
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
'''
    s=s[:a]+block+s[z:];(HERE/'verify_candidate.py').write_text(s)
    s=(OLD/'audit_imports.py').read_text().replace('K02 scalar conversion/composition','K02 byte-record/capture/catalog').replace('"unit": "K02-scalar-conversion"','"unit": "K02-binding-bytes"');(HERE/'audit_imports.py').write_text(s)
    print('Prepared fresh verifier: 52 dependencies, 7 new modules and 72 declarations.')
if __name__=='__main__':run()
