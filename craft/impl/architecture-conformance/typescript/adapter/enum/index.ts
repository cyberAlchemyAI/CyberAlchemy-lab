import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { basename, dirname, relative, resolve } from "node:path";

import ts from "typescript";

import type { GeneratedSourceManifest } from "../../../realization/contracts/generated-source.js";

type JsonRecord = Readonly<Record<string, unknown>>;

export type ObservationProjection = Readonly<{
  schema_version: "domainspec-observation-projection/v1";
  projection_id: string;
  language: "typescript";
  artifact_digest: string;
  tool: Readonly<{ provider_id: string; version: string; config_digest: string }>;
  adapter: Readonly<{ provider_id: string; version: string; config_digest: string }>;
  profile_digest: string;
  raw_evidence_refs: readonly JsonRecord[];
  subjects: readonly JsonRecord[];
  relations: readonly JsonRecord[];
  facts: readonly JsonRecord[];
  diagnostics: readonly JsonRecord[];
  redaction_posture: Readonly<{ mode: "opaque-references"; owner_route: string }>;
  authority_effect: "none";
}>;

export type ProjectTypeScriptEnumOptions = Readonly<{
  repositoryRoot: string;
  sourcePath: string;
  exportName: string;
  subjectRef: string;
  conceptId: string;
  expectedValues: readonly string[];
  profilePath: string;
  providerPath: string;
  profileActivationReceiptPath: string;
}>;

export type GeneratedEnumObservation = Readonly<{
  schema_version: "ObservationProjection/v1";
  observation_id: string;
  source_manifest_ref: Readonly<{ module_path: string; source_sha256: string }>;
  protocol_ref: Readonly<{ protocol_id: "typescript.owned-const-object-enum/v1"; provider_sha256: string }>;
  facts: readonly Readonly<{
    fact_type: "enum-member";
    semantic_member_id: null;
    target_identifier: string;
    runtime_value: string;
    source_span: Readonly<{ start: number; length: number }>;
    confidence: "exact";
  }>[];
  unsupported: readonly Readonly<{ code: string; reason: string }>[];
  diagnostics: readonly Readonly<{ code: string; message: string }>[];
  observation_sha256: string;
  authority_effect: "none";
}>;

export type ObserveGeneratedTypeScriptEnumOptions = Readonly<{
  source: string;
  manifest: GeneratedSourceManifest;
  providerSource: string;
  admittedProviderSha256: string;
}>;

export class TypeScriptEnumAdapterError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = "TypeScriptEnumAdapterError";
    this.code = code;
  }
}

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

const assertNoParseDiagnostics = (sourceFile: ts.SourceFile): void => {
  const diagnostics = (sourceFile as ts.SourceFile & {
    readonly parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics;
  if (diagnostics.length > 0) {
    throw new TypeScriptEnumAdapterError(
      "ARCH_ENUM_OBSERVATION_PARSE_DIAGNOSTIC",
      diagnostics.map(({ code }) => `TS${code}`).join(","),
    );
  }
};

const assertCompleteGeneratedModule = (
  sourceFile: ts.SourceFile,
  manifest: GeneratedSourceManifest,
): void => {
  const imports = sourceFile.statements.filter(ts.isImportDeclaration);
  const variables = sourceFile.statements.filter(ts.isVariableStatement);
  const types = sourceFile.statements.filter(ts.isTypeAliasDeclaration);
  const selectedVariables = variables.flatMap((statement) =>
    statement.declarationList.declarations.filter((declaration) =>
      ts.isIdentifier(declaration.name) && declaration.name.text === manifest.export_name));
  if (sourceFile.statements.length !== 3 || imports.length !== 1 || variables.length !== 1
      || types.length !== 1 || selectedVariables.length !== 1
      || types[0]?.name.text !== manifest.type_name) {
    throw new TypeScriptEnumAdapterError(
      "ARCH_ENUM_OBSERVATION_SOURCE_SCOPE_UNSUPPORTED",
      "the complete generated module must contain only its provider import, selected Enum, and value type",
    );
  }
};

const repositoryPath = (root: string, path: string): string =>
  resolve(root, path);

const filenameCase = (path: string): "kebab-case" | "snake_case" | "other" => {
  const stem = basename(path).replace(/\.[^.]+$/, "");
  if (/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(stem)) return "kebab-case";
  if (/^[a-z0-9]+(?:_[a-z0-9]+)*$/.test(stem)) return "snake_case";
  return "other";
};

const unwrapConstAssertion = (
  expression: ts.Expression,
  sourceFile: ts.SourceFile,
): ts.Expression | null => {
  if (!ts.isAsExpression(expression)) return null;
  if (expression.type.getText(sourceFile) !== "const") return null;
  return expression.expression;
};

const exportedVariable = (
  sourceFile: ts.SourceFile,
  exportName: string,
): ts.VariableDeclaration | null => {
  for (const statement of sourceFile.statements) {
    if (!ts.isVariableStatement(statement)) continue;
    if (!statement.modifiers?.some(({ kind }) => kind === ts.SyntaxKind.ExportKeyword)) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (ts.isIdentifier(declaration.name) && declaration.name.text === exportName) {
        return declaration;
      }
    }
  }
  return null;
};

const providerImportName = (
  sourceFile: ts.SourceFile,
  sourcePath: string,
  providerPath: string,
): string | null => {
  for (const statement of sourceFile.statements) {
    if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)) continue;
    const specifier = statement.moduleSpecifier.text;
    if (!specifier.startsWith(".")) continue;
    const resolvedImport = resolve(dirname(sourcePath), specifier).replace(/\.js$/, ".ts");
    if (resolvedImport !== providerPath) continue;
    const bindings = statement.importClause?.namedBindings;
    if (!bindings || !ts.isNamedImports(bindings)) continue;
    const binding = bindings.elements.find(
      (element) => (element.propertyName?.text ?? element.name.text) === "defineEnum",
    );
    if (binding) return binding.name.text;
  }
  return null;
};

type ParsedMembers =
  | Readonly<{ status: "supported"; members: readonly Readonly<{
      key: string;
      value: string;
      start: number;
      length: number;
    }>[] }>
  | Readonly<{ status: "unsupported"; code: string; reason: string }>;

const parseMembers = (
  sourceFile: ts.SourceFile,
  declaration: ts.VariableDeclaration | null,
  helperName: string | null,
): ParsedMembers => {
  if (!helperName) {
    return {
      status: "unsupported",
      code: "TS_ENUM_PROVIDER_BINDING_UNSUPPORTED",
      reason: "defineEnum is not imported from the exact admitted provider path.",
    };
  }
  const initializer = declaration?.initializer;
  if (!initializer || !ts.isCallExpression(initializer)) {
    return {
      status: "unsupported",
      code: "TS_ENUM_FORM_UNSUPPORTED",
      reason: "The selected export is not a defineEnum call.",
    };
  }
  if (!ts.isIdentifier(initializer.expression) || initializer.expression.text !== helperName) {
    return {
      status: "unsupported",
      code: "TS_ENUM_HELPER_IMPERSONATION_UNSUPPORTED",
      reason: "The selected export does not call the bound defineEnum import.",
    };
  }
  if (initializer.arguments.length !== 1) {
    return {
      status: "unsupported",
      code: "TS_ENUM_ARGUMENT_SHAPE_UNSUPPORTED",
      reason: "defineEnum requires one const-asserted object literal.",
    };
  }
  const object = unwrapConstAssertion(initializer.arguments[0], sourceFile);
  if (!object || !ts.isObjectLiteralExpression(object)) {
    return {
      status: "unsupported",
      code: "TS_ENUM_CONST_OBJECT_REQUIRED",
      reason: "defineEnum requires an inline object literal asserted as const.",
    };
  }

  const members: Array<Readonly<{ key: string; value: string; start: number; length: number }>> = [];
  for (const property of object.properties) {
    if (!ts.isPropertyAssignment(property)) {
      return {
        status: "unsupported",
        code: "TS_ENUM_MEMBER_SHAPE_UNSUPPORTED",
        reason: "Spread, accessor, method, and shorthand members are unsupported.",
      };
    }
    if (ts.isComputedPropertyName(property.name)) {
      return {
        status: "unsupported",
        code: "TS_ENUM_COMPUTED_MEMBER_UNSUPPORTED",
        reason: "Computed Enum member names are unsupported.",
      };
    }
    const key = ts.isIdentifier(property.name) || ts.isStringLiteral(property.name)
      ? property.name.text
      : null;
    const value = ts.isStringLiteral(property.initializer) ||
        ts.isNoSubstitutionTemplateLiteral(property.initializer)
      ? property.initializer.text
      : null;
    if (key === null || value === null) {
      return {
        status: "unsupported",
        code: "TS_ENUM_LITERAL_MEMBER_REQUIRED",
        reason: "Enum keys and values must be statically readable string literals.",
      };
    }
    members.push({ key, value, start: property.getStart(sourceFile), length: property.getWidth(sourceFile) });
  }
  return {
    status: "supported",
    members: [...members].sort((left, right) => Buffer.from(left.key).compare(Buffer.from(right.key))),
  };
};

const observationDigest = (
  value: Omit<GeneratedEnumObservation, "observation_sha256">,
): string => sha256(`${JSON.stringify(value)}\n`);

export const observeGeneratedTypeScriptEnum = (
  options: ObserveGeneratedTypeScriptEnumOptions,
): GeneratedEnumObservation => {
  const sourceDigest = sha256(options.source);
  if (options.manifest.schema_version !== "GeneratedSourceManifest/v1"
      || options.manifest.authority_effect !== "none"
      || sourceDigest !== options.manifest.source_sha256
      || Buffer.byteLength(options.source, "utf8") !== options.manifest.source_byte_length) {
    throw new TypeScriptEnumAdapterError(
      "ARCH_ENUM_OBSERVATION_SOURCE_STALE",
      "generated source does not match its manifest",
    );
  }
  const providerDigest = sha256(options.providerSource);
  if (options.manifest.provider_module_specifier !== "../runtime/enum/index.js"
      || providerDigest !== options.admittedProviderSha256) {
    throw new TypeScriptEnumAdapterError(
      "ARCH_ENUM_OBSERVATION_PROVIDER_STALE",
      "generated source is not bound to the admitted provider",
    );
  }
  const sourceFile = ts.createSourceFile(
    options.manifest.module_path,
    options.source,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  assertNoParseDiagnostics(sourceFile);
  assertCompleteGeneratedModule(sourceFile, options.manifest);
  const declaration = exportedVariable(sourceFile, options.manifest.export_name);
  const helperName = sourceFile.statements.flatMap((statement) => {
    if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)
        || statement.moduleSpecifier.text !== options.manifest.provider_module_specifier) return [];
    const bindings = statement.importClause?.namedBindings;
    if (!bindings || !ts.isNamedImports(bindings)) return [];
    const binding = bindings.elements.find(
      (element) => (element.propertyName?.text ?? element.name.text) === "defineEnum",
    );
    return binding ? [binding.name.text] : [];
  })[0] ?? null;
  const parsed = parseMembers(sourceFile, declaration, helperName);
  const unsupported = parsed.status === "unsupported"
    ? [{ code: parsed.code, reason: parsed.reason }] as const
    : [];
  const facts = parsed.status === "supported"
    ? parsed.members.map(({ key, value, start, length }) => Object.freeze({
        fact_type: "enum-member" as const,
        semantic_member_id: null,
        target_identifier: key,
        runtime_value: value,
        source_span: Object.freeze({ start, length }),
        confidence: "exact" as const,
      }))
    : [];
  const diagnostics = unsupported.map(({ code, reason }) => ({ code, message: reason }));
  const body = Object.freeze({
    schema_version: "ObservationProjection/v1" as const,
    observation_id: `observation.typescript.enum.${sourceDigest}`,
    source_manifest_ref: Object.freeze({
      module_path: options.manifest.module_path,
      source_sha256: sourceDigest,
    }),
    protocol_ref: Object.freeze({
      protocol_id: "typescript.owned-const-object-enum/v1" as const,
      provider_sha256: providerDigest,
    }),
    facts: Object.freeze(facts),
    unsupported: Object.freeze(unsupported),
    diagnostics: Object.freeze(diagnostics),
    authority_effect: "none" as const,
  });
  return Object.freeze({ ...body, observation_sha256: observationDigest(body) });
};

const fact = (
  id: string,
  subjectRef: string,
  predicateRef: string,
  scopeRef: string,
  value: unknown,
  provenance: JsonRecord,
): JsonRecord => ({
  fact_id: id,
  fact_scope: "observation",
  subject_ref: subjectRef,
  predicate_ref: predicateRef,
  scope_ref: scopeRef,
  value,
  provenance,
});

export const projectTypeScriptEnum = async (
  options: ProjectTypeScriptEnumOptions,
): Promise<ObservationProjection> => {
  const root = resolve(options.repositoryRoot);
  const sourcePath = repositoryPath(root, options.sourcePath);
  const profilePath = repositoryPath(root, options.profilePath);
  const providerPath = repositoryPath(root, options.providerPath);
  const [sourceText, profileText, providerText] = await Promise.all([
    readFile(sourcePath, "utf8"),
    readFile(profilePath, "utf8"),
    readFile(providerPath, "utf8"),
  ]);
  const profile = JSON.parse(profileText) as {
    representation_overlays?: Array<{
      candidate_protocols?: Array<{
        protocol_id?: string;
        runtime_provider?: { module_path?: string; provider_sha256?: string };
      }>;
      activation_binding?: {
        protocol_id?: string;
        decision_ref?: { path?: string; sha256?: string };
        provider_receipt_ref?: { path?: string; sha256?: string };
      };
    }>;
  };
  const overlay = profile.representation_overlays?.[0];
  const protocol = overlay?.candidate_protocols?.[0];
  const activation = overlay?.activation_binding;
  const providerRelativePath = relative(root, providerPath).replaceAll("\\", "/");
  if (protocol?.protocol_id !== "typescript.owned-const-object-enum/v1") {
    throw new TypeScriptEnumAdapterError("ADAPTER_PROTOCOL_MISMATCH", "profile protocol is not admitted");
  }
  if (protocol.runtime_provider?.module_path !== providerRelativePath) {
    throw new TypeScriptEnumAdapterError("ADAPTER_PROVIDER_PATH_MISMATCH", "profile provider path is stale");
  }
  const providerDigest = sha256(providerText);
  if (protocol.runtime_provider.provider_sha256 !== providerDigest) {
    throw new TypeScriptEnumAdapterError("ADAPTER_PROVIDER_DIGEST_STALE", "profile provider digest is stale");
  }
  if (activation?.protocol_id !== protocol.protocol_id
      || activation.decision_ref?.path === undefined
      || activation.provider_receipt_ref?.path === undefined
      || options.profileActivationReceiptPath !== activation.provider_receipt_ref.path) {
    throw new TypeScriptEnumAdapterError(
      "ADAPTER_ACTIVATION_BINDING_MISMATCH",
      "the supplied provider receipt is not the exact profile activation binding",
    );
  }
  const decisionPath = repositoryPath(root, activation.decision_ref.path);
  const receiptPath = repositoryPath(root, activation.provider_receipt_ref.path);
  const [decisionText, receiptText] = await Promise.all([
    readFile(decisionPath, "utf8"),
    readFile(receiptPath, "utf8"),
  ]);
  const decisionDigest = sha256(decisionText);
  const receiptDigest = sha256(receiptText);
  if (decisionDigest !== activation.decision_ref.sha256
      || receiptDigest !== activation.provider_receipt_ref.sha256) {
    throw new TypeScriptEnumAdapterError(
      "ADAPTER_ACTIVATION_EVIDENCE_STALE",
      "profile activation decision or provider receipt digest is stale",
    );
  }
  const decision = JSON.parse(decisionText) as {
    schema_version?: string;
    decision_id?: string;
    selected_protocol?: { protocol_id?: string; module_path?: string };
    owner?: { owner_role?: string };
    authority_effect?: string;
  };
  const receipt = JSON.parse(receiptText) as {
    schema_version?: string;
    swu_id?: string;
    result?: string;
    acceptance_accounting?: {
      protocol_id?: string;
      provider_source?: { path?: string; sha256?: string };
    };
  };
  if (decision.schema_version !== "ape.enum.typescript-representation-decision.v1"
      || decision.authority_effect !== "none"
      || decision.selected_protocol?.protocol_id !== protocol.protocol_id
      || decision.selected_protocol?.module_path !== providerRelativePath
      || decision.owner?.owner_role !== "typescript-architecture-profile-owner"
      || receipt.schema_version !== "ape.swu-receipt.v1"
      || receipt.swu_id !== "SWU-APE-ENUM-TS-001A"
      || receipt.result !== "pass"
      || receipt.acceptance_accounting?.protocol_id !== protocol.protocol_id
      || receipt.acceptance_accounting?.provider_source?.path !== providerRelativePath
      || receipt.acceptance_accounting?.provider_source?.sha256 !== providerDigest) {
    throw new TypeScriptEnumAdapterError(
      "ADAPTER_ACTIVATION_EVIDENCE_INVALID",
      "profile activation evidence does not join the selected protocol and provider",
    );
  }

  const sourceDigest = sha256(sourceText);
  const profileDigest = sha256(profileText);
  const sourceFile = ts.createSourceFile(
    sourcePath,
    sourceText,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  assertNoParseDiagnostics(sourceFile);
  const declaration = exportedVariable(sourceFile, options.exportName);
  const helperName = providerImportName(sourceFile, sourcePath, providerPath);
  const parsed = parseMembers(sourceFile, declaration, helperName);
  const sourceRef = "raw.typescript.enum.source";
  const decisionRef = "raw.typescript.profile-decision";
  const providerReceiptRef = "raw.typescript.provider-receipt";
  const scopeRef = `source:${options.exportName}`;
  const observed = { kind: "observed", owner_route: "typescript-adapter-owner", raw_refs: [sourceRef] };
  const ownerResolved = {
    kind: "owner-resolved",
    owner_route: "typescript-architecture-profile-owner",
    raw_refs: [decisionRef, providerReceiptRef],
    decision_ref: {
      decision_id: decision.decision_id,
      decision_digest: decisionDigest,
      decided_by: "typescript-architecture-profile-owner",
      outcome: "activate-typescript.owned-const-object-enum/v1",
    },
  };
  const rawEvidence = [
    { ref_id: sourceRef, kind: "source", uri: `repo://${options.sourcePath}`, sha256: sourceDigest, selector: options.exportName },
    { ref_id: decisionRef, kind: "owner-decision", uri: `repo://${activation.decision_ref.path}`, sha256: decisionDigest, selector: "/selected_protocol" },
    { ref_id: providerReceiptRef, kind: "provider-receipt", uri: `repo://${activation.provider_receipt_ref.path}`, sha256: receiptDigest, selector: "/acceptance_accounting/provider_source" },
  ];
  const common = {
    schema_version: "domainspec-observation-projection/v1" as const,
    projection_id: `projection.typescript.enum.${options.subjectRef}`,
    language: "typescript" as const,
    artifact_digest: sourceDigest,
    tool: {
      provider_id: "typescript-compiler-api",
      version: ts.version,
      config_digest: sha256(JSON.stringify({ scriptKind: "TS", scriptTarget: "ESNext" })),
    },
    adapter: {
      provider_id: "domainspec.typescript-enum-adapter",
      version: "1.0.0",
      config_digest: sha256(JSON.stringify({ protocol: protocol.protocol_id, provider: providerDigest })),
    },
    profile_digest: profileDigest,
    raw_evidence_refs: rawEvidence,
    subjects: [{ subject_ref: options.subjectRef, ontology_type: "architecture.EnumImplementation" }],
    relations: [],
    redaction_posture: { mode: "opaque-references" as const, owner_route: "typescript-adapter-owner" },
    authority_effect: "none" as const,
  };

  if (parsed.status === "unsupported") {
    const unsupported = {
      kind: "unsupported",
      owner_route: "typescript-architecture-profile-owner",
      raw_refs: [sourceRef],
      unsupported_ref: { code: parsed.code, reason: parsed.reason, scope: "representation.protocol_id" },
    };
    return {
      ...common,
      facts: [fact("fact.representation.protocol.unsupported", options.subjectRef, "representation.protocol_id", scopeRef, null, unsupported)],
      diagnostics: [{ code: parsed.code, message: parsed.reason, owner_route: "typescript-architecture-profile-owner", raw_refs: [sourceRef] }],
    };
  }

  const values = parsed.members.map(({ value }) => value);
  const sourceRelativePath = relative(root, sourcePath).replaceAll("\\", "/");
  const observedFacts: Array<readonly [string, string, unknown]> = [
    ["source.language", "source.language", "typescript"],
    ["source.path", "source.path", sourceRelativePath],
    ["source.filename-case", "source.filename_case", filenameCase(sourceRelativePath)],
    ["source.primary-concept-count", "source.primary_concept_count", 1],
    ["symbol.primary-callable-count", "symbol.primary_callable_count", 1],
    ["callable.helper-policy", "callable.helper_policy", "separate-source-units"],
    ["enum.implemented-values", "enum.implemented_values", values],
    ["enum.implemented-members", "enum.implemented_members", parsed.members],
    ["enum.composition-kind", "enum.composition_kind", "direct"],
    ["structure.typed-field-count", "structure.typed_field_count", 0],
    ["identity.component-count", "identity.component_count", 0],
    ["state.transition-count", "state.transition_count", 0],
    ["representation.protocol-id", "representation.protocol_id", protocol.protocol_id],
    ["runtime.provider-sha256", "runtime.provider_sha256", providerDigest],
  ];
  const facts = observedFacts.map(([id, predicate, value]) =>
    fact(`fact.${id}`, options.subjectRef, predicate, scopeRef, value, observed)
  );
  facts.push(
    fact("fact.binding.concept-id", options.subjectRef, "binding.concept_id", scopeRef, options.conceptId, ownerResolved),
    fact("fact.binding.current", options.subjectRef, "binding.current", scopeRef, true, ownerResolved),
    fact("fact.binding.expected-values", options.subjectRef, "binding.expected_enum_values", scopeRef, [...options.expectedValues], ownerResolved),
  );
  return { ...common, facts, diagnostics: [] };
};
