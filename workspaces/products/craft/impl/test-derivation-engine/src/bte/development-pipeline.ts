import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalize } from "./contract-publication.js";
import {
  composeDevelopmentTerminal,
  replayDevelopmentConsumers,
  replayDevelopmentTerminal,
  runDevelopmentConsumers,
  type DevelopmentConsumers,
  type DevelopmentTerminalRun,
} from "./consumer-engine.js";
import {
  compileDevelopmentProject,
  replayDevelopmentBuild,
  type DevelopmentBuild,
  type DevelopmentProject,
} from "./development-engine.js";
import { createCompleteDevelopmentProject } from "./development-fixture.js";
import {
  replayDevelopmentCore,
  runDevelopmentCore,
  type DevelopmentCoreRun,
} from "./proof-engine.js";
import { sha256 } from "./validation/validate-semantics.js";

export type DevelopmentBteSummary = {
  schema_version: "bte-development-summary/v1";
  project_id: string;
  profile_id: string;
  kind_count: number;
  relationship_count: number;
  catalogue_count: number;
  coverage_count: number;
  consumer_count: number;
  build_sha256: string;
  core_sha256: string;
  consumers_sha256: string;
  terminal_sha256: string;
  result: "pass";
  admission: "development-only";
};

export type DevelopmentBteRun = {
  build: DevelopmentBuild;
  core: DevelopmentCoreRun;
  consumers: DevelopmentConsumers;
  terminal: DevelopmentTerminalRun;
  summary: DevelopmentBteSummary;
  summaryBytes: string;
};

function bytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

function assertReplay(
  stage: string,
  replay: { result: "pass" | "fail"; codes: readonly string[] },
): void {
  if (replay.result !== "pass") {
    throw new Error(`${stage}:${replay.codes.join(",")}`);
  }
}

export function runDevelopmentBte(
  project: DevelopmentProject,
): DevelopmentBteRun {
  const build = compileDevelopmentProject(project);
  assertReplay("build-replay", replayDevelopmentBuild(project, build));

  const core = runDevelopmentCore(project, build);
  assertReplay("core-replay", replayDevelopmentCore(project, build, core));

  const consumers = runDevelopmentConsumers(build, core);
  assertReplay(
    "consumer-replay",
    replayDevelopmentConsumers(build, core, consumers),
  );

  const terminal = composeDevelopmentTerminal(core, consumers);
  assertReplay(
    "terminal-replay",
    replayDevelopmentTerminal(core, consumers, terminal),
  );

  const summary: DevelopmentBteSummary = {
    schema_version: "bte-development-summary/v1",
    project_id: project.project_id,
    profile_id: project.profile_id,
    kind_count: build.receipt.kind_set.length,
    relationship_count: build.receipt.relationship_set.length,
    catalogue_count: core.catalogueRuns.length,
    coverage_count: core.aggregate.total_coverage_count,
    consumer_count: consumers.replays.length,
    build_sha256: sha256(build.receiptBytes),
    core_sha256: sha256(core.aggregateBytes),
    consumers_sha256: sha256(consumers.aggregateBytes),
    terminal_sha256: sha256(terminal.aggregateBytes),
    result: "pass",
    admission: "development-only",
  };
  return {
    build,
    core,
    consumers,
    terminal,
    summary,
    summaryBytes: bytes(summary),
  };
}

export function runCompleteDevelopmentBte(): DevelopmentBteRun {
  return runDevelopmentBte(createCompleteDevelopmentProject());
}

const thisFile = fileURLToPath(import.meta.url);
if (process.argv[1] && resolve(process.argv[1]) === thisFile) {
  process.stdout.write(runCompleteDevelopmentBte().summaryBytes);
}
