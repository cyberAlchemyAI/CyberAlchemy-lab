import {describe,expect,it} from "vitest";
import {evaluateMappingCase,makeSettlementMappingCase} from "./mapping-v1.js";
describe("TypeScript Mapping v1 target",()=>{
  it("reuses W3 and closes the directional structured-failure extension",()=>{
    const result=evaluateMappingCase(makeSettlementMappingCase());
    expect(result.portable).toMatchObject({result:"pass",meta_type:"Mapping",source_contract_id:"SettlementRecord/v1",target_contract_id:"SettlementResponse/v1",direction:"forward",totality:"partial-fallible",structured_failure_preserved:true,silent_coercion_rejected:true,authority_effect:"none"});
    expect(result.native_evidence.language).toBe("typescript");
  });
  it("rejects W3 endpoint drift before portable normalization",()=>{
    const input=makeSettlementMappingCase();
    expect(()=>evaluateMappingCase({...input,w3_observation:{...input.w3_observation,source_contract_id:"SettlementResponse/v1"}})).toThrowError(/ARCH_MAPPING_ENDPOINT_DRIFT/);
  });
});
