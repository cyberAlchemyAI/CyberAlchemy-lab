"""One additive original-byte witness check; only obsolete selector is changed."""
import argparse
import ast
import copy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
import unittest

sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
OLD='product:cyberalchemy-lab@current-episode-0003.candidate.1'
NEW='product:cyberalchemy-lab@current-episode-0004.candidate.1'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def require(value,message):
 if not value:raise ValueError(message)
def dump(n):return ast.dump(n,include_attributes=False)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--profile',required=True);parser.add_argument('--caller-sha256',required=True);a=parser.parse_args()
 api=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12';output=RUN/'API12-supplemental-product-witness-0203.json';require(not output.exists(),'new exclusive witness supplement required')
 require(bind(Path(__file__))['sha256']==a.caller_sha256,'independently pinned supplemental caller changed')
 require(bind(api/'source-manifest.json')['sha256']==a.source and bind(api/'contract-profile.json')['sha256']==a.profile,'exact unchanged API12 producer required')
 are=RUN/'ARE-supplemental-witness-boundary-0191.json';authority=json.loads(are.read_bytes());require(authority['ok'] and authority['authority_effect']=='none','exact non-authorizing witness boundary required')
 original_path=api/'test_custody_api.py';original_binding=bind(original_path);tree=ast.parse(original_path.read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='OriginalAPI');old=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='test_04_actual_product_revision_witness');expected=copy.deepcopy(old);deltas=[]
 for n in ast.walk(expected):
  if isinstance(n,ast.Constant) and n.value==OLD:n.value=NEW;deltas.append({'old':OLD,'new':NEW})
 require(len(deltas)==1,'exact one original obsolete product selector required')
 spec=importlib.util.spec_from_file_location('_cal_supplement0203_guard',api/'guard.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G);G.verify(a.source)
 name='_cal_api12_supplement0203';spec=importlib.util.spec_from_file_location(name,api/'__init__.py',submodule_search_locations=[str(api)]);package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 P=__import__(name+'.protocol',fromlist=['*']);T=__import__(name+'.test_custody_api',fromlist=['*']);T.SOURCE=a.source;T.PROFILE=a.profile
 global model,call,cut
 model=T.model;call=T.call;cut=T.cut
 original_method=T.OriginalAPI.test_04_actual_product_revision_witness
 class CorrectedProductWitness(T.OriginalAPI):
  def test_04_actual_product_revision_witness(self):
   subject=self.view.subjects['product:cyberalchemy-lab@current-episode-0004.candidate.1'];header=model.artifact_ref(self.view,subject)
   self.assertNotEqual(header['version_ref'].rsplit('@',1)[1],subject['record']['version'])
   result=self.success(call(self.channel.context,'artifact.inspect',cut(self.view),artifact=header,include=['body','contract','authority','provenance','gaps']))
   self.assertEqual(result['envelope']['artifact'],header);self.assertEqual(result['envelope']['decoded_artifact']['body'],subject['record'])
   self.assertEqual(result['envelope']['content']['byte_sha256'],subject['source']['sha256'])
 caller=ast.parse(Path(__file__).read_text());main_node=next(x for x in caller.body if isinstance(x,ast.FunctionDef) and x.name=='main');newclass=next(x for x in main_node.body if isinstance(x,ast.ClassDef) and x.name=='CorrectedProductWitness');new=next(x for x in newclass.body if isinstance(x,ast.FunctionDef))
 require(dump(expected)==dump(new),'every original witness/inspection/assertion AST must remain identical except selected revision')
 cases=[];observations=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):
   super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'});subject=test.view.subjects[NEW];header=model.artifact_ref(test.view,subject)
   observations.append({'old_selector_present':OLD in test.view.subjects,'actual_selected_artifact':header,'record_body_version':subject['record']['version'],'version_ref_differs_from_body_version':header['version_ref'].rsplit('@',1)[1]!=subject['record']['version'],'original_content_sha256':subject['source']['sha256'],'owned_fixture_root':str(test.root),'owned_root_removed_after_original_cleanup':not test.root.exists()})
  def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
  def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
 started=datetime.now(timezone.utc).isoformat();result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.TestSuite([CorrectedProductWitness('test_04_actual_product_revision_witness')]))
 exit_error=None
 try:G.verify(a.source);require(T.OriginalAPI.test_04_actual_product_revision_witness is original_method and bind(original_path)==original_binding,'original method/file changed');require(bind(Path(__file__))['sha256']==a.caller_sha256,'supplement caller changed')
 except Exception:exit_error=traceback.format_exc()
 cleanup=bool(observations) and all(x['owned_root_removed_after_original_cleanup'] for x in observations);passed=result.wasSuccessful() and result.testsRun==len(cases)==1 and cleanup and exit_error is None
 value={'schema_version':'lab-additive-API12-product-selector-supplement/v1-candidate','result':'PASS' if passed else 'FAIL','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'source_sha256':a.source,'profile_sha256':a.profile,'actual_supplemental_cases':result.testsRun,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),'literal_delta':deltas,'total_literal_changes':1,'all_other_original_method_AST_unchanged':True,'original_method_ast_sha256':hashlib.sha256(dump(old).encode()).hexdigest(),'additive_method_ast_sha256':hashlib.sha256(dump(new).encode()).hexdigest(),'actual_source5_observations':observations,'full_history_entry_exit_guards':exit_error is None,'exit_guard_error':exit_error,'original_cleanup_completed':cleanup,'original_function_identity_retained':True,'original_test_binding':original_binding,'files':[bind(api/'source-manifest.json'),bind(api/'contract-profile.json'),bind(Path(__file__))],'are_boundary_binding':bind(are),'actual_authenticated_public_calls':1 if observations else 0,'original345_regression_replaced':False,'original_regression_failures_preserved':True,'test_method_or_production_monkeypatches':False,'original_clocks_or_callbacks_changed':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Exactly one supplemental currentSource5 product selector, retaining original revision/body-version inequality, actual authenticated artifact.inspect and exact artifact/body/content-SHA assertions with unchanged inherited fixture/cleanup. Original missing-episode3 failure and345 regression remain unchanged; no full API, human or R08 closure.'}
 with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':value['result'],'actual_supplemental_cases':result.testsRun,'literal_changes':1,'report_binding':bind(output),'whole_API_qualified':False}),flush=True);return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
