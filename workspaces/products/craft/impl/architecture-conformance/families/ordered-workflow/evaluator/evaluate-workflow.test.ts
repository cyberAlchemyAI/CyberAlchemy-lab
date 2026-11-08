import {readdirSync,readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {describe,expect,it} from "vitest";
import type {OrderedWorkflowObservation,WorkflowRelationAssertion} from "../contracts/workflow-contracts.js";
import {evaluateOrderedWorkflow,evaluateWorkflowRelation,evaluateWorkflowS1Binding} from "./evaluate-workflow.js";
import {settlementWorkflowDescriptor,settlementWorkflowObservation,workflowRelationAssertion} from "../fixtures/settlement-workflow.js";
type Hostile=Readonly<{hostile_id:string;hostile_class:"type-semantic"|"rel-a-evidence";expected_code:string;mutation:Record<string,unknown>;s1_control?:Readonly<{hostile_id:string;hostile_class:"s1-cross-boundary";expected_code:string;mutation:Record<string,unknown>}>}>;
const frozenCatalogue=JSON.parse(readFileSync("projects/domainspec-v2/development/refinement-runs/20260814T193343Z-active-meta-type-implementations/refreshes/20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/HOSTILE-CATALOGUE.json","utf8"));
const authoritativeHostiles=Object.freeze({
 "compensation-overclaim.json":["wf/compensation-overclaim","type-semantic","RMT_WF_COMPENSATION_OVERCLAIM"],
 "executes-effect.json":["wf/executes-effect","type-semantic","RMT_WF_EXECUTES_EFFECT"],
 "failure-continuation-mismatch.json":["wf/failure-continuation-mismatch","type-semantic","RMT_WF_FAILURE_CONTINUATION_MISMATCH"],
 "guard-bypass.json":["wf/guard-bypass","type-semantic","RMT_WF_GUARD_BYPASS"],
 "lifecycle-transition-bypass.json":["wf/lifecycle-transition-bypass","type-semantic","RMT_WF_LIFECYCLE_TRANSITION_BYPASS"],
 "materialized-without-exact-assertion.json":["wf/materialized-without-exact-assertion","rel-a-evidence","RMT_RELATION_ASSERTION_REQUIRED"],
 "relation-owner-evidence-stale.json":["wf/relation-owner-evidence-stale","rel-a-evidence","RMT_RELATION_OWNER_EVIDENCE_STALE"],
 "relation-source-endpoint-mismatch.json":["wf/relation-source-endpoint-mismatch","rel-a-evidence","RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
 "relation-target-endpoint-mismatch.json":["wf/relation-target-endpoint-mismatch","rel-a-evidence","RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
 "scope-drift.json":["wf/scope-drift","type-semantic","RMT_WF_SCOPE_DRIFT"],
 "stale-binding.json":["wf/stale-binding","type-semantic","RMT_WF_STALE_BINDING"],
 "step-duplicate.json":["wf/step-duplicate","type-semantic","RMT_WF_STEP_DUPLICATE"],
 "step-reorder.json":["wf/step-reorder","type-semantic","RMT_WF_STEP_REORDER"],
 "step-skip.json":["wf/step-skip","type-semantic","RMT_WF_STEP_SKIP"]
} as const);
const hostileDir=fileURLToPath(new URL("../hostiles/",import.meta.url)),hostileFiles=Object.keys(authoritativeHostiles).sort(),hostiles=hostileFiles.map(filename=>({filename,fixture:JSON.parse(readFileSync(fileURLToPath(new URL("../hostiles/"+filename,import.meta.url)),"utf8")) as Hostile,expected:authoritativeHostiles[filename as keyof typeof authoritativeHostiles]}));
describe("ordered Workflow family",()=>{
 it("passes unchanged W4 ordering with exact S1 bindings and forward recovery semantics",()=>{expect(evaluateOrderedWorkflow(settlementWorkflowDescriptor,settlementWorkflowObservation())).toMatchObject({verdict:"pass",findings:[],authority_effect:"none"});expect(evaluateWorkflowS1Binding(settlementWorkflowDescriptor,settlementWorkflowObservation())).toMatchObject({verdict:"pass",findings:[]});});
 it("binds 15 frozen control identities across exactly 14 fixture paths",()=>{expect(readdirSync(hostileDir).sort()).toEqual(hostileFiles);expect(hostiles).toHaveLength(14);expect(hostiles.filter(({expected})=>expected[1]==="type-semantic")).toHaveLength(10);expect(hostiles.filter(({expected})=>expected[1]==="rel-a-evidence")).toHaveLength(4);
  for(const{filename,fixture:hostile,expected}of hostiles){expect([hostile.hostile_id,hostile.hostile_class,hostile.expected_code],filename).toEqual(expected);expect(Object.keys(hostile.mutation).length).toBeGreaterThan(0);const result=expected[1]==="type-semantic"?evaluateOrderedWorkflow(settlementWorkflowDescriptor,{...settlementWorkflowObservation(),...hostile.mutation} as OrderedWorkflowObservation):evaluateWorkflowRelation({...workflowRelationAssertion(),...hostile.mutation} as WorkflowRelationAssertion);expect(result.verdict,hostile.hostile_id).toBe("reject");expect(result.findings.map(({code})=>code),hostile.hostile_id).toEqual([expected[2]]);}
  const shared=hostiles.find(({filename})=>filename==="stale-binding.json")!.fixture as any,baseRow=frozenCatalogue.groups.find(({prefix}:{prefix:string})=>prefix==="WF").controls.find(({hostile_id}:{hostile_id:string})=>hostile_id==="wf/stale-binding"),s1Row=frozenCatalogue.cross_type_controls.find(({hostile_id}:{hostile_id:string})=>hostile_id==="s1/stale-binding");
  expect(Object.keys(shared).sort()).toEqual(["expected_code","fixture_owner_swu","hostile_class","hostile_id","mutation","non_noop_required","proof_owner_swu","s1_control"]);
  expect(Object.keys(shared.s1_control).sort()).toEqual(["category","expected_code","fixture_owner_swu","hostile_class","hostile_id","mutation","non_noop_required","proof_owner_swu","required_observation","required_outcome"]);
  expect({hostile_id:shared.hostile_id,hostile_class:shared.hostile_class,expected_code:shared.expected_code,fixture_owner_swu:shared.fixture_owner_swu,proof_owner_swu:shared.proof_owner_swu,non_noop_required:shared.non_noop_required}).toEqual({hostile_id:baseRow.hostile_id,hostile_class:baseRow.hostile_class,expected_code:baseRow.expected_code,fixture_owner_swu:baseRow.fixture_owner_swu,proof_owner_swu:baseRow.proof_owner_swu,non_noop_required:baseRow.non_noop_required});
  expect({hostile_id:shared.s1_control.hostile_id,hostile_class:shared.s1_control.hostile_class,expected_code:shared.s1_control.expected_code,fixture_owner_swu:shared.s1_control.fixture_owner_swu,proof_owner_swu:shared.s1_control.proof_owner_swu,non_noop_required:shared.s1_control.non_noop_required,category:shared.s1_control.category,required_observation:shared.s1_control.required_observation,required_outcome:shared.s1_control.required_outcome}).toEqual({hostile_id:s1Row.hostile_id,hostile_class:s1Row.hostile_class,expected_code:s1Row.expected_code,fixture_owner_swu:s1Row.fixture_owner_swu,proof_owner_swu:s1Row.proof_owner_swu,non_noop_required:s1Row.non_noop_required,category:s1Row.category,required_observation:s1Row.required_observation,required_outcome:s1Row.required_outcome});
  expect(baseRow.fixture_path).toBe(s1Row.fixture_path);expect(baseRow.fixture_path).toBe("projects/domainspec-v2/impl/architecture-conformance/families/ordered-workflow/hostiles/stale-binding.json");expect(Object.keys(shared.mutation)).toEqual(["binding_state"]);expect(Object.keys(shared.s1_control.mutation)).toEqual(["s1_binding_state"]);expect(JSON.stringify([shared.mutation,shared.s1_control.mutation])).not.toContain("RMT_");
  const s1=evaluateWorkflowS1Binding(settlementWorkflowDescriptor,{...settlementWorkflowObservation(),...shared.s1_control.mutation});expect(s1.findings.map(({code})=>code)).toEqual(["RMT_S1_STALE_BINDING"]);expect(evaluateOrderedWorkflow(settlementWorkflowDescriptor,{...settlementWorkflowObservation(),...shared.s1_control.mutation}).findings).toEqual([]);expect(readFileSync(fileURLToPath(new URL("./evaluate-workflow.ts",import.meta.url)),"utf8")).not.toContain("expected_code");
 });
});
