"""Execute every declared E04 control using its exact isolated fixture assertions."""
import ast
import copy
import hashlib
import importlib
import json
import sys
import time
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(HERE))
REGISTRY=HERE/'hostile-cases.json'
MODULES={'test_A01':'InputControls','test_A05':'RelationControls','test_C01':'TypeControls','test_P02':'FiniteControls','test_E02':'PublicationControls','test_A09':'ReplayTests','test_E03':{'DenotationControls','SelectionControls'}}
CATEGORIES={'schema','types','relations','search','witness','denominator','publication','records'}
KEYS={'schema_version','authority_effect','semantic_ready','unit','categories','cases','declared_case_count','preserved_delivery_manifest_ref','claim_ceiling','fixture_reuse','goal_status'}
ROW_KEYS={'case_id','category','module','class','method','source_ref','method_sha256','source_line','named_cause','expected_literal_checks','fixture_assertion_contract','mutation_boundary','expected_test_outcome'}
class ManifestFault(ValueError):pass

def require(condition,message):
 if not condition:raise ManifestFault(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def unique(pairs):
 result={}
 for key,value in pairs:
  require(key not in result,'duplicate-json-key');result[key]=value
 return result

def read():return json.loads(REGISTRY.read_bytes(),object_pairs_hook=unique)
def validate(value):
 require(type(value) is dict and set(value)==KEYS,'closed-registry-fields')
 require(value['schema_version']=='definition-assurance-hostile-controls/v1-candidate' and value['unit']=='E04.1','registry-profile')
 require(value['authority_effect']=='none' and value['semantic_ready'] is False and value['goal_status']=='active','claim-boundary')
 require(type(value['declared_case_count']) is int and value['declared_case_count']==76,'selected-case-count')
 require(type(value['cases']) is list and len(value['cases'])==76,'case-denominator')
 require(value['categories']==sorted(CATEGORIES),'category-denominator')
 identities=set();methods=set();cache={}
 for row in value['cases']:
  require(type(row) is dict and set(row)==ROW_KEYS,'closed-case-fields')
  require(row['case_id']==f'E04-{len(identities)+1:03d}' and row['case_id'] not in identities,'case-identity');identities.add(row['case_id'])
  require(row['category'] in CATEGORIES and row['module'] in MODULES,'case-route')
  classes=MODULES[row['module']];require(row['class'] in ({classes} if isinstance(classes,str) else classes),'case-class')
  require(type(row['method']) is str and row['method'].startswith('test_'),'case-method')
  identity=(row['module'],row['class'],row['method']);require(identity not in methods,'duplicate-case-method');methods.add(identity)
  path=HERE/(row['module']+'.py');raw=path.read_bytes()
  require(row['source_ref']=={'path':path.relative_to(ROOT).as_posix(),'sha256':digest(raw)},'source-binding')
  if path not in cache:cache[path]=(raw.decode(),ast.parse(raw))
  text,tree=cache[path];cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==row['class']),None)
  require(cls is not None,'missing-case-class');node=next((n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==row['method']),None);require(node is not None,'missing-case-method')
  code=ast.get_source_segment(text,node)
  require(code==row['fixture_assertion_contract'] and digest(code.encode())==row['method_sha256'] and type(row['source_line']) is int and row['source_line']==node.lineno,'method-binding')
  literals={n.value for n in ast.walk(node) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
  require(type(row['expected_literal_checks']) is list and all(type(x) is str and x in literals for x in row['expected_literal_checks']),'assertion-cause-binding')
  require(row['expected_test_outcome']=='pass-with-no-skips-errors-or-unexpected-success','case-outcome-contract')
 require({r['category'] for r in value['cases']}==CATEGORIES,'category-coverage')
 ref=value['preserved_delivery_manifest_ref'];require(type(ref) is dict and set(ref)=={'path','sha256'},'delivery-ref')
 require(ref['path']=='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A10/delivery-manifest.json','delivery-path')
 require(digest((ROOT/ref['path']).read_bytes())==ref['sha256'],'delivery-manifest-binding')
 return value

def preserved(value):
 document=json.loads((ROOT/value['preserved_delivery_manifest_ref']['path']).read_bytes())
 for row in document['files']:require(digest((ROOT/row['path']).read_bytes())==row['sha256'],'preserved-input-changed:'+row['path'])
 return len(document['files'])

class HostileControls(unittest.TestCase):
 def test_registry_is_exact_closed_and_source_bound(self):
  value=validate(read());self.assertEqual(76,len(value['cases']));self.assertEqual(506,preserved(value))
 def test_registry_cannot_omit_duplicate_reroute_or_forge_controls(self):
  original=read()
  mutations=[('omit',lambda v:v['cases'].pop()),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('unknown-field',lambda v:v.update(ignored=True)),('reroute',lambda v:v['cases'][0].update(module='os')),('forged-method',lambda v:v['cases'][0].update(method='test_missing')),('forged-source',lambda v:v['cases'][0]['source_ref'].update(sha256='0'*64)),('forged-cause',lambda v:v['cases'][0].update(expected_literal_checks=['invented-result'])),('promotion',lambda v:v.update(semantic_ready=True)),('boolean-count',lambda v:v.update(declared_case_count=True))]
  for name,mutate in mutations:
   with self.subTest(mutation=name):
    value=copy.deepcopy(original);mutate(value)
    with self.assertRaises(ManifestFault):validate(value)
  with self.assertRaises(ManifestFault):json.loads('{"cases":[],"cases":[]}',object_pairs_hook=unique)
 def test_every_declared_control_runs_without_skipping_and_preserves_inputs(self):
  value=validate(read());before=preserved(value);reports=[];started=time.monotonic()
  for row in value['cases']:
   with self.subTest(case_id=row['case_id'],cause=row['named_cause']):
    module=importlib.import_module(row['module']);test=getattr(module,row['class'])(row['method']);result=unittest.TestResult();case_started=time.monotonic();unittest.TestSuite([test]).run(result)
    observation={'case_id':row['case_id'],'category':row['category'],'fixture_id':test.id(),'outcome':'PASS' if result.wasSuccessful() and not result.skipped and not result.unexpectedSuccesses and result.testsRun==1 else 'FAIL','tests_run':result.testsRun,'skipped':len(result.skipped),'errors':len(result.errors),'failures':len(result.failures),'unexpected_successes':len(result.unexpectedSuccesses),'expected_failures':len(result.expectedFailures),'elapsed_seconds':round(time.monotonic()-case_started,6),'method_sha256':row['method_sha256']};reports.append(observation)
    self.assertEqual(1,result.testsRun);self.assertFalse(result.skipped);self.assertFalse(result.unexpectedSuccesses);self.assertFalse(result.expectedFailures);self.assertFalse(result.errors+result.failures,str(result.errors+result.failures))
  after=preserved(value)
  self.assertEqual(before,after);self.assertEqual([r['case_id'] for r in value['cases']],[r['case_id'] for r in reports]);self.assertEqual(76,sum(r['outcome']=='PASS' for r in reports))
  print('E04_CONTROL_RESULTS='+json.dumps({'registry_sha256':digest(REGISTRY.read_bytes()),'declared_case_count':76,'executed_case_count':len(reports),'cases':reports,'preserved_prior_files':after,'elapsed_seconds':round(time.monotonic()-started,6),'authority_effect':'none','semantic_ready':False,'claim_ceiling':value['claim_ceiling']},sort_keys=True),flush=True)

if __name__=='__main__':unittest.main()
