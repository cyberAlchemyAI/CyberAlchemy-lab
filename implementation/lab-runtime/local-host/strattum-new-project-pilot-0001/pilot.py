"""Isolated Project admission pilot over the selected installed governance API.

This driver supplies a different exact target to the installed v5 qualification
fixture. Its generated keys and approval represent only this local pilot.
"""
import argparse
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

PICK = sys.modules.get('cal_installed_runtime_selection_v1')
if PICK is None:
    raise RuntimeError('Use the installed selected-python launcher')
PICK.require_runtime_ready()
ROOT = PICK.root()
API = ROOT / PICK.current().package['entrypoint']['api_directory']
members = json.loads((API / 'integration-members.json').read_bytes())
governance = members['members']['governance']
if governance['directory'] != 'api-governance-integration-v5-current-t12-0001' or governance['source_sha256'] != '8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337':
    raise RuntimeError('selected installed API does not bind reviewed current T12 governance v5')
if hashlib.sha256((API.parent / governance['directory'] / 'source-manifest.json').read_bytes()).hexdigest() != governance['source_sha256']:
    raise RuntimeError('installed governance source manifest differs from selected member')
sys.path.insert(0, str(API.parent))
G = importlib.import_module(governance['directory'] + '.fixture')
if not Path(G.__file__).resolve().is_relative_to(ROOT.resolve()):
    raise RuntimeError('governance fixture imported from outside selected installation')
P = importlib.import_module(API.name + '.protocol')

PROJECT = 'project:lab-strattum-feature-gap-pilot'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_new(path, value):
    raw = G.encoded(value) + b'\n'
    return write_raw_new(path, raw)


def write_raw_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return digest(raw)


def read_native_transaction(store_parent, sequence):
    if type(sequence) is not int or sequence < 0:
        raise ValueError('cold native transaction sequence differs')
    handles = []
    try:
        parent = os.open(store_parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for name in ('native-store', 'transactions'):
            parent = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                             dir_fd=parent)
            handles.append(parent)
        name = f'{sequence:010d}.json'
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=parent)
        handles.append(handle)
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError('unsafe native transaction original')
        with os.fdopen(os.dup(handle), 'rb') as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        after = os.fstat(handle)
        attached = os.stat(name, dir_fd=parent, follow_symlinks=False)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns)
        if len(raw) != before.st_size or identity(before) != identity(after) or identity(before) != identity(attached):
            raise ValueError('native transaction original changed during read')
        return raw
    finally:
        for handle in reversed(handles):
            os.close(handle)


def project_identity_record(scope, owner, route, evidence_ref, schema_raw):
    if type(route) is not str or not route:
        raise ValueError('selected native challenge route missing')
    project = {'schema_version': 'cyberalchemy-lab-project-identity/v1',
               'project_id': PROJECT, 'version': '1.0.0-candidate.1',
               'name': 'Lab Strattum feature gap pilot',
               'status': 'candidate-unadmitted', 'authority_effect': 'none',
               'semantic_definition_refs': ['CAV2-D60@1.0.0-candidate.1',
                                            'cal.definition.identity-carrier@1.0.0-candidate.1'],
               'purpose': 'Coordinate the bounded Strattum feature gap pilot.',
               'coordination_scope': {'includes': ['Local Lab feature inspection',
                                                   'Project State evidence coordination'],
                                      'excludes': ['Product meaning',
                                                   'Canonical Project admission',
                                                   'Production runtime activation']},
               'accountable_owner_ref': owner,
               'evidence_refs': [evidence_ref],
               'challenge_route': route,
               'claim_ceiling': 'Isolated disposable local Store only; no canonical admission or separate runtime.'}
    G.Draft202012Validator(G.parse(schema_raw), format_checker=G.FormatChecker()).validate(project)
    return project


class ProjectFixture(G.Fixture):
    def build_review(self):
        carrier = self.data['projection']['contracts'].get('cal.artifact-type.project-identity/v1')
        if carrier is None or carrier['lifecycle_state'] not in ('admitted-current', 'local-admitted-current'):
            raise ValueError('selected native Store has no current ProjectIdentity/v1 carrier')
        if carrier['artifact']['instance_contract']['identity_field'] != 'project_id':
            raise ValueError('selected ProjectIdentity contract identity field differs')
        cli = __import__(G.NATIVE_NAME + '.cli', fromlist=['*'])
        native = cli.example(self.store, 'strattumprojectpilot')
        schema_path = ROOT / 'authority/artifact-types/project-identity/v1/schema.json'
        schema_raw = schema_path.read_bytes()
        self.scope_evidence = self.body('evidence:pilot-project-scope',
                                        {'project_id': PROJECT, 'scope_ref': self.scope,
                                         'intended_use': 'Local Lab feature gap pilot only',
                                         'authority_effect': 'none'})
        project = project_identity_record(self.scope, self.role, native.get('challenge_route'),
                                          self.scope_evidence['ref'], schema_raw)
        target = native['targets'][0]
        target.update(version_ref=PROJECT + '@1.0.0-candidate.1',
                      carrier_ref='cal.artifact-type.project-identity/v1', record=project,
                      decision_ref='decision:local:strattum-project-pilot')
        original = b'  ' + G.encoded(project) + b'\n'
        native = G.U.with_originals(native, {target['version_ref']: original}, {})
        if native['targets'][0]['record']['challenge_route'] != native['challenge_route']:
            raise ValueError('ProjectIdentity challenge route differs from exact native proposal')
        self.native = native
        self.target_package = self.body('package:pilot-native', native)
        cores = self.store.review(native)['decision_cores']
        self.core = self.body('core:pilot', cores[0])
        keypath = self.root / 'pilot-owner.pem'
        G.put(keypath, self.owner.private_bytes(G.serialization.Encoding.PEM,
                                                G.serialization.PrivateFormat.PKCS8,
                                                G.serialization.NoEncryption()))
        approval = self.store.authorize(native, keypath)
        self.approval = self.body('approval:pilot-native', approval)
        nt = native['targets'][0]
        content = self.raw('content:pilot-original-project', original)
        metadata = self.body('metadata:pilot', {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
                                               'category': 'artifact-instance',
                                               'decision_ref': nt['decision_ref'], 'contract': None})
        self.raw(schema_path.relative_to(ROOT).as_posix(), schema_raw)
        profile = self.raw((G.NATIVE / 'profile.json').relative_to(ROOT).as_posix(),
                           (G.NATIVE / 'profile.json').read_bytes())
        workspace = self.body('workspace:pilot', {'authority_effect': 'none', 'claim_ceiling': G.CEILING})
        public_target = {'operation': 'admit', 'artifact': {'scope_ref': self.scope,
                         'identity_ref': PROJECT, 'version_ref': nt['version_ref'],
                         'carrier_ref': nt['carrier_ref'], 'byte_sha256': G.sha(original)},
                         'predecessor': None,
                         'content': {'content_ref': content['ref'], 'byte_sha256': G.sha(original),
                                     'size_bytes': len(original), 'media_type': 'application/json'},
                         'candidate_binding': metadata,
                         'requested_effect': 'Admit one Project artifact in this isolated local Store only',
                         'decision_core_binding': self.core}
        self.effect = self.body('effect:pilot', public_target)
        public = {'schema_version': 'lab-change-proposal/v1-candidate', 'proposal_ref': 'proposal:pilot',
                  'actor': self.actor, 'scope_ref': self.scope, 'base_cut': self.current,
                  'source_profile_binding': profile, 'workspace_binding': workspace,
                  'targets': [public_target],
                         'schema_bindings': [G.binding(schema_path.relative_to(ROOT).as_posix(), schema_raw)],
                  'connection_proposals': [], 'evidence_bindings': [],
                  'idempotency_key': 'strattum-project-pilot',
                  'challenge_route': native['challenge_route'], 'authority_effect': 'none'}
        self.public = self.body('proposal:pilot', public)
        evidence = self.body('evidence:pilot-native-review', self.store.review(native))
        report = {'schema_version': 'lab-validation-report/v1-candidate', 'report_ref': 'report:pilot-native',
                  'subject_binding': self.public, 'source_cut': self.current,
                  'validator_binding': G.binding((G.NATIVE / 'lab_runtime/operations.py').relative_to(ROOT).as_posix(),
                                                 (G.NATIVE / 'lab_runtime/operations.py').read_bytes()),
                  'checks': [{'check_ref': 'check:exact-native-original-schema', 'obligation_ref': 'O-EXACT',
                              'result': 'pass', 'evidence_bindings': [evidence], 'claim_ceiling': G.CEILING}],
                  'reference_checks': [], 'gaps': [], 'result': 'pass', 'claim_ceiling': G.CEILING,
                  'authority_effect': 'none'}
        report_b = self.body('report:pilot-native', report)
        principal = self.original('principal')
        principal.update(node_id=self.principal, scope_ref=self.scope, claim_ceiling=G.CEILING)
        principal['payload'].update(principal_kind='operator',
                                    stable_subject_ref='person-reference:synthetic-project-pilot-operator')
        pb = self.body('principal:pilot-original', principal)
        role = self.original('role')
        role.update(node_id=self.role, scope_ref=self.scope)
        rb = self.body('role:pilot-original', role)
        assignment = self.original('role-assignment')
        assignment.update(role_ref=self.role, assignee_ref=principal['payload']['stable_subject_ref'],
                          scope_ref=self.scope)
        assignment['period'] = {'start': G.instant(self.begin).strftime('%Y-%m-%dT%H:%M:%SZ'), 'end': None}
        ab = self.body('assignment:pilot-original', assignment)
        recognition = self.body('recognition:pilot-owner',
                                {'schema_version': 'lab-owned-governance-owner-recognition/v1-candidate',
                                 'principal_binding': pb, 'role_binding': rb, 'assignment_binding': ab,
                                 'public_key_hex': self.owner.public_key().public_bytes_raw().hex(),
                                 'scope_ref': self.scope, 'authority_effect': 'none', 'claim_ceiling': G.CEILING})
        owner = {'principal_ref': self.principal, 'role_ref': self.role, 'principal_binding': pb,
                 'role_binding': rb, 'assignment_binding': ab, 'recognition_binding': recognition,
                 'public_key_hex': self.owner.public_key().public_bytes_raw().hex(),
                 'not_before': self.begin, 'expires_at': self.end}
        self.member = {'core_binding': self.core, 'effect_binding': self.effect,
                       'recognition_binding': recognition, 'owner_principal_ref': self.principal,
                       'owner_role_ref': self.role}
        profile_body = self.original('workflow-decision-profile')
        profile_body['scope_ref'] = self.scope
        profile_body['payload'].update(decision_mode='single', exact_target_required=True,
                                       default_checkpoint_kind='final-review')
        self.workflow = self.artifact('profile:pilot@1', profile_body)
        cb = self.original('decision-checkpoint')
        cb.update(node_id='decision-checkpoint:pilot', scope_ref=self.scope, owner_ref=self.principal)
        cb['payload'].update(workflow_profile_ref=self.workflow['version_ref'],
                             decision_bundle_ref='decision-bundle:pilot', presentation_state='pending',
                             closed_at=None)
        self.checkpoint_ref = self.artifact('checkpoint:pilot@1', cb)
        self.checkpoint = {'ref': 'checkpoint:pilot@1', 'sha256': self.checkpoint_ref['byte_sha256']}
        bb = self.original('decision-bundle')
        bb.update(node_id='decision-bundle:pilot', scope_ref=self.scope, owner_ref=self.principal)
        ordered = [{'decision_ref': cores[0]['decision_ref'], 'decision_core_sha256': self.core['sha256'],
                    'scope_ref': self.scope, 'owner_ref': self.principal, 'effect_kind': 'artifact-instance:admit',
                    'target_refs': [nt['version_ref']],
                    'target_digests': [{'target_ref': nt['version_ref'], 'sha256': G.sha(original)}],
                    'selected_outcome': None}]
        bb['payload'].update(ordered_decisions=ordered, bundle_digest=G.sha(G.encoded(ordered)),
                             checkpoint_ref=cb['node_id'])
        bundle_ref = self.artifact('bundle:pilot@1', bb)
        example = self.body('example:pilot', {'original_target_binding': content, 'authority_effect': 'none'})
        manifest = {'schema_version': 'lab-exact-review-materialization/v1-candidate',
                    'base_cut': self.current, 'proposal_binding': self.public,
                    'all_targets_materialized': True, 'atomicity_requirement': 'all-or-nothing',
                    'human_checkpoint_count': 1, 'actual_owner_outcome': None,
                    'runtime_activations': 0, 'external_effect_refs': [],
                    'repository_admissions_applied': 0,
                    'targets': [{'target': public_target, 'core_binding': self.core,
                                 'original_content_binding': content}],
                    'generated_carriers': [{'artifact': self.checkpoint_ref, 'object_binding': self.checkpoint},
                                           {'artifact': bundle_ref,
                                            'object_binding': {'ref': 'bundle:pilot@1',
                                                               'sha256': bundle_ref['byte_sha256']}}],
                    'ordered_core_bindings': [self.core], 'example_bindings': [example],
                    'ordered_required_owner_responses': [{'core_binding': self.core,
                                                          'owner_role_ref': self.role,
                                                          'owner_principal': {'identity_ref': self.principal},
                                                          'selected_outcome': None}]}
        self.manifest = self.body('manifest:pilot-review', manifest)
        review = {'schema_version': 'lab-review-package/v1-candidate', 'package_ref': 'review-package:pilot',
                  'base_cut': self.current, 'manifest_binding': self.manifest,
                  'decision_bundle': bundle_ref, 'checkpoint': self.checkpoint_ref,
                  'workflow_decision_profile': self.workflow, 'ordered_core_bindings': [self.core],
                  'validation_bindings': [report_b], 'example_bindings': [example],
                  'operational_instruction_bindings': [], 'all_targets_materialized': True,
                  'human_checkpoint_count': 1, 'atomicity_requirement': 'all-or-nothing',
                  'invalidation_conditions': ['any-target-original-byte-change'], 'authority_effect': 'none'}
        self.review = self.body('review:pilot', review)
        self.channel_evidence = self.body('recognition:pilot-channel',
                                          {'scope_ref': self.scope, 'authorization_channel': 'operator-signature',
                                           'authority_effect': 'none', 'claim_ceiling': G.CEILING})
        selected = {'review_package_binding': self.review, 'proposal_binding': self.public,
                    'target_package_binding': self.target_package, 'runtime_approval_binding': self.approval,
                    'required_members': [self.member], 'recognized_owners': [owner],
                    'channel_key': {'public_key_hex': self.attestor.public_key().public_bytes_raw().hex(),
                                    'evidence_binding': self.channel_evidence, 'not_before': self.begin,
                                    'expires_at': self.end, 'channel': 'operator-signature'}}
        self.resolution = self.outcome('approve-exact-effect')
        return selected


def run(output):
    output = Path(output).absolute()
    if output.exists() or not output.parent.is_dir() or any(p.is_symlink() for p in output.parents):
        raise ValueError('fresh private output under a real parent required')
    output.mkdir(mode=0o700)
    write_new(output / 'INTENT.json', {'purpose': 'isolated installed Lab Project admission pilot',
                                      'project_ref': PROJECT, 'status': 'started', 'authority_effect': 'none'})
    dfd = os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)
    schemas = P.Schemas(PICK.binding('api.profile')['sha256'])
    private = Path(tempfile.mkdtemp(prefix='cal-strattum-project-pilot-', dir='/tmp'))
    try:
        fixture = ProjectFixture(private, schemas)
    except Exception:
        shutil.rmtree(private)
        raise
    operation_started = None
    checkpoint_recorded = False
    checkpoint_reply = None
    commit_reply = None
    completed = False
    try:
        checkpoint_call = fixture.checkpoint_call('pilot:checkpoint')
        operation_started = 'checkpoint.resolve'
        checkpoint_reply = fixture.service.call(P.compact(checkpoint_call))
        if checkpoint_reply.get('kind') != 'result':
            raise RuntimeError('checkpoint refused: ' + str(checkpoint_reply.get('message', {}).get('code')))
        checkpoint_recorded = True
        resolution_binding = fixture.host.object(G.encoded(fixture.resolution))
        commit_call = fixture.admission_call(resolution_binding, 'pilot:admission')
        operation_started = 'admission.apply'
        commit_reply = fixture.service.call(P.compact(commit_call))
        if commit_reply.get('kind') != 'result':
            raise RuntimeError('admission refused: ' + str(commit_reply.get('message', {}).get('code')))
        cold = G.S.Store(private / 'native-store', ROOT).replay(require_current=True)
        subjects = [s for s in cold['projection']['subjects'].values()
                    if s['identity'] == PROJECT and s['effective_state'] == 'local-admitted-current']
        if len(subjects) != 1 or subjects[0]['kind'] != 'project-identity':
            raise RuntimeError('new Project Identity subject missing from cold native replay')
        original = G.U.original_bytes(fixture.store, subjects[0]['version_ref'],
                                      cold['transactions'][-1]['digest'])
        if G.U.parse_original(original) != subjects[0]['record']:
            raise RuntimeError('cold Project original bytes disagree with replayed subject')
        evidence_ref = fixture.scope_evidence['ref']
        evidence_raw = fixture.memory[evidence_ref]
        if (subjects[0]['record']['evidence_refs'] != [evidence_ref] or
                digest(evidence_raw) != fixture.scope_evidence['sha256']):
            raise RuntimeError('Project scope evidence differs from admitted original')
        evidence_sha = write_raw_new(output / 'SCOPE-EVIDENCE.json', evidence_raw)
        if evidence_sha != fixture.scope_evidence['sha256'] or digest((output / 'SCOPE-EVIDENCE.json').read_bytes()) != evidence_sha:
            raise RuntimeError('retained Project scope evidence cold read differs')
        transaction_raw = read_native_transaction(private, cold['head']['sequence'])
        if G.parse(transaction_raw) != cold['transactions'][-1]:
            raise RuntimeError('cold native transaction original disagrees with replay')
        transaction_sha = write_raw_new(output / 'SIGNED-TRANSACTION.json', transaction_raw)
        if digest((output / 'SIGNED-TRANSACTION.json').read_bytes()) != transaction_sha:
            raise RuntimeError('retained native transaction original cold read differs')
        cold_sha = write_new(output / 'COLD-READBACK.json',
                             {'schema_version': 'lab-strattum-project-cold-readback/v1',
                              'project_ref': PROJECT, 'subject': subjects[0],
                              'head': cold['head'], 'transaction_sha256': transaction_sha,
                              'generated_state_ref': cold['projection']['state']['node_id'],
                              'generated_state_project_ref': cold['projection']['state']['payload']['project_ref'],
                              'authority_effect': 'none'})
        receipt = {'schema_version': 'lab-strattum-new-project-pilot/v1',
                   'project_ref': PROJECT, 'scope_ref': fixture.scope,
                   'target_version_ref': subjects[0]['version_ref'],
                   'target_record_sha256': G.sha(original),
                   'scope_evidence_ref': evidence_ref,
                   'scope_evidence_sha256': evidence_sha,
                   'checkpoint_reply_sha256': digest(P.compact(checkpoint_reply)),
                   'commit_reply_sha256': digest(P.compact(commit_reply)),
                   'transaction_sha256': transaction_sha, 'cold_readback_sha256': cold_sha,
                   'policy_sha256': fixture.policy_pin,
                   'api_source_sha256': PICK.binding('api.source')['sha256'],
                   'api_profile_sha256': PICK.binding('api.profile')['sha256'],
                   'pilot_driver_sha256': digest(Path(__file__).read_bytes()),
                   'cold_head': cold['head'],
                   'generated_state_ref': cold['projection']['state']['node_id'],
                   'generated_state_project_ref': cold['projection']['state']['payload']['project_ref'],
                   'store_disposition': 'disposable-private-tmp-store',
                   'cold_readback_scope': 'observed-in-process-before-disposable-store-removal',
                   'independently_replayable_durable_project_runtime': False,
                   'separate_project_runtime': False, 'repository_admissions_applied': 0,
                   'authority_effect': 'none'}
        receipt_sha = write_new(output / 'RESULT.json', receipt)
        if digest((output / 'RESULT.json').read_bytes()) != receipt_sha:
            raise RuntimeError('result cold read differs')
        dfd = os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        completed = True
        return {'result': 'PASS-disposable-local-project-identity-artifact', 'receipt_sha256': receipt_sha,
                'output': str(output), 'project_ref': PROJECT,
                'generated_state_project_ref': receipt['generated_state_project_ref'],
                'separate_project_runtime': False, 'authority_effect': 'none'}
    finally:
        try:
            fixture.service.close()
        finally:
            if operation_started is None or completed:
                shutil.rmtree(private)
            else:
                write_new(output / 'RECONCILIATION-REQUIRED.json',
                          {'schema_version': 'lab-strattum-project-reconciliation/v1',
                           'private_store': str(private), 'last_started_operation': operation_started,
                           'checkpoint_result_observed': checkpoint_recorded,
                           'last_reply_kind': (commit_reply if operation_started == 'admission.apply' else checkpoint_reply or {}).get('kind'),
                           'idempotency_key': 'pilot:admission' if operation_started == 'admission.apply' else 'pilot:checkpoint',
                           'retry_allowed': False,
                           'authority_effect': 'none'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.output), sort_keys=True))
    except Exception as exc:
        root = Path(args.output).absolute()
        if root.is_dir() and not (root / 'RESULT.json').exists():
            write_new(root / 'REFUSAL.json',
                      {'schema_version': 'lab-strattum-new-project-pilot-refusal/v1',
                       'project_ref': PROJECT, 'phase': 'preflight-or-application',
                       'exception_type': type(exc).__name__, 'reason': str(exc),
                       'repository_admissions_applied': 0, 'authority_effect': 'none'})
        print(json.dumps({'result': 'REFUSED', 'reason': str(exc), 'authority_effect': 'none'}, sort_keys=True))
        raise SystemExit(1)
