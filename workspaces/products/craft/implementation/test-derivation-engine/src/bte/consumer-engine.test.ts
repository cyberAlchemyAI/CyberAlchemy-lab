import { describe, expect, it } from "vitest";

import {
  composeDevelopmentTerminal,
  replayDevelopmentConsumer,
  replayDevelopmentConsumers,
  replayDevelopmentTerminal,
  runBodyWarDevelopmentConsumer,
  runDevelopmentConsumers,
  runIolmDevelopmentConsumer,
} from "./consumer-engine.js";
import { compileDevelopmentProject } from "./development-engine.js";
import { createCompleteDevelopmentProject } from "./development-fixture.js";
import { runDevelopmentCore } from "./proof-engine.js";

function completeRun() {
  const project = createCompleteDevelopmentProject();
  const build = compileDevelopmentProject(project);
  const core = runDevelopmentCore(project, build);
  return { project, build, core };
}

describe("BTE development consumers and terminal aggregate", () => {
  it("replays IOLM graph, hierarchy, and table GET parity", () => {
    const { build, core } = completeRun();
    const run = runIolmDevelopmentConsumer(build, core);
    expect(replayDevelopmentConsumer(build, core, run)).toEqual(
      expect.objectContaining({
        consumer_id: "iolm-development-adapter@1",
        result: "pass",
        checks: expect.arrayContaining([
          "graph-hierarchy-table-get-parity",
        ]),
      }),
    );
  });

  it("replays Body War's exact read-only redacted projection", () => {
    const { build, core } = completeRun();
    const run = runBodyWarDevelopmentConsumer(build, core);
    expect(JSON.stringify(run.evidence)).not.toMatch(
      /"body"|"intent"|"fields"|"states"/,
    );
    expect(replayDevelopmentConsumer(build, core, run)).toEqual(
      expect.objectContaining({
        consumer_id: "body-war-development-adapter@1",
        result: "pass",
        checks: expect.arrayContaining(["allowlisted-redaction"]),
      }),
    );
  });

  it("composes and independently replays exact consumer and terminal sets", () => {
    const { build, core } = completeRun();
    const consumers = runDevelopmentConsumers(build, core);
    const terminal = composeDevelopmentTerminal(core, consumers);
    expect(consumers.replays).toHaveLength(2);
    expect(replayDevelopmentConsumers(build, core, consumers)).toEqual({
      result: "pass",
      codes: [],
    });
    expect(replayDevelopmentTerminal(core, consumers, terminal)).toEqual({
      result: "pass",
      codes: [],
    });
    expect(terminal.aggregate.admission).toBe("development-only");
  });

  it("rejects IOLM parity drift", () => {
    const { build, core } = completeRun();
    const run = runIolmDevelopmentConsumer(build, core);
    if (run.evidence.consumer_id !== "iolm-development-adapter@1") {
      throw new Error("unexpected fixture");
    }
    run.evidence.projections.table.node_ids.pop();
    run.evidenceBytes = `${JSON.stringify(run.evidence)}\n`;
    expect(() => replayDevelopmentConsumer(build, core, run)).toThrowError(
      /BTE_CONSUMER_EVIDENCE_TAMPERED|BTE_CONSUMER_IOLM_PARITY/,
    );
  });

  it("rejects Body War projection leaks", () => {
    const { build, core } = completeRun();
    const run = runBodyWarDevelopmentConsumer(build, core);
    if (run.evidence.consumer_id !== "body-war-development-adapter@1") {
      throw new Error("unexpected fixture");
    }
    const leaking = run.evidence.projection.nodes[0]! as Record<string, unknown>;
    leaking.intent = "must not cross the boundary";
    expect(() => replayDevelopmentConsumer(build, core, run)).toThrowError(
      /BTE_CONSUMER_EVIDENCE_TAMPERED|BTE_CONSUMER_BODY_WAR_REDACTION/,
    );
  });

  it("rejects stale cores, missing consumers, and terminal tampering", () => {
    const { build, core } = completeRun();
    const staleRun = runIolmDevelopmentConsumer(build, core);
    staleRun.evidence.core_sha256 = "0".repeat(64);
    expect(() =>
      replayDevelopmentConsumer(build, core, staleRun),
    ).toThrowError(/BTE_CONSUMER_CORE_MISMATCH/);

    const consumers = runDevelopmentConsumers(build, core);
    const incomplete = structuredClone(consumers);
    incomplete.replays.pop();
    expect(replayDevelopmentConsumers(build, core, incomplete)).toEqual({
      result: "fail",
      codes: ["BTE_CONSUMER_REPLAY_MISMATCH"],
    });

    const terminal = composeDevelopmentTerminal(core, consumers);
    terminal.aggregate.consumer_aggregate_sha256 = "f".repeat(64);
    expect(replayDevelopmentTerminal(core, consumers, terminal)).toEqual({
      result: "fail",
      codes: ["BTE_TERMINAL_AGGREGATE_MISMATCH"],
    });
  });
});
