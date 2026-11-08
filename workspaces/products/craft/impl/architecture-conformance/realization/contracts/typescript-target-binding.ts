import { createHash } from "node:crypto";
import { posix, win32 } from "node:path";

import type { EnumDefinitionSnapshot } from "./enum-definition-snapshot.js";

type JsonObject = Record<string, unknown>;

export type TypeScriptTargetBinding = Readonly<{
  schema_version: "TypeScriptTargetBinding/v1";
  binding_id: string;
  definition_ref: Readonly<{
    definition_id: string;
    definition_version: string;
    definition_sha256: string;
  }>;
  language: "typescript";
  module_path: string;
  export_name: string;
  type_name: string;
  member_names: Readonly<Record<string, string>>;
  provider_module_specifier: string;
  protocol_ref: "typescript.owned-const-object-enum/v1";
  profile_ref: Readonly<{ path: string; sha256: string }>;
  provider_ref: Readonly<{ path: string; sha256: string }>;
  emitter_version: string;
  emitter_config_digest: string;
  format_version: "typescript-printer/v1";
  binding_sha256: string;
  authority_effect: "none";
}>;

export class TypeScriptTargetBindingError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "TypeScriptTargetBindingError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new TypeScriptTargetBindingError(code);
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;
const sha256 = (value: string): string =>
  createHash("sha256").update(value).digest("hex");
const exactKeys = (value: JsonObject, expected: readonly string[]): boolean => {
  const keys = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  return keys.length === wanted.length && keys.every((key, index) => key === wanted[index]);
};
const asObject = (value: unknown): JsonObject => {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return fail("ARCH_TS_BINDING_SHAPE_INVALID");
  }
  return value as JsonObject;
};
const asString = (value: unknown, code = "ARCH_TS_BINDING_SHAPE_INVALID"): string => {
  if (typeof value !== "string" || value.length === 0 || /[\u0000-\u001f\u007f]/u.test(value)) {
    return fail(code);
  }
  return value;
};
const safeRelativePath = (value: string): boolean => !posix.isAbsolute(value)
  && !win32.isAbsolute(value)
  && !value.includes("\\")
  && !value.split("/").some((part) => part === "" || part === "." || part === "..");
const reserved = new Set([
  "await", "break", "case", "catch", "class", "const", "continue", "debugger",
  "default", "delete", "do", "else", "enum", "export", "extends", "false",
  "finally", "for", "function", "if", "import", "in", "instanceof", "interface",
  "let", "new", "null", "package", "private", "protected", "public", "return",
  "static", "super", "switch", "this", "throw", "true", "try", "typeof", "var",
  "void", "while", "with", "yield",
]);
const unsafeKeys = new Set(["__proto__", "constructor", "prototype"]);
const validIdentifier = (value: string): boolean => /^[A-Za-z_$][A-Za-z0-9_$]*$/u.test(value)
  && !reserved.has(value);

const withoutDigest = (binding: Omit<TypeScriptTargetBinding, "binding_sha256">) => ({
  ...binding,
  member_names: Object.fromEntries(
    Object.entries(binding.member_names).sort(([left], [right]) => compareUtf8(left, right)),
  ),
});

export const computeTypeScriptTargetBindingSha256 = (
  binding: Omit<TypeScriptTargetBinding, "binding_sha256">,
): string => sha256(JSON.stringify(canonicalize(withoutDigest(binding))));

export const validateTypeScriptTargetBinding = (
  value: unknown,
  definition: EnumDefinitionSnapshot,
): TypeScriptTargetBinding => {
  const source = asObject(value);
  if (!exactKeys(source, [
    "schema_version", "binding_id", "definition_ref", "language", "module_path",
    "export_name", "type_name", "member_names", "provider_module_specifier",
    "protocol_ref", "profile_ref", "provider_ref", "emitter_version",
    "emitter_config_digest", "format_version", "binding_sha256", "authority_effect",
  ])) return fail("ARCH_TS_BINDING_SHAPE_INVALID");
  if (source.schema_version !== "TypeScriptTargetBinding/v1" || source.language !== "typescript"
      || source.protocol_ref !== "typescript.owned-const-object-enum/v1"
      || source.format_version !== "typescript-printer/v1") {
    return fail("ARCH_TS_BINDING_SHAPE_INVALID");
  }
  if (source.authority_effect !== "none") return fail("ARCH_TS_BINDING_AUTHORITY_INFLATION");
  const definitionRef = asObject(source.definition_ref);
  if (!exactKeys(definitionRef, ["definition_id", "definition_version", "definition_sha256"])
      || definitionRef.definition_id !== definition.definition_id
      || definitionRef.definition_version !== definition.definition_version
      || definitionRef.definition_sha256 !== definition.definition_sha256) {
    return fail("ARCH_TS_BINDING_DEFINITION_STALE");
  }
  const modulePath = asString(source.module_path, "ARCH_TS_BINDING_PATH_INVALID");
  if (!safeRelativePath(modulePath)) return fail("ARCH_TS_BINDING_PATH_INVALID");
  const providerSpecifier = asString(
    source.provider_module_specifier,
    "ARCH_TS_BINDING_PROVIDER_UNADMITTED",
  );
  if (providerSpecifier !== "../runtime/enum/index.js") {
    return fail("ARCH_TS_BINDING_PROVIDER_UNADMITTED");
  }
  const names = asObject(source.member_names);
  const definitionIds = definition.members.map(({ member_id: memberId }) => memberId)
    .sort(compareUtf8);
  const mappedIds = Object.keys(names).sort(compareUtf8);
  if (mappedIds.length !== definitionIds.length
      || mappedIds.some((identifier, index) => identifier !== definitionIds[index])) {
    return fail("ARCH_TS_BINDING_MEMBER_MAPPING_INCOMPLETE");
  }
  const identifiers = mappedIds.map((memberId) => {
    if (unsafeKeys.has(memberId)) return fail("ARCH_TS_BINDING_KEY_UNSAFE");
    return asString(names[memberId], "ARCH_TS_BINDING_IDENTIFIER_INVALID");
  });
  if (identifiers.some((identifier) => !validIdentifier(identifier))) {
    return fail("ARCH_TS_BINDING_IDENTIFIER_INVALID");
  }
  if (new Set(identifiers).size !== identifiers.length) {
    return fail("ARCH_TS_BINDING_IDENTIFIER_DUPLICATE");
  }
  const profileRef = asObject(source.profile_ref);
  const providerRef = asObject(source.provider_ref);
  if (!exactKeys(profileRef, ["path", "sha256"])
      || !exactKeys(providerRef, ["path", "sha256"]) || !safeRelativePath(asString(profileRef.path))
      || !safeRelativePath(asString(providerRef.path))) {
    return fail("ARCH_TS_BINDING_HANDLE_INVALID");
  }
  for (const digest of [profileRef.sha256, providerRef.sha256, source.emitter_config_digest,
    source.binding_sha256]) {
    if (typeof digest !== "string" || !/^[a-f0-9]{64}$/u.test(digest)) {
      return fail("ARCH_TS_BINDING_DIGEST_INVALID");
    }
  }
  const bindingWithoutDigest = {
    schema_version: "TypeScriptTargetBinding/v1" as const,
    binding_id: asString(source.binding_id),
    definition_ref: {
      definition_id: definition.definition_id,
      definition_version: definition.definition_version,
      definition_sha256: definition.definition_sha256,
    },
    language: "typescript" as const,
    module_path: modulePath,
    export_name: asString(source.export_name, "ARCH_TS_BINDING_IDENTIFIER_INVALID"),
    type_name: asString(source.type_name, "ARCH_TS_BINDING_IDENTIFIER_INVALID"),
    member_names: Object.freeze(Object.fromEntries(mappedIds.map((memberId) => [
      memberId,
      names[memberId] as string,
    ]))),
    provider_module_specifier: providerSpecifier,
    protocol_ref: "typescript.owned-const-object-enum/v1" as const,
    profile_ref: { path: profileRef.path as string, sha256: profileRef.sha256 as string },
    provider_ref: { path: providerRef.path as string, sha256: providerRef.sha256 as string },
    emitter_version: asString(source.emitter_version),
    emitter_config_digest: source.emitter_config_digest as string,
    format_version: "typescript-printer/v1" as const,
    authority_effect: "none" as const,
  };
  if (!validIdentifier(bindingWithoutDigest.export_name)
      || !validIdentifier(bindingWithoutDigest.type_name)) {
    return fail("ARCH_TS_BINDING_IDENTIFIER_INVALID");
  }
  const actual = computeTypeScriptTargetBindingSha256(bindingWithoutDigest);
  if (actual !== source.binding_sha256) return fail("ARCH_TS_BINDING_DIGEST_STALE");
  return Object.freeze({
    ...bindingWithoutDigest,
    binding_sha256: source.binding_sha256 as string,
  });
};
