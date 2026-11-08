"""Disposable technical T12 branch; retained public signed bytes only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / 'implementation/lab-runtime/local-host/t10-o03-current-engine-successor-0002'
WORK = ROOT / 'implementation/lab-work/candidates/v1/packages/0002/work.json'
WORK_SHA = '071df02a9434ea7a06d1fcc216b2c9c81cfe94e3c0764ba6b4d82a59292ea5e4'
CURRENT = PREDECESSOR / 'run-current-0002/RESULT.json'
CURRENT_SHA = 'c4da8c121facbbc859c000d3ae0f165681ee5777e2d38e95b49d97c9e8fa48f2'
SECURE = ROOT / 'implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004'
SECURE_SHA = '13f889f60430ebf53818bd9e4648e184dcbb23a2f3456ed01f0af014efa21676'
SECURE_RESULT_SHA = '827bbc856d2aac3b0db3ae448d072ec2820e08e045060a231fc0b6a18fb09278'
STORE_ID = 'O05-current-fixture-0001'
WORK_ID = 'work:lab-development:o05-current-source-fixture-0001'
PROPOSAL_ID = 'o05-current-source-fixture-0001'
PUBLIC = ('config.json', 'baseline.json', 'HEAD.json',
          'transactions/0000000000.json', 'transactions/0000000001.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def query():
    secure_path = SECURE / 'secure_query.py'
    if any(p.is_symlink() for p in (secure_path, *secure_path.parents)):
        raise ValueError('linked secure query loader path')
    secure_code = secure_path.read_bytes()
    if sha(secure_code) != SECURE_SHA:
        raise ValueError('secure query loader changed')
    secure_query = types.ModuleType('_selected_secure_query')
    secure_query.__file__ = str(secure_path)
    exec(compile(secure_code, str(secure_path), 'exec', dont_inherit=True), secure_query.__dict__)
    if sha(CURRENT.read_bytes()) != CURRENT_SHA:
        raise ValueError('selected current T12 query receipt changed')
    secure_raw = (SECURE / 'CURRENT-SECURE-RESULT.json').read_bytes()
    if sha(secure_raw) != SECURE_RESULT_SHA:
        raise ValueError('executed byte-backed query result changed')
    with secure_query.selected_modules() as (runner, modules):
        prior = runner.verify_result(CURRENT.parent)
        secure = json.loads(secure_raw)
        if (secure['scope'] != 'current-specialist-owner' or
                secure['answer_digests'] != {name: row['response_digest'] for name, row in prior['queries'].items()} or
                secure['query_control_sha256'] != secure_query.CONTROL_SHA or
                secure['loader_sha256'] != secure_query.LOADER_SHA or
                secure['probe_sha256'] != secure_query.PROBE_SHA or
                secure['query_run_sha256'] != secure_query.QUERY_SHA or
                secure['authority_effect'] != 'none' or secure['selected_governed_models'] != 0):
            raise ValueError('byte-backed execution does not match selected T12 answer')
        return modules['scope']


def proposal(template, data, output):
    config, baseline, head = (data[k] for k in ('config', 'baseline', 'head'))
    record = copy.deepcopy(template)
    record.update(node_id=WORK_ID, name='Inspect O05 current source translation on a technical branch',
                  owner_ref=config['owner_ref'], scope_ref=config['scope_ref'],
                  lifecycle_state='candidate', authority_effect='none',
                  challenge_route=config['challenge_route'],
                  claim_ceiling='Local fixture signing only; no repository authority or original O05 admission.',
                  evidence_refs=[CURRENT.relative_to(ROOT).as_posix() + '#sha256=' + CURRENT_SHA])
    record['payload'].update(completion_state='candidate-in-progress',
        work_statement='Exercise a fresh signed current T12 source branch for O05 translation diagnostics.',
        input_refs=[CURRENT.relative_to(ROOT).as_posix()],
        output_refs=[(output / 'RESULT.json').relative_to(ROOT).as_posix()])
    return {'schema_version': 'lab-runtime-proposal/v1', 'proposal_id': PROPOSAL_ID,
            'scope_ref': config['scope_ref'], 'policy_ref': config['policy_ref'],
            'challenge_route': config['challenge_route'],
            'source_snapshot_digest': baseline['snapshot_digest'],
            'expected_head': head['transaction_digest'], 'schemas': {},
            'targets': [{'category': 'artifact-instance', 'operation': 'admit',
                         'carrier_ref': 'cal.artifact-type.work/v1',
                         'version_ref': WORK_ID + '@candidate.1',
                         'predecessor_ref': None,
                         'decision_ref': 'decision:candidate-local:' + PROPOSAL_ID,
                         'contract': None, 'record': record}]}


def safe_public(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError('unsafe signed branch directory')
    entries = {p.relative_to(root).as_posix() for p in root.rglob('*')}
    if entries - set(PUBLIC) - {'transactions', '.writer.lock'}:
        raise ValueError('signed branch has an unselected entry')
    paths = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if not set(PUBLIC) <= paths or paths - set(PUBLIC) - {'.writer.lock'}:
        raise ValueError('signed branch public file closure differs')
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('linked signed branch entry')
    return {name: (root / name).read_bytes() for name in PUBLIC}


def construct(output):
    output = Path(output).absolute()
    if output.exists() or not output.parent.resolve().is_relative_to(HERE):
        raise ValueError('new task-local output directory required')
    scope = query()
    template_raw = WORK.read_bytes()
    if sha(template_raw) != WORK_SHA:
        raise ValueError('historical Work template changed')
    template = json.loads(template_raw)
    with tempfile.TemporaryDirectory(prefix='cal-O05-current-branch-') as temporary:
        with scope.loader.engine(scope.PINS) as handle:
            store, private_key = handle.create_owned(Path(temporary), STORE_ID)
            initial = store.replay(require_current=True)
            p = proposal(template, initial, output)
            review = store.review(p)
            if review['target_count'] != 1 or review['authority_effect'] != 'none':
                raise ValueError('fixture review differs')
            approval = store.authorize(p, private_key)
            applied = store.apply(p, approval)
            current = store.replay(require_current=True)
            if (current['head']['sequence'] != 1 or
                    current['transactions'][1]['proposal'] != p or
                    current['transactions'][1]['approval'] != approval or
                    current['freshness']['status'] != 'current'):
                raise ValueError('signed fixture replay differs')
            public = safe_public(store.path)
            output.mkdir(mode=0o700)
            branch = output / 'branch'
            branch.mkdir(mode=0o700)
            for name, raw in public.items():
                target = branch / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            result = {'schema_version': 'lab-T10-O05-current-signed-technical-branch/v2',
                      'status': 'PASS-LOCAL-SIGNED-BRANCH',
                      'engine_manifest_sha256': scope.PINS.manifest_sha256,
                      'current_t12_query_sha256': CURRENT_SHA,
                      'byte_backed_query_loader_sha256': SECURE_SHA,
                      'byte_backed_query_execution_sha256': SECURE_RESULT_SHA,
                      'historical_work_template_sha256': WORK_SHA,
                      'public_files': [{'path': name, 'sha256': sha(raw)} for name, raw in sorted(public.items())],
                      'store_id': STORE_ID, 'work_id': WORK_ID,
                      'baseline_snapshot_digest': current['baseline']['snapshot_digest'],
                      'head_sequence': 1, 'head_transaction_digest': current['head']['transaction_digest'],
                      'proposal_digest': handle.common.digest(p),
                      'approved_by': 'ephemeral local technical signer',
                      'private_key_retained': False, 'authority_effect': 'none',
                      'original_o05_event_package_retranslated': False,
                      'selected_governed_models': 0}
            (output / 'RESULT.json').write_bytes(encoded(result))
            return result


def replay(output):
    output = Path(output).absolute()
    if not output.resolve().is_relative_to(HERE) or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('unsafe retained output path')
    if ({p.name for p in output.iterdir()} != {'RESULT.json', 'branch'} or
            (output / 'RESULT.json').is_symlink()):
        raise ValueError('retained branch output closure differs')
    result = json.loads((output / 'RESULT.json').read_bytes())
    if (result['schema_version'] != 'lab-T10-O05-current-signed-technical-branch/v2' or
            result['status'] != 'PASS-LOCAL-SIGNED-BRANCH' or
            result['current_t12_query_sha256'] != CURRENT_SHA or
            result['byte_backed_query_loader_sha256'] != SECURE_SHA or
            result['byte_backed_query_execution_sha256'] != SECURE_RESULT_SHA or
            result['historical_work_template_sha256'] != WORK_SHA or
            result['store_id'] != STORE_ID or result['work_id'] != WORK_ID or
            result['head_sequence'] != 1 or result['private_key_retained'] is not False or
            result['authority_effect'] != 'none' or result['original_o05_event_package_retranslated'] is not False or
            result['selected_governed_models'] != 0 or result['approved_by'] != 'ephemeral local technical signer'):
        raise ValueError('retained branch receipt differs')
    if [row['path'] for row in result['public_files']] != sorted(PUBLIC):
        raise ValueError('retained branch file set differs')
    branch = output / 'branch'
    public = safe_public(branch)
    for row in result['public_files']:
        if sha(public[row['path']]) != row['sha256']:
            raise ValueError('retained branch bytes changed')
    scope = query()
    if result['engine_manifest_sha256'] != scope.PINS.manifest_sha256:
        raise ValueError('selected engine differs')
    with tempfile.TemporaryDirectory(prefix='cal-O05-cold-replay-') as temporary:
        dest = Path(temporary) / 'store'
        dest.mkdir(mode=0o700)
        for name, raw in public.items():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as f:
                f.write(raw)
        with scope.loader.engine(scope.PINS) as handle:
            handle.guard()
            data = handle.store_module.Store(dest, ROOT).replay(require_current=True)
            tx = data['transactions'][1]
            if (data['baseline']['snapshot_digest'] != result['baseline_snapshot_digest'] or
                    data['head']['transaction_digest'] != result['head_transaction_digest'] or
                    data['head']['sequence'] != 1 or tx['proposal']['proposal_id'] != PROPOSAL_ID or
                    tx['proposal']['targets'][0]['record']['node_id'] != WORK_ID or
                    handle.common.digest(tx['proposal']) != result['proposal_digest'] or
                    tx['consequences']['receipt']['repository_admission_effect'] != 'none' or
                    tx['consequences']['receipt']['runtime_activations'] != 0 or
                    tx['consequences']['receipt']['external_effects'] != 0):
                raise ValueError('signed branch semantics differ')
            handle.guard()
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('construct', 'replay'))
    parser.add_argument('output')
    args = parser.parse_args()
    print(json.dumps(construct(args.output) if args.operation == 'construct' else replay(args.output), sort_keys=True))
