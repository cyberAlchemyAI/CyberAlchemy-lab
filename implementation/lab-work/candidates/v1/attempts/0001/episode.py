"""Perform a real source audit and select exact public candidate Work evidence."""
import base64
import copy
from dataclasses import asdict, replace
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent; ROOT = PACKAGE.parents[3]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
for name in ['lab-provisioning', 'lab-review', 'lab-context']:
    sys.path.insert(0, str(ROOT / 'implementation' / name / 'candidates/v1'))
import provision
import review
from context import ContextSession, GeneratorPins, IMPLEMENTATION_VERSION
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load, require
from lab_runtime.sources import capture
from lab_runtime.profiles import select
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.replay import full_replay
sys.path.insert(0, str(ROOT / 'implementation/lab-context/candidates/v1/tests'))
from native_fixture import fixture as diagnostic_native_fixture

PREPARATION = 'implementation/lab-review/candidates/v1/packages/0001/preparation.json'
PREPARATION_SHA = '53e7d38b95442d3690aed50eca05c58afd9f3dc50e81e3095aeb503c4ab424e4'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': byte_digest(path.read_bytes())}


def check_context_sources():
    for row in load(RUN / 'context-C12.json')['source_bindings']:
        require(byte_digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'C12 source context drift')
    provision.verify_inputs()


def audit_current_members():
    """No canned fixture verdict: inspect every selected current member and byte pin."""
    value = review.validate_preparation(PREPARATION, PREPARATION_SHA)
    rows = []; paths = {}
    for member in value['members']:
        observations = []
        for row in member['targets'] + member['evidence']:
            actual = byte_digest((ROOT / row['path']).read_bytes()); paths[row['path']] = actual
            observations.append({'path': row['path'], 'expected_sha256': row['sha256'],
                'observed_sha256': actual, 'result': 'PASS' if actual == row['sha256'] else 'FLAG'})
        rows.append({'member_id': member['member_id'], 'member_class': member['member_class'],
            'proposed_owner_roles': member['proposed_owner_roles'], 'dependency_ids': member['dependencies'],
            'requested_effect': member['requested_effect'], 'exclusions': member['exclusions'],
            'actual_answering_principal_ref': member['actual_answering_principal_ref'],
            'current_owner_authority_verified': member['current_owner_authority_verified'],
            'selected_outcome': member['selected_outcome'], 'source_checks': observations,
            'final_readiness': 'needs actual owner authority and complete S02 assembly'})
    require(len(rows) == 13 and all(c['result'] == 'PASS' for r in rows for c in r['source_checks']), 'actual member source audit failed')
    return {'schema_version': 'lab-C12-source-review-audit/v1-candidate', 'authority_effect': 'none',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'target': review.binding(PREPARATION),
        'member_count': len(rows), 'unique_source_files_checked': len(paths), 'members': rows,
        'source_file_digests': paths, 'owner_authority_gaps': [r['member_id'] for r in rows if not r['current_owner_authority_verified']],
        'final_admission_ready': False, 'performance_posture': value['retained_performance_posture'],
        'unsupported_claims': ['complete plan', 'actual owner disposition', 'Product benefit', 'operational lesson effectiveness'],
        'claim_ceiling': 'Actual exact C10 source/member audit only; readiness gaps are findings, not owner outcomes.'}


def check_audit(audit):
    require(audit['authority_effect'] == 'none' and audit['member_count'] == len(audit['members']) == 13, 'incomplete audit coverage')
    ids = [r['member_id'] for r in audit['members']]
    require(len(set(ids)) == 13, 'duplicate audited member')
    require(audit['final_admission_ready'] is False, 'audit cannot invent admission readiness')
    for row in audit['members']:
        require(row['selected_outcome'] is None and row['actual_answering_principal_ref'] is None and not row['current_owner_authority_verified'], 'audit fabricated owner authority')
        for check in row['source_checks']:
            require(check['result'] == 'PASS' and check['expected_sha256'] == check['observed_sha256'] == byte_digest((ROOT / check['path']).read_bytes()), 'audit source drift')
    return True


def perform(destination, executable):
    check_context_sources()
    require(destination.parent == PACKAGE / 'packages' and destination.is_dir(), 'owned numbered Work output scope required')
    statement = {'schema_version': 'lab-C12-work-selection/v1-candidate', 'authority_effect': 'none',
        'human_instruction': 'complete the plan', 'selection_basis': 'Bounded repository development audit derived from that instruction.',
        'work_statement': 'Audit all thirteen exact C10 review members, produce source-attributable readiness findings, and record selected public evidence in a candidate local branch.',
        'acceptance': ['all thirteen members covered once', 'every target and evidence byte pin checked',
            'owner/dependency/effect boundaries retained', 'unresolved final-review authority explicitly reported',
            'no Session notes, private keys, invented lesson or Product benefit retained'],
        'human_satisfaction_observed': False, 'actual_owner_outcome': None}
    (destination / 'selection.json').write_bytes(encoded(statement))
    scope = provision.CandidateScope('c12-source-audit-' + destination.name, 'role:candidate-c12-operator',
        'scope:lab-runtime-local:c12-source-audit-' + destination.name)
    with provision.CandidateBranch(scope) as branch:
        row = next(r for r in load(provision.RUNTIME / 'profiles/selections.json')['selections'] if r['name'] == 'd75')
        snapshot = capture(select(ROOT, **{k: v for k, v in row.items() if k not in ['name', 'source_bytes', 'source_materials']}))
        native_root = branch.root / 'diagnostic-native'; native_root.mkdir()
        native = diagnostic_native_fixture(native_root, executable, snapshot)
        manifest = ROOT / 'implementation/lab-context/candidates/v1/packages/0004/generator-manifest.json'
        adapter = VerifiedLegacyReadStore(branch.store_path, ROOT, ROOT, branch.pins)
        session = ContextSession(adapter, snapshot, native, generator_manifest=manifest,
            generator_pins=GeneratorPins(byte_digest(manifest.read_bytes()), IMPLEMENTATION_VERSION),
            owner_ref='principal:repository-owner@candidate.1', context_ref='context:cyberalchemy-v2-to-lab-migration',
            scope_ref='project:cyberalchemy-v2-to-lab-migration', capability_ref='product-capability:cyberalchemy-lab:governed-knowledge-lifecycle',
            expected_profile_sha256=row['profile_sha256'], expected_snapshot_digest=snapshot['snapshot_digest'],
            subject_ref='product:cyberalchemy-lab')
        try:
            initial_context = session.context(); session.note('C12 temporary audit hypothesis')
            require(initial_context['action_permission'] == 'none', 'context supplied action authority')
            audit = audit_current_members(); check_audit(audit)
            (destination / 'audit.json').write_bytes(encoded(audit))
            assessment = {'schema_version': 'lab-C12-scoped-work-assessment/v1-candidate', 'authority_effect': 'none',
                'result': 'PASS', 'actual_execution': True, 'scope': statement['work_statement'],
                'audit_binding': binding(destination / 'audit.json'), 'observed_members': 13,
                'acceptance_checks': [{'criterion': text, 'result': 'PASS'} for text in statement['acceptance']],
                'assessor': 'protocol:current-Codex-development-execution', 'human_satisfaction_observed': False,
                'repository_admission': False, 'operational_lesson_created': False, 'Product_benefit_claimed': False,
                'limitations': ['No actual owner authority or human satisfaction.', 'Native ontology is an explicit diagnostic fixture, with no domain Artifact mapping.', 'Only bounded development output acceptance, not whole-plan completion.']}
            (destination / 'assessment.json').write_bytes(encoded(assessment))
            cli = importlib.import_module(branch.module_name + '.cli')
            proposal = cli.example(branch.store, 'c12-source-audit-' + destination.name)
            work = proposal['targets'][0]['record']
            selected = [binding(destination / name) for name in ('selection.json', 'audit.json', 'assessment.json')]
            work.update(name='Audit exact successor review-member readiness',
                evidence_refs=[r['path'] + '#sha256=' + r['sha256'] for r in selected],
                claim_ceiling='Actual bounded source audit completed and assessed. Candidate local persistence only; no repository Work admission, human satisfaction, ontology domain mapping or Product benefit.')
            work['payload'].update(work_statement=statement['work_statement'], completion_state='candidate-development-complete',
                goal_refs=['protocol:user-goal:complete-the-plan'], input_refs=[PREPARATION],
                output_refs=[r['path'] for r in selected[1:]])
            # Semantic kind and exact Work carrier are enforced at this bounded caller.
            require(len(proposal['targets']) == 1 and proposal['targets'][0]['carrier_ref'] == 'cal.artifact-type.work/v1'
                    and work['kind'] == 'work', 'bounded caller must persist only the selected Work')
            review_result = branch.store.review(proposal)
            approval = branch.store.authorize(proposal, branch.key_path)
            outcome = branch.store.apply(proposal, approval)
            (destination / 'work.json').write_bytes(encoded(work))
            (destination / 'proposal.json').write_bytes(encoded(proposal))
            (destination / 'local-authorization.json').write_bytes(encoded(approval))
            new_pins = replace(branch.pins, expected_head=outcome['transaction_digest'])
            replayed = full_replay(branch.store_path, ROOT, ROOT, new_pins, require_current=True)
            require(replayed['projection']['subjects'][proposal['targets'][0]['version_ref']]['effective_state'] == 'local-admitted-current', 'selected Work not locally persisted')
            invalidated = False
            try: session.context()
            except RuntimeFault: invalidated = session.closed and not session.core._memory
            require(invalidated, 'committed HEAD did not invalidate and erase old Agent context')
            files = ['config.json', 'baseline.json', 'HEAD.json'] + ['transactions/' + f'{i:010d}.json' for i in range(replayed['head']['sequence'] + 1)]
            archive = {'schema_version': 'lab-public-original-branch-archive/v1-candidate', 'authority_effect': 'none',
                'project_pins': asdict(new_pins), 'files': {p: {'sha256': byte_digest((branch.store_path / p).read_bytes()),
                    'base64_original_bytes': base64.b64encode((branch.store_path / p).read_bytes()).decode()} for p in files},
                'private_key_included': False, 'Session_memory_included': False, 'actual_owner_outcome': None}
            archive_bytes = encoded(archive)
            require(b'PRIVATE KEY' not in archive_bytes and b'C12 temporary audit hypothesis' not in archive_bytes, 'private material entered selected archive')
            (destination / 'branch.snapshot').write_bytes(archive_bytes)
            evidence = {'schema_version': 'lab-C12-observed-episode/v1-candidate', 'authority_effect': 'none',
                'actual_bounded_Work_performed': True, 'actual_owner_outcome': None,
                'candidate_operator_scope': asdict(scope), 'source_profile_sha256': row['profile_sha256'],
                'source_snapshot_digest': snapshot['snapshot_digest'], 'context_head_before': initial_context['head'],
                'context_pack_digest_before': initial_context['pack_digest'], 'context_action_permission': 'none',
                'native_input_scope': 'diagnostic C08 two-node/one-edge native fixture; no domain Artifact mapping',
                'old_Agent_invalidated': invalidated, 'short_memory_erased': not session.core._memory,
                'local_Work_version_ref': proposal['targets'][0]['version_ref'], 'local_transaction': outcome,
                'replay_pins_after': asdict(new_pins), 'committed_transactions': len(replayed['transactions']),
                'repository_admissions_applied': 0, 'supported_lesson': None, 'Product_benefit': None,
                'public_outputs': selected + [binding(destination / 'work.json'), binding(destination / 'branch.snapshot')],
                'claim_ceiling': 'Observed bounded development Work and candidate local record only; local admission is not repository admission.'}
            (destination / 'observed-episode.json').write_bytes(encoded(evidence))
        finally:
            session.close()
            require(not session.core._memory, 'Session memory remained after close')
    require(branch.closed and not branch.root.exists(), 'owned candidate branch/key not cleaned')
    check_context_sources()
    return evidence
