import {describe,expect,it} from "vitest";
import {existsSync,readdirSync,rmdirSync} from "node:fs";
import {interfaceTypeScriptV1Provider} from "../../../../factory/registry/providers/interface-typescript-v1.js";
import {interfacePythonV1Provider} from "../../../../factory/registry/providers/interface-python-v1.js";
import {interfaceRustV1Provider} from "../../../../factory/registry/providers/interface-rust-v1.js";
import {makeSettlementInterfaceCase} from "../../../../targets/typescript/interface-v1.js";

describe("WP-RMT-002 Interface direct-provider parity",()=>{
  it("matches portable semantics while keeping three native mechanisms separate",async()=>{
    const cargoRoot="projects/domainspec-v2/development/remaining-meta-types/runs/interface/cargo-target";
    expect(existsSync(cargoRoot),"pre-existing transient root must be preserved and blocks this proof").toBe(false);
    const input={raw_inputs:{interface_case:JSON.stringify(makeSettlementInterfaceCase())}} as never;
    const results=await Promise.all([
      interfaceTypeScriptV1Provider.execute(input),interfacePythonV1Provider.execute(input),interfaceRustV1Provider.execute(input),
    ]);
    expect(results.map(({provider_id})=>provider_id)).toEqual(["interface-typescript-v1","interface-python-v1","interface-rust-v1"]);
    const outputs=results.map((result:any)=>result.semantic_output);
    expect(outputs[1].portable).toEqual(outputs[0].portable);
    expect(outputs[2].portable).toEqual(outputs[0].portable);
    expect(outputs.map(({native_evidence}:any)=>native_evidence.language)).toEqual(["typescript","python","rust"]);
    expect(new Set(outputs.map(({native_evidence}:any)=>native_evidence.mechanism)).size).toBe(3);
    expect(outputs.some((output:any)=>"native_sha256" in output)).toBe(false);
    expect(readdirSync(cargoRoot)).toEqual([]);
    rmdirSync(cargoRoot);
    expect(existsSync(cargoRoot)).toBe(false);
  },120_000);
});
