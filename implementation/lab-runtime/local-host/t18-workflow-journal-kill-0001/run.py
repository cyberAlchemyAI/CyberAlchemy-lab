#!/usr/bin/env python3
"""Kill the selected workflow journal at two durable boundaries and cold replay."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[4]
KERNEL = ROOT / 'product/lab/release-candidates/v1/interface/workflow-transition-v1'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001'
JOURNAL = API / 'workflow_output_journal.py'
SOURCE_MANIFEST = API / 'source-manifest.json'
SOURCE_MANIFEST_SHA = '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560'
KERNEL_SHA = 'ac9a773cf7ab6c3c9383c3697a12a7e703fb2a53c8266a46b83bd4bf2ace52d9'
FIXTURES_SHA = '68aad9f3c61f33f76041740746af7506f3031dd6309abb62657acfe8b0afad95'
PACKAGE_SHA = '8d597b36b682f5fb846459da0bc47b7a9eaa9dbcdf2c001d0c95117dd31e2c23'
REQUEST = {'ref': 'request:isolated-workflow', 'sha256': 'a' * 64}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def selected_journal_sha():
    raw = SOURCE_MANIFEST.read_bytes()
    need(sha(raw) == SOURCE_MANIFEST_SHA, 'selected API43 source manifest changed')
    selected = json.loads(raw)
    path = str(JOURNAL.relative_to(ROOT))
    rows = [row for row in selected['files'] if row['path'] == path]
    need(len(rows) == 1, 'selected API43 journal member missing or duplicated')
    expected = rows[0]['sha256']
    need(sha(JOURNAL.read_bytes()) == expected, 'selected API43 journal member changed')
    return expected


def load(expected_journal_sha):
    need(selected_journal_sha() == expected_journal_sha, 'selected journal binding differs')
    name = '_cal_t18_kernel'
    def captured(module_name, path, expected_sha, *, package=False):
        raw = path.read_bytes()
        need(sha(raw) == expected_sha, 'workflow fixture source changed: ' + path.name)
        module = types.ModuleType(module_name)
        module.__file__ = str(path)
        module.__package__ = module_name if package else module_name.rsplit('.', 1)[0]
        if package:
            module.__path__ = [str(path.parent)]
        sys.modules[module_name] = module
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        return module
    captured(name, KERNEL / '__init__.py', PACKAGE_SHA, package=True)
    kernel = captured(name + '.kernel', KERNEL / 'kernel.py', KERNEL_SHA)
    fixtures = captured(name + '.fixtures', KERNEL / 'fixtures.py', FIXTURES_SHA)
    api_name = '_cal_t18_selected_api_journal'
    api_package = types.ModuleType(api_name)
    api_package.__path__ = [str(API)]
    sys.modules[api_name] = api_package
    transition = types.ModuleType(api_name + '.workflow_transition')
    transition.K = kernel
    sys.modules[transition.__name__] = transition
    journal_raw = JOURNAL.read_bytes()
    need(sha(journal_raw) == expected_journal_sha, 'selected API journal changed')
    journal_name = api_name + '.workflow_output_journal'
    journal = types.ModuleType(journal_name)
    journal.__file__ = str(JOURNAL)
    journal.__package__ = api_name
    sys.modules[journal_name] = journal
    exec(compile(journal_raw, str(JOURNAL), 'exec'), journal.__dict__)
    return kernel, fixtures, journal


def child(case, config_sha, stage, selected_sha):
    kernel, _, journal = load(selected_sha)
    base = Path(case)
    plan = json.loads((base / 'plan.json').read_bytes())
    store = journal.Journal(base / 'journal', config_sha)
    seen = 0
    stop_at = 3 if stage == 'claim' else 4

    def guard():
        nonlocal seen
        seen += 1
        if seen == stop_at:
            marker = base / 'kill-ready'
            with marker.open('xb') as output:
                output.write(stage.encode())
                output.flush()
                os.fsync(output.fileno())
            while True:
                time.sleep(1)

    store.apply(plan, request_binding=REQUEST, host_guard=guard)
    raise RuntimeError('child reached normal completion before SIGKILL')


def one(stage, selected_sha):
    kernel, fixtures, journal = load(selected_sha)
    message, facts = fixtures.build()
    plan = kernel.plan(message, **facts)
    plan['producer_receipt_bindings'] = []
    with tempfile.TemporaryDirectory(prefix='cal-t18-workflow-kill-') as temporary:
        base = Path(temporary)
        (base / 'plan.json').write_bytes(kernel.encoded(plan))
        foreign = base / 'foreign.bin'
        foreign.write_bytes(b'unrelated retained bytes\x00')
        store = journal.Journal.initialize(base / 'journal', facts['run_raw'], facts['host_grant']['scope_ref'], message['actor']['principal_ref'])
        before = store.replay()[0]
        child_cmd = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--child', str(base), store.config_sha256, stage, selected_sha]
        process = subprocess.Popen(child_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while not (base / 'kill-ready').exists():
                if process.poll() is not None:
                    out, err = process.communicate()
                    raise AssertionError(f'child exited before kill: {process.returncode} {out!r} {err!r}')
                if time.monotonic() >= deadline:
                    raise AssertionError('child did not reach selected journal boundary')
                time.sleep(.01)
            os.killpg(process.pid, signal.SIGKILL)
            _, err = process.communicate(timeout=10)
            need(process.returncode == -signal.SIGKILL, f'child was not SIGKILLed: {err!r}')
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=10)
        need(selected_journal_sha() == selected_sha, 'selected API journal changed during kill')
        cold = journal.Journal(base / 'journal', store.config_sha256)
        need(cold.replay()[0] == before, 'HEAD advanced before recovery')
        need(foreign.read_bytes() == b'unrelated retained bytes\x00', 'foreign bytes changed')
        fingerprint = kernel.digest({'request_binding': REQUEST, 'plan': plan})
        claim_path = cold.root / 'claims' / (cold.namespace(message['idempotency_key']) + '.json')
        need(claim_path.is_file(), 'durable claim missing')
        tx_path = cold.root / 'transactions/00000001.json'
        def inventory(folder):
            entries = list(folder.iterdir())
            need(all(p.is_file() and not p.is_symlink() for p in entries), 'non-file journal residue appeared')
            return {p.name: sha(p.read_bytes()) for p in entries}
        claims_before = inventory(cold.root / 'claims')
        tx_before = inventory(cold.root / 'transactions')
        need(set(claims_before) == {claim_path.name}, 'duplicate or foreign claim appeared')
        need(set(tx_before) == (set() if stage == 'claim' else {tx_path.name}),
             'duplicate or foreign transaction appeared')
        if stage == 'claim':
            need(not tx_path.exists(), 'transaction unexpectedly exists after claim kill')
            try:
                cold.apply(plan, request_binding=REQUEST, host_guard=lambda: None)
            except journal.Indeterminate:
                pass
            else:
                raise AssertionError('pending claim was redispatched')
            try:
                cold.recover(message['idempotency_key'], fingerprint, host_guard=lambda: None)
            except ValueError as error:
                need(str(error) == 'no observed immutable workflow effect; pending claim cannot be retried',
                     'claim-only recovery refused for wrong reason')
            else:
                raise AssertionError('unobserved transaction was recovered')
            need(cold.replay()[0] == before, 'claim-only kill advanced HEAD')
        else:
            need(tx_path.is_file(), 'transaction missing after transaction kill')
            tx = cold.recover(message['idempotency_key'], fingerprint, host_guard=lambda: None)
            need(cold.replay()[0]['sequence'] == 1, 'transaction recovery did not publish HEAD')
            first = tx_path.read_bytes()
            need(cold.apply(plan, request_binding=REQUEST, host_guard=lambda: None) == tx, 'exact retry changed result')
            need(tx_path.read_bytes() == first, 'exact retry changed transaction bytes')
            need(foreign.read_bytes() == b'unrelated retained bytes\x00', 'foreign bytes changed after recovery')
        try:
            cold.apply(plan, request_binding={'ref': 'request:foreign', 'sha256': 'b' * 64}, host_guard=lambda: None)
        except ValueError as error:
            need(str(error) == 'workflow idempotency key conflicts with different exact inputs',
                 'changed-request retry refused for wrong reason')
        else:
            raise AssertionError('same idempotency key accepted a changed request')
        need(inventory(cold.root / 'claims') == claims_before, 'retry changed claims')
        need(inventory(cold.root / 'transactions') == tx_before, 'retry changed transactions')
        need(foreign.read_bytes() == b'unrelated retained bytes\x00', 'foreign bytes changed after changed-request refusal')
        return {'stage': stage, 'child_exit': process.returncode, 'claim_sha256': sha(claim_path.read_bytes()),
                'transaction_sha256': sha(tx_path.read_bytes()) if tx_path.exists() else None,
                'cold_sequence_before_recovery': before['sequence'],
                'cold_sequence_after_recovery': cold.replay()[0]['sequence'],
                'foreign_preserved': True, 'duplicate_effects': False}


def main():
    if len(sys.argv) == 6 and sys.argv[1] == '--child':
        child(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        return
    need(len(sys.argv) == 1, 'unexpected CLI arguments')
    selected_sha = selected_journal_sha()
    result = {'result': 'PASS', 'scope': 'selected API43 workflow journal component only',
              'api_source_manifest_binding': {'path': str(SOURCE_MANIFEST.relative_to(ROOT)), 'sha256': SOURCE_MANIFEST_SHA},
              'api_journal_binding': {'path': str(JOURNAL.relative_to(ROOT)), 'sha256': selected_sha},
              'kernel_fixture_bindings': [{'path': str((KERNEL / filename).relative_to(ROOT)), 'sha256': digest}
                                          for filename, digest in [('__init__.py', PACKAGE_SHA), ('kernel.py', KERNEL_SHA), ('fixtures.py', FIXTURES_SHA)]],
              'runner_sha256': sha(Path(__file__).read_bytes()),
              'cases': [one('claim', selected_sha), one('transaction', selected_sha)], 'authority_effect': 'none',
              'limits': ['No authenticated Service or Vault claim/finish path', 'No host power-loss simulation',
                         'No original producer execution in this component probe']}
    output = Path(__file__).with_name('RESULT.json')
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': result['result'], 'cases': len(result['cases'])}))


if __name__ == '__main__':
    main()
