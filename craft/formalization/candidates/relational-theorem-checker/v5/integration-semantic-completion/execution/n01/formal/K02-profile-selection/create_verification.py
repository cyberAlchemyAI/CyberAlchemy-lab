"""Generate a fresh verification protocol without changing registered predecessors."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
BASE = HERE.parent / 'K02-digest-capture'
MODULES = ['ProfileSources', 'ProfileSelectionData', 'ProfileSelectionPreparation',
           'ProfileSelectionEvidence', 'ProfileSelectionControls', 'ProfileSelectionRuntimeControls']


def binding(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    for stem in MODULES:
        path = HERE / (stem + '.lean')
        source = path.read_text()
        names = re.findall(r'^theorem (\w+)', source, re.M)
        if names and '#print axioms' not in source:
            marker = 'end RelationalSuccessor.CandidateProfileSelection'
            if stem == 'ProfileSelectionControls':
                marker += '.Controls'
            assert source.count(marker) == 1
            source = source.replace(marker, '\n'.join('#print axioms ' + name for name in names) + '\n' + marker)
            path.write_text(source)
    predecessor = json.loads((BASE / 'verification.json').read_text())
    dependencies = [ROOT / item['path'] for item in predecessor['sources']
                    if Path(item['path']).stem != 'DigestCaptureRuntimeControls']
    assert len(dependencies) == 69
    source = (BASE / 'verify_candidate.py').read_text()
    start = source.index('    dependencies =')
    end = source.index('    sources = dependencies + new_sources')
    source = source[:start] + '    dependencies = [(HERE.parent/name).resolve() for name in ' + repr([
        os.path.relpath(path, HERE.parent) for path in dependencies
    ]) + ']\n    new_sources = [HERE/name for name in ' + repr([stem + '.lean' for stem in MODULES]) + ']\n' + source[end:]
    start = source.index("    controls=json.loads")
    end = source.index('    records = []', start)
    source = source[:start] + '''    controls = json.loads((HERE / 'control-index.json').read_text())
    runtime_source = (HERE / 'ProfileSelectionRuntimeControls.lean').read_text()
    expressions = re.findall(r'^#eval (.*)$', runtime_source, re.M)
    assert expressions == [row['expression'] for row in controls['runtime_cases']]
    for index, row in enumerate(controls['fixtures']):
        original = (ROOT / row['original_bytes']['path']).read_bytes()
        assert binding(ROOT / row['original_bytes']['path']) == row['original_bytes']
        assert len(original) == row['byte_count']
        assert hashlib.sha256(original).hexdigest() == row['computed_digest']
        match = re.search(r'^def capture' + str(index) + r' : CandidateBindingCapture.Envelope := ⟨\\[(.*?)\\],(\\d+),bootstrap.ref,"([^"]+)"⟩$', runtime_source, re.M)
        assert match, (index, row['name'])
        literal = bytes(int(value) for value in match.group(1).split(',') if value.strip())
        assert literal == original
        assert int(match.group(2)) == row['byte_count'] and match.group(3) == row['submitted_digest']
    assert controls['kernel_controls_are_typed_data_only'] is True
    assert controls['profile_principal_bootstrap_review_roots_synthetic'] is True
    assert controls['authentic_evidence_provider_realized'] is False

''' + source[end:]
    source = source.replace("source.stem=='DigestCaptureRuntimeControls'", "source.stem=='ProfileSelectionRuntimeControls'")
    start = source.index('    report={')
    end = source.index('    (HERE / "verification.json").write_text', start)
    source = source[:start] + '''    report = {
        "task": "N01", "unit": "K02-profile-selection", "result": "candidate-fragment-pass",
        "method": "Fresh isolated pinned Lean compilation and separate fresh same-kernel replay; exact original-byte fixture and runtime comparisons",
        "toolchain_lock": binding(lock_path), "compiler": binding(lean), "kernel_library": binding(kernel),
        "driver": binding(Path(__file__)), "context_pack": binding(HERE/'context-pack.json'),
        "source_capture": binding(capture_path), "sources": captured, "records": records,
        "new_declarations": declarations, "new_declaration_count": len(declarations),
        "new_general_declarations": 28, "new_worked_control_declarations": 24,
        "allowed_axioms": sorted(allowed), "control_index": binding(HERE/'control-index.json'),
        "runtime_composed_cases": len(controls['runtime_cases']),
        "profile_source_decoders_exact": True, "profile_selection_data_exact": True,
        "captured_profile_selection_exact": True, "all_input_envelopes_retained": True,
        "full_reference_resolution_proved": True, "order_independent_conflict_refusal_proved": True,
        "profile_source_provenance_proved": True, "configured_source_budgets_proved": True,
        "explicit_ownership_evidence_contract": True, "ownership_policy_adapter_implemented": True,
        "other_capture_policies_unchanged_proved": True, "conditional_complete_capture_bridge_proved": True,
        "claim_scope": "Exact captured declaration/selection data preparation under explicit bootstrap and budgets; exact full references and frames, non-equivocating declarations, selection agreement, retained sources and recorded review/revocation/expiry guards. Owned profile meaning and capture bridge require actual external evidence.",
        "kernel_controls_are_typed_data_only": True, "profile_principal_bootstrap_review_roots_synthetic": True,
        "authentic_evidence_provider_realized": False, "authenticated_digest_profile_selection_proved": False,
        "authenticated_capture_proved": False, "authenticated_full_source_policy_realization_proved": False,
        "JSON_schema_semantics_interpreter_proved": False, "whole_K02_source_refinement_proved": False,
        "raw_source_refinement_proved": False, "independent_checker_run": False,
        "external_standard_translation_reviewed": False, "collision_freedom_proved": False,
        "supported_resource_envelope_measured": False, "public_outcome_classification_implemented": False,
        "N03_API_freeze": False, "inherited_discharges": 0, "N01_accepted": False, "authority_effect": "none"
    }
    assert len(declarations) == 52
    assert len(records) == 150
''' + source[end:]
    source = source.replace('Rebuild and replay digest-checked byte capture/catalog composition; never accept or discharge it.',
                            'Rebuild and replay captured profile selection; never infer authentic ownership or discharge inherited obligations.')
    (HERE / 'verify_candidate.py').write_text(source)
    (HERE / 'audit_imports.py').write_text((BASE / 'audit_imports.py').read_text().replace('K02-digest-capture', 'K02-profile-selection').replace('K02 digest-capture composition', 'captured profile selection'))
    controls = json.loads((HERE / 'control-index.json').read_text())
    selected = [HERE / 'FORMALIZATION.md', BASE / 'verification.json',
                BASE / 'DigestCapture.lean', BASE / 'DigestCaptureCatalog.lean',
                HERE.parent / 'K02-binding-capture/CapturePolicies.lean']
    (HERE / 'context-pack.json').write_text(json.dumps({
        'task': 'N01', 'unit': 'K02-profile-selection', 'selected_sources': [binding(path) for path in selected],
        'full_plan_scope_retained': True, 'K04_pending': True, 'authority_effect': 'none'
    }, indent=2) + '\n')
    (HERE / 'source-capture.json').write_text(json.dumps({
        'task': 'N01', 'unit': 'K02-profile-selection', 'independent_formalization': binding(HERE / 'FORMALIZATION.md'),
        'predecessor_verification': binding(BASE / 'verification.json'),
        'control_index': binding(HERE / 'control-index.json'), 'control_generator': binding(HERE / 'generate_controls.py'),
        'fixtures': controls['fixtures'], 'frame_source': controls['frame_source'],
        'profile_principal_bootstrap_review_roots_synthetic': True,
        'authentic_evidence_provider_realized': False, 'inherited_discharges': 0, 'authority_effect': 'none'
    }, indent=2) + '\n')
    print({'dependencies': len(dependencies), 'new_modules': len(MODULES), 'new_declarations': 52})


if __name__ == '__main__':
    run()
