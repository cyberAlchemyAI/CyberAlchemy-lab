"""Exercise original Machine Context request construction immediately after auth."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v80'
SOURCE = '8abfcfe22b838f0779b8f3916d145018b83fb1b518173fbb98e44fd0d4b893cf'
PROFILE = '4702614e44bdb89a43292e2a8b231849b6464c8abf56d012f7d67a7216e1daa8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    started = datetime.now(timezone.utc).isoformat()
    name = '_cal_API80_actual_Machine_query_diagnosis'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE)
    sessions = __import__(name + '.test_custody_sessions', fromlist=['*'])
    sessions.PROFILE = PROFILE
    selected = __import__(name + '.test_machine_transport', fromlist=['*'])
    helpers = __import__(name + '.custody_context_sessions', fromlist=['D'])
    observations = []
    outcome = {'result': 'FAIL', 'fixed_exception_message': None, 'exception_frames': []}

    class Probe(selected.MachineTransport):
        def test_probe(self):
            context, _ = self.authenticated()
            observations.append({'phase': 'actual-Machine-authentication', 'result': 'PASS'})
            message = helpers.D.query(self.view.custody_signed_sources, self.peer.service.sessions.bridge)
            assert message['actor']['agent_instance_ref'] == context['agent_instance_ref']
            assert message['actor']['session_ref'] == context['session_ref']
            observations.append({'phase': 'original-Context-query-construction', 'result': 'PASS'})

    class Result(unittest.TextTestResult):
        def _exc_info_to_string(self, error, test):
            frames = []
            tb = error[2]
            while tb:
                path = Path(tb.tb_frame.f_code.co_filename)
                if path.is_relative_to(ROOT):
                    frames.append({'source': path.relative_to(ROOT).as_posix(), 'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
                tb = tb.tb_next
            outcome['exception_class'] = type(error[1]).__name__
            outcome['exception_frames'] = frames
            allowed = {'Session expired', 'Session is closed', 'Machine peer expired', 'Machine peer or Session is closed', 'Machine peer unauthenticated'}
            if type(error[1]) is ValueError and len(error[1].args) == 1 and error[1].args[0] in allowed:
                outcome['fixed_exception_message'] = error[1].args[0]
            return json.dumps({'exception_class': outcome['exception_class'], 'frames': frames})

    log = RUN / 'API80-Machine-context-query-diagnosis-0001.log'
    with log.open('x') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(unittest.TestSuite([Probe('test_probe')]))
    guard.verify(SOURCE)
    outcome.update(schema_version='lab-original-Machine-query-diagnosis/v1-candidate',
                   result='PASS' if result.wasSuccessful() and result.testsRun == 1 else 'FAIL',
                   actual_cases=result.testsRun, errors=len(result.errors), failures=len(result.failures),
                   observations=observations, started_at=started, completed_at=datetime.now(timezone.utc).isoformat(),
                   files=[bind(path) for path in [API / 'source-manifest.json', API / 'contract-profile.json', Path(__file__).resolve(), log]],
                   source_callbacks_replaced=False, clock_replaced=False, permissions_cached=False,
                   private_exception_values_exported=False, frame_locals_inspected=False,
                   current_Machine_qualified=False, whole_API_qualified=False,
                   authority_effect='none', actual_owner_outcome=None, task_complete=False, goal_complete=False)
    path = RUN / 'API80-Machine-context-query-diagnosis-0001.json'
    with path.open('x') as stream:
        json.dump(outcome, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': outcome['result'], 'actual_cases': result.testsRun, 'phases': observations,
                      'report_binding': bind(path)}), flush=True)
    return 0 if outcome['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
