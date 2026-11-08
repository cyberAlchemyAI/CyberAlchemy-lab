"""Owned disposable seven-family publisher rehearsal over the selected T14 component."""

from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import source_guard as G
import recovery as R


ROOT = G.ROOT
HERE = Path(__file__).resolve().parent
COMPONENT = ROOT / G.COMPONENT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def component():
    G.verify()
    name = '_cal_t14_heterogeneous_owned_0001'
    spec = importlib.util.spec_from_file_location(
        name, COMPONENT / '__init__.py', submodule_search_locations=[str(COMPONENT)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    T = __import__(name + '.typed_targets', fromlist=['adapt'])
    P = __import__(name + '.publisher', fromlist=['OwnedBytePublisher'])
    return T, P


def prepared_bundle(T, bundle_id):
    raw = G.capture(G.SELECTION, G.SELECTION_SHA256)
    selection = T.parse(raw)
    items = []
    for row in selection['rows']:
        fixture, schema, carrier = (row[key] for key in
                                    ('public_original_fixture', 'schema', 'carrier_binding'))
        body = G.capture(fixture['path'], fixture['sha256'])
        schemas = T.OriginalSchemas(
            [schema], {schema['path']: G.capture(schema['path'], schema['sha256'])},
            carrier_bindings=[carrier],
            raw_carriers={carrier['path']: G.capture(carrier['path'], carrier['sha256'])})
        spec = {key: row[key] for key in
                ('family', 'category', 'carrier_ref', 'schema_selector', 'identity_selector', 'identity_ref')}
        spec.update(schema_path=schema['path'], raw_sha256=T.sha(body))
        adapted = T.adapt(body, spec, schemas)
        if adapted['original_bytes'] != body or adapted['metadata']['canonical_admission'] is not False:
            raise ValueError('original public target adaptation differs')
        items.append({'output_path': 'targets/' + row['family'] + '.json', 'adapted': adapted})
    prepared = T.prepare_byte_bundle(items, bundle_id, schema_binding_sha256=T.sha(raw))
    T.verify_byte_bundle(prepared['files'], prepared['pins'])
    return prepared, [row['family'] for row in selection['rows']]


def root(stack):
    path = Path(stack.enter_context(tempfile.TemporaryDirectory(
        prefix='cal-T14-publisher-', dir='/tmp')))
    path.chmod(0o700)
    fd = os.open(path / 'publisher.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    if stat.S_IMODE(path.lstat().st_mode) != 0o700:
        raise ValueError('disposable owned root mode differs')
    return path


def publisher(P, path, cls=None):
    G.verify()
    guard_path = HERE / 'source_guard.py'
    return (cls or P.OwnedBytePublisher)(
        path, P.ident(path.stat()), G.verify,
        {'path': str(guard_path), 'sha256': sha(guard_path.read_bytes())},
        purpose='owned-technical-rehearsal')


def closed_use(P, path, callback, cls=None):
    value = publisher(P, path, cls)
    try:
        return callback(value)
    finally:
        value.close()
        if not value.closed or value.fds:
            raise ValueError('publisher descriptors not closed')


def stage_name(prepared):
    manifest = json.loads(prepared['files']['bundle.json'])
    return '.' + manifest['bundle_id'] + '-stage-' + prepared['pins']['bundle_sha256']


def run():
    T, P = component()
    prepared, families = prepared_bundle(T, 'technical-seven-families')
    pins, paths = prepared['pins'], tuple(prepared['files'])
    guard_entry = G.verify()
    with ExitStack() as stack:
        # Positive, exact replay, and independently reconstructed cold reader.
        positive_root = root(stack)
        positive = closed_use(P, positive_root, lambda value: value.publish(prepared, pins))
        if positive['state'] != 'committed-technical-bytes':
            raise ValueError('owned seven-family publish did not commit')
        cold = closed_use(P, positive_root, lambda value: value.inspect_committed(
            'technical-seven-families', pins, paths))
        replay = closed_use(P, positive_root, lambda value: value.publish(prepared, pins))
        if replay['state'] != 'already-committed-technical-bytes' or cold['technical_byte_closure_verified'] is not True:
            raise ValueError('cold complete-body inspection or exact replay differs')

        # Wrong selected bytes refuse before staging, leaving only our lock.
        rollback_root = root(stack)
        changed = {'files': dict(prepared['files']), 'pins': pins}
        changed['files']['targets/artifact-instance.json'] += b'\n'
        try:
            closed_use(P, rollback_root, lambda value: value.publish(changed, pins))
        except T.Refusal:
            pass
        else:
            raise ValueError('changed precommit target bytes were accepted')
        if {p.name for p in rollback_root.iterdir()} != {'publisher.lock'}:
            raise ValueError('precommit refusal left an unexpected owned write')

        # Fault after the first exact file has been fsynced but before any
        # commit syscall. The original publisher correctly preserves residue;
        # this local adapter removes only its exact owned selected subset.
        fault_root = root(stack)
        class FaultAfterFirstWrite(P.OwnedBytePublisher):
            def write(self, base, path, raw):
                super().write(base, path, raw)
                raise RuntimeError('technical precommit fault injection')
        fault = closed_use(P, fault_root, lambda value: value.publish(prepared, pins),
                           FaultAfterFirstWrite)
        if fault['state'] != 'uncommitted-residue-inspection-required':
            raise ValueError('precommit fault did not yield exact uncommitted state')
        rollback_observed = R.rollback(fault_root, stage_name(prepared), prepared['files'])
        if {p.name for p in fault_root.iterdir()} != {'publisher.lock'}:
            raise ValueError('precommit exact stage rollback left residue')

        # A foreign stage file is preserved and blocks a commit; no cleanup of
        # unknown residue is performed by the publisher.
        residue_root = root(stack)
        stage = residue_root / stage_name(prepared)
        stage.mkdir(mode=0o700)
        marker = stage / 'foreign.json'
        marker.write_bytes(b'foreign-owned-residue')
        marker.chmod(0o600)
        marker_sha = sha(marker.read_bytes())
        residue = closed_use(P, residue_root, lambda value: value.publish(prepared, pins))
        if (residue['state'] != 'uncommitted-residue-inspection-required'
                or not marker.is_file() or sha(marker.read_bytes()) != marker_sha
                or (residue_root / 'technical-seven-families.commit.json').exists()):
            raise ValueError('foreign stage residue was not preserved/refused')

        # A competing receipt is never replaced, even with a correct plan.
        compete_root = root(stack)
        competing = compete_root / 'technical-seven-families.commit.json'
        competing.write_bytes(b'foreign-competing-receipt')
        competing.chmod(0o600)
        competing_sha = sha(competing.read_bytes())
        competing_result = closed_use(P, compete_root, lambda value: value.publish(prepared, pins))
        if (competing_result['state'] != 'uncommitted-residue-inspection-required'
                or sha(competing.read_bytes()) != competing_sha):
            raise ValueError('competing no-replace receipt was overwritten')

        # Inject a competitor at the exact final-record syscall boundary,
        # after our complete staging has passed its precommit checks. The
        # selected original _commit_record still executes its linkat call.
        race_root = root(stack)
        race_bytes = b'foreign-race-commit-record'
        class CompetingAtCommit(P.OwnedBytePublisher):
            def _commit_record(self, raw, name):
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=self.fd)
                try:
                    os.write(fd, race_bytes)
                    os.fsync(fd)
                finally:
                    os.close(fd)
                os.fsync(self.fd)
                return super()._commit_record(raw, name)
        race = closed_use(P, race_root, lambda value: value.publish(prepared, pins),
                          CompetingAtCommit)
        race_receipt = race_root / 'technical-seven-families.commit.json'
        if (race['state'] != 'uncertain-commit-inspection-required'
                or not race_receipt.is_file() or race_receipt.read_bytes() != race_bytes):
            raise ValueError('descriptor-bound no-replace competition was not preserved')
        try:
            closed_use(P, race_root, lambda value: value.inspect_committed(
                'technical-seven-families', pins, paths))
        except T.Refusal:
            pass
        else:
            raise ValueError('foreign committed receipt passed cold inspection')

        # Child exits after the atomic commit but before returning a response.
        # Parent reconstructs from exact receipt/body and replays idempotently.
        crash_root = root(stack)
        pid = os.fork()
        if pid == 0:
            try:
                result = closed_use(P, crash_root, lambda value: value.publish(prepared, pins))
                os._exit(91 if result['state'] == 'committed-technical-bytes' else 92)
            except BaseException:
                os._exit(93)
        _, status = os.waitpid(pid, 0)
        if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 91:
            raise ValueError('crash child did not reach committed technical state')
        recovered = closed_use(P, crash_root, lambda value: value.inspect_committed(
            'technical-seven-families', pins, paths))
        recovered_replay = closed_use(P, crash_root, lambda value: value.publish(prepared, pins))
        if recovered['technical_byte_closure_verified'] is not True or recovered_replay['state'] != 'already-committed-technical-bytes':
            raise ValueError('postcommit lost-response recovery differs')
        guard_exit = G.verify()
        if guard_entry != guard_exit:
            raise ValueError('selected source guard changed across rehearsal')
        return {
            'schema_version': 'lab-T14-local-heterogeneous-publisher-rehearsal/v1-candidate',
            'result': 'PASS-owned-technical-seven-family-byte-publisher',
            'families': families, 'bundle_manifest_sha256': pins['bundle_sha256'],
            'whole_receipt_sha256': pins['whole_receipt_sha256'],
            'source_guard_binding': {'path': str(HERE / 'source_guard.py'),
                                     'sha256': sha((HERE / 'source_guard.py').read_bytes())},
            'source_guard_entry_exit': guard_entry,
            'positive_publish_state': positive['state'],
            'cold_complete_body_verified': cold['technical_byte_closure_verified'],
            'exact_replay_state': replay['state'],
            'precommit_changed_byte_rollback': 'refused-without-stage-or-commit',
            'postwrite_precommit_fault_state': fault['state'],
            'postwrite_precommit_exact_rollback': rollback_observed,
            'foreign_stage_residue': residue['state'],
            'foreign_stage_marker_sha256': marker_sha,
            'preexisting_competing_receipt': competing_result['state'],
            'competing_receipt_sha256': competing_sha,
            'at_commit_competitor_state': race['state'],
            'at_commit_competitor_sha256': sha(race_bytes),
            'at_commit_cold_inspection': 'refused-foreign-receipt',
            'postcommit_child_exit_code': 91,
            'cold_crash_recovery_verified': recovered['technical_byte_closure_verified'],
            'postcrash_exact_replay_state': recovered_replay['state'],
            'disposable_roots_cleaned_after_observation': True,
            'native_decision_cores_materialized': False,
            'semantic_governance_events_generated': False,
            'actual_owner_outcome': None,
            'canonical_admission': False,
            'authority_effect': 'none',
            'T14_complete': False,
        }


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
