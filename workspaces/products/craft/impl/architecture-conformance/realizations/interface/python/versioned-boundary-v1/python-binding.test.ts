import {describe, expect, it} from "vitest";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {interfacePythonV1Provider} from "../../../../factory/registry/providers/interface-python-v1.js";
import {makeSettlementInterfaceCase} from "../../../../targets/typescript/interface-v1.js";

describe("Interface Python realization binding", () => {
  it("hash-closes target and provider bytes",()=>{
    const binding=JSON.parse(readFileSync("projects/domainspec-v2/impl/architecture-conformance/realizations/interface/python/versioned-boundary-v1/python-binding.json","utf8"));
    for(const ref of [binding.target,binding.provider,binding.w3_observer,binding.interface_extension]){
      const bytes=readFileSync(ref.path);
      expect(createHash("sha256").update(bytes).digest("hex")).toBe(ref.sha256);
      if(ref.size_bytes!==undefined) expect(bytes.length).toBe(ref.size_bytes);
    }
    expect(binding.registered).toBe(false);
  });
  it("executes the native target and keeps native evidence separate", async () => {
    const result = await interfacePythonV1Provider.execute({raw_inputs:{interface_case:JSON.stringify(makeSettlementInterfaceCase())}} as never);
    expect(result).toMatchObject({result:"pass",provider_id:"interface-python-v1",authority_effect:"none"});
    expect(result.semantic_output).toMatchObject({portable:{meta_type:"Interface",contract_id:"SettlementPort"},native_evidence:{language:"python"}});
  });
});
