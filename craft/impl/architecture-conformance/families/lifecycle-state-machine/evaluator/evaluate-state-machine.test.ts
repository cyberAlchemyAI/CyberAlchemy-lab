import {readdirSync,readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {describe,expect,it} from "vitest";
import type {LifecycleStateMachineObservation,StateMachineRelationAssertion} from "../contracts/state-machine-contracts.js";
import {decodeReturnedEffectIntent,evaluateLifecycleStateMachine,evaluateStateMachineRelation} from "./evaluate-state-machine.js";
import {settlementStateMachineDescriptor,settlementStateMachineObservation,stateMachineRelationAssertion} from "../fixtures/settlement-state-machine.js";
type Hostile=Readonly<{hostile_id:string;hostile_class:"type-semantic"|"rel-a-evidence"|"s1-cross-boundary";expected_code:string;mutation:Record<string,unknown>}>;
const frozenCatalogue=JSON.parse(readFileSync("projects/domainspec-v2/development/refinement-runs/20260814T193343Z-active-meta-type-implementations/refreshes/20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/HOSTILE-CATALOGUE.json","utf8"));
const authoritativeHostiles=Object.freeze({
  "closed-decode.json":["s1/closed-decode","s1-cross-boundary","RMT_S1_CLOSED_DECODE_UNKNOWN_MEMBER"],
  "cycle-policy-mismatch.json":["sm/cycle-policy-mismatch","type-semantic","RMT_SM_CYCLE_POLICY_MISMATCH"],
  "executes-effect.json":["sm/executes-effect","type-semantic","RMT_SM_EXECUTES_EFFECT"],
  "guard-bypass.json":["sm/guard-bypass","type-semantic","RMT_SM_GUARD_BYPASS"],
  "hidden-mutation.json":["sm/hidden-mutation","type-semantic","RMT_SM_HIDDEN_MUTATION"],
  "illegal-transition.json":["sm/illegal-transition","type-semantic","RMT_SM_ILLEGAL_TRANSITION"],
  "initial-state-drift.json":["sm/initial-state-drift","type-semantic","RMT_SM_INITIAL_STATE_DRIFT"],
  "invalid-transition-success.json":["sm/invalid-transition-success","type-semantic","RMT_SM_INVALID_TRANSITION_SUCCESS"],
  "materialized-without-exact-assertion.json":["sm/materialized-without-exact-assertion","rel-a-evidence","RMT_RELATION_ASSERTION_REQUIRED"],
  "nondeterministic-transition.json":["sm/nondeterministic-transition","type-semantic","RMT_SM_NONDETERMINISTIC_TRANSITION"],
  "relation-owner-evidence-stale.json":["sm/relation-owner-evidence-stale","rel-a-evidence","RMT_RELATION_OWNER_EVIDENCE_STALE"],
  "relation-source-endpoint-mismatch.json":["sm/relation-source-endpoint-mismatch","rel-a-evidence","RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
  "relation-target-endpoint-mismatch.json":["sm/relation-target-endpoint-mismatch","rel-a-evidence","RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
  "terminal-state-drift.json":["sm/terminal-state-drift","type-semantic","RMT_SM_TERMINAL_STATE_DRIFT"],
  "unstable-transition-identity.json":["sm/unstable-transition-identity","type-semantic","RMT_SM_UNSTABLE_TRANSITION_IDENTITY"]
} as const);
const hostileDir=fileURLToPath(new URL("../hostiles/",import.meta.url));
const hostileFiles=Object.keys(authoritativeHostiles).sort();
const hostiles=hostileFiles.map(filename=>({filename,fixture:JSON.parse(readFileSync(fileURLToPath(new URL("../hostiles/"+filename,import.meta.url)),"utf8")) as Hostile,expected:authoritativeHostiles[filename as keyof typeof authoritativeHostiles]}));
describe("lifecycle State Machine family",()=>{
  it("passes unchanged W4 transitions under an explicit declared-only cycle policy",()=>{expect(evaluateLifecycleStateMachine(settlementStateMachineDescriptor,settlementStateMachineObservation())).toMatchObject({verdict:"pass",findings:[],authority_effect:"none"});});
  it("binds the authoritative 10 semantic, 4 REL-A, and one S1 hostile map",()=>{
    expect(readdirSync(hostileDir).sort()).toEqual(hostileFiles);expect(hostiles).toHaveLength(15);
    expect(hostiles.filter(({expected})=>expected[1]==="type-semantic")).toHaveLength(10);
    expect(hostiles.filter(({expected})=>expected[1]==="rel-a-evidence")).toHaveLength(4);
    expect(hostiles.filter(({expected})=>expected[1]==="s1-cross-boundary")).toHaveLength(1);
    for(const{filename,fixture:hostile,expected}of hostiles){
      expect([hostile.hostile_id,hostile.hostile_class,hostile.expected_code],filename).toEqual(expected);
      expect(Object.keys(hostile.mutation).length).toBeGreaterThan(0);
      if(expected[1]==="s1-cross-boundary"){
        const exactKeys=["category","expected_code","fixture_owner_swu","hostile_class","hostile_id","mutation","non_noop_required","proof_owner_swu","required_observation","required_outcome"];
        expect(Object.keys(hostile).sort()).toEqual(exactKeys);
        const row=frozenCatalogue.cross_type_controls.find((item:{hostile_id:string})=>item.hostile_id==="s1/closed-decode");
        expect(row).toBeTruthy();
        expect({hostile_id:hostile.hostile_id,hostile_class:hostile.hostile_class,expected_code:hostile.expected_code,fixture_owner_swu:(hostile as any).fixture_owner_swu,proof_owner_swu:(hostile as any).proof_owner_swu,non_noop_required:(hostile as any).non_noop_required,category:(hostile as any).category,required_observation:(hostile as any).required_observation,required_outcome:(hostile as any).required_outcome}).toEqual({hostile_id:row.hostile_id,hostile_class:row.hostile_class,expected_code:row.expected_code,fixture_owner_swu:row.fixture_owner_swu,proof_owner_swu:row.proof_owner_swu,non_noop_required:row.non_noop_required,category:row.category,required_observation:row.required_observation,required_outcome:row.required_outcome});
        expect(row.fixture_path).toBe("projects/domainspec-v2/impl/architecture-conformance/families/lifecycle-state-machine/hostiles/closed-decode.json");
        expect(JSON.stringify(hostile.mutation)).not.toContain(hostile.expected_code);
        expect(readFileSync(fileURLToPath(new URL("./evaluate-state-machine.ts",import.meta.url)),"utf8")).not.toContain("expected_code");
        expect(()=>decodeReturnedEffectIntent(hostile.mutation.effect_intent)).toThrowError(expected[2]);continue;
      }
      const result=expected[1]==="type-semantic"?evaluateLifecycleStateMachine(settlementStateMachineDescriptor,{...settlementStateMachineObservation(),...hostile.mutation} as LifecycleStateMachineObservation):evaluateStateMachineRelation({...stateMachineRelationAssertion(),...hostile.mutation} as StateMachineRelationAssertion);
      expect(result.verdict,hostile.hostile_id).toBe("reject");
      expect(result.findings.map(({code})=>code),hostile.hostile_id).toEqual([expected[2]]);
    }
  });
});
