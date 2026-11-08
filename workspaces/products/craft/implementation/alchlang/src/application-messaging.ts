import { parseDomainSource } from "./parser.js";
import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { DomainSpecCompiler } from "./domainspec-cli.js";

type Obj = Record<string, any>;
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
function exact(value: unknown, keys: string[], at: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value) || json(Object.keys(value).sort()) !== json([...keys].sort())) return fail("APPLICATION_MESSAGING_BINDING", at, "unexpected or missing member");
  return value as Obj;
}
function coverage(values: string[], expected: string[], at: string): void {
  if (new Set(values).size !== values.length || json([...values].sort()) !== json([...expected].sort())) fail("APPLICATION_MESSAGING_COVERAGE", at, "exact authored binding coverage required");
}

/** Static path-to-contract binding. Message aliases stay outside domain declarations. */
export function lowerApplicationMessaging(source: string, input: unknown, compiler: Pick<DomainSpecCompiler, "compileMessagingComposition">) {
  const root = exact(input, ["schema_version", "source_sha256", "composition", "declarations", "messages", "channels"], "$messaging");
  if (root.schema_version !== "alchlang.application-messaging/v1-candidate" || root.source_sha256 !== digest(source)) fail("APPLICATION_MESSAGING_SOURCE", "$messaging", "source bytes or binding version differ");
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_MESSAGING_PROFILE", "$", "explicit application profile required");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const declarations = model.integrations.filter(d => d.kind === "publication" || d.kind === "subscription");
  if (!declarations.length) fail("APPLICATION_MESSAGING_COVERAGE", "$", "no messaging declaration");
  const choices = exact(root.declarations, declarations.map(d => d.id), "$declarations");
  const messageNames = [...new Set(declarations.map(d => d.message.ref))];
  const channelNames = [...new Set(declarations.flatMap(d => [d.channel.ref, ...(d.kind === "subscription" ? [d.dead_letter.ref] : [])]))];
  const messages = exact(root.messages, messageNames, "$messages"), channels = exact(root.channels, channelNames, "$channels");
  const composition = compiler.compileMessagingComposition(root.composition);
  const byId = new Map(model.declarations.map(d => [d.id, d]));
  const selector = (id: string) => `${symbol(model.domain_id)}:${symbol(id)}`;
  const names = model.declarations.map(d => selector(d.id));
  if (new Set(names).size !== names.length) fail("APPLICATION_SYMBOL_COLLISION", "$", "domain identities collide");
  for (const name of [...messageNames, ...channelNames]) if (byId.has(name)) fail("APPLICATION_MESSAGING_IDENTITY", "$", "transport alias cannot shadow a domain declaration");
  coverage(Object.values(messages), composition.message_types.map((m: Obj) => m.message_type_id), "$messages");
  coverage(Object.values(channels), composition.channels.map((c: Obj) => c.channel_id), "$channels");
  const publications: string[] = [], subscriptions: string[] = [], mappings: string[] = [];
  const references = declarations.map(d => {
    const at = `$line:${d.source_line}`, choice = exact(choices[d.id], ["binding_ref"], at);
    const rows = d.kind === "publication" ? composition.publication_bindings : composition.subscription_bindings;
    const binding = rows.find((b: Obj) => b.binding_id === choice.binding_ref);
    if (!binding) return fail("APPLICATION_MESSAGING_REFERENCE", at, "missing binding of authored kind");
    const mapper = byId.get(d.mapping.ref);
    if (mapper?.kind !== "mapping" || binding.mapper_ref !== selector(mapper.id)) return fail("APPLICATION_MESSAGING_MAPPING", at, "map must select the exact declared Mapping");
    const mapping = composition.message_mappings.find((m: Obj) => m.mapper_ref === binding.mapper_ref)!;
    if (mapping.total !== mapper.total) fail("APPLICATION_MESSAGING_MAPPING", at, "mapping totality differs");
    const channel = composition.channels.find((c: Obj) => c.channel_id === channels[d.channel.ref]);
    if (channel?.channel_kind !== d.channel.kind || binding.channel_ref !== channel.channel_id || binding.message_type_ref !== messages[d.message.ref]) fail("APPLICATION_MESSAGING_PATH", at, "channel kind or message path differs");
    const kernel = composition.integration_kernel.integration_bindings.find((b: Obj) => b.binding_id === binding.integration_binding_ref)!;
    if (kernel.provider_realization_ref !== binding.provider_realization_ref || kernel.failure_mapping_ref !== binding.failure_mapping_ref) fail("APPLICATION_MESSAGING_KERNEL", at, "shared kernel and specialized binding differ");
    mappings.push(mapping.mapping_id);
    if (d.kind === "publication") {
      const event = byId.get(d.event.ref);
      if (event?.kind !== "event" || binding.logical_source_ref !== selector(event.id) || kernel.logical_boundary_ref !== selector(event.id)) fail("APPLICATION_MESSAGING_EVENT", at, "publication must select the exact declared Event");
      publications.push(binding.binding_id);
      return { source_id: d.id, kind: d.kind, source_line: d.source_line, binding_ref: binding.binding_id, event_ref: binding.logical_source_ref, mapping_ref: binding.mapper_ref, message_ref: binding.message_type_ref, channel_ref: binding.channel_ref };
    }
    const operation = byId.get(d.operation.ref);
    if (operation?.kind !== "operation" || binding.operation_ref !== selector(operation.id) || kernel.logical_boundary_ref !== selector(operation.id)) fail("APPLICATION_MESSAGING_OPERATION", at, "subscription must select the exact declared Operation");
    const ack = composition.acknowledgement_boundaries.find((a: Obj) => a.boundary_id === binding.acknowledgement_boundary_ref)!;
    if (ack.condition !== d.acknowledge.condition) fail("APPLICATION_MESSAGING_ACK", at, "acknowledgement boundary differs");
    const dedup = composition.deduplication_policies.find((p: Obj) => p.policy_id === binding.deduplication_policy_ref)!;
    if (dedup.key_expression !== `message.${d.deduplicate.key_path.join(".")}`) fail("APPLICATION_MESSAGING_DEDUP", at, "deduplication path differs; message is the explicit transport root");
    const delivery = composition.delivery_policies.find((p: Obj) => p.policy_id === binding.delivery_policy_ref)!;
    const dead = composition.channels.find((c: Obj) => c.channel_id === channels[d.dead_letter.ref]);
    if (delivery.terminal_disposition !== "dead-letter" || delivery.dead_letter_channel_ref !== dead?.channel_id || dead?.channel_kind !== "dead-letter" || dead.source_channel_ref !== channel.channel_id) fail("APPLICATION_MESSAGING_FAILURE", at, "dead-letter policy differs from the authored failure path");
    coverage(mapping.input_paths.map((p: Obj) => p.parameter), mapper.inputs.map(p => symbol(p.name, "_")), at);
    subscriptions.push(binding.binding_id);
    return { source_id: d.id, kind: d.kind, source_line: d.source_line, binding_ref: binding.binding_id, operation_ref: binding.operation_ref, mapping_ref: binding.mapper_ref, message_ref: binding.message_type_ref, channel_ref: binding.channel_ref, acknowledgement: ack.condition, deduplication: dedup.key_expression, dead_letter_ref: dead.channel_id };
  });
  coverage(publications, composition.publication_bindings.map((b: Obj) => b.binding_id), "$publications");
  coverage(subscriptions, composition.subscription_bindings.map((b: Obj) => b.binding_id), "$subscriptions");
  coverage([...new Set(mappings)], composition.message_mappings.map((m: Obj) => m.mapping_id), "$mappings");
  const sourceComposition = JSON.parse(json(root.composition));
  const sourceFile = json(sourceComposition), compiledFile = json(composition);
  const trace = { schema_version: "alchlang.application-messaging-trace/v1-candidate", source_sha256: digest(source), binding_sha256: digest(json(input)), composition_sha256: digest(sourceFile), compiled_composition_sha256: digest(compiledFile), references,
    deferred_integrations: model.integrations.filter(d => d.kind !== "publication" && d.kind !== "subscription").map(d => ({ id: d.id, kind: d.kind })), payload_type_join: "required", runtime_delivery_observed: false, authority_effect: "none" };
  return { sourceComposition, composition, trace, files: { "messaging-composition.json": sourceFile, "messaging-compiled.json": compiledFile, "messaging-trace.json": json(trace) } };
}

export function assertApplicationMessagingCurrent(source: string, input: unknown, compiler: Pick<DomainSpecCompiler, "compileMessagingComposition">, candidate: ReturnType<typeof lowerApplicationMessaging>): void {
  if (json(candidate) !== json(lowerApplicationMessaging(source, input, compiler))) fail("APPLICATION_MESSAGING_STALE", "$", "candidate differs from exact source and bindings");
}
