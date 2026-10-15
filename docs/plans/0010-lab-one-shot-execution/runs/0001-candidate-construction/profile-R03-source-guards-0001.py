"""Untraced actual guard timings, exact source; owned read-only replay only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v19'
API_PIN = 'fcd98b74253bc5a7f081faed13c2b4c198df55ff3f6e6772563e1d50a784ff1b'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def guard(pin):
    path = HERE / 'source-guard-profile-source-0001.json'
    assert sha(path.read_bytes()) == pin
    for row in json.loads(path.read_bytes())['files']:
        path = ROOT / row['path']
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], row['path']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    guard(args.source_sha256)
    name = '_cal_actual_guard_profile_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    P = __import__(name + '.protocol', fromlist=['*'])
    M = __import__(name + '.artifact_model', fromlist=['*'])
    G = __import__(name + '.guard', fromlist=['*'])
    G.verify(API_PIN)
    events = []

    def measured(label, function):
        started = time.perf_counter()
        value = function()
        event = {'operation': label, 'elapsed_seconds': time.perf_counter() - started, 'result': 'PASS'}
        events.append(event)
        print(json.dumps(event), flush=True)
        return value

    with P.source.replay_source('custody-participation') as view:
        selected = view.custody_signed_sources
        subject = next(s for s in view.subjects.values() if s['identity'] == 'work:R03-original-reader')
        D = measured('complete_delivery_source_preflight', P.source.custody_delivery)
        for index in range(2):
            measured('complete_signed_source_guard_' + str(index), selected.guard)
            actual = measured('current_public_artifact_header_' + str(index), lambda: M.artifact_ref(view, subject))
            direct = measured('already_selected_same_reader_header_' + str(index), lambda: D.reader.adapter.model.artifact_ref(view, subject))
            assert actual == direct
            actual_bytes = measured('current_public_original_bytes_' + str(index), lambda: M.record_bytes(view, subject))
            direct_bytes = measured('already_selected_same_reader_original_bytes_' + str(index), lambda: D.reader.adapter.model.record_bytes(view, subject))
            assert actual_bytes == direct_bytes
        measured('source_resolution_with_full_current_guard', lambda: selected.sources.resolve(subject['version_ref']))
        assert len(view.subjects) == 582
    G.verify(API_PIN)
    guard(args.source_sha256)
    result = {'schema_version': 'lab-original-source-guard-timings/v1-candidate', 'result': 'OBSERVED',
              'source_sha256': args.source_sha256, 'api_source_sha256': API_PIN, 'events': events,
              'all_current_guards_executed': True, 'production_code_modified': False, 'trace_enabled': False,
              'no_host_keys_or_sessions_created': True, 'owned_read_replay_closed': True,
              'performance_qualification': False, 'actual_owner_outcome': None, 'authority_effect': 'none',
              'task_complete': False}
    path = HERE / 'source-guard-profile-result-0001.json'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({'result': 'OBSERVED', 'measurements': len(events), 'trace_enabled': False}), flush=True)


if __name__ == '__main__':
    main()
