"""Real retained implementation/FLAG inputs; synthetic permission only."""
import copy
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE)]
import profiles as P
import product_negative as N

class ProductNegative(unittest.TestCase):
    def setUp(self):
        self.profile=P.load('engineering');scope=self.profile['scope_ref']
        def record(path,carrier,field,version):
            raw=path.read_bytes();body=json.loads(raw);identity=body[field]
            return ({'scope_ref':scope,'identity_ref':identity,'version_ref':identity+'@'+version,'carrier_ref':carrier,'byte_sha256':P.sha(raw)},raw)
        source=P.ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/source/packages/0001/setup-artifacts/product.json'
        self.product=record(source,'cal.artifact-type.product-identity/v2','product_id',json.loads(source.read_bytes())['version'])
        self.capability=record(P.ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json',
          'cal.artifact-type.product-capability/v1','node_id','foundation.1')
    def run_factory(self):return N.construct(self.profile,product=self.product,capability=self.capability,principal='principal:synthetic-local-metadata',seed='component-only')
    def test_actual_candidate_and_missing_pilot_outcome_preserve_original_meaning(self):
        transitions,raws,r,impl=self.run_factory()
        self.assertEqual(len(transitions),2);self.assertEqual(len(raws),2)
        bodies=[json.loads(raw) for raw in raws.values()]
        self.assertIsNone(bodies[0]['adoption_decision_ref']);self.assertEqual(bodies[0]['binding_state'],'candidate')
        self.assertEqual(bodies[1]['payload']['disposition'],'unsupported');self.assertEqual(bodies[1]['payload']['subject_ref'],self.profile['original_work']['version_ref'])
        self.assertFalse(r['human_pilot_performed']);self.assertFalse(r['original_ready_only_adapter_invoked']);self.assertIsNone(r['actual_owner_outcome'])
        self.assertEqual(r['excluded_original_transition']['required_obligation'],'obligation:exact-owner-outcome')
        self.assertNotIn('transition:product-adoption-release:release-reviewed',transitions)
    def test_another_schema_valid_Capability_cannot_claim_observed_implementation(self):
        header,raw=self.capability;body=json.loads(raw);body['node_id']='product-capability:another';raw=P.enc(body);header=copy.deepcopy(header)
        header.update(identity_ref=body['node_id'],version_ref=body['node_id']+'@foundation.1',byte_sha256=P.sha(raw));self.capability=(header,raw)
        with self.assertRaisesRegex(ValueError,'another Capability'):self.run_factory()
    def test_header_original_substitution_refused(self):
        header,raw=self.product;self.product=(header,raw+b' ')
        with self.assertRaisesRegex(ValueError,'original differs'):self.run_factory()
    def test_old_Work_Goal_retarget_refused(self):
        self.profile['original_work']['identity_ref']='work:another'
        with self.assertRaisesRegex(ValueError,'profile changed'):self.run_factory()

if __name__=='__main__':unittest.main()
