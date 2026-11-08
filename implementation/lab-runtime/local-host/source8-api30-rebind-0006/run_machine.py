"""Disjoint MachineTransport suffix replay after the frozen T02 v4/v5 runs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
V5 = HERE.with_name('source8-api30-rebind-0005')
V5_RESULT = V5 / 'working/remainder-result-0001.json'
V5_RESULT_SHA = '20b649f019253210123a4b345d9a6a8305a6cc5e7b11b158345e341ac307e143'
sys.path.insert(0, str(V5))
import run_remainder as prior


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    need(prior.sha(V5_RESULT) == V5_RESULT_SHA, 'frozen v5 result differs')
    v5 = json.loads(V5_RESULT.read_bytes())
    need(v5['result'] == 'FAIL' and v5['tests_run'] == 17 and
         len(v5['case_rows']) == 17 and
         all(row['result'] == 'PASS' for row in v5['case_rows']) and
         len(v5['errors']) == 1 and
         "NameError: name 'PROFILE' is not defined" in v5['errors'][0][1] and
         v5['selected_case_ids'][17:] and len(v5['selected_case_ids'][17:]) == 14,
         'frozen v5 17-pass/Machine class error differs')
    name, old, manifest = prior.select()
    need(v5['selected_case_ids'] == old['selected_case_ids'][68:],
         'v5 and v4 selected suffix differ')
    module = __import__(name + '.test_machine_transport', fromlist=['MachineTransport'])
    custody = sys.modules[name + '.test_custody_sessions']
    # The inherited setUpClass executes in test_custody_sessions globals.
    custody.PROFILE = prior.PROFILE_SHA
    module.PROFILE = prior.PROFILE_SHA
    cls = module.MachineTransport
    methods = unittest.defaultTestLoader.getTestCaseNames(cls)
    need(len(methods) == 14, 'MachineTransport inventory differs')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    cases = list(suite)
    need([case.id() for case in cases] == v5['selected_case_ids'][17:],
         'MachineTransport exact selected suffix differs')
    started = datetime.now(timezone.utc).isoformat()
    result = unittest.TextTestRunner(verbosity=2, failfast=True,
                                     resultclass=prior.Outcome).run(suite)
    verdict = {'result': 'PASS' if result.wasSuccessful() and result.testsRun == 14 else 'FAIL',
               'predecessor_result_sha256': V5_RESULT_SHA,
               'source_manifest_sha256': prior.API_SHA,
               'profile_sha256': prior.PROFILE_SHA,
               'selected_case_ids': v5['selected_case_ids'][17:],
               'started_at_utc': started,
               'completed_at_utc': datetime.now(timezone.utc).isoformat(),
               'tests_run': result.testsRun, 'case_rows': result.rows,
               'failures': [(case.id(), value[-1600:]) for case, value in result.failures],
               'errors': [(case.id(), value[-1600:]) for case, value in result.errors],
               'source_unchanged_during_run':
                    prior.sha(prior.API / 'source-manifest.json') == prior.API_SHA and
                    all(prior.sha(prior.ROOT / row['path']) == row['sha256'] for row in manifest['files']),
               'runner_sha256': prior.sha(Path(__file__).resolve())}
    out = HERE / 'working'
    out.mkdir(mode=0o700, exist_ok=True)
    target = out / 'machine-result-0001.json'
    need(not target.exists(), 'versioned result already exists')
    target.write_text(json.dumps(verdict, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'result': verdict['result'], 'tests_run': result.testsRun,
                      'failures': len(result.failures), 'errors': len(result.errors)}))


if __name__ == '__main__':
    main()
