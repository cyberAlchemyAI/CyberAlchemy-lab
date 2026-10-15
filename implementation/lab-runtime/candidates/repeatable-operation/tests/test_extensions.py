"""Synthetic candidate extension cases; none are semantic owner evidence."""
import copy,json
from pathlib import Path
import sys,unittest
PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE))
from lab_runtime.common import RuntimeFault,byte_digest
from lab_runtime.extensions import check_closed_domain,inspect_extension

class ExtensionTests(unittest.TestCase):
 def setUp(self):
  self.bytes={}
  def bind(ref,obj):
   raw=json.dumps(obj,sort_keys=True).encode();self.bytes[ref]=raw;return {'ref':ref,'sha256':byte_digest(raw)}
  self.bind=bind
  current_binding=bind('fixture:old-kind',{'kind':'relation-kind','unique_question':'Which activity belongs to this bounded project?'})
  self.relations={'fixture:member-of':{'version_ref':'fixture:member-of@1','effective_state':'admitted-current','unique_question':'Which activity belongs to this bounded project?','axis_ref':'fixture:bounded-membership','allowed_endpoint_pairs':[('work','project')]}}
  self.endpoints={}
  for kind in ['work','project','experiment-run']:
   self.endpoints['fixture:'+kind]={'kind':kind,'scope':'carrier','effective_state':'admitted-current','evidence_binding':bind('fixture:schema:'+kind,{'type':'object','properties':{'kind':{'const':kind}},'required':['kind']})}
  self.qualifier={'type':'object','additionalProperties':False,'properties':{'membership_role':{'enum':['delivery','experiment']},'scope':{'const':'fixture:project-scope'}},'required':['membership_role','scope'],'allOf':[{'if':{'properties':{'membership_role':{'const':'experiment'}}},'then':{'properties':{'scope':{'const':'fixture:project-scope'}}}}]}
  schema_binding=bind('fixture:qualifier',self.qualifier)
  constraints=bind('fixture:constraints',{'schema_binding':schema_binding,'constraints':['all JSON Schema constraints in the exact bound qualifier schema'],'authority_effect':'none'})
  def pair(source):return {'source_kind':source,'target_kind':'project','source_contract_ref':'fixture:'+source,'target_contract_ref':'fixture:project','source_role':'bounded member activity','target_role':'bounded project scope','qualifier_schema_binding':schema_binding,'cross_constraints_binding':constraints,'canonical_authority':'typed-relation','projection_binding':None}
  report=bind('fixture:no-collapse',{'schema_version':'lab-extension-noncollapse-review/v1-candidate','proposal_ref':'fixture:extension','question':self.relations['fixture:member-of']['unique_question'],'axis_ref':'fixture:bounded-membership','comparisons':[{'relation_kind_ref':'fixture:member-of','existing_version_ref':'fixture:member-of@1','existing_question':self.relations['fixture:member-of']['unique_question'],'difference':'Fixture preserves bounded membership semantics while adding one explicit activity kind; no delivery or use claim.','evidence_binding':current_binding}],'posture':'candidate-reasoning-for-owner-review','authority_effect':'none'})
  contest=bind('fixture:contest',{'owner_ref':'fixture:owner','challenge_route':'fixture:challenge','covered_subjects':['relation-kind','endpoint-pair','qualifiers','source-endpoint','target-endpoint','relation-instance'],'authority_effect':'none'})
  self.p={'schema_version':'lab-closed-extension-proposal/v1-candidate','authority_effect':'none','proposal_ref':'fixture:extension','scope':'global','ontology_contract_ref':None,'mode':'reuse','relation_kind_ref':'fixture:member-of','predecessor_version_ref':'fixture:member-of@1','successor_version_ref':'fixture:member-of@2','unique_question':self.relations['fixture:member-of']['unique_question'],'axis_ref':'fixture:bounded-membership','allowed_endpoint_pairs':[pair('work'),pair('experiment-run')],'source_kinds':['work','experiment-run'],'target_kinds':['project'],'noncollapse_report_binding':report,'owner_ref':'fixture:owner','contestability_binding':contest,'lifecycle_effect':'Candidate successor only; predecessor remains current until R08.','validation_effect':'New pair used only after exact successor admission.','effect_rule':'candidate-only; no pair availability or instance admission'}
 def run_inspect(self):return inspect_extension(self.p,current_relations=self.relations,endpoint_contracts=self.endpoints,evidence_bytes=self.bytes)
 def test_ready_is_not_effective(self):
  r=self.run_inspect();self.assertEqual(r['globally_available_pairs_added'],0);self.assertEqual(r['relation_instances_created'],0);self.assertEqual(r['semantic_verdict'],'not-issued-by-validator');self.assertEqual(len(r['pair_results']),2)
 def test_reversed_pair_requires_explicit_endpoint_contract(self):
  self.p['allowed_endpoint_pairs'][1]['source_kind']='project';self.p['allowed_endpoint_pairs'][1]['target_kind']='experiment-run'
  with self.assertRaises(RuntimeFault):self.run_inspect()
 def test_cartesian_projection_never_supplies_missing_pair(self):
  self.p['target_kinds'].append('work')
  with self.assertRaisesRegex(RuntimeFault,'projection'):self.run_inspect()
 def test_wildcard_rejected(self):
  self.p['allowed_endpoint_pairs'][1]['source_kind']='*'
  with self.assertRaisesRegex(RuntimeFault,'wildcard'):self.run_inspect()
 def test_stale_predecessor(self):
  self.p['predecessor_version_ref']='fixture:member-of@stale'
  with self.assertRaisesRegex(RuntimeFault,'predecessor'):self.run_inspect()
 def test_semantic_question_cannot_change_under_reuse(self):
  self.relations['fixture:member-of']['unique_question']='Which Product Capability is realized?'
  with self.assertRaises(RuntimeFault):self.run_inspect()
 def test_endpoint_contract_unresolved(self):
  self.endpoints.pop('fixture:experiment-run')
  with self.assertRaisesRegex(RuntimeFault,'unresolved'):self.run_inspect()
 def test_candidate_endpoint_is_explicitly_pending(self):
  self.endpoints['fixture:experiment-run']['effective_state']='candidate-for-R08'
  r=self.run_inspect();self.assertEqual(r['pending_endpoint_admission_refs'],['fixture:experiment-run']);self.assertEqual(r['globally_available_pairs_added'],0)
 def test_open_qualifier_strings_rejected(self):
  self.qualifier['properties']['membership_role']={'type':'string','minLength':1}
  b=self.bind('fixture:qualifier',self.qualifier);self.p['allowed_endpoint_pairs'][0]['qualifier_schema_binding']=b
  with self.assertRaisesRegex(RuntimeFault,'finite'):self.run_inspect()
 def test_domain_budget(self):
  schema={'type':'object','additionalProperties':False,'properties':{str(i):{'enum':[0,1]} for i in range(15)},'required':[str(i) for i in range(15)]}
  with self.assertRaisesRegex(RuntimeFault,'budget'):check_closed_domain(schema)
 def test_cross_constraints_actually_filter_values(self):
  s={'type':'object','additionalProperties':False,'properties':{'a':{'enum':[0,1]},'b':{'enum':[0,1]}},'required':['a','b'],'not':{'properties':{'a':{'const':1},'b':{'const':1}},'required':['a','b']}}
  r=check_closed_domain(s);self.assertEqual(r['candidate_values'],4);self.assertEqual(r['allowed_values'],3)
 def test_optional_null_is_not_omission(self):
  r=check_closed_domain({'type':'object','additionalProperties':False,'properties':{'a':{'enum':[None]}},'required':[]});self.assertEqual(r['allowed_values'],2)
 def test_dual_writable_authority(self):
  self.p['allowed_endpoint_pairs'][0]['canonical_authority']=['typed-relation','specialized-carrier']
  with self.assertRaises(RuntimeFault):self.run_inspect()
 def test_noncollapse_text_token_is_insufficient(self):
  self.p['noncollapse_report_binding']=self.bind('fixture:no-collapse',{'result':'PASS','noncollapse':True})
  with self.assertRaises(RuntimeFault):self.run_inspect()
 def test_noncollapse_must_cover_selected_inventory(self):
  self.relations['fixture:other']={**self.relations['fixture:member-of'],'unique_question':'Which inputs were used?'}
  with self.assertRaisesRegex(RuntimeFault,'complete selected'):self.run_inspect()
 def test_owner_outcome_cannot_be_fabricated_in_candidate_report(self):
  report=json.loads(self.bytes['fixture:no-collapse']);report['posture']='owner-approved';self.p['noncollapse_report_binding']=self.bind('fixture:no-collapse',report)
  with self.assertRaisesRegex(RuntimeFault,'owner outcome'):self.run_inspect()
 def test_local_never_enters_global_registry(self):
  self.p['scope']='ontology-local';self.p['ontology_contract_ref']='fixture:ontology';r=self.run_inspect();self.assertEqual(r['globally_available_pairs_added'],0)
 def test_predecessor_connections_cannot_be_dropped(self):
  self.p['allowed_endpoint_pairs']=self.p['allowed_endpoint_pairs'][1:];self.p['source_kinds']=['experiment-run']
  with self.assertRaisesRegex(RuntimeFault,'removes predecessor'):self.run_inspect()
 def test_internal_record_requires_explicit_kind_permission(self):
  self.endpoints['fixture:project']['scope']='explicit-governed-internal-record'
  with self.assertRaisesRegex(RuntimeFault,'explicitly permitted'):self.run_inspect()
 def test_evidence_bytes_changed(self):
  self.bytes['fixture:old-kind']+=b'\n'
  with self.assertRaisesRegex(RuntimeFault,'byte binding'):self.run_inspect()

 def test_nested_remote_schema_reference_rejected(self):
  s=copy.deepcopy(self.qualifier);s['allOf']=[{'$ref':'https://example.invalid/schema'}]
  with self.assertRaisesRegex(RuntimeFault,'prior explicit closure'):check_closed_domain(s)
 def test_patterned_names_are_not_finite_domains(self):
  s=copy.deepcopy(self.qualifier);s['patternProperties']={'^x':{'enum':[1]}}
  with self.assertRaisesRegex(RuntimeFault,'prior explicit closure'):check_closed_domain(s)

 def test_distinct_kind_cannot_duplicate_unique_question(self):
  self.p.update(mode='distinct-kind',relation_kind_ref='fixture:new-kind',predecessor_version_ref=None)
  with self.assertRaisesRegex(RuntimeFault,'duplicates'):self.run_inspect()
 def test_specialized_carrier_requires_exact_canonical_mapping(self):
  projection={'specialized_carrier_ref':'fixture:work','projection_carrier_ref':'cal.artifact-type.typed-relation/v3','projection_mode':'digest-bound-read-only','writable_authority':'specialized-carrier','authority_effect':'none'}
  pair=self.p['allowed_endpoint_pairs'][0];pair['canonical_authority']='specialized-carrier';pair['projection_binding']=self.bind('fixture:projection',projection)
  with self.assertRaisesRegex(RuntimeFault,'explicit canonical'):self.run_inspect()
 def test_missing_contestability_subject_rejected(self):
  contest=json.loads(self.bytes['fixture:contest']);contest['covered_subjects'].remove('qualifiers');self.p['contestability_binding']=self.bind('fixture:contest',contest)
  with self.assertRaisesRegex(RuntimeFault,'all connection subjects'):self.run_inspect()

 def test_predecessor_qualifier_axes_cannot_be_removed(self):
  self.relations['fixture:member-of']['qualifier_contract']={'required_axes':['required_old_axis'],'properties':{'required_old_axis':{'type':'string'}}}
  with self.assertRaisesRegex(RuntimeFault,'axes removed'):self.run_inspect()

if __name__=='__main__':unittest.main()
