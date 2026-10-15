"""Ordered task-local checks, immutable input selections, no runtime authority."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[6]
COMPONENT = ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def clock(): return datetime.now(timezone.utc).isoformat()
def save(path, value):
    if path.exists(): raise RuntimeError('attempt evidence already exists')
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def environment():
    import jsonschema, cryptography, referencing
    packages = ['attrs','cffi','cryptography','jsonschema','jsonschema-specifications',
                'pycparser','referencing','rpds-py']
    return {'python_version':sys.version.split()[0], 'interpreter_path':sys.executable,
        'interpreter_sha256':sha(Path(sys.executable)), 'prefix':sys.prefix,
        'packages':{p:importlib.metadata.version(p) for p in packages},
        'module_origins':{m.__name__:str(Path(m.__file__).resolve())
                          for m in (jsonschema,cryptography,referencing)},
        'stdlib_origin':str(Path(json.__file__).resolve())}

def input_rows():
    paths = {p for p in COMPONENT.iterdir() if p.is_file()}
    context = json.loads((RUN/'context.json').read_text())
    paths.update(ROOT/r['path'] for r in context['selected_sources'])
    # Include all original registry carrier inputs and transitive schema sources
    # in advance. A successful small fixture case does not imply all carriers
    # were exercised, but it cannot import unbound original bytes.
    registry = json.loads((ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json').read_text())
    for c in registry['admitted_contracts']:
        paths.add(ROOT/c['artifact_path']); paths.add(ROOT/c['schema_path'])
    paths.update((ROOT/'authority/artifact-types').rglob('schema.json'))
    paths.update(ROOT/p for p in [
        'authority/artifact-types/definition/v2/fixtures/valid/definition.json',
        'authority/artifact-types/definition/v1/fixtures/valid/definition.json',
        'authority/owners/foundation-01/v1/owners.json',
        'authority/artifact-types/governed-model/v1/fixtures/valid/record.json',
        'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json',
        'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'])
    relation_registry=json.loads((ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json').read_text())
    paths.update(ROOT/r['instance_path'] for r in relation_registry['entries'])
    paths.add(Path(__file__).resolve())
    return [{'path':str(p.relative_to(ROOT)), 'sha256':sha(p), 'size':p.stat().st_size}
            for p in sorted(paths)]

class Result(unittest.TextTestResult):
    def __init__(self,*args,**kw): super().__init__(*args,**kw); self.observations=[]
    def startTest(self,test): self.started=time.monotonic(); super().startTest(test)
    def observe(self,test,status): self.observations.append({'test':test.id(),'status':status,'elapsed_seconds':time.monotonic()-self.started})
    def addSuccess(self,test): self.observe(test,'PASS');super().addSuccess(test)
    def addFailure(self,test,err): self.observe(test,'FAIL');super().addFailure(test,err)
    def addError(self,test,err): self.observe(test,'ERROR');super().addError(test,err)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);a=parser.parse_args()
    prefix=RUN/a.attempt; start=clock(); before=environment(); rows=input_rows()
    need_versions={'attrs':'25.4.0','cffi':'2.0.0','cryptography':'46.0.5','jsonschema':'4.23.0','jsonschema-specifications':'2023.12.1','pycparser':'2.23','referencing':'0.36.2','rpds-py':'0.27.1'}
    if before['python_version']!='3.14.4' or before['packages']!=need_versions or before['interpreter_sha256']!='52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41':raise RuntimeError('independent selected environment differs')
    selection={'started_at':start,'environment':before,'inputs':rows,'authority_effect':'none','scope':'owned technical component tests; no API or native engine qualification'}
    save(prefix.with_suffix('.selection.json'),selection)
    sys.path.insert(0,str(COMPONENT));import test_inputs
    checkpoints=[]
    with prefix.with_suffix('.terminal.txt').open('x') as stream:
        for label,klass in [('protected-reader',test_inputs.ReaderCases),('semantic-graph',test_inputs.GraphCases)]:
            result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromTestCase(klass))
            checkpoints.append({'checkpoint':label,'tests_run':result.testsRun,'successful':result.wasSuccessful(),'observations':result.observations})
            stream.flush()
            if not result.wasSuccessful():break
    after=environment();same_inputs=all(sha(ROOT/r['path'])==r['sha256'] for r in rows)
    scratch_clean=not list(RUN.glob('owned-reader-*')) and not list(RUN.glob('owned-graph-*'))
    passed=all(c['successful'] for c in checkpoints) and len(checkpoints)==2 and after==before and same_inputs and scratch_clean
    save(prefix.with_suffix('.json'),{'started_at':start,'finished_at':clock(),'status':'PASS' if passed else 'FAIL','checkpoints':checkpoints,'environment_before':before,'environment_after':after,'selected_inputs_unchanged':same_inputs,'owned_scratch_cleaned':scratch_clean,'authority_effect':'none','full_original_history_qualification':False,'api17_integration':False,'task_complete':False})
    print(json.dumps({'status':'PASS' if passed else 'FAIL','tests':sum(c['tests_run'] for c in checkpoints),'report':str(prefix.with_suffix('.json'))}))
    return 0 if passed else 1

if __name__=='__main__':sys.exit(main())
