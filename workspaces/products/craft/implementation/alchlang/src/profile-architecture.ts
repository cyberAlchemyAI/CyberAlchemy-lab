import { CompilationRejected } from "./model.js";

export type ProfileArchitectureRole = "canonical-product" | "compatibility" | "capability-adapter" | "optional-package";
export type ProfileParserOwner = "shared-domain-parser" | "package-local-adapter";

export interface AlchSourceProfileDescriptor {
  id: string;
  role: ProfileArchitectureRole;
  parser_owner: ProfileParserOwner;
  normalized_model: "application-v1" | "legacy-carrier-v1" | "package-local";
  commands: readonly string[];
  capabilities: readonly string[];
  optional_feature: "rust" | "local-host" | null;
  product_language: boolean;
  authority_effect: "none";
}

const descriptor = (value: Omit<AlchSourceProfileDescriptor, "authority_effect">): AlchSourceProfileDescriptor =>
  Object.freeze({ ...value, commands: Object.freeze([...value.commands]), capabilities: Object.freeze([...value.capabilities]), authority_effect: "none" });

const adapter = (id: string, commands: string[], capabilities: string[]): AlchSourceProfileDescriptor => descriptor({
  id, role: "capability-adapter", parser_owner: "package-local-adapter", normalized_model: "package-local",
  commands, capabilities, optional_feature: null, product_language: false,
});

const rows: AlchSourceProfileDescriptor[] = [
  descriptor({ id: "application-v1", role: "canonical-product", parser_owner: "shared-domain-parser", normalized_model: "application-v1", commands: ["check", "build", "verify", "qualify"], capabilities: ["domain", "formal-claim", "integration", "realization", "runtime-profile"], optional_feature: null, product_language: true }),
  descriptor({ id: "legacy-sfol-v1", role: "compatibility", parser_owner: "shared-domain-parser", normalized_model: "legacy-carrier-v1", commands: ["check", "build", "trace", "ontology", "explain", "conformance"], capabilities: ["historical-inline-sfol"], optional_feature: null, product_language: false }),
  adapter("bound-application-v1", ["check", "build", "ontology"], ["historical-bound-application"]),
  adapter("declarative-function-v1", ["check", "build", "trace", "ontology", "explain", "conformance"], ["function", "module"]),
  adapter("event-function-v1", ["check", "build"], ["event-function"]),
  adapter("function-v1", ["check", "build", "trace", "ontology", "explain", "conformance"], ["function"]),
  adapter("http-contract-v1", [], ["imported-http-contract"]),
  adapter("module-configuration-v1", ["check", "build", "ontology"], ["module-configuration"]),
  adapter("module-configuration-v2", ["check", "build", "ontology"], ["module-configuration", "injected-runtime-binding"]),
  adapter("outbound-invocation-v1", ["check", "build"], ["outbound-invocation"]),
  adapter("outbound-invocation-v2", [], ["inference-router-outbound-invocation"]),
  adapter("query-iteration-v1", ["check", "build"], ["query-iteration"]),
  adapter("request-custody-v1", ["check", "build"], ["request-custody"]),
  adapter("response-stream-v1", ["check", "build"], ["response-stream"]),
  adapter("semantic-contract-v1", ["check", "build", "ontology"], ["semantic-contract"]),
  adapter("service-v1", ["check", "build", "ontology"], ["service-assembly"]),
  descriptor({ id: "event-execution-v1", role: "optional-package", parser_owner: "package-local-adapter", normalized_model: "package-local", commands: ["check", "build"], capabilities: ["event-execution"], optional_feature: "rust", product_language: false }),
  descriptor({ id: "semantic-host-v1", role: "optional-package", parser_owner: "package-local-adapter", normalized_model: "package-local", commands: ["check", "build", "ontology", "explain"], capabilities: ["semantic-host"], optional_feature: "rust", product_language: false }),
  descriptor({ id: "local-host-migration-v1", role: "optional-package", parser_owner: "package-local-adapter", normalized_model: "package-local", commands: ["check", "build"], capabilities: ["local-host-migration"], optional_feature: "local-host", product_language: false }),
  descriptor({ id: "local-host-v1", role: "optional-package", parser_owner: "package-local-adapter", normalized_model: "package-local", commands: ["check", "build"], capabilities: ["local-host"], optional_feature: "local-host", product_language: false }),
  descriptor({ id: "ontology-host-v1", role: "optional-package", parser_owner: "package-local-adapter", normalized_model: "package-local", commands: ["check", "build", "ontology"], capabilities: ["ontology-host"], optional_feature: "local-host", product_language: false }),
];

if (new Set(rows.map(row => row.id)).size !== rows.length) throw new Error("PROFILE_ARCHITECTURE_DUPLICATE");
export const ALCH_SOURCE_PROFILE_ARCHITECTURE = Object.freeze([...rows]);
const profiles = new Map(rows.map(row => [row.id, row]));

export interface SelectedAlchSourceProfile {
  profile: AlchSourceProfileDescriptor;
  selection: "explicit" | "historical-default";
  authority_effect: "none";
}

const reject = (code: string, line: number | "$", message: string): never => {
  throw new CompilationRejected([{ code, path: line === "$" ? "$profile" : `$line:${line}`, message }]);
};

/** Select one root profile; semantic parsing stays with the declared shared parser or bounded package adapter. */
export function selectAlchSourceProfile(source: string): SelectedAlchSourceProfile {
  const declarations: Array<{ id: string; line: number }> = [];
  for (const [index, raw] of source.split(/\r?\n/).entries()) {
    if (/^\s/.test(raw) || !raw.trim() || raw.trimStart().startsWith("#") || raw.startsWith("```")) continue;
    if (!raw.startsWith("profile")) continue;
    const match = /^profile\s+([A-Za-z_][\w.-]*)$/.exec(raw);
    if (!match) reject("ALCH_PROFILE_SYNTAX", index + 1, "expected profile <registered-id>");
    declarations.push({ id: match![1]!, line: index + 1 });
  }
  if (declarations.length > 1) reject("ALCH_PROFILE_CONFLICT", "$", "exactly one root source profile may be selected");
  if (!declarations.length) return Object.freeze({ profile: profiles.get("legacy-sfol-v1")!, selection: "historical-default", authority_effect: "none" });
  const selected = declarations[0]!, profile = profiles.get(selected.id);
  if (!profile) reject("ALCH_PROFILE_UNSUPPORTED", selected.line, `unregistered root source profile ${selected.id}`);
  return Object.freeze({ profile: profile!, selection: "explicit", authority_effect: "none" });
}
