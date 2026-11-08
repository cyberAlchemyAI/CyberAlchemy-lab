"""Real scope schemas over synthetic pending-review transport; no API claim."""
import copy
import json
import unittest
import review_scope as P

class ReviewScope(unittest.TestCase):
 def setUp(self):
  self.scope='project:synthetic-only';target={'node_id':'definition:synthetic','scope_ref':self.scope};raw=P.enc(target)
  self.target={'scope_ref':self.scope,'identity_ref':target['node_id'],'version_ref':target['node_id']+'@1','carrier_ref':'cal.artifact-type.definition/v1','byte_sha256':P.sha(raw)}
  ordered={'selected_outcome':None,'target_refs':[self.target['version_ref']],'target_digests':[{'target_ref':self.target['version_ref'],'sha256':P.sha(raw)}],'decision_core_sha256':'c'*64}
  b={'owner_ref':'principal:synthetic-proposed-owner','payload':{'checkpoint_ref':'checkpoint:synthetic','ordered_decisions':[ordered]}}
  c={'payload':{'decision_bundle_ref':'bundle:synthetic','presentation_state':'pending','closed_at':None}}
  self.records={}
  for identity,carrier,body in [('bundle:synthetic','cal.artifact-type.decision-bundle/v1',b),('checkpoint:synthetic','cal.artifact-type.decision-checkpoint/v1',c)]:
   original=P.enc(body);h={'scope_ref':self.scope,'identity_ref':identity,'version_ref':identity+'@1','carrier_ref':carrier,'byte_sha256':P.sha(original)};self.records[h['version_ref']]=(h,original)
  binding={'ref':'synthetic-content','sha256':P.sha(raw)}
  self.manifest={'schema_version':'lab-exact-review-materialization/v1-candidate','base_cut':{'synthetic':True},'all_targets_materialized':True,'actual_owner_outcome':None,
   'repository_admissions_applied':0,'runtime_activations':0,'external_effect_refs':[],
   'targets':[{'target':{'operation':'admit','artifact':self.target},'original_content_binding':binding,'core_binding':{'sha256':'c'*64}}]}
  self.raw=raw;self.binding=binding;self.seal()
 def seal(self):
  raw=P.enc(self.manifest);mb={'ref':'object:synthetic-manifest','sha256':P.sha(raw)}
  self.observed={'observation_binding':{'ref':'synthetic:review-observation','sha256':'o'*64},'original_source_cut':{'synthetic':True},
   'actual_reply':{'operation':'proposal.review','kind':'result','message':{'manifest_binding':mb,'decision_bundle':self.records['bundle:synthetic@1'][0],'checkpoint':self.records['checkpoint:synthetic@1'][0]}},
   'files':{'vault/objects/'+P.sha(raw)+'.json':raw,'vault/workspace.json':P.enc({'materials':[dict(self.binding,path='inputs/target.json')]}),'vault/inputs/target.json':self.raw}}
 def produce(self,controls=None):
  return P.produce(records=self.records,observations=[self.observed],controls=controls or {'review_observation_ref':'synthetic:review-observation'})
 def test_exact_original_pending_review_produces_private_scope_and_boundary(self):
  out=self.produce();self.assertEqual(len(out['records']),2);body=json.loads(out['records'][0][1]);self.assertEqual(body['payload']['subject_refs'],[self.target['version_ref']]);self.assertEqual(body['payload']['permitted_effects'],['candidate-review-ready-metadata']);self.assertFalse(out['receipt']['owner_decision_or_grant_created'])
 def test_target_bytes_cannot_change_after_review(self):
  self.observed['files']['vault/inputs/target.json']+=b' '
  with self.assertRaisesRegex(ValueError,'target bytes'):self.produce()
 def test_rebound_ordered_target_digest_refuses(self):
  body=json.loads(self.records['bundle:synthetic@1'][1]);body['payload']['ordered_decisions'][0]['target_digests'][0]['sha256']='0'*64
  header,raw=self.records['bundle:synthetic@1'];raw=P.enc(body);header=copy.deepcopy(header);header['byte_sha256']=P.sha(raw);self.records['bundle:synthetic@1']=(header,raw);self.seal()
  with self.assertRaisesRegex(ValueError,'target/core'):self.produce()
 def test_closed_checkpoint_or_owner_outcome_refuses(self):
  self.manifest['actual_owner_outcome']='admit';self.seal()
  with self.assertRaisesRegex(ValueError,'outcome'):self.produce()
 def test_undeclared_control_or_missing_target_original_refuses(self):
  with self.assertRaisesRegex(ValueError,'closed actual review'):self.produce({'review_observation_ref':'synthetic:review-observation','undeclared':True})
  self.observed['files'].pop('vault/inputs/target.json')
  with self.assertRaisesRegex(ValueError,'target bytes'):self.produce()
 def test_scope_production_is_deterministic_and_preserves_inputs(self):
  before=copy.deepcopy((self.records,self.observed));a=self.produce();self.assertEqual(a,self.produce());self.assertEqual(before,(self.records,self.observed))

if __name__=='__main__':unittest.main()
