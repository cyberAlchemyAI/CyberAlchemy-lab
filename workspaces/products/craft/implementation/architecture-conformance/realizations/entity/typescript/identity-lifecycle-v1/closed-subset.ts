import {createHash} from "node:crypto";
import ts from "typescript";

export type TypeScriptEntityClosedSubsetProofV1 = Readonly<{
  schema_version: "TypeScriptEntityClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  exports: readonly ["createSettlementEntityFactory", "settlementEntityProtocol"];
  construction_routes: readonly ["factory", "deserialization-reconstruction",
    "lifecycle-transition", "language-visible-direct-constructor"];
  source_control_count: 10;
  mechanism: "exact-source-ast-and-token-closed-subset";
  authority_effect: "none";
}>;

const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectTypeScriptEntityClosedSubset = (
  source: string,
): TypeScriptEntityClosedSubsetProofV1 => {
  const file = ts.createSourceFile("entity-v1.ts", source,
    ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
  const diagnostics = (file as ts.SourceFile & {
    readonly parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (diagnostics.length > 0) return fail("TS_ENTITY_SOURCE_INVALID");
  for (const token of ["Date", "Math.random", "process", "globalThis", "fetch(",
    "import(", "require(", "Proxy", "Reflect", "eval(", "async ", "await ",
    "class ", "new ", "constructor(", "constructor =", "constructor:",
    "Object.defineProperty"] as const) {
    if (source.includes(token)) return fail("TS_ENTITY_AMBIENT_SURFACE");
  }
  const exportedStatements = file.statements.filter((statement) =>
    ts.canHaveModifiers(statement) && (ts.getModifiers(statement) ?? [])
      .some((modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword));
  if (exportedStatements.some((statement) => !ts.isVariableStatement(statement))) {
    return fail("TS_ENTITY_EXPORT_SURFACE");
  }
  const exports = exportedStatements.filter(ts.isVariableStatement)
    .flatMap((statement) => statement.declarationList.declarations)
    .map((declaration) => ts.isIdentifier(declaration.name)
      ? declaration.name.text : "");
  if (JSON.stringify(exports) !== JSON.stringify([
    "createSettlementEntityFactory", "settlementEntityProtocol",
  ])) return fail("TS_ENTITY_EXPORT_SHAPE");
  const required = [
    "for (const validator of validators)",
    "ownerMatchesValidator,\n  amountValidValidator",
    "const identity = resolveIdentity(input)",
    "Object.freeze([...baseValidators, duplicateBlockedValidator])",
    "value: null",
    "return Object.freeze({\n    entity_case_id: input.entity_case_id",
    "equals: (other: SettlementEntity): boolean => key === identityKey(other.identity),",
    "hash: (): string => key,",
    "executeRoute(\"deserialization-reconstruction\", validators, input)",
    "organization_id: previous.identity[0]",
    "directConstructor: null",
    "? () => createSettlementEntityFactory(\"with-duplicate-blocked\") : null",
    "protocol_id: \"typescript.validated-extensible-entity-factory/v1\"",
    "direct_constructor_policy: \"private-inaccessible\"",
  ] as const;
  for (const token of required) {
    if (!source.includes(token)) return fail("TS_ENTITY_REQUIRED_SEMANTIC");
  }
  if ((source.match(/directConstructor: null,/gu) ?? []).length !== 1) {
    return fail("TS_ENTITY_DIRECT_CONSTRUCTOR_SURFACE");
  }
  if ((source.match(/value: null,/gu) ?? []).length !== 2) {
    return fail("TS_ENTITY_FAILURE_SURFACE");
  }
  return Object.freeze({
    schema_version: "TypeScriptEntityClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: createHash("sha256").update(source, "utf8").digest("hex"),
    exports: Object.freeze([
      "createSettlementEntityFactory", "settlementEntityProtocol",
    ] as const),
    construction_routes: Object.freeze(["factory",
      "deserialization-reconstruction", "lifecycle-transition",
      "language-visible-direct-constructor"] as const),
    source_control_count: 10 as const,
    mechanism: "exact-source-ast-and-token-closed-subset" as const,
    authority_effect: "none" as const,
  });
};
