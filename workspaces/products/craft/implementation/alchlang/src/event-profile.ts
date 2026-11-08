import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { resolveSqliteTransactionalOutboxEffect } from "./effect-adapters.js";
import { compileCarrier } from "./index.js";
import { parseDomainSource } from "./parser.js";
import { loadDomainSpecCompiler } from "./domainspec-cli.js";

export const EVENT_STAGES = ["outbox-committed", "provider-accepted", "consumer-received", "consumer-committed", "consumer-duplicate", "consumer-failed", "transport-unknown"] as const;
export type EventStage = typeof EVENT_STAGES[number];
export interface EventObservationProfile { id: string; transport: string; stages: EventStage[]; attributes: string[]; cardinalityBudget: number; mode: "simulation" }
type Block = { kind: string; id: string; fields: Record<string, string> };
const boundary = "intent-send-acceptance-delivery-and-commit-remain-distinct";
const shapes: Record<string, string[]> = {
  channel: ["purpose", "events", "publishers", "consumers"],
  delivery: ["semantics", "acknowledgement", "ordering", "visibility-seconds", "retention-seconds", "max-receives", "dead-letter", "deduplication"],
  "transport-failure": ["retry", "max-attempts", "backoff", "unknown-outcome", "terminal"],
  transport: ["operation", "event", "channel", "delivery", "failure", "envelope"],
  observation: ["transport", "correlation", "stages", "attributes", "cardinality-budget", "evidence"],
};
const fail = (message: string): never => { throw Error(`EVENT_PROFILE: ${message}`); };
const list = (value: string): string[] => {
  if (value === "none") return [];
  const values = value.split(",").map(v => v.trim());
  if (values.some(v => !v) || new Set(values).size !== values.length) fail("invalid or duplicate list item");
  return values;
};
const integer = (value: string): number => { if (!/^[1-9][0-9]*$/.test(value) || !Number.isSafeInteger(Number(value))) fail(`invalid integer ${value}`); return Number(value); };

/** This profile delegates business syntax to the existing Alch parser and delivery semantics to DomainSpec. */
export async function compileEventProfile(source: string) {
  const blocks: Block[] = []; const core: string[] = []; let current: Block | undefined; let profiles = 0;
  for (const [offset, line] of source.split(/\r?\n/).entries()) {
    if (!line.trim() || line.trimStart().startsWith("#")) { core.push(""); continue; }
    if (line === "profile event-function-v1") { profiles++; core.push(""); current = undefined; continue; }
    if (/^\s/.test(line) && current) {
      const match = /^  ([a-z][a-z-]*) (\S.*)$/.exec(line);
      if (!match || !shapes[current.kind].includes(match[1]) || Object.hasOwn(current.fields, match[1])) fail(`invalid/duplicate field at line ${offset + 1}`);
      current.fields[match![1]] = match![2]; core.push(""); continue;
    }
    current = undefined;
    const match = /^(channel|delivery|transport-failure|transport|observation) ([a-z][a-z0-9-]*):$/.exec(line);
    if (match) { current = { kind: match[1], id: match[2], fields: {} }; blocks.push(current); core.push(""); }
    else core.push(line);
  }
  if (profiles !== 1) fail("exactly one event-function-v1 profile required");
  const identities = new Set<string>();
  for (const block of blocks) {
    if (identities.has(block.id)) fail(`duplicate identity ${block.id}`); identities.add(block.id);
    for (const key of shapes[block.kind]) if (!Object.hasOwn(block.fields, key)) fail(`missing ${block.id}.${key}`);
  }
  const compiled = compileCarrier(parseDomainSource(core.join("\n")).carrier);
  const model = compiled.plan.model;
  const rows = (kind: string) => blocks.filter(b => b.kind === kind).sort((a,b) => a.id.localeCompare(b.id));
  const subject = (id: string) => `${model.domain_id}:${id}`;
  const operations = new Map(model.actions.filter(a => a.declaration_kind === "operation").map(a => [a.id, a]));
  const events = new Set(model.events.map(e => e.id));
  const operation = (id: string) => { if (!operations.has(id)) fail(`undeclared operation ${id}`); return subject(id); };
  const event = (id: string) => { if (!events.has(id)) fail(`undeclared event ${id}`); return subject(id); };
  const transports = rows("transport"); if (!transports.length) fail("transport required");
  // Reuse the existing registered persistence contract; no author-supplied JSON binding escape hatch.
  for (const t of transports) resolveSqliteTransactionalOutboxEffect(model,t.fields.operation,"sqlite-transactional-outbox");
  const persistence = JSON.parse(readFileSync(new URL("../../extensions/generatable-operation-patterns-v1/bindings/sqlite-transactional-outbox.binding-set.json",import.meta.url),"utf8")) as Record<string,unknown>;
  const bindingSet = {
    ...persistence,
    schema_version: "domainspec.system-integration-binding-set/v1", binding_set_id: `${model.domain_id}-messages`,
    profile_id: "domainspec.system-integration-profile/provider-neutral-v1", subject_ref: operation(transports[0].fields.operation),
    authority_effect: "none",
    message_channels: rows("channel").map(({id, fields:f}) => ({channel_id:id,purpose:f.purpose,allowed_event_refs:list(f.events).map(event),publisher_operation_refs:list(f.publishers).map(operation),consumer_operation_refs:list(f.consumers).map(operation),evidence_boundary:boundary})),
    delivery_policies: rows("delivery").map(({id,fields:f}) => ({policy_id:id,semantics:f.semantics,acknowledgement_boundary:f.acknowledgement,ordering_scope:f.ordering,visibility_timeout_seconds:integer(f["visibility-seconds"]),retention_seconds:integer(f["retention-seconds"]),max_receive_count:integer(f["max-receives"]),dead_letter_channel_ref:f["dead-letter"],deduplication_owner_ref:f.deduplication,evidence_boundary:boundary})),
    transport_failure_policies: rows("transport-failure").map(({id,fields:f}) => ({policy_id:id,retry_eligibility:f.retry,max_attempts:integer(f["max-attempts"]),backoff:f.backoff,unknown_outcome:f["unknown-outcome"],terminal_action:f.terminal,evidence_boundary:boundary})),
    transport_bindings: transports.map(({id,fields:f}) => ({binding_id:id,mode:"message",direction:"publish-subscribe",operation_ref:operation(f.operation),event_ref:event(f.event),channel_ref:f.channel,delivery_policy_ref:f.delivery,failure_policy_ref:f.failure,envelope_profile_ref:f.envelope,evidence_boundary:boundary})),
  };
  for (const t of transports) {
    const a = operations.get(t.fields.operation)!;
    if (!a.outcome_refs.includes(t.fields.event)) fail(`${a.id} does not emit ${t.fields.event}`);
  }
  const observations: EventObservationProfile[] = rows("observation").map(({id, fields:f}) => {
    if (!transports.some(t => t.id === f.transport)) fail(`unknown observed transport ${f.transport}`);
    if (f.correlation !== "message-id" || f.evidence !== "simulation") fail("prototype requires message-id correlation and simulation evidence");
    const stages = list(f.stages); if (!stages.length || stages.some(s => !EVENT_STAGES.includes(s as EventStage))) fail("unknown observation stage");
    const attributes = list(f.attributes); if (attributes.length !== 3 || ["message-id","event-type","stage"].some(a => !attributes.includes(a))) fail("closed observation attribute set required");
    const budget = integer(f["cardinality-budget"]); if (budget > 100000) fail("cardinality budget exceeds 100000");
    return {id,transport:f.transport,stages:stages as EventStage[],attributes,cardinalityBudget:budget,mode:"simulation"};
  });
  if (!observations.length) fail("observation profile required");
  const compiler = await loadDomainSpecCompiler();
  const targets = Object.fromEntries((["typescript","rust"] as const).map(language => [language, compiler.compileEventBindings(bindingSet, language)]));
  return {profile:"event-function-v1", domain_id:model.domain_id, bindingSet, observations, targets, business:compiled, source_sha256:createHash("sha256").update(source).digest("hex"), compiler:compiler.binding, authority_effect:"none"};
}

export async function buildEventProfile(file: string, output: string) {
  const result = await compileEventProfile(readFileSync(file,"utf8"));
  mkdirSync(output, {recursive:false});
  const json = (name:string,value:unknown) => writeFileSync(path.join(output,name),JSON.stringify(value,null,2)+"\n");
  json("binding-set.json",result.bindingSet); json("observations.json",result.observations);
  json("business-plan.json",result.business.plan);
  for (const language of ["typescript","rust"] as const) {
    json(`${language}.manifest.json`,result.targets[language].manifest);
    writeFileSync(path.join(output,`bindings.${language === "rust" ? "rs" : "ts"}`),result.targets[language].source);
  }
  json("build.json",{profile:result.profile,source_sha256:result.source_sha256,compiler:result.compiler,authority_effect:"none",runtime_guarantees_observed:false});
  return {status:"built",output:path.resolve(output),profile:result.profile,authority_effect:"none"};
}
