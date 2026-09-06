#!/usr/bin/env -S node --import tsx
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  makeCompileEventSourcingContractUseCase,
  makeSha256ContentDigest,
  type EventSourcingContractSource,
} from "../../../domainspec-core/implementation/domainspec/backend/src/modules/event-sourcing-contract/index.ts";

const scriptPath = fileURLToPath(import.meta.url);
const scriptDir = dirname(scriptPath);
const packageRoot = resolve(scriptDir, "..");
const labRoot = resolve(packageRoot, "..");
const domainSpecRoot = resolve(labRoot, "../domainspec-core");
const sourcePath = resolve(
  packageRoot,
  "domainspec/event-sourcing/source.json",
);
const generatedRoot = resolve(
  packageRoot,
  "domainspec/event-sourcing/generated",
);
const contractPath = resolve(generatedRoot, "contract.json");
const receiptPath = resolve(generatedRoot, "compile-receipt.json");

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function pretty(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function relativeToLab(path: string): string {
  return relative(labRoot, path);
}

function boundFile(path: string, role: string, posture: string) {
  return {
    path: relativeToLab(path),
    sha256: sha256(readFileSync(path)),
    role,
    posture,
  };
}

const sourceBytes = readFileSync(sourcePath, "utf8");
const source = JSON.parse(sourceBytes) as EventSourcingContractSource;
const compile = makeCompileEventSourcingContractUseCase({
  contentDigest: makeSha256ContentDigest(),
});
const first = compile(source);
const second = compile(structuredClone(source));
const permuted = compile({
  ...source,
  streams: [...source.streams].reverse(),
  events: [...source.events].reverse(),
  projections: [...source.projections].reverse().map((projection) => ({
    ...projection,
    consumes: [...projection.consumes].reverse(),
  })),
  joins: [...source.joins].reverse().map((join) => ({
    ...join,
    semanticEventTypes: [...join.semanticEventTypes].reverse(),
  })),
});
if (
  first.canonicalJson !== second.canonicalJson ||
  first.digest !== second.digest ||
  first.canonicalJson !== permuted.canonicalJson ||
  first.digest !== permuted.digest
) {
  throw new Error("Event-sourcing compilation is not deterministic");
}

const schemaBindings = [...new Set(source.events.map((event) => event.payloadSchemaRef))]
  .sort()
  .map((schemaRef) => {
    const path = resolve(dirname(sourcePath), schemaRef);
    JSON.parse(readFileSync(path, "utf8"));
    return {
      path: schemaRef,
      sha256: sha256(readFileSync(path)),
      posture: "selected-governed-node-schema-candidate",
    };
  });

const compilerFiles = [
  resolve(
    domainSpecRoot,
    "implementation/domainspec/backend/src/modules/event-sourcing-contract/domain/contract.ts",
  ),
  resolve(
    domainSpecRoot,
    "implementation/domainspec/backend/src/modules/event-sourcing-contract/application/compile-event-sourcing-contract.ts",
  ),
  resolve(
    domainSpecRoot,
    "implementation/domainspec/backend/src/modules/event-sourcing-contract/infrastructure/sha256-content-digest.ts",
  ),
];
const semanticInputs = [
  boundFile(
    resolve(
      labRoot,
      "docs/decisions/0005-governed-ontology-node-architecture/decision.json",
    ),
    "selected governed-node architecture",
    "selected-candidate-authority-effect-none",
  ),
  boundFile(
    resolve(
      labRoot,
      "docs/decisions/0006-governed-node-definition-selection/decision.json",
    ),
    "selected governed-node definitions",
    "selected-candidate-authority-effect-none",
  ),
  boundFile(
    resolve(
      labRoot,
      "docs/decisions/0007-ontology-lifecycle-state-vocabulary/decision.json",
    ),
    "selected ontology lifecycle vocabulary",
    "selected-candidate-authority-effect-none",
  ),
  boundFile(
    resolve(packageRoot, "business-ontology.json"),
    "capability-local meaning",
    "candidate-unadmitted",
  ),
  boundFile(resolve(packageRoot, "product-capability.json"), "selected capability behavior candidate", "candidate-unadmitted"),
];
const receipt = {
  schema_version: "cal-event-sourcing-contract-compile-receipt/v1-candidate",
  receipt_id: "CAL-ESOV-COMP-01",
  status: "PASS",
  contract_id: first.contract.contractId,
  source: {
    path: relativeToLab(sourcePath),
    sha256: sha256(sourceBytes),
  },
  compiled_contract: {
    path: relativeToLab(contractPath),
    schema_version: first.contract.schemaVersion,
    sha256: first.digest,
  },
  compiler_sources: compilerFiles.map((path) =>
    boundFile(path, "DomainSpec event-sourcing compiler", "local-candidate"),
  ),
  semantic_inputs: semanticInputs,
  payload_schemas: schemaBindings,
  determinism: {
    repeated_run_byte_equality: true,
    permutation_byte_equality: true,
    digest_algorithm: first.digestAlgorithm,
  },
  topology: {
    stream_count: first.contract.streams.length,
    event_type_count: first.contract.events.length,
    projection_count: first.contract.projections.length,
    exact_reference_join_count: first.contract.joins.length,
    runtime_obligation_count: first.contract.runtimeObligations.length,
  },
  runtime_binding: {
    complete_node_and_relation_shapes: "compiled-candidate",
    complete_governance_shape: "compiled-candidate",
    exact_governance_join: "compiled-candidate-runtime-evidence-separate",
    context_projection: "compiled-candidate-runtime-evidence-separate",
  },
  authority_effect: "none",
  claim_ceiling:
    "Deterministic candidate contract compilation only; no DomainSpec profile or system-ontology admission, challenge runtime conformance, implementation acceptance, migration, publication, release, or deployment.",
};

const outputs = new Map<string, string>([
  [contractPath, first.canonicalJson],
  [receiptPath, pretty(receipt)],
]);
const checkOnly = process.argv.includes("--check");
const mismatches: string[] = [];
for (const [path, content] of outputs) {
  if (checkOnly) {
    try {
      if (readFileSync(path, "utf8") !== content) mismatches.push(relativeToLab(path));
    } catch {
      mismatches.push(relativeToLab(path));
    }
  } else {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, content);
  }
}

const status = mismatches.length === 0 ? "PASS" : "BLOCK";
process.stdout.write(
  pretty({
    status,
    mode: checkOnly ? "check" : "write",
    outputs: [...outputs.keys()].map(relativeToLab).sort(),
    mismatches,
    source_sha256: receipt.source.sha256,
    compiled_sha256: first.digest,
    repeated_run_byte_equality: true,
    permutation_byte_equality: true,
    authority_effect: "none",
  }),
);
process.exit(status === "PASS" ? 0 : 1);
