import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {pythonEntityV1Provider} from
  "../../factory/registry/providers/python-entity-v1.js";
import {rustEntityV1Provider} from
  "../../factory/registry/providers/rust-entity-v1.js";
import {typeScriptEntityV1Provider} from
  "../../factory/registry/providers/typescript-entity-v1.js";
import {entityParityV1Provider} from
  "../../factory/registry/providers/entity-parity-v1.js";
import {entityRelationsV1Provider} from
  "../../factory/registry/providers/entity-relations-v1.js";
import {canonicalJson, sha256} from "../../factory/shared/canonical.js";
import {PYTHON_ENTITY_RAW_PATHS} from
  "../../realizations/entity/python/identity-lifecycle-v1/index.js";
import {RUST_ENTITY_RAW_PATHS} from
  "../../realizations/entity/rust/identity-lifecycle-v1/index.js";
import {TYPESCRIPT_ENTITY_RAW_PATHS} from
  "../../realizations/entity/typescript/identity-lifecycle-v1/index.js";
import {
  evaluateEntityParity,
  evaluateEntityRelations,
  proveEntityParity,
  proveEntityRelations,
  ENTITY_DIRECT_HANDLES,
  ENTITY_PARITY_HANDLE,
  ENTITY_PARITY_RAW_PATHS,
  ENTITY_RELATION_RAW_PATHS,
} from "./evaluate-entity-joins.js";

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
  parityInputs = await readPaths(ENTITY_PARITY_RAW_PATHS);
  relationInputs = await readPaths(ENTITY_RELATION_RAW_PATHS);
  const results = await Promise.all([
    typeScriptEntityV1Provider.execute({
      raw_inputs: await readPaths(TYPESCRIPT_ENTITY_RAW_PATHS), upstream: {},
    }),
    pythonEntityV1Provider.execute({
      raw_inputs: await readPaths(PYTHON_ENTITY_RAW_PATHS), upstream: {},
    }),
    rustEntityV1Provider.execute({
      raw_inputs: await readPaths(RUST_ENTITY_RAW_PATHS), upstream: {},
    }),
  ]);
  directUpstream = Object.fromEntries(results.map((result, index) => {
    const handle = ENTITY_DIRECT_HANDLES[index]!;
    return [handle.node_id, Object.freeze({
      node_id: handle.node_id,
      provider_id: result.provider_id,
      semantic_sha256: sha256(canonicalJson(result)),
      semantic_output: result.semantic_output,
    })];
  }));
  const parity = await entityParityV1Provider.execute({
    raw_inputs: parityInputs, upstream: directUpstream,
  });
  relationUpstream = {
    ...directUpstream,
    [ENTITY_PARITY_HANDLE.node_id]: Object.freeze({
      node_id: ENTITY_PARITY_HANDLE.node_id,
      provider_id: parity.provider_id,
      semantic_sha256: sha256(canonicalJson(parity)),
      semantic_output: parity.semantic_output,
    }),
  };
}, 90_000);

describe("Entity parity and architecture relations", () => {
  it("proves stable-identity lifecycle parity without native hash-byte equality", () => {
    const proof = proveEntityParity(directUpstream, parityInputs);
    expect(proof).toMatchObject({schema_version: "EntityParityProof/v1",
      result: "pass", authority_effect: "none"});
    expect(proof.composed_from.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.composed_from.map(({target_sha256, binding_sha256}) =>
      ({target_sha256, binding_sha256}))).toEqual(
      ENTITY_DIRECT_HANDLES.map(({target_sha256, binding_sha256}) =>
        ({target_sha256, binding_sha256})),
    );
    expect(proof.obligations).toHaveLength(20);
    expect(new Set(proof.obligations.map(({obligation_id: id}) => id)).size)
      .toBe(20);
    expect(proof.hostile_mutations).toHaveLength(26);
    expect(new Set(proof.hostile_mutations.map(({mutation_id: id}) => id)).size)
      .toBe(26);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(proof.native_evidence_by_language.map(({evidence}) => ({
      source: evidence.target_source_control_count,
      family: evidence.predecessor_family_control_count,
      distinct: evidence.evidence_classes_kept_distinct,
    }))).toEqual([
      {source: 10, family: 7, distinct: true},
      {source: 11, family: 7, distinct: true},
      {source: 12, family: 7, distinct: true},
    ]);
    expect(JSON.stringify(proof)).toContain(
      '"native_hash_bytes_compared_cross_language":false');
    expect(JSON.stringify(proof)).not.toContain('"pid":');
  });

  it("proves exact Entity constructed_by, validated_by, and extends_factory rows", () => {
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
    const proof = proveEntityRelations(relationUpstream, relationInputs);
    expect(proof).toMatchObject({schema_version: "EntityRelationsProof/v1",
      result: "pass", authority_effect: "none"});
    expect(proof.obligations).toHaveLength(12);
    expect(new Set(proof.obligations.map(({obligation_id: id}) => id)).size)
      .toBe(12);
    expect(proof.hostile_mutations).toHaveLength(15);
    expect(new Set(proof.hostile_mutations.map(({mutation_id: id}) => id)).size)
      .toBe(15);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(proof.relation_rows).toHaveLength(15);
    expect(proof.relation_rows.every(({source_type, target_type}) =>
      !source_type.includes("ValueObject") &&
      !target_type.includes("ValueObject"))).toBe(true);
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
    expect(() => proveEntityRelations(relationUpstream, crossed))
      .toThrowError("ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  });

  it("exposes both joins with exact accounting", async () => {
    const parity = await entityParityV1Provider.execute({
      raw_inputs: parityInputs, upstream: directUpstream});
    const relations = await entityRelationsV1Provider.execute({
      raw_inputs: relationInputs, upstream: relationUpstream});
    expect(parity.accounting).toEqual({positives_declared: 20,
      positives_passed: 20, mutants_declared: 26, mutants_killed: 26});
    expect(relations.accounting).toEqual({positives_declared: 12,
      positives_passed: 12, mutants_declared: 15, mutants_killed: 15});
  });

  it("fails closed on missing direct and totals-only parity handles", () => {
    const missing = structuredClone(directUpstream);
    delete missing[ENTITY_DIRECT_HANDLES[0]!.node_id];
    expect(() => evaluateEntityParity(missing, parityInputs))
      .toThrowError("ENTITY_PARITY_HANDLE_SET_MISMATCH");
    const totalsOnly = structuredClone(relationUpstream) as any;
    totalsOnly[ENTITY_PARITY_HANDLE.node_id].semantic_output = {
      accounting: {positives_declared: 20, positives_passed: 20},
    };
    expect(() => proveEntityRelations(totalsOnly, relationInputs))
      .toThrowError("ENTITY_RELATION_PARITY_INVALID");
  });

  it("fails closed on stale target, binding, observer, and provider digests", () => {
    const mutations = [
      ["target", "target_sha256", "ENTITY_PARITY_TARGET_MISMATCH"],
      ["binding", "binding_sha256", "ENTITY_PARITY_PROOF_INVALID"],
      ["observer_ref", "observer_sha256",
        "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING"],
      ["observer_ref", "provider_sha256",
        "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING"],
    ] as const;
    for (const [surface, field, code] of mutations) {
      const stale = structuredClone(directUpstream) as any;
      const proof = stale[ENTITY_DIRECT_HANDLES[0]!.node_id]
        .semantic_output.proof;
      const target = surface === "observer_ref" ?
        proof.observation.observer_ref : proof[surface];
      target[field] = "0".repeat(64);
      expect(() => evaluateEntityParity(stale, parityInputs))
        .toThrowError(code);
    }
  });

  it("binds exact native control identities, evidence kinds, and leak-free proof shapes", () => {
    const mutations: readonly ((upstream: any) => void)[] = [
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[0]!.node_id].semantic_output.proof
          .source_controls[0].control_id = "renamed-target-control";
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[0]!.node_id].semantic_output.proof
          .predecessor_family_controls[0].mutation_id = "renamed-family-control";
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[0]!.node_id].semantic_output.proof
          .source_controls[0].evidence_kind = "renamed-evidence-kind";
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[1]!.node_id].semantic_output.proof
          .target_source_controls[0].unexpected = true;
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[2]!.node_id].semantic_output.proof
          .source_controls[0].mechanism = "renamed-mechanism";
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[1]!.node_id].semantic_output.workspace
          .cleaned = false;
      },
      (upstream) => {
        upstream[ENTITY_DIRECT_HANDLES[0]!.node_id].semantic_output.proof
          .process_evidence.temp_path = "/tmp/entity-proof-leak";
      },
    ];
    for (const mutate of mutations) {
      const hostile = structuredClone(directUpstream) as any;
      mutate(hostile);
      expect(() => evaluateEntityParity(hostile, parityInputs))
        .toThrowError("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    }
  });

  it("binds exact descriptor, admission, ontology, and dependency receipt bytes", () => {
    const mutations: readonly ((raw: Record<string, string>) => void)[] = [
      (raw) => {
        const admission = JSON.parse(raw.protocol_admission!) as any;
        admission.descriptor_ref.sha256 = "0".repeat(64);
        raw.protocol_admission = JSON.stringify(admission);
      },
      (raw) => {
        const descriptor = JSON.parse(raw.descriptor!) as any;
        descriptor.material_refs[0].sha256 = "0".repeat(64);
        raw.descriptor = JSON.stringify(descriptor);
      },
      (raw) => {
        const admission = JSON.parse(raw.protocol_admission!) as any;
        admission.selected_relations.push(admission.selected_relations[0]);
        raw.protocol_admission = JSON.stringify(admission);
      },
      (raw) => {
        const receipt = JSON.parse(raw.typescript_receipt!) as any;
        receipt.swu_id = "RMT-ENTITY-004";
        raw.typescript_receipt = JSON.stringify(receipt);
      },
      (raw) => {
        const decision = JSON.parse(raw.entity_decision!) as any;
        decision.selected_option_id = "W1-ENTITY-B-DIRECT-CONSTRUCTOR";
        raw.entity_decision = JSON.stringify(decision);
      },
      (raw) => {
        const receipt = JSON.parse(raw.value_object_receipt!) as any;
        receipt.candidate_projection.sha256 = "0".repeat(64);
        raw.value_object_receipt = JSON.stringify(receipt);
      },
      (raw) => {
        const candidate = JSON.parse(raw.value_object_candidate!) as any;
        candidate.meta_type.id = "DS-D1.1";
        raw.value_object_candidate = JSON.stringify(candidate);
      },
      (raw) => {
        const descriptor = JSON.parse(raw.descriptor!) as any;
        descriptor.value_object_continuity_refs[0].sha256 = "0".repeat(64);
        raw.descriptor = JSON.stringify(descriptor);
      },
      (raw) => {
        const receipt = JSON.parse(raw.python_receipt!) as any;
        receipt.dependency_receipt.sha256 = "0".repeat(64);
        raw.python_receipt = JSON.stringify(receipt);
      },
    ];
    for (const mutate of mutations) {
      const hostile = structuredClone(relationInputs);
      mutate(hostile);
      expect(() => evaluateEntityRelations(relationUpstream, hostile))
        .toThrowError("ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    }
  });
});
