import {describe, expect, it} from "vitest";
import {evaluateInterfaceCase, makeSettlementInterfaceCase} from "./interface-v1.js";

describe("TypeScript Interface v1 target", () => {
  it("reuses W3 and closes the versioned boundary extension", () => {
    const result = evaluateInterfaceCase(makeSettlementInterfaceCase());
    expect(result.portable).toMatchObject({
      result:"pass", meta_type:"Interface", contract_id:"SettlementPort", version:"1.2.0",
      compatibility_direction:"consumer-to-provider", transport_domain_separated:true, authority_effect:"none",
    });
    expect(result.portable.exposed_bindings).toEqual(["Operation:completeSettlement", "Query:findSettlement"]);
    expect(result.native_evidence).toEqual({language:"typescript",mechanism:"readonly-type-and-frozen-boundary"});
  });

  it("rejects a W3 compatibility overclaim before normalization", () => {
    const input = makeSettlementInterfaceCase();
    expect(() => evaluateInterfaceCase({...input, w3_observation:{...input.w3_observation, compatibility_checks:[
      {requested_version:"1.2.0",accepted:true}, {requested_version:"2.0.0",accepted:true},
    ]}})).toThrowError(/ARCH_INTERFACE_COMPATIBILITY_DRIFT/);
  });
});
