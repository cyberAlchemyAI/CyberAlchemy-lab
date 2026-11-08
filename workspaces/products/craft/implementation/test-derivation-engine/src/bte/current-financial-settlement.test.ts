import { describe, expect, it } from "vitest";

import { createCurrentFinancialSettlementDevelopmentProject } from "./current-financial-settlement.js";
import {
  collectDevelopmentProjectDiagnostics,
  type DevelopmentProject,
} from "./development-engine.js";
import { runDevelopmentBte } from "./development-pipeline.js";
import { collectDevelopmentInstanceConformance } from "./proof-engine.js";

describe("BTE current authored financial-settlement structural slice", () => {
  it("binds the exact minted source, generated graph, and all nine manifest records", () => {
    const project = createCurrentFinancialSettlementDevelopmentProject();
    expect(project.project_id).toBe("financial-settlement");
    expect(project.coverage_mode).toBe("declared-subset");
    expect(project.nodes).toHaveLength(5);
    expect(project.edges).toHaveLength(4);
    expect(new Set(project.nodes.map(({ kind }) => kind))).toEqual(
      new Set(["Calculation", "Operation", "Rule", "Event"]),
    );
    expect(new Set(project.edges.map(({ family }) => family))).toEqual(
      new Set(["calculates", "produces", "enforces"]),
    );
    expect(
      [...project.nodes, ...project.edges].every(({ source_anchor }) =>
        /^nodes\/[^@]+\.json@[0-9a-f]{64}#(node|edge):financial-settlement\./.test(
          source_anchor ?? "",
        ),
      ),
    ).toBe(true);
    expect(collectDevelopmentProjectDiagnostics(project)).toEqual({
      result: "pass",
      diagnostics: [],
    });
  });

  it("derives and executes the exact current structural case catalogue", () => {
    const project = createCurrentFinancialSettlementDevelopmentProject();
    const run = runDevelopmentBte(project);
    expect(run.summary).toMatchObject({
      kind_count: 4,
      relationship_count: 3,
      catalogue_count: 6,
      result: "pass",
      admission: "development-only",
    });
    expect(
      Object.fromEntries(
        run.core.catalogueRuns.map(({ catalogue }) => [
          catalogue.catalogue_id,
          catalogue.members.length,
        ]),
      ),
    ).toEqual({
      "formation-criterion@1": 4,
      "formation-structure@1": 4,
      "node-kind-causality@1": 4,
      "node-instance-conformance@1": 5,
      "relationship-family-causality@1": 3,
      "edge-instance-conformance@1": 4,
    });
    expect(run.summary.coverage_count).toBe(24);
    expect(run.core.catalogueRuns.flatMap(({ executions }) => executions)).toHaveLength(24);
    expect(
      run.core.catalogueRuns.every(({ executions, mutations }) =>
        executions.every(({ status }) => status === "pass") &&
        mutations.every(({ killed }) => killed),
      ),
    ).toBe(true);

    const instances = collectDevelopmentInstanceConformance(project);
    expect(instances.cases).toHaveLength(9);
    expect(instances.result).toBe("pass");
  });

  it("rejects an enforces Rule to Event endpoint at its source-anchored edge", () => {
    const project: DevelopmentProject = structuredClone(
      createCurrentFinancialSettlementDevelopmentProject(),
    );
    const edge = project.edges.find(
      ({ edge_id }) => edge_id ===
        "financial-settlement.edge.no-duplicate-makeup-rule-enforces-generation",
    )!;
    edge.to = "financial-settlement.PayoutCreatedEvent";
    const result = collectDevelopmentProjectDiagnostics(project);
    expect(result.result).toBe("fail");
    expect(result.diagnostics).toContainEqual(
      expect.objectContaining({
        code: "BTE_DEV_EDGE_ENDPOINT_KIND",
        subject: edge.edge_id,
        source_anchor: edge.source_anchor,
      }),
    );
    const cases = collectDevelopmentInstanceConformance(project);
    expect(cases.cases).toHaveLength(9);
    expect(
      cases.cases.find(({ test }) => test.subject_id === edge.edge_id)?.execution.code,
    ).toBe("BTE_PROOF_SUBJECT_INVALID");
  });
});
