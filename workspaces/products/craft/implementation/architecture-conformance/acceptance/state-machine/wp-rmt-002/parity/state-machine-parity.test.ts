import {existsSync,readdirSync,rmdirSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {stateMachineTypeScriptV1Provider} from "../../../../factory/registry/providers/state-machine-typescript-v1.js";
import {stateMachinePythonV1Provider} from "../../../../factory/registry/providers/state-machine-python-v1.js";
import {stateMachineRustV1Provider} from "../../../../factory/registry/providers/state-machine-rust-v1.js";
import {makeSettlementStateMachineCase} from "../../../../targets/typescript/state-machine-v1.js";
const canonical=(value:unknown):unknown=>Array.isArray(value)?value.map(canonical):value&&typeof value==="object"?Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b)).map(([key,item])=>[key,canonical(item)])):value;
describe("WP-RMT-002 State Machine direct-provider parity",()=>{it("matches deterministic W4 outcomes and returned intents across all providers",async()=>{
  const cargoRoot="projects/domainspec-v2/development/remaining-meta-types/runs/state-machine/cargo-target";expect(existsSync(cargoRoot),"pre-existing transient root blocks proof").toBe(false);
  const providers=[stateMachineTypeScriptV1Provider,stateMachinePythonV1Provider,stateMachineRustV1Provider],input={raw_inputs:{state_machine_case:JSON.stringify(makeSettlementStateMachineCase())}} as never;
  const first=await Promise.all(providers.map(provider=>provider.execute(input))),second=await Promise.all(providers.map(provider=>provider.execute(input)));
  expect(first.map(({provider_id})=>provider_id)).toEqual(["state-machine-typescript-v1","state-machine-python-v1","state-machine-rust-v1"]);
  for(const results of[first,second]){expect(results.every(({result})=>result==="pass")).toBe(true);const outputs=results.map((result:any)=>result.semantic_output);const portable=outputs.map(({portable}:any)=>canonical(portable));expect(portable[1]).toEqual(portable[0]);expect(portable[2]).toEqual(portable[0]);expect(outputs.map(({native_evidence}:any)=>native_evidence.language)).toEqual(["typescript","python","rust"]);expect(new Set(outputs.map(({native_evidence}:any)=>native_evidence.mechanism)).size).toBe(3);expect(outputs.some((output:any)=>"native_sha256" in output)).toBe(false);expect(portable[0].transition_results.map(({accepted,next_state}:any)=>[accepted,next_state])).toEqual([[true,"settled"],[true,"failed"],[false,null]]);expect(portable[0].effects_performed_inline).toBe(false);}
  expect((second[0] as any).semantic_output.portable).toEqual((first[0] as any).semantic_output.portable);
  const baseline=makeSettlementStateMachineCase(),stale={...baseline,dependency_handles:{...baseline.dependency_handles,rule:{...baseline.dependency_handles.rule,sha256:"b".repeat(64)}}},extra={...baseline,execute_effects:true};
  for(const bad of[stale,extra]){const rejected=await Promise.all(providers.map(async provider=>{try{await provider.execute({raw_inputs:{state_machine_case:JSON.stringify(bad)}} as never);return false;}catch(error){expect(error).toBeInstanceOf(Error);return true;}}));expect(rejected).toEqual([true,true,true]);}
  expect(readdirSync(cargoRoot)).toEqual([]);rmdirSync(cargoRoot);expect(existsSync(cargoRoot)).toBe(false);
},120_000);});
