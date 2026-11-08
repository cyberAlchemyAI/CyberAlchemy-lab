import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import type {InterfaceRelationAssertion} from "../../../../families/versioned-interface-boundary/contracts/interface-contracts.js";
import {evaluateInterfaceRelation} from "../../../../families/versioned-interface-boundary/evaluator/evaluate-interface.js";
import {interfaceRelationAssertion} from "../../../../families/versioned-interface-boundary/fixtures/settlement-interface.js";

const relations=[
  {contract_id:"interface/exposes",architecture_relation_id:"architecture.exposes",source_types:["architecture.InterfaceImplementation"],target_types:["architecture.OperationImplementation","architecture.QueryImplementation"],owner:"source Interface candidate"},
  {contract_id:"interface/implemented-by-adapter",architecture_relation_id:"architecture.implements_interface",source_types:["architecture.AdapterImplementation"],target_types:["architecture.InterfaceImplementation"],owner:"source Adapter candidate"},
] as const;

describe("WP-RMT-002 Interface REL-A blueprints",()=>{
  it("binds exact directions and deliberately leaves contracts/maps unmapped",()=>{
    expect(relations.map(({contract_id})=>contract_id)).toEqual(["interface/exposes","interface/implemented-by-adapter"]);
    expect(relations[0]).toMatchObject({source_types:["architecture.InterfaceImplementation"],target_types:["architecture.OperationImplementation","architecture.QueryImplementation"]});
    expect(relations[1]).toMatchObject({source_types:["architecture.AdapterImplementation"],target_types:["architecture.InterfaceImplementation"]});
    expect(["contracts","maps"]).toEqual(["contracts","maps"]);
    expect(evaluateInterfaceRelation(interfaceRelationAssertion()).verdict).toBe("pass");
    expect(evaluateInterfaceRelation(interfaceRelationAssertion("interface/implemented-by-adapter")).verdict).toBe("pass");
  });
  it("kills all four exact REL-A evidence hostiles without materializing authority",()=>{
    const names=["relation-owner-evidence-stale","relation-source-endpoint-mismatch","relation-target-endpoint-mismatch","materialized-without-exact-assertion"];
    for(const name of names){
      const hostile=JSON.parse(readFileSync(`projects/domainspec-v2/impl/architecture-conformance/families/versioned-interface-boundary/hostiles/${name}.json`,"utf8"));
      const result=evaluateInterfaceRelation({...interfaceRelationAssertion(),...hostile.mutation} as InterfaceRelationAssertion);
      expect(result.findings.map(({code})=>code),hostile.hostile_id).toEqual([hostile.expected_code]);
      expect(result.authority_effect).toBe("none");
    }
  });
});
