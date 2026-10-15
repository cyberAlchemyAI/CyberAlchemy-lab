"""Observe original native validation returns; no original callback is replaced."""
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v12'
SOURCE = '5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PROFILE = '2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'
OUTPUT = RUN / 'package-export-diagnostic-0219.json'
MASTER = RUN / 'diagnose-package-export-0219.py'

def bind(path):
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    assert not OUTPUT.exists()
    assert Path(__file__).resolve().parent != RUN and Path(__file__).read_bytes() == MASTER.read_bytes()
    started = datetime.now(timezone.utc).isoformat()
    reports = []
    def observe(frame, event, value):
        if event == 'return' and frame.f_code.co_name == 'validate' and Path(frame.f_code.co_filename) in (
                API / 'candidate.py', API / 'generated_candidate.py'):
            if isinstance(value, tuple) and value and isinstance(value[0], dict):
                report = copy.deepcopy(value[0])
                json.dumps(report, allow_nan=False)
                writer = frame.f_locals.get('writer') or frame.f_locals.get('evidence_writer')
                objects = getattr(writer, '_objects', {})
                retained = []
                for check in report.get('checks', []):
                    for binding in check.get('evidence_bindings', []):
                        raw = objects.get(binding['sha256'])
                        if raw is not None:
                            assert hashlib.sha256(raw).hexdigest() == binding['sha256']
                            value = json.loads(raw)
                            assert value.get('check') == check['check_ref'].removeprefix('check:')
                            retained.append({'binding': copy.deepcopy(binding), 'original_json': value})
                reports.append({'producer_path': str(Path(frame.f_code.co_filename).relative_to(ROOT)),
                                'report': report, 'retained_original_check_objects': retained})
    with (RUN / 'final-api-regression-0173-0190.execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        spec = importlib.util.spec_from_file_location('_pkg_export_diagnostic_guard', API / 'guard.py')
        guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
        manifest = guard.verify(SOURCE)
        name = '_cal_package_export_original_0219'
        spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
        module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
        tests = __import__(name + '.test_package_export', fromlist=['PackageExportAPI'])
        helper = __import__(name + '.export_test_base', fromlist=['*'])
        for fixture in (tests, helper):
            fixture.SOURCE = SOURCE; fixture.PROFILE = PROFILE
        method = 'test_01_controlled_native_candidate_export_with_original_source_proofs'
        stream = io.StringIO()
        sys.setprofile(observe)
        try:
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite([tests.PackageExportAPI(method)]))
        finally:
            sys.setprofile(None)
        guard.verify(SOURCE)
        assert result.testsRun == 1 and reports, 'actual original method and native report required'
        for item in reports:
            __import__(name + '.workspace', fromlist=['privacy']).privacy(item['report'])
        value = {'schema_version': 'lab-original-package-export-diagnostic/v1-candidate',
                 'result': 'PASS-diagnostic-observation', 'original_test_passed': result.wasSuccessful(),
                 'original_failures': len(result.failures), 'original_errors': len(result.errors),
                 'original_methods': result.testsRun, 'original_output': stream.getvalue(),
                 'native_validation_returns': reports, 'started_at': started,
                 'completed_at': datetime.now(timezone.utc).isoformat(),
                 'source_entry_exit_guards': True, 'verified_source_files': len(manifest['files']),
                 'bindings': [bind(MASTER), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json'),
                              bind(API / 'test_package_export.py')],
                 'original_callbacks_or_clocks_modified': False, 'qualification_claim': False,
                 'authority_effect': 'none', 'actual_owner_outcome': None, 'goal_complete': False}
        with OUTPUT.open('x') as output:
            json.dump(value, output, indent=2, sort_keys=True); output.write('\n')
        print(json.dumps({'result': value['result'], 'native_reports': len(reports), 'report_binding': bind(OUTPUT)}), flush=True)

if __name__ == '__main__':
    main()
