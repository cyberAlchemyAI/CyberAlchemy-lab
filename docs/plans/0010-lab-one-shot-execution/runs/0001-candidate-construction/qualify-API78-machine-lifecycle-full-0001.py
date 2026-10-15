"""Select all original Machine and termination cases with exact fresh bindings."""
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v78'
SOURCE=json.loads((RUN/'API78-independent-selection-0001.json').read_bytes())['source_binding']['sha256']
PROFILE=json.loads((RUN/'API78-independent-selection-0001.json').read_bytes())['profile_binding']['sha256']
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def chain(error):
    result=[];seen=set()
    # Only fixed source messages. Arbitrary exception values, locals, notes,
    # credentials and their hashes never appear in this diagnostic output.
    public_messages={'Session expired','Session is closed','Machine peer expired','Machine peer or Session is closed','Machine peer unauthenticated','current Machine operation subset differs'}
    while error is not None and id(error) not in seen and len(result)<8:
        seen.add(id(error));frames=[];tb=error.__traceback__
        while tb is not None:
            code=tb.tb_frame.f_code;path=Path(code.co_filename)
            if path.is_relative_to(ROOT):frames.append({'source':path.relative_to(ROOT).as_posix(),'function':code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        row={'exception_class':type(error).__name__,'frames':frames}
        if type(error) is ValueError and type(error.args) is tuple and len(error.args)==1 and type(error.args[0]) is str and error.args[0] in public_messages:row['fixed_source_message']=error.args[0]
        result.append(row);error=error.__cause__ or error.__context__
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    selection_path=RUN/'API78-independent-selection-0001.json'
    assert bind(selection_path)['sha256']==args.selection_sha256
    selection=json.loads(selection_path.read_bytes())
    assert selection['source_binding']['sha256']==SOURCE and selection['profile_binding']['sha256']==PROFILE
    assert selection['driver_binding']==bind(Path(__file__).resolve())
    assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
    name='_cal_API78_machine_read_diagnosis';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(SOURCE)
    original=__import__(name+'.test_custody_sessions',fromlist=['*']);original.PROFILE=PROFILE
    selected=__import__(name+'.test_machine_transport',fromlist=['*']);cases=[]
    class Result(unittest.TextTestResult):
        def _exc_info_to_string(self,error,test):return json.dumps({'exception_chain':chain(error[1])})
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','exception_chain':chain(error[1])})
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','exception_chain':chain(error[1])})
    termination=__import__(name+'.test_termination_boundaries',fromlist=['*']);termination.PROFILE=PROFILE
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(selected.MachineTransport),unittest.defaultTestLoader.loadTestsFromTestCase(termination.TerminationBoundaries)])
    assert suite.countTestCases()==20
    started=datetime.now(timezone.utc).isoformat()
    log=RUN/'API78-machine-lifecycle-full-0001.log'
    with log.open('x') as f:result=unittest.TextTestRunner(stream=f,verbosity=2,resultclass=Result).run(suite)
    guard.verify(SOURCE)
    report={'schema_version':'lab-original-Machine-read-diagnosis/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==20 else 'FAIL',
        'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),'selected_original_cases':20,'original_Machine_cases':14,'original_termination_cases':6,'actual_cases':result.testsRun,'cases':cases,
        'completed_Machine_public_replies':len(getattr(selected.MachineTransport,'machine_events',[])),
        'failures':len(result.failures),'errors':len(result.errors),'source_callbacks_replaced':False,'clock_replaced':False,'time_bounds_extended':False,
        'source_guarded_exit_completed':True,'tracing_used':False,'private_exception_values_exported':False,'private_memory_exported':False,
        'files':[bind(API/'source-manifest.json'),bind(API/'contract-profile.json'),bind(API/'test_machine_transport.py'),bind(Path(__file__).resolve()),bind(log)],
        'original_full_suite_root_cause_established':False,'current_Machine_and_termination_cases_qualified':result.wasSuccessful() and result.testsRun==20,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,
        'claim_ceiling':'All original14 Machine and6 termination cases selected with original source callbacks, real clocks and900 second ceiling. This proof qualifies only observed current cases when all20 actually pass; complete API, owner outcome and admission remain.'}
    path=RUN/'API78-machine-lifecycle-full-0001.json';emit(path,report)
    print(json.dumps({'result':report['result'],'actual_cases':report['actual_cases'],'completed_Machine_public_replies':report['completed_Machine_public_replies'],'failures':report['failures'],'errors':report['errors'],'report_binding':bind(path)}),flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
