#!/usr/bin/env python3
"""Freeze the full W02 declared boundary suite before owned runtime effects."""
from pathlib import Path
import hashlib,json,os,sys,time,unittest
from fixtures import ROOT,PACKAGE,encoded,parse,byte_sha,require

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
HERE=Path(__file__).resolve().parent

def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':byte_sha(path.read_bytes())}

class Recording(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.checks=[];self.passed=False
    def startTest(self,test):self.passed=False;super().startTest(test)
    def addSuccess(self,test):self.passed=True;super().addSuccess(test)
    def stopTest(self,test):
        self.checks.append({'test':test.id(),'result':'PASS' if self.passed else 'FLAG'})
        print(json.dumps(self.checks[-1]),flush=True);super().stopTest(test)

if __name__=='__main__':
    require(len(sys.argv)==2,'exact native executable path required')
    executable=Path(sys.argv[1]).resolve();manifest=parse((ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json').read_bytes())
    require(byte_sha(executable.read_bytes())==manifest['native_executable_sha256'],'native generator executable changed')
    os.environ['W02_NATIVE_EXECUTABLE']=str(executable)
    context=parse((RUN/'context-W02-v2.json').read_bytes())
    for row in context['source_bindings']:require(byte_sha((ROOT/row['path']).read_bytes())==row['sha256'],'W02 context source drift')
    c13=parse((ROOT/'implementation/lab-continuity/candidates/v1/receipts/C13/0002.json').read_bytes())
    require(c13['result']=='PASS' and c13['task_complete'],'C13 predecessor incomplete')
    files=[binding(p) for folder in [PACKAGE/'authority',PACKAGE/'tools',HERE] for p in folder.glob('*.py')]
    files += [binding(PACKAGE/'authority/BOUNDARY.md'),binding(RUN/'context-W02-v2.json'),binding(RUN/'CONTEXT-W02-v2.md')]
    files += c13['files']+c13['source_bindings']+context['source_bindings']
    for kind in ['principal','role','role-assignment','agent-assignment','delegation','tool','agent-instance','agent-session','agent-profile']:
        files.append(binding(ROOT/f'authority/artifact-types/{kind}/v1/fixtures/valid/record.json'))
    files=list({r['path']:{'path':r['path'],'sha256':r['sha256']} for r in files}.values())
    for r in files:require(byte_sha((ROOT/r['path']).read_bytes())==r['sha256'],'W02 prerequisite/source changed')
    index=1
    while (HERE/f'{index:04d}.json').exists():index+=1
    directory=HERE/f'{index:04d}';directory.mkdir()
    frozen=directory/'manifest.json';frozen.write_bytes(encoded({'authority_effect':'none','files':files}))
    suite=unittest.defaultTestLoader.discover(str(HERE),pattern='test_boundaries.py');count=suite.countTestCases();started=time.perf_counter()
    log=directory/'terminal.log'
    with log.open('w') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recording).run(suite)
    import test_boundaries
    example=directory/'observed-boundaries.json';example.write_bytes(encoded({'authority_effect':'none','fixture_only_permission':True,'actual_owner_outcome':None,'Tool_episode':test_boundaries.DispatchTests.observed,'actual_context':test_boundaries.ActualContextTests.observed}))
    drift=[r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    passed=result.wasSuccessful() and result.testsRun==count==40 and len(result.checks)==40 and not drift and test_boundaries.ActualContextTests.observed is not None
    receipt={'schema_version':'lab-W02-bounded-action-suite/v1-candidate','task':'W02','authority_effect':'none','result':'PASS' if passed else 'FLAG','task_complete':passed,'tests':result.testsRun,'checks':result.checks,'source_drift':drift,'duration_seconds':time.perf_counter()-started,'files':files+[binding(frozen),binding(log),binding(example)],'source_bindings':context['source_bindings'],'actual_owner_outcome':None,'remaining_obligations':[] if passed else ['Every declared bounded actor/Tool check must pass.'],'claim_ceiling':'40 candidate actor/Tool checks; generic APIs, permanent production authority and power-loss durability remain downstream.'}
    path=HERE/f'{index:04d}.json';path.write_bytes(encoded(receipt));print(json.dumps({'result':receipt['result'],'tests':result.testsRun,'task_complete':passed,'receipt':str(path.relative_to(ROOT))}),flush=True)
    sys.exit(0 if passed else 1)
