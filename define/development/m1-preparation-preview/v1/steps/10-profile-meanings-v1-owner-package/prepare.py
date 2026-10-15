#!/usr/bin/env python3
"""Prepare local, non-authorizing v1 owner material; never apply an effect."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import jsonschema

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[5]
BASE = HERE.parent.parent
FROZEN = BASE / 'steps/09-assurance-evidence-closure'
REVIEWS = BASE / 'reviews/e04-final-review/v1'
EXTERNAL = {}
CHECKS = []

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reference(path, selector=None):
    result = {'path': str(path.relative_to(LAB)), 'sha256': sha(path), 'bytes': path.stat().st_size}
    if selector is not None:
        result['selector'] = selector
    EXTERNAL[result['path']] = {k: v for k, v in result.items() if k != 'selector'}
    return result

def put(name, data):
    path = HERE / name
    if path.exists():
        raise RuntimeError('Existing output must not be overwritten: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    return path

def prose(name, text):
    path = HERE / name
    if path.exists():
        raise RuntimeError('Existing output must not be overwritten: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path

def check(name, passed, detail):
    CHECKS.append({'check_id': name, 'outcome': 'PASS' if passed else 'FAIL', 'detail': detail})
    if not passed:
        raise RuntimeError(name + ': ' + str(detail))

def module(path, name):
    reference(path)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def pure_renderers(path):
    reference(path)
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('render_index', 'render_drift')]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace

def pointer(value, selector):
    for token in selector.lstrip('/').split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

def main():
    manifest_path = FROZEN / 'package-manifest.json'
    frozen = read(manifest_path)
    check('frozen-review-seal', sha(manifest_path) == 'a7fdbdd26120d536289161bb6d21eb8f0ad7c273f1b17fa91c9afc15077a94ee', reference(manifest_path))
    for item in frozen['files'] + frozen['external_inputs']:
        path = LAB / item['path']
        check('frozen-input:' + item['path'], path.exists() and sha(path) == item['sha256'], item['sha256'])
    baseline_path = LAB / 'authority/definitions/registry.json'
    baseline = read(baseline_path)
    reference(baseline_path)
    old_entries = {(x['definition_id'], x['version']): x for x in baseline['entries']}
    targets = [x for x in read(FROZEN / 'targets.json')['targets'] if x['model_role'] in ('EvaluationProfile', 'LifecycleProfile')]
    check('only-two-v1-targets', len(targets) == 2 and all(x['carrier_ref'] == 'cal.artifact-type.definition/v1' for x in targets), [x['definition_ref'] for x in targets])
    reference(FROZEN / 'targets.json')
    schema_path = LAB / 'authority/artifact-types/definition/v1/schema.json'
    schema = read(schema_path)
    reference(schema_path)
    generator_path = LAB / 'authority/artifact-types/definition/v1/generator.py'
    generator = module(generator_path, 'profile_meaning_definition_v1')
    records = {}
    for target in targets:
        path = LAB / target['path']
        record = read(path)
        records[target['definition_ref']] = record
        reference(path)
        errors = [e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(record)]
        check('schema:' + target['definition_ref'], not errors and sha(path) == target['sha256'], errors)
        projected = generator.render(record)
        original = LAB / target['human_projection']['path']
        reference(original)
        check('projection:' + target['definition_ref'], projected == generator.render(record) == original.read_text(), reference(generator_path))
        prose('subjects/' + record['definition_id'].split('.')[-1] + '/DEFINITION.md', projected)
    put('subjects.json', {'authority_effect': 'none', 'subjects': targets, 'source_bytes_changed': False, 'excluded': ['foundational successor', 'Pack', 'Define', 'incident completeness specimen', 'profile/v2 types and concrete profile adoption']})

    owner_path = LAB / 'authority/owners/foundation-01/v1/owners.json'
    decision_path = LAB / 'docs/decisions/0013-foundation-01-admission/decision.json'
    owners, owner_admission = read(owner_path), read(decision_path)
    admitted = {x['record_id']: x for x in owner_admission['admitted_records']}
    check('admitted-owner-map', owner_admission['status'] == 'owner-admitted' and admitted[owners['record_id']]['sha256'] == sha(owner_path), reference(decision_path))
    semantic = next(x for x in owners['role_assignments'] if x['role_id'] == 'definition-owner')
    evidence = next(x for x in owners['role_assignments'] if x['role_id'] == 'evidence-conformance-owner')
    mechanics = next(x for x in owners['role_assignments'] if x['role_id'] == 'artifact-mechanics-owner')
    check('scope:candidate-semantic-owner', all(r['semantic_owner_ref'] == 'role:definition-owner' and r['drift_route']['owner_ref'] == 'role:definition-owner' for r in records.values()), semantic)
    check('scope:meaning-registry-lifecycle', all(w in semantic['scope'] for w in ('Definition meaning', 'registry postimages', 'lifecycle decisions')), semantic['scope'])
    owner_evidence = {'authority_effect': 'none', 'owner_map': reference(owner_path), 'owner_admission': reference(decision_path), 'semantic_assignment': semantic, 'evaluation_assignment': evidence, 'mechanics_assignment_for_remaining_registry_determination': mechanics, 'scope_result': 'PASS recorded admitted Definition/v1 semantic/registry/drift scope; no v2 type-registration scope needed for these two meanings', 'recorded_principal': semantic['principal_id'], 'identity_ceiling': 'Admitted repository owner-declared identity and role scope verified; no external person authentication, credential or signing authority is fabricated.', 'separation': owners['separation_rule'], 'actual_effect_selected': False}
    put('owner-scope-evidence.json', owner_evidence)

    route = {}
    for kind, filename, record_id in [('evaluation', 'evaluation.json', 'CAL-EVALUATION-DEFINITION-V1'), ('lifecycle', 'lifecycle.json', 'CAL-LIFECYCLE-DEFINITION-V1')]:
        path = LAB / 'authority/profiles/definition/v1' / filename
        data = read(path)
        check('adopted-v1-profile:' + kind, admitted[record_id]['sha256'] == sha(path) and data['subject_artifact_type_ref'] == 'cal.artifact-type.definition/v1', admitted[record_id])
        route[kind] = reference(path)
    catalog_path = LAB / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    catalog = read(catalog_path)
    carrier = next(x for x in catalog['admitted_contracts'] if x['artifact_type_ref'] == 'cal.artifact-type.definition/v1')
    carrier_decision = LAB / 'docs/decisions/0015-definition-v1-admission/decision.json'
    if not carrier_decision.exists():
        carrier_decision = next(p for p in (LAB / 'docs/decisions').glob('0015*/decision.json'))
    check('exact-admitted-v1-carrier', read(carrier_decision)['status'] == 'owner-admitted' and sha(LAB / carrier['artifact_path']) == carrier['artifact_sha256'] and sha(schema_path) == carrier['schema_sha256'], carrier)
    reference(carrier_decision)
    route.update({'authority_effect': 'none', 'carrier_contract': carrier, 'catalog': reference(catalog_path), 'carrier_posture': 'admitted-historical, not withdrawn; selected exact v1 bootstrap use is explicit, not a claim that v1 is the global latest carrier', 'schema': reference(schema_path), 'generator': reference(generator_path), 'actual_v2_profile_adoption': False})
    put('v1-route-bindings.json', route)

    closure_path = BASE / 'steps/07-profile-formal-source-evidence/source-closure.json'
    closure = read(closure_path)
    reference(closure_path)
    source_rows = []
    for row in closure['bindings']:
        if row['candidate_ref'] not in records:
            continue
        path, dec = LAB / row['path'], LAB / row['decision_path']
        reference(path)
        reference(dec)
        value = pointer(read(path), row['selector'])
        digests = [hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=flag).encode()).hexdigest() for flag in (False, True)]
        check('source:' + row['candidate_ref'] + ':' + row['source_ref'] + row['selector'], sha(path) == row['content_sha256'] and sha(dec) == row['decision_sha256'] and row['selected_canonical_sha256'] in digests, {'source': row['source_ref'], 'selector': row['selector']})
        if '@' in row['source_ref']:
            identity, version = row['source_ref'].rsplit('@', 1)
            entry = old_entries[(identity, version)]
            check('source-admission:' + row['source_ref'], entry['sha256'] == sha(path) and entry['admission_decision_ref'] == row['decision_ref'], entry['admission_decision_ref'])
        else:
            check('source-admission:' + row['source_ref'], admitted[row['source_ref']]['sha256'] == sha(path) and row['decision_ref'] == owner_admission['decision_id'], row['decision_ref'])
        source_rows.append({**row, 'fresh_result': 'PASS exact record/selector/admission binding; inherited use ceiling retained'})
    check('24-source-bindings', len(source_rows) == 24, len(source_rows))
    put('source-bindings.json', {'authority_effect': 'none', 'bindings': source_rows, 'technical_source_gaps': 0, 'new_source_admissions': 0})

    delta = [{'definition_id': r['definition_id'], 'version': r['version'], 'term': r['term'], 'path': t['path'], 'sha256': t['sha256'], 'lifecycle_state': 'candidate-unadmitted'} for t in targets for r in [records[t['definition_ref']]]]
    proposed_lookup = {**baseline['current_lookup'], **{r['definition_id']: r['definition_id'] + '@' + r['version'] for r in delta}}
    put('registry-delta.json', {'authority_effect': 'none', 'baseline': reference(baseline_path), 'added_candidates': delta, 'before_versions': 189, 'proposed_versions': 191, 'before_current_identities': 183, 'proposed_current_identities': 185, 'proposed_lookup_additions': {r['definition_id']: proposed_lookup[r['definition_id']] for r in delta}, 'current_lookup_unchanged_now': True, 'inherited_rows_preserved': True, 'new_admission_decision_refs': None})
    postimage = copy.deepcopy(baseline)
    postimage.update({'record_id': 'CAL-DEFINITION-REGISTRY-POSTIMAGE-PROFILE-MEANINGS-V1', 'status': 'candidate-postimage', 'authority_effect': 'none', 'admission_decision_ref': None, 'entries': sorted(baseline['entries'] + delta, key=lambda x: (x['definition_id'], x['version'])), 'predecessor': {'path': str(baseline_path.relative_to(LAB)), 'sha256': sha(baseline_path), 'entry_count': 189, 'current_count': 183}, 'claim_ceiling': 'Conservative 189-row preservation plus two pending Definition/v1 meanings. No candidate is admitted and current_lookup stays unchanged. This legacy admitted-output-form proposal is not claimed valid against the original closed authored Foundation/v1 registry schema; exact compatibility determination remains required.'})
    postimage['source_direction'] = {**baseline['source_direction'], 'canonical': 'registry-postimage.json', 'human_projection': 'DEFINITIONS-INDEX.md'}
    registry_path = put('registry-postimage.json', postimage)
    render_source = LAB / 'docs/decisions/0074-governance-transaction-surface-admission/apply.py'
    renderers = pure_renderers(render_source)
    index = renderers['render_index'](postimage)
    check('registry-index-determinism', index == renderers['render_index'](postimage), 'Pure pinned render_index component only; admission builder/application not invoked.')
    prose('DEFINITIONS-INDEX.md', index)
    check('191-unique-preserved-rows', len({(x['definition_id'], x['version']) for x in postimage['entries']}) == 191 and all(x in postimage['entries'] for x in baseline['entries']) and postimage['current_lookup'] == baseline['current_lookup'], '189 exact inherited rows + two pending meanings; unchanged actual lookup')

    foundation_schema_path = LAB / 'authority/foundation/v1/schema.json'
    foundation_schema = read(foundation_schema_path)
    reference(foundation_schema_path)
    scoped_validator = jsonschema.Draft202012Validator({**foundation_schema, '$ref': '#/$defs/definitionRegistry'})
    old_v1, excluded = [], []
    for row in baseline['entries']:
        path = LAB / row['path']
        reference(path)
        if read(path)['schema_version'] == 'cyberalchemy-lab-definition/v1':
            old_v1.append({k: row[k] for k in ('definition_id', 'version', 'path', 'sha256', 'term')} | {'authority_state': 'admitted'})
        else:
            excluded.append(copy.deepcopy(row))
    foundation_renderer_path = LAB / 'authority/foundation/v1/render.py'
    foundation_renderer = module(foundation_renderer_path, 'v1_bootstrap_view_renderer')
    v1_view = {'schema_version': 'cyberalchemy-lab-definition-registry/v1', 'record_id': 'CAL-DEFINITION-REGISTRY-V1-BOOTSTRAP-READ-VIEW', 'artifact_type_ref': 'cal.artifact-type.definition-registry/v1', 'status': 'candidate-unadmitted', 'authority_effect': 'none', 'owner_ref': 'role:definition-owner', 'definition_artifact_type_ref': 'cal.artifact-type.definition/v1', 'entries': old_v1, 'identity_rule': baseline['identity_rule'], 'index_policy': 'generated-only', 'source_direction': {'canonical': 'registry.json', 'human_projection': 'DEFINITIONS-INDEX.md', 'projection_policy': 'generated-only', 'generator_ref': 'cal.generator.foundation-projections/v1', 'generator_sha256': sha(foundation_renderer_path)}, 'claim_ceiling': 'Schema-conforming scoped read view of already admitted Definition/v1 rows only. Two pending candidates and inherited non-v1 rows are deliberately outside this view and remain preserved in separate exact material. This view cannot replace the complete canonical registry or establish pending admission.'}
    errors = [e.message for e in scoped_validator.iter_errors(v1_view)]
    check('authored-v1-view-schema', not errors, errors)
    put('v1-view/registry.json', v1_view)
    view_text = foundation_renderer.registry(v1_view)
    check('authored-v1-view-determinism', view_text == foundation_renderer.registry(v1_view), len(old_v1))
    prose('v1-view/DEFINITIONS-INDEX.md', view_text)
    original_errors = list(scoped_validator.iter_errors(postimage))
    baseline_errors = list(scoped_validator.iter_errors(baseline))
    pending_probes = [{k: r[k] for k in ('definition_id', 'version', 'path', 'sha256', 'term')} | {'authority_state': 'candidate-unadmitted'} for r in delta]
    probe_validator = jsonschema.Draft202012Validator({**foundation_schema, '$ref': '#/$defs/definitionEntry'})
    pending_errors = [[e.message for e in probe_validator.iter_errors(p)] for p in pending_probes]
    check('honest-schema-difference-retained', bool(original_errors) and bool(baseline_errors) and all(pending_errors), 'Applied admitted-output metadata and pending candidates cannot be passed off as authored closed v1 schema instances.')
    compatibility = {'authority_effect': 'none', 'schema': reference(foundation_schema_path), 'baseline': reference(baseline_path), 'postimage_ref': 'registry-postimage.json', 'strict_v1_view_ref': 'v1-view/registry.json', 'scope': 'Two new Definition/v1 semantic meanings; no new Definition/v2 rows or registry-v2 policy adoption', 'strict_view_result': 'PASS', 'strict_view_admitted_rows': len(old_v1), 'inherited_non_v1_rows_preserved_outside_view': excluded, 'pending_candidates_preserved_outside_view': delta, 'baseline_vs_authored_schema_error_count': len(baseline_errors), 'postimage_vs_authored_schema_error_count': len(original_errors), 'sample_schema_differences': [{'path': '/' + '/'.join(str(x) for x in e.path), 'reason': e.message[:350]} for e in original_errors[:6]], 'pending_entry_errors': pending_errors, 'full_postimage_closed_v1_schema_result': 'NOT_CONFORMING; not relabeled PASS', 'required_determination': 'Confirm the exact conservative admitted-output-form/authoring-view/delta mapping under applicable mechanics, Definition registry and evidence scopes before asserting v1 check 06. Preservation and projection evidence do not adopt a representation policy.', 'owner_routes': ['role:artifact-mechanics-owner', 'role:definition-owner', 'role:evidence-conformance-owner'], 'status': 'material prepared; exact registry compatibility determination outstanding'}
    put('registry-compatibility.json', compatibility)

    accepted_records = [reference(REVIEWS / f'E04-FIDELITY-{i:02d}-accepted-2026-10-14.json') for i in (4, 5)]
    accepted_records += [reference(REVIEWS / f'E04-COHORT-{i:02d}-accepted-2026-10-14.json') for i in range(1, 5)]
    for name in ('formal-expression-correspondence.json', 'voice-fidelity-review.json', 'assurance-results.json', 'source-closure.json', 'residue-disposition.json'):
        reference(FROZEN / name)
    put('review-bindings.json', {'authority_effect': 'none', 'accepted_exact_reviews': accepted_records, 'original_index_refs_retained': {k: r['index_entry'] for k, r in records.items()}, 'original_drift_refs_retained': {k: r['drift_route'] for k, r in records.items()}, 'package_resolution': 'Package-level exact review/index/drift material resolves this owner request without mutating the frozen candidate fields or globally registering their old aliases.'})
    findings = [{'finding_id': 'V1-BOOTSTRAP-REGISTRY-MAPPING', 'status': 'open', 'condition': compatibility['required_determination'], 'remediation': 'Use the exact scoped compatibility determination request; do not rewrite the admitted schema or mark candidates admitted to make validation pass.'}, {'finding_id': 'V1-BOOTSTRAP-NO-EFFECT', 'status': 'preserved', 'condition': 'No profile type registration, concrete v2 profile adoption, foundational successor or runtime action belongs to this two-meaning effect.', 'remediation': 'Retain independent later owner packages.'}]
    audit = {'schema_version': 'cal.define-v1-owner-drift-review/v1', 'authority_effect': 'none', 'owner_ref': 'role:evidence-conformance-owner', 'registry_ref': 'registry-postimage.json', 'registry_sha256': sha(registry_path), 'findings': findings, 'claim_ceiling': 'Scoped two-meaning owner package audit. The schema/material mapping is open; no zero-drift, universal consistency or completed owner effect is asserted.'}
    put('drift-audit.json', audit)
    drift_text = renderers['render_drift'](audit)
    check('drift-projection-determinism', drift_text == renderers['render_drift'](audit), 'Pinned pure component; not an application invocation.')
    prose('DRIFT-AUDIT.md', drift_text)
    put('compatibility-determination-request.json', {'authority_effect': 'none', 'selected': False, 'actual_decision_ref': None, 'owner_routes': compatibility['owner_routes'], 'material': ['registry-compatibility.json', 'registry-delta.json', 'registry-postimage.json', 'v1-view/registry.json', 'DEFINITIONS-INDEX.md', 'owner-scope-evidence.json'], 'requested_determination': compatibility['required_determination'], 'alternatives': ['Explicit qualified scoped admitted-output compatibility mapping, preserving all baseline rows and authority history', 'Prepare an explicitly owned compatible representation amendment if the existing governing contract cannot support that mapping'], 'excluded': ['Automatically replacing the complete registry with the filtered read view', 'Forging admitted standing for pending candidates', 'Silently loosening the admitted schema', 'Global mixed-v2 or runtime activation effects']})

    evaluations = []
    for target in targets:
        results = [{'check_id': f'DEF-EVAL-{i:02d}-' + name, 'outcome': 'PASS', 'scope': 'exact preparation evidence; no admission effect'} for i, name in [(1, 'SCHEMA'), (2, 'VOICES'), (3, 'SOURCES'), (4, 'OWNER'), (5, 'PROJECTION')]]
        results += [{'check_id': 'DEF-EVAL-06-REGISTRY', 'outcome': 'NOT_EVALUABLE', 'reason': compatibility['required_determination']}, {'check_id': 'DEF-EVAL-07-DECISION', 'outcome': 'NOT_EVALUABLE', 'reason': 'No actual exact admission Decision; registry compatibility is also outstanding, so this is not solely a pending-selection exception.'}]
        evaluations.append({'subject': target['definition_ref'], 'profile': route['evaluation'], 'checks': results, 'predecision_aggregate': 'NOT_EVALUABLE', 'eligible_for_admission': False, 'authority_effect': 'none'})
    put('evaluation-preview.json', {'authority_effect': 'none', 'evaluations': evaluations, 'admission_ready': False, 'limits': 'Fresh package-specific schema/projection/source/owner checks; existing formal evidence retains its original scope. No runtime suite or theorem rerun.'})
    put('owner-request.json', {'schema_version': 'cal.define-v1-owner-preparation-request/v1', 'authority_effect': 'none', 'status': 'prepared for owner review; admission selection unavailable until required compatibility evidence closes', 'selected': False, 'actual_decision_ref': None, 'principal_ref': semantic['principal_id'], 'role_ref': 'role:definition-owner', 'assignment_ref': semantic['assignment_id'], 'requested_future_effect': 'Admit only the two exact Definition/v1 profile meanings and their separately qualified registry/index/drift consequences.', 'subjects': targets, 'prerequisites': ['Exact registry compatibility determination and current v1 checks 01-06 PASS', 'Check 07 pending solely because owner selection has not occurred', 'Actual qualified owner selection binds the package seal and candidate/evidence/postimage digests', 'Applicable lifecycle/application/Project State effects independently recorded; no implied state transition'], 'registry_before_versions': 189, 'registry_after_if_authorized': 191, 'current_before_identities': 183, 'current_after_if_authorized': 185, 'excluded_effects': ['register or adopt profile/v2 types or concrete profiles', 'admit foundational successor, Pack, Define or incident criterion', 'rebind inherited Definitions', 'change Relation Kinds', 'create private keys or mutate stores', 'run an agent or activate the CLI'], 'package_manifest_ref': 'package-manifest.json', 'application_receipt': None})
    put('application-recipe.json', {'authority_effect': 'none', 'status': 'prospective only; not runnable application', 'actual_decision': None, 'actual_application_receipt': None, 'immutable_baseline': reference(baseline_path), 'candidate_delta_ref': 'registry-delta.json', 'required_compatibility': 'registry-compatibility.json', 'after_authorization': ['Bind the actual qualified admission Decision and exact selected subjects/evidence/compatible postimages', 'Generate applied admitted entries with the actual Decision reference, preserving every inherited row', 'Select only the two new identities; preserve all 183 existing current choices', 'Instantiate applied source-direction/index/drift and immutable Project State material using the qualified route', 'Verify exact output/effect bindings and perform only the independently authorized coherent visibility effect'], 'effective_current_lookup_is_not_precomputed_authority': True, 'rollback': 'Before any effect, revise/defer the candidate package; after any effect use the applicable explicit reversal/withdrawal/successor route preserving history.'})
    put('validation-observations.json', {'authority_effect': 'none', 'checks': CHECKS, 'observed_failures': 0, 'registry_schema_differences_are_reported_separately': True, 'runtime_tests_executed': False})
    prose('REVIEW.md', '# First owner package — two profile meanings under v1\n\nOnly the exact Definition Evaluation Profile and Definition Lifecycle Profile candidate.3 records are selected. Their canonical bytes and v1 representations are unchanged. The admitted semantic-owner scope is verified from the exact owner map and its Foundation-01 admission; identity assurance remains owner-declared.\n\n- [Owner request](owner-request.json)\n- [Exact subjects and projections](subjects.json)\n- [Verified owner scope](owner-scope-evidence.json)\n- [Current v1 route bindings](v1-route-bindings.json)\n- [Two-entry delta](registry-delta.json)\n- [191-row conservative pending postimage](registry-postimage.json) and [generated index](DEFINITIONS-INDEX.md)\n- [Schema-conforming existing admitted v1 read view](v1-view/registry.json)\n- [Exact registry compatibility gap](registry-compatibility.json) and [qualified determination request](compatibility-determination-request.json)\n- [Scoped drift](DRIFT-AUDIT.md)\n- [Honest v1 evaluation previews](evaluation-preview.json)\n- [Prospective application recipe](application-recipe.json)\n\n## What the package would do\n\nAfter valid qualification and authorization, admit only these two semantic meanings: 189 to 191 versions and 183 to 185 current identities. All 189 inherited rows and existing current choices are preserved. The foundational predecessor remains selected. No profile/v2 type registration, concrete profile adoption, incident criterion admission or runtime change is included.\n\n## Remaining gate\n\nThe old authored Foundation/v1 registry schema and the existing admitted-output registry form differ. The old schema also allows only admitted entries. A filtered authored read view is valid but cannot replace the full registry or admit the pending subjects. The conservative complete postimage and two pending rows remain explicitly separate. Exact qualified compatibility determination is required before check 06 can PASS. Checks 01-05 have preparation evidence; 06 and 07 remain NOT_EVALUABLE and these subjects are not admission-ready. No schema is silently amended and no future Decision identity is fabricated.\n')
    local = [p for p in HERE.rglob('*') if p.is_file()]
    put('package-manifest.json', {'schema_version': 'cal.define-v1-owner-preparation-manifest/v1', 'authority_effect': 'none', 'status': 'frozen preparation package; registry compatibility prevents admission readiness', 'subjects': targets, 'files': [{'path': str(p.relative_to(LAB)), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(local)], 'external_inputs': list(EXTERNAL.values()), 'exclusions': ['self manifest', 'later verification output', 'mutable progress/agenda', 'private/live stores and credentials'], 'admission_ready': False, 'actual_decisions': None, 'application_receipts': None})
    print(json.dumps({'package': str(HERE.relative_to(LAB)), 'manifest_sha256': sha(HERE / 'package-manifest.json'), 'subjects': len(targets), 'source_bindings': len(source_rows), 'preserved_versions': len(baseline['entries']), 'v1_read_view_rows': len(old_v1), 'postimage_versions': len(postimage['entries']), 'checks': len(CHECKS), 'admission_ready': False, 'blocker': 'Exact registry compatibility determination'}, indent=2))

if __name__ == '__main__':
    main()
