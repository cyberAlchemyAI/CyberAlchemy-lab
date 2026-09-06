#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import {
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";

import {
  NODE_LOGIC_ENVELOPE_VERSION,
  NODE_PROJECTION_ADMISSION_VERSION,
  NODE_PROOF_CONTEXT_VERSION,
  projectNodeLogic,
  type NodeLogicEnvelope,
} from "../test-derivation-engine/src/sfol/node-source/index";
import {
  typecheckLogicModule,
} from "../test-derivation-engine/src/sfol/language/typecheck";
import {
  canonicalJson,
} from "../test-derivation-engine/src/sfol/language/contracts";
import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
} from "./minted-project/views";

type JsonRecord = Record<string, any>;

const implRoot = resolve(new URL("..", import.meta.url).pathname);
const projectRoot = resolve(
  process.cwd(),
  getArg("--project") ??
    "spec/features/financial-settlement",
);
const registryPath = resolve(
  process.cwd(),
  getArg("--registry") ??
    "spec/sfol-profile/minted-project-profile.json",
);
const outRoot = resolve(
  projectRoot,
  getArg("--out") ?? "generated",
);
const writeOutputs = !process.argv.includes("--verify-only");
const profileHandle = "sfol-development-explicit-v0.1";
const admittedNodeIds = [
  "financial-settlement.DealSplitCalculation",
  "financial-settlement.GenerateSettlement",
] as const;

export function assertContainedOutput(
  sourceRoot: string,
  outputRoot: string,
): void {
  const relativeOutput = relative(sourceRoot, outputRoot);
  if (
    outputRoot === sourceRoot ||
    isAbsolute(relativeOutput) ||
    relativeOutput === ".." ||
    relativeOutput.startsWith(`..${separator()}`)
  ) {
    throw new Error(
      "FINANCIAL_SETTLEMENT_SFOL_OUTPUT_INVALID: generated output must remain below the feature project",
    );
  }
}

assertContainedOutput(projectRoot, outRoot);

const options = {
  developmentProfileRegistry: {
    path: registryPath,
    handle: profileHandle,
  },
};
const first = buildMintedProjectViews(projectRoot, options);
const second = buildMintedProjectViews(projectRoot, options);
for (const key of [
  "graphBytes",
  "sourceManifestBytes",
  "markdownBytes",
  "markdownViewBytes",
  "buildReceiptBytes",
] as const) {
  if (first[key] !== second[key]) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_NONDETERMINISTIC:${key}`,
    );
  }
}
const verification = verifyMintedProjectBuild(projectRoot, first);
if (verification.status !== "pass") {
  throw new Error(
    `FINANCIAL_SETTLEMENT_SFOL_BUILD_INVALID:${verification.codes.join(",")}`,
  );
}

const projection = projectNodeLogic(
  {
    schema_version: NODE_PROOF_CONTEXT_VERSION,
    route: "canonical-minted-project-build",
    graph_bytes: first.graphBytes,
    source_manifest_bytes: first.sourceManifestBytes,
    build_receipt_bytes: first.buildReceiptBytes,
  },
  {
    schema_version: NODE_PROJECTION_ADMISSION_VERSION,
    profile_id: "sfol-development",
    profile_version: "0.1",
    logic_schema_versions: ["domainspec-node-logic/v1"],
    admitted_node_ids: admittedNodeIds,
  },
);
if (!projection.ok) {
  throw new Error(
    `FINANCIAL_SETTLEMENT_SFOL_PROJECTION_INVALID:${JSON.stringify(projection.diagnostics)}`,
  );
}

const proposalPath = resolve(projectRoot, "sfol/source-proposal.json");
const proposal = readJson(proposalPath);
const clauses = new Map(
  (proposal.clauses as JsonRecord[]).map((clause) => [
    clause.clause_id,
    clause,
  ]),
);
const expectedByNode = new Map<string, JsonRecord>([
  [
    "financial-settlement.DealSplitCalculation",
    requireClause(clauses, "C3"),
  ],
  [
    "financial-settlement.GenerateSettlement",
    requireClause(clauses, "P4"),
  ],
]);

const moduleReceipts = projection.value.map((envelope) =>
  verifyProjectedModule(
    envelope,
    expectedByNode.get(envelope.node.node_id),
  ),
);
if (
  canonicalJson(moduleReceipts.map((entry) => entry.node_id).sort()) !==
  canonicalJson([...admittedNodeIds].sort())
) {
  throw new Error(
    "FINANCIAL_SETTLEMENT_SFOL_PROJECTION_SET_MISMATCH",
  );
}

const artifactDigests = {
  graph: sha256(first.graphBytes),
  source_manifest: sha256(first.sourceManifestBytes),
  markdown: sha256(first.markdownBytes),
  markdown_view: sha256(first.markdownViewBytes),
  build_receipt: sha256(first.buildReceiptBytes),
};
const projectionReceiptUnsigned = {
  schema_version:
    "financial-settlement-sfol-build-projection-receipt/v1",
  status: "pass",
  authority: "experimental-test-lane-evidence",
  authority_effect: "none",
  formal_owner_approval: false,
  release_admission: "not-granted",
  project_id: first.graph.project_id,
  profile_handle: profileHandle,
  profile_registry: {
    path: relative(implRoot, registryPath).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(registryPath)),
  },
  source_proposal: {
    path: relative(implRoot, proposalPath).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(proposalPath)),
  },
  proof_context: projection.value[0]?.proof_context,
  artifacts: artifactDigests,
  deterministic_double_build: true,
  build_verification: "pass",
  modules: moduleReceipts,
};
const projectionReceipt = {
  ...projectionReceiptUnsigned,
  receipt_digest: digest(projectionReceiptUnsigned),
};
const digestMatrix = {
  schema_version: "financial-settlement-sfol-digest-matrix/v1",
  status: "pass",
  artifact_digests: artifactDigests,
  proposal_digest: projectionReceipt.source_proposal.sha256,
  profile_registry_digest:
    projectionReceipt.profile_registry.sha256,
  module_digests: Object.fromEntries(
    moduleReceipts.map((entry) => [
      entry.module_id,
      entry.module_digest,
    ]),
  ),
  clause_ast_digests: Object.fromEntries(
    moduleReceipts.map((entry) => [
      entry.clause_id,
      {
        proposal: entry.proposed_ast_digest,
        projected_proposal: entry.projected_proposal_ast_digest,
        materialized_clause: entry.materialized_clause_digest,
      },
    ]),
  ),
  clause_semantic_digests: Object.fromEntries(
    moduleReceipts.map((entry) => [
      entry.clause_id,
      {
        proposal: entry.proposed_semantic_digest,
        projected: entry.projected_semantic_digest,
      },
    ]),
  ),
};
const corePathSet = buildCorePathSet();

if (writeOutputs) {
  rmSync(outRoot, { recursive: true, force: true });
  mkdirSync(outRoot, { recursive: true });
  for (const [name, content] of [
    ["graph.json", first.graphBytes],
    ["source-manifest.json", first.sourceManifestBytes],
    ["SPEC.md", first.markdownBytes],
    ["markdown-view.json", first.markdownViewBytes],
    ["build-receipt.json", first.buildReceiptBytes],
    ["sfol-projection-receipt.json", bytes(projectionReceipt)],
    ["deterministic-digest-matrix.json", bytes(digestMatrix)],
    ["core-path-set-before-adoption.json", bytes(corePathSet)],
  ] as const) {
    write(resolve(outRoot, name), content);
  }
}

console.log(
  JSON.stringify(
    {
      status: "PASS",
      project_id: first.graph.project_id,
      nodes: first.graph.nodes.length,
      edges: first.graph.edges.length,
      projected_modules: moduleReceipts.length,
      deterministic_double_build: true,
      graph_digest: artifactDigests.graph,
      projection_receipt_digest:
        projectionReceipt.receipt_digest,
      output: relative(implRoot, outRoot).replaceAll("\\", "/"),
      wrote_outputs: writeOutputs,
      formal_owner_approval: false,
      release_admission: "not-granted",
    },
    null,
    2,
  ),
);

function verifyProjectedModule(
  envelope: NodeLogicEnvelope,
  proposalClause: JsonRecord | undefined,
): JsonRecord {
  if (
    envelope.schema_version !== NODE_LOGIC_ENVELOPE_VERSION ||
    proposalClause === undefined
  ) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_MODULE_UNBOUND:${envelope.node.node_id}`,
    );
  }
  const typed = typecheckLogicModule(envelope.logic);
  if (!typed.ok) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_TYPE_INVALID:${JSON.stringify(typed.diagnostics)}`,
    );
  }
  const projectedProposal = projectProposalAst(
    envelope,
    proposalClause.clause_id,
  );
  const projectedProposalDigest = digest(projectedProposal);
  if (projectedProposalDigest !== proposalClause.ast_digest) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_AST_DRIFT:${proposalClause.clause_id}:${projectedProposalDigest}:${proposalClause.ast_digest}`,
    );
  }
  const normalized = normalizeProjectedSemantics(
    envelope,
    proposalClause.clause_id,
  );
  const semanticDigest = digest(normalized);
  if (semanticDigest !== proposalClause.semantic_digest) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_SEMANTIC_DRIFT:${proposalClause.clause_id}`,
    );
  }
  const clause = envelope.logic.clauses[0];
  if (clause === undefined || envelope.logic.clauses.length !== 1) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_CLAUSE_SET_INVALID:${proposalClause.clause_id}`,
    );
  }
  return {
    node_id: envelope.node.node_id,
    node_digest: envelope.node.node_digest,
    source_path: envelope.node.source_path,
    module_id: envelope.module_id,
    module_digest: envelope.logic_digest,
    typed_module_digest: digest(typed.value),
    clause_id: proposalClause.clause_id,
    projected_clause_id: clause.clause_id,
    proposed_ast_digest: proposalClause.ast_digest,
    projected_proposal_ast_digest: projectedProposalDigest,
    materialized_clause_digest: digest(clause),
    proposed_semantic_digest: proposalClause.semantic_digest,
    projected_semantic_digest: semanticDigest,
    source_status: clause.status,
  };
}

function projectProposalAst(
  envelope: NodeLogicEnvelope,
  clauseId: string,
): JsonRecord {
  const logic = envelope.logic;
  const clause = logic.clauses[0];
  if (clause === undefined) {
    throw new Error(`FINANCIAL_SETTLEMENT_SFOL_CLAUSE_MISSING:${clauseId}`);
  }
  if (clauseId === "C3") {
    return {
      schema_version: "financial-settlement-proposed-ast/v1",
      node_id: envelope.node.node_id,
      node_kind: envelope.node.kind,
      module_id: envelope.module_id,
      clause: stripMaterialization(clause),
    };
  }
  if (clauseId === "P4") {
    assertP4Expression(clause.expression);
    const stripped = stripMaterialization(clause) as JsonRecord;
    const declarationOrder = [
      "financial-settlement.PayoutPre",
      "financial-settlement.PayoutPost",
      "financial-settlement.PayoutPayload",
      "financial-settlement.PayoutEffect",
    ];
    const declarations = [...logic.declarations].sort(
      (left, right) =>
        declarationOrder.indexOf(left.declaration_id) -
        declarationOrder.indexOf(right.declaration_id),
    );
    return {
      schema_version: "financial-settlement-proposed-ast/v1",
      node_id: envelope.node.node_id,
      node_kind: envelope.node.kind,
      module_id: envelope.module_id,
      declarations: stripMaterialization(declarations),
      clause: {
        clause_id: stripped.clause_id,
        kind: stripped.kind,
        status: stripped.status,
        logical_form: "implication",
        inputs: stripped.inputs,
        result_sort: stripped.result_sort,
        relation: {
          antecedent: {
            all: [
              "pre.total_payout > 0",
              "pre.existing_payout_count = 0",
            ],
          },
          consequent: {
            all: [
              "post.payout_write_count = 1",
              "post.payout_event_count = 1",
              "effects = [write(PAYOUT, pre.total_payout, pre.end_date), event(PayoutCreated, pre.total_payout, pre.end_date)]",
            ],
          },
        },
        observation_sort: stripped.observation_sort,
      },
    };
  }
  throw new Error(
    `FINANCIAL_SETTLEMENT_SFOL_CLAUSE_UNKNOWN:${clauseId}`,
  );
}

function normalizeProjectedSemantics(
  envelope: NodeLogicEnvelope,
  clauseId: string,
): JsonRecord {
  const clause = envelope.logic.clauses[0];
  if (clause === undefined) {
    throw new Error(`FINANCIAL_SETTLEMENT_SFOL_CLAUSE_MISSING:${clauseId}`);
  }
  if (clauseId === "C3") {
    const expression = stripMaterialization(
      clause.expression,
    ) as JsonRecord;
    if (
      expression.tag !== "conditional" ||
      expression.condition?.operator !== "gte" ||
      expression.condition?.left?.name !== "limit_value" ||
      expression.condition?.right?.value?.value !== "100" ||
      expression.when_true?.value?.numerator !== "1" ||
      expression.when_true?.value?.denominator !== "2" ||
      expression.when_false?.value?.numerator !== "2" ||
      expression.when_false?.value?.denominator !== "5"
    ) {
      throw new Error("FINANCIAL_SETTLEMENT_SFOL_C3_SHAPE_INVALID");
    }
    return {
      schema_version: "financial-settlement-normalized-semantic/v1",
      clause_id: "C3",
      function: "player-share-for-limit",
      input: {
        name: "limit_value",
        sort: "integer",
        adapter: "strip-NL-prefix-and-parse-base-10",
      },
      result: {
        sort: "rational",
        conditional: {
          operator: "gte",
          threshold: 100,
          when_true: { numerator: 1, denominator: 2 },
          when_false: { numerator: 2, denominator: 5 },
        },
      },
    };
  }
  assertP4Expression(clause.expression);
  return {
    schema_version: "financial-settlement-normalized-semantic/v1",
    clause_id: "P4",
    logical_form: "implication",
    antecedent: {
      all: [
        { operator: "gt", left: "totalPayout", right: 0 },
        {
          operator: "not-exists",
          transaction: { type: "PAYOUT", date: "endDate" },
        },
      ],
    },
    consequent: {
      ordered_observations: [
        {
          sequence: 0,
          kind: "write",
          name: "PAYOUT",
          payload: { amount: "totalPayout", date: "endDate" },
        },
        {
          sequence: 1,
          kind: "event",
          name: "PayoutCreated",
          payload: { amount: "totalPayout", date: "endDate" },
        },
      ],
      cardinality: {
        "PAYOUT-write": 1,
        "PayoutCreated-event": 1,
      },
    },
    converse_admitted: false,
  };
}

function assertP4Expression(input: unknown): void {
  const expression = stripMaterialization(input) as JsonRecord;
  const antecedent = expression.operands?.[0]?.operand;
  const consequent = expression.operands?.[1];
  const effects = consequent?.operands?.[2]?.right?.items;
  const write = effects?.[0];
  const event = effects?.[1];
  const signature = {
    root: [expression.tag, expression.operator],
    antecedent: [
      expression.operands?.[0]?.tag,
      antecedent?.tag,
      antecedent?.operator,
      antecedent?.operands?.[0]?.operator,
      antecedent?.operands?.[0]?.left?.field,
      antecedent?.operands?.[0]?.right?.value?.value,
      antecedent?.operands?.[1]?.operator,
      antecedent?.operands?.[1]?.left?.field,
      antecedent?.operands?.[1]?.right?.value?.value,
    ],
    consequent: [
      consequent?.tag,
      consequent?.operator,
      consequent?.operands?.[0]?.left?.field,
      consequent?.operands?.[0]?.right?.value?.value,
      consequent?.operands?.[1]?.left?.field,
      consequent?.operands?.[1]?.right?.value?.value,
      consequent?.operands?.[2]?.operator,
      consequent?.operands?.[2]?.left?.name,
      effects?.length,
    ],
    write: effectSignature(write),
    event: effectSignature(event),
  };
  const expected = {
    root: ["boolean", "or"],
    antecedent: [
      "not",
      "boolean",
      "and",
      "gt",
      "total_payout",
      "0",
      "eq",
      "existing_payout_count",
      "0",
    ],
    consequent: [
      "boolean",
      "and",
      "payout_write_count",
      "1",
      "payout_event_count",
      "1",
      "eq",
      "effects",
      2,
    ],
    write: [
      "financial-settlement.PayoutEffect",
      "0",
      "write",
      "PAYOUT",
      "financial-settlement.PayoutPayload",
      "total_payout",
      "end_date",
    ],
    event: [
      "financial-settlement.PayoutEffect",
      "1",
      "event",
      "PayoutCreated",
      "financial-settlement.PayoutPayload",
      "total_payout",
      "end_date",
    ],
  };
  if (canonicalJson(signature) !== canonicalJson(expected)) {
    throw new Error("FINANCIAL_SETTLEMENT_SFOL_P4_SHAPE_INVALID");
  }
}

function effectSignature(effect: JsonRecord | undefined): unknown[] {
  const fields = new Map<string, JsonRecord>(
    (Array.isArray(effect?.fields) ? effect.fields : [])
      .filter(isJsonRecord)
      .map((field): [string, JsonRecord] => [
        String(field.name),
        asJsonRecord(field.value),
      ]),
  );
  const payload = fields.get("payload");
  const payloadFields = new Map<string, JsonRecord>(
    (Array.isArray(payload?.fields) ? payload.fields : [])
      .filter(isJsonRecord)
      .map((field): [string, JsonRecord] => [
        String(field.name),
        asJsonRecord(field.value),
      ]),
  );
  return [
    effect?.declaration_id,
    fields.get("sequence")?.value?.value,
    fields.get("kind")?.value?.value,
    fields.get("name")?.value?.value,
    payload?.declaration_id,
    payloadFields.get("amount")?.field,
    payloadFields.get("date")?.field,
  ];
}

function isJsonRecord(value: unknown): value is JsonRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asJsonRecord(value: unknown): JsonRecord {
  return isJsonRecord(value) ? value : {};
}

function stripMaterialization(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(stripMaterialization);
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as JsonRecord)
        .filter(([key]) => key !== "span" && key !== "required")
        .map(([key, child]) => [key, stripMaterialization(child)]),
    );
  }
  return value;
}

function requireClause(
  clauses: Map<string, JsonRecord>,
  clauseId: string,
): JsonRecord {
  const clause = clauses.get(clauseId);
  if (clause === undefined) {
    throw new Error(
      `FINANCIAL_SETTLEMENT_SFOL_PROPOSAL_CLAUSE_MISSING:${clauseId}`,
    );
  }
  return clause;
}

function readJson(path: string): JsonRecord {
  return JSON.parse(readFileSync(path, "utf8")) as JsonRecord;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function digest(value: unknown): string {
  return sha256(canonicalJson(value));
}

function bytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function write(path: string, content: string): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

function getArg(name: string): string | undefined {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function buildCorePathSet(): JsonRecord {
  const coreRoot = resolve(
    implRoot,
    "test-derivation-engine/src/sfol",
  );
  const files = listFiles(coreRoot).map((absolutePath) => ({
    path: relative(implRoot, absolutePath).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(absolutePath)),
  }));
  const unsigned = {
    schema_version: "domainspec-sfol-core-path-set/v1",
    lifecycle_point: "after-bc-003-before-bc-005",
    root: "test-derivation-engine/src/sfol",
    files,
  };
  return {
    ...unsigned,
    path_set_digest: digest(unsigned),
  };
}

function listFiles(root: string): string[] {
  return readdirSync(root, { withFileTypes: true })
    .flatMap((entry) => {
      const path = resolve(root, entry.name);
      return entry.isDirectory() ? listFiles(path) : [path];
    })
    .sort();
}

function separator(): string {
  return process.platform === "win32" ? "\\" : "/";
}
