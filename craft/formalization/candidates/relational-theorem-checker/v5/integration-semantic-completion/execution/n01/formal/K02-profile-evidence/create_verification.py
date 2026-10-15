"""Build a fresh isolated protocol for the complete authority evidence interpreter."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
BASE = HERE.parent / 'K02-profile-selection'
MODULES = ['AuthoritySources', 'AuthorityChecks', 'AuthorityPreparation', 'AuthorityOwnership', 'AuthorityControls', 'AuthorityRuntimeControls']


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    for stem in MODULES:
        path = HERE / (stem + '.lean'); source = path.read_text()
        names = re.findall(r'^theorem (\w+)', source, re.M)
        if names and '#print axioms' not in source:
            marker = 'end RelationalSuccessor.CandidateProfileEvidence'
            if stem == 'AuthorityControls': marker += '.Controls'
            assert source.count(marker) == 1
            path.write_text(source.replace(marker, '\n'.join('#print axioms ' + name for name in names) + '\n' + marker))
    previous = json.loads((BASE / 'verification.json').read_text())
    dependencies = [ROOT / item['path'] for item in previous['sources'] if Path(item['path']).stem != 'ProfileSelectionRuntimeControls']
    assert len(dependencies) == 74
    source = (BASE / 'verify_candidate.py').read_text()
    start = source.index('    dependencies ='); end = source.index('    sources = dependencies + new_sources')
    source = source[:start] + '    dependencies = [(HERE.parent/name).resolve() for name in ' + repr([os.path.relpath(p, HERE.parent) for p in dependencies]) + ']\n    new_sources = [HERE/name for name in ' + repr([stem + '.lean' for stem in MODULES]) + ']\n' + source[end:]
    source = source.replace('ProfileSelectionRuntimeControls', 'AuthorityRuntimeControls')
    source = source.replace("    assert controls['authentic_evidence_provider_realized'] is False", "    assert controls['real_authoritative_snapshot_provider'] is False")
    start = source.index('    report = {'); end = source.index('    (HERE / "verification.json").write_text', start)
    source = source[:start] + '''    report = {
        "task": "N01", "unit": "K02-profile-evidence", "result": "candidate-fragment-pass",
        "method": "Fresh isolated pinned Lean compilation and separate fresh same-kernel replay; exact original-byte fixture and runtime comparisons",
        "toolchain_lock": binding(lock_path), "compiler": binding(lean), "kernel_library": binding(kernel),
        "driver": binding(Path(__file__)), "context_pack": binding(HERE/'context-pack.json'), "source_capture": binding(capture_path),
        "sources": captured, "records": records, "new_declarations": declarations, "new_declaration_count": len(declarations),
        "new_general_declarations": 26, "new_worked_control_declarations": 35,
        "allowed_axioms": sorted(allowed), "control_index": binding(HERE/'control-index.json'), "runtime_composed_cases": len(controls['runtime_cases']),
        "authority_source_decoders_exact": True, "authority_capture_preparation_exact": True,
        "complete_profile_evidence_preparation_exact": True, "original_source_bytes_and_envelopes_retained": True,
        "all_source_evidence_joins_exact": True, "unused_fact_equivocation_refusal_proved": True,
        "batched_review_and_multi_action_grants_supported": True, "eight_evidence_requirements_interpreted": True,
        "authoritative_snapshot_boundary_explicit": True, "absent_boundary_refuses_ownership_proved": True,
        "conditional_owned_selection_and_capture_bridges_proved": True,
        "claim_scope": "Exact captured authority snapshot decoding and full profile evidence preparation. Every retained declaration/selection has exact issuance/byte/issuer, principal/action/scope, owner-review/source/posture/expiry joins. Batched reviews and multi-action grants supported; unused equivocation refuses. Eight concrete evidence interpretations retain one independently required authoritative-snapshot boundary.",
        "kernel_controls_are_typed_data_only": True, "profile_principal_bootstrap_review_roots_synthetic": True,
        "real_authoritative_snapshot_provider": False, "authentic_evidence_provider_realized": False,
        "authenticated_digest_profile_selection_proved": False, "authenticated_capture_proved": False,
        "authenticated_full_source_policy_realization_proved": False, "JSON_schema_semantics_interpreter_proved": False,
        "whole_K02_source_refinement_proved": False, "raw_source_refinement_proved": False,
        "independent_checker_run": False, "external_standard_translation_reviewed": False,
        "collision_freedom_proved": False, "supported_resource_envelope_measured": False,
        "public_outcome_classification_implemented": False, "N03_API_freeze": False,
        "inherited_discharges": 0, "N01_accepted": False, "authority_effect": "none"
    }
    assert len(declarations) == 61 and len(records) == 160
''' + source[end:]
    source = source.replace('Rebuild and replay captured profile selection; never infer authentic ownership or discharge inherited obligations.',
                            'Rebuild and replay the captured authority evidence interpreter; never infer an authoritative snapshot from structural success.')
    (HERE / 'verify_candidate.py').write_text(source)
    (HERE / 'audit_imports.py').write_text((BASE / 'audit_imports.py').read_text().replace('K02-profile-selection', 'K02-profile-evidence').replace('captured profile selection', 'captured authority evidence interpretation'))
    controls = json.loads((HERE / 'control-index.json').read_text())
    (HERE / 'context-pack.json').write_text(json.dumps({'task': 'N01', 'unit': 'K02-profile-evidence',
        'selected_sources': [binding(path) for path in [HERE / 'FORMALIZATION.md', BASE / 'verification.json', BASE / 'ProfileSelectionEvidence.lean',
            HERE.parent / 'K02-source-contract/policy-obligations.json', HERE.parent / 'K02-binding-capture/CapturePolicies.lean']],
        'full_plan_scope_retained': True, 'K04_pending': True, 'authority_effect': 'none'}, indent=2) + '\n')
    (HERE / 'source-capture.json').write_text(json.dumps({'task': 'N01', 'unit': 'K02-profile-evidence',
        'independent_formalization': binding(HERE / 'FORMALIZATION.md'), 'predecessor_verification': binding(BASE / 'verification.json'),
        'control_index': binding(HERE / 'control-index.json'), 'control_generator': binding(HERE / 'generate_controls.py'),
        'fixtures': controls['fixtures'], 'bootstrap_source': controls['bootstrap_source'],
        'profile_principal_bootstrap_review_roots_synthetic': True, 'real_authoritative_snapshot_provider': False,
        'inherited_discharges': 0, 'authority_effect': 'none'}, indent=2) + '\n')
    print({'dependencies': len(dependencies), 'new_modules': len(MODULES), 'new_declarations': 61})


if __name__ == '__main__': run()
