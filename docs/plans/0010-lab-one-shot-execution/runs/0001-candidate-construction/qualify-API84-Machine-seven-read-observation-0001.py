"""Run the original seven-read method with a surviving owned audit custodian.

Only the test observer uses the actual parent Vault. Runtime dispatch, source,
clock, permission and lifecycle callbacks are unchanged. No frame locals, RAM,
credentials or arbitrary exception values are exported.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v83'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    name='_cal_API84_Machine_original_seven_read_observer'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.test_machine_transport',fromlist=['MachineTransport'])
    sessions=__import__(name+'.test_custody_sessions',fromlist=['Sessions'])
    observer=__import__(name+'.fixture_observation',fromlist=['record'])
    guard=__import__(name+'.guard',fromlist=['verify'])
    source_binding=bind(API/'source-manifest.json')
    sessions.PROFILE=bind(API/'contract-profile.json')['sha256']
    guard.verify(source_binding['sha256'])
    calls=[]

    class Observed(selected.MachineTransport):
        def machine_call(self,request):
            raw=selected.compact(request)
            started=time.monotonic()
            reply=self.peer.call(raw)
            # Parent owns the same actual workspace after the peer disposes.
            observer.record(self.id(),self.service,raw,reply)
            message=reply.get('message',{})
            calls.append({'operation':request['operation'],'duration_seconds':time.monotonic()-started,
                          'reply_schema_version':reply.get('schema_version'),'kind':reply.get('kind'),
                          'code':message.get('code',reply.get('code')),
                          'peer_closed':self.peer.closed,'resource_closed':self.resource.closed,
                          'observed_after_actual_Session_expiry':selected.A.now()>=self.resource.expires})
            print(json.dumps({'phase':'ACTUAL-CALL-OBSERVED',**calls[-1]}),flush=True)
            self.assertTrue(self.schemas.valid('api-reply',reply),reply)
            self.assertEqual(reply['request_binding']['sha256'],selected.source.sha(raw))
            self.assertEqual(reply['trusted_context_binding'],selected.binding(self.peer.context['context_ref'],selected.compact(self.peer.context)))
            self.machine_events.append({'operation':request['operation'],'request_sha256':selected.source.sha(raw),'reply':reply})
            return reply

    errors=[]

    class Result(unittest.TextTestResult):
        def addError(self,test,error):
            super().addError(test,error)
            frames=[]
            current=error[2]
            while current is not None:
                path=Path(current.tb_frame.f_code.co_filename).resolve()
                if path.is_relative_to(ROOT):frames.append({'path':str(path.relative_to(ROOT)),
                                                            'function':current.tb_frame.f_code.co_name,'line':current.tb_lineno})
                current=current.tb_next
            errors.append({'test_id':test.id(),'exception_class':type(error[1]).__name__,'repository_frames':frames})

    case=Observed('test_02_all_seven_public_read_operations_with_actual_Actor')
    assert getattr(Observed,case._testMethodName) is getattr(selected.MachineTransport,case._testMethodName)
    suite=unittest.TestSuite([case])
    log=RUN/'API84-Machine-seven-read-observation-case-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    guard.verify(source_binding['sha256'])
    report={'schema_version':'lab-original-Machine-seven-read-observation/v1-candidate',
            'result':'PASS' if result.wasSuccessful() else 'FAIL','actual_cases':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'error_frames':errors,'actual_calls':calls,
            'original_test_method_identity_preserved':True,'observer_parent_Vault_selection_declared':True,
            'runtime_source_permission_clock_callbacks_unchanged':True,'time_bounds_extended':False,
            'private_memory_or_exception_values_exported':False,'whole_API_qualified':False,
            'files':[source_binding,bind(API/'contract-profile.json'),bind(API/'test_machine_transport.py'),
                     bind(API/'fixture_observation.py'),bind(Path(__file__).resolve())],
            'task_complete':False,'goal_complete':False,'actual_owner_outcome':None,'authority_effect':'none',
            'claim_ceiling':'Original seven-read method with explicitly changed owned test observation only; actual returned transport/schema outcomes retained. No full Machine/API qualification.'}
    output=RUN/'API84-Machine-seven-read-observation-0001.json'
    with output.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'binding':bind(output),'actual_cases':result.testsRun}),flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
