import { canonicalize } from "./contract-publication.js";
import type { DevelopmentBuild } from "./development-engine.js";
import type { DevelopmentCoreRun } from "./proof-engine.js";
import { sha256 } from "./validation/validate-semantics.js";

export const DEVELOPMENT_CONSUMER_IDS = [
  "iolm-development-adapter@1",
  "body-war-development-adapter@1",
] as const;

export type DevelopmentConsumerId = (typeof DEVELOPMENT_CONSUMER_IDS)[number];

type Projection = {
  node_ids: string[];
  edge_tuples: string[];
};

export type IolmDevelopmentEvidence = {
  schema_version: "bte-iolm-development-evidence/v1";
  consumer_id: "iolm-development-adapter@1";
  core_sha256: string;
  method: "GET";
  projections: {
    graph: Projection;
    hierarchy: Projection;
    table: Projection;
  };
  declared_writes: [];
};

export type BodyWarDevelopmentEvidence = {
  schema_version: "bte-body-war-development-evidence/v1";
  consumer_id: "body-war-development-adapter@1";
  core_sha256: string;
  projection: {
    nodes: Array<{
      node_id: string;
      feature_id: string;
      kind: string;
    }>;
    relationships: Array<{
      edge_id: string;
      family: string;
      from: string;
      to: string;
      ordinal?: number;
    }>;
  };
  allowlisted_fields: {
    node: ["node_id", "feature_id", "kind"];
    relationship: ["edge_id", "family", "from", "to", "ordinal"];
  };
  declared_writes: [];
};

export type DevelopmentConsumerEvidence =
  | IolmDevelopmentEvidence
  | BodyWarDevelopmentEvidence;

export type DevelopmentConsumerReceipt = {
  schema_version: "bte-development-consumer-receipt/v1";
  receipt_id: string;
  consumer_id: DevelopmentConsumerId;
  producer: "iolm-development-adapter" | "body-war-development-adapter";
  core_sha256: string;
  evidence_sha256: string;
  result: "pass";
  admission: "development-only";
};

export type DevelopmentConsumerRun = {
  evidence: DevelopmentConsumerEvidence;
  evidenceBytes: string;
  receipt: DevelopmentConsumerReceipt;
  receiptBytes: string;
};

export type DevelopmentConsumerReplay = {
  schema_version: "bte-development-consumer-replay/v1";
  replay_id: string;
  consumer_id: DevelopmentConsumerId;
  producer: "bte-development-replayer";
  core_sha256: string;
  consumer_receipt_sha256: string;
  checks: string[];
  result: "pass";
  admission: "development-only";
};

export type DevelopmentConsumerAggregate = {
  schema_version: "bte-development-consumer-aggregate/v1";
  aggregate_id: "bte-development-consumers";
  core_sha256: string;
  required_consumers: DevelopmentConsumerId[];
  replay_handles: Array<{
    consumer_id: DevelopmentConsumerId;
    sha256: string;
  }>;
  result: "pass";
  admission: "development-only";
};

export type DevelopmentConsumers = {
  runs: DevelopmentConsumerRun[];
  replays: DevelopmentConsumerReplay[];
  aggregate: DevelopmentConsumerAggregate;
  aggregateBytes: string;
};

export type DevelopmentTerminalAggregate = {
  schema_version: "bte-development-terminal-aggregate/v1";
  aggregate_id: "bte-development-terminal";
  core_sha256: string;
  consumer_aggregate_sha256: string;
  required_handles: ["core", "consumers"];
  result: "pass";
  admission: "development-only";
};

export type DevelopmentTerminalRun = {
  aggregate: DevelopmentTerminalAggregate;
  aggregateBytes: string;
};

export const CONSUMER_ERROR_CODES = [
  "BTE_CONSUMER_CORE_MISMATCH",
  "BTE_CONSUMER_EVIDENCE_TAMPERED",
  "BTE_CONSUMER_IOLM_PARITY",
  "BTE_CONSUMER_BODY_WAR_REDACTION",
  "BTE_CONSUMER_WRITES_DECLARED",
  "BTE_CONSUMER_RECEIPT_SELF_AUTHORED",
  "BTE_CONSUMER_SET_INCOMPLETE",
  "BTE_CONSUMER_REPLAY_MISMATCH",
  "BTE_TERMINAL_AGGREGATE_MISMATCH",
] as const;

export type ConsumerErrorCode = (typeof CONSUMER_ERROR_CODES)[number];

export class ConsumerEngineError extends Error {
  readonly code: ConsumerErrorCode;
  readonly subject: string;

  constructor(code: ConsumerErrorCode, subject: string, detail: string) {
    super(`${code}:${subject}:${detail}`);
    this.name = "ConsumerEngineError";
    this.code = code;
    this.subject = subject;
  }
}

function bytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

function coreSha(core: DevelopmentCoreRun): string {
  return sha256(core.aggregateBytes);
}

function projection(build: DevelopmentBuild): Projection {
  return {
    node_ids: build.graph.nodes.map(({ node_id }) => node_id).sort(),
    edge_tuples: build.graph.edges
      .map(({ edge_id, family, from, to, ordinal }) =>
        [edge_id, family, from, to, ordinal ?? ""].join("|"),
      )
      .sort(),
  };
}

function bodyWarProjection(
  build: DevelopmentBuild,
): BodyWarDevelopmentEvidence["projection"] {
  return {
    nodes: build.graph.nodes
      .map(({ node_id, feature_id, kind }) => ({ node_id, feature_id, kind }))
      .sort((left, right) => left.node_id.localeCompare(right.node_id)),
    relationships: build.graph.edges
      .map(({ edge_id, family, from, to, ordinal }) => ({
        edge_id,
        family,
        from,
        to,
        ...(ordinal === undefined ? {} : { ordinal }),
      }))
      .sort((left, right) => left.edge_id.localeCompare(right.edge_id)),
  };
}

function consumerReceipt(
  evidence: DevelopmentConsumerEvidence,
): DevelopmentConsumerReceipt {
  const producer =
    evidence.consumer_id === "iolm-development-adapter@1"
      ? "iolm-development-adapter"
      : "body-war-development-adapter";
  return {
    schema_version: "bte-development-consumer-receipt/v1",
    receipt_id: `consumer/${evidence.consumer_id}`,
    consumer_id: evidence.consumer_id,
    producer,
    core_sha256: evidence.core_sha256,
    evidence_sha256: sha256(bytes(evidence)),
    result: "pass",
    admission: "development-only",
  };
}

function consumerRun(
  evidence: DevelopmentConsumerEvidence,
): DevelopmentConsumerRun {
  const receipt = consumerReceipt(evidence);
  return {
    evidence,
    evidenceBytes: bytes(evidence),
    receipt,
    receiptBytes: bytes(receipt),
  };
}

export function runIolmDevelopmentConsumer(
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
): DevelopmentConsumerRun {
  const normalized = projection(build);
  return consumerRun({
    schema_version: "bte-iolm-development-evidence/v1",
    consumer_id: "iolm-development-adapter@1",
    core_sha256: coreSha(core),
    method: "GET",
    projections: {
      graph: structuredClone(normalized),
      hierarchy: structuredClone(normalized),
      table: structuredClone(normalized),
    },
    declared_writes: [],
  });
}

export function runBodyWarDevelopmentConsumer(
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
): DevelopmentConsumerRun {
  return consumerRun({
    schema_version: "bte-body-war-development-evidence/v1",
    consumer_id: "body-war-development-adapter@1",
    core_sha256: coreSha(core),
    projection: bodyWarProjection(build),
    allowlisted_fields: {
      node: ["node_id", "feature_id", "kind"],
      relationship: ["edge_id", "family", "from", "to", "ordinal"],
    },
    declared_writes: [],
  });
}

function containsForbiddenBodyWarField(value: unknown): boolean {
  if (Array.isArray(value)) {
    return value.some(containsForbiddenBodyWarField);
  }
  if (value === null || typeof value !== "object") return false;
  return Object.entries(value).some(
    ([key, child]) =>
      ["body", "intent", "fields", "values", "states", "equality"].includes(
        key,
      ) || containsForbiddenBodyWarField(child),
  );
}

export function replayDevelopmentConsumer(
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
  run: DevelopmentConsumerRun,
): DevelopmentConsumerReplay {
  const expectedCoreSha = coreSha(core);
  const consumerId = run.receipt.consumer_id;
  if (
    run.evidence.core_sha256 !== expectedCoreSha ||
    run.receipt.core_sha256 !== expectedCoreSha
  ) {
    throw new ConsumerEngineError(
      "BTE_CONSUMER_CORE_MISMATCH",
      consumerId,
      "consumer evidence does not cite the exact core",
    );
  }
  if (
    run.evidenceBytes !== bytes(run.evidence) ||
    run.receiptBytes !== bytes(run.receipt) ||
    run.receipt.evidence_sha256 !== sha256(run.evidenceBytes)
  ) {
    throw new ConsumerEngineError(
      "BTE_CONSUMER_EVIDENCE_TAMPERED",
      consumerId,
      "consumer evidence or receipt bytes do not recompose",
    );
  }
  if (
    run.receipt.producer ===
    ("bte-development-replayer" as DevelopmentConsumerReceipt["producer"])
  ) {
    throw new ConsumerEngineError(
      "BTE_CONSUMER_RECEIPT_SELF_AUTHORED",
      consumerId,
      "the BTE replayer cannot produce consumer evidence",
    );
  }

  const checks: string[] = ["exact-core", "canonical-evidence", "read-only"];
  if (run.evidence.declared_writes.length !== 0) {
    throw new ConsumerEngineError(
      "BTE_CONSUMER_WRITES_DECLARED",
      consumerId,
      "development consumer must remain read-only",
    );
  }

  if (run.evidence.consumer_id === "iolm-development-adapter@1") {
    const expected = projection(build);
    const { graph, hierarchy, table } = run.evidence.projections;
    if (
      run.evidence.method !== "GET" ||
      canonicalize(graph) !== canonicalize(hierarchy) ||
      canonicalize(graph) !== canonicalize(table) ||
      canonicalize(graph) !== canonicalize(expected)
    ) {
      throw new ConsumerEngineError(
        "BTE_CONSUMER_IOLM_PARITY",
        consumerId,
        "graph, hierarchy, and table GET projections must have exact parity",
      );
    }
    checks.push("graph-hierarchy-table-get-parity");
  } else {
    if (
      containsForbiddenBodyWarField(run.evidence.projection) ||
      canonicalize(run.evidence.projection) !==
        canonicalize(bodyWarProjection(build))
    ) {
      throw new ConsumerEngineError(
        "BTE_CONSUMER_BODY_WAR_REDACTION",
        consumerId,
        "Body War projection is not the exact allowlisted view",
      );
    }
    checks.push("allowlisted-redaction");
  }

  return {
    schema_version: "bte-development-consumer-replay/v1",
    replay_id: `replay/${consumerId}`,
    consumer_id: consumerId,
    producer: "bte-development-replayer",
    core_sha256: expectedCoreSha,
    consumer_receipt_sha256: sha256(run.receiptBytes),
    checks,
    result: "pass",
    admission: "development-only",
  };
}

export function runDevelopmentConsumers(
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
): DevelopmentConsumers {
  const runs = [
    runIolmDevelopmentConsumer(build, core),
    runBodyWarDevelopmentConsumer(build, core),
  ];
  const replays = runs.map((run) =>
    replayDevelopmentConsumer(build, core, run),
  );
  if (
    replays.length !== DEVELOPMENT_CONSUMER_IDS.length ||
    !DEVELOPMENT_CONSUMER_IDS.every(
      (consumerId) =>
        replays.filter(({ consumer_id }) => consumer_id === consumerId)
          .length === 1,
    )
  ) {
    throw new ConsumerEngineError(
      "BTE_CONSUMER_SET_INCOMPLETE",
      "bte-development-consumers",
      "exactly one replay is required for each development consumer",
    );
  }
  const aggregate: DevelopmentConsumerAggregate = {
    schema_version: "bte-development-consumer-aggregate/v1",
    aggregate_id: "bte-development-consumers",
    core_sha256: coreSha(core),
    required_consumers: [...DEVELOPMENT_CONSUMER_IDS],
    replay_handles: replays.map((replay) => ({
      consumer_id: replay.consumer_id,
      sha256: sha256(bytes(replay)),
    })),
    result: "pass",
    admission: "development-only",
  };
  return {
    runs,
    replays,
    aggregate,
    aggregateBytes: bytes(aggregate),
  };
}

export function replayDevelopmentConsumers(
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
  consumers: DevelopmentConsumers,
): { result: "pass" | "fail"; codes: ConsumerErrorCode[] } {
  try {
    const expected = runDevelopmentConsumers(build, core);
    if (
      consumers.aggregateBytes !== bytes(consumers.aggregate) ||
      consumers.aggregateBytes !== expected.aggregateBytes ||
      canonicalize(consumers.aggregate) !== canonicalize(expected.aggregate) ||
      canonicalize(consumers.runs) !== canonicalize(expected.runs) ||
      canonicalize(consumers.replays) !== canonicalize(expected.replays)
    ) {
      return { result: "fail", codes: ["BTE_CONSUMER_REPLAY_MISMATCH"] };
    }
    return { result: "pass", codes: [] };
  } catch (error) {
    if (error instanceof ConsumerEngineError) {
      return { result: "fail", codes: [error.code] };
    }
    throw error;
  }
}

export function composeDevelopmentTerminal(
  core: DevelopmentCoreRun,
  consumers: DevelopmentConsumers,
): DevelopmentTerminalRun {
  if (consumers.aggregate.core_sha256 !== coreSha(core)) {
    throw new ConsumerEngineError(
      "BTE_TERMINAL_AGGREGATE_MISMATCH",
      "bte-development-terminal",
      "consumer aggregate does not cite the exact core",
    );
  }
  const aggregate: DevelopmentTerminalAggregate = {
    schema_version: "bte-development-terminal-aggregate/v1",
    aggregate_id: "bte-development-terminal",
    core_sha256: coreSha(core),
    consumer_aggregate_sha256: sha256(consumers.aggregateBytes),
    required_handles: ["core", "consumers"],
    result: "pass",
    admission: "development-only",
  };
  return { aggregate, aggregateBytes: bytes(aggregate) };
}

export function replayDevelopmentTerminal(
  core: DevelopmentCoreRun,
  consumers: DevelopmentConsumers,
  terminal: DevelopmentTerminalRun,
): { result: "pass" | "fail"; codes: ConsumerErrorCode[] } {
  try {
    const expected = composeDevelopmentTerminal(core, consumers);
    if (
      terminal.aggregateBytes !== bytes(terminal.aggregate) ||
      terminal.aggregateBytes !== expected.aggregateBytes ||
      canonicalize(terminal.aggregate) !== canonicalize(expected.aggregate)
    ) {
      return {
        result: "fail",
        codes: ["BTE_TERMINAL_AGGREGATE_MISMATCH"],
      };
    }
    return { result: "pass", codes: [] };
  } catch (error) {
    if (error instanceof ConsumerEngineError) {
      return { result: "fail", codes: [error.code] };
    }
    throw error;
  }
}
