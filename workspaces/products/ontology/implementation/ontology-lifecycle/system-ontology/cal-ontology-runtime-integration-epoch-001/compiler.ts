import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { compileMintedProject } from "../../../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/compiler.ts";
import {
  canonicalizeCompiledEventSourcingContract,
  compileEventSourcingContract,
  type EventSourcingContractSource,
} from "../../../../domainspec-core/implementation/domainspec/backend/src/modules/event-sourcing-contract/domain/contract.ts";

type JsonRecord = Record<string, any>;
type SourceRecord = { source_id: string; path: string; sha256: string; role: string };

const packageRoot = dirname(fileURLToPath(import.meta.url));
const sourcePackageRoot = resolve(
  packageRoot,
  "../../domainspec-source/cal-ontology-runtime-integration-epoch-001",
);
const mintedRoot = resolve(sourcePackageRoot, "domainspec");
const registryPath = resolve(mintedRoot, "development-profile-registry.json");
const defaultSourcesPath = resolve(packageRoot, "sources.json");
const defaultOutputRoot = resolve(packageRoot, "generated");
const compilerPath = fileURLToPath(import.meta.url);
const profileHandle = "cal-ontology-runtime-integration-explicit-v0.1";

function sha256Bytes(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256Bytes(readFileSync(path));
}

function readJson(path: string): JsonRecord {
  return JSON.parse(readFileSync(path, "utf8")) as JsonRecord;
}

function pretty(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function assertEqual(left: string, right: string, code: string): void {
  if (left !== right) throw new Error(code);
}

function parseArgs(): { outputRoot: string; sourcesPath: string } {
  let outputRoot = defaultOutputRoot;
  let sourcesPath = defaultSourcesPath;
  for (let index = 2; index < process.argv.length; index += 1) {
    const argument = process.argv[index];
    if (argument === "--output-root") outputRoot = resolve(process.argv[++index]!);
    else if (argument === "--sources-path") sourcesPath = resolve(process.argv[++index]!);
    else throw new Error(`UNKNOWN_ARGUMENT:${argument}`);
  }
  return { outputRoot, sourcesPath };
}

function verifySelectedSources(sourcesPath: string): SourceRecord[] {
  const sourceManifest = readJson(sourcesPath);
  if (sourceManifest.schema_version !== "cal-d65-s5-source-manifest/v1") {
    throw new Error("SOURCE_MANIFEST_VERSION_INVALID");
  }
  const records = sourceManifest.records as SourceRecord[];
  for (const record of records) {
    let observed: string;
    try {
      observed = sha256File(record.path);
    } catch {
      throw new Error(`SELECTED_SOURCE_MISSING:${record.source_id}`);
    }
    if (observed !== record.sha256) {
      throw new Error(`SELECTED_SOURCE_DIGEST_DRIFT:${record.source_id}`);
    }
  }
  return records;
}

function buildSystemOntology(
  graph: JsonRecord,
  sourceManifest: JsonRecord,
  eventContract: JsonRecord,
  decision: JsonRecord,
  selectedSources: SourceRecord[],
  hashes: JsonRecord,
): JsonRecord {
  const eventsByType = new Map(
    (eventContract.events as JsonRecord[]).map((event) => [event.eventType, event]),
  );
  const streamsById = new Map(
    (eventContract.streams as JsonRecord[]).map((stream) => [stream.streamId, stream]),
  );
  const projectionContracts = (eventContract.projections as JsonRecord[]).map(
    (projection) => ({
      ...projection,
      resolvedInputs: (projection.consumes as string[]).map((eventType) => {
        const event = eventsByType.get(eventType)!;
        const stream = streamsById.get(event.streamId)!;
        return {
          eventType,
          streamId: event.streamId,
          subjectKind: stream.subjectKind,
          streamFamily: stream.streamFamily,
          stateSemantics: event.stateSemantics,
        };
      }),
    }),
  );
  const subjectKinds = [...new Set(
    (eventContract.streams as JsonRecord[]).map((stream) => stream.subjectKind as string),
  )].sort();
  const subjectCalculations = subjectKinds.map((subjectKind) => {
    const streams = (eventContract.streams as JsonRecord[])
      .filter((stream) => stream.subjectKind === subjectKind)
      .map((stream) => ({
        streamId: stream.streamId,
        streamFamily: stream.streamFamily,
        eventTypes: stream.eventTypes,
      }));
    const eventTypes = new Set(streams.flatMap((stream) => stream.eventTypes as string[]));
    return {
      subjectKind,
      identityRule: "subject-kind-and-id",
      canonicalStateSource: "ordered-complete-resulting-state-events",
      streams,
      calculatedBy: projectionContracts
        .filter((projection) =>
          (projection.consumes as string[]).some((eventType) => eventTypes.has(eventType)),
        )
        .map((projection) => projection.projectionId),
    };
  });

  return {
    schema_version: "cal.d65-system-runtime-ontology/v1",
    ontology_id: "cal.ontology-runtime-integration.system-runtime.epoch-001",
    authority: "generated-system-runtime-read-model",
    status: "candidate-unadmitted",
    source: {
      domainspec_package_id: "cal-ontology-runtime-integration-domainspec-source-epoch-001",
      admission_decision_id: decision.decision_id,
      admission_option_id: decision.selection.option_id,
      graph_sha256: hashes.graph,
      source_manifest_sha256: hashes.sourceManifest,
      event_contract_sha256: hashes.eventContract,
      source_set_digest: graph.source_set_digest,
      compiler_sha256: sha256File(compilerPath),
      selected_sources: selectedSources.map((record) => ({
        source_id: record.source_id,
        sha256: record.sha256,
        role: record.role,
      })),
    },
    semantic_graph: {
      schema_version: graph.schema_version,
      authority: graph.authority,
      project_id: graph.project_id,
      language: graph.language,
      source_set_digest: graph.source_set_digest,
      nodes: graph.nodes,
      edges: graph.edges,
      provenance_record_count: sourceManifest.records.length,
    },
    event_calculus: {
      contract: eventContract,
      subject_calculations: subjectCalculations,
      projection_contracts: projectionContracts,
      canonical_truth_rule: "Per-subject ordered event history is canonical; snapshots, projections, compiled graph, and this system ontology are rebuildable derived evidence.",
      consistent_cut_rule: eventContract.ordering.global,
    },
    claim_ceiling: "Generated candidate projection only; no ontology admission, implementation binding, runtime conformance, migration, publication, deployment, or external effect.",
  };
}

function compile(outputRoot: string, sourcesPath: string): JsonRecord {
  const selectedSources = verifySelectedSources(sourcesPath);
  const decisionRecord = selectedSources.find(
    (record) => record.source_id === "SRC-CAL-D65-S4-ADMISSION",
  );
  if (!decisionRecord) throw new Error("SOURCE_ADMISSION_RECORD_MISSING");
  const decision = readJson(decisionRecord.path);
  if (
    decision.decision_id !== "CAL-D65SRC-0019" ||
    decision.selection?.option_id !== "D65SRC-1" ||
    decision.next_gate !== "G-D65-COMPILE"
  ) {
    throw new Error("SOURCE_ADMISSION_INVALID");
  }

  const mintedA = compileMintedProject(mintedRoot, {
    developmentProfileRegistry: { path: registryPath, handle: profileHandle },
  });
  const mintedB = compileMintedProject(mintedRoot, {
    developmentProfileRegistry: { path: registryPath, handle: profileHandle },
  });
  assertEqual(mintedA.graphBytes, mintedB.graphBytes, "GRAPH_NONDETERMINISTIC");
  assertEqual(
    mintedA.sourceManifestBytes,
    mintedB.sourceManifestBytes,
    "SOURCE_MANIFEST_NONDETERMINISTIC",
  );

  const eventSource = readJson(
    resolve(sourcePackageRoot, "contracts/event-sourcing-source.json"),
  ) as unknown as EventSourcingContractSource;
  const eventA = canonicalizeCompiledEventSourcingContract(
    compileEventSourcingContract(eventSource),
  );
  const eventB = canonicalizeCompiledEventSourcingContract(
    compileEventSourcingContract(eventSource),
  );
  assertEqual(eventA, eventB, "EVENT_CONTRACT_NONDETERMINISTIC");
  const eventContract = JSON.parse(eventA) as JsonRecord;
  const hashes = {
    graph: sha256Bytes(mintedA.graphBytes),
    sourceManifest: sha256Bytes(mintedA.sourceManifestBytes),
    eventContract: sha256Bytes(eventA),
  };
  const systemA = pretty(
    buildSystemOntology(
      mintedA.graph,
      mintedA.sourceManifest,
      eventContract,
      decision,
      selectedSources,
      hashes,
    ),
  );
  const systemB = pretty(
    buildSystemOntology(
      mintedB.graph,
      mintedB.sourceManifest,
      JSON.parse(eventB),
      decision,
      selectedSources,
      hashes,
    ),
  );
  assertEqual(systemA, systemB, "SYSTEM_ONTOLOGY_NONDETERMINISTIC");

  const outputs: Record<string, string> = {
    "graph.json": mintedA.graphBytes,
    "source-manifest.json": mintedA.sourceManifestBytes,
    "event-sourcing-contract.json": eventA,
    "system-ontology.json": systemA,
  };
  const receipt = {
    schema_version: "cal-d65-s5-compile-receipt/v1",
    result: "PASS",
    source_set_digest: mintedA.graph.source_set_digest,
    deterministic_internal_double_compile: true,
    counts: {
      graph_nodes: mintedA.graph.nodes.length,
      graph_edges: mintedA.graph.edges.length,
      source_records: mintedA.sourceManifest.records.length,
      streams: eventContract.streams.length,
      events: eventContract.events.length,
      projections: eventContract.projections.length,
      joins: eventContract.joins.length,
      runtime_obligations: eventContract.runtimeObligations.length,
    },
    outputs: Object.fromEntries(
      Object.entries(outputs).map(([path, bytes]) => [path, sha256Bytes(bytes)]),
    ),
    compiler_sha256: sha256File(compilerPath),
    implementation_binding_present: false,
    claim_ceiling: "PASS proves deterministic candidate materialization only and grants no system-ontology admission or successor authority.",
  };
  outputs["compile-receipt.json"] = pretty(receipt);
  mkdirSync(outputRoot, { recursive: true });
  for (const [path, bytes] of Object.entries(outputs)) {
    writeFileSync(resolve(outputRoot, path), bytes);
  }
  return receipt;
}

try {
  const { outputRoot, sourcesPath } = parseArgs();
  process.stdout.write(pretty(compile(outputRoot, sourcesPath)));
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${JSON.stringify({ result: "BLOCK", error: message })}\n`);
  process.exitCode = 1;
}
