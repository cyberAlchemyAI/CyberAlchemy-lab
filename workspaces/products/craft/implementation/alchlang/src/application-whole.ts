import { CompilationRejected } from "./model.js";
import { digest, json } from "./domainspec-profile.js";
import { compileApplicationExecutable, type prepareApplicationExecutable } from "./application-executable.js";
import type { DomainSpecCompiler, DomainSpecGraph } from "./domainspec-cli.js";

const fail = (code: string, message: string): never => {
  throw new CompilationRejected([{ code, path: "$application", message }]);
};

/** Combine already-authored partitions; never synthesize missing integration intent. */
export function compileApplicationWhole(candidate: ReturnType<typeof prepareApplicationExecutable>, graph: DomainSpecGraph, observation: unknown, compiler: DomainSpecCompiler) {
  if (!observation || typeof observation !== "object" || Array.isArray(observation)
    || json(Object.keys(observation).sort()) !== json(["disclosure_policy", "orodi_binding", "schema_version", "source_id", "source_sha256"])) {
    fail("APPLICATION_WHOLE_OBSERVATION", "explicit closed observation binding required");
  }
  const input = observation as Record<string, unknown>;
  if (input.schema_version !== "alchlang.application-observation/v1-candidate") fail("APPLICATION_WHOLE_OBSERVATION", "unsupported observation binding");
  // This verifies preparation custody and exact graph bytes before consuming partitions.
  const executable = compileApplicationExecutable(candidate, graph, compiler);
  const formation = candidate.projection.formation;
  if (input.source_sha256 !== formation.trace.source_sha256) fail("APPLICATION_WHOLE_STALE", "observation must bind exact authored source bytes");
  if (!formation.persistence || !formation.messaging || !formation.externalApi || !formation.runtime) {
    return fail("APPLICATION_WHOLE_PARTITIONS", "this whole-application vertical requires explicit persistence, messaging, API and runtime partitions");
  }
  const inbound = formation.model.integrations.filter(item => item.kind === "inbound-endpoint");
  if (inbound.length !== 1 || inbound[0]!.protocol.method !== "POST") {
    return fail("APPLICATION_WHOLE_ENDPOINT", "the reference provider currently requires one authored HTTP POST endpoint");
  }
  const route = { method: "POST" as const, path: inbound[0]!.protocol.path };
  const integrationSource = {
    schema_version: "domainspec.integration-generation-source/v2-candidate",
    source_id: input.source_id,
    persistence: formation.persistence.sourceComposition,
    messaging: formation.messaging.sourceComposition,
    external_api: formation.externalApi.sourceComposition,
    disclosure_policy: input.disclosure_policy, orodi_binding: input.orodi_binding,
  };
  const runtimeBinding = compiler.compileApplicationRuntimeBinding(graph, integrationSource, formation.runtime.selected.selection, candidate.selection);
  const wholeApplication = compiler.composeApplicationArtifacts(executable.plan, integrationSource, runtimeBinding.binding);
  const application = compiler.composeProviderApplicationArtifacts(wholeApplication, formation.runtime.selected.selection, integrationSource, route);
  const artifactIndex = { whole_application_plan_sha256: wholeApplication.plan_sha256,
    provider_application_plan_sha256: application.plan_sha256,
    provider_selection_sha256: application.provider_selection_sha256,
    artifacts: application.artifacts.map(({ relative_path, sha256, size_bytes }) => ({ relative_path, sha256, size_bytes })),
    runtime_guarantees_observed: false, authority_effect: "none" };
  const files = { "application-integration-source.json": json(integrationSource), "application-runtime-binding.json": json(runtimeBinding), "application-artifact-index.json": json(artifactIndex) };
  const trace = { schema_version: "alchlang.whole-application-trace/v1-candidate",
    source_sha256: formation.trace.source_sha256, executable_trace_sha256: digest(json(executable.trace)),
    observation_sha256: digest(json(observation)), selected_profile: formation.runtime.selected.id,
    runtime_binding_sha256: runtimeBinding.runtime_binding_sha256,
    whole_application_plan_sha256: wholeApplication.plan_sha256,
    provider_application_plan_sha256: application.plan_sha256,
    files: Object.fromEntries(Object.entries(files).map(([p, bytes]) => [p, { sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes) }])),
    runtime_guarantees_observed: false, authority_effect: "none" };
  return { executable, integrationSource, runtimeBinding, wholeApplication, application, files: { ...files, "application-whole-trace.json": json(trace) }, trace };
}

export function assertApplicationWholeCurrent(candidate: ReturnType<typeof prepareApplicationExecutable>, graph: DomainSpecGraph, observation: unknown, compiler: DomainSpecCompiler, result: unknown): void {
  if (json(result) !== json(compileApplicationWhole(candidate, graph, observation, compiler))) fail("APPLICATION_WHOLE_STALE", "whole application differs from exact current inputs");
}
