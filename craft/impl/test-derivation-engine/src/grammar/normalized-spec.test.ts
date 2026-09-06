import { describe, expect, it } from "vitest";
import {
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { BindingSet } from "../bindings/index.js";
import { computeProvenance } from "../provenance/index.js";
import { derive } from "../rules/index.js";
import {
  buildResidueReceipt,
  renderResidueReceipt,
} from "../residue/receipt.js";
import { parse } from "./index.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AEO_DIR = resolve(
  __dirname,
  "../../../spec/features/agent-execution-orchestrator",
);

describe("normalized SPEC.md adapter", () => {
  const parsed = parse(AEO_DIR);
  const byType = (type: string) =>
    parsed.graph.nodes.filter((node) => node.type === type);

  it("parses the newest AEO pack without guessing behavioral semantics", () => {
    expect(parsed.violations).toEqual([]);
    expect(byType("SpecConcept")).toHaveLength(13);
    expect(byType("SpecRelationship")).toHaveLength(9);
    expect(byType("SpecField")).toHaveLength(6);
    expect(byType("SpecAttribute")).toHaveLength(11);
    expect(byType("SpecOmission")).toHaveLength(3);
    expect(parsed.graph.nodes).toHaveLength(42);
  });

  it("derives a non-vacuous structural obligation set", () => {
    const obligations = derive(parsed.graph);
    expect(obligations).toHaveLength(39);
    expect(new Set(obligations.map((o) => o.rule_type))).toEqual(
      new Set([
        "spec-concept",
        "spec-relationship",
        "spec-field",
        "spec-attribute",
      ]),
    );
  });

  it("is deterministic across independent parses", () => {
    expect(parse(AEO_DIR)).toEqual(parse(AEO_DIR));
    expect(derive(parse(AEO_DIR).graph)).toEqual(
      derive(parse(AEO_DIR).graph),
    );
  });

  it("fails closed when required normalized tables or endpoints are missing", () => {
    const emptyDir = mkdtempSync(join(tmpdir(), "domainspec-normalized-empty-"));
    const invalidEdgeDir = mkdtempSync(
      join(tmpdir(), "domainspec-normalized-invalid-edge-"),
    );
    try {
      writeFileSync(join(emptyDir, "SPEC.md"), "# Empty normalized pack\n", "utf8");
      expect(parse(emptyDir).violations).toEqual([
        "SPEC.md: normalized dialect requires a Concept Registry table",
        "SPEC.md: normalized dialect requires a Feature Concept Graph table",
      ]);

      writeFileSync(
        join(invalidEdgeDir, "SPEC.md"),
        [
          "# Invalid endpoint pack",
          "",
          "## Concept Registry",
          "",
          "| Concept | Type |",
          "| --- | --- |",
          "| Known | Entity |",
          "",
          "## Feature Concept Graph",
          "",
          "| From | Edge | To | Source Evidence |",
          "| --- | --- | --- | --- |",
          "| Known | contains | Missing | source `domain.md#known` |",
          "",
        ].join("\n"),
        "utf8",
      );
      expect(parse(invalidEdgeDir).violations).toEqual([
        "SPEC.md: Feature Concept Graph row 0 references an undeclared concept (Known --contains--> Missing)",
      ]);
    } finally {
      rmSync(emptyDir, { recursive: true, force: true });
      rmSync(invalidEdgeDir, { recursive: true, force: true });
    }
  });

  it("adding one supported field preserves old obligations and adds exactly one", () => {
    const dir = mkdtempSync(join(tmpdir(), "domainspec-normalized-refinement-"));
    try {
      const original = readFileSync(join(AEO_DIR, "SPEC.md"), "utf8");
      const marker =
        "| selectedStages | string[] | yes |  | selected lifecycle stages |";
      const refined = original.replace(
        marker,
        `${marker}\n| retryBudget | number | yes |  | bounded route retries |`,
      );
      expect(refined).not.toBe(original);
      writeFileSync(join(dir, "SPEC.md"), refined, "utf8");

      const coarse = derive(parse(AEO_DIR).graph);
      const fine = derive(parse(dir).graph);
      const fineKeys = new Set(fine.map((o) => o.obligation_key));

      expect(fine).toHaveLength(coarse.length + 1);
      for (const obligation of coarse) {
        expect(fineKeys.has(obligation.obligation_key)).toBe(true);
      }
      expect(
        fine.some(
          (o) =>
            o.rule_type === "spec-field" &&
            o.canonical_params.field === "retryBudget",
        ),
      ).toBe(true);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("accounts separately for target, preserved, omitted, and binding-added data", () => {
    const bindings: BindingSet = {
      feature: "agent-execution-orchestrator",
      emit_dir: "private/generated",
      test_file: "aeo.derived.test.ts",
      bindings: [
        {
          match: { rule_type: "spec-field", field: "templateId" },
          module: "../domain/route-template.js",
          symbol: "validateRouteTemplate",
          strategy: "property",
          kind: "route-template-validator",
        },
      ],
    };
    const receipt = buildResidueReceipt(
      "agent-execution-orchestrator",
      parsed.graph,
      parsed.violations,
      bindings,
    );

    expect(receipt.input_dialect).toBe("normalized-spec");
    expect(receipt.summary).toEqual({
      target_declarations: 39,
      preserved_source_rows: 9,
      omitted_source_rows: 3,
      parser_rejections: 0,
      binding_added_commitments: 1,
    });
    expect(receipt.omitted_source_rows.map((row) => row.fields.declaration)).toContain(
      "AssemblePipelineRoute --enforces--> StageContract",
    );
    expect(receipt.binding_added_commitments[0]?.symbol).toBe(
      "validateRouteTemplate",
    );
    expect(renderResidueReceipt(receipt)).toBe(renderResidueReceipt(receipt));
  });

  it("hashes normalized SPEC.md as the sole provenance input", () => {
    const provenance = computeProvenance(AEO_DIR, "test-commit");
    expect(provenance.engineCommit).toBe("test-commit");
    expect(provenance.inputs).toHaveLength(1);
    expect(provenance.inputs[0]?.file).toBe("SPEC.md");
    expect(provenance.inputs[0]?.sha256).toMatch(/^[0-9a-f]{64}$/);
  });
});
