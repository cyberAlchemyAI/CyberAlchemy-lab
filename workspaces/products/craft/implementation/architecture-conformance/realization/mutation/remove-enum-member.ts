import { createHash } from "node:crypto";

import ts from "typescript";

import type { EnumMutationResult } from "../contracts/architecture-mutation.js";
import type { GeneratedSource } from "../contracts/generated-source.js";
import type { TypeScriptTargetBinding } from "../contracts/typescript-target-binding.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
export const enumMutationConfigSha256 = sha256(
  "remove-one-bound-enum-member/v1",
);
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const propertyIdentifier = (property: ts.ObjectLiteralElementLike): string | null =>
  ts.isPropertyAssignment(property)
    && (ts.isIdentifier(property.name) || ts.isStringLiteral(property.name))
    ? property.name.text
    : null;

export const removeEnumMember = (
  parent: GeneratedSource,
  binding: TypeScriptTargetBinding,
  memberId: string,
): EnumMutationResult => {
  if (sha256(parent.source) !== parent.manifest.source_sha256) {
    return fail("ARCH_ENUM_MUTATION_PARENT_STALE");
  }
  const targetIdentifier = binding.member_names[memberId];
  if (!targetIdentifier) return fail("ARCH_ENUM_MUTATION_BINDING_MISSING");
  const sourceFile = ts.createSourceFile(
    parent.manifest.module_path,
    parent.source,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  let matchedNodes = 0;
  const transformedStatements = sourceFile.statements.map((statement) => {
    if (!ts.isVariableStatement(statement)) return statement;
    const declarations = statement.declarationList.declarations.map((declaration) => {
      if (!ts.isIdentifier(declaration.name) || declaration.name.text !== binding.export_name) {
        return declaration;
      }
      const call = declaration.initializer;
      if (!call || !ts.isCallExpression(call) || call.arguments.length !== 1) {
        return fail("ARCH_ENUM_MUTATION_FORM_UNSUPPORTED");
      }
      const asserted = call.arguments[0];
      if (!asserted || !ts.isAsExpression(asserted)
          || !ts.isObjectLiteralExpression(asserted.expression)) {
        return fail("ARCH_ENUM_MUTATION_FORM_UNSUPPORTED");
      }
      const kept = asserted.expression.properties.filter((property) => {
        const matched = propertyIdentifier(property) === targetIdentifier;
        if (matched) matchedNodes += 1;
        return !matched;
      });
      const object = ts.factory.updateObjectLiteralExpression(asserted.expression, kept);
      const updatedAssertion = ts.factory.updateAsExpression(asserted, object, asserted.type);
      const updatedCall = ts.factory.updateCallExpression(
        call,
        call.expression,
        call.typeArguments,
        [updatedAssertion],
      );
      return ts.factory.updateVariableDeclaration(
        declaration,
        declaration.name,
        declaration.exclamationToken,
        declaration.type,
        updatedCall,
      );
    });
    return ts.factory.updateVariableStatement(
      statement,
      statement.modifiers,
      ts.factory.updateVariableDeclarationList(statement.declarationList, declarations),
    );
  });
  if (matchedNodes !== 1) return fail("ARCH_ENUM_MUTATION_TARGET_CARDINALITY");
  const childFile = ts.factory.updateSourceFile(sourceFile, transformedStatements);
  const childSource = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed }).printFile(childFile);
  const reparsed = ts.createSourceFile(
    parent.manifest.module_path,
    childSource,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (reparsed as ts.SourceFile & {
    readonly parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics;
  if (parseDiagnostics.length > 0 || childSource === parent.source) {
    return fail("ARCH_ENUM_MUTATION_CHILD_INVALID");
  }
  const childDigest = sha256(childSource);
  const deltaBody = {
    operation: "remove-enum-member" as const,
    member_id: memberId,
    target_identifier: targetIdentifier,
    deleted_nodes: 1 as const,
    inserted_nodes: 0 as const,
  };
  const delta = Object.freeze({
    ...deltaBody,
    delta_sha256: sha256(JSON.stringify(deltaBody)),
  });
  const childManifest = Object.freeze({
    ...parent.manifest,
    source_sha256: childDigest,
    source_byte_length: Buffer.byteLength(childSource, "utf8"),
    emitted_members: Object.freeze(parent.manifest.emitted_members.filter(
      ({ member_id: emittedMemberId }) => emittedMemberId !== memberId,
    )),
  });
  return Object.freeze({
    child: Object.freeze({ source: childSource, manifest: childManifest }),
    mutation: Object.freeze({
      schema_version: "ArchitectureMutation/v1" as const,
      mutation_id: `mutation.enum.${sha256(`${parent.manifest.source_sha256}:${childDigest}:${delta.delta_sha256}`)}`,
      parent_source_sha256: parent.manifest.source_sha256,
      child_source_sha256: childDigest,
      delta,
      expected_compile_phase: "compile-green" as const,
      expected_failure_code: "ARCH_ENUM_MEMBER_MISSING" as const,
      tool: Object.freeze({
        name: "domainspec-enum-mutator" as const,
        version: "1.0.0" as const,
        config_sha256: enumMutationConfigSha256,
      }),
      authority_effect: "none" as const,
    }),
  });
};
