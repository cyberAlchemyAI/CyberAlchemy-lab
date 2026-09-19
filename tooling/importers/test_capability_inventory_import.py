import copy
import unittest
import capability_inventory_import as tool

class InventoryTests(unittest.TestCase):
    def test_nested_registry_and_escaped_selector(self):
        data={'a/b':[{'capability_id':'cap','outcome':'useful'}]}
        found=[(p,tool.classify(r)) for p,r in tool.walk(data) if tool.classify(r)]
        self.assertEqual(found,[('/a~1b/0','declaration')])
    def test_reference_does_not_become_instance(self):
        self.assertEqual(tool.classify({'capability_id':'cap','sha256':'x'}),'reference-or-support')
        self.assertEqual(tool.classify({'id':'Team','role':'collective_actor'}),None)
    def test_agent_not_misclassified_as_product(self):
        self.assertEqual(tool.classify({'capability_id':'agent','schema_version':'cav2.agent-capability/v1','outcome':'run'}),'agent-declaration')
    def test_conflicting_same_scope_is_rejected(self):
        index={'p':[{'source':{'path':'a/nodes.json','selector':'/0'},'record':{'id':'p','label':'one'}},{'source':{'path':'a/other.json','selector':'/0'},'record':{'id':'p','label':'two'}}]}
        with self.assertRaisesRegex(ValueError,'ambiguous'):tool.resolve(index,'p','a/capability.json')
    def test_source_package_precedes_distant_projection(self):
        near={'source':{'path':'a/nodes.json','selector':'/0'},'record':{'id':'p','label':'one'}}
        far={'source':{'path':'b/nodes.json','selector':'/0'},'record':{'id':'p','label':'two'}}
        self.assertEqual(tool.resolve({'p':[far,near]},'p','a/capability.json'),near)
    def test_unresolved_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'unresolved'):tool.resolve({},'no-such-product','a/capability.json')
    def test_missing_product_blocks_before_validation(self):
        with self.assertRaisesRegex(ValueError,'Product reference'):
            tool.normalize({'record':{'capability_id':'cap'},'source':{'path':'a.json'}},{},None,'scope')

class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tool.load_registry()
        import sys
        sys.path.insert(0,str(tool.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
        import engine
        cls.engine=engine
    def fixture(self):
        product={'source':{'path':'a/nodes.json','selector':'/nodes/0'},'record':{'id':'p','role':'product','label':'Product','plain_language':'Useful purpose','forbidden_collapse':'Bounded identity','owner_route':'Product owner'}}
        cap={'source':{'path':'a/capability.json','selector':''},'record':{'capability_id':'cap','product_ref':'p','outcome':'Useful outcome','owner_route':'Capability owner','exclusions':['No effects'],'acceptance_conditions':['Exact source preserved']}}
        return product,cap
    def test_candidate_validates_without_team_or_realization(self):
        product,cap=self.fixture()
        result=tool.normalize(cap,{'p':[product]},self.engine,'migration')
        self.assertEqual(result['capability']['kind'],'product-capability')
        self.assertEqual(result['capability']['status'],'candidate-unadmitted')
        self.assertEqual(result['capability']['authority_effect'],'none')
    def test_explicit_parent_supplies_product(self):
        product,cap=self.fixture();parent=copy.deepcopy(cap);parent['record']['capability_id']='parent'
        del cap['record']['product_ref'];cap['record']['parent_capability_ref']='parent'
        result=tool.normalize(cap,{'p':[product],'parent':[parent]},self.engine,'migration')
        self.assertEqual(result['capability']['product_ref'],result['product']['node_id'])
        self.assertIn(parent['source'],result['resolved_sources'])
    def test_cyclic_parent_chain_rejected(self):
        product,cap=self.fixture();del cap['record']['product_ref'];cap['record']['parent_capability_ref']='parent'
        parent=copy.deepcopy(cap);parent['record']['capability_id']='parent';parent['record']['parent_capability_ref']='cap'
        with self.assertRaisesRegex(ValueError,'cyclic'):
            tool.normalize(cap,{'p':[product],'parent':[parent],'cap':[cap]},self.engine,'migration')
    def test_missing_declared_input_rejected(self):
        product,cap=self.fixture();cap['record']['input_contract_refs']=['missing-input']
        with self.assertRaisesRegex(ValueError,'unresolved'):
            tool.normalize(cap,{'p':[product]},self.engine,'migration')

if __name__=='__main__':unittest.main()
