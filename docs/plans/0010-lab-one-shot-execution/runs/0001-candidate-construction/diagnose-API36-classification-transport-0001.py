"""One actual public call; capture public transport metadata, never credentials."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v36'
SOURCE = '1c32032bf01bf9327f8bf2efb731ac30a0970734cd408307ddbe97c6b7a5b1fa'
PROFILE = '6abdc9fece51b43351c3bb0ee78290992e07d3efee63cb97e6ecc3a5155fb2d8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-sha256', required=True)
    args = parser.parse_args()
    inputs = RUN / 'API36-classification-transport-inputs-0001.json'
    assert bind(inputs)['sha256'] == args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        assert bind(ROOT / row['path']) == row
    name = '_cal_API36_classification_transport_diagnostic_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE)
    assert bind(API / 'contract-profile.json')['sha256'] == PROFILE
    P = __import__(name + '.protocol', fromlist=['Schemas'])
    CF = __import__(name + '.classification_fixture', fromlist=['example'])
    started = time.monotonic()
    schemas = P.Schemas(PROFILE)
    print(json.dumps({'stage': 'schemas-ready'}), flush=True)
    with P.source.replay_source('custody-participation') as view:
        print(json.dumps({'stage': 'actual-source-replay-ready'}), flush=True)
        with CF.example(view, schemas) as (host, request, selected):
            owned_root = selected['root']
            print(json.dumps({'stage': 'actual-owned-host-ready'}), flush=True)
            raw = P.compact(request)
            reply = host.call(raw)
            public = {key: reply[key] for key in ('schema_version', 'kind', 'code') if key in reply}
            print(json.dumps({'stage': 'actual-public-reply', 'public_fields': public}), flush=True)
            valid = schemas.valid('api-call', request)
            print(json.dumps({'stage': 'original-call-schema-check', 'valid': valid}), flush=True)
    assert not owned_root.exists(), 'owned diagnostic workspace remains'
    guard.verify(SOURCE)
    report = {'schema_version': 'lab-public-classification-transport-diagnostic/v1-candidate',
              'result': 'OBSERVED', 'source_binding': bind(API / 'source-manifest.json'),
              'profile_binding': bind(API / 'contract-profile.json'), 'input_binding': bind(inputs),
              'request_sha256': hashlib.sha256(raw).hexdigest(),
              'reply_sha256': hashlib.sha256(P.compact(reply)).hexdigest(),
              'public_reply_fields': public, 'original_api_call_schema_valid': valid,
              'elapsed_seconds': time.monotonic() - started, 'actual_public_calls': 1,
              'owned_workspace_removed': True, 'private_keys_exported': False,
              'original_test_methods_invoked': 0, 'clock_replaced': False,
              'source_callbacks_replaced': False, 'time_bounds_extended': False,
              'whole_API_qualified': False, 'current_Agent_qualified': False,
              'authority_effect': 'none', 'actual_owner_outcome': None}
    with (RUN / 'API36-classification-transport-diagnostic-0001.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'OBSERVED', 'public_reply_fields': public,
                      'original_api_call_schema_valid': valid, 'owned_workspace_removed': True}), flush=True)


if __name__ == '__main__':
    main()
