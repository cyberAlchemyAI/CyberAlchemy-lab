import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {beforeAll, describe, expect, it} from "vitest";

import {sha256OperationValue} from
  "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {
  buildOperationRelationProof,
  canonicalJson,
  computeBindingSha256,
  sha256Bytes,
} from "./operation-relation-proof-v1.js";

type JsonObject = Record<string, any>;
const repositoryRoot = process.cwd();
const bindingPath =
  "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
  "operation/wp-rmt-002/relations/operation-relation-binding.json";

let bindingRaw: string;
let rawInputs: Record<string, string>;
let resolvedRequestInputs: Record<string, Buffer>;

const rebound = (
  mutateBinding: (binding: JsonObject) => void,
  replacements: Readonly<Record<string, string>> = {},
  resolvedReplacements: Readonly<Record<string, Buffer>> = {},
): Readonly<{
  binding_raw: string;
  raw_inputs: Record<string, string>;
  resolved_request_inputs: Record<string, Buffer>;
}> => {
  const binding = JSON.parse(bindingRaw) as JsonObject;
  mutateBinding(binding);
  const nextRaw = {...rawInputs, ...replacements};
  for (const [role, raw] of Object.entries(replacements)) {
    const source = binding.sources.find((entry: JsonObject) =>
      entry.role === role) as JsonObject;
    source.sha256 = sha256Bytes(raw);
    source.size_bytes = Buffer.byteLength(raw, "utf8");
  }
  binding.binding_sha256 = computeBindingSha256(binding);
  return {
    binding_raw: `${JSON.stringify(binding, null, 2)}\n`,
    raw_inputs: nextRaw,
    resolved_request_inputs: {
      ...resolvedRequestInputs,
      ...resolvedReplacements,
    },
  };
};

beforeAll(async () => {
  bindingRaw = await readFile(resolve(repositoryRoot, bindingPath), "utf8");
  const binding = JSON.parse(bindingRaw) as JsonObject;
  rawInputs = Object.fromEntries(await Promise.all(binding.sources.map(
    async ({role, path}: {role: string; path: string}) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ],
  )));
  const request = JSON.parse(rawInputs.op007_factory_request!) as JsonObject;
  const paths = [...new Set(request.nodes.flatMap((node: JsonObject) =>
    node.input_refs.map(({ref}: JsonObject) => ref.path as string)))];
  resolvedRequestInputs = Object.fromEntries(await Promise.all(paths.map(
    async (path) => [
      path,
      await readFile(resolve(repositoryRoot, path)),
    ],
  )));
});

describe("RMT-OP-008 exact Operation relation blueprints", () => {
  it("binds four exact blueprints, the S1 handle schema, and four REL-A kills", () => {
    const proof = buildOperationRelationProof({
      binding_raw: bindingRaw,
      raw_inputs: rawInputs,
      resolved_request_inputs: resolvedRequestInputs,
    });
    expect(proof).toMatchObject({
      schema_version: "OperationRelationProof/v1",
      result: "pass",
      semantic_plan_epoch_id: "WP-RMT-002/S1/2026-08-16",
      semantic_contract_digest:
        "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7",
      relation_contract_count: 4,
      blueprint_relation_count: 4,
      materialized_relation_count: 0,
      s1_handle_materialized: false,
      no_self_authored_authority: true,
      publication_authority: false,
      authority_effect: "none",
      upstream_closure: {
        source_role_count: 25,
        source_size_bytes: 2993281,
        source_aggregate_sha256:
          "7e6da173a9c889edd461b6dbaa524d50246e59345d057e0de7651095cf30992c",
        request_role_count: 109,
        request_path_count: 49,
        request_ref_bytes_scanned: expect.any(Number),
        op006_pins_exact: true,
        s1_materialized_field_occurrences: 0,
      },
    });
    expect(proof.relation_contracts.map((contract) => ({
      contract_id: contract.contract_id,
      relation_id: contract.architecture_relation_id,
      source_types: contract.source_types,
      target_types: contract.target_types,
      owner: contract.assertion_owner_mapping,
      mode: contract.evidence_mode,
      materialized: contract.materialized,
      evidence: contract.owner_evidence,
      fixture_classification: contract.fixture_owner_evidence_classification,
    }))).toEqual([
      {
        contract_id: "op/enforced-by-to-guards",
        relation_id: "architecture.guards",
        source_types: ["architecture.RuleImplementation"],
        target_types: ["architecture.OperationImplementation"],
        owner: "source Rule candidate",
        mode: "blueprint", materialized: false,
        evidence: {status: "not-materialized", sha256: null},
        fixture_classification: "synthetic-family-fixture-placeholder",
      },
      {
        contract_id: "op/exposed-by-to-exposes",
        relation_id: "architecture.exposes",
        source_types: ["architecture.InterfaceImplementation"],
        target_types: ["architecture.OperationImplementation"],
        owner: "source Interface candidate",
        mode: "blueprint", materialized: false,
        evidence: {status: "not-materialized", sha256: null},
        fixture_classification: "synthetic-family-fixture-placeholder",
      },
      {
        contract_id: "op/emitted-events-to-emits",
        relation_id: "architecture.emits",
        source_types: ["architecture.OperationImplementation"],
        target_types: ["architecture.EventImplementation"],
        owner: "source Operation candidate",
        mode: "blueprint", materialized: false,
        evidence: {status: "not-materialized", sha256: null},
        fixture_classification: "synthetic-family-fixture-placeholder",
      },
      {
        contract_id: "op/workflow-step-to-binds-step",
        relation_id: "architecture.binds_step",
        source_types: ["architecture.WorkflowStepContract"],
        target_types: [
          "architecture.OperationImplementation",
          "architecture.WorkflowImplementation",
        ],
        owner: "Workflow candidate owning the step assertion",
        mode: "blueprint", materialized: false,
        evidence: {status: "not-materialized", sha256: null},
        fixture_classification: "synthetic-family-fixture-placeholder",
      },
    ]);
    expect(proof.s1_handle_blueprint).toEqual({
      handle: "operation-transaction-effect-group/v1",
      fields: [
        "transaction_id", "effect_group_id", "state_write_id",
        "outbox_checkpoint_id", "occurrence_id", "commit_outcome",
      ],
      publication_authority: false,
      materialized: false,
      evidence_sha256: null,
    });
    expect(proof.hostile_evidence.map((control) => ({
      id: control.hostile_id,
      codes: control.observed_codes,
      status: control.status,
      non_noop: control.semantic_non_noop,
    }))).toEqual([
      {
        id: "op/relation-owner-evidence-stale",
        codes: ["RMT_RELATION_OWNER_EVIDENCE_STALE"],
        status: "killed", non_noop: true,
      },
      {
        id: "op/relation-source-endpoint-mismatch",
        codes: ["RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
        status: "killed", non_noop: true,
      },
      {
        id: "op/relation-target-endpoint-mismatch",
        codes: ["RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
        status: "killed", non_noop: true,
      },
      {
        id: "op/materialized-without-exact-assertion",
        codes: ["RMT_RELATION_ASSERTION_REQUIRED"],
        status: "killed", non_noop: true,
      },
    ]);
    expect(proof.proof_sha256).toMatch(/^[a-f0-9]{64}$/u);
    expect(proof.upstream_closure.request_ref_bytes_scanned).toBe(
      Object.values(resolvedRequestInputs).reduce((total, bytes) =>
        total + bytes.length, 0),
    );
  });

  it("rehashes all 109 OP-007 request roles across 49 current live paths", async () => {
    const request = JSON.parse(rawInputs.op007_factory_request!) as JsonObject;
    const refs = request.nodes.flatMap((node: JsonObject) => node.input_refs) as
      Array<{role: string; ref: {
        path: string; sha256: string; size_bytes?: number;
      }}>;
    expect(refs).toHaveLength(109);
    expect(new Set(refs.map(({role}) => role)).size).toBe(109);
    expect(new Set(refs.map(({ref}) => ref.path)).size).toBe(49);
    await Promise.all(refs.map(async ({ref}) => {
      const bytes = await readFile(resolve(repositoryRoot, ref.path));
      expect(sha256Bytes(bytes)).toBe(ref.sha256);
      if (ref.size_bytes !== undefined) {
        expect(bytes.length).toBe(ref.size_bytes);
      }
    }));
  });

  it("rejects re-bound relation, endpoint, owner, and S1-handle drift", () => {
    const relationPlan = JSON.parse(rawInputs.relation_contracts!) as JsonObject;
    const operationGroup = relationPlan.type_contracts.find(
      (entry: JsonObject) => entry.owner_swu === "RMT-OP-008",
    ) as JsonObject;
    operationGroup.contracts[0].architecture_relation_id =
      "architecture.queries";
    const relationPlanRaw = `${JSON.stringify(relationPlan, null, 2)}\n`;
    const changedPlan = rebound(() => undefined, {
      relation_contracts: relationPlanRaw,
    });
    expect(() => buildOperationRelationProof(changedPlan)).toThrow(
      "RMT_OP_RELATION_CONTRACT_DRIFT",
    );

    const wrongSource = rebound((binding) => {
      binding.relation_blueprints[0].source_types = [
        "architecture.QueryImplementation",
      ];
    });
    expect(() => buildOperationRelationProof(wrongSource)).toThrow(
      "RMT_OP_RELATION_BLUEPRINT_DRIFT",
    );

    const wrongOwner = rebound((binding) => {
      binding.relation_blueprints[1].assertion_owner_mapping =
        "source Operation candidate";
    });
    expect(() => buildOperationRelationProof(wrongOwner)).toThrow(
      "RMT_OP_RELATION_BLUEPRINT_DRIFT",
    );

    const wrongHandle = rebound((binding) => {
      binding.s1_handle_blueprint.fields[0] = "request_id";
    });
    expect(() => buildOperationRelationProof(wrongHandle)).toThrow(
      "RMT_OP_S1_HANDLE_BLUEPRINT_DRIFT",
    );
  });

  it("closes the family evaluator's relation-id gap at the acceptance edge", () => {
    const observations = JSON.parse(
      rawInputs.positive_observations!,
    ) as JsonObject;
    const first = observations.observations[0] as JsonObject;
    first.relation_assertions[0].architecture_relation_id =
      "architecture.queries";
    const {observation_sha256: _old, ...body} = first;
    first.observation_sha256 = sha256OperationValue(body);
    const observationRaw = `${JSON.stringify(observations, null, 2)}\n`;
    const changed = rebound(() => undefined, {
      positive_observations: observationRaw,
    });
    expect(() => buildOperationRelationProof(changed)).toThrow(
      "RMT_OP_RELATION_ASSERTION_ID_DRIFT",
    );
  });

  it("rejects materialization overclaim, nested extras, stale bytes, and authority", () => {
    const materializedWithoutAssertion = rebound((binding) => {
      binding.relation_blueprints[0].evidence_mode = "materialized";
      binding.relation_blueprints[0].materialized = true;
    });
    expect(() => buildOperationRelationProof(
      materializedWithoutAssertion,
    )).toThrow("RMT_RELATION_ASSERTION_REQUIRED");

    const nestedExtra = rebound((binding) => {
      binding.relation_blueprints[0].owner_evidence.oracle_hint = "forbidden";
    });
    expect(() => buildOperationRelationProof(nestedExtra)).toThrow(
      "RMT_OP_RELATION_BLUEPRINT_INVALID",
    );

    expect(() => buildOperationRelationProof({
      binding_raw: bindingRaw,
      raw_inputs: {...rawInputs, admission: `${rawInputs.admission!}\n`},
      resolved_request_inputs: resolvedRequestInputs,
    })).toThrow("RMT_OP_RELATION_SOURCE_STALE");

    const authority = rebound((binding) => {
      binding.authority_effect = "promote";
    });
    expect(() => buildOperationRelationProof(authority)).toThrow(
      "RMT_OP_RELATION_BINDING_INVALID",
    );
  });

  it("rejects a correctly re-bound S1 handle instance in the 49-path transitive closure", () => {
    const binding = JSON.parse(bindingRaw) as JsonObject;
    const boundPaths = new Set(binding.sources.map(
      ({path}: {path: string}) => path,
    ));
    const request = JSON.parse(rawInputs.op007_factory_request!) as JsonObject;
    const refs = request.nodes.flatMap((node: JsonObject) => node.input_refs) as
      Array<{ref: {path: string; sha256: string; size_bytes?: number}}>;
    const targetPath = [...new Set(refs.map(({ref}) => ref.path))].find(
      (path) => !boundPaths.has(path),
    );
    expect(targetPath).toBeDefined();
    const mutated = Buffer.concat([
      resolvedRequestInputs[targetPath!]!,
      Buffer.from(
        "\nschema_version = \"operation-transaction-effect-group/v1\"\n",
        "utf8",
      ),
    ]);
    const mutatedSha256 = sha256Bytes(mutated);
    for (const entry of refs.filter(({ref}) => ref.path === targetPath)) {
      entry.ref.sha256 = mutatedSha256;
      if (entry.ref.size_bytes !== undefined) {
        entry.ref.size_bytes = mutated.length;
      }
    }
    const requestRaw = `${JSON.stringify(request, null, 2)}\n`;
    const changed = rebound(
      () => undefined,
      {op007_factory_request: requestRaw},
      {[targetPath!]: mutated},
    );
    expect(() => buildOperationRelationProof(changed)).toThrow(
      "RMT_OP_S1_MATERIALIZATION_REQUIRES_REFRESH",
    );
  });

  it("rejects a valid-SHA owner value before classifying it synthetic", () => {
    const definition = JSON.parse(rawInputs.definition!) as JsonObject;
    definition.relation_contracts[0].owner_evidence_sha256 = "e".repeat(64);
    const definitionRaw = `${JSON.stringify(definition, null, 2)}\n`;
    const changed = rebound(() => undefined, {definition: definitionRaw});
    expect(() => buildOperationRelationProof(changed)).toThrow(
      "RMT_OP_RELATION_FIXTURE_PLACEHOLDER_DRIFT",
    );
  });

  it("keeps the proof independent of product targets and canonical authority", async () => {
    const proofSource = await readFile(resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
        "operation/wp-rmt-002/relations/operation-relation-proof-v1.ts",
    ), "utf8");
    expect(proofSource).not.toMatch(/architecture-conformance\/targets\//u);
    expect(proofSource).not.toMatch(/factory\/registry/u);
    expect(proofSource).not.toMatch(/ontology/u);
    expect(proofSource).not.toContain("RMT-OP-009");
    expect(canonicalJson(Object.keys(rawInputs).sort())).toBe(
      canonicalJson((JSON.parse(bindingRaw) as JsonObject).sources
        .map(({role}: {role: string}) => role).sort()),
    );
  });
});
