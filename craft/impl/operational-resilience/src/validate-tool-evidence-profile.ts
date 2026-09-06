import { createHash } from "node:crypto";

import {
  DEFERRED_TOOL_EVIDENCE_PROFILE_FAMILIES,
  SELECTOR_VALUE_TYPES,
  TOOL_EVIDENCE_PROFILE_FAMILIES,
  type ToolEvidenceProfileAttributePolicy,
  type ToolEvidenceProfileFamilyInventory,
  type ToolEvidenceProfileFinding,
  type ToolEvidenceProfileReferentInventory,
  type ToolEvidenceProfileValidationInputs,
  type ToolEvidenceProfileValidationResult,
} from "../contracts/tool-evidence-profile.js";

type JsonObject = Record<string, unknown>;
type AddFinding = (code: string, path: string, detail: string) => void;

const SHA256 = /^[a-f0-9]{64}$/;
const RFC3339_UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;
const CONTROL_IDS = Object.freeze(
  Array.from({ length: 16 }, (_, index) => `C${String(index + 1).padStart(2, "0")}`),
);
const PROPOSED_CONTROL_IDS = Object.freeze(["C17", "C18", "C19", "C20"]);
const REQUIRED_REFERENT_ROLES = Object.freeze([
  "producer",
  "offline-normalizer",
  "input-schema",
  "output-schema",
  "validation-receipt-schema",
]);
const OCCURRENCE_KEYS = new Set([
  "observation_id",
  "observed_at",
  "effect_occurred",
  "eligible_controls",
  "normalized_output",
  "runtime_eligible",
  "telemetry_count",
  "control_receipt",
]);

function toBytes(value: Uint8Array | string): Uint8Array {
  return typeof value === "string" ? new TextEncoder().encode(value) : value;
}

function digest(value: Uint8Array | string): string {
  return createHash("sha256").update(toBytes(value)).digest("hex");
}

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function sortedUnique(values: readonly string[]): string[] {
  return [...new Set(values)].sort((left, right) => left.localeCompare(right));
}

function sameStringSet(left: readonly string[], right: readonly string[]): boolean {
  const a = sortedUnique(left);
  const b = sortedUnique(right);
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

function validateExactKeys(
  value: unknown,
  required: readonly string[],
  path: string,
  add: AddFinding,
): value is JsonObject {
  if (!isObject(value)) {
    add("PROFILE_SHAPE_INVALID", path, "expected an object");
    return false;
  }
  const allowed = new Set(required);
  for (const key of required) {
    if (!Object.hasOwn(value, key)) {
      add("PROFILE_REQUIRED_FIELD_MISSING", `${path}/${key}`, "required field is absent");
    }
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) {
      add("PROFILE_UNKNOWN_FIELD", `${path}/${key}`, "field is outside the closed contract");
    }
  }
  return true;
}

function validateStringArray(
  value: unknown,
  path: string,
  add: AddFinding,
  options: Readonly<{ nonEmpty?: boolean; unique?: boolean }> = {},
): string[] {
  if (!Array.isArray(value)) {
    add("PROFILE_SHAPE_INVALID", path, "expected an array");
    return [];
  }
  const result: string[] = [];
  for (const [index, item] of value.entries()) {
    if (typeof item !== "string" || item.length === 0) {
      add("PROFILE_SHAPE_INVALID", `${path}/${index}`, "expected a non-empty string");
      continue;
    }
    result.push(item);
  }
  if (options.nonEmpty && result.length === 0) {
    add("PROFILE_REQUIRED_FIELD_MISSING", path, "at least one value is required");
  }
  if (options.unique && new Set(result).size !== result.length) {
    add("PROFILE_DUPLICATE_ARRAY_IDENTITY", path, "array values must be unique");
  }
  return result;
}

function scanForDuplicateObjectKeys(
  text: string,
  rootPath: string,
  add: AddFinding,
): void {
  let cursor = 0;

  const whitespace = (): void => {
    while (/\s/.test(text[cursor] ?? "")) cursor += 1;
  };

  const readString = (): string => {
    const start = cursor;
    cursor += 1;
    while (cursor < text.length) {
      const char = text[cursor];
      if (char === "\\") {
        cursor += 2;
        continue;
      }
      cursor += 1;
      if (char === '"') break;
    }
    return JSON.parse(text.slice(start, cursor)) as string;
  };

  const parseValue = (path: string): void => {
    whitespace();
    const char = text[cursor];
    if (char === "{") {
      cursor += 1;
      whitespace();
      const keys = new Set<string>();
      if (text[cursor] === "}") {
        cursor += 1;
        return;
      }
      while (cursor < text.length) {
        whitespace();
        const key = readString();
        if (keys.has(key)) {
          add(
            "PROFILE_JSON_DUPLICATE_OBJECT_KEY",
            `${path}/${key}`,
            "duplicate object keys are forbidden in exact-byte JSON inputs",
          );
        }
        keys.add(key);
        whitespace();
        cursor += 1;
        parseValue(`${path}/${key.replaceAll("~", "~0").replaceAll("/", "~1")}`);
        whitespace();
        if (text[cursor] === "}") {
          cursor += 1;
          return;
        }
        cursor += 1;
      }
      return;
    }
    if (char === "[") {
      cursor += 1;
      whitespace();
      if (text[cursor] === "]") {
        cursor += 1;
        return;
      }
      let index = 0;
      while (cursor < text.length) {
        parseValue(`${path}/${index}`);
        index += 1;
        whitespace();
        if (text[cursor] === "]") {
          cursor += 1;
          return;
        }
        cursor += 1;
      }
      return;
    }
    if (char === '"') {
      readString();
      return;
    }
    while (cursor < text.length && !/[\s,\]}]/.test(text[cursor] ?? "")) cursor += 1;
  };

  parseValue(rootPath);
}

function parseExactJson(
  input: Uint8Array | string,
  inputName: string,
  add: AddFinding,
): unknown {
  let text: string;
  try {
    text = typeof input === "string"
      ? input
      : new TextDecoder("utf-8", { fatal: true }).decode(input);
  } catch {
    add("PROFILE_JSON_INVALID_UTF8", inputName, "input is not valid UTF-8");
    return undefined;
  }
  try {
    const value = JSON.parse(text) as unknown;
    scanForDuplicateObjectKeys(text, inputName, add);
    return value;
  } catch {
    add("PROFILE_JSON_INVALID", inputName, "input is not one complete JSON value");
    return undefined;
  }
}

function validateTimestamp(value: unknown, path: string, add: AddFinding): number | undefined {
  if (typeof value !== "string" || !RFC3339_UTC.test(value)) {
    add("PROFILE_TIMESTAMP_INVALID", path, "timestamp must be RFC3339 UTC with a Z suffix");
    return undefined;
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    add("PROFILE_TIMESTAMP_INVALID", path, "timestamp is not a real instant");
    return undefined;
  }
  return parsed;
}

function validateDigest(value: unknown, path: string, add: AddFinding): value is string {
  if (typeof value !== "string" || !SHA256.test(value)) {
    add("PROFILE_DIGEST_INVALID", path, "expected a lowercase SHA-256 digest");
    return false;
  }
  return true;
}

function validateDigestRef(value: unknown, path: string, add: AddFinding): value is JsonObject {
  if (!validateExactKeys(value, ["ref", "version", "sha256"], path, add)) return false;
  for (const key of ["ref", "version"] as const) {
    if (typeof value[key] !== "string" || value[key].length === 0) {
      add("PROFILE_SHAPE_INVALID", `${path}/${key}`, "expected a non-empty string");
    }
  }
  validateDigest(value.sha256, `${path}/sha256`, add);
  return true;
}

function occurrenceClaimWalk(value: unknown, path: string, add: AddFinding): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => occurrenceClaimWalk(item, `${path}/${index}`, add));
    return;
  }
  if (!isObject(value)) return;
  for (const [key, item] of Object.entries(value)) {
    if (OCCURRENCE_KEYS.has(key) || key === "telemetry" || key === "live") {
      add(
        "PROFILE_OUTPUT_OCCURRENCE_CLAIM",
        `${path}/${key}`,
        "profile descriptions cannot contain observations, effects, eligibility, or nonzero telemetry claims",
      );
    }
    occurrenceClaimWalk(item, `${path}/${key}`, add);
  }
}

function validateSelector(selector: unknown, path: string, add: AddFinding): string[] | undefined {
  if (typeof selector !== "string" || !selector.startsWith("/")) {
    add("PROFILE_SELECTOR_INVALID", path, "selector must be an absolute JSON Pointer");
    return undefined;
  }
  if (
    selector.includes("#") ||
    selector.includes("*") ||
    selector.includes("..") ||
    selector.includes("//") ||
    selector.includes("[") ||
    selector.includes("]") ||
    selector.includes("?")
  ) {
    add("PROFILE_SELECTOR_DISCOVERY_FORBIDDEN", path, "selector discovery and traversal syntax is forbidden");
    return undefined;
  }
  const result: string[] = [];
  for (const token of selector.slice(1).split("/")) {
    if (token.length === 0 || /~(?![01])/u.test(token)) {
      add("PROFILE_SELECTOR_INVALID", path, "selector contains an invalid JSON Pointer token");
      return undefined;
    }
    result.push(token.replaceAll("~1", "/").replaceAll("~0", "~"));
  }
  return result;
}

function resolveSelector(value: unknown, tokens: readonly string[]): unknown {
  let current = value;
  for (const token of tokens) {
    if (Array.isArray(current)) {
      if (!/^(0|[1-9]\d*)$/.test(token)) return undefined;
      current = current[Number(token)];
      continue;
    }
    if (!isObject(current) || !Object.hasOwn(current, token)) return undefined;
    current = current[token];
  }
  return current;
}

function jsonValueType(value: unknown): string {
  if (Array.isArray(value)) return "array";
  if (value === null) return "null";
  return typeof value === "object" ? "object" : typeof value;
}

function validateTopLevelDescriptor(descriptor: unknown, add: AddFinding): descriptor is JsonObject {
  return validateExactKeys(
    descriptor,
    [
      "schema_version", "profile_id", "profile_version", "status", "family_id",
      "family_inventory_ref", "attribute_policy_ref", "producer", "normalizer", "mapping",
      "admitted_control_refs", "proposed_control_refs", "created_at", "expires_at",
      "invalidation_key_digest", "execution_mode", "runtime_admission", "authority_effect",
    ],
    "/descriptor",
    add,
  );
}

export function validateToolEvidenceProfile(
  inputs: ToolEvidenceProfileValidationInputs,
): ToolEvidenceProfileValidationResult {
  const findings: ToolEvidenceProfileFinding[] = [];
  const add: AddFinding = (code, path, detail) => findings.push({ code, path, detail });
  const hashes = {
    descriptor: digest(inputs.descriptor),
    family: digest(inputs.family_inventory),
    policy: digest(inputs.attribute_policy),
    referents: digest(inputs.referent_inventory),
  };

  const descriptor = parseExactJson(inputs.descriptor, "/descriptor", add);
  const familyInventory = parseExactJson(inputs.family_inventory, "/family_inventory", add);
  const policy = parseExactJson(inputs.attribute_policy, "/attribute_policy", add);
  const referentInventory = parseExactJson(inputs.referent_inventory, "/referent_inventory", add);
  const evaluatedAt = validateTimestamp(inputs.evaluated_at, "/evaluated_at", add);

  occurrenceClaimWalk(descriptor, "/descriptor", add);

  let familyRows: JsonObject[] = [];
  if (
    validateExactKeys(
      familyInventory,
      ["schema_version", "inventory_id", "inventory_version", "valid_families", "deferred_extensions", "authority_effect"],
      "/family_inventory",
      add,
    )
  ) {
    if (familyInventory.schema_version !== "domainspec.orodi.tool-evidence-profile-family-inventory/v1") {
      add("PROFILE_FAMILY_INVENTORY_IDENTITY_MISMATCH", "/family_inventory/schema_version", "unexpected family inventory schema version");
    }
    if (familyInventory.inventory_id !== "domainspec.orodi.tool-evidence-profile-families" || familyInventory.inventory_version !== "1.0.0-candidate-local") {
      add("PROFILE_FAMILY_INVENTORY_IDENTITY_MISMATCH", "/family_inventory", "family inventory identity is not the admitted candidate-local identity");
    }
    if (familyInventory.authority_effect !== "none") {
      add("PROFILE_AUTHORITY_EXPANSION", "/family_inventory/authority_effect", "inventory authority effect must remain none");
    }
    if (Array.isArray(familyInventory.valid_families)) {
      familyRows = familyInventory.valid_families.filter(isObject);
      const ids = familyRows.map((row) => stringValue(row.family_id) ?? "");
      if (new Set(ids).size !== ids.length) {
        add("PROFILE_DUPLICATE_ARRAY_IDENTITY", "/family_inventory/valid_families", "family identities must be unique");
      }
      if (!sameStringSet(ids, TOOL_EVIDENCE_PROFILE_FAMILIES)) {
        add("PROFILE_FAMILY_INVENTORY_NOT_CLOSED", "/family_inventory/valid_families", "inventory must contain exactly the seven admitted families");
      }
      familyRows.forEach((row, index) => {
        const path = `/family_inventory/valid_families/${index}`;
        validateExactKeys(row, ["family_id", "allowed_normalized_kinds", "required_safeguards", "required_referent_roles", "attribute_policy_sha256"], path, add);
        validateStringArray(row.allowed_normalized_kinds, `${path}/allowed_normalized_kinds`, add, { nonEmpty: true, unique: true });
        validateStringArray(row.required_safeguards, `${path}/required_safeguards`, add, { nonEmpty: true, unique: true });
        const roles = validateStringArray(row.required_referent_roles, `${path}/required_referent_roles`, add, { nonEmpty: true, unique: true });
        if (!sameStringSet(roles, REQUIRED_REFERENT_ROLES)) {
          add("PROFILE_REFERENT_ROLE_SET_MISMATCH", `${path}/required_referent_roles`, "each family must require the closed five-role referent set");
        }
        if (row.attribute_policy_sha256 !== hashes.policy) {
          add("PROFILE_ATTRIBUTE_POLICY_DIGEST_MISMATCH", `${path}/attribute_policy_sha256`, "family row is not bound to the exact attribute policy bytes");
        }
      });
    } else {
      add("PROFILE_SHAPE_INVALID", "/family_inventory/valid_families", "expected an array");
    }
    const deferred = validateStringArray(familyInventory.deferred_extensions, "/family_inventory/deferred_extensions", add, { unique: true });
    if (!sameStringSet(deferred, DEFERRED_TOOL_EVIDENCE_PROFILE_FAMILIES)) {
      add("PROFILE_DEFERRED_EXTENSION_SET_MISMATCH", "/family_inventory/deferred_extensions", "deferred family set is closed");
    }
  }

  let policyObject: ToolEvidenceProfileAttributePolicy | undefined;
  if (
    validateExactKeys(
      policy,
      ["schema_version", "policy_id", "policy_version", "allowed_normalized_keys", "forbidden_exact_keys", "forbidden_prefixes", "max_key_bytes", "max_value_bytes", "max_attribute_count", "wildcards_allowed", "authority_effect"],
      "/attribute_policy",
      add,
    )
  ) {
    policyObject = policy as ToolEvidenceProfileAttributePolicy;
    if (policy.schema_version !== "domainspec.orodi.tool-evidence-profile-attribute-policy/v1" || policy.policy_id !== "domainspec.orodi.tool-evidence-profile-attributes" || policy.policy_version !== "1.0.0-candidate-local") {
      add("PROFILE_ATTRIBUTE_POLICY_IDENTITY_MISMATCH", "/attribute_policy", "unexpected attribute policy identity");
    }
    if (policy.wildcards_allowed !== false) {
      add("PROFILE_ATTRIBUTE_WILDCARD_FORBIDDEN", "/attribute_policy/wildcards_allowed", "attribute wildcards must remain disabled");
    }
    if (policy.authority_effect !== "none") {
      add("PROFILE_AUTHORITY_EXPANSION", "/attribute_policy/authority_effect", "policy authority effect must remain none");
    }
    for (const key of ["allowed_normalized_keys", "forbidden_exact_keys", "forbidden_prefixes"] as const) {
      validateStringArray(policy[key], `/attribute_policy/${key}`, add, { nonEmpty: true, unique: true });
    }
    for (const key of ["max_key_bytes", "max_value_bytes", "max_attribute_count"] as const) {
      if (!Number.isInteger(policy[key]) || Number(policy[key]) < 1) {
        add("PROFILE_ATTRIBUTE_POLICY_INVALID", `/attribute_policy/${key}`, "limit must be a positive integer");
      }
    }
  }

  let referentRows: JsonObject[] = [];
  if (
    validateExactKeys(
      referentInventory,
      ["schema_version", "inventory_id", "inventory_version", "referents", "authority_effect"],
      "/referent_inventory",
      add,
    )
  ) {
    if (referentInventory.schema_version !== "domainspec.orodi.tool-evidence-profile-referent-inventory/v1") {
      add("PROFILE_REFERENT_INVENTORY_IDENTITY_MISMATCH", "/referent_inventory/schema_version", "unexpected referent inventory schema version");
    }
    if (referentInventory.authority_effect !== "none") {
      add("PROFILE_AUTHORITY_EXPANSION", "/referent_inventory/authority_effect", "referent inventory authority effect must remain none");
    }
    if (Array.isArray(referentInventory.referents)) {
      referentRows = referentInventory.referents.filter(isObject);
      const refs = referentRows.map((row) => stringValue(row.ref) ?? "");
      if (new Set(refs).size !== refs.length) {
        add("PROFILE_DUPLICATE_ARRAY_IDENTITY", "/referent_inventory/referents", "referent identities must be unique");
      }
      referentRows.forEach((row, index) => {
        const path = `/referent_inventory/referents/${index}`;
        validateExactKeys(row, ["ref", "role", "name", "version", "sha256", "bytes_utf8"], path, add);
        for (const key of ["ref", "role", "name", "version", "bytes_utf8"] as const) {
          if (typeof row[key] !== "string" || (key !== "bytes_utf8" && row[key].length === 0)) {
            add("PROFILE_SHAPE_INVALID", `${path}/${key}`, "expected a string value");
          }
        }
        if (validateDigest(row.sha256, `${path}/sha256`, add) && typeof row.bytes_utf8 === "string" && row.sha256 !== digest(row.bytes_utf8)) {
          add("PROFILE_REFERENT_DIGEST_MISMATCH", `${path}/sha256`, "referent digest does not match exact bytes_utf8");
        }
      });
    } else {
      add("PROFILE_SHAPE_INVALID", "/referent_inventory/referents", "expected an array");
    }
  }

  const findReferent = (ref: unknown): JsonObject | undefined =>
    typeof ref === "string" ? referentRows.find((row) => row.ref === ref) : undefined;

  const checkBoundReferent = (
    reference: unknown,
    path: string,
    expectedRole: string,
  ): JsonObject | undefined => {
    if (!validateDigestRef(reference, path, add)) return undefined;
    const row = findReferent(reference.ref);
    if (!row) {
      add("PROFILE_REFERENT_MISSING", path, "referent is absent from the caller-resolved inventory");
      return undefined;
    }
    if (row.role !== expectedRole) {
      add("PROFILE_REFERENT_ROLE_MISMATCH", `${path}/role`, `referent must have role ${expectedRole}`);
    }
    if (row.version !== reference.version) {
      add("PROFILE_REFERENT_VERSION_MISMATCH", `${path}/version`, "referent version does not match inventory row");
    }
    if (row.sha256 !== reference.sha256) {
      add("PROFILE_REFERENT_DIGEST_MISMATCH", `${path}/sha256`, "referent digest does not match inventory row");
    }
    return row;
  };

  if (validateTopLevelDescriptor(descriptor, add)) {
    if (descriptor.schema_version !== "domainspec.orodi.tool-evidence-profile/v1") {
      add("PROFILE_IDENTITY_MISMATCH", "/descriptor/schema_version", "unexpected profile schema version");
    }
    for (const key of ["profile_id", "profile_version"] as const) {
      if (typeof descriptor[key] !== "string" || descriptor[key].length === 0) {
        add("PROFILE_IDENTITY_MISMATCH", `/descriptor/${key}`, "profile identity fields must be non-empty strings");
      }
    }
    if (descriptor.status !== "candidate-local" || descriptor.execution_mode !== "offline-fixture-only") {
      add("PROFILE_EXECUTION_MODE_INVALID", "/descriptor/execution_mode", "only candidate-local offline fixture validation is allowed");
    }
    if (descriptor.runtime_admission !== "denied") {
      add("PROFILE_RUNTIME_ADMISSION_FORBIDDEN", "/descriptor/runtime_admission", "runtime admission is always denied");
    }
    if (descriptor.authority_effect !== "none") {
      add("PROFILE_AUTHORITY_EXPANSION", "/descriptor/authority_effect", "profile authority effect must remain none");
    }
    validateDigest(descriptor.invalidation_key_digest, "/descriptor/invalidation_key_digest", add);

    const createdAt = validateTimestamp(descriptor.created_at, "/descriptor/created_at", add);
    const expiresAt = validateTimestamp(descriptor.expires_at, "/descriptor/expires_at", add);
    if (createdAt !== undefined && expiresAt !== undefined && createdAt >= expiresAt) {
      add("PROFILE_TIME_WINDOW_INVALID", "/descriptor/expires_at", "expires_at must be later than created_at");
    }
    if (evaluatedAt !== undefined && createdAt !== undefined && evaluatedAt < createdAt) {
      add("PROFILE_BINDING_NOT_YET_VALID", "/evaluated_at", "evaluation precedes profile creation");
    }
    if (evaluatedAt !== undefined && expiresAt !== undefined && evaluatedAt >= expiresAt) {
      add("PROFILE_BINDING_EXPIRED", "/descriptor/expires_at", "profile is expired at or before the evaluation instant");
    }

    if (validateDigestRef(descriptor.family_inventory_ref, "/descriptor/family_inventory_ref", add)) {
      if (descriptor.family_inventory_ref.sha256 !== hashes.family) {
        add("PROFILE_FAMILY_INVENTORY_DIGEST_MISMATCH", "/descriptor/family_inventory_ref/sha256", "profile is not bound to exact family inventory bytes");
      }
      if (descriptor.family_inventory_ref.ref !== "domainspec.orodi.tool-evidence-profile-families" || descriptor.family_inventory_ref.version !== "1.0.0-candidate-local") {
        add("PROFILE_FAMILY_INVENTORY_IDENTITY_MISMATCH", "/descriptor/family_inventory_ref", "unexpected family inventory reference");
      }
    }
    if (validateDigestRef(descriptor.attribute_policy_ref, "/descriptor/attribute_policy_ref", add)) {
      if (descriptor.attribute_policy_ref.sha256 !== hashes.policy) {
        add("PROFILE_ATTRIBUTE_POLICY_DIGEST_MISMATCH", "/descriptor/attribute_policy_ref/sha256", "profile is not bound to exact attribute policy bytes");
      }
      if (descriptor.attribute_policy_ref.ref !== "domainspec.orodi.tool-evidence-profile-attributes" || descriptor.attribute_policy_ref.version !== "1.0.0-candidate-local") {
        add("PROFILE_ATTRIBUTE_POLICY_IDENTITY_MISMATCH", "/descriptor/attribute_policy_ref", "unexpected attribute policy reference");
      }
    }

    const familyId = stringValue(descriptor.family_id) ?? "";
    if ((DEFERRED_TOOL_EVIDENCE_PROFILE_FAMILIES as readonly string[]).includes(familyId)) {
      add("PROFILE_FAMILY_DEFERRED_EXTENSION", "/descriptor/family_id", "family is explicitly deferred and unadmitted");
    } else if (!(TOOL_EVIDENCE_PROFILE_FAMILIES as readonly string[]).includes(familyId)) {
      add("PROFILE_FAMILY_UNKNOWN", "/descriptor/family_id", "family is outside the closed seven-family inventory");
    }
    const familyRow = familyRows.find((row) => row.family_id === familyId);
    if (!familyRow && (TOOL_EVIDENCE_PROFILE_FAMILIES as readonly string[]).includes(familyId)) {
      add("PROFILE_FAMILY_NOT_IN_INVENTORY", "/descriptor/family_id", "family is not present in the supplied inventory");
    }

    let producerRow: JsonObject | undefined;
    if (validateExactKeys(descriptor.producer, ["ref", "version", "sha256", "role"], "/descriptor/producer", add)) {
      if (descriptor.producer.role !== "producer") {
        add("PROFILE_REFERENT_ROLE_MISMATCH", "/descriptor/producer/role", "producer role must be producer");
      }
      producerRow = checkBoundReferent(
        { ref: descriptor.producer.ref, version: descriptor.producer.version, sha256: descriptor.producer.sha256 },
        "/descriptor/producer",
        "producer",
      );
    }

    if (
      validateExactKeys(
        descriptor.normalizer,
        ["ref", "version", "sha256", "role", "execution_mode", "input_schema_ref", "output_schema_ref", "validation_receipt_schema_ref"],
        "/descriptor/normalizer",
        add,
      )
    ) {
      if (descriptor.normalizer.role !== "offline-normalizer" || descriptor.normalizer.execution_mode !== "offline-fixture-only") {
        add("PROFILE_NORMALIZER_ROLE_INVALID", "/descriptor/normalizer", "normalizer must remain a distinct offline-normalizer");
      }
      if (isObject(descriptor.producer) && descriptor.producer.ref === descriptor.normalizer.ref) {
        add("PROFILE_PRODUCER_NORMALIZER_ROLE_COLLAPSE", "/descriptor/normalizer/ref", "producer and normalizer must be different referents");
      }
      checkBoundReferent(
        { ref: descriptor.normalizer.ref, version: descriptor.normalizer.version, sha256: descriptor.normalizer.sha256 },
        "/descriptor/normalizer",
        "offline-normalizer",
      );
      checkBoundReferent(descriptor.normalizer.input_schema_ref, "/descriptor/normalizer/input_schema_ref", "input-schema");
      checkBoundReferent(descriptor.normalizer.output_schema_ref, "/descriptor/normalizer/output_schema_ref", "output-schema");
      checkBoundReferent(descriptor.normalizer.validation_receipt_schema_ref, "/descriptor/normalizer/validation_receipt_schema_ref", "validation-receipt-schema");
    }

    const admitted = validateStringArray(descriptor.admitted_control_refs, "/descriptor/admitted_control_refs", add, { unique: true });
    if (!sameStringSet(admitted, CONTROL_IDS)) {
      add("PROFILE_ADMITTED_CONTROL_SET_MISMATCH", "/descriptor/admitted_control_refs", "admitted controls must be exactly C01 through C16");
    }
    if (admitted.some((control) => PROPOSED_CONTROL_IDS.includes(control))) {
      add("PROFILE_PROPOSED_CONTROL_NOT_ADMITTED", "/descriptor/admitted_control_refs", "C17-C20 remain proposed and cannot be admitted");
    }

    if (!Array.isArray(descriptor.proposed_control_refs)) {
      add("PROFILE_SHAPE_INVALID", "/descriptor/proposed_control_refs", "expected an array");
    } else {
      const proposedIds: string[] = [];
      descriptor.proposed_control_refs.forEach((item, index) => {
        const path = `/descriptor/proposed_control_refs/${index}`;
        if (!validateExactKeys(item, ["control_id", "catalog_ref"], path, add)) return;
        if (typeof item.control_id === "string") proposedIds.push(item.control_id);
        if (!PROPOSED_CONTROL_IDS.includes(String(item.control_id))) {
          add("PROFILE_PROPOSED_CONTROL_ID_INVALID", `${path}/control_id`, "only C17-C20 may appear in the proposed set");
        }
        checkBoundReferent(item.catalog_ref, `${path}/catalog_ref`, "proposed-control-catalog");
      });
      if (new Set(proposedIds).size !== proposedIds.length) {
        add("PROFILE_DUPLICATE_ARRAY_IDENTITY", "/descriptor/proposed_control_refs", "proposed control identities must be unique");
      }
    }

    if (
      validateExactKeys(
        descriptor.mapping,
        ["selector", "selector_value_type", "normalized_kind", "required_source_fields", "required_attributes", "attribute_value_templates", "output_constraints", "missing_data_behavior", "error_map", "family_requirements"],
        "/descriptor/mapping",
        add,
      )
    ) {
      const mapping = descriptor.mapping;
      const selector = validateSelector(mapping.selector, "/descriptor/mapping/selector", add);
      if (!(SELECTOR_VALUE_TYPES as readonly unknown[]).includes(mapping.selector_value_type)) {
        add("PROFILE_SELECTOR_TYPE_INVALID", "/descriptor/mapping/selector_value_type", "unsupported selector value type");
      }
      if (producerRow && typeof producerRow.bytes_utf8 === "string" && selector) {
        let producerValue: unknown;
        try {
          producerValue = JSON.parse(producerRow.bytes_utf8) as unknown;
        } catch {
          add("PROFILE_PRODUCER_BYTES_INVALID", "/referent_inventory/referents", "producer bytes are not JSON");
        }
        if (isObject(producerValue) && producerValue.source !== "offline-fixture") {
          add("PROFILE_PRODUCT_EVIDENCE_SUBSTITUTION", "/referent_inventory/referents", "configuration or workflow telemetry cannot substitute for product evidence");
        }
        const selected = resolveSelector(producerValue, selector);
        if (selected === undefined) {
          add("PROFILE_SELECTOR_MISSING", "/descriptor/mapping/selector", "selector resolves to no value in exact producer bytes");
        } else if (jsonValueType(selected) !== mapping.selector_value_type) {
          add("PROFILE_SELECTOR_TYPE_MISMATCH", "/descriptor/mapping/selector_value_type", "resolved value has a different JSON type");
        }
      }

      validateStringArray(mapping.required_source_fields, "/descriptor/mapping/required_source_fields", add, { nonEmpty: true, unique: true });
      const requiredAttributes = validateStringArray(mapping.required_attributes, "/descriptor/mapping/required_attributes", add, { nonEmpty: true, unique: true });
      const familyRequirements = validateStringArray(mapping.family_requirements, "/descriptor/mapping/family_requirements", add, { nonEmpty: true, unique: true });
      if (familyRow) {
        const allowedKinds = validateStringArray(familyRow.allowed_normalized_kinds, "/family_inventory/allowed_normalized_kinds", add);
        if (!allowedKinds.includes(String(mapping.normalized_kind))) {
          add("PROFILE_NORMALIZED_KIND_NOT_ADMITTED", "/descriptor/mapping/normalized_kind", "normalized kind is not admitted for the selected family");
        }
        const safeguards = validateStringArray(familyRow.required_safeguards, "/family_inventory/required_safeguards", add);
        if (!sameStringSet(familyRequirements, safeguards)) {
          add("PROFILE_FAMILY_REQUIREMENT_SET_MISMATCH", "/descriptor/mapping/family_requirements", "family safeguards must be complete and exact");
        }
        if (familyId === "workload" && !familyRequirements.includes("thresholds-enabled")) {
          add("PROFILE_WORKLOAD_THRESHOLD_REQUIRED", "/descriptor/mapping/family_requirements", "workload thresholds cannot be disabled or omitted");
        }
        if (familyId === "workload" && !familyRequirements.includes("generator-saturation-behavior")) {
          add("PROFILE_GENERATOR_SATURATION_BEHAVIOR_REQUIRED", "/descriptor/mapping/family_requirements", "generator saturation behavior is required");
        }
      }
      if (mapping.missing_data_behavior !== "reject") {
        add("PROFILE_MISSING_DATA_BEHAVIOR_REQUIRED", "/descriptor/mapping/missing_data_behavior", "missing data must reject");
      }
      if (!Array.isArray(mapping.error_map) || mapping.error_map.length === 0) {
        add("PROFILE_ERROR_MAP_REQUIRED", "/descriptor/mapping/error_map", "a non-empty error map is required");
      } else {
        mapping.error_map.forEach((entry, index) => {
          const path = `/descriptor/mapping/error_map/${index}`;
          if (validateExactKeys(entry, ["condition", "code"], path, add)) {
            if (typeof entry.condition !== "string" || entry.condition.length === 0 || typeof entry.code !== "string" || !/^[A-Z][A-Z0-9_]+$/.test(entry.code)) {
              add("PROFILE_ERROR_MAP_INVALID", path, "error map entries require a condition and stable code");
            }
          }
        });
      }

      if (!isObject(mapping.attribute_value_templates)) {
        add("PROFILE_ATTRIBUTE_TEMPLATE_INVALID", "/descriptor/mapping/attribute_value_templates", "expected a closed string map");
      } else if (policyObject) {
        const templateKeys = Object.keys(mapping.attribute_value_templates);
        if (!sameStringSet(templateKeys, requiredAttributes)) {
          add("PROFILE_ATTRIBUTE_TEMPLATE_SET_MISMATCH", "/descriptor/mapping/attribute_value_templates", "attribute templates must match required attributes exactly");
        }
        if (requiredAttributes.length > policyObject.max_attribute_count) {
          add("PROFILE_ATTRIBUTE_CARDINALITY_EXCEEDED", "/descriptor/mapping/required_attributes", "attribute count exceeds policy maximum");
        }
        for (const [key, value] of Object.entries(mapping.attribute_value_templates)) {
          const keyBytes = new TextEncoder().encode(key).length;
          const valueBytes = typeof value === "string" ? new TextEncoder().encode(value).length : Number.POSITIVE_INFINITY;
          if (keyBytes > policyObject.max_key_bytes) {
            add("PROFILE_ATTRIBUTE_KEY_TOO_LARGE", `/descriptor/mapping/attribute_value_templates/${key}`, "attribute key exceeds byte limit");
          }
          if (valueBytes > policyObject.max_value_bytes) {
            add("PROFILE_ATTRIBUTE_VALUE_TOO_LARGE", `/descriptor/mapping/attribute_value_templates/${key}`, "attribute value exceeds byte limit");
          }
          if (key.includes("*") || key.includes("?")) {
            add("PROFILE_ATTRIBUTE_WILDCARD_FORBIDDEN", `/descriptor/mapping/attribute_value_templates/${key}`, "attribute wildcard syntax is forbidden");
          }
          if (policyObject.forbidden_exact_keys.includes(key) || policyObject.forbidden_prefixes.some((prefix) => key.startsWith(prefix))) {
            add("PROFILE_ATTRIBUTE_SECRET_KEY_FORBIDDEN", `/descriptor/mapping/attribute_value_templates/${key}`, "secret, token, credential, and authorization keys are forbidden");
          }
          if (!policyObject.allowed_normalized_keys.includes(key)) {
            add("PROFILE_ATTRIBUTE_KEY_NOT_ALLOWED", `/descriptor/mapping/attribute_value_templates/${key}`, "attribute key is outside the allowlist");
          }
        }
      }

      if (
        validateExactKeys(
          mapping.output_constraints,
          ["plane", "mode", "allowed_normalized_fields", "cardinality_budget", "telemetry_accounting_required", "independently_observed_required", "deployment_effect_allowed"],
          "/descriptor/mapping/output_constraints",
          add,
        )
      ) {
        const output = mapping.output_constraints;
        if (output.plane !== "product" || !["simulation", "observation"].includes(String(output.mode))) {
          add("PROFILE_OUTPUT_PLANE_INVALID", "/descriptor/mapping/output_constraints", "output must be a product-plane simulation or observation description");
        }
        const allowedFields = validateStringArray(output.allowed_normalized_fields, "/descriptor/mapping/output_constraints/allowed_normalized_fields", add, { nonEmpty: true, unique: true });
        if (allowedFields.some((field) => OCCURRENCE_KEYS.has(field) || field === "telemetry")) {
          add("PROFILE_OUTPUT_OCCURRENCE_CLAIM", "/descriptor/mapping/output_constraints/allowed_normalized_fields", "observation and effect occurrence fields are forbidden");
        }
        if (!Number.isInteger(output.cardinality_budget) || Number(output.cardinality_budget) < 1 || (policyObject && Number(output.cardinality_budget) > policyObject.max_attribute_count)) {
          add("PROFILE_ATTRIBUTE_CARDINALITY_EXCEEDED", "/descriptor/mapping/output_constraints/cardinality_budget", "cardinality budget must be positive and within policy");
        }
        if (familyId === "telemetry" && output.telemetry_accounting_required !== true) {
          add("PROFILE_TELEMETRY_ACCOUNTING_REQUIRED", "/descriptor/mapping/output_constraints/telemetry_accounting_required", "telemetry profiles must require accounting");
        }
        if (["deployment-observation", "rollback-observation"].includes(familyId)) {
          if (output.independently_observed_required !== true || output.mode !== "observation") {
            add("PROFILE_INDEPENDENT_OBSERVATION_REQUIRED", "/descriptor/mapping/output_constraints", "deployment and rollback descriptions must require independent observation");
          }
        } else if (output.deployment_effect_allowed !== false) {
          add("PROFILE_DEPLOYMENT_EFFECT_FORBIDDEN", "/descriptor/mapping/output_constraints/deployment_effect_allowed", "non-deployment families cannot describe deployment effects");
        }
      }
    }
  }

  const normalizedFindings = [...new Map(
    findings
      .sort((left, right) => `${left.path}\u0000${left.code}\u0000${left.detail}`.localeCompare(`${right.path}\u0000${right.code}\u0000${right.detail}`))
      .map((finding) => [`${finding.path}\u0000${finding.code}\u0000${finding.detail}`, finding]),
  ).values()];
  const valid = normalizedFindings.length === 0;
  const descriptorObject = isObject(descriptor) ? descriptor : {};

  return {
    schema_version: "domainspec.orodi.tool-evidence-profile-validation-result/v1",
    validator_id: "domainspec.orodi.tool-evidence-profile-validator",
    validator_version: "1.0.0-candidate-local",
    profile_id: stringValue(descriptorObject.profile_id) ?? "",
    profile_version: stringValue(descriptorObject.profile_version) ?? "",
    family_id: stringValue(descriptorObject.family_id) ?? "",
    descriptor_sha256: hashes.descriptor,
    family_inventory_sha256: hashes.family,
    attribute_policy_sha256: hashes.policy,
    referent_inventory_sha256: hashes.referents,
    evaluated_at: inputs.evaluated_at,
    verdict: valid ? "pass" : "reject",
    profile_state: valid ? "structurally-valid" : "rejected",
    runtime_admission: "denied",
    referent_trust: "unverified",
    findings: normalizedFindings,
    authority_effect: "none",
  };
}

export type {
  ToolEvidenceProfileFamilyInventory,
  ToolEvidenceProfileReferentInventory,
};
