"""All original prospective preparation guards against the selected successor."""
import argparse, hashlib, importlib.util, json, os, sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[5]; API = HERE.parent/'api-v16'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    with p.open('x') as f:f.write(json.dumps(v,sort_keys=True,indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser()
    for name in ['source-sha256','profile-sha256','producer-sha256']:parser.add_argument('--'+name,required=True)
    args=parser.parse_args();assert sha(HERE/'source-manifest.json')==args.producer_sha256
    for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256']
    assert sha(API/'source-manifest.json')==args.source_sha256
    for row in json.loads((API/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256']
    name='_cal_api_v16';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    protocol=__import__(name+'.protocol',fromlist=['Schemas']);protocol.Schemas(args.profile_sha256)
    original=__import__(name+'.test_preparation_corrected',fromlist=['CorrectedPreparation']);roots=[]
    class TrackedPreparation(original.CorrectedPreparation):
        def setUp(self):
            try:super().setUp()
            finally:
                if hasattr(self,'root'):roots.append(self.root)
    cls=TrackedPreparation
    output=HERE/'receipts/0001';output.mkdir(parents=True,exist_ok=False)
    names=unittest.defaultTestLoader.getTestCaseNames(cls);assert len(names)==47
    with (output/'tests.stderr').open('x') as stderr:
        result=unittest.TextTestRunner(stream=stderr,verbosity=2).run(unittest.TestSuite(cls(n) for n in names))
    report={'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'methods':names,
            'all_observed_primary_roots_removed':all(not p.exists() for p in roots),'observed_primary_roots':len(roots),
            'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    emit(output/'tests.json',report);print(json.dumps({'result':report['result'],'tests':report['tests_run'],'errors':report['errors'],'failures':report['failures']}),flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
