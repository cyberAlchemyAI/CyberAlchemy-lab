"""Verify frozen sources before importing the candidate; retain terminal results."""
import argparse,hashlib,importlib.metadata,json,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(manifest):
    for row in manifest['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('source changed: '+row['path'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);ap.add_argument('--suite',choices=['legacy','custody','all'],default='all');ap.add_argument('--out',required=True);args=ap.parse_args()
    if sha(HERE/'source-manifest.json')!=args.source_sha256:raise RuntimeError('source manifest preflight mismatch')
    manifest=json.loads((HERE/'source-manifest.json').read_bytes());check(manifest)
    out=HERE/args.out
    if not out.resolve().is_relative_to(HERE/'receipts') or out.exists():raise RuntimeError('result requires unused receipt path')
    # Verify regression adaptation byte-for-byte before importing its successor.
    old=(ROOT/'implementation/lab-runtime/v2/tests/test_runtime.py').read_text()
    expected=old.replace('REPO = PACKAGE.parents[2]','REPO = PACKAGE.parents[6]').replace('PACKAGE.parent / "v1"','REPO / "implementation/lab-runtime/v1"').replace('PACKAGE.parent / "v1/profile.json"','REPO / "implementation/lab-runtime/v1/profile.json"')
    if (HERE/'runtime/tests/test_runtime.py').read_text()!=expected:raise RuntimeError('original regression assertions changed')
    sys.path[:0]=[str(HERE/'runtime'),str(HERE/'runtime/tests')]
    import tempfile,unittest,test_runtime,test_custody
    roots=[]
    class OwnedTemporaryDirectory(tempfile.TemporaryDirectory):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);roots.append(Path(self.name))
    test_runtime.TemporaryDirectory=OwnedTemporaryDirectory
    from lab_runtime.common import load
    from lab_runtime.protocols import SCHEMAS
    for name,schema in SCHEMAS.items():
        if load(HERE/'runtime/schemas'/f'{name}.schema.json')!=schema:raise RuntimeError('derived protocol schema mismatch: '+name)
    checks=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);checks.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);checks.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);checks.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite()
    if args.suite in ('legacy','all'):suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_runtime.RuntimeTests))
    if args.suite in ('custody','all'):suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_custody.CustodyTests))
    count=suite.countTestCases();started=time.monotonic();r=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    check(manifest);cleanup=[{'path':str(p),'removed':not p.exists()} for p in roots]
    good=r.wasSuccessful() and r.testsRun==count and all(v['removed'] for v in cleanup)
    report={'schema_version':'lab-original-byte-custody-tests/v1-candidate','result':'PASS' if good else 'FAIL','suite':args.suite,
        'source_manifest_binding':{'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':args.source_sha256},
        'tests_run':r.testsRun,'expected_test_methods':count,'checks':checks,'sources_unchanged':True,
        'owned_roots':cleanup,'private_keys_exported':False,'private_memory_exported':False,
        'observations':test_custody.OBSERVATIONS,'elapsed_seconds':round(time.monotonic()-started,3),
        'dependencies':{n:importlib.metadata.version(n) for n in ('jsonschema','cryptography')},'python':sys.version,
        'actual_owner_outcome':None,'authority_effect':'none','repository_admission_effect':'none','task_complete':False,
        'claim_ceiling':'Candidate storage primitive and all selected original assertions only; no full API/semantic/privacy/package/admission closure.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':report['result'],'suite':args.suite,'tests_run':r.testsRun,'owned_roots':len(roots),'removed':all(v['removed'] for v in cleanup),'result_binding':{'path':str(out.relative_to(ROOT)),'sha256':sha(out)}}),flush=True)
    raise SystemExit(0 if good else 1)
if __name__=='__main__':main()
