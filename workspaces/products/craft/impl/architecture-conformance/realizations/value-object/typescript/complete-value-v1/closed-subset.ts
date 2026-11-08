import {createHash} from "node:crypto";
import ts from "typescript";

export type TypeScriptValueObjectClosedSubsetProofV1 = Readonly<{
  schema_version: "TypeScriptValueObjectClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  exports: readonly ["createSettlementValueFactory", "settlementValueProtocol"];
  tuple_components: readonly ["currency", "minor_units", "settlement_account"];
  mechanism: "exact-source-ast-and-token-closed-subset";
  authority_effect: "none";
}>;

const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectTypeScriptValueObjectClosedSubset = (
  source: string,
): TypeScriptValueObjectClosedSubsetProofV1 => {
  const file = ts.createSourceFile("value-object-v1.ts", source,
    ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
  const parseDiagnostics = (file as ts.SourceFile & {
    readonly parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (parseDiagnostics.length > 0) return fail("TS_VALUE_OBJECT_SOURCE_INVALID");
  for (const token of ["Date", "Math.random", "process", "globalThis", "fetch(",
    "import(", "require(", "Proxy", "Reflect", "eval(", "async ", "await "]) {
    if (source.includes(token)) return fail("TS_VALUE_OBJECT_AMBIENT_SURFACE");
  }
  const exports = file.statements.filter(ts.isVariableStatement)
    .filter((statement) => ts.canHaveModifiers(statement)
      && (ts.getModifiers(statement) ?? []).some((modifier) =>
        modifier.kind === ts.SyntaxKind.ExportKeyword))
    .flatMap((statement) => statement.declarationList.declarations)
    .map((declaration) => ts.isIdentifier(declaration.name)
      ? declaration.name.text : "");
  if (JSON.stringify(exports) !== JSON.stringify([
    "createSettlementValueFactory", "settlementValueProtocol",
  ])) return fail("TS_VALUE_OBJECT_EXPORT_SHAPE");
  for (const required of [
    "complete-normalized-tuple",
    "additive-validation-only",
    "Object.freeze([...baseValidators, accountValidator])",
    "settlementAccount.equals(other.settlement_account)",
    "settlementAccount.hash()",
    "tuple[0] === other.tuple[0]",
    "tuple[1] === other.tuple[1]",
    "return Object.freeze({\n    protocol_id: protocolId",
    "account_ref: input.owned_value.account_ref",
    "for (const validator of validators)",
    "&& observed.protocol_sha256 === expected.protocol_sha256",
    "ok: false as const",
    "value: null",
    "input.settlement_account.owned_value.active",
    "protocol_id: \"typescript.owned-value-component.currency-code/v1\"",
    "protocol_id: \"typescript.owned-value-component.minor-units/v1\"",
    "protocol_id: \"typescript.owned-value-component.settlement-account/v1\"",
  ]) {
    if (!source.includes(required)) return fail("TS_VALUE_OBJECT_REQUIRED_SEMANTIC");
  }
  return Object.freeze({
    schema_version: "TypeScriptValueObjectClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: createHash("sha256").update(source, "utf8").digest("hex"),
    exports: Object.freeze([
      "createSettlementValueFactory", "settlementValueProtocol",
    ] as const),
    tuple_components: Object.freeze([
      "currency", "minor_units", "settlement_account",
    ] as const),
    mechanism: "exact-source-ast-and-token-closed-subset" as const,
    authority_effect: "none" as const,
  });
};
