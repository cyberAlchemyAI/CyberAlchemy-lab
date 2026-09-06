import copy,dataclasses,importlib.util,json,pathlib,sys,unittest
MODULE_PATH=pathlib.Path(__file__).with_name("remaining_types")/"state_machine_v1.py"
SPEC=importlib.util.spec_from_file_location("state_machine_v1",MODULE_PATH);assert SPEC and SPEC.loader
MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
ROOT=pathlib.Path(__file__).parents[3]
def baseline()->dict:
    descriptor={"semantic_plan_epoch_id":"WP-RMT-002/S1/2026-08-16","semantic_contract_digest":"75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7","state_ids":["pending","settled","failed"],"initial_state":"pending","terminal_states":["settled","failed"],"cycle_policy":"declared-only","transitions":[{"transition_id":"sm.pending.confirm.settled/v1","from_state":"pending","trigger":"confirm","to_state":"settled"},{"transition_id":"sm.pending.reject.failed/v1","from_state":"pending","trigger":"reject","to_state":"failed"}]}
    observation={"observed_transition_ids":[item["transition_id"] for item in descriptor["transitions"]],"observed_initial_state":"pending","observed_terminal_states":["settled","failed"],"observed_cycle_policy":"declared-only","illegal_transition_observed":False,"guard_bypass_observed":False,"nondeterministic_outcome_observed":False,"effects_performed_inline":[],"undeclared_cycle_observed":False,"invalid_transition_accepted":False,"hidden_mutation_observed":False,"stable_transition_ids":True}
    requests=[{"current_state":"pending","trigger":"confirm","guard_passed":True},{"current_state":"pending","trigger":"reject","guard_passed":True},{"current_state":"settled","trigger":"confirm","guard_passed":True}]
    return {"dependency_handles":MODULE.EXPECTED_DEPENDENCIES,"descriptor":descriptor,"observation":observation,"requests":requests}
class StateMachineV1Test(unittest.TestCase):
    def test_native_pure_transition_and_closed_handle(self)->None:
        decision=MODULE.transition("pending","confirm",True);self.assertEqual((decision.next_state,decision.effect_intents),("settled",("persist-settlement","append-settlement-created")))
        with self.assertRaises(dataclasses.FrozenInstanceError):decision.accepted=False
        result=MODULE.evaluate_case(baseline());self.assertEqual([item["next_state"] for item in result["portable"]["transition_results"]],["settled","failed",None]);self.assertFalse(result["portable"]["effects_performed_inline"])
        with self.assertRaisesRegex(ValueError,"RMT_S1_CLOSED_DECODE_UNKNOWN_MEMBER"):MODULE.decode_effect_intent({"effect_intent_id":"x","payload":{},"execute":True})
    def test_replays_all_ten_semantic_controls_as_singletons(self)->None:
        hostile_dir=ROOT/"architecture-conformance/families/lifecycle-state-machine/hostiles"
        semantic=sorted(path for path in hostile_dir.glob("*.json") if json.loads(path.read_text())["hostile_class"]=="type-semantic");self.assertEqual(len(semantic),10)
        for path in semantic:
            hostile=json.loads(path.read_text());case=baseline();case["observation"].update(copy.deepcopy(hostile["mutation"]));self.assertEqual(MODULE.evaluate_state_machine(case["descriptor"],case["observation"]),(hostile["expected_code"],),hostile["hostile_id"])
if __name__=="__main__":unittest.main()
