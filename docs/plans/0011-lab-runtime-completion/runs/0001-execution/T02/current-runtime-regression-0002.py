"""Whole original affected classes with durable per-case observations.

Future independent source/profile selection must include this true origin.
Never restore the interrupted process, its keys, identities or lease state.
"""
import argparse
import datetime
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'

class Observed(unittest.TestResult):
    def __init__(self, event):
        super().__init__()
        self.observations = []
        self.started = None
        self.event = event

    def startTest(self, test):
        super().startTest(test)
        self.started = time.monotonic()
        self.event({'phase': 'test-start', 'test': test.id()})

    def record(self, test, status, error=None):
        row = {'test': test.id(), 'status': status,
            'elapsed_seconds': None if self.started is None else time.monotonic()-self.started}
        if error:
            row['error_type'] = error[0].__name__
            frames = []
            tb = error[2]
            while tb:
                path = Path(tb.tb_frame.f_code.co_filename)
                if path.is_relative_to(ROOT):
                    frames.append({'file': str(path.relative_to(ROOT)),
                        'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
                tb = tb.tb_next
            row['frames'] = frames
        self.observations.append(row)
        self.event({'phase': 'test-result', **row})
        self.started = None

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, 'PASS')

    def addFailure(self, test, error):
        self.failures.append((test, error[0].__name__))
        self.record(test, 'FAIL', error)

    def addError(self, test, error):
        self.errors.append((test, error[0].__name__))
        self.record(test, 'ERROR', error)

    def addSkip(self, test, reason):
        super().addSkip(test, 'bounded skip')
        self.record(test, 'SKIP')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--output-prefix', required=True)
    args = parser.parse_args()
    assert len(args.source) == len(args.profile) == 64
    assert args.output_prefix.replace('-', '').isalnum()
    events = RUN/'T02'/(args.output_prefix+'.events.jsonl')
    output = RUN/'T02'/(args.output_prefix+'.json')
    assert not events.exists() and not output.exists()
    with events.open('x') as stream:
        def event(value):
            row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), **value}
            stream.write(json.dumps(row)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
            print(json.dumps({k: v for k, v in row.items() if k != 'frames'}), flush=True)
        lock = os.open(RUN/'lease-sensitive-runtime.lock', os.O_RDWR|os.O_NOFOLLOW)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
            event({'phase': 'runner-start', 'OS_pid': os.getpid(),
                'source_sha256': args.source, 'profile_sha256': args.profile})
            name = '_root_api17_current_whole_regression0002'
            spec = importlib.util.spec_from_file_location(name, API/'__init__.py', submodule_search_locations=[str(API)])
            package = importlib.util.module_from_spec(spec)
            sys.modules[name] = package
            spec.loader.exec_module(package)
            guard = __import__(name+'.guard', fromlist=['verify'])
            guard.verify(args.source)
            event({'phase': 'full-current-entry-guard', 'result': 'PASS'})
            classes = []
            for leaf, class_name in [('test_custody_sessions', 'Sessions'),
                    ('run_session_checks', 'Sessions'), ('test_termination_boundaries', 'TerminationBoundaries')]:
                module = __import__(name+'.'+leaf, fromlist=[class_name])
                module.PROFILE = args.profile  # independently selected test fixture input
                classes.append(getattr(module, class_name))
            suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in classes)
            assert suite.countTestCases() == 74, 'complete original affected class selection required'
            result = Observed(event)
            suite.run(result)
            guard.verify(args.source)
            event({'phase': 'full-current-exit-guard', 'result': 'PASS'})
            value = {'schema_version': 'lab-current-whole-Session-regression/v2-candidate',
                'source_sha256': args.source, 'profile_sha256': args.profile,
                'observations': result.observations, 'tests_expected': 74, 'tests_run': result.testsRun,
                'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
                'entry_exit_current_guard': 'PASS', 'historical_physical_closure': 'REFUSED',
                'task_complete': False, 'authority_effect': 'none', 'private_values_recorded': False,
                'result': 'PASS' if result.wasSuccessful() and not result.skipped and result.testsRun == 74 else 'FAIL'}
            with output.open('x') as handle:
                json.dump(value, handle, indent=2)
                handle.write('\n')
            event({'phase': 'terminal', **{k: v for k, v in value.items() if k != 'observations'}})
            return 0 if value['result'] == 'PASS' else 1
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
            os.close(lock)

if __name__ == '__main__':
    raise SystemExit(main())
