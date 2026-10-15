"""Profile one owned actual call separately from the unchanged complete suites."""
import argparse
import cProfile
import hashlib
import importlib.util
import json
from pathlib import Path
import pstats
import sys
import time

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v41'
SOURCE = 'd3fed5312abf115041e35ed22d6bc062386668cdebd5416a782d6703d372e7ab'
PROFILE = '1bb6bc10a17220c209bb813a254a3faef585f5d11315beb7eacfb8a42c0a1f02'


def binding(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-sha256', required=True)
    args = parser.parse_args()
    inputs = RUN / 'API41-public-classification-profile-inputs-0001.json'
    assert binding(inputs)['sha256'] == args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        assert binding(ROOT / row['path']) == row
    name = '_cal_API41_owned_classification_profile_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE)
    assert binding(API / 'contract-profile.json')['sha256'] == PROFILE
    protocol = __import__(name + '.protocol', fromlist=['Schemas'])
    fixture = __import__(name + '.classification_fixture', fromlist=['example'])
    schemas = protocol.Schemas(PROFILE)
    phases = []
    profiler = cProfile.Profile()
    started = time.monotonic()

    def phase(label):
        elapsed = time.monotonic() - started
        row = {'phase': label, 'elapsed_seconds': elapsed}
        phases.append(row)
        print(json.dumps(row), flush=True)

    def profile_phase(label, callback):
        profiler.enable()
        try:
            return callback()
        finally:
            profiler.disable()
            phase(label)
            profiler.dump_stats(str(RUN / ('API41-classification-' + label + '-0001.pstats')))

    phase('schemas-ready')
    manager = protocol.source.replay_source('custody-participation')
    view = profile_phase('source-open', manager.__enter__)
    try:
        owned = fixture.example(view, schemas)
        host, request, selected = profile_phase('host-open', owned.__enter__)
        owned_root = selected['root']
        try:
            raw = protocol.compact(request)
            reply = profile_phase('public-call', lambda: host.call(raw))
            public = {k: reply[k] for k in ('schema_version', 'kind', 'code') if k in reply}
            if reply.get('kind') == 'error':
                public['domain_error_code'] = reply['message']['code']
            phase('public-reply-observed')
        finally:
            profile_phase('host-close', lambda: owned.__exit__(None, None, None))
    finally:
        profile_phase('source-close', lambda: manager.__exit__(None, None, None))
    assert not owned_root.exists()
    guard.verify(SOURCE)
    stats = pstats.Stats(profiler)
    top = sorted(stats.stats.items(), key=lambda row: row[1][3], reverse=True)[:100]
    functions = [{'source': key[0], 'line': key[1], 'function': key[2],
                  'primitive_calls': value[0], 'calls': value[1],
                  'self_seconds': value[2], 'cumulative_seconds': value[3]}
                 for key, value in top]
    value = {'schema_version': 'lab-public-call-performance-diagnostic/v1-candidate',
             'result': 'OBSERVED', 'actual_public_calls': 1,
             'source_binding': binding(API / 'source-manifest.json'),
             'profile_binding': binding(API / 'contract-profile.json'),
             'input_binding': binding(inputs), 'phases': phases,
             'top_cumulative_functions': functions, 'public_reply_fields': public,
             'owned_workspace_removed': True, 'private_values_or_locals_exported': False,
             'clock_replaced': False, 'source_callbacks_replaced': False,
             'time_bounds_extended': False, 'cProfile_enabled': True,
             'original_test_methods_invoked': 0, 'timing_qualification': False,
             'whole_API_qualified': False, 'current_Agent_qualified': False,
             'actual_owner_outcome': None, 'authority_effect': 'none'}
    put(RUN / 'API41-public-classification-profile-0001.json', value)
    print(json.dumps({'result': 'OBSERVED', 'public_fields': public,
                      'owned_workspace_removed': True}), flush=True)


if __name__ == '__main__':
    main()
