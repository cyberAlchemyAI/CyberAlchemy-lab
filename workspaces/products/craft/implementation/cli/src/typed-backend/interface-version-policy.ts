export const INTERFACE_VERSION_POLICY_SCHEMA = "domainspec.interface-version-policy/v1" as const;
export const INTERFACE_VERSION_POLICY_DEFINITION_SHA256 = "15f8132055336ba19d64fb0bee59d8f8bc711600ab1aa159116d5a03d65d6526";

export interface InterfaceVersionPolicy {
  readonly schema_version: typeof INTERFACE_VERSION_POLICY_SCHEMA;
  readonly mode: "exact" | "backward";
  readonly direction: "consumer-to-provider";
  readonly provider_version: string;
}

const versionPattern = /^(0|[1-9][0-9]{0,63})\.(0|[1-9][0-9]{0,63})\.(0|[1-9][0-9]{0,63})$/;
type Parts = readonly [string, string, string];

function parts(value: unknown): Parts | null {
  if (typeof value !== "string" || value.length > 194) return null;
  const match = versionPattern.exec(value);
  if (!match || match[0] !== value) return null;
  return [match[1]!, match[2]!, match[3]!];
}

function fail(reason: string): never {
  throw Object.assign(new TypeError(`MTCLI_INTERFACE_VERSION_POLICY: ${reason}`), {
    code: "MTCLI_INTERFACE_VERSION_POLICY",
  });
}

/** Closed inert data, not a sandbox against arbitrary Proxy traps. */
export function decodeInterfaceVersionPolicy(value: unknown): InterfaceVersionPolicy {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("ordinary policy object required");
  const prototype = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) fail("ordinary policy object required");
  const descriptors = Object.getOwnPropertyDescriptors(value);
  const keys = ["schema_version", "mode", "direction", "provider_version"] as const;
  if (Reflect.ownKeys(descriptors).length !== keys.length) fail("exact policy fields required");
  for (const key of keys) {
    const descriptor = descriptors[key];
    if (!descriptor || !Object.hasOwn(descriptor, "value") || !descriptor.enumerable) fail("data fields required");
  }
  const schema_version: unknown = descriptors.schema_version!.value;
  const mode: unknown = descriptors.mode!.value;
  const direction: unknown = descriptors.direction!.value;
  const provider_version: unknown = descriptors.provider_version!.value;
  if (schema_version !== INTERFACE_VERSION_POLICY_SCHEMA) fail("unsupported schema");
  if (mode !== "exact" && mode !== "backward") fail("unsupported mode");
  if (direction !== "consumer-to-provider") fail("unsupported direction");
  if (parts(provider_version) === null) fail("canonical three-part provider version required");
  return Object.freeze({schema_version, mode, direction, provider_version: provider_version as string});
}

/** Version eligibility only; no request/result shape or execution guarantee. */
export function acceptsInterfaceVersion(policy: InterfaceVersionPolicy, consumerVersion: unknown): boolean {
  const checked = decodeInterfaceVersionPolicy(policy);
  const consumer = parts(consumerVersion);
  if (consumer === null) return false;
  if (checked.mode === "exact") return consumerVersion === checked.provider_version;
  const provider = parts(checked.provider_version)!;
  if (provider[0] !== consumer[0]) return false;
  for (const index of [1, 2] as const) {
    const left = provider[index], right = consumer[index];
    if (left.length !== right.length) return left.length > right.length;
    if (left !== right) return left > right;
  }
  return true;
}
