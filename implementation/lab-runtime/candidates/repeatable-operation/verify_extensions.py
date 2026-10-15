#!/usr/bin/env python3
"""Capture actual C14 checks, source-bound examples and immutable receipts."""
import base64,hashlib,io,json,platform,sys,time,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
sys.path.insert(0,str(PACKAGE/'tests'))
import test_extensions,test_bound_extensions
started=time.perf_counter();suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(test_extensions.ExtensionTests),unittest.defaultTestLoader.loadTestsFromTestCase(test_bound_extensions.BoundExtensionTests)])
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
coverage=json.loads((PACKAGE/'design/extension-rule-coverage.json').read_text());definition=json.loads((ROOT/coverage['definition_path']).read_text())
assert len(coverage['coverage'])==len(definition['voices']['scientific_formal']['testable_conditions'])==12
names={name for cls in [test_extensions.ExtensionTests,test_bound_extensions.BoundExtensionTests] for name in unittest.defaultTestLoader.getTestCaseNames(cls)}
assert all(name in names for row in coverage['coverage'] for name in row['tests'])
Draft202012Validator.check_schema(json.loads((PACKAGE/'schemas/extension-evidence.schema.json').read_text()))
directory=PACKAGE/'receipts/C14';directory.mkdir(exist_ok=True);index=1
while (directory/f'{index:04d}.json').exists():index+=1
log=directory/f'{index:04d}.log';log.write_text(stream.getvalue())
example_files=[]
if result.wasSuccessful():
 fixture=test_bound_extensions.BoundExtensionTests();fixture.setUp();inspection=fixture.inspect()
 folder=PACKAGE/f'examples/typed-extension/{index:04d}';folder.mkdir(parents=True)
 values={'proposal.json':fixture.p,'inspection.json':inspection,'evidence-bundle.json':{'authority_effect':'none','fixture_values_only':True,'source_profile_sha256':fixture.profile_sha,'source_snapshot_digest':fixture.snapshot_digest,'source_cut':fixture.snapshot['expected_cut'],'candidate_bytes':{k:base64.b64encode(v).decode() for k,v in fixture.evidence.items()},'scope':'Existing acts-for pair and source-bound comparison examples; not an actual proposed effective extension or instance.'}}
 for name,value in values.items():
  file=folder/name;file.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');example_files.append(file)
files=[Path(__file__).resolve(),PACKAGE/'lab_runtime/extensions.py',PACKAGE/'tests/test_extensions.py',PACKAGE/'tests/test_bound_extensions.py',PACKAGE/'design/extension-rule-coverage.json',PACKAGE/'design/extension-contract.md',PACKAGE/'schemas/extension-evidence.schema.json']+example_files+list((PACKAGE/'profiles').rglob('*.json'))
receipt={'schema_version':'lab-extension-check/v1-candidate','task':'C14','result':'PASS' if result.wasSuccessful() and result.testsRun==29 else 'FLAG','authority_effect':'none','tests':{'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},'duration_seconds':time.perf_counter()-started,'definition_conditions_covered':12,'effective_kind_comparison_inventory':41,'semantic_owner_outcome':None,'semantic_verdict':'not-issued-by-validator','wire_adapter_integration':'S01/API integration required','globally_available_pairs_added':0,'relation_instances_created':0,'environment':{'python':sys.version,'platform':platform.platform()},'log_binding':{'path':log.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()},'files':[{'path':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(files)],'definition_binding':{'path':coverage['definition_path'],'sha256':hashlib.sha256((ROOT/coverage['definition_path']).read_bytes()).hexdigest()},'scope':'Candidate structural extension inspector, complete selected-question comparison preparation, closed pair/domain checks and real D75 input binding. Actual semantic review/admission and instance creation remain separate.'}
path=directory/f'{index:04d}.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':receipt['result'],'tests':receipt['tests'],'duration_seconds':receipt['duration_seconds'],'receipt':path.relative_to(ROOT).as_posix(),'authority_effect':'none'}),flush=True)
sys.exit(0 if receipt['result']=='PASS' else 1)
