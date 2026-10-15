"""Exactly two additive caller assertions; frozen original345 remains unchanged."""
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
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def require(value,message):
 if not value:raise ValueError(message)
def dump(node):return ast.dump(node,include_attributes=False)
def find(path,classname,method):
 tree=ast.parse(path.read_text())
 cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==classname)
 return next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name==method)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--profile',required=True);parser.add_argument('--caller-sha256',required=True);a=parser.parse_args()
 api=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12';output=RUN/'API12-supplemental-operation-counts-0202.json';require(not output.exists(),'new exclusive supplemental report required')
 require(bind(Path(__file__).resolve())['sha256']==a.caller_sha256,'independently selected additive caller changed')
 require(bind(api/'source-manifest.json')['sha256']==a.source and bind(api/'contract-profile.json')['sha256']==a.profile,'explicit unchanged frozen API12 pins required')
 are=RUN/'ARE-supplemental-count-boundary-0188.json';receipt=json.loads(are.read_bytes());require(receipt['ok'] and receipt['authority_effect']=='none','exact non-authorizing supplement boundary required')
 spec=importlib.util.spec_from_file_location('_cal_supplement0202_guard',api/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(a.source)
 name='_cal_api12_supplement0202';spec=importlib.util.spec_from_file_location(name,api/'__init__.py',submodule_search_locations=[str(api)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 P=__import__(name+'.protocol',fromlist=['*']);CC=__import__(name+'.test_current_controls',fromlist=['*']);CS=__import__(name+'.test_custody_sessions',fromlist=['*'])
 # Only independently selected fixture pin globals are supplied. Original
 # class methods, production code, callbacks and clocks are not replaced.
 CC.SOURCE=a.source;CC.PROFILE=a.profile;CS.SOURCE=a.source;CS.PROFILE=a.profile
 global SUPPORTED,LEGACY_SUPPORTED,METADATA_SUPPORTED,EXPORT_SUPPORTED,D,HERE
 SUPPORTED=P.SUPPORTED;LEGACY_SUPPORTED=P.LEGACY_SUPPORTED;METADATA_SUPPORTED=P.METADATA_SUPPORTED;EXPORT_SUPPORTED=P.EXPORT_SUPPORTED;D=CC.D;HERE=P.HERE
 original_cc=CC.CurrentControls.test_03_exact_current_profile_and_protocol_controls;original_cs=CS.Sessions.test_30_current_handler_profile_retains_all_original_contracts
 class CorrectedCurrentControls(CC.CurrentControls):
  def test_03_exact_current_profile_and_protocol_controls(self):
   self.assertEqual(self.schemas.profile['implemented_operations'],list(SUPPORTED));self.assertEqual(len(SUPPORTED),34)
   self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(LEGACY_SUPPORTED),12)
   self.assertEqual(Path(D.API.__file__).resolve(),HERE.parent/'api-v25/protocol.py')
 class CorrectedCustodySessions(CS.Sessions):
  def test_30_current_handler_profile_retains_all_original_contracts(self):
   self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),34)
   self.assertEqual(len(LEGACY_SUPPORTED),12);self.assertEqual(len(METADATA_SUPPORTED),8);self.assertEqual(len(EXPORT_SUPPORTED),9)
   self.assertEqual(self.schemas.profile['actual_owner_outcome'],None);self.assertEqual(self.schemas.profile['authority_effect'],'none')
 caller_tree=ast.parse(Path(__file__).read_text());main_node=next(n for n in caller_tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');caller_classes={n.name:n for n in main_node.body if isinstance(n,ast.ClassDef)}
 corrections=[];original_files=[]
 for file,classname,method,newclass in [('test_current_controls.py','CurrentControls','test_03_exact_current_profile_and_protocol_controls','CorrectedCurrentControls'),('test_custody_sessions.py','Sessions','test_30_current_handler_profile_retains_all_original_contracts','CorrectedCustodySessions')]:
  old=find(api/file,classname,method);expected=copy.deepcopy(old);changes=[]
  for node in ast.walk(expected):
   if isinstance(node,ast.Constant) and type(node.value) is int and node.value==24:node.value=34;changes.append({'original':24,'new':34})
  new=next(n for n in caller_classes[newclass].body if isinstance(n,ast.FunctionDef) and n.name==method)
  require(len(changes)==1 and dump(expected)==dump(new),'supplement must differ by exactly one24->34 literal per original method')
  corrections.append({'original_method':file+':'+classname+'.'+method,'additive_class':newclass,'literal_delta':changes,'original_method_ast_sha256':hashlib.sha256(dump(old).encode()).hexdigest(),'additive_method_ast_sha256':hashlib.sha256(dump(new).encode()).hexdigest(),'all_other_method_AST_unchanged':True});original_files.append(bind(api/file))
 require(len(SUPPORTED)==34 and list(P.Schemas(a.profile).profile['implemented_operations'])==list(SUPPORTED),'actual original current profile/equality must declare34')
 cases=[];owned=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):
   super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
   root=getattr(test,'root',None)
   if isinstance(root,Path):owned.append({'root':str(root),'removed_after_original_cleanup':not root.exists()})
  def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
  def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
 suite=unittest.TestSuite([CorrectedCurrentControls('test_03_exact_current_profile_and_protocol_controls'),CorrectedCustodySessions('test_30_current_handler_profile_retains_all_original_contracts')]);started=datetime.now(timezone.utc).isoformat();result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
 exit_error=None
 try:
  guard.verify(a.source);require(CC.CurrentControls.test_03_exact_current_profile_and_protocol_controls is original_cc and CS.Sessions.test_30_current_handler_profile_retains_all_original_contracts is original_cs,'original function identity changed')
  for row in original_files:require(bind(ROOT/row['path'])==row,'frozen original test bytes changed')
  require(bind(Path(__file__))['sha256']==a.caller_sha256,'additive caller changed during execution')
 except Exception:exit_error=traceback.format_exc()
 cleanup=all(x['removed_after_original_cleanup'] for x in owned);passed=result.wasSuccessful() and result.testsRun==len(cases)==2 and exit_error is None and cleanup
 value={'schema_version':'lab-additive-API12-operation-count-supplement/v1-candidate','result':'PASS' if passed else 'FAIL','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'source_sha256':a.source,'profile_sha256':a.profile,'actual_supplemental_cases':result.testsRun,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),'precise_method_AST_deltas':corrections,'total_literal_changes':2,'original_functions_retained':True,'original_test_files_binding':original_files,'owned_fixture_cleanup':owned,'original_cleanup_completed':cleanup,'full_history_entry_exit_guards':exit_error is None,'exit_guard_error':exit_error,'actual_supported_count':len(SUPPORTED),'actual_schema_operation_count':len(CorrectedCurrentControls.schemas.operations),'actual_profile_declared_operations':CorrectedCurrentControls.schemas.profile['implemented_operations'],'actual_profile_equals_original_SUPPORTED':CorrectedCurrentControls.schemas.profile['implemented_operations']==list(SUPPORTED),'files':[bind(api/'source-manifest.json'),bind(api/'contract-profile.json'),bind(Path(__file__))],'are_boundary_binding':bind(are),'original345_regression_replaced':False,'original_regression_failures_preserved':True,'test_method_or_production_monkeypatches':False,'original_clocks_or_callbacks_changed':False,'task_complete':False,'whole_API_qualified':False,'goal_complete':False,'actual_owner_outcome':None,'authority_effect':'none','claim_ceiling':'Exactly two additive caller cardinality assertions against unchanged API12, with original equality/origin/subset/authority assertions and inherited real fixtures/cleanup. Does not make the original345 regression pass or close R03/human/R08/wholeLab obligations.'}
 with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':value['result'],'actual_supplemental_cases':result.testsRun,'literal_changes':2,'report_binding':bind(output),'whole_API_qualified':False}),flush=True);return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
