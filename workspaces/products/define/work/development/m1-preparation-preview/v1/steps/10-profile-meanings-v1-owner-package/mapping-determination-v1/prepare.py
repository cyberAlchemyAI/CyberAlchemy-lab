#!/usr/bin/env python3
"""Build exact mapping-review evidence. No role selection or application."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import jsonschema

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
LAB = next(p for p in HERE.parents if (p / 'authority/foundation/v1/schema.json').is_file())
INPUTS = {}
CHECKS = []

def load(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def ref(p, selector=None):
    result = {'path': str(p.relative_to(LAB)), 'sha256': sha(p), 'bytes': p.stat().st_size}
    INPUTS[result['path']] = result.copy()
    if selector is not None:
        result['selector'] = selector
    return result

def write(name, data):
    p = HERE / name
    if p.exists():
        raise RuntimeError('Do not overwrite reviewed material: ' + str(p))
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    return p

def textfile(name, text):
    p = HERE / name
    if p.exists():
        raise RuntimeError('Do not overwrite reviewed material: ' + str(p))
    p.write_text(text)
    return p

def check(name, ok, detail):
    CHECKS.append({'check_id': name, 'outcome': 'PASS' if ok else 'FAIL', 'detail': detail})
    if not ok:
        raise RuntimeError(name + ': ' + str(detail))

def main():
    for p in (PACKAGE / 'package-manifest.json', PACKAGE / 'owner-package-manifest.json', PACKAGE / 'supplement-01-authored-postimage/package-manifest.json'):
        seal = load(p)
        for item in seal.get('files', []) + seal.get('external_inputs', []) + seal.get('component_seals', []):
            check('sealed-input:' + item['path'], sha(LAB / item['path']) == item['sha256'], item['sha256'])
        ref(p)
    mapping_path = PACKAGE / 'supplement-01-authored-postimage/registry-representation-mapping.json'
    authored_path = PACKAGE / 'supplement-01-authored-postimage/authored-postimage/registry.json'
    index_path = authored_path.with_name('DEFINITIONS-INDEX.md')
    mapping, authored = load(mapping_path), load(authored_path)
    baseline_path = LAB / mapping['baseline']['path']
    baseline = load(baseline_path)
    delta_path = PACKAGE / 'registry-delta.json'
    pending_path = PACKAGE / 'registry-postimage.json'
    pending, delta = load(pending_path), load(delta_path)
    for p in (mapping_path, authored_path, index_path, baseline_path, delta_path, pending_path, PACKAGE / 'registry-compatibility-owner-request.json'):
        ref(p)
    fields = ('definition_id', 'version', 'path', 'sha256', 'term')
    key = lambda r: (r['definition_id'], r['version'])
    before = {key(r): r for r in baseline['entries']}
    planned = {key(r): r for r in authored['entries']}
    check('191-exact-unique-authoring-pairs', len(planned) == len(authored['entries']) == 191, len(planned))
    check('189-unique-baseline-pairs', len(before) == len(baseline['entries']) == 189, len(before))
    for row in mapping['inherited_admission_rows']:
        original, projected = row['exact_original_row'], row['authored_fields']
        k = key(original)
        check('preserve-full-row:' + row['definition_ref'], before[k] == original and original in pending['entries'], original['admission_decision_ref'])
        check('project-common-fields:' + row['definition_ref'], all(projected[f] == original[f] == planned[k][f] for f in fields), list(fields))
        reconstructed = copy.deepcopy(original)
        reconstructed.update({f: projected[f] for f in fields})
        check('metadata-assisted-roundtrip:' + row['definition_ref'], reconstructed == original, 'Inverse uses exact historical metadata, never the authored view alone.')
        source = LAB / original['path']
        ref(source)
        check('inherited-source-unchanged:' + row['definition_ref'], sha(source) == original['sha256'] and load(source)['schema_version'] == 'cyberalchemy-lab-definition/v1', original['sha256'])
    new_keys = set(planned) - set(before)
    check('only-two-requested-additions', new_keys == {key(r) for r in delta['added_candidates']}, sorted(new_keys))
    for row in mapping['new_entries']:
        candidate = row['exact_candidate']
        check('pending-standing-kept:' + candidate['definition_id'], candidate['lifecycle_state'] == row['captured_standing'] == 'candidate-unadmitted' and row['actual_decision_ref'] is None and row['actual_application_ref'] is None and row['planned_status_is_conditional'], row['captured_standing'])
        check('conditional-prospective-fields:' + candidate['definition_id'], all(planned[key(candidate)][f] == candidate[f] for f in fields) and planned[key(candidate)]['authority_state'] == 'admitted' and authored['status'] == 'candidate-unadmitted' and authored['authority_effect'] == 'none', 'Requested future postimage label supplies no current standing or admitted-source premise.')
    check('actual-lookup-unchanged', pending['current_lookup'] == baseline['current_lookup'] and len(baseline['current_lookup']) == 183, len(baseline['current_lookup']))
    future_lookup = baseline['current_lookup'] | delta['proposed_lookup_additions']
    check('only-two-future-current-additions', len(future_lookup) == 185 and all(future_lookup[k] == v for k, v in baseline['current_lookup'].items()), sorted(delta['proposed_lookup_additions']))
    schema_path = LAB / 'authority/foundation/v1/schema.json'
    schema = load(schema_path)
    ref(schema_path)
    check('closed-v1-authoring-schema', not list(jsonschema.Draft202012Validator(schema | {'$ref': '#/$defs/definitionRegistry'}).iter_errors(authored)), ref(authored_path))
    renderer_path = LAB / 'authority/foundation/v1/render.py'
    ref(renderer_path)
    spec = importlib.util.spec_from_file_location('mapping_review_foundation_renderer', renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    check('authoring-index-parity', index_path.read_text() == renderer.registry(authored) == renderer.registry(authored), sha(index_path))

    owners_path = LAB / 'authority/owners/foundation-01/v1/owners.json'
    decision_path = LAB / 'docs/decisions/0013-foundation-01-admission/decision.json'
    owners, owner_admission = load(owners_path), load(decision_path)
    ref(owners_path)
    ref(decision_path)
    check('admitted-owner-scope-source', owner_admission['status'] == 'owner-admitted' and next(r for r in owner_admission['admitted_records'] if r['record_id'] == owners['record_id'])['sha256'] == sha(owners_path), owners['record_id'])
    scopes = [('artifact-mechanics-owner', 'Exact unchanged v1 field/projection mapping and renderer bindings. No canonical schema/source-policy change or runtime approval.', ['Source direction', 'schema', 'generator']), ('definition-owner', 'Exact identities, two conditional new entries, preserved original registry rows/current choices and their complete historical metadata. No semantic admission.', ['Definition meaning', 'registry postimages']), ('evidence-conformance-owner', 'Adequacy and declared limits of these exact check-06 mapping/schema/index/drift observations. No semantic truth or admission selection.', ['evaluation contracts', 'receipts'])]
    drafts = []
    for role, scope, words in scopes:
        assignment = next(r for r in owners['role_assignments'] if r['role_id'] == role)
        check('assignment-scope:' + role, all(w in assignment['scope'] for w in words), assignment)
        draft = {'schema_version': 'cal.define-v1-mapping-role-determination-draft/v1', 'authority_effect': 'none', 'role_ref': 'role:' + role, 'assignment': assignment, 'owner_admission': ref(decision_path), 'status': 'draft recommended determination; not selected', 'selected': False, 'actual_decision_ref': None, 'scope': scope, 'recommendation': 'Confirm this exact mapping within the stated preservation/prospective-standing limits.', 'inputs': [ref(mapping_path), ref(authored_path), ref(index_path), ref(baseline_path)], 'excluded_effects': ['admit either profile meaning', 'adopt a profile or artifact type', 'rewrite the admitted schema or registry', 'change current lookup', 'grant execution permission'], 'identity_ceiling': 'Recorded repository owner-declared principal and admitted role scope; no external authentication or signed Decision invented.'}
        write(role + '.draft.json', draft)
        drafts.append(draft)

    drift = {'schema_version': 'cyberalchemy-lab-definition-drift-audit/v1', 'record_id': 'CAL-DEFINE-V1-PROFILE-MEANINGS-MAPPING-DRIFT-DRAFT', 'artifact_type_ref': 'cal.artifact-type.drift-audit/v1', 'status': 'candidate-unadmitted', 'authority_effect': 'none', 'owner_ref': 'role:evidence-conformance-owner', 'registry_ref': str(authored_path.relative_to(LAB)), 'registry_sha256': sha(authored_path), 'source_direction': {'canonical': 'drift-audit.json', 'human_projection': 'DRIFT-AUDIT.md', 'projection_policy': 'generated-only', 'generator_ref': 'cal.generator.foundation-projections/v1', 'generator_sha256': sha(renderer_path)}, 'findings': [{'finding_id': 'V1-MAPPING-ROLE-CONCURRENCE', 'severity': 'blocker', 'target': str(mapping_path.relative_to(LAB)), 'condition': 'Mechanical mapping/schema/projection/preservation evidence is prepared; the three exact scoped owner determinations remain unselected.', 'remediation': 'Obtain attributable exact mechanics, Definition-registry and evidence review concurrence; then produce a fresh check-06 assessment without rewriting this snapshot.', 'blocking_for': 'v1 registry check 06 and semantic admission eligibility'}, {'finding_id': 'V1-PROSPECTIVE-STANDING-SEPARATION', 'severity': 'info', 'target': str(authored_path.relative_to(LAB)), 'condition': 'Two future authored authority_state labels are conditional postimage values; current captured standing remains candidate-unadmitted and the live registry is unchanged.', 'remediation': 'Preserve the candidate delta and exact historical metadata alongside the authored view; never use its future labels as actual source standing.', 'blocking_for': 'any unsupported actual-admission or execution claim'}], 'summary': {'undefined_critical_terms': 0, 'conflicting_consumers': 0, 'stale_entries': 0, 'wrong_workspace_voices': 0}, 'claim_ceiling': 'Scoped candidate-material observations for the two already reviewed meaning records and exact mapping, not a current-authority/global zero-drift audit. Zero summary counters mean no measured defects in these selected drafts; the explicit owner-concurrence blocker remains. Historical live audit is preserved unchanged, no semantic admission or runtime correctness is established.'}
    drift_path = write('drift-audit.json', drift)
    check('closed-v1-drift-schema', not list(jsonschema.Draft202012Validator(schema | {'$ref': '#/$defs/driftAudit'}).iter_errors(drift)), sha(drift_path))
    projected = renderer.drift(drift)
    textfile('DRIFT-AUDIT.md', projected)
    check('closed-v1-drift-projection', projected == renderer.drift(drift), sha(drift_path))
    write('mapping-correspondence.json', {'authority_effect': 'none', 'common_fields': list(fields), 'forward': 'Authored identity/version/path/hash/term fields equal their exact source fields. authority_state is an intended postimage value for the two pending rows, not observed standing.', 'inverse': 'Reconstruct inherited complete rows only from the authored common fields plus exact preserved original admission/lifecycle metadata.', 'actual_standing': 'Obtain from exact baseline/delta/qualified Decision and application evidence, never from a prospective authoring label alone.', 'current_selection': 'Preserve all 183 live choices; only a separately authorized application can add the two intended choices.', 'witness_scope': '189 exact inherited rows and two specific pending meanings, no arbitrary serializer or whole-repository theorem.', 'mapping_source': ref(mapping_path)})
    technical = write('technical-evidence.json', {'schema_version': 'cal.define-v1-mapping-technical-evidence/v1', 'authority_effect': 'none', 'result': 'PASS all executed scoped material checks', 'checks': CHECKS, 'inherited_rows': 189, 'pending_rows': 2, 'prospective_unique_entries': 191, 'actual_current_lookup': 183, 'future_current_lookup': 185, 'role_determinations_selected': 0, 'runtime_tests_executed': False, 'full_check_06': 'NOT_EVALUABLE until required qualified scoped concurrence', 'limits': ['Exact finite captured rows and pinned renderers only.', 'Field projection is lossless only with preserved metadata.', 'Component validation is not owner concurrence, contract adoption, runtime conformance or a complete semantic proof.']})
    old_evaluation = load(PACKAGE / 'evaluation-preview.json')
    ref(PACKAGE / 'evaluation-preview.json')
    actual, conditional = [], []
    for original in old_evaluation['evaluations']:
        current = copy.deepcopy(original)
        current['checks'][5] = {'check_id': 'DEF-EVAL-06-REGISTRY', 'outcome': 'NOT_EVALUABLE', 'reason': 'Exact mapping, original v1 authoring schema/index and new v1 drift checks pass; qualified three-scope concurrence remains unselected.', 'evidence_ref': str(technical.relative_to(LAB))}
        current['checks'][6] = {'check_id': 'DEF-EVAL-07-DECISION', 'outcome': 'NOT_EVALUABLE', 'reason': 'No actual semantic admission Decision; required registry review concurrence is still an additional blocker.'}
        actual.append(current)
        hypothetical = copy.deepcopy(current)
        hypothetical['condition'] = 'Only after attributable exact concurrence covers all three declared roles and inputs remain current; this condition is not presently established.'
        hypothetical['checks'][5]['outcome'] = 'PASS'
        hypothetical['checks'][5]['reason'] = 'Conditional illustration of qualified check-06 closure, not an actual receipt.'
        hypothetical['checks'][6]['reason'] = 'Conditional case: solely pending semantic owner selection; no semantic Decision or application exists.'
        hypothetical['predecision_aggregate'] = 'PASS'
        hypothetical['eligible_for_admission'] = True
        hypothetical['actual'] = False
        conditional.append(hypothetical)
    write('evaluation-refresh.json', {'authority_effect': 'none', 'actual_evaluations': actual, 'conditional_after_exact_review': conditional, 'conditions_established': False, 'admission_ready': False, 'actual_decisions': None})
    request = write('review-request.json', {'schema_version': 'cal.define-v1-mapping-concurrence-review-request/v1', 'authority_effect': 'none', 'selected': False, 'actual_decision_ref': None, 'request': 'Confirm the exact existing v1 authoring/admitted-output mapping within each of the three separate assigned scopes; this review selects no semantic admission or applied effect.', 'scopes': [{'role_ref': d['role_ref'], 'scope': d['scope'], 'draft': ref(HERE / (d['assignment']['role_id'] + '.draft.json'))} for d in drafts], 'materials': [ref(mapping_path), ref(authored_path), ref(index_path), ref(drift_path), ref(HERE / 'DRIFT-AUDIT.md'), ref(technical), ref(HERE / 'mapping-correspondence.json')], 'required_limits': ['Preserve complete 189-row admission metadata and 183 live choices.', 'Two new labels describe a conditional future postimage; actual candidates remain unadmitted.', 'No schema amendment, global source-policy adoption or application is selected.', 'No runtime, external consumer compatibility or global semantic theorem is established.'], 'after_confirmed_review': 'Bind the attributable review to exact role scopes and this seal; recheck current inputs and refresh actual check 06. Semantic admission requires its separate exact owner selection.'})
    textfile('REVIEW.md', '# Exact v1 registry mapping determination\n\nTechnical mapping evidence is prepared and passed for 189 inherited rows plus two pending meanings. Field projection preserves identity/version/path/hash/term; the inverse requires the exact historical metadata, so the authored view cannot supply current admission standing on its own. The original closed v1 schema and renderer are unchanged.\n\n- [Role-separated exact review request](review-request.json)\n- [Mechanics determination draft](artifact-mechanics-owner.draft.json)\n- [Definition registry determination draft](definition-owner.draft.json)\n- [Evidence determination draft](evidence-conformance-owner.draft.json)\n- [Executed technical evidence](technical-evidence.json)\n- [Explicit mapping correspondence](mapping-correspondence.json)\n- [Original-schema v1 drift audit](drift-audit.json) and [generated view](DRIFT-AUDIT.md)\n- [Actual and separately conditional eligibility refresh](evaluation-refresh.json)\n\n## Example\n\nThe Evaluation Profile meaning has captured standing candidate-unadmitted. Its prospective authored postimage row says authority_state=admitted only as the requested future output IF qualified admission and application later occur. The live registry contains neither new meaning. Existing historical Decision references remain in complete inherited rows even though the authored view omits those fields.\n\n## Current status\n\nDO NEXT authorizes preparation of this next review, not automatic owner concurrence. All three determinations remain unselected. Actual check 06 and the admission aggregate remain NOT_EVALUABLE. The conditional PASS preview is explicitly not an actual evaluation or admission-ready claim. Confirming only these scoped mapping reviews can support a fresh check-06 assessment; it would not admit either meaning, adopt a profile or change current state.\n')
    write('package-manifest.json', {'schema_version': 'cal.define-v1-mapping-determination-manifest/v1', 'authority_effect': 'none', 'status': 'frozen role-separated review material; concurrence and semantic admission unselected', 'files': [{'path': str(p.relative_to(LAB)), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(HERE.iterdir()) if p.is_file()], 'external_inputs': list(INPUTS.values()), 'exclusions': ['self manifest', 'later verification', 'mutable progress/readme', 'private state'], 'actual_owner_concurrence': None, 'admission_ready': False})
    print(json.dumps({'checks': len(CHECKS), 'scoped_technical_result': 'PASS', 'draft_role_determinations': len(drafts), 'v1_drift_schema': 'PASS', 'actual_check_06': 'NOT_EVALUABLE', 'manifest_sha256': sha(HERE / 'package-manifest.json')}, indent=2))

if __name__ == '__main__':
    main()
