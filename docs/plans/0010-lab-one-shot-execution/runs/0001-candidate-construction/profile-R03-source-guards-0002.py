"""Observe actual cold source construction and an original guard, without grants."""
import argparse
import cProfile
import hashlib
import importlib.util
import json
import pstats
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v30'
SOURCE = RUN / 'source-guard-profile-source-0002.json'
PARENT = RUN / 'guard-stamp-probe-proof-0001.json'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if args.freeze:
        rows = {row['path']: row for row in load(PARENT)['files']}
        for path in [PARENT, Path(__file__)]:
            row = bind(path); rows[row['path']] = row
        for row in rows.values():
            assert bind(ROOT / row['path']) == row, row['path']
        put(SOURCE, {'schema_version': 'lab-source-guard-profile-input/v1-candidate',
                     'files': [rows[key] for key in sorted(rows)],
                     'scope': 'Actual cold selected source and original callback, own read workspace; no host policy, signing key, Session, patch or admission.',
                     'authority_effect': 'none', 'actual_owner_outcome': None})
        print(json.dumps({'source_binding': bind(SOURCE), 'files': len(rows)}), flush=True)
        return
    assert bind(SOURCE)['sha256'] == args.source_sha256
    selected = load(SOURCE)
    def guard():
        for row in selected['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    name = '_cal_actual_source_guard_profile_1'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec);sys.modules[name] = module
    spec.loader.exec_module(module)
    protocol = __import__(name + '.protocol', fromlist=['source'])
    def observe(label, function):
        profile = cProfile.Profile()
        started = time.monotonic()
        value = profile.runcall(function)
        elapsed = time.monotonic() - started
        target = RUN / ('source-guard-profile-' + label + '-0002.pstats')
        assert not target.exists()
        profile.dump_stats(str(target))
        stats = pstats.Stats(profile)
        rows = []
        for (path, line, symbol), (primitive, calls, own, total, callers) in stats.stats.items():
            rows.append({'path': path, 'line': line, 'symbol': symbol, 'calls': calls,
                         'primitive_calls': primitive, 'self_seconds': own, 'cumulative_seconds': total})
        result = {'label': label, 'elapsed_seconds': elapsed, 'total_calls': stats.total_calls,
                  'profile_binding': bind(target),
                  'top_cumulative': sorted(rows, key=lambda row: row['cumulative_seconds'], reverse=True)[:40],
                  'top_self': sorted(rows, key=lambda row: row['self_seconds'], reverse=True)[:40]}
        print(json.dumps({'stage': label, 'elapsed_seconds': elapsed}), flush=True)
        return value, result
    manager = protocol.source.replay_source('custody-participation')
    view, opened = observe('cold-open', manager.__enter__)
    try:
        _, callback = observe('original-guard', view.custody_signed_sources.guard)
        count = len(view.custody_signed_sources.sources.records)
    finally:
        manager.__exit__(None, None, None)
    guard()
    result = {'schema_version': 'lab-original-source-guard-profile/v1-candidate',
              'result': 'PASS', 'source_binding': bind(SOURCE), 'actual_source_records': count,
              'observations': [opened, callback], 'original_callbacks_replaced': False,
              'runtime_change_qualified': False, 'task_complete': False, 'goal_complete': False,
              'authority_effect': 'none', 'actual_owner_outcome': None}
    put(RUN / 'source-guard-profile-result-0002.json', result)
    print(json.dumps({'result': 'PASS', 'result_binding': bind(RUN / 'source-guard-profile-result-0002.json')}), flush=True)


if __name__ == '__main__':
    main()
