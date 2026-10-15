"""Real D75 source-bound extension inspection; no owner outcome is simulated."""
import base64,copy,json
from pathlib import Path
import sys,unittest
PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3];sys.path.insert(0,str(PACKAGE))
from lab_runtime.common import RuntimeFault,byte_digest,digest,load
from lab_runtime.extensions import inspect_bound_extension
from lab_runtime.profiles import select
from lab_runtime.sources import capture

class BoundExtensionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  row=next(x for x in load(PACKAGE/'profiles/selections.json')['selections'] if x['name']=='d75')
  cls.snapshot=capture(select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']}))
  cls.profile_sha=row['profile_sha256'];cls.snapshot_digest=cls.snapshot['snapshot_digest']
 def setUp(self):
  self.evidence={}
  def bind(ref,value):
   raw=json.dumps(value,sort_keys=True).encode();self.evidence[ref]=raw;return {'ref':ref,'sha256':byte_digest(raw)}
  self.bind=bind
  old=self.snapshot['relation_contracts']['relation.acts-for']['payload']
  prior=next(x for x in self.snapshot['subjects'].values() if x['category']=='relation-kind' and x['identity']=='relation.acts-for' and x['effective_state']=='admitted-current')
  comparisons=[]
  for ref,record in self.snapshot['relation_contracts'].items():
   entry=next(x for x in self.snapshot['subjects'].values() if x['category']=='relation-kind' and x['identity']==ref and x['effective_state']=='admitted-current')
   b={'ref':entry['source']['path'],'sha256':entry['source']['sha256']}
   comparisons.append({'relation_kind_ref':ref,'existing_version_ref':entry['version_ref'],'existing_question':record['payload']['unique_question'],'difference':('This candidate retains the same bounded Principal representation question and exact predecessor endpoints.' if ref=='relation.acts-for' else 'This selected kind asks '+record['payload']['unique_question']+' The proposal retains only acts-for representation and makes no additional claim on that question.'),'evidence_binding':b})
  report=bind('candidate:acts-for-review',{'schema_version':'lab-extension-noncollapse-review/v1-candidate','proposal_ref':'candidate:acts-for-inspection','question':old['unique_question'],'axis_ref':old['axis_id'],'comparisons':comparisons,'posture':'candidate-reasoning-for-owner-review','authority_effect':'none'})
  props={k:{'const':'example:'+k} for k in old['qualifier_contract']['required_axes']}
  qualifier=bind('candidate:closed-qualifiers',{'type':'object','additionalProperties':False,'properties':props,'required':old['qualifier_contract']['required_axes']})
  constraints=bind('candidate:cross-constraints',{'schema_binding':qualifier,'constraints':['all JSON Schema constraints in the exact bound qualifier schema'],'authority_effect':'none'})
  contest=bind('candidate:contestability',{'owner_ref':'role:relation-owner','challenge_route':'challenge:relation-governance-review','covered_subjects':['relation-kind','endpoint-pair','qualifiers','source-endpoint','target-endpoint','relation-instance'],'authority_effect':'none'})
  self.p={'schema_version':'lab-closed-extension-proposal/v1-candidate','authority_effect':'none','proposal_ref':'candidate:acts-for-inspection','scope':'global','ontology_contract_ref':None,'mode':'reuse','relation_kind_ref':'relation.acts-for','predecessor_version_ref':prior['version_ref'],'successor_version_ref':'candidate:relation.acts-for@inspection.1','unique_question':old['unique_question'],'axis_ref':old['axis_id'],'allowed_endpoint_pairs':[{'source_kind':'agent-instance','target_kind':'principal','source_contract_ref':'cal.artifact-type.agent-instance/v1','target_contract_ref':'cal.artifact-type.principal/v1','source_role':'ephemeral represented Agent Instance','target_role':'accountable represented Principal','qualifier_schema_binding':qualifier,'cross_constraints_binding':constraints,'canonical_authority':'typed-relation','projection_binding':None}],'source_kinds':['agent-instance'],'target_kinds':['principal'],'noncollapse_report_binding':report,'owner_ref':'role:relation-owner','contestability_binding':contest,'lifecycle_effect':'Candidate inspection; no predecessor effect.','validation_effect':'Owner must review exact successor; no effective pair or instance here.','effect_rule':'candidate-only; no pair availability or instance admission'}
 def inspect(self,snapshot=None):return inspect_bound_extension(self.p,snapshot=self.snapshot if snapshot is None else snapshot,expected_profile_sha256=self.profile_sha,expected_snapshot_digest=self.snapshot_digest,candidate_endpoint_contracts={},evidence_bytes=self.evidence)
 def test_actual_d75_binding_and_complete_comparison_inventory(self):
  from jsonschema import Draft202012Validator
  Draft202012Validator(load(PACKAGE/'schemas/extension-evidence.schema.json')).validate(self.p)
  result=self.inspect();self.assertEqual(result['globally_available_pairs_added'],0);self.assertEqual(result['semantic_verdict'],'not-issued-by-validator');self.assertEqual(result['pending_endpoint_admission_refs'],[])
 def test_resealed_effective_metadata_fails_independent_snapshot_pin(self):
  snapshot=copy.deepcopy(self.snapshot);snapshot['subjects'][next(iter(snapshot['subjects']))]['effective_state']='forged';snapshot['snapshot_digest']=digest({k:v for k,v in snapshot.items() if k!='snapshot_digest'})
  with self.assertRaisesRegex(RuntimeFault,'semantic snapshot pin'):self.inspect(snapshot)
 def test_candidate_evidence_cannot_shadow_canonical_bytes(self):
  name=next(iter(self.snapshot['byte_contents']));self.evidence[name]=b'{}'
  with self.assertRaisesRegex(RuntimeFault,'canonical bytes'):self.inspect()

if __name__=='__main__':unittest.main()
