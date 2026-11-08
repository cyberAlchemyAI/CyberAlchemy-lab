import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { compileDevelopmentProject } from "./development-engine.js";
import { createCompleteDevelopmentProject } from "./development-fixture.js";
import {
  CATALOGUE_IDS,
  collectDevelopmentInstanceConformance,
  compareDevelopmentCatalogues,
  createDevelopmentSpecCatalogues,
  deriveDevelopmentCatalogues,
  replayDevelopmentCore,
  runDevelopmentCore,
} from "./proof-engine.js";

describe("BTE development proof core", () => {
  it("executes and replays all six exact catalogues", () => {
    const project = createCompleteDevelopmentProject();
    const build = compileDevelopmentProject(project);
    const core = runDevelopmentCore(project, build);
    expect(core.aggregate.required_catalogues).toEqual(CATALOGUE_IDS);
    expect(core.catalogueRuns).toHaveLength(6);
    expect(
      Object.fromEntries(
        core.catalogueRuns.map(({ catalogue }) => [
          catalogue.catalogue_id,
          catalogue.members.length,
        ]),
      ),
    ).toEqual({
      "formation-criterion@1": 16,
      "formation-structure@1": 13,
      "node-kind-causality@1": 13,
      "node-instance-conformance@1": 15,
      "relationship-family-causality@1": 17,
      "edge-instance-conformance@1": 17,
    });
    expect(core.aggregate.total_coverage_count).toBe(91);
    expect(
      core.catalogueRuns.every(
        (run) =>
          run.tests.length === run.executions.length &&
          run.executions.length === run.mutations.length &&
          run.executions.every(({ status }) => status === "pass") &&
          run.mutations.every(({ killed }) => killed),
      ),
    ).toBe(true);
    expect(replayDevelopmentCore(project, build, core)).toEqual({
      result: "pass",
      codes: [],
    });
  });

  it("detects missing, extra, and duplicate catalogue members before TestCase materialization", () => {
    const project = createCompleteDevelopmentProject();
    const build = compileDevelopmentProject(project);
    const expected = createDevelopmentSpecCatalogues(project)[0]!;
    const generated = structuredClone(deriveDevelopmentCatalogues(build)[0]!);

    generated.members.pop();
    expect(compareDevelopmentCatalogues(expected, generated)).toEqual(
      expect.objectContaining({
        result: "fail",
        missing: [expected.members.at(-1)!.coverage_key],
      }),
    );

    const extra = structuredClone(expected);
    extra.members.push({
      ...extra.members[0]!,
      obligation_id: "unexpected",
      coverage_key: `${extra.catalogue_id}::unexpected`,
    });
    expect(compareDevelopmentCatalogues(expected, extra)).toEqual(
      expect.objectContaining({
        result: "fail",
        extra: [`${extra.catalogue_id}::unexpected`],
      }),
    );

    const duplicate = structuredClone(expected);
    duplicate.members.push(structuredClone(duplicate.members[0]!));
    expect(compareDevelopmentCatalogues(expected, duplicate)).toEqual(
      expect.objectContaining({
        result: "fail",
        duplicate: [duplicate.members[0]!.coverage_key],
      }),
    );
  });

  it("rejects a shared expectation/generator oracle", () => {
    const project = createCompleteDevelopmentProject();
    const expected = createDevelopmentSpecCatalogues(project)[0]!;
    const sharedOracle = structuredClone(expected);

    expect(compareDevelopmentCatalogues(expected, sharedOracle)).toEqual({
      result: "fail",
      diagnostic: "BTE_EXPECTATION_NOT_INDEPENDENT",
      missing: [],
      extra: [],
      duplicate: [],
    });

    const expectationSource = readFileSync(
      new URL("./self-authored-expectations.ts", import.meta.url),
      "utf8",
    );
    expect(expectationSource).not.toMatch(
      /buildCatalogues|deriveDevelopmentCatalogues/,
    );
  });

  it("keeps TestCase, ExecutionResult, MutationResult, ProofReceipt, and ReplayResult distinct", () => {
    const project = createCompleteDevelopmentProject();
    const build = compileDevelopmentProject(project);
    const run = runDevelopmentCore(project, build).catalogueRuns[0]!;
    expect(run.tests[0]!.schema_version).toBe("bte-development-test-case/v1");
    expect(run.executions[0]!.schema_version).toBe(
      "bte-development-execution-result/v1",
    );
    expect(run.mutations[0]!.schema_version).toBe(
      "bte-development-mutation-result/v1",
    );
    expect(run.proofReceipt.schema_version).toBe(
      "bte-development-proof-receipt/v1",
    );
    expect(run.replayResult.schema_version).toBe(
      "bte-development-replay-result/v1",
    );
    expect(run.proofReceipt.admission).toBe("development-only");
  });

  it("materializes every node and edge case when independent siblings are red", () => {
    const project = createCompleteDevelopmentProject();
    project.nodes.find(({ node_id }) => node_id === "core.Account")!.body = {
      fields: [{ name: "account_id", type: 7, identity: "yes" }],
    };
    project.edges.find(({ edge_id }) => edge_id === "edge-performs")!.to =
      "core.AccountChanged";

    const run = collectDevelopmentInstanceConformance(project);
    expect(run.result).toBe("fail");
    expect(run.cases).toHaveLength(project.nodes.length + project.edges.length);

    const nodeCase = run.cases.find(
      ({ test }) => test.coverage_key ===
        "node-instance-conformance@1::core.Account",
    )!;
    expect(nodeCase.execution).toEqual(
      expect.objectContaining({
        status: "fail",
        code: "BTE_PROOF_SUBJECT_INVALID",
      }),
    );
    expect(nodeCase.diagnostics.map(({ code }) => code)).toContain(
      "BTE_DEV_FORMATION_INVALID",
    );

    const edgeCase = run.cases.find(
      ({ test }) => test.coverage_key ===
        "edge-instance-conformance@1::edge-performs",
    )!;
    expect(edgeCase.execution).toEqual(
      expect.objectContaining({
        status: "fail",
        code: "BTE_PROOF_SUBJECT_INVALID",
      }),
    );
    expect(edgeCase.diagnostics.map(({ code }) => code)).toContain(
      "BTE_DEV_EDGE_ENDPOINT_KIND",
    );

    expect(
      run.cases.find(
        ({ test }) =>
          test.coverage_key ===
          "node-instance-conformance@1::core.Money",
      )!.execution.status,
    ).toBe("pass");
    expect(
      run.cases.find(
        ({ test }) =>
          test.coverage_key ===
          "edge-instance-conformance@1::edge-produces",
      )!.execution.status,
    ).toBe("pass");
  });

  it("rejects one-unit-as-breadth and replay tampering", () => {
    const project = createCompleteDevelopmentProject();
    const build = compileDevelopmentProject(project);
    const core = runDevelopmentCore(project, build);
    const tampered = structuredClone(core);
    tampered.aggregate.total_coverage_count = 1;
    tampered.aggregateBytes = `${JSON.stringify(tampered.aggregate)}\n`;
    expect(replayDevelopmentCore(project, build, tampered)).toEqual({
      result: "fail",
      codes: ["BTE_PROOF_REPLAY_MISMATCH"],
    });
  });
});
