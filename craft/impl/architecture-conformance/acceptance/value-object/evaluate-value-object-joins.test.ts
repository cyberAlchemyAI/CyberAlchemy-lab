import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {pythonValueObjectV1Provider} from
  "../../factory/registry/providers/python-value-object-v1.js";
import {rustValueObjectV1Provider} from
  "../../factory/registry/providers/rust-value-object-v1.js";
import {typeScriptValueObjectV1Provider} from
  "../../factory/registry/providers/typescript-value-object-v1.js";
import {valueObjectParityV1Provider} from
  "../../factory/registry/providers/value-object-parity-v1.js";
import {valueObjectRelationsV1Provider} from
  "../../factory/registry/providers/value-object-relations-v1.js";
import {canonicalJson, sha256} from "../../factory/shared/canonical.js";
import {PYTHON_VALUE_OBJECT_RAW_PATHS} from
  "../../realizations/value-object/python/complete-value-v1/index.js";
import {RUST_VALUE_OBJECT_RAW_PATHS} from
  "../../realizations/value-object/rust/complete-value-v1/index.js";
import {TYPESCRIPT_VALUE_OBJECT_RAW_PATHS} from
  "../../realizations/value-object/typescript/complete-value-v1/index.js";
import {
  evaluateValueObjectParity,
  proveValueObjectParity,
  proveValueObjectRelations,
  VALUE_OBJECT_DIRECT_HANDLES,
  VALUE_OBJECT_PARITY_HANDLE,
  VALUE_OBJECT_PARITY_RAW_PATHS,
  VALUE_OBJECT_RELATION_RAW_PATHS,
} from "./evaluate-value-object-joins.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const readPaths = async (paths: Readonly<Record<string, string>>):
Promise<Record<string, string>> => Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) =>
    [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
));

let directUpstream: Record<string, FactoryUpstreamResultV1>;
let relationUpstream: Record<string, FactoryUpstreamResultV1>;
let parityInputs: Record<string, string>;
let relationInputs: Record<string, string>;

beforeAll(async () => {
  parityInputs = await readPaths(VALUE_OBJECT_PARITY_RAW_PATHS);
  relationInputs = await readPaths(VALUE_OBJECT_RELATION_RAW_PATHS);
  const results = await Promise.all([
    typeScriptValueObjectV1Provider.execute({
      raw_inputs: await readPaths(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS), upstream: {},
    }),
    pythonValueObjectV1Provider.execute({
      raw_inputs: await readPaths(PYTHON_VALUE_OBJECT_RAW_PATHS), upstream: {},
    }),
    rustValueObjectV1Provider.execute({
      raw_inputs: await readPaths(RUST_VALUE_OBJECT_RAW_PATHS), upstream: {},
    }),
  ]);
  directUpstream = Object.fromEntries(results.map((result, index) => {
    const handle = VALUE_OBJECT_DIRECT_HANDLES[index]!;
    return [handle.node_id, Object.freeze({
      node_id: handle.node_id,
      provider_id: result.provider_id,
      semantic_sha256: sha256(canonicalJson(result)),
      semantic_output: result.semantic_output,
    })];
  }));
  const parity = await valueObjectParityV1Provider.execute({
    raw_inputs: parityInputs,
    upstream: directUpstream,
  });
  relationUpstream = {
    ...directUpstream,
    [VALUE_OBJECT_PARITY_HANDLE.node_id]: Object.freeze({
      node_id: VALUE_OBJECT_PARITY_HANDLE.node_id,
      provider_id: parity.provider_id,
      semantic_sha256: sha256(canonicalJson(parity)),
      semantic_output: parity.semantic_output,
    }),
  };
}, 70_000);

describe("Value Object parity and architecture relations", () => {
  it("proves portable parity without comparing native hash bytes", () => {
    const proof = proveValueObjectParity(directUpstream, parityInputs);
    expect(proof).toMatchObject({schema_version: "ValueObjectParityProof/v1",
      result: "pass", authority_effect: "none"});
    expect(proof.composed_from.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.composed_from.map(({target_sha256, binding_sha256}) =>
      ({target_sha256, binding_sha256}))).toEqual(
      VALUE_OBJECT_DIRECT_HANDLES.map(({target_sha256, binding_sha256}) =>
        ({target_sha256, binding_sha256})),
    );
    expect(proof.obligations).toHaveLength(17);
    expect(proof.hostile_mutations).toHaveLength(18);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(JSON.stringify(proof)).toContain(
      '"native_hash_bytes_compared_cross_language":false');
    expect(JSON.stringify(proof)).not.toContain('"pid"');
  });

  it("proves exact constructed_by, validated_by, and extends_factory rows", () => {
    const ontology = JSON.parse(relationInputs.ontology!) as any;
    const relationPairs = Object.fromEntries(ontology.relation_definitions
      .filter(({relation_id: id}: any) => ["architecture.constructed_by",
        "architecture.validated_by", "architecture.extends_factory"].includes(id))
      .map(({relation_id: id, allowed_type_pairs: pairs}: any) => [id, pairs]));
    expect(relationPairs).toEqual({
      "architecture.constructed_by": [
        {source_type: "architecture.ValueObjectImplementation",
          target_type: "architecture.ValueObjectFactoryProvider"},
        {source_type: "architecture.EntityImplementation",
          target_type: "architecture.EntityFactoryProvider"},
      ],
      "architecture.validated_by": [
        {source_type: "architecture.ValueObjectFactoryProvider",
          target_type: "architecture.RuleImplementation"},
        {source_type: "architecture.EntityFactoryProvider",
          target_type: "architecture.RuleImplementation"},
      ],
      "architecture.extends_factory": [
        {source_type: "architecture.ValueObjectFactoryProvider",
          target_type: "architecture.ValueObjectFactoryProvider"},
        {source_type: "architecture.EntityFactoryProvider",
          target_type: "architecture.EntityFactoryProvider"},
      ],
    });
    const proof = proveValueObjectRelations(relationUpstream, relationInputs);
    expect(proof).toMatchObject({schema_version: "ValueObjectRelationsProof/v1",
      result: "pass", authority_effect: "none"});
    expect(proof.obligations).toHaveLength(11);
    expect(proof.hostile_mutations).toHaveLength(14);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(proof.relation_rows.filter(({relation_id: id}) =>
      id === "architecture.constructed_by")).toHaveLength(3);
    expect(proof.relation_rows.filter(({relation_id: id}) =>
      id === "architecture.validated_by")).toHaveLength(9);
    expect(proof.relation_rows.filter(({relation_id: id}) =>
      id === "architecture.extends_factory")).toHaveLength(3);
  });

  it("rejects a cross-family ontology factory-extension pair", () => {
    const crossed = structuredClone(relationInputs);
    const ontology = JSON.parse(crossed.ontology!) as any;
    const extension = ontology.relation_definitions.find(
      ({relation_id: id}: any) => id === "architecture.extends_factory");
    extension.allowed_type_pairs[1] = {
      source_type: "architecture.EntityFactoryProvider",
      target_type: "architecture.ValueObjectFactoryProvider",
    };
    crossed.ontology = JSON.stringify(ontology);
    expect(() => proveValueObjectRelations(relationUpstream, crossed))
      .toThrowError("VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  });

  it("exposes both joins with truthful factory accounting", async () => {
    const parity = await valueObjectParityV1Provider.execute({
      raw_inputs: parityInputs, upstream: directUpstream});
    const relations = await valueObjectRelationsV1Provider.execute({
      raw_inputs: relationInputs, upstream: relationUpstream});
    expect(parity.accounting).toEqual({positives_declared: 17,
      positives_passed: 17, mutants_declared: 18, mutants_killed: 18});
    expect(relations.accounting).toEqual({positives_declared: 11,
      positives_passed: 11, mutants_declared: 14, mutants_killed: 14});
  });

  it("fails closed on missing direct and totals-only parity handles", () => {
    const missing = structuredClone(directUpstream);
    delete missing[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id];
    expect(() => evaluateValueObjectParity(missing, parityInputs))
      .toThrowError("VALUE_OBJECT_PARITY_HANDLE_SET_MISMATCH");
    const totalsOnly = structuredClone(relationUpstream) as any;
    totalsOnly[VALUE_OBJECT_PARITY_HANDLE.node_id].semantic_output = {
      accounting: {positives_declared: 17, positives_passed: 17},
    };
    expect(() => proveValueObjectRelations(totalsOnly, relationInputs))
      .toThrowError("VALUE_OBJECT_RELATION_PARITY_INVALID");
  });

  it("fails closed on stale target, binding, observer, and provider digests", () => {
    const mutations = [
      ["target", "target_sha256", "VALUE_OBJECT_PARITY_TARGET_MISMATCH"],
      ["binding", "binding_sha256", "VALUE_OBJECT_PARITY_PROOF_INVALID"],
      ["observer_ref", "observer_sha256",
        "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING"],
      ["observer_ref", "provider_sha256",
        "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING"],
    ] as const;
    for (const [surface, field, code] of mutations) {
      const stale = structuredClone(directUpstream) as any;
      const proof = stale[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id]
        .semantic_output.proof;
      const target = surface === "observer_ref" ?
        proof.observation.observer_ref : proof[surface];
      target[field] = "0".repeat(64);
      expect(() => evaluateValueObjectParity(stale, parityInputs))
        .toThrowError(code);
    }
  });
});
