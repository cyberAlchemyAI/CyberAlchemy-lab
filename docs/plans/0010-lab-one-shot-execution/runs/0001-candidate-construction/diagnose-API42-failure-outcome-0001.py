"""Observe one unchanged public call and its own isolated development residue.

No clock, callback, grant or test is replaced. Direct residue reading uses only
the development authorization for the newly created owned fixture. It is not
operation.inspect or permission to read a live/existing store after expiry.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v42'
SOURCE = '825f52b83a6a6f318488a47c34dc706f25621b16b85d7607f0e873e7bac338ca'
PROFILE = '63c6a87c23e4c4742d5a4c2aab55908bfe24e85dfedb21c52e5d7b81a470145b'


def bind(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-sha256', required=True)
    args = parser.parse_args()
    inputs = RUN / 'API42-failure-outcome-inputs-0001.json'
    assert bind(inputs)['sha256'] == args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        assert bind(ROOT / row['path']) == row
    name = '_cal_API42_actual_failure_outcome_diagnostic_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE)
    assert bind(API / 'contract-profile.json')['sha256'] == PROFILE
    P = __import__(name + '.protocol', fromlist=['Schemas'])
    F = __import__(name + '.failure_fixture', fromlist=['example'])
    W = __import__(name + '.workspace', fromlist=['read_private'])
    schemas = P.Schemas(PROFILE)
    phases = []
    started = time.monotonic()

    def phase(value):
        row = {'phase': value, 'elapsed_seconds': time.monotonic() - started}
        phases.append(row)
        print(json.dumps(row), flush=True)

    phase('actual-schemas-ready')
    with P.source.replay_source('custody-participation') as view:
        phase('actual-source-replayed')
        with F.example(view, schemas) as (host, request, selected):
            owned_root = selected['root']
            raw = P.compact(request)
            phase('actual-owned-host-ready')
            reply = host.call(raw)
            phase('actual-public-reply')
            public = {k: reply[k] for k in ('schema_version', 'kind') if k in reply}
            if reply.get('kind') == 'error':
                public['domain_error_code'] = reply['message']['code']
                public['domain_error_message'] = reply['message']['message']
            # Read only operation residue from this newly owned development store.
            # Export no material contents, private policy, key or session memory.
            allocations = list((host.vault.root / 'journal').glob('*.allocated.json'))
            stored = []
            for path in (host.vault.root / 'journal').glob('*.result.json'):
                record_raw = W.read_private(path)
                record = P.frame_parse(record_raw)
                domain_raw = host.vault.object_read(record['domain_binding'])
                domain = P.frame_parse(domain_raw)
                stored.append({'posture': record['posture'],
                               'record_sha256': P.source.sha(record_raw),
                               'domain_sha256': P.source.sha(domain_raw),
                               'domain_binding_sha256_matches': P.source.sha(domain_raw) == record['domain_binding']['sha256'],
                               'domain_schema_version': domain.get('schema_version'),
                               'domain_error_code': domain.get('code'),
                               'original_ChangeProposal_schema_valid': schemas.protocol_valid(
                                   'urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', domain),
                               'evidence_binding_count': len(record['evidence_bindings'])})
            phase('owned-development-residue-read')
    assert not owned_root.exists()
    guard.verify(SOURCE)
    phase('owned-fixture-removed-and-source-rechecked')
    value = {'schema_version': 'lab-public-failure-outcome-diagnostic/v1-candidate',
             'result': 'OBSERVED', 'source_binding': bind(API / 'source-manifest.json'),
             'profile_binding': bind(API / 'contract-profile.json'), 'input_binding': bind(inputs),
             'actual_public_calls': 1, 'original_test_methods_invoked': 0,
             'public_reply_fields': public, 'owned_operation_allocation_count': len(allocations),
             'owned_stored_result_summaries': stored, 'phases': phases,
             'request_sha256': P.source.sha(raw), 'reply_sha256': P.source.sha(P.compact(reply)),
             'owned_workspace_removed': True, 'clock_replaced': False,
             'source_callbacks_replaced': False, 'time_bounds_extended': False,
             'private_values_or_memory_exported': False, 'whole_API_qualified': False,
             'current_Agent_qualified': False, 'actual_owner_outcome': None,
             'authority_effect': 'none', 'task_complete': False,
             'claim_ceiling': 'One unchanged public call and residue from its newly owned development fixture only. Direct diagnostic residue reading is not post-expiry API permission or operation qualification.'}
    with (RUN / 'API42-failure-outcome-diagnostic-0001.json').open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'OBSERVED', 'public_fields': public,
                      'stored_result_count': len(stored), 'owned_workspace_removed': True}), flush=True)


if __name__ == '__main__':
    main()
