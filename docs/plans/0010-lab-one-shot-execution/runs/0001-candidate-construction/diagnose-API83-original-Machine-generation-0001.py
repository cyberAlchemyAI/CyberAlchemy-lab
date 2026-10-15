"""Call the original generator directly to retain its safe refusal chain."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v83'
KNOWN='fact scope selects another host channel'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def chain(error):
    result=[]
    while error is not None:
        frames=[];tb=error.__traceback__
        while tb is not None:
            path=Path(tb.tb_frame.f_code.co_filename).resolve()
            if path.is_relative_to(ROOT):frames.append({'path':str(path.relative_to(ROOT)),
                                                        'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        item={'exception_class':type(error).__name__,'repository_frames':frames}
        if type(error) is ValueError and str(error)==KNOWN:item['known_original_refusal']=KNOWN
        result.append(item);error=error.__cause__ or error.__context__
    return result


def main():
    name='_cal_API83_original_generation_refusal'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.test_machine_transport',fromlist=['MachineTransport'])
    sessions=__import__(name+'.test_custody_sessions',fromlist=['Sessions'])
    guard=__import__(name+'.guard',fromlist=['verify'])
    source_binding=bind(API/'source-manifest.json')
    sessions.PROFILE=bind(API/'contract-profile.json')['sha256']
    guard.verify(source_binding['sha256'])
    observed={}

    class Diagnosis(selected.MachineTransport):
        def test_original_generation_refuses_parent_policy_host_in_Machine_scope(self):
            self.authenticated()
            child=self.peer.service
            bridge=child.sessions.bridge
            message=selected.D.query(self.view.custody_signed_sources,bridge)
            message['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
            runtime=__import__(name+'.custody_context_sessions',fromlist=['MAPPING_PIN'])
            caught=None
            try:
                selected.D.generate(self.view.custody_signed_sources,bridge,message,
                                    selected.compact(message),runtime.MAPPING_PIN,self.schemas)
            except Exception as error:
                caught=error;observed['exception_chain']=chain(error)
            observed.update(peer_closed=self.peer.closed,resource_closed=self.resource.closed,
                            actual_Session_expired=selected.A.now()>=self.resource.expires,
                            original_generation_function_binding=bind(Path(selected.D.generate.__code__.co_filename)))
            self.assertIsNotNone(caught)
            self.assertTrue(any(row.get('known_original_refusal')==KNOWN for row in observed['exception_chain']))
            self.assertTrue(self.peer.closed)
            self.assertFalse(self.resource.closed)
            self.assertFalse(observed['actual_Session_expired'])

    suite=unittest.TestSuite([Diagnosis('test_original_generation_refuses_parent_policy_host_in_Machine_scope')])
    log=RUN/'API83-original-Machine-generation-diagnosis-case-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    guard.verify(source_binding['sha256'])
    report={'schema_version':'lab-original-Machine-generation-refusal-diagnosis/v1-candidate',
            'result':'PASS' if result.wasSuccessful() else 'FAIL','actual_cases':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'observed':observed,
            'files':[source_binding,bind(API/'contract-profile.json'),bind(Path(__file__).resolve()),
                     bind(API/'machine_transport.py'),bind(API/'auth.py'),
                     bind(ROOT/'product/lab/release-candidates/v1/interface/fact-read-scope-v1/scope.py')],
            'original_callbacks_unchanged':True,'clock_replaced':False,'time_bounds_extended':False,
            'private_frame_locals_or_exception_values_exported':False,'whole_API_qualified':False,
            'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,
            'claim_ceiling':'Actual current original generator refusal and safe known source-host mismatch only. Older historical suite cause and complete Machine/API remain unqualified.'}
    output=RUN/'API83-original-Machine-generation-diagnosis-0001.json'
    with output.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'binding':bind(output),'actual_cases':result.testsRun}),flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
