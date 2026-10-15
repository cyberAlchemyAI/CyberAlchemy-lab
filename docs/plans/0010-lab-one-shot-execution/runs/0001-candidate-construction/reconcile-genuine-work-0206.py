"""Read-only original C12/W06/W09 reconciliation; writes only new 0206 reports.

This verifies original receipt closures and recorded outcomes. It does not rerun
domain work, grant authority, restore a key or infer final-interface delivery.
"""
import argparse
import ast
import base64
import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
WORK = 'implementation/lab-work/candidates/v1'
FLOW = 'implementation/lab-workflows/candidates/v1'
W09 = FLOW + '/episodes/W09'
SEEDS = {
    WORK + '/receipts/C12/0001.json': 'f1e9078b22b5c835d3fffc1e5d09b0570f1297c326ba1f92c594c308b52c8381',
    FLOW + '/learning/receipts/0002.json': 'b1bce82b765b9f22a525dee0fa74d96f96ae3a8fe0b7fc0201e7325f695a9cd4',
    W09 + '/receipts/0001.json': '28952cff7345612a3f2d4a0784c5a2fd8a17e44677e3deedf83371a198ff0ae0',
    str((RUN / 'ARE-genuine-work-reconciliation-0206.json').relative_to(ROOT)): '8bbf62336cb53e52c2f73966f756806ff59b7fc94b3e72b949de9a36ef3d9ced',
}
CHECKS = []
MATERIAL = {}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def structural(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hash_file(path):
    require(path.is_file() and not path.is_symlink(), 'missing or symbolic material: ' + str(path))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1048576):
            digest.update(chunk)
    return digest.hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def pin(path, expected, witness):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    require(path.resolve().is_relative_to(ROOT) or str(path).startswith('/tmp/cal-'), 'unexpected external material')
    observed = hash_file(path)
    require(observed == expected, 'original binding differs: ' + str(path))
    name = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    previous = MATERIAL.setdefault(name, {'path': name, 'sha256': expected, 'size_bytes': path.stat().st_size, 'witnesses': []})
    require(previous['sha256'] == expected, 'contradictory selected bindings')
    if witness not in previous['witnesses']:
        previous['witnesses'].append(witness)
    return path


def load(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    name = str(path.relative_to(ROOT))
    require(name in MATERIAL, 'document outside original receipt closure: ' + name)
    require(hash_file(path) == MATERIAL[name]['sha256'], 'fresh document binding differs')
    return parse(path.read_bytes())


def check(label, condition, **details):
    require(condition, label)
    CHECKS.append({'check': label, 'result': 'PASS', **details})


def schema_check(body, kind):
    path = 'authority/artifact-types/' + kind + '/v1/schema.json'
    schema = load(path)
    Draft202012Validator(schema).validate(body)
    return {'kind': kind, 'schema_binding': MATERIAL[path], 'record_structural_sha256': structural(body)}


def archive(path, expected_pins, expected_sha):
    require(hash_file(ROOT / path) == expected_sha, 'independent original archive hash differs')
    value = load(path)
    require(value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None
            and value['private_key_included'] is False and value['Session_memory_included'] is False, 'archive authority/private boundary')
    require(value['project_pins'] == expected_pins, 'external replay pins differ')
    originals = {}
    for name, row in value['files'].items():
        require(name in {'config.json', 'baseline.json', 'HEAD.json', 'transactions/0000000000.json', 'transactions/0000000001.json'}, 'unexpected archive entry')
        raw = base64.b64decode(row['base64_original_bytes'], validate=True)
        require(sha(raw) == row['sha256'], 'embedded original byte hash differs')
        originals[name] = parse(raw)
    require(len(originals) == 5, 'incomplete original branch')
    config, head = originals['config.json'], originals['HEAD.json']
    require(config['repository_admission_effect'] == 'none' and config['allowed_categories'] == ['artifact-instance']
            and config['allowed_effects'] == ['admit'], 'local-only source authority differs')
    require(value['files']['config.json']['sha256'] == expected_pins['config_sha256'], 'external config binding differs')
    for body in [config, head, originals['transactions/0000000000.json'], originals['transactions/0000000001.json']]:
        require(body['digest'] == structural({k: v for k, v in body.items() if k != 'digest'}), 'original structural digest differs')
    genesis, tx = originals['transactions/0000000000.json'], originals['transactions/0000000001.json']
    require(genesis['sequence'] == 0 and genesis['previous_digest'] is None and tx['sequence'] == head['sequence'] == 1
            and tx['previous_digest'] == genesis['digest'] and tx['digest'] == head['transaction_digest'] == expected_pins['expected_head'], 'original transaction chain differs')
    approval, proposal = tx['approval'], tx['proposal']
    core = {k: v for k, v in approval.items() if k != 'signature'}
    wanted = {'schema_version': 'lab-runtime-approval/v1', 'store_id': config['store_id'], 'owner_ref': config['owner_ref'],
              'scope_ref': proposal['scope_ref'], 'policy_ref': proposal['policy_ref'], 'challenge_route': proposal['challenge_route'],
              'source_snapshot_digest': proposal['source_snapshot_digest'], 'expected_head': proposal['expected_head'],
              'proposal_digest': structural(proposal), 'decision_core_digests': [structural(c) for c in tx['decision_cores']],
              'approved_at': approval['approved_at'], 'outcome': 'authorize-exact-local-effects'}
    require(core == wanted and approval['scope_ref'] == config['scope_ref'] and approval['expected_head'] == genesis['digest'], 'signature authority/material binding differs')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(config['public_key'])).verify(bytes.fromhex(approval['signature']), encoded(core))
    return {'archive_binding': MATERIAL[path], 'pins': expected_pins, 'public_key_sha256': sha(bytes.fromhex(config['public_key'])),
            'config_scope': config['scope_ref'], 'approved_at': approval['approved_at'], 'signed_local_transactions_verified': 1,
            'chain_transactions_verified': 2, 'files_restored': 0, 'private_key_restored': False,
            'verification_ceiling': 'Fresh original-byte/digest/chain/Ed25519 verification; original full semantic cold-replay receipt retained, not rerun here.'}, tx


def records(index, folder):
    result = {}
    for row in index['records']:
        path = str(Path(folder) / row['path'])
        pin(path, row['sha256'], folder + '/episode-index.json#/records')
        result[row['version_ref']] = {'binding': MATERIAL[path], 'body': load(path), 'role': row['role']}
    return result


def reconcile_learning(folder, receipt):
    index = load(folder + '/episode-index.json')
    recs = records(index, folder)
    lesson, application, outcome = [recs[index[key]] for key in ('lesson_ref', 'application_ref', 'outcome_ref')]
    for key, kind in [('lesson_ref', 'operational-lesson'), ('reflection_ref', 'agent-reflection'), ('application_ref', 'lesson-application'), ('outcome_ref', 'lesson-outcome-assessment')]:
        schema_check(recs[index[key]]['body'], kind)
    selection = load(folder + '/later/selection-1.json')
    pending = load(folder + '/later/application-pending.json')
    observed = load(folder + '/later/application-manifest.json')
    completed = load(folder + '/later/application-completed.json')
    review = load(folder + '/later/durable-lesson-review.json')
    rule = load(folder + '/later/durable-applicability-rule.json')
    context = load(folder + '/context-later.json')
    proof, tx = archive(folder + '/branch.snapshot', index['replay_pins'], index['archive_sha256'])
    target = [t for t in tx['proposal']['targets'] if t['version_ref'] == index['lesson_ref']]
    check(folder + ': exact independently signed Lesson original', len(target) == 1 and target[0]['record'] == lesson['body']
          and review['approval'] == tx['approval'] and review['fixture_only'] is True and review['canonical_admission'] is False)
    check(folder + ': selection/application/later process distinct', selection['applications_created'] == index['applications_after_selection'] == 0
          and index['actual_later_application'] and selection['selected_refs'] == [index['lesson_ref']]
          and completed['application_ref'] == index['application_ref'] and observed['lesson_ref'] == pending['lesson_ref'] == index['lesson_ref'])
    check(folder + ': independent later Agent and exact source cut', index['first_Agent_handles'] != index['new_Agent_handles']
          and index['first_Agent_invalidated'] and index['first_memory_erased'] and index['later_Agent_closed'] and index['later_memory_erased']
          and selection['session_ref'] == observed['session_ref'] == pending['session_ref'] == index['new_Agent_handles']['session_ref']
          and selection['source_head'] == pending['source_head'] == observed['source_head'] == index['replay_pins']['expected_head'])
    expiry = datetime.fromisoformat(lesson['body']['payload']['expires_at'])
    executed_at = datetime.fromisoformat(observed['observed_at'])
    check(folder + ': genuine original clock and scoped outcome', datetime.fromisoformat(proof['approved_at'].replace('Z', '+00:00')) <= executed_at < expiry
          and observed['returncode'] == 0 and observed['result']['preparation_posture'] == 'completed'
          and observed['result']['validated_records'] == 13 and observed['original_source_unchanged'] and observed['inline_only_change']
          and observed['result'] == load(folder + '/later/application-stdout.json'))
    op = outcome['body']['payload']
    check(folder + ': original prediction/evidence/counterevidence chain', op['predicted_outcome'] == pending['predicted_outcome']
          and op['lesson_application_ref'] == index['application_ref'] and application['body']['payload']['lesson_revision_ref'] == index['lesson_ref']
          and op['disposition'] == index['outcome_disposition'] == 'supported-for-this-controlled-case'
          and bool(op['evidence_refs']) and bool(op['counterevidence_refs']) and rule['counterevidence_posture'] == 'limits-causality-not-this-repair'
          and not index['general_benefit_established'] and not index['lesson_promoted'] and index['canonical_effects_applied'] == 0
          and op['causal_claim_ceiling'] == index['causal_claim_ceiling'])
    all_bound = {r['reference']: r for r in index['blobs']}
    unresolved = [ref for ref in op['counterevidence_refs'] if ref not in all_bound]
    check(folder + ': counterevidence originals resolve', not unresolved)
    reflection = recs[index['reflection_ref']]['body']
    original_observation_refs = reflection['payload']['observation_refs']
    check(folder + ': attributable real failure/Reflection/Lesson chain', bool(original_observation_refs)
          and all(ref in recs for ref in original_observation_refs)
          and index['reflection_ref'] in lesson['body']['payload']['evidence_refs']
          and any(r['counterpart_ref'] == index['reflection_ref'] and r['relation_kind_ref'] == 'relation.derives-from'
                  for r in lesson['body']['relation_refs']))
    source_observations = load(folder + '/later/source-observation-manifest.json')
    old, corrected = source_observations['observations']
    check(folder + ': original failure and existing success kept separate', old['result']['preparation_posture'] == 'rejected'
          and old['result']['validated_records'] == 0 and corrected['result']['preparation_posture'] == 'completed'
          and corrected['result']['validated_records'] == 13 and source_observations['failed_preparations'] == 1
          and source_observations['subject_bytes_unchanged'])
    ast.parse((ROOT / folder / 'later/repaired_builder.py').read_bytes())
    return {'episode_binding': MATERIAL[folder + '/episode-index.json'], 'source_authority': proof, 'task_ref': selection['task_ref'],
            'source_cut': selection['source_head'], 'context_binding': MATERIAL[folder + '/context-later.json'],
            'context_generator_source_bindings': index['original_sources'], 'selection': selection,
            'Lesson': lesson, 'Application': application, 'OutcomeAssessment': outcome,
            'predicted_outcome_original': pending, 'actual_process_observation': observed,
            'counterevidence_bindings': [all_bound[ref] for ref in op['counterevidence_refs']],
            'failure_reflection': reflection,
            'original_failure_records': [recs[ref] for ref in original_observation_refs],
            'original_failure_and_successor_process_manifest': source_observations,
            'clock_provenance': {'later_application': 'Recorded real host-clock sample from original later episode; preserved, not replaced by reconciliation time.',
                                 'signed_local_review': 'Original Ed25519-bound approved_at; a signature authenticates the recorded assertion, not an independent clock attestation.',
                                 'W05_failure_and_counterevidence': 'Both original observed_at fields are fixed 2026-10-08T12:00:00+00:00 fixture-clock values. They are not real elapsed/chronological evidence. In W06 that value is after its real later-episode timestamp; source/process provenance and pre-effect constructor order remain separate evidence.'},
            'original_execution_at': observed['observed_at'], 'original_lesson_expiry': lesson['body']['payload']['expires_at'],
            'currently_applicable': datetime.now(timezone.utc) < expiry,
            'current_application_authority': False, 'original_cold_replay_evidence': receipt,
            'claim': 'Real later controlled preparation repair and bounded assessment, separate from synthetic guard tests and fixture-only local authority.',
            'limitations': ['Pre-existing corrected builder success defeats a newly established causal-benefit claim.',
                            'The prepared thirteen records and current local Lesson are distinct from canonical admissions and human satisfaction.',
                            'Historical expiry is retained; reconciliation supplies no current permission or Lesson promotion.']}


def reconcile():
    began = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    receipts = {}
    for path, digest in SEEDS.items():
        pin(path, digest, 'externally selected immutable 0206 seed')
    for path in list(SEEDS)[:3]:
        r = load(path)
        require(r['result'] == 'PASS' and r['task_complete'] and r['actual_owner_outcome'] is None and r['authority_effect'] == 'none', 'original completed candidate receipt required')
        receipts[r['task']] = r
        for row in r['files'] + r.get('source_bindings', []):
            pin(row['path'], row['sha256'], path)
    # Include every selected W06 second-episode row, independent of its first predecessor.
    manifest = FLOW + '/learning/receipts/0002/manifest.json'
    pin(manifest, 'b57893193eeb67805275841c15aba48fa1fe629f854f7f1011097199770d3862', 'explicit W06 second-episode proof')
    for row in load(manifest)['files']:
        pin(row['path'], row['sha256'], manifest)
    check('all original receipt proof rows freshly verified at entry', True, files=len(MATERIAL))
    c12 = WORK + '/packages/0002'
    audit, selected, assessment = [load(c12 + '/' + name + '.json') for name in ('audit', 'selection', 'assessment')]
    observed = load(c12 + '/observed-episode.json')
    expected = load('implementation/lab-review/candidates/v1/packages/0001/preparation.json')
    expected_members = {m['member_id']: m for m in expected['members']}
    check('C12 real source audit acceptance independent of Work schema/signature', len(audit['members']) == audit['member_count'] == 13
          and set(expected_members) == {m['member_id'] for m in audit['members']} and assessment['actual_execution']
          and observed['actual_bounded_Work_performed'] and not audit['final_admission_ready'])
    checked_paths = {}
    for member in audit['members']:
        original = expected_members[member['member_id']]
        for key in ('member_class', 'proposed_owner_roles', 'requested_effect', 'exclusions'):
            require(member[key] == original[key], 'C12 changed member boundary')
        require(member['dependency_ids'] == original['dependencies'], 'C12 member dependency changed')
        require([(c['path'], c['expected_sha256']) for c in member['source_checks']] == [(r['path'], r['sha256']) for r in original['targets'] + original['evidence']], 'C12 omitted exact check')
        for row in member['source_checks']:
            pin(row['path'], row['expected_sha256'], c12 + '/audit.json')
            require(row['observed_sha256'] == row['expected_sha256'] and row['result'] == 'PASS', 'C12 observed check differs')
            checked_paths[row['path']] = row['expected_sha256']
    check('C12 all 28 exact inputs and 13 unresolved owner checks retained', len(checked_paths) == 28
          and checked_paths == audit['source_file_digests'] and audit['owner_authority_gaps'] == [m['member_id'] for m in audit['members']])
    work = load(c12 + '/work.json')
    schema_check(work, 'work')
    signed_c12, tx = archive(c12 + '/branch.snapshot', observed['replay_pins_after'], next(r['sha256'] for r in observed['public_outputs'] if r['path'].endswith('branch.snapshot')))
    check('C12 Work original independently signed; satisfaction separate', len(tx['proposal']['targets']) == 1
          and tx['proposal']['targets'][0]['record'] == work and assessment['result'] == 'PASS'
          and [c['criterion'] for c in assessment['acceptance_checks']] == selected['acceptance']
          and all(c['result'] == 'PASS' for c in assessment['acceptance_checks'])
          and observed['old_Agent_invalidated'] and observed['short_memory_erased'] and observed['repository_admissions_applied'] == 0)
    learning = {
        'W06': reconcile_learning(FLOW + '/learning/receipts/0002/observed', receipts['W06']['cold_verification']),
        'W09': reconcile_learning(W09 + '/runs/0004/scenarios/learning', load(W09 + '/runs/0007/audit/result.json')['cold_Learning']),
    }
    eroot, rroot = W09 + '/runs/0003/scenarios/engineering', W09 + '/runs/0001/scenarios/research'
    ec, rc = load(eroot + '/case.json'), load(rroot + '/case.json')
    ea, ra = load(eroot + '/assessment.json'), load(rroot + '/assessment.json')
    observations = load(rroot + '/observed.json')
    procedure = load(rc['procedure']['path'])
    ratios = [row['observations']['facade']['seconds'] / row['observations']['direct']['seconds'] for row in observations['trials']]
    check('W09 research genuine finite observations and negative hypothesis recomputed', procedure['samples'] == len(ratios) == 3
          and procedure['ratio_threshold'] == 0.8 and procedure['timeout_seconds'] == 45
          and [row['order'] for row in observations['trials']] == procedure['order']
          and ratios == ra['ratios'] and statistics.median(ratios) == ra['median_ratio'] > procedure['ratio_threshold']
          and ra['disposition'] == rc['facts']['hypothesis_disposition'] == receipts['W09']['Research_hypothesis_disposition'] == 'negative')
    for row in observations['trials']:
        for method, original in row['observations'].items():
            require(original['returncode'] == 0 and original['seconds'] > 0 and original['posture'] == 'completed', 'research observation incomplete')
            for stream in ('stdout', 'stderr'):
                pin(rroot + '/sample-' + str(row['sample']) + '-' + method + '.' + stream, original[stream + '_sha256'], rroot + '/observed.json')
    check('W09 engineering actual criterion and original seven checks', ec['facts']['actual_execution'] and ec['facts']['default_regression_tests'] == 42
          and ea['disposition'] == ec['facts']['assessment_disposition'] == 'supported' and len(ea['checks']) == 7
          and all(c['result'] == 'PASS' for c in ea['checks'].values()))
    selected_records = []
    for domain, case in [('engineering', ec), ('research', rc)]:
        for row in case['records']:
            if row['kind'] in {'work', 'work-outcome-assessment', 'operational-observation', 'operational-lesson', 'agent-reflection', 'lesson-application', 'lesson-outcome-assessment'}:
                body = load(row['path'])
                selected_records.append({'domain': domain, 'binding': MATERIAL[row['path']], 'version_ref': row['version_ref'], 'schema_check': schema_check(body, row['kind']), 'body': body})
    # No current/final API selection is assumed: record an exact historical API12 snapshot.
    api = 'product/lab/release-candidates/v1/interface/api-integration-v12'
    api_bindings = []
    for name, digest in [('source-manifest.json', '5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'),
                         ('contract-profile.json', '2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a')]:
        path = api + '/' + name
        pin(path, digest, 'historical API12 selection; not final-interface episode proof')
        api_bindings.append(MATERIAL[path])
    for path in ('product/lab/release-candidates/v1/release-scope.json', 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R05.md',
                 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R07.md', 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/S02.md'):
        pin(path, hash_file(ROOT / path), 'explicit current obligation snapshot; no prior immutable episode claim')
    # Fresh reads at exit; no digest cache substitutes for either material boundary.
    for path, row in MATERIAL.items():
        require(hash_file(Path(path) if Path(path).is_absolute() else ROOT / path) == row['sha256'], 'exit drift: ' + path)
    check('all selected original and obligation material freshly verified at exit', True, files=len(MATERIAL))
    return {'schema_version': 'lab-genuine-work-learning-reconciliation/v1-candidate', 'result': 'PASS',
            'started_at': began, 'completed_at': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - start,
            'authority_effect': 'none', 'actual_owner_outcome': None, 'human_response_created': False, 'canonical_admissions': 0,
            'domain_actions_reexecuted': 0, 'source_originals_mutated': 0, 'full_suite_rerun': False,
            'method_ceiling': 'Independent fresh byte closure, record schema, exact original output correspondence, finite research arithmetic, signed archive chain and Ed25519 verification. Historical full replay/clock assertions remain bound original evidence; no newly synthesized prior prediction.',
            'checks': CHECKS, 'material_count': len(MATERIAL), 'material_bytes': sum(r['size_bytes'] for r in MATERIAL.values()),
            'material_bindings': sorted(MATERIAL.values(), key=lambda r: r['path']),
            'C12': {'task_selection': selected, 'assessment': assessment, 'Work': work, 'source_authority': signed_c12,
                    'episode_binding': MATERIAL[c12 + '/observed-episode.json'], 'context_head': observed['context_head_before'],
                    'generator_manifest_binding': MATERIAL['implementation/lab-context/candidates/v1/packages/0004/generator-manifest.json'],
                    'source_snapshot_digest': observed['source_snapshot_digest'], 'source_profile_sha256': observed['source_profile_sha256'],
                    'scope': 'Actual bounded audit of thirteen C10 members/28 source files, not whole release or human outcome.'},
            'learning': learning, 'W09_work': {'engineering_case_binding': MATERIAL[eroot + '/case.json'], 'engineering_assessment': ea,
                    'research_case_binding': MATERIAL[rroot + '/case.json'], 'procedure': procedure, 'observations': observations,
                    'research_assessment': ra, 'actual_task_records': selected_records,
                    'current_generation_selection_binding': MATERIAL[W09 + '/packages/0002-learning-successor/selection.json'],
                    'original_audit_binding': MATERIAL[W09 + '/runs/0007/audit/result.json']},
            'acceptance_mapping': {
                'AC08': {'genuine_candidate_work_evidence': 'demonstrated within unchanged C12/W09 selected task scopes',
                         'engineering': 'C12 source audit and W09 seven declared checks supported',
                         'research': 'Three real finite comparisons completed; declared hypothesis negative, retained as satisfaction assessment rather than fabricated positive result',
                         'final_interface_delivery': 'not demonstrated by these original episode sources/cuts'},
                'AC09': {'genuine_candidate_learning_episode': 'demonstrated in unchanged W06/W09 selections: attributable failure/reflection, signed scoped Lesson, later real controlled repair, Application and counterevidence-bearing OutcomeAssessment',
                         'general_or_causal_effectiveness': False, 'automatic_canonical_admission': False,
                         'final_interface_delivery': 'not demonstrated by these original episode sources/cuts',
                         'additional_lesson_required_by_original_criterion': False}},
            'final_interface_binding': {'historical_api12_snapshot': api_bindings, 'final_selected_api_source': None,
                    'final_selected_api_profile': None, 'final_selected_S02_cut': None,
                    'gap': 'Original candidate evidence may be selected unchanged as historical work evidence. Final public API preparation/inspection must separately bind retained episode originals, Tasks/Work/Lesson/Application/OutcomeAssessment and actual returned domain evidence under its current source/cut/permission. An envelope or proposed attribution does not prove that delivery.'},
            'remaining_obligations': ['Freeze the actual final API/schema/context sources and verify episode evidence delivered through that exact interface and source cut.',
                    'Select retained original episode bytes explicitly in final R07/S02, with their candidate/private/source-history dispositions and claim ceilings.',
                    'Complete actual R05 human journeys and independently attributable responses; reconcile final package/privacy/local effects and owner/member closure.',
                    'Preserve expired/scoped Lessons; a changed applicability scope or new actual application needs its own current authority and exact revision, without retrospectively changing original evidence.'],
            'goal_complete': False, 'R05_complete': False, 'R07_complete': False, 'S02_complete': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args()
    require(hash_file(Path(__file__)) == args.script_sha256, 'independently supplied reconciliation source pin differs')
    ast.parse(Path(__file__).read_bytes())
    json_out = RUN / 'Genuine-work-learning-reconciliation-0206.json'
    md_out = RUN / 'Genuine-work-learning-reconciliation-0206.md'
    require(not json_out.exists() and not md_out.exists(), '0206 outputs already exist')
    try:
        report = reconcile()
    except Exception as error:
        report = {'schema_version': 'lab-genuine-work-learning-reconciliation/v1-candidate', 'result': 'FAIL',
                  'error_type': type(error).__name__, 'error': str(error), 'completed_at': datetime.now(timezone.utc).isoformat(),
                  'checks_completed': CHECKS, 'authority_effect': 'none', 'actual_owner_outcome': None, 'goal_complete': False}
    report['reconciliation_source_binding'] = {'path': str(Path(__file__).relative_to(ROOT)), 'sha256': args.script_sha256}
    require(hash_file(Path(__file__)) == args.script_sha256, 'reconciliation source changed before report')
    raw = encoded(report)
    with json_out.open('xb') as stream:
        stream.write(raw)
    if report['result'] == 'PASS':
        md = ('# Genuine Work and learning reconciliation 0206\n\n'
              'Independent verification passed for ' + str(report['material_count']) + ' selected files and ' + str(len(CHECKS)) + ' substantive checks. Original domain actions were not repeated.\n\n'
              '- AC08: unchanged C12 real source-audit Work and W09 engineering/research task observations provide bounded candidate evidence. Engineering is supported; the finite research hypothesis is negative. Schema validity and signed local authority are independently checked and do not establish task satisfaction by themselves.\n'
              '- AC09: unchanged W06/W09 originals establish attributable failure/reflection, scoped independently signed candidate Lesson, a later real controlled repair, Application and OutcomeAssessment with counterevidence. The earlier successful corrected builder limits causality; no general benefit or automatic canonical admission is established.\n'
              '- These episodes use their original generators, source cuts and candidate local permissions. They do not demonstrate delivery through the final selected API. Their scope does not require inventing a new lesson to replace a qualifying genuine episode.\n'
              '- R05 human journeys, final API delivery of exact retained evidence, complete R07 package/privacy validation and S02 owner/member/effect closure remain open. Historical expiry and all original bytes remain unchanged.\n\n'
              'The JSON contains exact Task/Work/Lesson/Application/OutcomeAssessment bodies, original predictions/process clocks/counterevidence, source bindings, fresh entry/exit proof rows and independently verified original Ed25519 archive chains. Fresh semantic full replay was not performed here; its original bound receipts remain explicit.\n\n'
              'JSON SHA-256: `' + sha(raw) + '`\n')
    else:
        md = '# Genuine Work and learning reconciliation 0206 — failed\n\n' + report['error_type'] + ': ' + report['error'] + '\n\nNo original evidence or closure claim was rewritten.\n'
    with md_out.open('x', encoding='utf-8') as stream:
        stream.write(md)
    print(json.dumps({'result': report['result'], 'actual_exit_code': 0 if report['result'] == 'PASS' else 1,
                      'json_path': str(json_out.relative_to(ROOT)), 'json_sha256': sha(raw),
                      'markdown_sha256': hash_file(md_out), 'script_sha256': args.script_sha256,
                      'checks': len(CHECKS), 'material_files': report.get('material_count'), 'error': report.get('error')}), flush=True)
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
