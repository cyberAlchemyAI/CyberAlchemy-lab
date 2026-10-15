"""Profile the unchanged actual expiry test; no clock, source or assertion edits."""
import argparse
import cProfile
import importlib
import importlib.util
import io
import json
from pathlib import Path
import pstats
import sys
import time
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v53'
SOURCE = 'e002f631d6731de456a96aec9f9b8c25a6abd17ca050f04800477ca928752a19'
PROFILE = 'f620983bf0533896adf57a2ebc21c725cf71b117803fbc2164b61e6b253413ec'


def main():
    spec = importlib.util.spec_from_file_location('_cal_API53_expiry_profile_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    name = '_cal_API53_expiry_profile'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = importlib.import_module(name + '.protocol')
    tests = importlib.import_module(name + '.run_session_checks')
    tests.PROFILE = PROFILE
    suite = unittest.TestSuite([tests.Sessions('test_27_actual_expiry_timer_disposes')])
    before = time.monotonic()
    profiler = cProfile.Profile()
    log = io.StringIO()
    profiler.enable()
    try:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    finally:
        profiler.disable()
    elapsed = time.monotonic() - before
    guard.verify(SOURCE)
    stats = pstats.Stats(profiler)
    rows = []
    for (filename, line, function), (primitive, total, own_time, cumulative, callers) in stats.stats.items():
        rows.append({'file': filename, 'line': line, 'function': function,
                     'primitive_calls': primitive, 'total_calls': total,
                     'own_seconds': own_time, 'cumulative_seconds': cumulative})
    rows.sort(key=lambda row: row['cumulative_seconds'], reverse=True)
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': P.source.sha(path.read_bytes())}
    path = RUN / 'API53-original-expiry-profile-0001.log'
    with path.open('x') as stream:
        stream.write(log.getvalue())
    report = {'schema_version': 'lab-expiry-runtime-profile/v1-candidate',
        'measurement_completed': True, 'test_result': 'PASS' if result.wasSuccessful() else 'FAIL',
        'actual_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'elapsed_seconds': elapsed, 'profiling_adds_runtime_overhead': True,
        'original_70_second_test_unchanged': True, 'source_guarded_exit_completed': True,
        'top_cumulative_functions': rows[:80], 'authority_effect': 'none',
        'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'files': [bind(path), bind(Path(__file__).resolve()), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json')],
        'claim_ceiling': 'One unchanged original expiry fixture with actual source/channel and profiler overhead. A failed timing test is preserved; profiling does not qualify a latency bound, alter clocks or admit runtime.'}
    output = RUN / 'API53-original-expiry-profile-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'measurement_completed': True, 'test_result': report['test_result'],
        'actual_cases': result.testsRun, 'elapsed_seconds': elapsed,
        'report_binding': bind(output), 'top_functions': rows[:12]}), flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
