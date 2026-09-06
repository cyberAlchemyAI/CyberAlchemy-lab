import {readdirSync,readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {describe,expect,it} from "vitest";
import type {DirectionalMappingObservation,MappingRelationAssertion} from "../contracts/mapping-contracts.js";
import {evaluateDirectionalMapping,evaluateMappingRelation} from "./evaluate-mapping.js";
import {mappingRelationAssertion,settlementMappingDescriptor,settlementMappingObservation} from "../fixtures/settlement-mapping.js";

type Hostile=Readonly<{hostile_id:string;hostile_class:"type-semantic"|"rel-a-evidence";expected_code:string;mutation:Record<string,unknown>}>;
const authoritativeHostiles=Object.freeze({
  "source-target-swap.json":["map/source-target-swap","type-semantic","RMT_MAP_SOURCE_TARGET_SWAP"],
  "direction-flip.json":["map/direction-flip","type-semantic","RMT_MAP_DIRECTION_FLIP"],
  "missing-required-field.json":["map/missing-required-field","type-semantic","RMT_MAP_MISSING_REQUIRED_FIELD"],
  "undeclared-extra-field.json":["map/undeclared-extra-field","type-semantic","RMT_MAP_UNDECLARED_EXTRA_FIELD"],
  "correspondence-drift.json":["map/correspondence-drift","type-semantic","RMT_MAP_CORRESPONDENCE_DRIFT"],
  "totality-overclaim.json":["map/totality-overclaim","type-semantic","RMT_MAP_TOTALITY_OVERCLAIM"],
  "silent-coercion.json":["map/silent-coercion","type-semantic","RMT_MAP_SILENT_COERCION"],
  "effect-policy-violation.json":["map/effect-policy-violation","type-semantic","RMT_MAP_EFFECT_POLICY_VIOLATION"],
  "failure-as-success.json":["map/failure-as-success","type-semantic","RMT_MAP_FAILURE_AS_SUCCESS"],
  "failure-detail-loss.json":["map/failure-detail-loss","type-semantic","RMT_MAP_FAILURE_DETAIL_LOSS"],
  "relation-owner-evidence-stale.json":["map/relation-owner-evidence-stale","rel-a-evidence","RMT_RELATION_OWNER_EVIDENCE_STALE"],
  "relation-source-endpoint-mismatch.json":["map/relation-source-endpoint-mismatch","rel-a-evidence","RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
  "relation-target-endpoint-mismatch.json":["map/relation-target-endpoint-mismatch","rel-a-evidence","RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
  "materialized-without-exact-assertion.json":["map/materialized-without-exact-assertion","rel-a-evidence","RMT_RELATION_ASSERTION_REQUIRED"],
} as const);
const hostileDir=fileURLToPath(new URL("../hostiles/",import.meta.url));
const hostileFiles=Object.keys(authoritativeHostiles).sort();
const hostiles=hostileFiles.map((filename)=>({filename,fixture:JSON.parse(readFileSync(fileURLToPath(new URL(`../hostiles/${filename}`,import.meta.url)),"utf8")) as Hostile,expected:authoritativeHostiles[filename as keyof typeof authoritativeHostiles]}));
describe("directional Mapping family",()=>{
  it("passes the W3-derived structured mapping extension",()=>{expect(evaluateDirectionalMapping(settlementMappingDescriptor,settlementMappingObservation())).toMatchObject({verdict:"pass",findings:[],authority_effect:"none"});});
  it("binds the authoritative 10 semantic and 4 REL-A hostile map",()=>{
    expect(readdirSync(hostileDir).sort()).toEqual(hostileFiles);expect(hostiles).toHaveLength(14);
    expect(new Set(hostiles.map(({expected})=>expected[0])).size).toBe(14);
    expect(hostiles.filter(({expected})=>expected[1]==="type-semantic")).toHaveLength(10);expect(hostiles.filter(({expected})=>expected[1]==="rel-a-evidence")).toHaveLength(4);
    for(const {filename,fixture:hostile,expected} of hostiles){
      expect([hostile.hostile_id,hostile.hostile_class,hostile.expected_code],filename).toEqual(expected);expect(Object.keys(hostile.mutation).length).toBeGreaterThan(0);
      const result=expected[1]==="type-semantic"
        ?evaluateDirectionalMapping(settlementMappingDescriptor,{...settlementMappingObservation(),...hostile.mutation} as DirectionalMappingObservation)
        :evaluateMappingRelation({...mappingRelationAssertion(),...hostile.mutation} as MappingRelationAssertion);
      expect(result.verdict,hostile.hostile_id).toBe("reject");expect(result.findings.map(({code})=>code),hostile.hostile_id).toEqual([expected[2]]);
    }
  });
});
