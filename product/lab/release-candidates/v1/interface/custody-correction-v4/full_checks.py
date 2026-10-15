"""Preflight frozen sources before all inherited and exact-schema runtime checks."""
import argparse,hashlib,importlib.util,json,sys,time,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True)
    ap.add_argument('--group',choices=['runtime','custody','schemas','coupling'],required=True)
    args=ap.parse_args();source=HERE/'source-manifest.json'
    if sha(source)!=args.source_sha256:raise RuntimeError('source manifest pin differs')
    manifest=json.loads(source.read_bytes())
    def guard():
        for row in manifest['files']:
            if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('source drift '+row['path'])
    guard();sys.path.insert(0,str(HERE));started=time.monotonic();owned=[]
    if args.group=='coupling':
        import coupling_regression
        ok=coupling_regression.run(HERE/'receipts/0001/coupling-adaptation')
        guard();raise SystemExit(0 if ok else 1)
    sys.path.insert(0,str(HERE/'runtime'))
    def module(name,path):
        spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
        sys.modules[name]=m;spec.loader.exec_module(m);return m
    runtime=module('test_runtime',HERE/'regression-sources/test_runtime.py')
    original=runtime.RuntimeTests.setUp
    def setup(test):
        original(test);owned.append(test.root)
    runtime.RuntimeTests.setUp=setup
    if args.group=='runtime':selected=runtime;expected=38
    elif args.group=='custody':selected=module('test_custody',HERE/'regression-sources/test_custody.py');expected=28
    else:selected=module('test_exact_schemas',HERE/'test_exact_schemas.py');expected=12
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.defaultTestLoader.loadTestsFromModule(selected)
    if suite.countTestCases()!=expected:raise RuntimeError('original or new test count differs')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);guard()
    cleanup=[{'path':str(p),'removed':not p.exists()} for p in owned]
    ok=result.wasSuccessful() and result.testsRun==expected and len(owned)==expected and all(r['removed'] for r in cleanup)
    report={'schema_version':'lab-exact-schema-regression-result/v1-candidate','result':'PASS' if ok else 'FAIL',
        'group':args.group,'expected':expected,'tests_run':result.testsRun,'cases':cases,
        'source_sha256':args.source_sha256,'sources_unchanged':True,'original_assertions_changed':False,
        'owned_roots':cleanup,'observations':getattr(selected,'OBSERVATIONS',[]),'elapsed_seconds':time.monotonic()-started,
        'authority_effect':'none','actual_owner_outcome':None,'private_keys_exported':False,
        'task_complete':False,'goal_complete':False}
    p=HERE/'receipts/0001'/f'{args.group}.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt':str(p.relative_to(ROOT)),'sha256':sha(p)}),flush=True)
    raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
