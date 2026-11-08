import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { extractFacts } from "./extract.js";
import { assertOutcomeFree, buildGraphLawRequest } from "./request.js";
import { fixtureGraph, fixtureProperty } from "./extract.test.js";
import type { ExactRef } from "./types.js";

const ref = (path: string): ExactRef => ({
  path,
  sha256: "a".repeat(64),
  size_bytes: 1,
});

const REQUEST_SCHEMA = fileURLToPath(new URL(
  "../../../../../development/evolvable-validation-framework/contracts/graph-law-request.v1.schema.json",
  import.meta.url,
));

function validateRequestSchema(value: unknown): void {
  execFileSync("python3", [
    "-c",
    "import json,sys; from jsonschema import Draft202012Validator; Draft202012Validator(json.load(open(sys.argv[1], encoding='utf-8'))).validate(json.load(sys.stdin))",
    REQUEST_SCHEMA,
  ], { input: `${JSON.stringify(value)}\n`, stdio: ["pipe", "pipe", "pipe"] });
}

describe("EVF L2 graph-law request", () => {
  it("builds an exact two-provider request without an expected result", () => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    const request = buildGraphLawRequest(
      "evf.l2.request.fixture.v1",
      projection,
      fixtureProperty(),
      {
        decision_ref: ref("decision.md"),
        prerequisite_ref: ref("l1.json"),
        fact_manifest_ref: ref("facts.json"),
        property_definition_ref: ref("property.json"),
        comparison_contract_ref: ref("comparison.json"),
        scope_contract_ref: ref("scope.json"),
        project_id: "financial-settlement",
        source_set_digest: "b".repeat(64),
        registry_digests: {
          profile: "c".repeat(64),
          kinds: "d".repeat(64),
          relationships: "e".repeat(64),
        },
        datalog: {
          provider_kind: "datalog",
          evaluator_id: "souffle",
          evaluator_version: "2.5",
          runtime_ref: ref("souffle"),
          adapter_ref: ref("datalog.ts"),
          query_or_model_ref: ref("query.dl"),
          invocation_contract_ref: ref("runtime.json"),
        },
        alloy: {
          provider_kind: "alloy",
          evaluator_id: "alloy",
          evaluator_version: "6.2.0",
          runtime_ref: ref("alloy.jar"),
          adapter_ref: ref("alloy.ts"),
          query_or_model_ref: ref("model.als"),
          invocation_contract_ref: ref("runtime.json"),
        },
        working_directory: "evidence/attempt-001",
      },
    );
    expect(request.request_state).toBe("execution-ready");
    expect(request.providers.map((provider) => provider.provider_kind)).toEqual(["datalog", "alloy"]);
    expect(JSON.stringify(request)).not.toContain("expected_result");
    expect(request.claim_ceiling).toBe("request-only-no-evaluation-claim");
    expect(() => validateRequestSchema(request)).not.toThrow();
  });

  it("rejects an injected expected result at any depth", () => {
    expect(() => assertOutcomeFree({ property: { expected_result: "pass" } }))
      .toThrowError(expect.objectContaining({ code: "GRAPH_REQUEST_SCHEMA_INVALID" }));
  });
});
