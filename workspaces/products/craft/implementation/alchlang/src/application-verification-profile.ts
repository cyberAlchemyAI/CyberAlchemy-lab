import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { lowerApplicationFormalClaims, resolveExactFormalSource, type ExactFormalSourceRef } from "./formal-claim-lowering.js";
import { parseDomainSource } from "./parser.js";
import type { ApplicationFormalSource, ApplicationSourceSection } from "./formal-claim.js";

export interface ApplicationVerificationRuntimeBounds {
  timeout_ms: number;
  memory_ceiling_bytes: number;
  max_output_bytes: number;
  network: "forbidden";
  working_directory: string;
  environment_allowlist: string[];
}

export interface ApplicationVerificationProfile {
  id: string;
  source_line: number;
  claim_ref: string;
  context_id: string;
  context_version: string;
  interpretation_selector: string | null;
  route_selector: string;
  provider_selector: string;
  runtime_selector: string;
  assumptions: string[];
  limits: string[];
  runtime_bounds: ApplicationVerificationRuntimeBounds;
  ceiling: string;
}

type JsonObject = Record<string, unknown>;
type SelectedExactRef = { selector: string; ref: ExactFormalSourceRef };
export interface ApplicationVerificationProfileBinding {
  interpretation: SelectedExactRef | null;
  route: SelectedExactRef;
  provider: SelectedExactRef;
  runtime: SelectedExactRef;
}

const fail = (code: string, where: string | number, message: string): never => {
  throw new CompilationRejected([{ code, path: typeof where === "number" ? `$line:${where}` : where, message }]);
};
const relativeDirectory = /^(?!\/)(?!.*(?:^|\/)\.\.?(?:\/|$))[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/;
const environmentName = /^[A-Z][A-Z0-9_]*$/;
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as JsonObject)[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const object = (value: unknown, where: string): JsonObject => {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_VERIFICATION_BINDING", where, "expected object");
  return value as JsonObject;
};
const exactKeys = (value: unknown, keys: string[], where: string): JsonObject => {
  const result = object(value, where);
  if (canonical(Object.keys(result).sort()) !== canonical([...keys].sort())) fail("APPLICATION_VERIFICATION_BINDING", where, "unexpected or missing property");
  return result;
};
const quoted = (source: string, line: number): string => {
  try {
    const value: unknown = JSON.parse(source);
    if (typeof value !== "string" || !value.trim()) return fail("APPLICATION_VERIFICATION_SYNTAX", line, "expected nonempty quoted text");
    return value;
  } catch {
    return fail("APPLICATION_VERIFICATION_SYNTAX", line, "expected valid quoted text");
  }
};
const boundedInteger = (source: string, line: number, field: string): number => {
  if (!/^[1-9][0-9]*$/.test(source)) fail("APPLICATION_VERIFICATION_BOUND", line, `${field} must be a positive integer`);
  const value = Number(source);
  if (!Number.isSafeInteger(value)) fail("APPLICATION_VERIFICATION_BOUND", line, `${field} exceeds the safe integer range`);
  return value;
};

/** Verification profiles select evaluation inputs. They never evaluate or mutate a FormalClaim. */
export function normalizeApplicationVerificationProfiles(
  sections: ApplicationSourceSection[],
  claimIds: ReadonlySet<string>,
): ApplicationVerificationProfile[] {
  const contextIds = new Set<string>();
  return sections.map(section => {
    let claimRef: string | undefined; let contextId: string | undefined; let contextVersion: string | undefined;
    let interpretationSelector: string | null | undefined; let routeSelector: string | undefined;
    let providerSelector: string | undefined; let runtimeSelector: string | undefined; let ceiling: string | undefined;
    let timeoutMs: number | undefined; let memoryCeilingBytes: number | undefined; let maxOutputBytes: number | undefined;
    let workingDirectory: string | undefined; let network: "forbidden" | undefined;
    const assumptions: string[] = []; const limits: string[] = []; const environmentAllowlist: string[] = [];
    const once = (current: unknown, line: number, field: string) => {
      if (current !== undefined) fail("APPLICATION_VERIFICATION_DUPLICATE", line, `${field} is already declared`);
    };
    for (const row of section.rows) {
      let match: RegExpExecArray | null;
      if ((match = /^claim ([A-Za-z_][A-Za-z0-9_.-]*)$/.exec(row.text))) {
        once(claimRef, row.line, "claim"); claimRef = match[1]!;
      } else if ((match = /^context ([A-Za-z_][A-Za-z0-9_.:-]*) version ([1-9][0-9]*)$/.exec(row.text))) {
        once(contextId, row.line, "context"); contextId = match[1]!; contextVersion = match[2]!;
      } else if ((match = /^interpretation (none|[A-Za-z_][A-Za-z0-9_.:-]*)$/.exec(row.text))) {
        once(interpretationSelector, row.line, "interpretation"); interpretationSelector = match[1] === "none" ? null : match[1]!;
      } else if ((match = /^route ([A-Za-z_][A-Za-z0-9_.:-]*)$/.exec(row.text))) {
        once(routeSelector, row.line, "route"); routeSelector = match[1]!;
      } else if ((match = /^provider ([A-Za-z_][A-Za-z0-9_.:-]*)$/.exec(row.text))) {
        once(providerSelector, row.line, "provider"); providerSelector = match[1]!;
      } else if ((match = /^runtime ([A-Za-z_][A-Za-z0-9_.:-]*)$/.exec(row.text))) {
        once(runtimeSelector, row.line, "runtime"); runtimeSelector = match[1]!;
      } else if ((match = /^timeout-ms ([^\s]+)$/.exec(row.text))) {
        once(timeoutMs, row.line, "timeout-ms"); timeoutMs = boundedInteger(match[1]!, row.line, "timeout-ms");
      } else if ((match = /^memory-ceiling-bytes ([^\s]+)$/.exec(row.text))) {
        once(memoryCeilingBytes, row.line, "memory-ceiling-bytes"); memoryCeilingBytes = boundedInteger(match[1]!, row.line, "memory-ceiling-bytes");
      } else if ((match = /^max-output-bytes ([^\s]+)$/.exec(row.text))) {
        once(maxOutputBytes, row.line, "max-output-bytes"); maxOutputBytes = boundedInteger(match[1]!, row.line, "max-output-bytes");
      } else if (row.text === "network forbidden") {
        once(network, row.line, "network"); network = "forbidden";
      } else if ((match = /^working-directory ([^\s]+)$/.exec(row.text))) {
        once(workingDirectory, row.line, "working-directory");
        if (!relativeDirectory.test(match[1]!)) fail("APPLICATION_VERIFICATION_BOUND", row.line, "working-directory must be a bounded relative path");
        workingDirectory = match[1]!;
      } else if ((match = /^environment-allow ([A-Z][A-Z0-9_]*)$/.exec(row.text))) {
        if (!environmentName.test(match[1]!) || environmentAllowlist.includes(match[1]!)) fail("APPLICATION_VERIFICATION_DUPLICATE", row.line, "environment allowlist names must be unique");
        environmentAllowlist.push(match[1]!);
      } else if ((match = /^assumption ("(?:[^"\\]|\\.)*")$/.exec(row.text))) {
        const value = quoted(match[1]!, row.line); if (assumptions.includes(value)) fail("APPLICATION_VERIFICATION_DUPLICATE", row.line, "assumptions must be unique"); assumptions.push(value);
      } else if ((match = /^limit ("(?:[^"\\]|\\.)*")$/.exec(row.text))) {
        const value = quoted(match[1]!, row.line); if (limits.includes(value)) fail("APPLICATION_VERIFICATION_DUPLICATE", row.line, "limits must be unique"); limits.push(value);
      } else if ((match = /^ceiling ("(?:[^"\\]|\\.)*")$/.exec(row.text))) {
        once(ceiling, row.line, "ceiling"); ceiling = quoted(match[1]!, row.line);
      } else {
        fail("APPLICATION_VERIFICATION_SYNTAX", row.line, "expected an exact claim/context/route/provider/runtime selection, runtime bound, assumption, limit, or ceiling");
      }
    }
    if (!claimRef || !claimIds.has(claimRef)) fail("APPLICATION_VERIFICATION_CLAIM", section.line, `claim ${claimRef ?? "<missing>"} is not declared`);
    if (!contextId || !contextVersion || interpretationSelector === undefined || !routeSelector || !providerSelector || !runtimeSelector ||
        timeoutMs === undefined || memoryCeilingBytes === undefined || maxOutputBytes === undefined || network !== "forbidden" || !workingDirectory || !limits.length || !ceiling) {
      fail("APPLICATION_VERIFICATION_INCOMPLETE", section.line, "claim, context/version, interpretation, route, provider, runtime, all runtime bounds, at least one limit, and ceiling must be explicit");
    }
    const complete = { claimRef: claimRef!, contextId: contextId!, contextVersion: contextVersion!, interpretationSelector: interpretationSelector!,
      routeSelector: routeSelector!, providerSelector: providerSelector!, runtimeSelector: runtimeSelector!, timeoutMs: timeoutMs!,
      memoryCeilingBytes: memoryCeilingBytes!, maxOutputBytes: maxOutputBytes!, workingDirectory: workingDirectory!, ceiling: ceiling! };
    if (contextIds.has(complete.contextId)) fail("APPLICATION_VERIFICATION_COLLISION", section.line, "evaluation context identities must be unique");
    contextIds.add(complete.contextId);
    return { id: section.id, source_line: section.line, claim_ref: complete.claimRef, context_id: complete.contextId, context_version: complete.contextVersion,
      interpretation_selector: complete.interpretationSelector, route_selector: complete.routeSelector, provider_selector: complete.providerSelector,
      runtime_selector: complete.runtimeSelector, assumptions, limits,
      runtime_bounds: { timeout_ms: complete.timeoutMs, memory_ceiling_bytes: complete.memoryCeilingBytes, max_output_bytes: complete.maxOutputBytes,
        network: "forbidden", working_directory: complete.workingDirectory, environment_allowlist: environmentAllowlist }, ceiling: complete.ceiling };
  });
}

function selected(value: unknown, selector: string, sources: ReadonlyMap<string, Buffer>, where: string): SelectedExactRef {
  const item = exactKeys(value, ["selector", "ref"], where);
  if (item.selector !== selector) fail("APPLICATION_VERIFICATION_SELECTION", where, `binding selector must equal authored selector ${selector}`);
  return { selector, ref: resolveExactFormalSource(item.ref, sources, `${where}/ref`).ref };
}

/**
 * Lowers exact evaluation contexts and request-only artifacts. The supplied refs are
 * caller-selected, current bytes; provider availability and execution are not inferred.
 */
export function lowerApplicationVerificationProfiles(
  source: string,
  input: unknown,
  sources: ReadonlyMap<string, Buffer>,
) {
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_VERIFICATION_PROFILE", "$", "verification profiles require application-v1");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const root = exactKeys(input, ["schema_version", "source_sha256", "owner", "formal", "verification_profiles"], "$bindings");
  if (root.schema_version !== "alchlang.verification-profile-bindings/v1" || root.source_sha256 !== digest(source) || root.owner !== model.owner) {
    fail("APPLICATION_VERIFICATION_BINDING", "$bindings", "source, owner or binding version differs");
  }
  const formal = lowerApplicationFormalClaims(source, root.formal, sources);
  const bindingMap = object(root.verification_profiles, "$bindings/verification_profiles");
  const profiles = model.verification_profiles ?? [];
  if (canonical(Object.keys(bindingMap).sort()) !== canonical(profiles.map(profile => profile.id).sort())) {
    fail("APPLICATION_VERIFICATION_BINDING", "$bindings/verification_profiles", "binding coverage differs from authored profiles");
  }
  const files: Record<string, string> = {}; const contexts: JsonObject[] = []; const requests: JsonObject[] = []; const declarations: JsonObject[] = [];
  for (const profile of profiles) {
    const where = `$bindings/verification_profiles/${profile.id}`;
    const binding = exactKeys(bindingMap[profile.id], ["interpretation", "route", "provider", "runtime"], where);
    const route = selected(binding.route, profile.route_selector, sources, `${where}/route`);
    const provider = selected(binding.provider, profile.provider_selector, sources, `${where}/provider`);
    const runtime = selected(binding.runtime, profile.runtime_selector, sources, `${where}/runtime`);
    let interpretation: SelectedExactRef | null = null;
    if (profile.interpretation_selector === null) {
      if (binding.interpretation !== null) fail("APPLICATION_VERIFICATION_SELECTION", `${where}/interpretation`, "authored interpretation none requires a null binding");
    } else {
      interpretation = selected(binding.interpretation, profile.interpretation_selector, sources, `${where}/interpretation`);
    }
    const claimIndex = model.formal_claims.findIndex(claim => claim.id === profile.claim_ref);
    const claimBytes = formal.files[`formalization/claims/${profile.claim_ref}.json`];
    if (claimIndex < 0 || !claimBytes) fail("APPLICATION_VERIFICATION_CLAIM", where, "selected FormalClaim was not lowered");
    const claimRef: ExactFormalSourceRef = { path: `formalization/claims/${profile.claim_ref}.json`, sha256: digest(claimBytes), size_bytes: Buffer.byteLength(claimBytes), current: true };
    const context = { schema_version: "domainspec-v2.evaluation-context/v1-candidate", context_id: profile.context_id,
      version: profile.context_version, status: "draft", formal_claim_ref: claimRef,
      interpretation_model_ref: interpretation?.ref ?? null, route_binding_ref: route.ref,
      provider_profile_ref: provider.ref, runtime_ref: runtime.ref, assumptions: profile.assumptions,
      limits: profile.limits, context_ceiling: profile.ceiling, authority_effect: "none" };
    const prefix = `verification-profiles/${symbol(profile.id)}`;
    const contextPath = `${prefix}/evaluation-context.json`; const contextBytes = json(context);
    files[contextPath] = contextBytes;
    const contextRef: ExactFormalSourceRef = { path: contextPath, sha256: digest(contextBytes), size_bytes: Buffer.byteLength(contextBytes), current: true };
    const request = { schema_version: "alchlang.verification-request/v1-candidate", request_id: `VerificationRequest:${profile.id}`,
      request_state: "ready", formal_claim_ref: claimRef, evaluation_context_ref: contextRef,
      route_binding_ref: route.ref, provider_profile_ref: provider.ref, runtime_ref: runtime.ref,
      execution_policy: profile.runtime_bounds, authority_effect: "none", release_admission: "not-granted",
      claim_ceiling: profile.ceiling, residue: [] as string[] };
    const requestPath = `${prefix}/request.json`; const requestBytes = json(request); files[requestPath] = requestBytes;
    contexts.push(context); requests.push(request);
    declarations.push({ source_id: profile.id, source_line: profile.source_line, claim_source_id: profile.claim_ref,
      claim_identity_inputs_digest: formal.claims[claimIndex]!.claim.identity_inputs_digest,
      claim_ref: claimRef, context_ref: contextRef,
      request_ref: { path: requestPath, sha256: digest(requestBytes), size_bytes: Buffer.byteLength(requestBytes), current: true },
      selectors: { interpretation: profile.interpretation_selector, route: profile.route_selector, provider: profile.provider_selector, runtime: profile.runtime_selector } });
  }
  const trace = { schema_version: "alchlang.verification-profile-trace/v1-candidate", source_sha256: digest(source),
    bindings_sha256: digest(canonical(input)), formal_claim_trace_sha256: digest(json(formal.trace)), declarations,
    provider_execution_observed: false, evaluation_result_observed: false, authority_effect: "none" };
  files["verification-profiles/trace.json"] = json(trace);
  return { model, formal, contexts, requests, files, trace };
}

export function assertApplicationVerificationProfilesCurrent(
  source: string,
  input: unknown,
  sources: ReadonlyMap<string, Buffer>,
  candidate: unknown,
): void {
  if (json(candidate) !== json(lowerApplicationVerificationProfiles(source, input, sources))) {
    fail("APPLICATION_VERIFICATION_STALE", "$candidate", "verification profiles differ from exact current source, bindings, or referenced artifacts");
  }
}
