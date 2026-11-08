import { CompilationRejected } from "./model.js";
import type { ApplicationSourceSection } from "./formal-claim.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { parseDomainSource } from "./parser.js";
import type { DomainSpecCompiler } from "./domainspec-cli.js";

export interface ApplicationRuntimeProfile {
  id: string;
  source_line: number;
  target: "typescript" | "python" | "rust";
  selection_id: string;
  pack_id: string;
  requirements: Record<string, string>;
  providers: Record<string, string>;
  environment: Array<{ name: string; classification: "secret-reference" | "endpoint-reference"; required: true }>;
  messaging_destinations: Array<{ channel_ref: string; environment_name: string }>;
}
const fail = (code: string, line: number, message: string): never => {
  throw new CompilationRejected([{ code, path: `$line:${line}`, message }]);
};
const roles = ["persistence", "messaging", "outbound-http", "inbound-http"] as const;
const baseEnvironmentOrder = ["DATABASE_URL", "INBOUND_BIND_ADDRESS", "NATS_URL", "PAYMENT_BASE_URL", "WEBHOOK_SECRET"];
const compare = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;

/** Runtime declarations are selections, never domain nodes or executable instructions. */
export function normalizeApplicationRuntimeProfiles(sections: ApplicationSourceSection[]): ApplicationRuntimeProfile[] {
  const paths = new Set<string>(); const selections = new Set<string>();
  return sections.map(section => {
    let target: ApplicationRuntimeProfile["target"] | undefined;
    let selection: string | undefined; let pack: string | undefined;
    const requirements: Record<string, string> = Object.create(null);
    const providers: ApplicationRuntimeProfile["providers"] = Object.create(null);
    const environment: ApplicationRuntimeProfile["environment"] = [];
    const messagingDestinations: ApplicationRuntimeProfile["messaging_destinations"] = [];
    for (const row of section.rows) {
      let m: RegExpExecArray | null;
      if ((m = /^target (typescript|python|rust)$/.exec(row.text))) {
        if (target) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "target is already declared");
        target = m[1] as ApplicationRuntimeProfile["target"];
      } else if ((m = /^selection (provider-selection:[a-z0-9]+(?:-[a-z0-9]+)*)$/.exec(row.text))) {
        if (selection) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "selection is already declared");
        selection = m[1]!;
      } else if ((m = /^provider-pack ([A-Za-z0-9][A-Za-z0-9./:_-]*)$/.exec(row.text))) {
        if (pack) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "pack is already declared");
        pack = m[1]!;
      } else if ((m = /^runtime (node|python|rust-edition) "([>=0-9.]+)"$/.exec(row.text))) {
        if (Object.hasOwn(requirements, m[1]!)) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "runtime is already declared");
        requirements[m[1]!] = m[2]!;
      } else if ((m = /^provider (persistence|messaging|outbound-http|inbound-http) ([A-Za-z0-9:_-]+)$/.exec(row.text))) {
        const key = m[1]!.replaceAll("-", "_");
        if (Object.hasOwn(providers, key)) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "provider is already declared");
        providers[key] = m[2]!;
      } else if ((m = /^environment ([A-Z][A-Z0-9_]*) (secret-reference|endpoint-reference) required$/.exec(row.text))) {
        const name = m[1]!;
        if (environment.some(e => e.name === name)) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "environment reference is already declared");
        environment.push({ name: m[1]!, classification: m[2] as "secret-reference" | "endpoint-reference", required: true });
      } else if ((m = /^messaging-destination (channel:[a-z0-9]+(?:-[a-z0-9]+)*) ([A-Z][A-Z0-9_]*)$/.exec(row.text))) {
        if (messagingDestinations.some(destination => destination.channel_ref === m![1] || destination.environment_name === m![2])) fail("APPLICATION_RUNTIME_DUPLICATE", row.line, "messaging destination channel and environment names must be unique");
        messagingDestinations.push({ channel_ref: m[1]!, environment_name: m[2]! });
      } else fail("APPLICATION_RUNTIME_SYNTAX", row.line, "expected an explicit runtime/provider selection, environment reference, or messaging destination; values and executable clauses are forbidden");
    }
    if (!target || !selection || !pack || !Object.keys(requirements).length || roles.some(role => !Object.hasOwn(providers, role.replaceAll("-", "_"))) || !environment.length || !messagingDestinations.length) {
      fail("APPLICATION_RUNTIME_INCOMPLETE", section.line, "target, selection, pack, runtime, all provider roles, environment references, and messaging destinations must be explicit");
    }
    const key = symbol(section.id);
    if (paths.has(key) || selections.has(selection!)) fail("APPLICATION_RUNTIME_COLLISION", section.line, "profile paths and selection identities must be unique");
    paths.add(key); selections.add(selection!);
    const environmentOrder = (name: string) => {
      const index = baseEnvironmentOrder.indexOf(name);
      return index < 0 ? baseEnvironmentOrder.length : index;
    };
    environment.sort((a, b) => environmentOrder(a.name) - environmentOrder(b.name) || compare(a.name, b.name));
    messagingDestinations.sort((a, b) => compare(a.channel_ref, b.channel_ref));
    return { id: section.id, source_line: section.line, target: target!, selection_id: selection!, pack_id: pack!,
      requirements, providers, environment, messaging_destinations: messagingDestinations };
  });
}

export type RuntimeProfileCompiler = Pick<DomainSpecCompiler, "compileProviderRuntimeProfile">;

/** All profiles are validated; consumption requires an explicit profile, never a default. */
export function lowerApplicationRuntimeProfiles(source: string, profileId: string, compiler: RuntimeProfileCompiler) {
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("ALCH_PROFILE_REQUIRED", 1, "runtime profiles require application-v1");
  const profiles = (parsed.carrier as unknown as { runtime_profiles?: ApplicationRuntimeProfile[] }).runtime_profiles ?? [];
  if (!profiles.some(p => p.id === profileId)) fail("APPLICATION_RUNTIME_SELECTION", 1, "select one declared runtime profile explicitly");
  const files: Record<string, string> = {};
  const lowered = profiles.map(profile => {
    const compiled = compiler.compileProviderRuntimeProfile({
      schema_version: "domainspec.provider-profile-request/v1-candidate",
      selection_id: profile.selection_id, pack_id: profile.pack_id, language: profile.target,
      capabilities: [...roles], providers: profile.providers,
      configuration: { environment: profile.environment, messaging_destinations: profile.messaging_destinations }, authority_effect: "none",
    }, profile.requirements);
    const prefix = `runtime-profiles/${symbol(profile.id)}`;
    files[`${prefix}/providers.json`] = json(compiled.selection);
    files[`${prefix}/requirements.json`] = json(compiled.requirements);
    return { id: profile.id, source_line: profile.source_line, ...compiled };
  });
  const selected = lowered.find(p => p.id === profileId)!;
  const trace = { schema_version: "alchlang.runtime-profile-trace/v1-candidate",
    source_sha256: digest(source), selected_profile: profileId,
    profiles: lowered.map(p => ({ id: p.id, source_line: p.source_line, selection_sha256: p.selection_sha256, requirements_sha256: p.requirements_sha256 })),
    files: Object.fromEntries(Object.entries(files).map(([p, bytes]) => [p, { sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes) }])),
    runtime_guarantees_observed: false, authority_effect: "none" };
  files["runtime-profiles/trace.json"] = json(trace);
  return { selected, profiles: lowered, files, trace };
}

export function assertApplicationRuntimeProfilesCurrent(source: string, profileId: string, compiler: RuntimeProfileCompiler, candidate: unknown): void {
  if (json(candidate) !== json(lowerApplicationRuntimeProfiles(source, profileId, compiler))) fail("APPLICATION_RUNTIME_STALE", 1, "runtime profiles differ from exact current source, selection or compiler requirements");
}
