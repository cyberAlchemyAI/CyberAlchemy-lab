"""Seal E04 only from actual complete hostile-control execution and preserved bytes."""
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6]
BASE=UNIT.parents[1];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL/'tests'));import test_E04 as checks

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def bound(row):
 if ref(ROOT/row['path'])!=row:raise ValueError('Stale binding: '+row['path'])
def put(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def main():
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:bound(row)
 for name in ['E03','A09']:
  receipt=json.loads((BASE/f'units/{name}/receipt.json').read_bytes())
  for row in receipt['inputs']+receipt['outputs']:bound(row)
 registry=checks.validate(checks.read());prior=checks.preserved(registry)
 attempts=sorted(UNIT.glob('run-*/result.json'));assert attempts
 selected=attempts[-1];result=json.loads(selected.read_bytes());report=result['control_results']
 if result['result']!='PASS' or result['return_code']!=0 or report is None:raise ValueError('Actual passing execution required')
 for key in ['stdout_ref','stderr_ref']:bound(result[key])
 stdout=(ROOT/result['stdout_ref']['path']).read_text();rows=[json.loads(x.split('=',1)[1]) for x in stdout.splitlines() if x.startswith('E04_CONTROL_RESULTS=')]
 if rows!=[report]:raise ValueError('Retained report/log substitution')
 if report['registry_sha256']!=ref(checks.REGISTRY)['sha256'] or report['declared_case_count']!=76 or report['executed_case_count']!=76 or report['preserved_prior_files']!=prior:raise ValueError('Execution denominator substitution')
 if [x['case_id'] for x in report['cases']]!=[x['case_id'] for x in registry['cases']]:raise ValueError('Missing or duplicated executed controls')
 for actual,expected in zip(report['cases'],registry['cases']):
  if actual['outcome']!='PASS' or actual['method_sha256']!=expected['method_sha256'] or actual['tests_run']!=1 or any(actual[k] for k in ['skipped','errors','failures','expected_failures','unexpected_successes']):raise ValueError('Incomplete control outcome')
 spec=importlib.util.spec_from_file_location('E04_source_binding',BASE/'units/A07/pilot_spec.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);source=p.bind_sources(json.loads((BASE/'pilot-v2/interpretation.json').read_bytes()),ROOT)
 counts=dict(sorted(collections.Counter(row['category'] for row in registry['cases']).items()))
 episode={'authority_effect':'none','goal_status':'active','new_candidate_unit':'E04.1','current_definitions':183,'admitted_source_versions':189,'partial_interpretations':7,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'owner_fidelity':'pending','executed_hostile_fixture_methods':76,'case_categories':counts,'source_capture_check':source,'prior_candidate_files_preserved':prior,'next_ready_unit':'I01.1','remaining':'Transitive invalidation, regeneration, regression, CLI/revision workflow, family translations, global logical assurance, owner fidelity and complete episode review remain required.'}
 put(UNIT/'episode-status.json',episode)
 outputs=[ref(path) for path in sorted(UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts]+[ref(checks.REGISTRY),ref(IMPL/'tests/test_E04.py')]
 receipt={'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'E04.1','authority_effect':'none','semantic_ready':False,'goal_status':'active','task_result':'PASS for all 76 declared exact fixture assertions and explicit claim boundaries','inputs':context['sources'],'outputs':outputs,'validation':{'command':result['command'],'actual_result_ref':ref(selected),'top_level_unittest_tests':3,'declared_and_executed_fixture_methods':76,'registry_negative_mutations':10,'category_counts':counts,'elapsed_control_seconds':report['elapsed_seconds'],'failures':0,'errors':0,'skips':0},'criterion_results':[{'criterion':'Exact-cause controls cover schemas, semantics, alias/subtype policy, witness verification, scope, source races and budgets','result':'PASS','evidence':'Closed byte-bound 76-member registry with complete fixture assertion contracts and eight categories; every member actually executed.'},{'criterion':'No malformed-input escape in the declared controls','result':'PASS for selected fixtures only','evidence':'Malformed requests, typed failures, unsupported extensions and unknown markers meet their exact fixture assertions; no universal claim.'},{'criterion':'All declared controls run without skipped obligations','result':'PASS','evidence':'Exact case identities/order matched actual report; no errors/failures/skips/expected failures/unexpected successes; registry rejects omission, duplication, reroute, forgery and readiness promotion.'},{'criterion':'Mutation is isolated and canonical/prior inputs preserved','result':'PASS','evidence':f'{prior} prior sealed files rehashed before/after; current captured source bytes verified; hostile changes confined to in-memory, private temporary or isolated copied fixtures.'}],'trust_and_limitations':['Existing exact fixture implementation and assertions are reused; E04 does not claim 76 new fixture implementations.','Per-method execution outcomes are retained; underlying native responses and nested mutations are specified in bound assertions rather than all serialized separately.','Selected controls are not exhaustive fuzzing or a soundness proof.','No source fidelity, semantic admission, whole-definition translation, universal proof or complete semantic closure is inferred.'],'source_binding_check':source,'prior_candidate_files_preserved':prior,'full_project_completion':'not-established','next_ready_unit':'I01.1'}
 put(UNIT/'receipt.json',receipt)
 files=[ref(path) for folder in [BASE,IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
 put(UNIT/'delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda row:row['path']),'claim_ceiling':'76 executed selected hostile fixture methods and preserved exact candidate bytes; no owner fidelity or full episode completion.'})
 print(json.dumps({'result':'PASS','executed_fixture_methods':76,'categories':counts,'candidate_files':len(files),'prior_candidate_files_preserved':prior,'source_capture_files':source['source_capture_files'],'goal_status':'active','next_ready_unit':'I01.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()
