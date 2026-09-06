import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { compileMintedProject } from "../../../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/compiler.ts";
import {
  canonicalizeCompiledEventSourcingContract,
  compileEventSourcingContract,
  type EventSourcingContractSource,
} from "../../../../domainspec-core/implementation/domainspec/backend/src/modules/event-sourcing-contract/domain/contract.ts";

const packageRoot = dirname(fileURLToPath(import.meta.url));
const mintedRoot = resolve(packageRoot, "domainspec");
const registryPath = resolve(mintedRoot, "development-profile-registry.json");
const eventSourcePath = resolve(packageRoot, "contracts/event-sourcing-source.json");
const handle = "cal-ontology-runtime-integration-explicit-v0.1";

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function assertEqual(left: string, right: string, label: string): void {
  if (left !== right) {
    throw new Error(`${label} is not deterministic`);
  }
}

const mintedA = compileMintedProject(mintedRoot, {
  developmentProfileRegistry: { path: registryPath, handle },
});
const mintedB = compileMintedProject(mintedRoot, {
  developmentProfileRegistry: { path: registryPath, handle },
});
assertEqual(mintedA.graphBytes, mintedB.graphBytes, "minted graph bytes");
assertEqual(
  mintedA.sourceManifestBytes,
  mintedB.sourceManifestBytes,
  "minted source-manifest bytes",
);

const eventSource = JSON.parse(
  readFileSync(eventSourcePath, "utf8"),
) as EventSourcingContractSource;
const eventA = canonicalizeCompiledEventSourcingContract(
  compileEventSourcingContract(eventSource),
);
const eventB = canonicalizeCompiledEventSourcingContract(
  compileEventSourcingContract(eventSource),
);
assertEqual(eventA, eventB, "event-sourcing contract bytes");

const result = {
  schema_version: "cal-d65-s4-compile-check/v1",
  result: "PASS",
  materialized_outputs_written: false,
  minted: {
    node_count: mintedA.graph.nodes.length,
    edge_count: mintedA.graph.edges.length,
    source_record_count: mintedA.sourceManifest.records.length,
    source_set_digest: mintedA.graph.source_set_digest,
    graph_sha256: sha256(mintedA.graphBytes),
    source_manifest_sha256: sha256(mintedA.sourceManifestBytes),
    deterministic_double_compile: true,
  },
  event_sourcing: {
    stream_count: eventSource.streams.length,
    event_count: eventSource.events.length,
    projection_count: eventSource.projections.length,
    join_count: eventSource.joins.length,
    compiled_contract_sha256: sha256(eventA),
    deterministic_double_compile: true,
  },
  claim_ceiling:
    "Compile validation produces in-memory candidate evidence only; no graph, system ontology, admission, implementation, migration, or cutover is granted.",
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
