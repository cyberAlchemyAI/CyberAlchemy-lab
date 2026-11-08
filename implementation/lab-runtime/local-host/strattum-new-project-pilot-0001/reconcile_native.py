"""Read-only reconciliation of the one committed disposable native ProjectIdentity cut."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import stat


DRIVER = Path(__file__).with_name('pilot_native.py')
DRIVER_SHA = 'ace7e88ed24ebcdebc9f8df987cb28eb288b4a46389d6ecd948148edfeba4d8b'
if hashlib.sha256(DRIVER.read_bytes()).hexdigest() != DRIVER_SHA:
    raise RuntimeError('reviewed native pilot driver changed')
N = runpy.run_path(str(DRIVER), run_name='_cal_native_project_recovery_dependency')
PICK, G, ROOT, PROJECT = N['PICK'], N['G'], N['ROOT'], N['PROJECT']
write_new, write_raw_new = N['write_new'], N['write_raw_new']
fsync_directory = N['fsync_directory']
EXPECTED_RECONCILIATION = 'bd2256ba8ca333ee5f48bce2597f9134e554a677ed572df5b754b242a2d36598'
EXPECTED_REFUSAL = '32a9287381153ed966030d4166c115b4370a64e37dce3608f9466e938588d61d'
EXPECTED_PRIVATE = Path('/tmp/cal-strattum-native-project-xsz98akg')
EXPECTED_TX_SHA = '55d99805b60d85fb0b2cfe8f0d13d6897870a29f32a0369ebf2f411de7541ffa'
EXPECTED_TX_DIGEST = 'fde5728576277d8a0c5f3080a8008404bf7ff1476309e4daf67f1adf539680a6'
SOURCE_RESULT = Path('/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/native-run-0001')
EXPECTED_OUTPUT = SOURCE_RESULT.parent / 'native-recovery-0001'
EXPECTED_VERSION = PROJECT + '@1.0.0-candidate.1'
EXPECTED_CARRIER = 'cal.artifact-type.project-identity/v1'
STORE_FILES = {'.writer.lock': 1, 'config.json': 1024 * 1024,
               'baseline.json': 16 * 1024 * 1024, 'HEAD.json': 1024 * 1024,
               'transactions/0000000000.json': 1024 * 1024,
               'transactions/0000000001.json': 16 * 1024 * 1024}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_json(raw):
    if type(raw) is not bytes or len(raw) > 16 * 1024 * 1024:
        raise ValueError('recovery JSON exceeds exact native file bound')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate recovery JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError('nonfinite recovery JSON constant')))


def read_owned(root, relative, limit):
    handles = []
    try:
        parent = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        parts = Path(relative).parts
        if not parts or any(part in ('', '.', '..') for part in parts):
            raise ValueError('unsafe recovery relative path')
        for part in parts[:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                             dir_fd=parent)
            handles.append(parent)
        handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=parent)
        handles.append(handle)
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError('unsafe recovery original')
        with os.fdopen(os.dup(handle), 'rb') as stream:
            raw = stream.read(limit + 1)
        after = os.fstat(handle)
        attached = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns)
        if (len(raw) != before.st_size or identity(before) != identity(after) or
                identity(before) != identity(attached)):
            raise ValueError('recovery original changed during read')
        return raw
    finally:
        for handle in reversed(handles):
            os.close(handle)


def run(output):
    PICK.require_runtime_ready()
    selected = PICK.current()
    if (PICK.root() != N['EXPECTED_ROOT'] or selected.package_pin != N['EXPECTED_PACKAGE'] or
            selected.package['entrypoint']['api_directory'] != N['EXPECTED_API'] or
            PICK.binding('api.source')['sha256'] != N['EXPECTED_SOURCE'] or
            PICK.binding('api.profile')['sha256'] != N['EXPECTED_PROFILE']):
        raise ValueError('foreign installed API76 ProjectIdentity recovery cut')
    reconciliation_raw = read_owned(SOURCE_RESULT, 'RECONCILIATION-REQUIRED.json', 1024 * 1024)
    refusal_raw = read_owned(SOURCE_RESULT, 'REFUSAL.json', 1024 * 1024)
    if sha(reconciliation_raw) != EXPECTED_RECONCILIATION or sha(refusal_raw) != EXPECTED_REFUSAL:
        raise ValueError('prior native refusal/reconciliation bytes differ')
    reconciliation, refusal = bounded_json(reconciliation_raw), bounded_json(refusal_raw)
    if (Path(reconciliation['private_store']) != EXPECTED_PRIVATE or
            reconciliation['operation'] != 'native-Store.apply' or
            reconciliation['retry_allowed'] is not False or
            refusal['reason'] != 'input budget'):
        raise ValueError('prior native refusal/reconciliation meaning differs')
    source_store = EXPECTED_PRIVATE / 'native-store'
    if not EXPECTED_PRIVATE.is_dir() or EXPECTED_PRIVATE.is_symlink():
        raise ValueError('retained private native Store is absent or linked')
    actual_store_entries = {path.relative_to(source_store).as_posix()
                            for path in source_store.rglob('*')}
    if (actual_store_entries != set(STORE_FILES) | {'transactions'} or
            not (source_store / 'transactions').is_dir() or
            (source_store / 'transactions').is_symlink()):
        raise ValueError('retained native Store contains an unreviewed or pending file')
    file_raw = {relative: read_owned(source_store, relative, limit)
                for relative, limit in STORE_FILES.items()}
    tx_raw = file_raw['transactions/0000000001.json']
    tx = bounded_json(tx_raw)
    if (sha(tx_raw) != EXPECTED_TX_SHA or tx.get('digest') != EXPECTED_TX_DIGEST or
            tx.get('sequence') != 1 or tx.get('kind') != 'admission'):
        raise ValueError('committed native transaction identity differs')
    proposal_raw = read_owned(EXPECTED_PRIVATE, 'materials/' + reconciliation['proposal_sha256'], 1024 * 1024)
    approval_raw = read_owned(EXPECTED_PRIVATE, 'materials/' + reconciliation['approval_sha256'], 1024 * 1024)
    if (sha(proposal_raw) != reconciliation['proposal_sha256'] or
            sha(approval_raw) != reconciliation['approval_sha256'] or
            bounded_json(proposal_raw) != tx['proposal'] or
            bounded_json(approval_raw) != tx['approval']):
        raise ValueError('retained proposal/approval and signed transaction differ')
    source_cold = G.S.Store(source_store, ROOT).replay(require_current=True)
    if (source_cold['head']['sequence'] != 1 or
            source_cold['head']['transaction_digest'] != EXPECTED_TX_DIGEST or
            source_cold['transactions'][-1] != tx):
        raise ValueError('native Store cold replay differs from signed transaction')
    subjects = [item for item in source_cold['projection']['subjects'].values()
                if item['identity'] == PROJECT and item['effective_state'] == 'local-admitted-current']
    if len(subjects) != 1 or subjects[0]['kind'] != 'project-identity':
        raise ValueError('ProjectIdentity subject not current in retained native Store')
    subject = subjects[0]
    contract = source_cold['projection']['contracts'].get(EXPECTED_CARRIER)
    targets = tx['proposal']['targets']
    if (subject['version_ref'] != EXPECTED_VERSION or
            len(targets) != 1 or targets[0]['version_ref'] != EXPECTED_VERSION or
            targets[0]['carrier_ref'] != EXPECTED_CARRIER or
            contract is None or contract['lifecycle_state'] != 'admitted-current' or
            contract['artifact']['instance_contract']['identity_field'] != 'project_id'):
        raise ValueError('current ProjectIdentity carrier or exact target differs')
    original = G.U.original_bytes(G.S.Store(source_store, ROOT), subject['version_ref'], EXPECTED_TX_DIGEST)
    if G.U.parse_original(original) != targets[0]['record']:
        raise ValueError('project original differs from current native subject')
    evidence_refs = targets[0]['record']['evidence_refs']
    if len(evidence_refs) != 1 or evidence_refs[0] != 'evidence:pilot-project-scope':
        raise ValueError('project scope evidence reference differs')
    evidence_candidates = []
    for item in (EXPECTED_PRIVATE / 'materials').iterdir():
        if not item.name.isalnum() or len(item.name) != 64:
            continue
        raw = read_owned(EXPECTED_PRIVATE, 'materials/' + item.name, 1024 * 1024)
        if sha(raw) != item.name:
            raise ValueError('retained material filename/digest differs')
        try:
            body = bounded_json(raw)
        except (ValueError, json.JSONDecodeError):
            continue
        if (type(body) is dict and body.get('project_id') == PROJECT and
                body.get('intended_use') == 'Local Lab feature gap pilot only'):
            evidence_candidates.append((item.name, raw))
    if len(evidence_candidates) != 1:
        raise ValueError('unique retained Project scope evidence missing')
    evidence_sha, evidence_raw = evidence_candidates[0]
    config_original = bounded_json(file_raw['config.json'])
    if (config_original.get('digest') != source_cold['head']['config_digest'] or
            {key: value for key, value in config_original.items() if key != 'digest'} != source_cold['config']):
        raise ValueError('retained public Store config and native head differ')
    output = Path(output).absolute()
    if (output != EXPECTED_OUTPUT or output.exists() or not output.parent.is_dir() or
            any(p.is_symlink() for p in output.parents)):
        raise ValueError('fresh recovery output must use exact owner-private Lab root')
    output.mkdir(mode=0o700)
    fsync_directory(output.parent)
    copied = output / 'NATIVE-STORE'
    copied.mkdir(mode=0o700)
    (copied / 'transactions').mkdir(mode=0o700)
    inventory = {}
    for relative, raw in file_raw.items():
        inventory[relative] = write_raw_new(copied / relative, raw)
    fsync_directory(copied / 'transactions')
    fsync_directory(copied)
    copy_cold = G.S.Store(copied, ROOT).replay(require_current=True)
    if (copy_cold['head'] != source_cold['head'] or
            copy_cold['projection'] != source_cold['projection'] or
            copy_cold['transactions'] != source_cold['transactions']):
        raise ValueError('retained native Store copy differs on cold replay')
    for relative, expected in inventory.items():
        if sha(read_owned(copied, relative, STORE_FILES[relative])) != expected:
            raise ValueError('retained native Store copy byte differs')
    retained = {'PRIOR-REFUSAL.json': refusal_raw,
                'PRIOR-RECONCILIATION.json': reconciliation_raw,
                'NATIVE-PROPOSAL.json': proposal_raw,
                'NATIVE-APPROVAL.json': approval_raw,
                'PROJECT-ORIGINAL.json': original,
                'SCOPE-EVIDENCE.json': evidence_raw,
                'SIGNED-TRANSACTION.json': tx_raw,
                'NATIVE-STORE-CONFIG.json': file_raw['config.json']}
    retained_sha = {name: write_raw_new(output / name, raw) for name, raw in retained.items()}
    if any(sha(read_owned(output, name, 16 * 1024 * 1024)) != expected
           for name, expected in retained_sha.items()):
        raise ValueError('recovered original byte changed')
    receipt = {'schema_version': 'lab-strattum-native-project-recovery/v1',
               'result': 'PASS-reconciled-local-ProjectIdentity-admission',
               'prior_run_result': 'REFUSED-postcommit-receipt-input-budget',
               'project_ref': PROJECT, 'target_version_ref': subject['version_ref'],
               'target_record_sha256': sha(original),
               'signed_transaction_sha256': EXPECTED_TX_SHA,
               'signed_transaction_digest': EXPECTED_TX_DIGEST,
               'scope_evidence_ref': evidence_refs[0], 'scope_evidence_sha256': evidence_sha,
               'retained_originals': retained_sha, 'store_files': inventory,
               'store_head': copy_cold['head'],
               'generated_state_project_ref': copy_cold['projection']['state']['payload']['project_ref'],
               'governance_API_checkpoint_or_admission_qualified': False,
               'local_native_admission_observed': True,
               'separate_project_runtime': False,
               'independently_replayable_durable_project_runtime': False,
               'retained_private_store_copy': 'NATIVE-STORE',
               'source_private_store_preserved': str(EXPECTED_PRIVATE),
               'repository_admissions_applied': 0, 'authority_effect': 'none'}
    receipt_sha = write_new(output / 'RECOVERY-RESULT.json', receipt)
    fsync_directory(output)
    if sha(read_owned(output, 'RECOVERY-RESULT.json', 1024 * 1024)) != receipt_sha:
        raise ValueError('recovery receipt cold read differs')
    return {'result': receipt['result'], 'receipt_sha256': receipt_sha,
            'project_ref': PROJECT, 'source_store_preserved': True,
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), sort_keys=True), flush=True)
