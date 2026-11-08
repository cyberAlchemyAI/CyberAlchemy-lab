import {readFile, readdir} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  OPERATION_EXPECTED_DIAGNOSTIC,
  OPERATION_HOSTILE_IDS,
  OPERATION_S1_HOSTILE_IDS,
  type OperationFindingCode,
  type OperationHostileFixtureV1,
  type OperationHostileId,
  type OperationS1HostileFixtureV1,
  type OperationS1HostileId,
  type StateChangingActionDefinitionV1,
  type StateChangingActionDenominatorV1,
  type StateChangingActionObservationSetV1,
  type StateChangingActionObservationV1,
} from "../contracts/state-changing-action-contracts.js";
import {applyOperationHostile, applyOperationS1Mutation} from
  "../mutations/apply-operation-hostile.js";
import {
  decodeOperationHostileFixtureV1,
  decodeStateChangingActionDefinitionV1,
  decodeStateChangingActionDenominatorV1,
  decodeStateChangingActionObservationSetV1,
  sha256OperationValue,
} from "../providers/decode-state-changing-action.js";
import {evaluateOperationS1Residue, evaluateStateChangingAction} from
  "./evaluate-state-changing-action.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = process.cwd();
const familyRoot = resolve(here, "..");
const fixtureRoot = resolve(familyRoot, "fixtures/complete-settlement");
const hostileRoot = resolve(familyRoot, "hostiles");

const definitionPath =
  "projects/domainspec-v2/impl/architecture-conformance/families/" +
  "state-changing-action/fixtures/complete-settlement/operation-contract.json";
const admissionPath =
  "projects/domainspec-v2/development/remaining-meta-types/active-types/" +
  "operation/admission/admission.json";
const hostileCataloguePath =
  "projects/domainspec-v2/development/refinement-runs/" +
  "20260814T193343Z-active-meta-type-implementations/refreshes/" +
  "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
  "HOSTILE-CATALOGUE.json";
const relationContractsPath =
  "projects/domainspec-v2/development/refinement-runs/" +
  "20260814T193343Z-active-meta-type-implementations/refreshes/" +
  "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
  "RELATION-CONTRACTS.json";

type ExpectedHostile = Readonly<{
  file: string;
  hostile_id: OperationHostileId;
  hostile_class: "type-semantic" | "rel-a-evidence";
  mutation_kind: string;
  expected_code: OperationFindingCode;
  proof_owner_swu: "RMT-OP-006" | "RMT-OP-008";
}>;

const EXPECTED_HOSTILES: readonly ExpectedHostile[] = Object.freeze([
  {
    file: "undeclared-write.json",
    hostile_id: "op/undeclared-write",
    hostile_class: "type-semantic",
    mutation_kind: "add-undeclared-write",
    expected_code: "RMT_OP_UNDECLARED_WRITE",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "undeclared-effect.json",
    hostile_id: "op/undeclared-effect",
    hostile_class: "type-semantic",
    mutation_kind: "add-undeclared-effect",
    expected_code: "RMT_OP_UNDECLARED_EFFECT",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "guard-bypass.json",
    hostile_id: "op/guard-bypass",
    hostile_class: "type-semantic",
    mutation_kind: "start-rejected-transition",
    expected_code: "RMT_OP_GUARD_BYPASS",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "order-swap.json",
    hostile_id: "op/order-swap",
    hostile_class: "type-semantic",
    mutation_kind: "swap-read-write-order",
    expected_code: "RMT_OP_ORDER_SWAP",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "atomicity-removed.json",
    hostile_id: "op/atomicity-removed",
    hostile_class: "type-semantic",
    mutation_kind: "remove-single-commit",
    expected_code: "RMT_OP_ATOMICITY_REMOVED",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "success-failure-collapse.json",
    hostile_id: "op/success-failure-collapse",
    hostile_class: "type-semantic",
    mutation_kind: "attach-success-value-to-failure",
    expected_code: "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "emitted-before-commit.json",
    hostile_id: "op/emitted-before-commit",
    hostile_class: "type-semantic",
    mutation_kind: "move-event-before-commit",
    expected_code: "RMT_OP_EMITTED_BEFORE_COMMIT",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "continuation-mismatch.json",
    hostile_id: "op/continuation-mismatch",
    hostile_class: "type-semantic",
    mutation_kind: "mismatch-continuation-closure",
    expected_code: "RMT_OP_CONTINUATION_MISMATCH",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "read-set-drift.json",
    hostile_id: "op/read-set-drift",
    hostile_class: "type-semantic",
    mutation_kind: "add-undeclared-read",
    expected_code: "RMT_OP_READ_SET_DRIFT",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "output-contract-overclaim.json",
    hostile_id: "op/output-contract-overclaim",
    hostile_class: "type-semantic",
    mutation_kind: "claim-exactly-once-delivery",
    expected_code: "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
    proof_owner_swu: "RMT-OP-006",
  },
  {
    file: "relation-owner-evidence-stale.json",
    hostile_id: "op/relation-owner-evidence-stale",
    hostile_class: "rel-a-evidence",
    mutation_kind: "stale-owner-evidence",
    expected_code: "RMT_RELATION_OWNER_EVIDENCE_STALE",
    proof_owner_swu: "RMT-OP-008",
  },
  {
    file: "relation-source-endpoint-mismatch.json",
    hostile_id: "op/relation-source-endpoint-mismatch",
    hostile_class: "rel-a-evidence",
    mutation_kind: "replace-source-endpoint",
    expected_code: "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
    proof_owner_swu: "RMT-OP-008",
  },
  {
    file: "relation-target-endpoint-mismatch.json",
    hostile_id: "op/relation-target-endpoint-mismatch",
    hostile_class: "rel-a-evidence",
    mutation_kind: "replace-target-endpoint",
    expected_code: "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
    proof_owner_swu: "RMT-OP-008",
  },
  {
    file: "materialized-without-exact-assertion.json",
    hostile_id: "op/materialized-without-exact-assertion",
    hostile_class: "rel-a-evidence",
    mutation_kind: "remove-exact-assertion",
    expected_code: "RMT_RELATION_ASSERTION_REQUIRED",
    proof_owner_swu: "RMT-OP-008",
  },
]);

type ExpectedS1Hostile = Readonly<{
  file: string;
  hostile_id: OperationS1HostileId;
  mutation_kind: string;
  expected_code: OperationFindingCode;
  category: string;
  required_observation: string;
  required_outcome: string;
}>;

const EXPECTED_S1_HOSTILES: readonly ExpectedS1Hostile[] = Object.freeze([
  {file:"before-state-write-failure.json",hostile_id:"s1/before-state-write-failure",mutation_kind:"observe-before-state-write-failure",expected_code:"RMT_S1_BEFORE_STATE_WRITE_FAILURE",category:"fault-matrix:S1-F01",required_observation:"state-write-attempt and transaction abort",required_outcome:"no durable state and no occurrence"},
  {file:"between-state-and-outbox-failure.json",hostile_id:"s1/between-state-and-outbox-failure",mutation_kind:"observe-state-outbox-gap",expected_code:"RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH",category:"fault-matrix:S1-F02",required_observation:"state write plus missing outbox checkpoint",required_outcome:"atomic abort; no mixed commit"},
  {file:"missing-member.json",hostile_id:"s1/missing-member",mutation_kind:"remove-required-member",expected_code:"RMT_S1_MISSING_MEMBER",category:"decode-contract",required_observation:"missing transaction or occurrence member",required_outcome:"closed rejection with stable code"},
  {file:"mixed-commit.json",hostile_id:"s1/mixed-commit",mutation_kind:"observe-mixed-commit",expected_code:"RMT_S1_MIXED_COMMIT",category:"atomicity-contract",required_observation:"state durable while outbox absent, or inverse",required_outcome:"reject mixed commit"},
  {file:"rollback-after-commit.json",hostile_id:"s1/rollback-after-commit",mutation_kind:"request-rollback-after-commit",expected_code:"RMT_S1_ROLLBACK_AFTER_COMMIT",category:"recovery-contract",required_observation:"attempt to erase committed state or outbox occurrence",required_outcome:"reject rollback and require forward recovery"},
]);

type CatalogueControl = Readonly<{
  hostile_id: string;
  hostile_class: string;
  expected_code: string;
  fixture_owner_swu: string;
  proof_owner_swu: string;
  fixture_path: string;
  non_noop_required: boolean;
}>;

type S1CatalogueControl = CatalogueControl & Readonly<{
  category: string;
  required_observation: string;
  required_outcome: string;
}>;

let definitionRaw: string;
let denominatorRaw: string;
let observationSetRaw: string;
let admissionRaw: string;
let definition: StateChangingActionDefinitionV1;
let denominator: StateChangingActionDenominatorV1;
let observations: StateChangingActionObservationSetV1;
let hostileRawById: ReadonlyMap<OperationHostileId, string>;
let hostiles: ReadonlyMap<OperationHostileId, OperationHostileFixtureV1>;
let catalogueControls: readonly CatalogueControl[];
let s1Hostiles: ReadonlyMap<OperationS1HostileId, OperationS1HostileFixtureV1>;
let catalogueS1Controls: readonly S1CatalogueControl[];
let relationContracts: readonly Record<string, unknown>[];

const semanticBodyDigest = (
  observation: StateChangingActionObservationV1,
): string => {
  const {
    observation_sha256: _digest,
    source_kind: _sourceKind,
    ...semanticBody
  } = observation;
  return sha256OperationValue(semanticBody);
};

beforeAll(async () => {
  [
    definitionRaw,
    denominatorRaw,
    observationSetRaw,
    admissionRaw,
  ] = await Promise.all([
    readFile(resolve(fixtureRoot, "operation-contract.json"), "utf8"),
    readFile(resolve(fixtureRoot, "denominator.json"), "utf8"),
    readFile(resolve(fixtureRoot, "positive-observation.json"), "utf8"),
    readFile(resolve(repositoryRoot, admissionPath), "utf8"),
  ]);
  definition = decodeStateChangingActionDefinitionV1(
    definitionRaw,
    admissionPath,
    admissionRaw,
  );
  denominator = decodeStateChangingActionDenominatorV1(
    denominatorRaw,
    definitionPath,
    definitionRaw,
    definition,
  );
  observations = decodeStateChangingActionObservationSetV1(
    observationSetRaw,
    definition,
    definitionPath,
    definitionRaw,
    denominator,
    denominatorRaw,
  );

  const hostilePairs = await Promise.all(EXPECTED_HOSTILES.map(async (expected) =>
    [expected.hostile_id, await readFile(
      resolve(hostileRoot, expected.file),
      "utf8",
    )] as const));
  hostileRawById = new Map(hostilePairs);
  hostiles = new Map(hostilePairs.map(([id, raw]) =>
    [id, decodeOperationHostileFixtureV1(raw)] as const));
  const s1Pairs = await Promise.all(EXPECTED_S1_HOSTILES.map(async (expected) =>
    [expected.hostile_id, await readFile(
      resolve(hostileRoot, expected.file), "utf8",
    )] as const));
  s1Hostiles = new Map(s1Pairs.map(([id, raw]) => {
    const fixture = decodeOperationHostileFixtureV1(raw) as
      OperationS1HostileFixtureV1;
    return [id, fixture] as const;
  }));

  const catalogue = JSON.parse(await readFile(
    resolve(repositoryRoot, hostileCataloguePath),
    "utf8",
  )) as {groups: {type: string; controls: CatalogueControl[]}[];
    cross_type_controls: S1CatalogueControl[]};
  const operationGroup = catalogue.groups.find(({type}) => type === "Operation");
  if (!operationGroup) throw new Error("RMT_OP_AUTHORITATIVE_GROUP_MISSING");
  catalogueControls = operationGroup.controls;
  catalogueS1Controls = catalogue.cross_type_controls.filter(
    ({fixture_owner_swu}) => fixture_owner_swu === "RMT-OP-002",
  );

  const relations = JSON.parse(await readFile(
    resolve(repositoryRoot, relationContractsPath),
    "utf8",
  )) as {type_contracts: {type: string; contracts: Record<string, unknown>[]}[]};
  const operationRelations = relations.type_contracts.find(({type}) =>
    type === "Operation");
  if (!operationRelations) {
    throw new Error("RMT_OP_RELATION_CONTRACT_GROUP_MISSING");
  }
  relationContracts = operationRelations.contracts;
});

describe("portable state-changing Operation family", () => {
  it("accepts committed success and guard rejection without overclaim", () => {
    expect(observations.observations.map(({case_id}) => case_id)).toEqual([
      "committed-success",
      "guard-rejected",
    ]);
    for (const observation of observations.observations) {
      const result = evaluateStateChangingAction(
        definition,
        denominator,
        observation,
      );
      expect(result.verdict).toBe("pass");
      expect(result.findings).toEqual([]);
      expect(result.accounting).toEqual({
        semantic_controls: 10,
        relation_controls: 4,
        total_controls: 14,
        failed_controls: 0,
        unaccounted: 0,
      });
      expect(result.authority_effect).toBe("none");
    }

    const committed = observations.observations.find(({case_id}) =>
      case_id === "committed-success")!;
    const rejected = observations.observations.find(({case_id}) =>
      case_id === "guard-rejected")!;
    expect(committed.atomicity.outcome).toBe("committed");
    expect(committed.emitted_events[0]?.trace_ordinal).toBeGreaterThan(
      committed.trace.indexOf("atomic:commit"),
    );
    expect(rejected.transition_started).toBe(false);
    expect(rejected.read_attempts).toEqual([]);
    expect(rejected.write_attempts).toEqual([]);
    expect(rejected.external_effect_attempts).toEqual([]);
    expect(rejected.outcome).toMatchObject({
      kind: "failure",
      value: null,
      exactly_once_distributed_delivery_claimed: false,
    });
  });

  it("matches the authoritative 10 semantic plus 4 REL-A catalogue exactly", async () => {
    const expectedFiles = [...EXPECTED_HOSTILES, ...EXPECTED_S1_HOSTILES]
      .map(({file}) => file).sort();
    expect(expectedFiles).toHaveLength(19);
    expect((await readdir(hostileRoot)).sort()).toEqual(expectedFiles);
    expect(OPERATION_HOSTILE_IDS).toEqual(
      EXPECTED_HOSTILES.map(({hostile_id}) => hostile_id),
    );
    expect(denominator.semantic_hostile_count).toBe(10);
    expect(denominator.relation_hostile_count).toBe(4);
    expect(denominator.relation_contract_count).toBe(4);

    expect(catalogueControls).toEqual(EXPECTED_HOSTILES.map((expected) => ({
      hostile_id: expected.hostile_id,
      hostile_class: expected.hostile_class,
      expected_code: expected.expected_code,
      fixture_owner_swu: "RMT-OP-002",
      proof_owner_swu: expected.proof_owner_swu,
      fixture_path:
        "projects/domainspec-v2/impl/architecture-conformance/families/" +
        `state-changing-action/hostiles/${expected.file}`,
      non_noop_required: true,
    })));

    for (const expected of EXPECTED_HOSTILES) {
      expect(hostiles.get(expected.hostile_id)).toEqual({
        schema_version: "StateChangingActionHostile/v1",
        hostile_id: expected.hostile_id,
        hostile_class: expected.hostile_class,
        mutation_kind: expected.mutation_kind,
        expected_code: expected.expected_code,
        fixture_owner_swu: "RMT-OP-002",
        proof_owner_swu: expected.proof_owner_swu,
        non_noop_required: true,
        authority_effect: "none",
      });
      expect(OPERATION_EXPECTED_DIAGNOSTIC[expected.hostile_id]).toBe(
        expected.expected_code,
      );
    }
  });

  it("binds all five integrated S1 controls and their exact durable outcomes", () => {
    expect(OPERATION_S1_HOSTILE_IDS).toEqual(
      EXPECTED_S1_HOSTILES.map(({hostile_id}) => hostile_id),
    );
    expect(catalogueS1Controls).toEqual(EXPECTED_S1_HOSTILES.map((expected) => ({
      hostile_id: expected.hostile_id,
      hostile_class: "s1-cross-boundary",
      expected_code: expected.expected_code,
      fixture_owner_swu: "RMT-OP-002",
      proof_owner_swu: "RMT-OP-006",
      fixture_path:
        "projects/domainspec-v2/impl/architecture-conformance/families/" +
        `state-changing-action/hostiles/${expected.file}`,
      non_noop_required: true,
      category: expected.category,
      required_observation: expected.required_observation,
      required_outcome: expected.required_outcome,
    })));
    for (const expected of EXPECTED_S1_HOSTILES) {
      const hostile = s1Hostiles.get(expected.hostile_id)!;
      expect(hostile).toMatchObject({
        schema_version: "StateChangingActionS1Hostile/v1",
        hostile_id: expected.hostile_id,
        hostile_class: "s1-cross-boundary",
        mutation_kind: expected.mutation_kind,
        expected_code: expected.expected_code,
        fixture_owner_swu: "RMT-OP-002",
        proof_owner_swu: "RMT-OP-006",
        non_noop_required: true,
        category: expected.category,
        required_observation: expected.required_observation,
        required_outcome: expected.required_outcome,
        authority_effect: "none",
      });
      const observed = applyOperationS1Mutation(
        hostile.baseline,
        hostile.mutation,
      );
      expect(sha256OperationValue(observed)).not.toBe(
        sha256OperationValue(hostile.baseline),
      );
      const result = evaluateOperationS1Residue(observed);
      expect(result.verdict).toBe("reject");
      expect(result.findings.map(({code}) => code)).toEqual([
        expected.expected_code,
      ]);
      expect(result.required_residue_observed).toBe(true);
      expect(() => evaluateOperationS1Residue({
        ...observed,
        closed_rejection: false,
      })).toThrow("RMT_OP_S1_RESIDUE_INCOHERENT");
    }
  });

  it("makes every mutation semantically non-noop and kills it with one exact code", () => {
    const committed = observations.observations.find(({case_id}) =>
      case_id === "committed-success")!;
    const rejected = observations.observations.find(({case_id}) =>
      case_id === "guard-rejected")!;
    const frozenPositive = observations.observations.map(
      ({observation_sha256}) => observation_sha256,
    );

    for (const expected of EXPECTED_HOSTILES) {
      const base = expected.hostile_id === "op/guard-bypass" ||
          expected.hostile_id === "op/success-failure-collapse"
        ? rejected
        : committed;
      const mutated = applyOperationHostile(base, expected.hostile_id);
      expect(mutated.observation_sha256).toMatch(/^[a-f0-9]{64}$/u);
      expect(mutated.observation_sha256).not.toBe(base.observation_sha256);
      expect(semanticBodyDigest(mutated)).not.toBe(semanticBodyDigest(base));
      const result = evaluateStateChangingAction(
        definition,
        denominator,
        mutated,
      );
      expect(result.verdict).toBe("fail");
      expect(result.findings.map(({code}) => code)).toEqual([
        expected.expected_code,
      ]);
      expect(result.accounting.failed_controls).toBe(1);
    }
    expect(observations.observations.map(
      ({observation_sha256}) => observation_sha256,
    )).toEqual(frozenPositive);
  });

  it("preserves the four authoritative relation directions and owner mappings", () => {
    const projected = definition.relation_contracts.map((contract) => ({
      contract_id: contract.contract_id,
      architecture_relation_id: contract.architecture_relation_id,
      source_types: contract.source_types,
      target_types: contract.target_types,
      assertion_owner_mapping: contract.assertion_owner,
    }));
    expect(projected).toEqual(relationContracts.map((contract) => ({
      contract_id: contract.contract_id,
      architecture_relation_id: contract.architecture_relation_id,
      source_types: contract.source_types,
      target_types: contract.target_types,
      assertion_owner_mapping: contract.assertion_owner_mapping,
    })));
    expect(projected.find(({architecture_relation_id}) =>
      architecture_relation_id === "architecture.guards")).toMatchObject({
      source_types: ["architecture.RuleImplementation"],
      target_types: ["architecture.OperationImplementation"],
    });
    expect(projected.find(({architecture_relation_id}) =>
      architecture_relation_id === "architecture.exposes")).toMatchObject({
      source_types: ["architecture.InterfaceImplementation"],
      target_types: ["architecture.OperationImplementation"],
    });
    const binds = projected.find(({architecture_relation_id}) =>
      architecture_relation_id === "architecture.binds_step")!;
    expect(binds.source_types).toEqual(["architecture.WorkflowStepContract"]);
    expect(binds.source_types).not.toContain(
      "architecture.WorkflowImplementation",
    );
  });

  it("fails closed for nested extras and stale exact-byte bindings", () => {
    const hostileWithExtra = {
      ...JSON.parse(hostileRawById.get("op/undeclared-write")!) as object,
      oracle_hint: "RMT_OP_UNDECLARED_WRITE",
    };
    expect(() => decodeOperationHostileFixtureV1(
      JSON.stringify(hostileWithExtra),
    )).toThrow("RMT_OP_HOSTILE_CONTRACT_INVALID");

    const definitionWithInputExtra = JSON.parse(definitionRaw) as {
      input_contract: Record<string, unknown>;
    };
    definitionWithInputExtra.input_contract.oracle_hint = "forbidden";
    expect(() => decodeStateChangingActionDefinitionV1(
      JSON.stringify(definitionWithInputExtra),
      admissionPath,
      admissionRaw,
    )).toThrow("RMT_OP_DEFINITION_DENOMINATOR_INVALID");

    const definitionWithRelationExtra = JSON.parse(definitionRaw) as {
      relation_contracts: Record<string, unknown>[];
    };
    definitionWithRelationExtra.relation_contracts[0]!.oracle_hint =
      "forbidden";
    expect(() => decodeStateChangingActionDefinitionV1(
      JSON.stringify(definitionWithRelationExtra),
      admissionPath,
      admissionRaw,
    )).toThrow("RMT_OP_DEFINITION_DENOMINATOR_INVALID");

    const denominatorWithExtra = JSON.parse(denominatorRaw) as {
      portable_contract: Record<string, unknown>;
    };
    denominatorWithExtra.portable_contract.oracle_hint = "forbidden";
    expect(() => decodeStateChangingActionDenominatorV1(
      JSON.stringify(denominatorWithExtra),
      definitionPath,
      definitionRaw,
      definition,
    )).toThrow("RMT_OP_DENOMINATOR_PORTABLE_CONTRACT_INVALID");

    const observationWithExtra = JSON.parse(observationSetRaw) as {
      observations: (Record<string, unknown> & {
        outcome: Record<string, unknown>;
        observation_sha256: string;
      })[];
    };
    observationWithExtra.observations[0]!.outcome.oracle_hint = "forbidden";
    const {observation_sha256: _oldDigest, ...observationBody} =
      observationWithExtra.observations[0]!;
    observationWithExtra.observations[0]!.observation_sha256 =
      sha256OperationValue(observationBody);
    expect(() => decodeStateChangingActionObservationSetV1(
      JSON.stringify(observationWithExtra),
      definition,
      definitionPath,
      definitionRaw,
      denominator,
      denominatorRaw,
    )).toThrow("RMT_OP_OBSERVATION_SHAPE_INVALID");

    const staleObservations = JSON.parse(observationSetRaw) as {
      observations: {trace: string[]}[];
    };
    staleObservations.observations[0]!.trace = [
      ...staleObservations.observations[0]!.trace,
      "undeclared:step",
    ];
    expect(() => decodeStateChangingActionObservationSetV1(
      JSON.stringify(staleObservations),
      definition,
      definitionPath,
      definitionRaw,
      denominator,
      denominatorRaw,
    )).toThrow("RMT_OP_OBSERVATION_DIGEST_STALE");
    expect(() => decodeStateChangingActionDefinitionV1(
      definitionRaw,
      admissionPath,
      `${admissionRaw}\n`,
    )).toThrow("RMT_OP_DEFINITION_ADMISSION_STALE");
    expect(() => decodeStateChangingActionDenominatorV1(
      denominatorRaw,
      definitionPath,
      `${definitionRaw}\n`,
      definition,
    )).toThrow("RMT_OP_DENOMINATOR_DEFINITION_STALE");
  });

  it("keeps evaluator and mutator independent of the oracle and product targets", async () => {
    const [evaluatorSource, mutatorSource] = await Promise.all([
      readFile(resolve(here, "evaluate-state-changing-action.ts"), "utf8"),
      readFile(resolve(familyRoot, "mutations/apply-operation-hostile.ts"),
        "utf8"),
    ]);
    for (const source of [evaluatorSource, mutatorSource]) {
      expect(source).not.toContain("expected_code");
      expect(source).not.toContain("HOSTILE-CATALOGUE");
      expect(source).not.toMatch(/architecture-conformance\/targets\//u);
      expect(source).not.toMatch(/realizations\/operation\//u);
    }
    expect(mutatorSource).not.toContain("hostiles/");
  });
});
