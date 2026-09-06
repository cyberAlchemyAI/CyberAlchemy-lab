import {readdirSync, readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {describe, expect, it} from "vitest";
import type {InterfaceRelationAssertion, VersionedInterfaceObservation} from "../contracts/interface-contracts.js";
import {evaluateInterfaceRelation, evaluateVersionedInterface} from "./evaluate-interface.js";
import {interfaceRelationAssertion, settlementInterfaceDescriptor, settlementInterfaceObservation} from "../fixtures/settlement-interface.js";

type Hostile = Readonly<{
  hostile_id: string;
  hostile_class: "type-semantic" | "rel-a-evidence";
  expected_code: string;
  mutation: Record<string, unknown>;
}>;

const authoritativeHostiles = Object.freeze({
  "undeclared-exposure.json": ["iface/undeclared-exposure", "type-semantic", "RMT_IFACE_UNDECLARED_EXPOSURE"],
  "exposure-drift.json": ["iface/exposure-drift", "type-semantic", "RMT_IFACE_EXPOSURE_DRIFT"],
  "internal-type-leak.json": ["iface/internal-type-leak", "type-semantic", "RMT_IFACE_INTERNAL_TYPE_LEAK"],
  "version-regression.json": ["iface/version-regression", "type-semantic", "RMT_IFACE_VERSION_REGRESSION"],
  "compatibility-overclaim.json": ["iface/compatibility-overclaim", "type-semantic", "RMT_IFACE_COMPATIBILITY_OVERCLAIM"],
  "compatibility-direction-flip.json": ["iface/compatibility-direction-flip", "type-semantic", "RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP"],
  "boundary-crossing.json": ["iface/boundary-crossing", "type-semantic", "RMT_IFACE_BOUNDARY_CROSSING"],
  "mapping-obligation-missing.json": ["iface/mapping-obligation-missing", "type-semantic", "RMT_IFACE_MAPPING_OBLIGATION_MISSING"],
  "transport-domain-collapse.json": ["iface/transport-domain-collapse", "type-semantic", "RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE"],
  "consumer-route-outside.json": ["iface/consumer-route-outside", "type-semantic", "RMT_IFACE_CONSUMER_ROUTE_OUTSIDE"],
  "relation-owner-evidence-stale.json": ["iface/relation-owner-evidence-stale", "rel-a-evidence", "RMT_RELATION_OWNER_EVIDENCE_STALE"],
  "relation-source-endpoint-mismatch.json": ["iface/relation-source-endpoint-mismatch", "rel-a-evidence", "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
  "relation-target-endpoint-mismatch.json": ["iface/relation-target-endpoint-mismatch", "rel-a-evidence", "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
  "materialized-without-exact-assertion.json": ["iface/materialized-without-exact-assertion", "rel-a-evidence", "RMT_RELATION_ASSERTION_REQUIRED"],
} as const);
const hostileDir = fileURLToPath(new URL("../hostiles/", import.meta.url));
const hostileFiles = Object.keys(authoritativeHostiles).sort();
const hostiles = hostileFiles.map((filename) => ({
  filename,
  fixture: JSON.parse(readFileSync(fileURLToPath(new URL(`../hostiles/${filename}`, import.meta.url)), "utf8")) as Hostile,
  expected: authoritativeHostiles[filename as keyof typeof authoritativeHostiles],
}));

describe("versioned Interface boundary family", () => {
  it("passes the exact W3-derived boundary extension", () => {
    expect(evaluateVersionedInterface(settlementInterfaceDescriptor, settlementInterfaceObservation())).toEqual({
      schema_version: "domainspec.versioned-interface-evaluation/v1",
      descriptor_id: "interface.settlement-port-v1",
      verdict: "pass",
      findings: [],
      authority_effect: "none",
    });
  });

  it("binds the authoritative 10 semantic and 4 REL-A hostile map", () => {
    expect(readdirSync(hostileDir).sort()).toEqual(hostileFiles);
    expect(hostiles).toHaveLength(14);
    expect(new Set(hostiles.map(({expected}) => expected[0])).size).toBe(14);
    expect(hostiles.filter(({expected}) => expected[1] === "type-semantic")).toHaveLength(10);
    expect(hostiles.filter(({expected}) => expected[1] === "rel-a-evidence")).toHaveLength(4);
    for (const {filename, fixture: hostile, expected} of hostiles) {
      expect([hostile.hostile_id, hostile.hostile_class, hostile.expected_code], filename).toEqual(expected);
      expect(Object.keys(hostile.mutation).length).toBeGreaterThan(0);
      const result = expected[1] === "type-semantic"
        ? evaluateVersionedInterface(
            settlementInterfaceDescriptor,
            {...settlementInterfaceObservation(), ...hostile.mutation} as VersionedInterfaceObservation,
          )
        : evaluateInterfaceRelation(
            {...interfaceRelationAssertion(), ...hostile.mutation} as InterfaceRelationAssertion,
          );
      expect(result.verdict, hostile.hostile_id).toBe("reject");
      expect(result.findings.map(({code}) => code), hostile.hostile_id).toEqual([expected[2]]);
    }
  });
});
