// Machine-readable accounting at the normalized-spec boundary.
//
// This receipt is intentionally structural. It records what the normalized
// target declares, which source rows the target explicitly says it omitted,
// parser rejections, and which commitments a binding sidecar adds. It does not
// claim semantic satisfiability or application-implementation generation.

import type { BindingSet } from "../bindings/index.js";
import type { ConceptGraph, Node, Value } from "../ir/types.js";

export interface ReceiptDeclaration {
  readonly kind: Node["type"];
  readonly source_anchor: string;
  readonly fields: Readonly<Record<string, Value>>;
}

export interface BindingCommitment {
  readonly match: Readonly<Record<string, string>>;
  readonly module: string;
  readonly symbol: string;
  readonly strategy: string;
  readonly kind: string;
  readonly result_field: string | null;
  readonly decision_field: string | null;
  readonly emit_dir: string;
  readonly test_file: string;
  readonly has_fixture: boolean;
}

export interface ResidueReceipt {
  readonly format_version: 1;
  readonly feature: string;
  readonly input_dialect: "normalized-spec" | "aspect-documents" | "empty";
  /** Every declaration present in the parsed target dialect. */
  readonly target_declarations: readonly ReceiptDeclaration[];
  /** Normalized graph rows that carry an explicit source-evidence pointer. */
  readonly preserved_source_rows: readonly ReceiptDeclaration[];
  /** Source rows the normalized target explicitly documents as absent. */
  readonly omitted_source_rows: readonly ReceiptDeclaration[];
  /** Non-canonical input structures rejected by the parser. */
  readonly parser_rejections: readonly string[];
  /** Choices supplied by a binding sidecar rather than by normalized SPEC.md. */
  readonly binding_added_commitments: readonly BindingCommitment[];
  readonly summary: {
    readonly target_declarations: number;
    readonly preserved_source_rows: number;
    readonly omitted_source_rows: number;
    readonly parser_rejections: number;
    readonly binding_added_commitments: number;
  };
}

const normalizedTypes = new Set<Node["type"]>([
  "SpecConcept",
  "SpecRelationship",
  "SpecField",
  "SpecAttribute",
]);

function declaration(node: Node): ReceiptDeclaration {
  return {
    kind: node.type,
    source_anchor: node.source_anchor,
    fields: node.fields,
  };
}

export function buildResidueReceipt(
  feature: string,
  graph: ConceptGraph,
  violations: readonly string[],
  bindings: BindingSet | null = null,
): ResidueReceipt {
  const normalized = graph.nodes.filter((node) => normalizedTypes.has(node.type));
  const aspect = graph.nodes.filter(
    (node) => !normalizedTypes.has(node.type) && node.type !== "SpecOmission",
  );
  const inputDialect =
    normalized.length > 0
      ? "normalized-spec"
      : aspect.length > 0
        ? "aspect-documents"
        : "empty";

  const targetDeclarations = (normalized.length > 0 ? normalized : aspect).map(
    declaration,
  );
  const preservedSourceRows = normalized
    .filter(
      (node) =>
        node.type === "SpecRelationship" &&
        String(node.fields.source_evidence ?? "").trim() !== "",
    )
    .map(declaration);
  const omittedSourceRows = graph.nodes
    .filter((node) => node.type === "SpecOmission")
    .map(declaration);
  const bindingAddedCommitments = (bindings?.bindings ?? [])
    .map((binding): BindingCommitment => ({
      match: binding.match,
      module: binding.module,
      symbol: binding.symbol,
      strategy: binding.strategy,
      kind: binding.kind,
      result_field: binding.result_field ?? null,
      decision_field: binding.decision_field ?? null,
      emit_dir: bindings?.emit_dir ?? "",
      test_file: bindings?.test_file ?? "",
      has_fixture: binding.fixture !== undefined,
    }))
    .sort((a, b) => {
      const ka = `${a.module}|${a.symbol}|${a.strategy}|${JSON.stringify(a.match)}`;
      const kb = `${b.module}|${b.symbol}|${b.strategy}|${JSON.stringify(b.match)}`;
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });

  return {
    format_version: 1,
    feature,
    input_dialect: inputDialect,
    target_declarations: targetDeclarations,
    preserved_source_rows: preservedSourceRows,
    omitted_source_rows: omittedSourceRows,
    parser_rejections: [...violations].sort(),
    binding_added_commitments: bindingAddedCommitments,
    summary: {
      target_declarations: targetDeclarations.length,
      preserved_source_rows: preservedSourceRows.length,
      omitted_source_rows: omittedSourceRows.length,
      parser_rejections: violations.length,
      binding_added_commitments: bindingAddedCommitments.length,
    },
  };
}

export function renderResidueReceipt(receipt: ResidueReceipt): string {
  return `${JSON.stringify(receipt, null, 2)}\n`;
}
