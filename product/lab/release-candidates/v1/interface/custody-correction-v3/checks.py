"""Guard selected source before imports; run all preserved correction guards."""
import argparse,hashlib,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(m):
    for row in m['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('source changed '+row['path'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    if sha(HERE/'source-manifest.json')!=args.source_sha256:raise RuntimeError('source pin differs')
    m=json.loads((HERE/'source-manifest.json').read_bytes());guard(m);sys.path.insert(0,str(HERE))
    import test_corrections,test_schema_cache
    from loader import EnginePins,engine,parse
    with engine(EnginePins(**parse((HERE/'pins.json').read_bytes()))) as handle:
        protocols=__import__(handle.name+'.protocols',fromlist=['SCHEMAS'])
        for name,schema in protocols.SCHEMAS.items():
            if handle.common.load(HERE/'runtime/schemas'/f'{name}.schema.json')!=schema:raise RuntimeError('protocol export drift '+name)
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_corrections),unittest.defaultTestLoader.loadTestsFromModule(test_schema_cache)])
    expected=suite.countTestCases();result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);guard(m)
    owned=getattr(test_corrections.CorrectionGuards,'owned',None)
    removed=owned is not None and not Path(owned).exists()
    report={'schema_version':'lab-custody-correction-guard-result/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==expected and removed else 'FAIL','tests_run':result.testsRun,'expected':expected,'cases':cases,'sources_unchanged':True,'owned_correction_root':{'path':str(owned),'removed':removed},'authority_effect':'none','actual_owner_outcome':None,'private_keys_exported':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'All inherited correction and syntax cache assertions against this successor; combined positive custody and full public API are separate checks.'}
    p=HERE/'receipts/0001/guards.json';p.parent.mkdir(parents=True,exist_ok=True);p.open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt':str(p.relative_to(ROOT)),'sha256':sha(p)}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
