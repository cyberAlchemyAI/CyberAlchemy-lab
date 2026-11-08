import { readFileSync } from "node:fs";
import path from "node:path";
import { executableFixture } from "./application-executable-fixture.js";
import { persistenceFixture, messagingFixture, externalApiFixture } from "./application-integration-fixtures.js";
import { digest, json } from "../../src/domainspec-profile.js";
import { lowerApplicationDomain } from "../../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../../src/application-rule-projection.js";
import { prepareApplicationExecutable } from "../../src/application-executable.js";
import { deriveApplicationIntegrationBindings } from "../../src/application-integration-derivation.js";

/** Synthetic author choices only: no production approval or environment access. */
export async function wholeApplicationFixture(selectionId = "provider-selection:commerce-runtime", composed = false, derivedIntegration = false,
  language: "typescript" | "python" | "rust" = "typescript") {
  const base = executableFixture();
  const [p, m, a] = await Promise.all([persistenceFixture(), messagingFixture(), externalApiFixture()]);
  const compiler = a.compiler;
  const messageDeclarations = m.source.slice(base.source.length).replace(/mapping OrderToMessage:[\s\S]*?publication PublishOrder:/, `value-object OrderNotice:
  id UInt64
mapping OrderToMessage:
  input order -> Order.id
  target OrderNotice
  total true
  field id <- order.id
mapping MessageToOrder:
  input payload OrderNotice
  target OrderNotice
  total true
  field id <- payload.id
operation ReceiveNotice:
  input OrderNotice
  output OrderNotice
  requires IdentityValid
publication PublishOrder:`).replace("-> operation SubmitOrder", "-> operation ReceiveNotice");
  const profileName = language === "typescript" ? "CommerceRuntime" : language === "python" ? "CommerceRuntimePython" : "CommerceRuntimeRust";
  const runtimeProfile = (name: string, target: "typescript" | "python" | "rust", selectedId: string) => `runtime-profile ${name}:
  target ${target}
  selection ${selectedId}
  provider-pack domainspec.reference-postgresql16-nats-http/v1-candidate
  runtime ${target === "typescript" ? 'node "26.8.1"' : target === "python" ? 'python ">=3.11"' : 'rust-edition "2024"'}
  provider persistence postgresql:16
  provider messaging nats:jetstream
  provider outbound-http http:outbound
  provider inbound-http http:inbound
  environment DATABASE_URL secret-reference required
  environment INBOUND_BIND_ADDRESS endpoint-reference required
  environment NATS_URL endpoint-reference required
  environment PAYMENT_BASE_URL endpoint-reference required
  environment WEBHOOK_SECRET secret-reference required
  environment ORDER_EVENTS_TOPIC endpoint-reference required
  messaging-destination channel:order-events-topic ORDER_EVENTS_TOPIC
`;
  const profileSelection = (target: "typescript" | "python" | "rust") => target === language ? selectionId : `provider-selection:reference-${target}`;
  const source = base.source + p.source.slice(base.source.length) + messageDeclarations + a.source.slice(base.source.length)
    + runtimeProfile("CommerceRuntime", "typescript", profileSelection("typescript"))
    + runtimeProfile("CommerceRuntimePython", "python", profileSelection("python"))
    + runtimeProfile("CommerceRuntimeRust", "rust", profileSelection("rust"))
    + (composed ? `realization SubmitOrderExecution:
  operation SubmitOrder
  input request
  read current <- Order key request.id
  guard EligibleOrder(order <- current)
  write Order replace <- request
  result <- request
  atomicity state-and-outbox
  continuation awaited-settlement
realization ReceiveNoticeExecution:
  operation ReceiveNotice
  input request
  map normalized <- MessageToOrder(payload <- request)
  guard IdentityValid(identity <- normalized.id)
  result <- normalized
  atomicity state-and-outbox
  continuation awaited-settlement
` : "");
  const sourceHash = digest(source);
  for (const f of [p, m, a]) f.binding.source_sha256 = sourceHash;
  m.binding.composition.subscription_bindings[0].operation_ref = "commerce:receive-notice";
  m.binding.composition.integration_kernel.integration_bindings[1].logical_boundary_ref = "commerce:receive-notice";
  m.binding.composition.message_mappings[1].target_ref = "commerce:receive-notice#request";
  // Explicit synthetic failure policy: all provider categories return the one
  // authored submission failure; categories/matchers remain distinct.
  const failure = "commerce:submit-order";
  for (const f of [p, m, a]) for (const mapping of f.binding.composition.integration_kernel.failure_mappings) {
    mapping.unknown_failure_outcome_ref = failure;
    for (const item of mapping.cases) item.failure_outcome_ref = failure;
  }
  for (const contract of a.binding.composition.external_api_contracts) for (const operation of contract.operations) operation.failure_outcome_refs = [failure];
  for (const mapping of a.binding.composition.api_failure_mappings) {
    mapping.unknown_fallback_ref = failure;
    for (const item of mapping.cases) item.failure_outcome_ref = failure;
  }
  const fields = (ontology: string) => ({ ontology, properties: {
    id: { ontology: ontology + "#id", meaning: "Public identity value." },
    accepted: { ontology: ontology + "#accepted", meaning: "Explicit acceptance flag." },
  } });
  const bindings = { ...base.bindings, source_sha256: sourceHash, formal: { ...base.bindings.formal, source_sha256: sourceHash }, declarations: {
    ...base.bindings.declarations,
    FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "At most one explicitly eligible order." },
    OrderSubmitted: { ontology: "FIXTURE-ORDER-SUBMITTED", meaning: "An occurrence carrying the Order identity." },
    OrderNotice: { ontology: "FIXTURE-ORDER-NOTICE", meaning: "An explicitly projected order identity.", invariants: ["IdentityValid"], properties: { id: { ontology: "FIXTURE-ORDER-NOTICE#id", meaning: "The projected identity." } } },
    OrderToMessage: { ontology: "FIXTURE-ORDER-TO-MESSAGE", meaning: "Project the Event identity into a notice." },
    MessageToOrder: { ontology: "FIXTURE-MESSAGE-TO-ORDER", meaning: "Project the message payload into a notice." },
    ReceiveNotice: { ontology: "FIXTURE-RECEIVE-NOTICE", meaning: "Return the supplied notice without persistence.", failure_continuation: "return-notice-error" },
    OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Named API boundary.", contracts: { SubmitRequest: fields("FIXTURE-SUBMIT-REQUEST"), Summary: fields("FIXTURE-SUMMARY") } },
    RequestToOrder: { ontology: "FIXTURE-REQUEST-TO-ORDER", meaning: "Project request fields without construction." },
    OrderToSummary: { ontology: "FIXTURE-ORDER-TO-SUMMARY", meaning: "Project public response fields." },
    ProviderRequest: { ontology: "FIXTURE-PROVIDER-REQUEST", meaning: "Explicit provider request projection." },
    ProviderResponse: { ontology: "FIXTURE-PROVIDER-RESPONSE", meaning: "Explicit provider response projection." },
  } };
  const explicitContexts = [{ binding: p.binding, compiler }, { binding: m.binding, compiler }, { binding: a.binding, compiler }, { profile: profileName, compiler }] as const;
  const derived = derivedIntegration ? deriveApplicationIntegrationBindings(source, profileName, compiler) : undefined;
  const contexts: readonly [any, any, any, any] = derived
    ? [{ binding: derived.persistence, compiler }, { binding: derived.messaging, compiler },
      { binding: derived.externalApi, compiler }, { profile: profileName, compiler }]
    : explicitContexts;
  const formation = lowerApplicationDomain(source, bindings, base.sources, ...contexts);
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, base.sources, interpretation, ...contexts);
  const selection: any = structuredClone(base.execution.selection);
  if (language === "python") {
    selection.schema_version = "domainspec.reconciled-python-compilation/v1-candidate";
    selection.profile_id = "domainspec.reconciled-python/v1-candidate";
    selection.language = "python";
    delete selection.value_profile;
  } else if (language === "rust") {
    selection.schema_version = "domainspec.reconciled-rust-compilation/v1-candidate";
    selection.profile_id = "domainspec.reconciled-rust/v1-candidate";
    selection.language = "rust";
    delete selection.value_profile;
  }
  selection.factories.push({ selector: "commerce:order-notice", base_validators: [{ rule: "commerce:identity-valid", arguments: [{ parameter: "identity", field: "id" }] }], extensions: [] });
  selection.operations.push({ schema_version: "domainspec.operation-action-bindings/v1-candidate", selector: "commerce:receive-notice",
    inputs: [{ name: "request", type: { kind: "named", selector: "commerce:order-notice" } }], reads: [],
    guards: [{ selector: "commerce:identity-valid", arguments: [{ parameter: "identity", value: { op: "path", root: "request", properties: ["FIXTURE-ORDER-NOTICE#id"] } }] }],
    writes: [], events: [], result: { type: { kind: "named", selector: "commerce:order-notice" }, value: { op: "path", root: "request", properties: [] } },
    atomicity: "state-and-outbox", continuation: "awaited-settlement" });
  if(composed){
    delete selection.operations;
    selection.schema_version="domainspec.reconciled-compilation/v2-candidate";
    selection.profile_id="domainspec.reconciled-typescript/v2-candidate";
  }
  const execution = { ...base.execution, ...(composed?{schema_version:"alchlang.application-execution/v2-candidate"}:{}), selection, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(source, bindings, base.sources, interpretation, execution, compiler, ...contexts);
  const existing = JSON.parse(readFileSync(path.join(compiler.binding.package_root, "examples/reconciled-commerce/integrations/application.json"), "utf8"));
  const observation = { schema_version: "alchlang.application-observation/v1-candidate", source_sha256: sourceHash,
    source_id: "integration-source:alch-commerce", disclosure_policy: existing.disclosure_policy, orodi_binding: existing.orodi_binding };
  return { source, compiler, bindings, sources: base.sources, contexts, formation, interpretation, execution, candidate, observation };
}

export const wholeApplicationFixtureForLanguage = (language: "typescript" | "python" | "rust") =>
  wholeApplicationFixture(`provider-selection:reference-${language}`, false, false, language);
