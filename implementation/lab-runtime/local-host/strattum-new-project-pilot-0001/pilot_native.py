"""One disposable local ProjectIdentity admission through selected native Store."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import stat
import tempfile


SOURCE = Path(__file__).with_name('pilot.py')
PILOT_HELPER_SHA = 'dc19fe89f8448dd6f998b8ea0d8ad8dad5e56ba021804a8e52d4d936dbbf3447'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != PILOT_HELPER_SHA:
    raise RuntimeError('reviewed installed-root ProjectIdentity helper changed')
H = runpy.run_path(str(SOURCE), run_name='_cal_project_identity_helper')
PICK, G, P = H['PICK'], H['G'], H['P']
PROJECT = H['PROJECT']
write_new, write_raw_new = H['write_new'], H['write_raw_new']
read_native_transaction = H['read_native_transaction']
digest = H['digest']
ProjectFixture = H['ProjectFixture']
ROOT = H['ROOT']
EXPECTED_ROOT = Path('/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/api76-build-0003/installation/runtime/repository')
EXPECTED_PACKAGE = 'e4d30e95c73aa6a537f0bb922008955414aabea9d49bc472b395e2d43c350c6e'
EXPECTED_SOURCE = '9b8020f40e37940c5b331138554c9a62e9d3c854e738f4cc06447162f06d7cda'
EXPECTED_PROFILE = 'b0037a7b55b3c94d6713cd21072dcb51ec2617f51c548ae44e0861ce60646184'
EXPECTED_API = 'product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001'


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_native_config(store_parent):
    handles = []
    try:
        parent = os.open(store_parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        parent = os.open('native-store', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                         dir_fd=parent)
        handles.append(parent)
        handle = os.open('config.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=parent)
        handles.append(handle)
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 1024 * 1024:
            raise ValueError('unsafe native Store config original')
        with os.fdopen(os.dup(handle), 'rb') as stream:
            raw = stream.read(1024 * 1024 + 1)
        after = os.fstat(handle)
        attached = os.stat('config.json', dir_fd=parent, follow_symlinks=False)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns)
        if (len(raw) != before.st_size or identity(before) != identity(after) or
                identity(before) != identity(attached)):
            raise ValueError('native Store config original changed during read')
        return raw
    finally:
        for handle in reversed(handles):
            os.close(handle)


def run(output):
    PICK.require_runtime_ready()
    selected = PICK.current()
    if (PICK.root() != EXPECTED_ROOT or selected.package_pin != EXPECTED_PACKAGE or
            selected.package['entrypoint']['api_directory'] != EXPECTED_API or
            PICK.binding('api.source')['sha256'] != EXPECTED_SOURCE or
            PICK.binding('api.profile')['sha256'] != EXPECTED_PROFILE):
        raise ValueError('foreign installed API76 ProjectIdentity pilot cut')
    output = Path(output).absolute()
    if output.exists() or not output.parent.is_dir() or any(p.is_symlink() for p in output.parents):
        raise ValueError('fresh private output under a real parent required')
    output.mkdir(mode=0o700)
    fsync_directory(output.parent)
    write_new(output / 'INTENT.json',
              {'purpose': 'isolated installed native Store ProjectIdentity admission',
               'project_ref': PROJECT, 'route': 'native-Store.apply',
               'governance_API_checkpoint_or_admission_qualified': False,
               'authority_effect': 'none'})
    private = Path(tempfile.mkdtemp(prefix='cal-strattum-native-project-', dir='/tmp'))
    try:
        schemas = P.Schemas(PICK.binding('api.profile')['sha256'])
        fixture = ProjectFixture(private, schemas)
    except Exception:
        shutil.rmtree(private)
        raise
    apply_started = False
    completed = False
    try:
        proposal_raw = fixture.memory[fixture.target_package['ref']]
        approval_raw = fixture.memory[fixture.approval['ref']]
        if (digest(proposal_raw) != fixture.target_package['sha256'] or
                digest(approval_raw) != fixture.approval['sha256']):
            raise RuntimeError('independent selected native proposal/approval bytes differ')
        approval = G.parse(approval_raw)
        before = fixture.store.replay(require_current=True)
        if before['head']['sequence'] != 0:
            raise RuntimeError('fresh private native Store is not at bootstrap cut')
        apply_started = True
        result = fixture.store.apply(fixture.native, approval)
        if result['idempotent'] is not False:
            raise RuntimeError('fresh native Store unexpectedly reused an earlier admission')
        cold = G.S.Store(private / 'native-store', ROOT).replay(require_current=True)
        if cold['head']['sequence'] != 1 or len(cold['transactions']) != 2:
            raise RuntimeError('new native ProjectIdentity transaction missing from cold cut')
        subjects = [subject for subject in cold['projection']['subjects'].values()
                    if subject['identity'] == PROJECT and
                    subject['effective_state'] == 'local-admitted-current']
        if len(subjects) != 1 or subjects[0]['kind'] != 'project-identity':
            raise RuntimeError('new ProjectIdentity subject missing from cold replay')
        subject = subjects[0]
        original = G.U.original_bytes(fixture.store, subject['version_ref'],
                                      cold['transactions'][-1]['digest'])
        if G.U.parse_original(original) != subject['record']:
            raise RuntimeError('native ProjectIdentity original and replay differ')
        evidence_ref = fixture.scope_evidence['ref']
        evidence_raw = fixture.memory[evidence_ref]
        if (subject['record']['evidence_refs'] != [evidence_ref] or
                digest(evidence_raw) != fixture.scope_evidence['sha256']):
            raise RuntimeError('selected ProjectIdentity scope evidence differs')
        transaction_raw = read_native_transaction(private, cold['head']['sequence'])
        if G.parse(transaction_raw) != cold['transactions'][-1]:
            raise RuntimeError('exact native transaction original and replay differ')
        config_raw = read_native_config(private)
        config_original = G.parse(config_raw)
        if (config_original.get('digest') != cold['head']['config_digest'] or
                {key: value for key, value in config_original.items() if key != 'digest'} != cold['config'] or
                cold['transactions'][-1]['config_digest'] != cold['head']['config_digest']):
            raise RuntimeError('native Store config original and cold head differ')
        proposal_sha = write_raw_new(output / 'NATIVE-PROPOSAL.json', proposal_raw)
        approval_sha = write_raw_new(output / 'NATIVE-APPROVAL.json', approval_raw)
        original_sha = write_raw_new(output / 'PROJECT-ORIGINAL.json', original)
        evidence_sha = write_raw_new(output / 'SCOPE-EVIDENCE.json', evidence_raw)
        transaction_sha = write_raw_new(output / 'SIGNED-TRANSACTION.json', transaction_raw)
        config_sha = write_raw_new(output / 'NATIVE-STORE-CONFIG.json', config_raw)
        if not all(digest((output / name).read_bytes()) == expected for name, expected in (
                ('NATIVE-PROPOSAL.json', proposal_sha),
                ('NATIVE-APPROVAL.json', approval_sha),
                ('PROJECT-ORIGINAL.json', original_sha),
                ('SCOPE-EVIDENCE.json', evidence_sha),
                ('SIGNED-TRANSACTION.json', transaction_sha),
                ('NATIVE-STORE-CONFIG.json', config_sha))):
            raise RuntimeError('retained native ProjectIdentity originals changed on cold read')
        if (proposal_sha != fixture.target_package['sha256'] or
                approval_sha != fixture.approval['sha256'] or
                evidence_sha != fixture.scope_evidence['sha256'] or
                original_sha != digest(original)):
            raise RuntimeError('retained native ProjectIdentity binding differs')
        cold_readback_sha = write_new(output / 'COLD-READBACK.json',
                                      {'schema_version': 'lab-strattum-native-project-cold-readback/v1',
                                       'project_ref': PROJECT, 'subject': subject,
                                       'head': cold['head'],
                                       'transaction_sha256': transaction_sha,
                                       'generated_state_ref': cold['projection']['state']['node_id'],
                                       'generated_state_project_ref': cold['projection']['state']['payload']['project_ref'],
                                       'authority_effect': 'none'})
        receipt = {'schema_version': 'lab-strattum-native-project-pilot/v1',
                   'result': 'PASS-disposable-local-ProjectIdentity-artifact',
                   'project_ref': PROJECT, 'target_version_ref': subject['version_ref'],
                   'target_record_sha256': original_sha,
                   'scope_evidence_ref': evidence_ref,
                   'scope_evidence_sha256': evidence_sha,
                   'native_proposal_sha256': proposal_sha,
                   'native_approval_sha256': approval_sha,
                   'native_transaction_sha256': transaction_sha,
                   'native_store_config_sha256': config_sha,
                   'native_transaction_digest': cold['transactions'][-1]['digest'],
                   'cold_readback_sha256': cold_readback_sha,
                   'source_cut': cold['head'],
                   'api_source_sha256': PICK.binding('api.source')['sha256'],
                   'api_profile_sha256': PICK.binding('api.profile')['sha256'],
                   'pilot_driver_sha256': digest(Path(__file__).read_bytes()),
                   'pilot_helper_sha256': PILOT_HELPER_SHA,
                   'generated_state_project_ref': cold['projection']['state']['payload']['project_ref'],
                   'governance_API_checkpoint_or_admission_qualified': False,
                   'local_native_admission_observed': True,
                   'separate_project_runtime': False,
                   'independently_replayable_durable_project_runtime': False,
                   'store_disposition': 'disposable-private-tmp-store-after-cold-replay',
                   'repository_admissions_applied': 0,
                   'authority_effect': 'none'}
        receipt_sha = write_new(output / 'RESULT.json', receipt)
        if digest((output / 'RESULT.json').read_bytes()) != receipt_sha:
            raise RuntimeError('native ProjectIdentity result cold read differs')
        fsync_directory(output)
        completed = True
        return {'result': receipt['result'], 'receipt_sha256': receipt_sha,
                'project_ref': PROJECT, 'separate_project_runtime': False,
                'authority_effect': 'none'}
    finally:
        try:
            fixture.service.close()
        finally:
            if not apply_started or completed:
                shutil.rmtree(private)
            else:
                write_new(output / 'RECONCILIATION-REQUIRED.json',
                          {'schema_version': 'lab-strattum-native-project-reconciliation/v1',
                           'private_store': str(private), 'operation': 'native-Store.apply',
                           'proposal_sha256': fixture.target_package['sha256'],
                           'approval_sha256': fixture.approval['sha256'],
                           'retry_allowed': False, 'authority_effect': 'none'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.output), sort_keys=True), flush=True)
    except Exception as error:
        out = Path(args.output).absolute()
        if out.is_dir() and not (out / 'RESULT.json').exists():
            write_new(out / 'REFUSAL.json',
                      {'schema_version': 'lab-strattum-native-project-refusal/v1',
                       'project_ref': PROJECT, 'exception_type': type(error).__name__,
                       'reason': str(error), 'authority_effect': 'none'})
        print(json.dumps({'result': 'REFUSED', 'reason': str(error),
                          'authority_effect': 'none'}, sort_keys=True), flush=True)
        raise SystemExit(1)
