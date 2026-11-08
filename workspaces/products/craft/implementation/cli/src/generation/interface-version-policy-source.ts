import {decodeInterfaceVersionPolicy, INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from "../typed-backend/interface-version-policy.js";

/** Standalone policy source for composition into the configured Interface emitter.
 * Planning source is not public CLI integration or transport construction. */
export function renderInterfaceVersionPolicy(value: unknown): string {
  const policy = decodeInterfaceVersionPolicy(value);
  const descriptor = {...policy, definition_sha256: INTERFACE_VERSION_POLICY_DEFINITION_SHA256, authority_effect: "none"};
  const body = policy.mode === "exact"
    ? `  return consumerVersion === ${JSON.stringify(policy.provider_version)};\n`
    : `  const consumer = match.slice(1);
  const provider = ${JSON.stringify(policy.provider_version.split("."))};
  if (consumer[0] !== provider[0]) return false;
  for (let index = 1; index < 3; index += 1) {
    const left = provider[index]!, right = consumer[index]!;
    const order = left.length === right.length ? (left === right ? 0 : left > right ? 1 : -1) : left.length > right.length ? 1 : -1;
    if (order !== 0) return order > 0;
  }
  return true;
`;
  return `export const versionPolicy = Object.freeze(${JSON.stringify(descriptor)} as const);
export const acceptsVersion = (consumerVersion: unknown): boolean => {
  if (typeof consumerVersion !== "string" || consumerVersion.length > 194) return false;
  const match = /^(0|[1-9][0-9]{0,63})\\.(0|[1-9][0-9]{0,63})\\.(0|[1-9][0-9]{0,63})$/.exec(consumerVersion);
  if (!match || match[0] !== consumerVersion) return false;
${body}};
`;
}
