"""Independent revision labels, regenerated targets, retained history and explicit claims."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(HERE),str(HERE/'tests')]
import diff as x
import test_E03 as fixture

class RevisionControls(unittest.TestCase):
 def setUp(self):
  self.fixture,self.bundle,self.required,self.put,self.selected=fixture.setup_selection();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.root;self.counter=0
  epoch=x.i.capture_epoch(self.root,{'snapshot_ref':self.bundle['snapshot_ref'],'roots':self.bundle['sources'],'packet_refs':[],'cycle_policies':[],'required_edges':[],'bindings':[{'definition_id':s['definition_id'],'artifacts':{role:[] for role in x.i.ROLES}} for s in self.bundle['sources']]});epoch_ref=self.put('candidate/revision-epoch.json',epoch)
  side={'epoch_ref':epoch_ref,'theory_ref':self.bundle['theory_ref'],'relations_ref':self.selected['relation_requests_ref'],'populations_ref':self.selected['populations_ref'],'bindings_ref':self.selected['endpoint_bindings_ref'],'assumptions_ref':self.bundle['assumption_set_ref']}
  self.selection={'schema_version':'definition-assurance-revision-selection/v1-candidate','authority_effect':'none','baseline':copy.deepcopy(side),'proposal':copy.deepcopy(side),'declared_change':'unchanged','claims':[]}
 def data(self,key,side='proposal'):return json.loads((self.root/self.selection[side][key+'_ref']['path']).read_bytes())
 def change(self,key,value,side='proposal',raw=None):
  self.counter+=1;path=f'candidate/{side}-{key}-{self.counter}.json'
  if raw is None:ref=self.put(path,value)
  else:(self.root/path).write_bytes(raw);ref={'path':path,'sha256':x.r.digest(raw)}
  self.selection[side][key+'_ref']=ref;return ref
 def run_revision(self):return x.generate(self.root,self.selection)
 def fault(self,code,callback):
  with self.assertRaises(x.RevisionFault) as caught:callback()
  self.assertEqual(code,caught.exception.code)
 def add_constraint(self):
  theory=self.data('theory');theory['statements'].append(x.o.p.quant('forall','Object',x.o.p.pred('P')));self.change('theory',theory)
 def add_predicate(self):
  theory=self.data('theory');theory['declarations'].append({'kind':'predicate','symbol_id':'R','scope':theory['scope'],'argument_sorts':['Object']});self.change('theory',theory);bindings=self.data('bindings');bindings['extra']={**copy.deepcopy(bindings['left']),'predicate':'R'};self.change('bindings',bindings);pops=self.data('populations');pops.append({'population_id':'POP-R','carrier':'Object','predicate_ref':'R','requirement':'required','statement':x.o.p.quant('exists','Object',x.o.p.pred('R')),'scope':theory['scope'],'rationale':'An explicitly selected synthetic extra predicate.','review_ref':None});self.change('populations',pops)
 def test_unchanged_regeneration_matches_baseline_without_evidence_inheritance(self):
  out=self.run_revision();self.assertEqual('unchanged',out['derived_change']);self.assertEqual(out['baseline_required_set'],out['proposal_required_set']);self.assertTrue(all(row['status']=='unchanged' and row['prior_evidence_inherited'] is False for row in out['requirement_ledger']));self.assertFalse(out['semantic_ready']);self.assertFalse(out['evidence_verified'])
 def test_mislabelled_representation_cannot_waive_constraint_review(self):
  self.add_constraint();self.selection['declared_change']='representation-only';out=self.run_revision();self.assertEqual('constraint-change',out['derived_change']);self.assertTrue(any(row['check']=='constraint-change-review' for row in out['supplemental_gates']));self.assertEqual(['DEF-A','DEF-B'],out['invalidated_current_definitions']);self.assertTrue(out['global_regression_required'])
 def test_all_labels_keep_independently_generated_logical_denominator(self):
  self.add_constraint();outputs=[]
  for label in sorted(x.LABELS):
   self.selection['declared_change']=label;out=self.run_revision();outputs.append(out['proposal_required_set']);self.assertEqual('constraint-change',out['derived_change'])
  self.assertTrue(all(value==outputs[0] for value in outputs))
 def test_added_predicate_generates_population_and_conservativity_obligation(self):
  self.add_predicate();out=self.run_revision();self.assertEqual('additive',out['derived_change']);self.assertIn('population:POP-R',{row['obligation_id'] for row in out['proposal_required_set']['logical_manifest']['obligations']});claim=out['revision_claim_obligations'][0];self.assertEqual('conservativity',claim['descriptor']['kind']);self.assertEqual('mechanized-theorem',claim['minimum_strength']);self.assertEqual('pending-explicit-cross-theory-contract',claim['proof_encoding'])
 def test_signature_addition_does_not_create_identity_or_conservativity_evidence(self):
  self.add_predicate();out=self.run_revision();self.assertFalse(out['evidence_verified']);self.assertTrue(all(row['semantic_ready'] is False for row in out['revision_claim_obligations']));self.assertEqual(None,out['revision_claim_obligations'][0]['descriptor']['embedding_ref'])
 def test_json_format_only_requires_exact_rebinding_and_regeneration(self):
  theory=self.data('theory');self.change('theory',None,raw=json.dumps(theory,indent=4).encode());out=self.run_revision();self.assertEqual('representation-only',out['derived_change']);self.assertIn('theory_ref',out['representation_binding_changes']);self.assertTrue(out['global_regression_required']);self.assertTrue(any(row['check']=='revision-input-binding-review' for row in out['supplemental_gates']))
 def test_changed_premise_is_typed_and_invalidates_whole_selected_scope(self):
  doc=self.data('assumptions');doc['assumptions']=[x.o.p.quant('forall','Object',x.o.p.pred('Q'))];self.change('assumptions',doc);out=self.run_revision();self.assertTrue(out['observed_content_changes']['premise']);self.assertEqual(['DEF-A','DEF-B'],out['invalidated_current_definitions']);self.assertTrue(all(row['status']!='unchanged' for row in out['requirement_ledger']))
 def test_removed_relation_retains_obsolete_target_and_retirement_review(self):
  self.change('relations',[]);out=self.run_revision();row=next(row for row in out['requirement_ledger'] if row['category']=='logical' and row['requirement_id']=='relation:R1:equivalence');self.assertEqual('removed-pending-retirement-review',row['status']);self.assertIsNotNone(row['baseline_requirement']);self.assertIsNone(row['proposal_requirement']);self.assertTrue(any(g['check']=='obsolete-requirement-retirement-review' for g in out['supplemental_gates']))
 def test_alias_replaced_by_disjointness_retains_both_denominators(self):
  rel=self.data('relations');rel[0]['relation']['relation_class']='disjoint';self.change('relations',rel);out=self.run_revision();self.assertTrue(out['observed_content_changes']['coupling']);self.assertTrue(any(row['requirement_id']=='relation:R1:equivalence' and row['status']=='removed-pending-retirement-review' for row in out['requirement_ledger']));self.assertTrue(any(row['requirement_id']=='relation:R1:disjointness' and row['status']=='new' for row in out['requirement_ledger']))
 def test_population_exemption_keeps_old_target_and_both_review_gates(self):
  pops=self.data('populations');pops[0].update(requirement='exempt',statement=None,review_ref={'path':'pending-owner-review.json','sha256':'0'*64});self.change('populations',pops);out=self.run_revision();self.assertTrue(any(row['status']=='removed-pending-retirement-review' and row['requirement_id'].startswith('population:') for row in out['requirement_ledger']));self.assertTrue(any(g['check']=='population-exemption-review' for g in out['proposal_required_set']['administrative_and_semantic_gates']));self.assertTrue(any(g['check']=='obsolete-requirement-retirement-review' for g in out['supplemental_gates']))
 def test_same_formula_in_changed_context_is_not_unchanged_evidence(self):
  self.add_constraint();out=self.run_revision();row=next(row for row in out['requirement_ledger'] if row['category']=='logical' and row['requirement_id']=='query:consistency');self.assertEqual(row['baseline_requirement'],row['proposal_requirement']);self.assertEqual('replaced-context-or-target',row['status']);self.assertNotEqual(row['baseline_context_sha256'],row['proposal_context_sha256'])
 def test_source_only_theory_relabel_does_not_create_identity_equivalence(self):
  theory=self.data('theory');theory['theory_id']='RenamedSyntheticTheory';self.change('theory',theory);out=self.run_revision();self.assertEqual('meaning-change',out['derived_change']);self.assertTrue(out['observed_content_changes']['theory-identity']);self.assertEqual([],out['revision_claim_obligations'])
 def test_wrong_source_hash_cannot_rebind_to_epoch_identity(self):
  theory=self.data('theory');theory['sources'][0]['sha256']='0'*64;self.change('theory',theory);self.fault('theory-epoch-source-substitution',self.run_revision)
 def test_explicit_preservation_is_extra_kernel_strength_requirement(self):
  self.add_constraint();self.selection['claims']=[{'claim_id':'preserve-alias','kind':'preservation','targets':['relation:R1:equivalence'],'embedding_ref':None}];out=self.run_revision();claim=out['revision_claim_obligations'][0];self.assertEqual(['relation:R1:equivalence'],claim['descriptor']['selected_target_ids']);self.assertEqual('mechanized-theorem',claim['minimum_strength']);self.assertTrue(any(row['check']=='cross-theory-embedding-review' for row in out['supplemental_gates']))
 def test_empty_baseline_model_class_cannot_bypass_admissibility_witnesses(self):
  theory=self.data('theory');theory['statements']=[x.o.p.quant('forall','Object',{'op':'not','arg':x.o.p.pred('P')})];self.change('theory',theory,'baseline');self.selection['claims']=[{'claim_id':'vacuous-conservation','kind':'conservativity','targets':[],'embedding_ref':None}];out=self.run_revision();gate=next(g for g in out['supplemental_gates'] if g['gate_id']=='revision:baseline-admissibility');self.assertEqual('model-witness',gate['minimum_strength']);self.assertEqual({'query:consistency','query:joint-population'},{q['obligation_id'] for q in gate['subject']['required_queries']});joint=next(q['statement'] for q in gate['subject']['required_queries'] if q['obligation_id']=='query:joint-population');matches=0
  for p_on,q_on in [(False,False),(False,True),(True,False),(True,True)]:
   model={'domains':{'Object':['a']},'constants':{},'functions':{},'predicates':{'P':[['a']] if p_on else [],'Q':[['a']] if q_on else []}};evaluator=fixture.v.Denotation(theory['declarations'],model);matches+=all(evaluator.truth(f) for f in theory['statements']) and evaluator.truth(joint)
  self.assertEqual(0,matches);self.assertFalse(out['semantic_ready']);self.assertEqual('required',out['revision_claim_obligations'][0]['status'])
 def test_conservativity_claim_cannot_limit_old_signature_to_easy_targets(self):
  self.selection['claims']=[{'claim_id':'weak-conservative','kind':'conservativity','targets':['query:consistency'],'embedding_ref':None}];self.fault('conservativity-cannot-shrink-old-signature',self.run_revision)
 def test_identity_claim_requires_exact_selected_endpoints_and_stays_pending(self):
  sources=self.data('theory')['sources'];self.selection['claims']=[{'claim_id':'identity','kind':'identity-equivalence','targets':[row['version_ref'] for row in sources],'embedding_ref':None}];out=self.run_revision();self.assertFalse(out['revision_claim_obligations'][0]['semantic_ready']);self.selection['claims'][0]['targets'][0]='unselected@1.0.0';self.fault('unbound-identity-equivalence-target',self.run_revision)
 def test_same_source_version_identity_is_still_a_cross_interpretation_claim(self):
  source=self.data('theory')['sources'][0];self.add_constraint();self.selection['claims']=[{'claim_id':'same-source','kind':'identity-equivalence','targets':[source['version_ref'],source['version_ref']],'embedding_ref':None}];out=self.run_revision();claim=out['revision_claim_obligations'][0];self.assertEqual({'baseline_source':source,'proposal_source':source},claim['descriptor']['selected_source_pair']);self.assertEqual('mechanized-theorem',claim['minimum_strength']);self.assertFalse(claim['semantic_ready'])
 def test_identity_target_must_belong_to_its_selected_side(self):
  original=self.data('theory');old=copy.deepcopy(original);old['sources']=old['sources'][:1];old['declarations']=[d for d in old['declarations'] if d['kind']=='sort' or d['symbol_id']=='P'];self.change('theory',old,'baseline');self.change('relations',[],'baseline');self.change('populations',[p for p in self.data('populations') if p['predicate_ref']=='P'],'baseline');bindings=self.data('bindings');self.change('bindings',{'left':bindings['left']},'baseline');self.selection['claims']=[{'claim_id':'wrong-old-side','kind':'identity-equivalence','targets':[original['sources'][1]['version_ref'],original['sources'][0]['version_ref']],'embedding_ref':None}];self.fault('unbound-identity-equivalence-target',self.run_revision)
 def test_unbound_preservation_target_cannot_invent_an_obligation(self):
  self.selection['claims']=[{'claim_id':'fake','kind':'preservation','targets':['invented-target'],'embedding_ref':None}];self.fault('unbound-preservation-target',self.run_revision)
 def test_prior_conservativity_is_not_erased_by_initial_metadata_label(self):
  initial=self.data('theory');prior=self.put('candidate/earlier-initial-theory.json',initial);baseline=copy.deepcopy(initial);baseline.update(change_class='additive',prior_theory_ref=prior);self.change('theory',baseline,'baseline');self.selection['proposal']['theory_ref']=self.put('candidate/proposal-initial-relabel.json',initial);self.selection['declared_change']='initial';out=self.run_revision();gate=next(g for g in out['supplemental_gates'] if g['gate_id']=='revision:prior-policy:gate:conservativity');self.assertEqual('mechanized-theorem',gate['minimum_strength']);self.assertEqual('conservativity',gate['subject']['baseline_requirement']['check'])
 def test_new_prior_binding_comes_from_selected_actual_baseline(self):
  self.add_constraint();out=self.run_revision();self.assertEqual(self.selection['baseline']['theory_ref'],out['effective_proposal_theory']['prior_theory_ref']);self.assertIsNone(self.data('theory')['prior_theory_ref'])
 def test_drop_population_or_weaken_alias_strength_is_rejected(self):
  self.change('populations',[])
  with self.assertRaises(x.o.p.PolicyFault):self.run_revision()
 def test_unbound_or_ill_sorted_formula_does_not_pass_as_typed_change(self):
  theory=self.data('theory');theory['statements']=[{'op':'pred','name':'Missing','args':[]}];self.change('theory',theory)
  with self.assertRaises(x.ir.IRFault):self.run_revision()
 def test_duplicate_signature_or_unknown_declaration_cannot_pass(self):
  theory=self.data('theory');theory['declarations'].append(copy.deepcopy(theory['declarations'][0]));self.change('theory',theory);self.fault('duplicate-or-unscoped-declaration',self.run_revision)
 def test_assumption_context_and_unknown_fields_are_rejected(self):
  doc=self.data('assumptions');doc['assumption_set_id']='OTHER';self.change('assumptions',doc);self.fault('assumption-context-substitution',self.run_revision)
 def test_submission_cannot_omit_retired_requirement_or_extra_claim(self):
  self.change('relations',[]);out=self.run_revision();bad=copy.deepcopy(out);bad['requirement_ledger']=[row for row in bad['requirement_ledger'] if row['status']!='removed-pending-retirement-review'];self.fault('revision-requirement-denominator-or-binding-substitution',lambda:x.compare_submission(self.root,self.selection,bad))
 def test_selected_input_mutation_at_closing_clears_revision(self):
  ref=self.selection['proposal']['theory_ref'];self.fault('revision-input-changed-during-check',lambda:x.generate(self.root,self.selection,before_final_check=lambda:(self.root/ref['path']).write_bytes(b'{}')))
 def test_stale_selected_file_and_malformed_selection_return_explicit_unresolved(self):
  for selection in [{}, {**self.selection,'authority_effect':'admitted'}, {**self.selection,'claims':None}, {**self.selection,'ignored':True}]:
   ref=self.put('candidate/malformed-selection.json',selection);out=x.analyze_selected(self.root,ref);self.assertEqual('revision-unresolved',out['status']);self.assertIsNone(out['result'])
  ref=self.put('candidate/selected-revision.json',self.selection);ref['sha256']='0'*64;out=x.analyze_selected(self.root,ref);self.assertEqual('stale-revision-selection',out['diagnostics'][0]['code'])
 def test_selection_file_race_returns_no_revision_result(self):
  ref=self.put('candidate/racing-revision-selection.json',self.selection);out=x.analyze_selected(self.root,ref,before_final_check=lambda:(self.root/ref['path']).write_bytes(b'{}'));self.assertEqual('revision-unresolved',out['status']);self.assertIsNone(out['result']);self.assertEqual('revision-selection-changed-during-check',out['diagnostics'][0]['code'])
 def test_engine_read_drift_is_unresolved_without_mutating_canonical_code(self):
  original=Path.read_bytes;changed=[False]
  def read(path):return b'simulated new rules' if changed[0] and path==x.o.RULES else original(path)
  with patch.object(Path,'read_bytes',read):self.fault('revision-engine-changed-during-check',lambda:x.generate(self.root,self.selection,before_final_check=lambda:changed.__setitem__(0,True)))
 def test_claim_limits_and_input_limits_never_become_logical_negative_results(self):
  with patch.object(x,'MAX_INPUT_BYTES',1):self.fault('revision-input-byte-limit',self.run_revision)
  with patch.object(x,'MAX_CLAIMS',0):
   self.selection['claims']=[{'claim_id':'c','kind':'conservativity','targets':[],'embedding_ref':None}];self.fault('malformed-revision-claims',self.run_revision)
 def test_repeated_exact_generation_is_deterministic(self):self.assertEqual(self.run_revision(),self.run_revision())

if __name__=='__main__':unittest.main()
