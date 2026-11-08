import { createHash } from "node:crypto";
import { posix, win32 } from "node:path";

import ts from "typescript";

import type { EnumRealizationIR } from "../../../realization/contracts/enum-realization-ir.js";
import type { GeneratedSource } from "../../../realization/contracts/generated-source.js";
import type { TypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";

export class EnumEmitterError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "EnumEmitterError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new EnumEmitterError(code);
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const unsafeKeys = new Set(["__proto__", "constructor", "prototype"]);
const validIdentifier = (value: string): boolean => /^[A-Za-z_$][A-Za-z0-9_$]*$/u.test(value)
  && !new Set(["class", "enum", "function", "import", "export", "default", "const", "let", "var"])
    .has(value);
const safeModulePath = (value: string): boolean => !posix.isAbsolute(value)
  && !win32.isAbsolute(value) && !value.includes("\\")
  && !value.split("/").some((part) => ["", ".", ".."].includes(part));

const assertInputs = (ir: EnumRealizationIR, binding: TypeScriptTargetBinding): void => {
  if (ir.schema_version !== "EnumRealizationIR/v1" || ir.authority_effect !== "none"
      || binding.schema_version !== "TypeScriptTargetBinding/v1"
      || binding.authority_effect !== "none") return fail("ARCH_ENUM_EMITTER_INPUT_INVALID");
  if (binding.definition_ref.definition_id !== ir.definition_ref.definition_id
      || binding.definition_ref.definition_version !== ir.definition_ref.definition_version
      || binding.definition_ref.definition_sha256 !== ir.definition_ref.definition_sha256) {
    return fail("ARCH_ENUM_EMITTER_HANDLE_STALE");
  }
  if (!safeModulePath(binding.module_path)
      || binding.provider_module_specifier !== "../runtime/enum/index.js") {
    return fail("ARCH_ENUM_EMITTER_PATH_UNSAFE");
  }
  if (!validIdentifier(binding.export_name) || !validIdentifier(binding.type_name)) {
    return fail("ARCH_ENUM_EMITTER_IDENTIFIER_INVALID");
  }
  const memberIds = ir.members.map(({ member_id: memberId }) => memberId).sort(compareUtf8);
  const mappedIds = Object.keys(binding.member_names).sort(compareUtf8);
  if (memberIds.length !== mappedIds.length
      || memberIds.some((memberId, index) => memberId !== mappedIds[index])) {
    return fail("ARCH_ENUM_EMITTER_MAPPING_INCOMPLETE");
  }
  const identifiers = mappedIds.map((memberId) => binding.member_names[memberId] ?? "");
  if (identifiers.some((identifier) => !validIdentifier(identifier) || unsafeKeys.has(identifier))) {
    return fail("ARCH_ENUM_EMITTER_IDENTIFIER_INVALID");
  }
  if (new Set(identifiers).size !== identifiers.length) {
    return fail("ARCH_ENUM_EMITTER_IDENTIFIER_DUPLICATE");
  }
  if (ir.members.some(({ semantic_value: value }) => typeof value !== "string"
      || /[\u0000-\u001f\u007f]/u.test(value))) {
    return fail("ARCH_ENUM_EMITTER_VALUE_UNSAFE");
  }
};

const printSource = (ir: EnumRealizationIR, binding: TypeScriptTargetBinding): string => {
  const factory = ts.factory;
  const members = [...ir.members]
    .sort((left, right) => compareUtf8(left.member_id, right.member_id));
  const statements = [
    factory.createImportDeclaration(
      undefined,
      factory.createImportClause(
        false,
        undefined,
        factory.createNamedImports([
          factory.createImportSpecifier(false, undefined, factory.createIdentifier("defineEnum")),
          factory.createImportSpecifier(true, undefined, factory.createIdentifier("EnumValue")),
        ]),
      ),
      factory.createStringLiteral(binding.provider_module_specifier),
      undefined,
    ),
    factory.createVariableStatement(
      [factory.createModifier(ts.SyntaxKind.ExportKeyword)],
      factory.createVariableDeclarationList([
        factory.createVariableDeclaration(
          factory.createIdentifier(binding.export_name),
          undefined,
          undefined,
          factory.createCallExpression(factory.createIdentifier("defineEnum"), undefined, [
            factory.createAsExpression(
              factory.createObjectLiteralExpression(members.map((member) =>
                factory.createPropertyAssignment(
                  factory.createIdentifier(binding.member_names[member.member_id] as string),
                  factory.createStringLiteral(member.semantic_value),
                )), true),
              factory.createTypeReferenceNode("const"),
            ),
          ]),
        ),
      ], ts.NodeFlags.Const),
    ),
    factory.createTypeAliasDeclaration(
      [factory.createModifier(ts.SyntaxKind.ExportKeyword)],
      factory.createIdentifier(binding.type_name),
      undefined,
      factory.createTypeReferenceNode("EnumValue", [
        factory.createTypeQueryNode(factory.createIdentifier(binding.export_name)),
      ]),
    ),
  ];
  const sourceFile = factory.updateSourceFile(
    ts.createSourceFile(binding.module_path, "", ts.ScriptTarget.ESNext, false, ts.ScriptKind.TS),
    statements,
  );
  return ts.createPrinter({ newLine: ts.NewLineKind.LineFeed }).printFile(sourceFile);
};

const assertReparse = (
  source: string,
  ir: EnumRealizationIR,
  binding: TypeScriptTargetBinding,
): void => {
  const sourceFile = ts.createSourceFile(
    binding.module_path,
    source,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (sourceFile as ts.SourceFile & {
    readonly parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics;
  if (parseDiagnostics.length > 0 || sourceFile.statements.length !== 3) {
    return fail("ARCH_ENUM_EMITTER_REPARSE_FAILED");
  }
  const importDeclaration = sourceFile.statements[0];
  const variableStatement = sourceFile.statements[1];
  const typeAlias = sourceFile.statements[2];
  if (!importDeclaration || !ts.isImportDeclaration(importDeclaration)
      || !ts.isStringLiteral(importDeclaration.moduleSpecifier)
      || importDeclaration.moduleSpecifier.text !== binding.provider_module_specifier
      || !variableStatement || !ts.isVariableStatement(variableStatement)
      || !typeAlias || !ts.isTypeAliasDeclaration(typeAlias)
      || typeAlias.name.text !== binding.type_name) {
    return fail("ARCH_ENUM_EMITTER_REPARSE_FAILED");
  }
  const declaration = variableStatement.declarationList.declarations[0];
  const call = declaration?.initializer;
  if (!declaration || !ts.isIdentifier(declaration.name)
      || declaration.name.text !== binding.export_name
      || !call || !ts.isCallExpression(call) || call.arguments.length !== 1
      || !ts.isIdentifier(call.expression) || call.expression.text !== "defineEnum") {
    return fail("ARCH_ENUM_EMITTER_REPARSE_FAILED");
  }
  const asserted = call.arguments[0];
  const object = asserted && ts.isAsExpression(asserted) ? asserted.expression : undefined;
  if (!object || !ts.isObjectLiteralExpression(object) || object.properties.length !== ir.members.length) {
    return fail("ARCH_ENUM_EMITTER_REPARSE_FAILED");
  }
  const observed = object.properties.map((property) => {
    if (!ts.isPropertyAssignment(property) || !ts.isIdentifier(property.name)
        || !ts.isStringLiteral(property.initializer)) {
      return fail("ARCH_ENUM_EMITTER_REPARSE_FAILED");
    }
    return { target_identifier: property.name.text, semantic_value: property.initializer.text };
  });
  const expected = [...ir.members].sort((left, right) => compareUtf8(left.member_id, right.member_id))
    .map((member) => ({
      target_identifier: binding.member_names[member.member_id] as string,
      semantic_value: member.semantic_value,
    }));
  if (JSON.stringify(observed) !== JSON.stringify(expected)) {
    return fail("ARCH_ENUM_EMITTER_REPARSE_MISMATCH");
  }
};

export const emitTypeScriptEnum = (
  ir: EnumRealizationIR,
  binding: TypeScriptTargetBinding,
): GeneratedSource => {
  assertInputs(ir, binding);
  const source = printSource(ir, binding);
  assertReparse(source, ir, binding);
  const repeat = printSource(ir, binding);
  if (repeat !== source) return fail("ARCH_ENUM_EMITTER_NONDETERMINISTIC");
  const emittedMembers = [...ir.members]
    .sort((left, right) => compareUtf8(left.member_id, right.member_id))
    .map((member) => Object.freeze({
      member_id: member.member_id,
      target_identifier: binding.member_names[member.member_id] as string,
      semantic_value: member.semantic_value,
    }));
  return Object.freeze({
    source,
    manifest: Object.freeze({
      schema_version: "GeneratedSourceManifest/v1" as const,
      module_path: binding.module_path,
      source_sha256: sha256(source),
      source_byte_length: Buffer.byteLength(source, "utf8"),
      export_name: binding.export_name,
      type_name: binding.type_name,
      provider_module_specifier: binding.provider_module_specifier,
      emitted_members: Object.freeze(emittedMembers),
      format_version: "typescript-printer/v1" as const,
      authority_effect: "none" as const,
    }),
  });
};
