import copy,dataclasses,importlib.util,json,pathlib,sys,unittest
MODULE_PATH=pathlib.Path(__file__).with_name("remaining_types")/"mapping_v1.py"
SPEC=importlib.util.spec_from_file_location("mapping_v1",MODULE_PATH);assert SPEC and SPEC.loader
MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
def baseline()->dict:
    correspondence=[{"source":"id","target":"settlement_id","required":True},{"source":"player_id","target":"player_id","required":True},{"source":"amount","target":"amount","required":True}]
    descriptor={"source_contract_id":"SettlementRecord/v1","target_contract_id":"SettlementResponse/v1","direction":"forward","correspondence":correspondence,"totality":"partial-fallible","failure_contract_id":"MappingFailure/v1","effect_policy":"none"}
    observation={"source_contract_id":"SettlementRecord/v1","target_contract_id":"SettlementResponse/v1","direction":"forward","observed_correspondence":copy.deepcopy(correspondence),"missing_required_fields":[],"undeclared_extra_fields":[],"totality":"partial-fallible","coercions":[],"effect_policy":"none","effects":[],"failure_outcome":{"status":"failure","code":"MAPPING_INPUT_INVALID","details":["missing:id"]}}
    w3c=[{"source":"id","target":"settlement_id","mode":"direct"},{"source":"player_id","target":"player_id","mode":"direct"},{"source":"amount","target":"amount","mode":"direct"}]
    return {"descriptor":descriptor,"observation":observation,"w3_descriptor":{"source_contract_id":"SettlementRecord/v1","target_contract_id":"SettlementResponse/v1","direction":"forward","correspondence":w3c,"effect_policy":"none"},"w3_observation":{"source_contract_id":"SettlementRecord/v1","target_contract_id":"SettlementResponse/v1","direction":"forward","observed_correspondence":copy.deepcopy(w3c),"effects":[]}}
class MappingV1Test(unittest.TestCase):
    def test_native_failure_is_frozen_and_normalizes(self)->None:
        failure=MODULE.MappingFailure("MAPPING_INPUT_INVALID",("missing:id",))
        with self.assertRaises(dataclasses.FrozenInstanceError): failure.code="OTHER"
        result=MODULE.evaluate_case(baseline());self.assertEqual(result["portable"]["meta_type"],"Mapping");self.assertEqual(result["native_evidence"]["language"],"python")
    def test_replays_all_ten_semantic_controls(self)->None:
        root=pathlib.Path(__file__).parents[3];hostile_dir=root/"architecture-conformance/families/directional-mapping/hostiles"
        semantic=sorted(path for path in hostile_dir.glob("*.json") if json.loads(path.read_text())["hostile_class"]=="type-semantic");self.assertEqual(len(semantic),10)
        for path in semantic:
            hostile=json.loads(path.read_text());case=baseline();case["observation"].update(copy.deepcopy(hostile["mutation"]));verdict,findings=MODULE.evaluate_mapping(case["descriptor"],case["observation"]);self.assertEqual((verdict,findings),("reject",(hostile["expected_code"],)),hostile["hostile_id"])
if __name__=="__main__": unittest.main()
