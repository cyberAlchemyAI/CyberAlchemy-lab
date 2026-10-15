#!/usr/bin/env python3
"""Freeze and validate all C13 actual Work continuity cases with progress evidence."""
import argparse,json,os,time,unittest
from continuity import *


class RecordingResult(unittest.TextTestResult):
    def __init__(self,*args,**kw):super().__init__(*args,**kw);self.checks=[];self.ok=False
    def startTest(self,test):self.ok=False;super().startTest(test)
    def addSuccess(self,test):self.ok=True;super().addSuccess(test)
    def stopTest(self,test):
        self.checks.append({'test':test.id(),'result':'PASS' if self.ok else 'FLAG'})
        PROGRESS.write_bytes(encoded({'result':'RUNNING','tests':self.testsRun,'checks':self.checks,'last_test':test.id(),'elapsed_seconds':time.perf_counter()-STARTED}))
        print(json.dumps(self.checks[-1]),flush=True);super().stopTest(test)


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':byte_digest(regular(path))}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--native-executable',required=True);args=parser.parse_args()
    verify_inputs();generator=load(MANIFEST);executable=Path(args.native_executable).resolve()
    require(byte_digest(regular(executable))==generator['native_executable_sha256'],'native executable differs from reviewed generator')
    os.environ['C13_NATIVE_EXECUTABLE']=str(executable)
    receipts=PACKAGE/'receipts/C13';receipts.mkdir(parents=True,exist_ok=True);index=1
    while (receipts/f'{index:04d}.json').exists():index+=1
    run=receipts/f'{index:04d}';run.mkdir();PROGRESS=run/'progress.json';STARTED=time.perf_counter()
    source_files=[binding(p) for p in PACKAGE.glob('*.py')]+[binding(p) for p in (PACKAGE/'tests').glob('*.py')]
    source_files+=[binding(PACKAGE/'README.md')]+[binding(RUN/name) for name in ['context-C13-v2.json','CONTEXT-C13-v2.md']]
    source_files+=generator['files']+[binding(MANIFEST),generator['implementation_record'],generator['realization_record']]
    source_files=list({r['path']:r for r in source_files}.values())
    frozen=run/'manifest.json';frozen.write_bytes(encoded({'schema_version':'lab-C13-complete-continuity-source-manifest/v1-candidate','authority_effect':'none','files':source_files}))
    suite=unittest.defaultTestLoader.discover(str(PACKAGE/'tests'));count=suite.countTestCases()
    log=run/'terminal.log'
    with log.open('w') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=RecordingResult).run(suite)
    import test_continuity
    observed=test_continuity.ContinuityTests.observed
    drift=[r['path'] for r in source_files if byte_digest(regular(ROOT/r['path']))!=r['sha256']]
    verify_inputs();passed=result.wasSuccessful() and result.testsRun==count==21 and len(result.checks)==count and observed is not None and not drift
    example=run/'observed-continuity.json';example.write_bytes(encoded({'authority_effect':'none','actual_owner_outcome':None,'observations':observed}))
    if observed is not None:
        # All Session and transition private keys were owned by the class root.
        require(not test_continuity.ContinuityTests.root.exists(),'owned continuity root/private key remained after suite')
    receipt={'schema_version':'lab-C13-actual-Work-continuity-check/v1-candidate','task':'C13','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':passed,'tests':result.testsRun,'checks':result.checks,
        'duration_seconds':time.perf_counter()-STARTED,'source_drift':drift,'actual_owner_outcome':None,
        'repository_admissions_applied':0,'actual_admitted_L1_closure':False,'candidate_runtime_scope':'actual restored C12 Work, fresh committed-source Agent context and explicit independent D75 read-profile reconstruction',
        'files':source_files+[binding(frozen),binding(log),binding(example)],'source_bindings':load(RUN/'context-C13-v2.json')['source_bindings'],
        'remaining_obligations':[] if passed else ['All declared actual Work continuity, provenance and fresh-Agent cases must pass.'],
        'operational_deferrals':L1_DEFERRALS,'claim_ceiling':'Candidate continuity only; operational owner admission/activation, general APIs, domain ontology mapping and Product claims remain explicit downstream obligations.'}
    path=receipts/f'{index:04d}.json';path.write_bytes(encoded(receipt))
    print(json.dumps({'result':receipt['result'],'tests':result.testsRun,'receipt':path.relative_to(ROOT).as_posix(),'source_drift':drift}),flush=True)
    sys.exit(0 if passed else 1)
