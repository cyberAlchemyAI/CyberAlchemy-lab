"""Whole-theory controls: pairwise compatibility, joint populations and independent truth."""
import copy
import json
import sys
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(HERE),str(HERE/'tests')]
import regression as x
import test_I02 as fixtures
import test_A01 as core_fixture
TRUE={'op':'and','args':[]};FALSE={'op':'or','args':[]}
def pred(name,nullary=False):return {'op':'pred','name':name,'args':[] if nullary else [{'op':'var','name':'x'}]}
def neg(arg):return {'op':'not','arg':arg}
def quant(op,body):return {'op':op,'sort':'Object','var':'x','body':body}

class WholeTheoryControls(unittest.TestCase):
 data=fixtures.RevisionControls.data
 change=fixtures.RevisionControls.change
 def setUp(self):fixtures.RevisionControls.setUp(self);self.revision=self.selection
 def configure(self,statements=(),nullary=False,one_source=False,clause=TRUE,roles=None,assumptions=None,ir_populations=None,cards=2):
  theory=self.data('theory');theory['statements']=list(statements)
  if one_source:
   theory['sources']=theory['sources'][:1]
  if nullary:
   for declaration in theory['declarations']:
    if declaration['kind']=='predicate':declaration['argument_sorts']=[]
   self.change('populations',[]);self.change('relations',[]);self.change('bindings',{})
  elif one_source:
   self.change('relations',[]);bindings=self.data('bindings');bindings['right']['source']=theory['sources'][0];self.change('bindings',bindings)
  self.change('theory',theory)
  originals=[];owners={}
  for n,source in enumerate(theory['sources']):
   core=core_fixture.payloads()['interpretation'];core.update(source=source,scope=theory['scope'],interpretation_id='I'+str(n))
   names=['P','Q'] if one_source else [['P'],['Q']][n]
   core['declarations']=[copy.deepcopy(declaration) for declaration in theory['declarations'] if declaration['kind']=='sort' or declaration['symbol_id'] in names]
   core['clauses'][0].update(formal_statement=copy.deepcopy(clause),roles=roles or ['definition'])
   if clause is None:core['clauses'][0]['disposition']='deferred'
   core['assumptions']=copy.deepcopy(assumptions or []);core['populations']=copy.deepcopy(ir_populations or [])
   original=x.ir.compile_interpretation(core);originals.append(original)
   for name in names:owners[name]=source
  aligns=[] if one_source else self.bundle['coupling_refs'];subject=x.ir.compose(originals,aligns,self.root)
  names={name:x.ir.qualified(source,theory['scope'],name) for name,source in owners.items()};names['Object']=subject['sort_alignment'][x.ir.qualified(theory['sources'][0],theory['scope'],'Object')]
  renaming=[{'local_symbol_id':name,'canonical_id':names[name],'source':theory['sources'][0] if name=='Object' else owners[name]} for name in ['Object','P','Q']]
  self.names=names;self.originals=originals;self.subject=subject
  self.request={'schema_version':'definition-assurance-regression-selection/v1-candidate','authority_effect':'none','revision_selection_ref':self.put('regression/revision.json',self.revision),'revision_result_ref':self.put('regression/requirements.json',x.d.generate(self.root,self.revision)),'input_ir_refs':[self.put('regression/input-'+str(n)+'.json',original) for n,original in enumerate(originals)],'alignment_refs':aligns,'renaming_ref':self.put('regression/renaming.json',renaming),'cardinalities_ref':self.put('regression/cards.json',{names['Object']:cards}),'profile_ref':self.put('regression/profile.json',json.loads(x.f.POLICY_PATH.read_bytes())),'toolchain_ref':self.put('regression/toolchain.json',{'bindings':x.f.current_bindings()}),'budgets':{},'scope_policy':'selected-inputs-only'}
  return self.request
 def run_check(self,**kwargs):return x.run(self.root,self.request,**kwargs)
 def unresolved(self,out,code=None):
  self.assertEqual('regression-unresolved',out['status'],out);self.assertEqual([],out['results']);self.assertFalse(out['semantic_ready'])
  if code:self.assertEqual(code,out['diagnostics'][0]['code'])
 def test_three_pairwise_satisfiable_constraints_fail_together(self):
  p,q=pred('P',True),pred('Q',True);constraints=[{'op':'or','args':[p,q]},{'op':'or','args':[neg(p),q]},neg(q)]
  for pair in combinations(constraints,2):
   self.configure(pair,nullary=True,one_source=True);out=self.run_check();self.assertEqual('selected-existential-regression-checked',out['status'],out);self.assertEqual(2,len(out['results']))
  self.configure(constraints,nullary=True,one_source=True);out=self.run_check();self.assertEqual('finite-scope-regression-failed',out['status']);self.assertEqual('bounded-no-theory-model',out['results'][0]['native_result']['status']);self.assertEqual('blocked-by-global-prerequisites',out['results'][1]['status']);self.assertIsNone(out['unbounded_conclusion'])
 def test_individually_inhabited_predicates_cannot_substitute_for_joint_population(self):
  p,q=pred('P'),pred('Q');T=[{'op':'or','args':[quant('forall',p),quant('forall',q)]},quant('forall',neg({'op':'and','args':[p,q]}))]
  self.configure(T,one_source=True,cards=1);prepared=x.prepare(self.root,self.request)
  for population in prepared['I']:
   native=x.f.search(prepared['subject'],prepared['T'],[population],TRUE,prepared['cards'],selected_inputs=prepared['originals'],snapshot=prepared['snapshot'],live_root=self.root)
   self.assertEqual('witness-found',native['status']);checked=x.v.witness(prepared['subject'],native,prepared['T'],[population],TRUE,prepared['cards'],'witness',prepared['provider_bindings'],selected_inputs=prepared['originals'],root=self.root);self.assertEqual('checked-model-witness',checked['status'])
  out=self.run_check();self.assertEqual('independently-checked-witness',out['results'][0]['status']);self.assertEqual('bounded-no-admissible-model',out['results'][1]['native_result']['status']);self.assertTrue(all(row['status']=='blocked-by-global-prerequisites' for row in out['results'][2:]));self.assertEqual(len(prepared['queries']),len(out['results']))
 def test_all_included_definition_clauses_are_conjoined(self):
  self.configure(nullary=True,one_source=True,clause=FALSE);out=self.run_check();self.assertEqual('finite-scope-regression-failed',out['status']);self.assertEqual([FALSE],out['joint_theory_statements']);self.assertEqual('included-in-joint-theory',out['clause_accounts'][0]['disposition'])
 def test_derived_claim_is_tested_after_consistency_and_not_assumed(self):
  self.configure(nullary=True,one_source=True,clause=FALSE,roles=['proof-obligation']);out=self.run_check();self.assertEqual([],out['joint_theory_statements']);self.assertEqual('finite-scope-regression-failed',out['status']);self.assertTrue(all(row['status']=='independently-checked-witness' for row in out['results'][:2]));self.assertEqual('independently-checked-counterexample',out['results'][2]['status'])
 def test_tautological_claim_remains_pending_without_unbounded_kernel_proof(self):
  self.configure(nullary=True,one_source=True,roles=['derived-claim']);out=self.run_check();self.assertEqual('universal-evidence-pending',out['status']);self.assertEqual('reported-bounded-no-counterexample-unverified',out['results'][2]['status']);self.assertFalse(out['mechanized_proof']);self.assertIsNone(out['unbounded_conclusion'])
 def test_selected_assumption_is_included_and_unselected_assumption_is_recorded(self):
  assumption=core_fixture.payloads()['assumption'];assumption.update(statement=FALSE,selected=True)
  self.configure(nullary=True,one_source=True,assumptions=[assumption]);out=self.run_check();self.assertEqual('finite-scope-regression-failed',out['status']);self.assertIn(FALSE,out['joint_theory_statements'])
  assumption['selected']=False;self.configure(nullary=True,one_source=True,assumptions=[assumption]);out=self.run_check();self.assertEqual('selected-existential-regression-checked',out['status']);self.assertFalse(out['assumption_accounts'][0]['selected'])
 def test_interpretation_required_population_cannot_be_omitted_from_joint_check(self):
  pop=core_fixture.payloads()['population'];pop.update(requirement='required',statement=FALSE)
  self.configure(one_source=True,ir_populations=[pop]);out=self.run_check();self.assertEqual('bounded-no-admissible-model',out['results'][1]['native_result']['status']);self.assertEqual(5,len(out['required_query_ids']));self.assertIn(FALSE,out['joint_population_statements'])
 def test_ambiguous_claim_premise_roles_cannot_assume_the_proof_target(self):
  self.configure(nullary=True,one_source=True,roles=['definition','proof-obligation']);self.unresolved(self.run_check(),'ambiguous-assumed-and-claim-clause-role')
 def test_pending_clause_and_missing_global_definition_stay_visible(self):
  self.configure(nullary=True,one_source=True,clause=None);out=self.run_check();self.assertEqual('selected-existential-regression-checked',out['status']);self.assertEqual(['DEF-B'],out['coverage']['missing_current_interpretations']);self.assertEqual(1,len(out['coverage']['pending_source_clauses']));self.assertEqual('pending',out['source_fidelity']);self.assertFalse(out['semantic_ready'])
 def test_all_current_scope_never_reports_success_for_a_partial_selection(self):
  self.configure(nullary=True,one_source=True);self.request['scope_policy']='all-current-required';out=self.run_check();self.assertEqual('all-current-regression-unresolved',out['status']);self.assertEqual('selected-existential-regression-checked',out['selected_scope_status'])
 def test_alias_target_is_not_promoted_after_bounded_no_counterexample(self):
  self.configure([quant('forall',{'op':'iff','left':pred('P'),'right':pred('Q')})]);out=self.run_check();self.assertEqual('universal-evidence-pending',out['status']);self.assertEqual('reported-bounded-no-counterexample-unverified',next(row for row in out['results'] if 'relation:' in row['obligation_id'])['status'])
 def test_local_alias_counterexample_is_checked_only_after_joint_witness(self):
  self.configure();out=self.run_check();self.assertEqual('finite-scope-regression-failed',out['status']);self.assertEqual('independently-checked-counterexample',next(row for row in out['results'] if 'relation:' in row['obligation_id'])['status']);self.assertTrue(all(row['status']=='independently-checked-witness' for row in out['results'][:2]))
 def test_missing_and_duplicate_interpretations_cannot_shrink_selected_theory(self):
  self.configure();original=copy.deepcopy(self.request['input_ir_refs'])
  for refs in [original[:1],original+[original[0]]]:
   self.request['input_ir_refs']=refs;self.unresolved(self.run_check())
 def test_wrong_nominal_source_cannot_borrow_the_other_predicate(self):
  self.configure();ref=self.request['renaming_ref'];rows=json.loads((self.root/ref['path']).read_bytes());rows[1]['source']=self.originals[1]['source'];self.request['renaming_ref']=self.put('regression/wrong-renaming.json',rows);self.unresolved(self.run_check())
 def test_forged_rehashed_ir_is_regenerated_and_rejected(self):
  self.configure();forged=copy.deepcopy(self.originals[0]);forged['clauses'][0]['formal_statement']=FALSE;forged['ir_sha256']=x.ir.digest({k:v for k,v in forged.items() if k!='ir_sha256'});self.request['input_ir_refs'][0]=self.put('regression/forged-ir.json',forged);self.unresolved(self.run_check())
 def test_stale_revision_result_cannot_remove_a_required_query(self):
  self.configure();ref=self.request['revision_result_ref'];value=json.loads((self.root/ref['path']).read_bytes());value['proposal_required_set']['logical_manifest']['obligations'].pop();self.request['revision_result_ref']=self.put('regression/forged-requirements.json',value);self.unresolved(self.run_check(),'stale-or-substituted-revision-requirements')
 def test_boolean_empty_and_extra_cardinalities_are_rejected(self):
  self.configure(nullary=True,one_source=True)
  for cards in [{self.names['Object']:True},{},{self.names['Object']:1,'unknown':1}]:
   self.request['cardinalities_ref']=self.put('regression/invalid-cards.json',cards);self.unresolved(self.run_check(),'malformed-regression-cardinalities')
 def test_profile_and_runtime_substitutions_are_rejected(self):
  self.configure(nullary=True,one_source=True);self.request['profile_ref']=self.put('regression/wrong-profile.json',{});self.unresolved(self.run_check(),'regression-profile-substitution')
  self.configure(nullary=True,one_source=True);self.request['toolchain_ref']=self.put('regression/wrong-runtime.json',{'bindings':[]});self.unresolved(self.run_check(),'regression-runtime-substitution')
 def test_cancellation_blocks_all_queries_without_logical_absence(self):
  self.configure(nullary=True,one_source=True);out=self.run_check(cancelled=lambda:True);self.assertEqual('regression-incomplete',out['status']);self.assertEqual('cancelled',out['results'][0]['native_result']['status']);self.assertEqual(2,len(out['results']))
 def test_provider_interpretation_limit_is_unknown_not_a_negative_result(self):
  self.configure([pred('P',True)],nullary=True,one_source=True);self.request['budgets']={'max_interpretations':1};out=self.run_check();self.assertEqual('regression-incomplete',out['status']);self.assertEqual('resource-limit',out['results'][0]['native_result']['status'])
 def test_output_limit_keeps_obligation_ids_and_clears_all_model_support(self):
  self.configure(nullary=True,one_source=True)
  with patch.object(x,'MAX_REPORT_BYTES',1):out=self.run_check()
  self.assertEqual('regression-resource-limit',out['status']);self.assertEqual(2,len(out['required_query_ids']));self.assertTrue(all(row['native_result'] is None and row['verification'] is None for row in out['results']))
 def test_snapshot_substitution_in_native_witness_is_rejected(self):
  self.configure(nullary=True,one_source=True);original=x.f.search
  def forged(*args,**kwargs):
   native=original(*args,**kwargs);native['input_bindings']['snapshot_sha256']='0'*64;return native
  with patch.object(x.f,'search',forged):self.unresolved(self.run_check(),'regression-native-snapshot-substitution')
 def test_independent_verifier_rejects_rehashed_false_population_model(self):
  self.configure(one_source=True);original=x.f.search
  def forged(*args,**kwargs):
   native=original(*args,**kwargs)
   if args[2] and native['witness'] is not None:
    native['witness']['model']['predicates'][self.names['P']]=[];native['witness']['model_sha256']=x.ir.digest(native['witness']['model'])
   return native
  with patch.object(x.f,'search',forged):self.unresolved(self.run_check(),'witness-fails-population')
 def test_input_closing_race_clears_previously_checked_models(self):
  self.configure(nullary=True,one_source=True);path=self.root/self.request['renaming_ref']['path'];self.unresolved(self.run_check(before_final_check=lambda:path.write_bytes(b'{}')),'revision-input-changed-during-check')
 def test_active_engine_closing_race_clears_model_support(self):
  self.configure(nullary=True,one_source=True);read=Path.read_bytes;changed=[False]
  def reading(path):return b'changed regression engine' if changed[0] and path==Path(x.__file__) else read(path)
  with patch.object(Path,'read_bytes',reading):self.unresolved(self.run_check(before_final_check=lambda:changed.__setitem__(0,True)),'regression-active-build-or-runtime-drift')
 def test_source_file_closing_race_has_no_current_model_support(self):
  self.configure(nullary=True,one_source=True);path=self.root/self.originals[0]['source']['path'];self.unresolved(self.run_check(before_final_check=lambda:path.write_bytes(b'{}')))
 def test_unknown_cache_and_malformed_selection_cannot_waive_full_checks(self):
  self.configure(nullary=True,one_source=True)
  for request in [{},{**self.request,'cache_success':True},{**self.request,'scope_policy':[]},{**self.request,'authority_effect':'admitted'}]:self.unresolved(x.run(self.root,request))
 def test_stale_or_changed_selection_file_has_no_retained_model_support(self):
  self.configure(nullary=True,one_source=True);ref=self.put('regression/selection.json',self.request);bad={**ref,'sha256':'0'*64};self.unresolved(x.run_selected(self.root,bad),'stale-regression-selection');self.unresolved(x.run_selected(self.root,ref,before_final_check=lambda:(self.root/ref['path']).write_bytes(b'{}')),'regression-selection-changed-during-check')
 def test_required_query_limit_has_no_false_success(self):
  self.configure(nullary=True,one_source=True)
  with patch.object(x,'MAX_QUERIES',1):self.unresolved(self.run_check(),'regression-query-denominator-limit-or-duplicate')

if __name__=='__main__':unittest.main()
