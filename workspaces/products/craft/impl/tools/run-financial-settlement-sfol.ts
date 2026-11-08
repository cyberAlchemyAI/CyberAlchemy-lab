#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import {
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import {
  bindingSelectorForCase,
  derivePureCases,
  digestSfolValue,
  fixtureDigest,
  toPureInvocation,
  type DerivedPureCase,
  type PureFixture,
} from "../test-derivation-engine/src/sfol/cases/index";
import {
  deriveEffectCases,
  effectContractAdmissionDigest,
  effectFixtureDigest,
  runDerivedEffectCase,
  type DerivedEffectCase,
  type EffectCaseDerivationInput,
  type EffectContractAdmission,
  type EffectFixture,
} from "../test-derivation-engine/src/sfol/cases/effect";
import {
  decodeLogicBindingRegistry,
  resolvePureBinding,
  SFOL_BINDING_SCHEMA_VERSION,
  type ResolvedPureBinding,
} from "../test-derivation-engine/src/sfol/bindings/index";
import {
  effectBindingSelectorForCase,
  resolveEffectBinding,
  type ResolvedEffectBinding,
} from "../test-derivation-engine/src/sfol/bindings/effect";
import {
  buildClauseDenominator,
  type ClauseDenominator,
  type ProofContextHandle,
} from "../test-derivation-engine/src/sfol/denominator/index";
import {
  integerValue,
} from "../test-derivation-engine/src/sfol/evaluator/index";
import {
  typecheckLogicModule,
  type TypedLogicModule,
} from "../test-derivation-engine/src/sfol/language/typecheck";
import {
  NODE_PROJECTION_ADMISSION_VERSION,
  NODE_PROOF_CONTEXT_VERSION,
  projectNodeLogic,
  type NodeLogicEnvelope,
} from "../test-derivation-engine/src/sfol/node-source/index";
import {
  buildPureProofReceipt,
  evaluatePureObservation,
  replayPureProofReceipt,
  type PureProofBuildInput,
} from "../test-derivation-engine/src/sfol/proof/index";
import {
  buildEffectProofReceipt,
  evaluateEffectObservation,
  replayEffectProofReceipt,
  type EffectProofBuildInput,
} from "../test-derivation-engine/src/sfol/proof/effect";
import {
  runPureCase,
  type PureTargetHandle,
} from "../test-derivation-engine/src/sfol/runners/pure/index";
import type {
  EffectTraceContract,
} from "../test-derivation-engine/src/sfol/runners/effect/contracts";
import {
  createDealSplitTarget,
  createPayoutEffectAdapter,
  type DealSplitMutation,
  type PayoutFixture,
  type PayoutTraceMutation,
} from "../../../../validation/poker-team/backend/src/domain/__derived__/financial-settlement.sfol.adapter";

type JsonObject = Record<string, any>;

const here = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(here, "..");
const repositoryRoot = resolve(implRoot, "../../..");
const featureRoot = resolve(
  implRoot,
  "spec/features/financial-settlement",
);
const adoptionRoot = resolve(featureRoot, "sfol/adoption");
const generatedRoot = resolve(featureRoot, "generated");
const runnerPath = fileURLToPath(import.meta.url);
const validatorPath = resolve(
  implRoot,
  "tools/validate-financial-settlement-sfol.ts",
);
const schemaPath = resolve(
  featureRoot,
  "sfol/adoption-report.schema.json",
);
const adapterPath = resolve(
  repositoryRoot,
  "validation/poker-team/backend/src/domain/__derived__/financial-settlement.sfol.adapter.ts",
);
const dealSourcePath = resolve(
  repositoryRoot,
  "validation/poker-team/backend/src/domain/deal/deal.service.ts",
);
const useCaseSourcePath = resolve(
  repositoryRoot,
  "validation/poker-team/backend/src/use-cases/financial-settlement/generate-settlement.ts",
);
const backendLockPath = resolve(
  repositoryRoot,
  "validation/poker-team/backend/package-lock.json",
);

async function main(): Promise<void> {
  verifyBte();
  const sourceProposalPath = resolve(
    featureRoot,
    "sfol/source-proposal.json",
  );
  const sourceProposal = readJson(sourceProposalPath);
  const sourceProposalDigest = sha256(
    readFileSync(sourceProposalPath),
  );
  const fixtureManifest = readJson(
    resolve(featureRoot, "sfol/fixtures/manifest.json"),
  );
  const sourceFixtures = loadSourceFixtures(fixtureManifest);
  const projection = projectCanonicalModules();
  const byNode = new Map(
    projection.map((envelope) => [
      envelope.node.node_id,
      envelope,
    ]),
  );

  const pureEnvelope = requireEnvelope(
    byNode,
    "financial-settlement.DealSplitCalculation",
  );
  const effectEnvelope = requireEnvelope(
    byNode,
    "financial-settlement.GenerateSettlement",
  );
  const pureTyped = requireTyped(pureEnvelope);
  const effectTyped = requireTyped(effectEnvelope);
  const proofContext = denominatorProofContext(pureEnvelope);
  if (
    digestSfolValue(proofContext) !==
    digestSfolValue(denominatorProofContext(effectEnvelope))
  ) {
    fail("module proof contexts differ");
  }

  const pureDenominator = denominator(
    proofContext,
    pureEnvelope,
    "return",
  );
  const effectDenominator = denominator(
    proofContext,
    effectEnvelope,
    "effects",
  );
  const proofToolDigest = digestSfolValue({
    runner: sha256(readFileSync(runnerPath)),
    consumer_adapter: sha256(readFileSync(adapterPath)),
    pure_core: {
      cases: fileDigest(
        "projects/domainspec-v2/impl/test-derivation-engine/src/sfol/cases/index.ts",
      ),
      proof: fileDigest(
        "projects/domainspec-v2/impl/test-derivation-engine/src/sfol/proof/index.ts",
      ),
    },
    effect_core: {
      cases: fileDigest(
        "projects/domainspec-v2/impl/test-derivation-engine/src/sfol/cases/effect.ts",
      ),
      proof: fileDigest(
        "projects/domainspec-v2/impl/test-derivation-engine/src/sfol/proof/effect.ts",
      ),
    },
  });
  const targetDigest = sha256(readFileSync(dealSourcePath));
  const effectTargetDigest = sha256(
    readFileSync(useCaseSourcePath),
  );
  const runtimeDigest = sha256(readFileSync(backendLockPath));

  const pure = runPureAdoption({
    envelope: pureEnvelope,
    typed: pureTyped,
    denominator: pureDenominator,
    sourceFixtures,
    targetDigest,
    runtimeDigest,
    proofToolDigest,
  });
  const effect = await runEffectAdoption({
    envelope: effectEnvelope,
    typed: effectTyped,
    denominator: effectDenominator,
    sourceFixture: requireSourceFixture(
      sourceFixtures,
      "financial-settlement.P4.eligible-payout",
    ) as PayoutFixture,
    sourceProposal,
    sourceProposalDigest,
    effectTargetDigest,
    runtimeDigest,
    proofToolDigest,
  });

  const mutations = {
    ...runPureMutations(
      pure,
      pureTyped,
      targetDigest,
      runtimeDigest,
    ),
    ...(await runEffectMutations(
      effect,
      effectTyped,
      effectTargetDigest,
      runtimeDigest,
      sourceProposalDigest,
    )),
  };
  const beforeCore = readJson(
    resolve(generatedRoot, "core-path-set-before-adoption.json"),
  );
  const afterCore = buildCorePathSet();
  const coreAudit = compareCorePathSets(beforeCore, afterCore);
  if (coreAudit.status !== "pass") {
    fail(
      `DS-SFOL core changed during adoption: ${JSON.stringify(coreAudit)}`,
    );
  }

  rmSync(adoptionRoot, { recursive: true, force: true });
  mkdirSync(adoptionRoot, { recursive: true });
  writeJson("pure-evidence.json", pure.evidence);
  writeJson("pure-proof-receipt.json", pure.proof);
  writeJson("pure-replay-receipt.json", pure.replay);
  writeJson("effect-evidence.json", effect.evidence);
  writeJson("effect-proof-receipt.json", effect.proof);
  writeJson("effect-replay-receipt.json", effect.replay);
  writeJson("mutation-report.json", {
    schema_version:
      "financial-settlement-sfol-mutation-report/v1",
    status: "pass",
    mutations,
  });
  writeJson("core-path-set-after-adoption.json", afterCore);

  const caseIds = [
    ...pure.cases.map((entry) => entry.case_id),
    ...effect.cases.map((entry) => entry.case_id),
  ].sort();
  const reportUnsigned = {
    schema_version: "domainspec-sfol-adoption-report/v1",
    status: "pass",
    authority: "experimental-test-lane-evidence",
    authority_effect: "none",
    formal_owner_approval: false,
    release_admission: "not-granted",
    project_id: "financial-settlement",
    schema: fileHandle(schemaPath),
    tool: {
      runner: fileHandle(runnerPath),
      validator: fileHandle(validatorPath),
      consumer_adapter: fileHandle(adapterPath),
      proof_tool_digest: proofToolDigest,
    },
    source_proposal: fileHandle(sourceProposalPath),
    proof_context: {
      graph_digest: proofContext.graph_digest,
      manifest_digest: proofContext.manifest_digest,
      build_digest: proofContext.build_digest,
      source_set_digest: proofContext.source_set_digest,
      profile_digest: proofContext.profile_digest,
    },
    modules: [
      {
        clause_id: "C3",
        module_id: pureEnvelope.module_id,
        module_digest: pureEnvelope.logic_digest,
        typed_artifact_digest: pure.typedArtifactDigest,
        denominator_digest: pureDenominator.digest,
        case_ids: pure.cases.map((entry) => entry.case_id).sort(),
        proof_receipt_digest: pure.proof.receipt_digest,
        replay_digest: pure.replay.replay_digest,
      },
      {
        clause_id: "P4",
        module_id: effectEnvelope.module_id,
        module_digest: effectEnvelope.logic_digest,
        typed_artifact_digest: effect.typedArtifactDigest,
        denominator_digest: effectDenominator.digest,
        case_ids: effect.cases.map((entry) => entry.case_id).sort(),
        proof_receipt_digest: effect.proof.receipt_digest,
        replay_digest: effect.replay.replay_digest,
      },
    ],
    stage_sets: [
      "C_spec",
      "C_projected",
      "C_validated",
      "C_typed",
      "T_generated",
      "C_bound",
      "O_run",
      "R_evaluated",
    ].map((stage) => ({ stage, case_ids: caseIds })),
    case_count: caseIds.length,
    fixture_ids: sourceFixtures
      .map((fixture) => fixture.fixture_id)
      .sort(),
    admitted_clause_ids: ["C3", "P4"],
    admitted_residue: [],
    non_admitted_residue: (
      sourceProposal.residue as JsonObject[]
    )
      .map((entry) => entry.id)
      .sort(),
    mutations,
    core_path_audit: coreAudit,
    bte: {
      verifier_status: "pass",
      structural_result: "expected-red",
      behavioral_authority: false,
    },
    claims: {
      experimental_c3_p4_profile_complete: true,
      full_financial_settlement_coverage: false,
      formal_source_approval: false,
      release_ready: false,
      production_ready: false,
    },
  };
  const report = {
    ...reportUnsigned,
    report_digest: digestSfolValue(reportUnsigned),
  };
  writeJson("adoption-report.json", report);

  console.log(
    JSON.stringify(
      {
        status: "PASS",
        report: relative(
          implRoot,
          resolve(adoptionRoot, "adoption-report.json"),
        ).replaceAll("\\", "/"),
        cases: caseIds.length,
        mutations_detected: Object.keys(mutations).length,
        pure_proof: pure.proof.receipt_digest,
        effect_proof: effect.proof.receipt_digest,
        core_path_audit: coreAudit.status,
        bte_structural_result: "expected-red",
        formal_owner_approval: false,
        release_admission: "not-granted",
      },
      null,
      2,
    ),
  );
}

function runPureAdoption(input: {
  envelope: NodeLogicEnvelope;
  typed: TypedLogicModule;
  denominator: ClauseDenominator;
  sourceFixtures: JsonObject[];
  targetDigest: string;
  runtimeDigest: string;
  proofToolDigest: string;
}) {
  const coverageKey = onlyCoverage(input.denominator);
  const fixtures: PureFixture[] = input.sourceFixtures
    .filter((fixture) => fixture.clause_id === "C3")
    .map((fixture) => {
      const unsigned = {
        fixture_id: fixture.fixture_id as string,
        coverage_key: coverageKey,
        inputs: {
          limit_value: integerValue(
            String(fixture.inputs.limit_value),
          ),
        },
        universes: {},
      };
      return {
        ...unsigned,
        fixture_digest: fixtureDigest(unsigned),
      };
    });
  const clause = onlyClause(input.envelope);
  const derived = derivePureCases({
    typed: input.typed,
    typed_module_digest: input.envelope.logic_digest,
    typed_clause_digests: {
      [clause.clause_id]: digestSfolValue(clause),
    },
    denominator: input.denominator,
    fixtures,
  });
  if (!derived.ok) fail(JSON.stringify(derived.diagnostics));
  const cases = derived.value;
  if (cases.length !== 3) {
    fail(`C3 must derive three cases; received ${cases.length}`);
  }
  const bindings = resolvePureBindings(
    cases,
    input.targetDigest,
    input.runtimeDigest,
  );
  const target = createDealSplitTarget({
    targetDigest: input.targetDigest,
    runtimeDigest: input.runtimeDigest,
  });
  const observations = cases.map((derivedCase, index) =>
    runPureCase(
      toPureInvocation(derivedCase),
      requireIndex(bindings, index, "pure binding"),
      pureTargetResolver(target),
    ),
  );
  const evaluations = cases.map((derivedCase, index) =>
    evaluatePureObservation(
      input.typed,
      derivedCase,
      requireIndex(bindings, index, "pure binding"),
      requireIndex(observations, index, "pure observation"),
    ),
  );
  if (evaluations.some((entry) => entry.status !== "pass")) {
    fail(`C3 evaluation failed: ${JSON.stringify(evaluations)}`);
  }
  const typedArtifactDigest = digestSfolValue(input.typed);
  const caseIds = cases.map((entry) => entry.case_id).sort();
  const proofInput: PureProofBuildInput = {
    denominator: input.denominator,
    typed_artifact_digest: typedArtifactDigest,
    upstream_case_sets: stageInputs(caseIds),
    cases,
    bindings,
    observations,
    evaluations,
    tool_digest: input.proofToolDigest,
  };
  const proofResult = buildPureProofReceipt(proofInput);
  if (!proofResult.ok) fail(JSON.stringify(proofResult.diagnostics));
  const proof = proofResult.value;
  const replayResult = replayPureProofReceipt(proof, proofInput, {
    receipt_digest: proof.receipt_digest,
    denominator_digest: input.denominator.digest,
    typed_artifact_digest: typedArtifactDigest,
    tool_digest: input.proofToolDigest,
  });
  if (!replayResult.ok) fail(JSON.stringify(replayResult.diagnostics));
  return {
    cases,
    bindings,
    observations,
    evaluations,
    proofInput,
    proof,
    replay: replayResult.value,
    typedArtifactDigest,
    evidence: {
      schema_version:
        "financial-settlement-sfol-pure-evidence/v1",
      denominator: input.denominator,
      typed_artifact_digest: typedArtifactDigest,
      fixtures,
      cases,
      bindings,
      observations,
      evaluations,
    },
  };
}

async function runEffectAdoption(input: {
  envelope: NodeLogicEnvelope;
  typed: TypedLogicModule;
  denominator: ClauseDenominator;
  sourceFixture: PayoutFixture;
  sourceProposal: JsonObject;
  sourceProposalDigest: string;
  effectTargetDigest: string;
  runtimeDigest: string;
  proofToolDigest: string;
}) {
  const coverageKey = onlyCoverage(input.denominator);
  const contract = input.sourceProposal.effect_contract
    .contract as EffectTraceContract;
  const declaredContractDigest =
    input.sourceProposal.effect_contract.contract_digest;
  if (digestSfolValue(contract) !== declaredContractDigest) {
    fail("P4 effect contract digest differs from the source proposal");
  }
  const admissionUnsigned = {
    schema_version:
      "domainspec-sfol-effect-contract-admission/v1" as const,
    admission_id:
      "financial-settlement.experimental-p4-contract-admission",
    proof_context: input.denominator.proof_context,
    source_proposal_digest: input.sourceProposalDigest,
    contract_bindings: [
      {
        contract_id: contract.contract_id,
        contract_digest: declaredContractDigest,
        source_proposal_digest: input.sourceProposalDigest,
      },
    ],
  };
  const contractAdmission: EffectContractAdmission = {
    ...admissionUnsigned,
    admission_digest:
      effectContractAdmissionDigest(admissionUnsigned),
  };
  const fixtureUnsigned = {
    fixture_id: input.sourceFixture.fixture_id,
    coverage_key: coverageKey,
    contract_id: contract.contract_id,
    inputs: {},
    universes: {},
  };
  const fixture: EffectFixture = {
    ...fixtureUnsigned,
    fixture_digest: effectFixtureDigest(fixtureUnsigned),
  };
  const clause = onlyClause(input.envelope);
  const derivationInput: EffectCaseDerivationInput = {
    typed: input.typed,
    typed_module_digest: input.envelope.logic_digest,
    typed_clause_digests: {
      [clause.clause_id]: digestSfolValue(clause),
    },
    denominator: input.denominator,
    fixtures: [fixture],
    contracts: [contract],
    contract_admission: contractAdmission,
    source_proposal_digest: input.sourceProposalDigest,
  };
  const derived = deriveEffectCases(derivationInput);
  if (!derived.ok) fail(JSON.stringify(derived.diagnostics));
  if (derived.value.length !== 1) {
    fail(`P4 must derive one case; received ${derived.value.length}`);
  }
  const derivedCase = requireIndex(derived.value, 0, "effect case");
  const adapterDigest = effectAdapterDigest(
    input.sourceFixture,
    "none",
    input.effectTargetDigest,
    input.runtimeDigest,
  );
  const adapter = createPayoutEffectAdapter({
    fixture: input.sourceFixture,
    contractId: contract.contract_id,
    adapterDigest,
  });
  const binding = resolveEffectCaseBinding(
    derivedCase,
    adapter.adapter_id,
    adapterDigest,
    input.effectTargetDigest,
    input.runtimeDigest,
  );
  const observation = await runDerivedEffectCase(
    derivedCase,
    binding,
    contract,
    adapter,
    { timeout_ms: 5000, max_open_resources: 3 },
  );
  const evaluation = evaluateEffectObservation(
    input.typed,
    derivedCase,
    binding,
    observation,
    contract,
  );
  if (evaluation.status !== "pass") {
    fail(`P4 evaluation failed: ${JSON.stringify(evaluation)}`);
  }
  const typedArtifactDigest = digestSfolValue(input.typed);
  const caseIds = [derivedCase.case_id];
  const proofInput: EffectProofBuildInput = {
    denominator: input.denominator,
    typed_artifact_digest: typedArtifactDigest,
    upstream_case_sets: stageInputs(caseIds),
    cases: [derivedCase],
    bindings: [binding],
    observations: [observation],
    evaluations: [evaluation],
    trace_contracts: [contract],
    contract_admission: contractAdmission,
    source_proposal_digest: input.sourceProposalDigest,
    tool_digest: input.proofToolDigest,
  };
  const proofResult = buildEffectProofReceipt(proofInput);
  if (!proofResult.ok) fail(JSON.stringify(proofResult.diagnostics));
  const proof = proofResult.value;
  const replayResult = replayEffectProofReceipt(proof, proofInput, {
    receipt_digest: proof.receipt_digest,
    denominator_digest: input.denominator.digest,
    typed_artifact_digest: typedArtifactDigest,
    contract_admission_digest: contractAdmission.admission_digest,
    source_proposal_digest: input.sourceProposalDigest,
    tool_digest: input.proofToolDigest,
  });
  if (!replayResult.ok) fail(JSON.stringify(replayResult.diagnostics));
  return {
    cases: [derivedCase],
    binding,
    observation,
    evaluation,
    proofInput,
    proof,
    replay: replayResult.value,
    typedArtifactDigest,
    contract,
    contractAdmission,
    fixture: input.sourceFixture,
    evidence: {
      schema_version:
        "financial-settlement-sfol-effect-evidence/v1",
      denominator: input.denominator,
      typed_artifact_digest: typedArtifactDigest,
      source_fixture_sha256: sourceFixtureDigest(
        input.sourceFixture.fixture_id,
      ),
      fixture,
      contract,
      contract_admission: contractAdmission,
      cases: [derivedCase],
      bindings: [binding],
      observations: [observation],
      evaluations: [evaluation],
    },
  };
}

function runPureMutations(
  pure: ReturnType<typeof runPureAdoption>,
  typed: TypedLogicModule,
  targetDigest: string,
  runtimeDigest: string,
) {
  const selected = {
    comparator: requireCaseContaining(pure.cases, "at-threshold"),
    "returned-value": requireCaseContaining(
      pure.cases,
      "below-threshold",
    ),
  } as const;
  return Object.fromEntries(
    (
      Object.entries(selected) as Array<
        [DealSplitMutation, DerivedPureCase]
      >
    ).map(([mutation, derivedCase]) => {
      const mutantDigest = digestSfolValue({
        target_digest: targetDigest,
        mutation,
      });
      const binding = resolvePureBindings(
        [derivedCase],
        mutantDigest,
        runtimeDigest,
      )[0]!;
      const target = createDealSplitTarget({
        targetDigest: mutantDigest,
        runtimeDigest,
        mutation,
      });
      const observation = runPureCase(
        toPureInvocation(derivedCase),
        binding,
        pureTargetResolver(target),
      );
      const evaluation = evaluatePureObservation(
        typed,
        derivedCase,
        binding,
        observation,
      );
      if (evaluation.status === "pass") {
        fail(`C3 mutation ${mutation} was not detected`);
      }
      return [`C3-${mutation}`, "detected"];
    }),
  );
}

async function runEffectMutations(
  effect: Awaited<ReturnType<typeof runEffectAdoption>>,
  typed: TypedLogicModule,
  targetDigest: string,
  runtimeDigest: string,
  sourceProposalDigest: string,
) {
  const derivedCase = effect.cases[0]!;
  const mutationResults: Record<string, "detected"> = {};
  for (const mutation of [
    "missing-write",
    "missing-event",
    "wrong-amount",
    "wrong-date",
    "wrong-order",
  ] as const) {
    const adapterDigest = effectAdapterDigest(
      effect.fixture,
      mutation,
      targetDigest,
      runtimeDigest,
    );
    const adapter = createPayoutEffectAdapter({
      fixture: effect.fixture,
      contractId: effect.contract.contract_id,
      adapterDigest,
      mutation,
    });
    const binding = resolveEffectCaseBinding(
      derivedCase,
      adapter.adapter_id,
      adapterDigest,
      targetDigest,
      runtimeDigest,
    );
    const observation = await runDerivedEffectCase(
      derivedCase,
      binding,
      effect.contract,
      adapter,
      { timeout_ms: 5000, max_open_resources: 3 },
    );
    const evaluation = evaluateEffectObservation(
      typed,
      derivedCase,
      binding,
      observation,
      effect.contract,
    );
    if (evaluation.status === "pass") {
      fail(`P4 mutation ${mutation} was not detected`);
    }
    mutationResults[`P4-${mutation}`] = "detected";
  }
  const replay = replayEffectProofReceipt(
    effect.proof,
    {
      ...effect.proofInput,
      tool_digest: "0".repeat(64),
    },
    {
      receipt_digest: effect.proof.receipt_digest,
      denominator_digest: effect.proofInput.denominator.digest,
      typed_artifact_digest:
        effect.proofInput.typed_artifact_digest,
      contract_admission_digest:
        effect.contractAdmission.admission_digest,
      source_proposal_digest: sourceProposalDigest,
      tool_digest: effect.proofInput.tool_digest,
    },
  );
  if (replay.ok) fail("P4 proof-input mutation was not detected");
  mutationResults["P4-proof-input"] = "detected";
  return mutationResults;
}

function projectCanonicalModules(): readonly NodeLogicEnvelope[] {
  const result = projectNodeLogic(
    {
      schema_version: NODE_PROOF_CONTEXT_VERSION,
      route: "canonical-minted-project-build",
      graph_bytes: readFileSync(
        resolve(generatedRoot, "graph.json"),
        "utf8",
      ),
      source_manifest_bytes: readFileSync(
        resolve(generatedRoot, "source-manifest.json"),
        "utf8",
      ),
      build_receipt_bytes: readFileSync(
        resolve(generatedRoot, "build-receipt.json"),
        "utf8",
      ),
    },
    {
      schema_version: NODE_PROJECTION_ADMISSION_VERSION,
      profile_id: "sfol-development",
      profile_version: "0.1",
      logic_schema_versions: ["domainspec-node-logic/v1"],
      admitted_node_ids: [
        "financial-settlement.DealSplitCalculation",
        "financial-settlement.GenerateSettlement",
      ],
    },
  );
  if (!result.ok) fail(JSON.stringify(result.diagnostics));
  return result.value;
}

function denominatorProofContext(
  envelope: NodeLogicEnvelope,
): ProofContextHandle {
  return {
    graph_id: "financial-settlement.graph",
    graph_digest: envelope.proof_context.graph_digest,
    manifest_id: "financial-settlement.source-manifest",
    manifest_digest: envelope.proof_context.manifest_digest,
    build_id: "financial-settlement.build",
    build_digest: envelope.proof_context.build_receipt_digest,
    source_set_digest: envelope.proof_context.source_set_digest,
    profile_id: envelope.proof_context.profile_id,
    profile_version: envelope.proof_context.profile_version,
    profile_digest: envelope.proof_context.profile_digest,
  };
}

function denominator(
  proofContext: ProofContextHandle,
  envelope: NodeLogicEnvelope,
  role: "return" | "effects",
): ClauseDenominator {
  const clause = onlyClause(envelope);
  return buildClauseDenominator({
    schema_version:
      "domainspec-sfol-clause-admission-manifest/v1",
    source_form: "canonical-node-graph-manifest-build",
    unsupported_residue_policy: "reject",
    proof_context: proofContext,
    clause_membership: [clause.clause_id],
    clauses: [
      {
        clause_id: clause.clause_id,
        clause_digest: digestSfolValue(clause),
        node_id: envelope.node.node_id,
        node_digest: envelope.node.node_digest,
        module_id: envelope.module_id,
        module_digest: envelope.logic_digest,
        kind: clause.kind,
        required_roles: [role],
        status: "admitted",
        proof_context: {
          graph_digest: proofContext.graph_digest,
          manifest_digest: proofContext.manifest_digest,
          build_digest: proofContext.build_digest,
          source_set_digest: proofContext.source_set_digest,
          profile_id: proofContext.profile_id,
          profile_version: proofContext.profile_version,
          profile_digest: proofContext.profile_digest,
        },
      },
    ],
  });
}

function resolvePureBindings(
  cases: readonly DerivedPureCase[],
  targetDigest: string,
  runtimeDigest: string,
): ResolvedPureBinding[] {
  const registry = decodeLogicBindingRegistry({
    schema_version: SFOL_BINDING_SCHEMA_VERSION,
    registry_id: "financial-settlement.C3.bindings",
    bindings: cases.map((derivedCase) => ({
      binding_id: `financial-settlement.C3.binding.${derivedCase.fixture_id}`,
      selector: bindingSelectorForCase(derivedCase),
      target: {
        adapter_kind: "pure-function",
        module:
          "validation/poker-team/backend/src/domain/deal/deal.service.ts",
        symbol: "getDealSplit",
        target_digest: targetDigest,
        runtime_digest: runtimeDigest,
      },
      argument_map: [
        { parameter: "limit", input_name: "limit_value" },
      ],
      observation_map: { kind: "return" },
    })),
  });
  if (!registry.ok) fail(JSON.stringify(registry.diagnostics));
  return cases.map((derivedCase) => {
    const result = resolvePureBinding(
      {
        selector: bindingSelectorForCase(derivedCase),
        adapter_kind: "pure-function",
      },
      registry.value,
    );
    if (!result.ok) fail(JSON.stringify(result.diagnostics));
    return result.value;
  });
}

function resolveEffectCaseBinding(
  derivedCase: DerivedEffectCase,
  adapterId: string,
  adapterDigest: string,
  targetDigest: string,
  runtimeDigest: string,
): ResolvedEffectBinding {
  const selector = effectBindingSelectorForCase(derivedCase);
  const result = resolveEffectBinding(
    { selector, adapter_kind: "effect-harness" },
    {
      schema_version: "domainspec-sfol-effect-binding/v1",
      registry_id: "financial-settlement.P4.bindings",
      bindings: [
        {
          binding_id: `financial-settlement.P4.binding.${derivedCase.fixture_id}`,
          selector,
          target: {
            adapter_kind: "effect-harness",
            module:
              "validation/poker-team/backend/src/use-cases/financial-settlement/generate-settlement.ts",
            symbol: "generateSettlementUseCase",
            target_digest: targetDigest,
            runtime_digest: runtimeDigest,
            adapter_id: adapterId,
            adapter_digest: adapterDigest,
          },
        },
      ],
    },
  );
  if (!result.ok) fail(JSON.stringify(result.diagnostics));
  return result.value;
}

function pureTargetResolver(target: PureTargetHandle) {
  return {
    resolve(module: string, symbol: string) {
      return module ===
        "validation/poker-team/backend/src/domain/deal/deal.service.ts" &&
        symbol === "getDealSplit"
        ? target
        : null;
    },
  };
}

function effectAdapterDigest(
  fixture: PayoutFixture,
  mutation: PayoutTraceMutation,
  targetDigest: string,
  runtimeDigest: string,
): string {
  return digestSfolValue({
    adapter_source_digest: sha256(readFileSync(adapterPath)),
    fixture_digest: sourceFixtureDigest(fixture.fixture_id),
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
    mutation,
  });
}

function loadSourceFixtures(manifest: JsonObject): JsonObject[] {
  return (manifest.fixtures as JsonObject[])
    .map((entry) => {
      const path = resolve(repositoryRoot, entry.path);
      const actual = sha256(readFileSync(path));
      if (actual !== entry.sha256) {
        fail(`source fixture digest mismatch: ${entry.fixture_id}`);
      }
      return readJson(path);
    })
    .sort((left, right) =>
      String(left.fixture_id).localeCompare(
        String(right.fixture_id),
      ),
    );
}

function sourceFixtureDigest(fixtureId: string): string {
  const manifest = readJson(
    resolve(featureRoot, "sfol/fixtures/manifest.json"),
  );
  const entry = (manifest.fixtures as JsonObject[]).find(
    (candidate) => candidate.fixture_id === fixtureId,
  );
  if (entry === undefined) fail(`unknown fixture ${fixtureId}`);
  return entry.sha256;
}

function verifyBte(): void {
  if (process.argv.includes("--skip-bte")) return;
  const result = spawnSync(
    "npm",
    [
      "--prefix",
      implRoot,
      "run",
      "verify:bte:financial-settlement",
    ],
    {
      cwd: repositoryRoot,
      encoding: "utf8",
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  if (result.status !== 0) {
    fail(
      `BTE verifier failed: ${String(result.stderr || result.stdout)}`,
    );
  }
  const report = readJson(
    resolve(
      implRoot,
      "generated-tests/financial-settlement/financial-settlement.structural.report.json",
    ),
  );
  if (report.result !== "expected-red") {
    fail(`unexpected BTE structural result ${String(report.result)}`);
  }
}

function buildCorePathSet(): JsonObject {
  const coreRoot = resolve(
    implRoot,
    "test-derivation-engine/src/sfol",
  );
  const files = listFiles(coreRoot).map((path) => ({
    path: relative(implRoot, path).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(path)),
  }));
  const unsigned = {
    schema_version: "domainspec-sfol-core-path-set/v1",
    lifecycle_point: "after-bc-003-before-bc-005",
    root: "test-derivation-engine/src/sfol",
    files,
  };
  return {
    ...unsigned,
    path_set_digest: digestSfolValue(unsigned),
  };
}

function compareCorePathSets(
  before: JsonObject,
  after: JsonObject,
) {
  const beforeByPath = new Map(
    (before.files as JsonObject[]).map((entry) => [
      entry.path,
      entry.sha256,
    ]),
  );
  const afterByPath = new Map(
    (after.files as JsonObject[]).map((entry) => [
      entry.path,
      entry.sha256,
    ]),
  );
  const added = [...afterByPath.keys()]
    .filter((path) => !beforeByPath.has(path))
    .sort();
  const removed = [...beforeByPath.keys()]
    .filter((path) => !afterByPath.has(path))
    .sort();
  const changed = [...afterByPath.keys()]
    .filter(
      (path) =>
        beforeByPath.has(path) &&
        beforeByPath.get(path) !== afterByPath.get(path),
    )
    .sort();
  return {
    status:
      added.length + removed.length + changed.length === 0
        ? ("pass" as const)
        : ("fail" as const),
    before_digest: before.path_set_digest as string,
    after_digest: after.path_set_digest as string,
    added,
    removed,
    changed,
  };
}

function listFiles(root: string): string[] {
  return readdirSync(root, { withFileTypes: true })
    .flatMap((entry) => {
      const path = resolve(root, entry.name);
      return entry.isDirectory() ? listFiles(path) : [path];
    })
    .filter((path) => statSync(path).isFile())
    .sort();
}

function stageInputs(caseIds: readonly string[]) {
  return {
    C_spec: caseIds,
    C_projected: caseIds,
    C_validated: caseIds,
    C_typed: caseIds,
  };
}

function requireTyped(envelope: NodeLogicEnvelope): TypedLogicModule {
  const result = typecheckLogicModule(envelope.logic);
  if (!result.ok) fail(JSON.stringify(result.diagnostics));
  return result.value;
}

function requireEnvelope(
  byNode: ReadonlyMap<string, NodeLogicEnvelope>,
  nodeId: string,
): NodeLogicEnvelope {
  const envelope = byNode.get(nodeId);
  if (envelope === undefined) fail(`projected module absent: ${nodeId}`);
  return envelope;
}

function onlyClause(envelope: NodeLogicEnvelope) {
  const clause = envelope.logic.clauses[0];
  if (clause === undefined || envelope.logic.clauses.length !== 1) {
    fail(`module ${envelope.module_id} must contain one clause`);
  }
  return clause;
}

function onlyCoverage(denominator_: ClauseDenominator): string {
  const coverage = denominator_.coverage_keys[0];
  if (
    coverage === undefined ||
    denominator_.coverage_keys.length !== 1
  ) {
    fail("adopter denominator must contain one clause-role obligation");
  }
  return coverage;
}

function requireSourceFixture(
  fixtures: readonly JsonObject[],
  fixtureId: string,
): JsonObject {
  const fixture = fixtures.find(
    (candidate) => candidate.fixture_id === fixtureId,
  );
  if (fixture === undefined) fail(`missing source fixture ${fixtureId}`);
  return fixture;
}

function requireCaseContaining(
  cases: readonly DerivedPureCase[],
  token: string,
): DerivedPureCase {
  const derivedCase = cases.find((entry) =>
    entry.fixture_id.includes(token),
  );
  if (derivedCase === undefined) fail(`missing pure case ${token}`);
  return derivedCase;
}

function requireIndex<T>(
  values: readonly T[],
  index: number,
  subject: string,
): T {
  const value = values[index];
  if (value === undefined) fail(`${subject} ${index} is absent`);
  return value;
}

function fileHandle(path: string) {
  return {
    path: relative(repositoryRoot, path).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(path)),
  };
}

function fileDigest(repositoryRelativePath: string): string {
  return sha256(
    readFileSync(resolve(repositoryRoot, repositoryRelativePath)),
  );
}

function writeJson(name: string, value: unknown): void {
  writeFileSync(
    resolve(adoptionRoot, name),
    `${JSON.stringify(value, null, 2)}\n`,
  );
}

function readJson(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function fail(message: string): never {
  throw new Error(`FINANCIAL_SETTLEMENT_SFOL_ADOPTION:${message}`);
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
