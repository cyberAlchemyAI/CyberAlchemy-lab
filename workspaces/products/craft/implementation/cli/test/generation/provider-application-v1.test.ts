import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHmac } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  assertProviderApplicationPlanV1,
  composeProviderApplicationV1,
} from "../../src/generation/provider-application-v1.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";
import * as wholeApplicationFacade from "../../src/whole-application.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");
const integration = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));

function json(relative: string): any {
  return JSON.parse(fs.readFileSync(path.join(example, relative), "utf8"));
}

function plan(language: "typescript" | "python" | "rust") {
  const whole = planWholeApplicationV1(path.join(example, "source"), json(`selections/${language}.json`), structuredClone(integration));
  return composeProviderApplicationV1(whole, json(`providers/${language}.json`), structuredClone(integration));
}

test("L2 public facade composes raw provider selection JSON into immutable plans", () => {
  assert.equal(wholeApplicationFacade.composeProviderApplicationV1, composeProviderApplicationV1);
  for (const language of ["typescript", "python", "rust"] as const) {
    const first = plan(language);
    const second = plan(language);
    assert.deepEqual(second, first);
    assertProviderApplicationPlanV1(first);
    assert.equal(Object.isFrozen(first), true);
    assert.equal(first.language, language);
    assert.equal(first.path_owners.length, first.artifacts.length);
    assert.equal(new Set(first.artifacts.map(item => item.relative_path)).size, first.artifacts.length);
    assert.equal(first.artifacts.filter(item => item.relative_path === ({ typescript: "package.json", python: "pyproject.toml", rust: "Cargo.toml" } as const)[language]).length, 1);
    const manifest = first.artifacts.find(item => item.relative_path === ({ typescript: "package.json", python: "pyproject.toml", rust: "Cargo.toml" } as const)[language])!.content;
    if (language === "typescript") assert.deepEqual(JSON.parse(manifest).engines, { node: "26.8.1" });
    if (language === "python") assert.match(manifest, /requires-python = ">=3\.11"/);
    if (language === "rust") assert.match(manifest, /edition = "2024"/);
    assert.equal(first.artifacts.some(item => item.relative_path === ".domainspec/providers/manifest.json"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === ".domainspec/providers/configuration.schema.json"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === "migrations/0001_domainspec_reference.sql"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === "migrations/0001_domainspec_reference.verify.sql"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === "migrations/manifest.json"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === ".domainspec/providers/failure-mappings.json"), true);
    assert.equal(first.artifacts.some(item => item.relative_path === ".domainspec/runtime-ports.json"), true);
    assert.equal(first.runtime_guarantees_observed, false);
    assert.equal(first.claim_ceiling, "provider-code-formation-and-static-compilation-only");
    assert.equal(first.authority_effect, "none");
  }
});

test("L2 runtime ports preserve one language-neutral integration contract", () => {
  const manifests = (["typescript", "python", "rust"] as const).map(language => {
    const formed = plan(language);
    const artifact = formed.artifacts.find(item => item.relative_path === ".domainspec/runtime-ports.json")!;
    assert.equal(formed.path_owners.find(item => item.relative_path === artifact.relative_path)?.owner, "provider-pack");
    return { artifact, value: JSON.parse(artifact.content) };
  });
  assert.equal(new Set(manifests.map(item => item.artifact.sha256)).size, 1);
  const manifest = manifests[0]!.value;
  assert.equal(manifest.schema_version, "domainspec.runtime-port-manifest/v1-candidate");
  assert.equal(manifest.required_execution_model, "async");
  assert.equal(manifest.runtime_guarantees_observed, false);
  assert.equal(manifest.mapping_bindings.length, 6);
  assert.equal(manifest.operation_requests[0].request_ref, "commerce:perform#request");
  assert.deepEqual(manifest.operation_requests[0].mapping_binding_refs, ["api-mapping:payment-webhook-request", "message-mapping:order-submitted-in"]);
  assert.deepEqual(manifest.operation_requests[0].bindings[0].parameters, [
    { parameter: "amount", source: { kind: "mapping-result", path: [] } },
    { parameter: "notice_input", source: { kind: "source-body", path: ["notice_input"] } },
  ]);
  assert.deepEqual(manifest.mapping_bindings.find((binding: any) => binding.binding_id === "message-mapping:order-submitted-out").inputs[0].source, { kind: "event-identity-reference", reference: "commerce:posted", path: ["order-id"] });
  assert.deepEqual(manifest.mapping_bindings.find((binding: any) => binding.binding_id === "api-mapping:authorize-request").result_type, { kind: "named", selector: "commerce:customer" });
  assert.deepEqual(manifest.ports.map((port: any) => [port.port_id, port.port_kind]), [
    ["external-api-binding:authorize-payment", "external-api-outbound"],
    ["inbound-endpoint:payment-webhook", "external-api-inbound"],
    ["persistence-binding:orders", "persistence"],
    ["publication:order-submitted", "message-publication"],
    ["subscription:billing-order", "message-subscription"],
  ]);
  assert.deepEqual(manifest.ports.find((port: any) => port.port_id === "persistence-binding:orders").transaction_refs, ["transaction-binding:submit-order"]);
  assert.equal(manifest.ports.find((port: any) => port.port_id === "subscription:billing-order").invokes_operation_ref, "commerce:perform");
  assert.equal(manifest.ports.find((port: any) => port.port_id === "inbound-endpoint:payment-webhook").invokes_operation_ref, "commerce:perform");
  assert.deepEqual(manifest.ports.find((port: any) => port.port_id === "publication:order-submitted").result_contract, {
    kind: "provider-acceptance-receipt",
    claim_ceiling: "provider-accepted",
    observation_boundary: "boundary:broker-publish-response",
    delivery_observed: false,
    consumer_completion_observed: false,
  });
  assert.equal(manifest.ports.find((port: any) => port.port_id === "publication:order-submitted").destination_environment_name, "ORDER_EVENTS_TOPIC");
  assert.deepEqual(manifest.transactions[0].participant_refs, ["participant:order-row", "participant:outbox-row"]);
});

test("L2 publication contracts return provider acceptance without collapsing delivery or completion", () => {
  const expected = {
    typescript: ["ProviderAcceptanceReceipt", "JetStreamClient", "acknowledgement.stream", "delivery_observed:false", "consumer_completion_observed:false"],
    python: ["ProviderAcceptanceReceipt", "JetStreamContext", "acknowledgement.stream", '"delivery_observed": False', '"consumer_completion_observed": False'],
    rust: ["ProviderAcceptanceReceipt", "jetstream::Context", "acknowledgement.stream", "delivery_observed:false", "consumer_completion_observed:false"],
  } as const;
  const files = {
    typescript: ["src/features/integration/application/contracts.ts", "src/providers/reference/messaging.ts"],
    python: ["src/commerce_corpus/features/integration/application/contracts.py", "src/commerce_corpus/providers/reference/messaging.py"],
    rust: ["src/features/integration/application/contracts.rs", "src/providers/reference/messaging.rs"],
  } as const;
  for (const language of ["typescript", "python", "rust"] as const) {
    const formed = plan(language);
    const content = files[language].map(relative => formed.artifacts.find(item => item.relative_path === relative)!.content).join("\n");
    for (const marker of expected[language]) assert.equal(content.includes(marker), true, `${language}:${marker}`);
    assert.equal(content.includes("provider-accepted"), true);
    assert.equal(content.includes("delivery_observed:true"), false);
    assert.equal(content.includes("consumer_completion_observed:true"), false);
  }
});

test("L2 provider composition rejects missing capabilities and undeclared failure matchers", () => {
  const missingCapability = structuredClone(integration);
  missingCapability.messaging.integration_kernel.provider_profiles[0].capability_set = ["topic"];
  const capabilityPlan = planWholeApplicationV1(path.join(example, "source"), json("selections/typescript.json"), missingCapability);
  assert.throws(() => composeProviderApplicationV1(capabilityPlan, json("providers/typescript.json"), missingCapability), /DS_PROVIDER_CAPABILITY_INCOMPATIBLE/);
  const missingFailure = structuredClone(integration);
  missingFailure.external_api.integration_kernel.failure_mappings[0].cases = missingFailure.external_api.integration_kernel.failure_mappings[0].cases.filter((item: any) => item.provider_failure_matcher !== "http:timeout");
  const failurePlan = planWholeApplicationV1(path.join(example, "source"), json("selections/typescript.json"), missingFailure);
  assert.throws(() => composeProviderApplicationV1(failurePlan, json("providers/typescript.json"), missingFailure), /DS_PROVIDER_FAILURE_UNDECLARED/);
  const wrongDestination = json("providers/typescript.json");
  wrongDestination.configuration.messaging_destinations[0].channel_ref = "channel:different-topic";
  const destinationPlan = planWholeApplicationV1(path.join(example, "source"), json("selections/typescript.json"), structuredClone(integration));
  assert.throws(() => composeProviderApplicationV1(destinationPlan, wrongDestination, structuredClone(integration)), /DS_PROVIDER_MESSAGING_DESTINATION_COVERAGE/);
});

test("L2 provider composition rejects an integration source other than the bound source", () => {
  const whole = planWholeApplicationV1(path.join(example, "source"), json("selections/typescript.json"), structuredClone(integration));
  const changed = structuredClone(integration);
  changed.source_id = "integration-source:different-valid-source";
  assert.throws(() => composeProviderApplicationV1(whole, json("providers/typescript.json"), changed), /DS_PROVIDER_INTEGRATION_SOURCE/);
});

test("L2 provider plans contain selected adapter and reachable bootstrap source only", () => {
  const expectations = {
    typescript: ["src/providers/reference/bootstrap.ts", "pg", "nats"],
    python: ["src/commerce_corpus/providers/reference/bootstrap.py", "psycopg", "nats-py"],
    rust: ["src/providers/reference/bootstrap.rs", "sqlx", "async-nats"],
  } as const;
  for (const language of ["typescript", "python", "rust"] as const) {
    const formed = plan(language);
    const [bootstrap, persistence, messaging] = expectations[language];
    const bootstrapBytes = formed.artifacts.find(item => item.relative_path === bootstrap)!.content;
    assert.equal(formed.artifacts.some(item => item.relative_path === bootstrap), true);
    assert.equal(formed.dependencies.some(item => item.library === persistence), true);
    assert.equal(formed.dependencies.some(item => item.library === messaging), true);
    assert.equal(formed.path_owners.find(item => item.relative_path === bootstrap)?.owner, "provider-pack");
    for (const marker of language === "typescript" ? ["Postgresql16OrderStore", "NatsJetStreamOrderPublisher", "FetchPaymentGateway", "createWebhookServer", "migrate"] : language === "python" ? ["Postgresql16OrderStore", "NatsJetStreamOrderPublisher", "HttpxPaymentGateway", "create_webhook_application", "migrate"] : ["Postgresql16OrderStore", "NatsJetStreamOrderPublisher", "ReqwestPaymentGateway", "webhook_router"]) assert.match(bootstrapBytes, new RegExp(marker));
  }
});

test("R05 TypeScript provider invokes exact mappings, one Operation, transactional state/outbox, NATS, and HTTP", async t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-r05-ts-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const formed = plan("typescript");
  for (const item of formed.artifacts) {
    const destination = path.join(temporary, item.relative_path);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, item.content);
  }
  const temporaryModules = path.join(temporary, "node_modules");
  fs.mkdirSync(path.join(temporaryModules, "@types"), { recursive: true });
  fs.symlinkSync(path.resolve(here, "../../node_modules/@types/node"), path.join(temporaryModules, "@types/node"), "dir");
  fs.mkdirSync(path.join(temporaryModules, "nats"), { recursive: true });
  fs.writeFileSync(path.join(temporaryModules, "nats/package.json"), JSON.stringify({ name: "nats", type: "module", exports: { ".": { types: "./index.d.ts", import: "./index.js" } } }));
  fs.writeFileSync(path.join(temporaryModules, "nats/index.js"), 'export const headers=()=>{const values=new Map();return{set:(name,value)=>values.set(name,value),get:name=>values.get(name)}};export const connect=async()=>({jetstream:()=>({}),drain:async()=>{}});\n');
  fs.writeFileSync(path.join(temporaryModules, "nats/index.d.ts"), 'export interface MsgHdrs { set(name:string,value:string):void; get(name:string):string|undefined; }\nexport function headers():MsgHdrs;\nexport interface JetStreamClient { publish(subject:string,payload:Uint8Array,options?:{headers?:MsgHdrs}):Promise<{stream:string;seq:number}>; }\nexport interface NatsConnection { jetstream():JetStreamClient; drain():Promise<void>; }\nexport function connect(options:{servers:string}):Promise<NatsConnection>;\n');
  fs.mkdirSync(path.join(temporaryModules, "pg"), { recursive: true });
  fs.writeFileSync(path.join(temporaryModules, "pg/package.json"), JSON.stringify({ name: "pg", type: "module", exports: { ".": { types: "./index.d.ts", import: "./index.js" } } }));
  fs.writeFileSync(path.join(temporaryModules, "pg/index.js"), 'export class Pool { constructor(_options){} async connect(){throw new Error("stub")} async query(){return{rows:[]}} async end(){} }\n');
  fs.writeFileSync(path.join(temporaryModules, "pg/index.d.ts"), 'export interface QueryResult<Row=Record<string,unknown>> { rows:Row[]; }\nexport interface PoolClient { query<Row=Record<string,unknown>>(sql:string,values?:readonly unknown[]):Promise<QueryResult<Row>>; release():void; }\nexport class Pool { constructor(options?:{connectionString?:string}); connect():Promise<PoolClient>; query<Row=Record<string,unknown>>(sql:string,values?:readonly unknown[]):Promise<QueryResult<Row>>; end():Promise<void>; }\n');
  const compiler = path.resolve(here, "../../node_modules/typescript/bin/tsc");
  const compiled = spawnSync(process.execPath, [compiler, "-p", "tsconfig.json", "--noEmit", "--types", "node", "--pretty", "false"], { cwd: temporary, encoding: "utf8" });
  assert.equal(compiled.status, 0, `${compiled.stdout}\n${compiled.stderr}`);

  const queries: { sql: string; values: readonly unknown[] }[] = [];
  let released = 0;
  const client = {
    query: async (sql: string, values: readonly unknown[] = []) => { queries.push({ sql, values }); return { rows: [] }; },
    release: () => { released += 1; },
  };
  const pool = { connect: async () => client, query: async () => ({ rows: [] }) };
  const persistence = await import(pathToFileURL(path.join(temporary, "src/providers/reference/persistence.ts")).href) as any;
  const applicationModule = await import(pathToFileURL(path.join(temporary, "src/providers/reference/application.ts")).href) as any;
  const store = new persistence.Postgresql16OrderStore(pool);
  const application = new applicationModule.CommerceApplicationRuntime(store);
  const order = {
    billing_customer_id: "7",
    choice: { variant: "Some", payload: { quantity: "5", note: null } },
    customer: { id: "7", name: "Ada" },
    id: "9",
    labels: ["priority"],
    lines: [{ quantity: "2", note: "first" }],
    money: { quantity: "25", note: null },
    tags: ["new", "paid"],
  };
  const notice = { occurrence: { "event-id": "evt-9" }, occurredAt: "2026-09-16T12:00:00Z", payload: { "order-id": "9", delta: "1", ratio: 1 } };
  const webhook = await application.handleWebhook({ amount: order, notice_input: notice });
  assert.deepEqual(webhook, { statusCode: 200, body: { id: 9n, name: "accepted" } });
  assert.equal(queries.filter(item => item.sql === "BEGIN").length, 1);
  assert.equal(queries.filter(item => item.sql.includes('INSERT INTO "orders"')).length, 1);
  assert.equal(queries.filter(item => item.sql.includes('INSERT INTO "domainspec_outbox"')).length, 1);
  assert.equal(queries.filter(item => item.sql === "COMMIT").length, 1);
  assert.equal(released, 1);

  const published: { subject: string; payload: unknown; messageId: string | undefined }[] = [];
  const messaging = await import(pathToFileURL(path.join(temporary, "src/providers/reference/messaging.ts")).href) as any;
  const publisher = new messaging.NatsJetStreamOrderPublisher({
    publish: async (subject: string, bytes: Uint8Array, options: { headers?: { get(name: string): string | undefined } }) => {
      published.push({ subject, payload: JSON.parse(new TextDecoder().decode(bytes)), messageId: options.headers?.get("Nats-Msg-Id") });
      return { stream: "ORDERS", seq: 4 };
    },
  }, "orders.test");
  const receipt = await publisher.publish({ type: "posted", version: "1", occurrence: { "event-id": "evt-9" }, occurredAt: notice.occurredAt, payload: { "order-id": 9n, delta: 1n, ratio: 1 } });
  assert.deepEqual(published, [{ subject: "orders.test", payload: { id: "9", name: "integration" }, messageId: "evt-9" }]);
  assert.deepEqual(receipt, { acceptance_boundary_ref: "acceptance:order-event-publish", provider_acknowledgement_ref: "ORDERS:4", claim_ceiling: "provider-accepted", delivery_observed: false, consumer_completion_observed: false });

  const outbound = await import(pathToFileURL(path.join(temporary, "src/providers/reference/outbound-http.ts")).href) as any;
  const originalFetch = globalThis.fetch;
  let requestBody: unknown;
  globalThis.fetch = async (_input, init) => { requestBody = JSON.parse(String(init?.body)); return new Response(JSON.stringify(order), { status: 200, headers: { "content-type": "application/json" } }); };
  try {
    const authorized = await new outbound.FetchPaymentGateway("https://payments.invalid").authorize({ ...order, id: 9n, billing_customer_id: 7n, customer: { id: 7n, name: "Ada" }, money: { quantity: 25n, note: null }, lines: [{ quantity: 2n, note: "first" }] });
    assert.deepEqual(requestBody, { id: "9", name: "integration" });
    assert.equal(authorized.id, 9n);
  } finally {
    globalThis.fetch = originalFetch;
  }

  const lifecycle: string[] = [];
  const entrypoint = await import(pathToFileURL(path.join(temporary, "src/providers/reference/entrypoint.ts")).href) as any;
  const lifecyclePool = {
    connect: async () => client,
    query: async () => { lifecycle.push("migrate"); return { rows: [] }; },
    end: async () => { lifecycle.push("database-end"); },
  };
  const running = await entrypoint.startReferenceApplication({
    DATABASE_URL: "postgres://reference",
    INBOUND_BIND_ADDRESS: "127.0.0.1:0",
    NATS_URL: "nats://reference",
    PAYMENT_BASE_URL: "https://payments.invalid",
    WEBHOOK_SECRET: "reference-secret",
    ORDER_EVENTS_TOPIC: "orders.runtime",
  }, {
    database: async () => { lifecycle.push("database-connect"); return lifecyclePool; },
    messaging: async () => { lifecycle.push("messaging-connect"); return { connection: { drain: async () => { lifecycle.push("messaging-drain"); } }, jetstream: {} }; },
    listen: async () => { lifecycle.push("listen"); },
    close: async () => { lifecycle.push("server-close"); },
  });
  assert.deepEqual(running.health(), { status: "ready" });
  await running.stop();
  await running.stop();
  assert.deepEqual(running.health(), { status: "stopped" });
  assert.deepEqual(lifecycle, ["database-connect", "messaging-connect", "migrate", "listen", "server-close", "messaging-drain", "database-end"]);
});

test("R05 Python provider invokes exact mappings, one Operation, transactional state/outbox, NATS, and HTTP", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-r05-py-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const formed = plan("python");
  for (const item of formed.artifacts) {
    const destination = path.join(temporary, item.relative_path);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, item.content);
  }
  const compiled = spawnSync("python3", ["-m", "compileall", "-q", path.join(temporary, "src")], { encoding: "utf8" });
  assert.equal(compiled.status, 0, `${compiled.stdout}\n${compiled.stderr}`);
  const probe = String.raw`
import asyncio
import json
import sys
import types

class AsyncConnection:
    @classmethod
    def __class_getitem__(cls, item): return cls
class UniqueViolation(Exception): pass
psycopg = types.ModuleType("psycopg"); psycopg.AsyncConnection = AsyncConnection
psycopg_errors = types.ModuleType("psycopg.errors"); psycopg_errors.UniqueViolation = UniqueViolation
sys.modules.update({"psycopg": psycopg, "psycopg.errors": psycopg_errors})

class JetStreamContext: pass
nats = types.ModuleType("nats")
nats_js = types.ModuleType("nats.js")
nats_client = types.ModuleType("nats.js.client"); nats_client.JetStreamContext = JetStreamContext
sys.modules.update({"nats": nats, "nats.js": nats_js, "nats.js.client": nats_client})

class TimeoutException(Exception): pass
class HTTPError(Exception): pass
class AsyncClient: pass
httpx = types.ModuleType("httpx")
httpx.TimeoutException = TimeoutException; httpx.HTTPError = HTTPError; httpx.AsyncClient = AsyncClient
sys.modules["httpx"] = httpx

sys.path.insert(0, sys.argv[1])
from commerce_corpus.features.commerce.domain.events.posted import event_posted
from commerce_corpus.providers.reference.application import CommerceApplicationRuntime
from commerce_corpus.providers.reference.messaging import NatsJetStreamOrderPublisher
from commerce_corpus.providers.reference.outbound_http import HttpxPaymentGateway
from commerce_corpus.providers.reference.persistence import Postgresql16OrderStore

order = {
    "billing_customer_id": "7",
    "choice": {"variant": "Some", "payload": {"quantity": "5", "note": None}},
    "customer": {"id": "7", "name": "Ada"},
    "id": "9",
    "labels": ["priority"],
    "lines": [{"quantity": "2", "note": "first"}],
    "money": {"quantity": "25", "note": None},
    "tags": ["new", "paid"],
}
notice = {"occurrence": {"event-id": "evt-9"}, "occurredAt": "2026-09-16T12:00:00Z", "payload": {"order-id": "9", "delta": "1", "ratio": 1}}

class Cursor:
    def __init__(self, connection): self.connection, self.rows = connection, []
    async def __aenter__(self): return self
    async def __aexit__(self, kind, value, trace): return False
    async def execute(self, sql, parameters=()): self.connection.queries.append((sql, parameters))
    async def fetchall(self): return self.rows
class Connection:
    def __init__(self): self.queries = []
    def cursor(self): return Cursor(self)
class Ack:
    stream = "ORDERS"
    seq = 4
class JetStream:
    def __init__(self): self.published = []
    async def publish(self, subject, payload, headers=None):
        self.published.append((subject, json.loads(payload), headers))
        return Ack()
class Response:
    status_code = 200
    is_success = True
    def json(self): return order
class HttpClient:
    def __init__(self): self.requests = []
    async def post(self, url, json):
        self.requests.append((url, json))
        return Response()

async def run():
    connection = Connection()
    application = CommerceApplicationRuntime(Postgresql16OrderStore(connection))
    webhook = await application.handle_webhook({"amount": order, "notice_input": notice})
    assert webhook["status_code"] == 200
    assert webhook["body"]["id"] == 9 and webhook["body"]["name"] == "accepted"
    sql = [row[0] for row in connection.queries]
    assert sql.count("BEGIN") == 1
    assert len([value for value in sql if 'INSERT INTO "orders"' in value]) == 1
    assert len([value for value in sql if 'INSERT INTO "domainspec_outbox"' in value]) == 1
    assert sql.count("COMMIT") == 1
    outbox = next(parameters for statement, parameters in connection.queries if 'INSERT INTO "domainspec_outbox"' in statement)
    assert json.loads(outbox[4]) == {"type": "posted", "version": "1", "occurrence": {"event-id": "evt-9"}, "occurredAt": "2026-09-16T12:00:00Z", "payload": {"order-id": 9, "delta": 1, "ratio": 1.0}}

    jetstream = JetStream()
    receipt = await NatsJetStreamOrderPublisher(jetstream, "orders.test").publish(event_posted(notice))
    assert jetstream.published == [("orders.test", {"id": 9, "name": "integration"}, {"Nats-Msg-Id": "evt-9"})], repr(jetstream.published)
    assert receipt == {"acceptance_boundary_ref": "acceptance:order-event-publish", "provider_acknowledgement_ref": "ORDERS:4", "claim_ceiling": "provider-accepted", "delivery_observed": False, "consumer_completion_observed": False}

    client = HttpClient()
    authorized = await HttpxPaymentGateway(client, "https://payments.invalid").authorize(order)
    assert client.requests == [("https://payments.invalid/authorize", {"id": 9, "name": "integration"})]
    assert authorized["id"] == 9

asyncio.run(run())
print(json.dumps({"status": "pass"}))
`;
  const result = spawnSync("python3", ["-B", "-c", probe, path.join(temporary, "src")], { encoding: "utf8" });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.deepEqual(JSON.parse(result.stdout), { status: "pass" });
});

test("R06 Python entrypoint orders readiness and graceful resource shutdown", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-r06-py-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const formed = plan("python");
  for (const item of formed.artifacts) {
    const destination = path.join(temporary, item.relative_path);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, item.content);
  }
  const probe = String.raw`
import asyncio
import json
import sys
import types

class AsyncConnection:
    @classmethod
    def __class_getitem__(cls, item): return cls
class UniqueViolation(Exception): pass
psycopg = types.ModuleType("psycopg"); psycopg.AsyncConnection = AsyncConnection
psycopg_errors = types.ModuleType("psycopg.errors"); psycopg_errors.UniqueViolation = UniqueViolation
sys.modules.update({"psycopg": psycopg, "psycopg.errors": psycopg_errors})

class JetStreamContext: pass
nats = types.ModuleType("nats"); nats.connect = None
nats_js = types.ModuleType("nats.js")
nats_client = types.ModuleType("nats.js.client"); nats_client.JetStreamContext = JetStreamContext
sys.modules.update({"nats": nats, "nats.js": nats_js, "nats.js.client": nats_client})

class TimeoutException(Exception): pass
class HTTPError(Exception): pass
class AsyncClient: pass
httpx = types.ModuleType("httpx"); httpx.TimeoutException = TimeoutException; httpx.HTTPError = HTTPError; httpx.AsyncClient = AsyncClient
sys.modules["httpx"] = httpx

class Config:
    def __init__(self, *args, **kwargs): pass
class UvicornServer: pass
uvicorn = types.ModuleType("uvicorn"); uvicorn.Config = Config; uvicorn.Server = UvicornServer
sys.modules["uvicorn"] = uvicorn

class Starlette:
    def __init__(self, routes): self.routes = routes
class Request: pass
class Response:
    def __init__(self, content=None, status_code=200, media_type=None): self.status_code = status_code
class JSONResponse(Response): pass
class Route:
    def __init__(self, path, endpoint, methods): self.path, self.endpoint, self.methods = path, endpoint, methods
starlette = types.ModuleType("starlette")
applications = types.ModuleType("starlette.applications"); applications.Starlette = Starlette
requests = types.ModuleType("starlette.requests"); requests.Request = Request
responses = types.ModuleType("starlette.responses"); responses.Response = Response; responses.JSONResponse = JSONResponse
routing = types.ModuleType("starlette.routing"); routing.Route = Route
sys.modules.update({"starlette": starlette, "starlette.applications": applications, "starlette.requests": requests, "starlette.responses": responses, "starlette.routing": routing})

sys.path.insert(0, sys.argv[1])
from commerce_corpus.providers.reference.entrypoint import start_reference_application

events = []
class Cursor:
    async def __aenter__(self): return self
    async def __aexit__(self, kind, value, trace): return False
    async def execute(self, sql, parameters=()): events.append("migrate")
class Database:
    def cursor(self): return Cursor()
    async def close(self): events.append("database-close")
class Messaging:
    async def drain(self): events.append("messaging-drain")
class HttpClient:
    async def aclose(self): events.append("http-close")
class Server:
    def __init__(self): self.started, self.should_exit = False, False
    async def serve(self):
        events.append("serve")
        while not self.should_exit: await asyncio.sleep(0)
        events.append("serve-stop")
class Connectors:
    async def database(self, url): events.append("database-connect"); return Database()
    async def messaging(self, url): events.append("messaging-connect"); return Messaging(), JetStreamContext()
    def http_client(self): events.append("http-client"); return HttpClient()
    def server(self, application, address): events.append("server-create"); return Server()
    async def wait_started(self, server, task): events.append("wait-started"); await asyncio.sleep(0); server.started = True

async def run():
    running = await start_reference_application({"DATABASE_URL":"postgres://reference","INBOUND_BIND_ADDRESS":"127.0.0.1:0","NATS_URL":"nats://reference","PAYMENT_BASE_URL":"https://payments.invalid","WEBHOOK_SECRET":"reference-secret","ORDER_EVENTS_TOPIC":"orders.runtime"}, Connectors())
    assert running.health() == {"status": "ready"}
    await running.stop(); await running.stop()
    assert running.health() == {"status": "stopped"}
    assert events == ["database-connect","messaging-connect","http-client","migrate","server-create","wait-started","serve","serve-stop","messaging-drain","http-close","database-close"], events
asyncio.run(run())
print(json.dumps({"status":"pass"}))
`;
  const result = spawnSync("python3", ["-B", "-c", probe, path.join(temporary, "src")], { encoding: "utf8" });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.deepEqual(JSON.parse(result.stdout), { status: "pass" });
});

test("R05 Rust provider invokes exact mappings, one Operation, transactional state/outbox, NATS, and HTTP", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-r05-rs-"));
  const cargoTarget = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-r05-rs-target-"));
  t.after(() => { fs.rmSync(temporary, { recursive: true, force: true }); fs.rmSync(cargoTarget, { recursive: true, force: true }); });
  const formed = plan("rust");
  for (const item of formed.artifacts) {
    const destination = path.join(temporary, item.relative_path);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, item.content);
  }
  const persistence = formed.artifacts.find(item => item.relative_path === "src/providers/reference/persistence.rs")!.content;
  const messaging = formed.artifacts.find(item => item.relative_path === "src/providers/reference/messaging.rs")!.content;
  const outbound = formed.artifacts.find(item => item.relative_path === "src/providers/reference/outbound_http.rs")!.content;
  const application = formed.artifacts.find(item => item.relative_path === "src/providers/reference/application.rs")!.content;
  assert.match(persistence, /impl PerformStore for Postgresql16OrderStore/);
  assert.match(persistence, /INSERT INTO "domainspec_outbox"/);
  assert.doesNotMatch(persistence, /ContractOrderStore|SELECT \$1::text/);
  assert.match(messaging, /invoke_message_mapping_order_submitted_out/);
  assert.match(messaging, /Nats-Msg-Id/);
  assert.match(outbound, /invoke_api_mapping_authorize_request/);
  assert.match(outbound, /invoke_api_mapping_authorize_response/);
  assert.match(application, /perform_request/);
  const environment = { ...process.env, CARGO_TARGET_DIR: cargoTarget };
  const clippy = spawnSync("cargo", ["clippy", "--locked", "--offline", "--", "-D", "warnings"], { cwd: temporary, env: environment, encoding: "utf8", timeout: 300_000 });
  assert.equal(clippy.status, 0, `${clippy.stdout}\n${clippy.stderr}`);
  const result = spawnSync("cargo", ["test", "--locked", "--offline"], { cwd: temporary, env: environment, encoding: "utf8", timeout: 300_000 });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.match(result.stdout, /3 passed/);
});

test("R06 generated applications expose executable entrypoints and pinned lifecycle dependencies", () => {
  const typescript = plan("typescript");
  const typescriptPackage = JSON.parse(typescript.artifacts.find(item => item.relative_path === "package.json")!.content);
  assert.equal(typescriptPackage.scripts.start, "tsc --noEmit false --outDir dist && node dist/providers/reference/main.js");
  assert.equal(typescript.artifacts.some(item => item.relative_path === "src/providers/reference/entrypoint.ts"), true);
  assert.equal(typescript.artifacts.some(item => item.relative_path === "src/providers/reference/main.ts"), true);

  const python = plan("python");
  const pyproject = python.artifacts.find(item => item.relative_path === "pyproject.toml")!.content;
  const requirements = python.artifacts.find(item => item.relative_path === "requirements.lock")!.content;
  assert.match(pyproject, /uvicorn==0\.53\.0/);
  assert.match(pyproject, /domainspec-application = "commerce_corpus\.providers\.reference\.main:main"/);
  assert.match(requirements, /^click==8\.5\.0$/m);
  assert.match(requirements, /^uvicorn==0\.53\.0$/m);
  assert.equal(python.artifacts.some(item => item.relative_path === "src/commerce_corpus/providers/reference/entrypoint.py"), true);
  assert.equal(python.artifacts.some(item => item.relative_path === "src/commerce_corpus/providers/reference/main.py"), true);

  const rust = plan("rust");
  const cargo = rust.artifacts.find(item => item.relative_path === "Cargo.toml")!.content;
  assert.match(cargo, /tokio = \{ version = "=1\.47\.1", features = \["macros", "net", "rt-multi-thread", "signal"\] \}/);
  assert.equal(rust.artifacts.some(item => item.relative_path === "src/providers/reference/entrypoint.rs"), true);
  assert.equal(rust.artifacts.some(item => item.relative_path === "src/main.rs"), true);
});

test("L2 generated migrations preserve complete required fields and verify their physical contract", () => {
  const formed = plan("typescript");
  const migration = formed.artifacts.find(item => item.relative_path === "migrations/0001_domainspec_reference.sql")!.content;
  const verification = formed.artifacts.find(item => item.relative_path === "migrations/0001_domainspec_reference.verify.sql")!.content;
  assert.match(migration, /"customers" \("id" TEXT PRIMARY KEY, "name" TEXT NOT NULL\)/);
  assert.match(migration, /"billing-customer-id" TEXT NOT NULL/);
  assert.match(migration, /CREATE TABLE IF NOT EXISTS "domainspec_outbox"/);
  assert.match(migration, /"publication_id" TEXT NOT NULL/);
  assert.match(migration, /CREATE TABLE IF NOT EXISTS "domainspec_inbox"/);
  assert.match(migration, /"subscription_id" TEXT NOT NULL/);
  assert.match(migration, /CREATE TABLE IF NOT EXISTS "domainspec_dead_letter"/);
  assert.match(migration, /"failure_class" TEXT NOT NULL/);
  assert.match(migration, /FOREIGN KEY \("order-id"\) REFERENCES "orders" \("id"\)/);
  assert.equal(migration.startsWith("BEGIN;\n"), true);
  assert.equal(migration.trimEnd().endsWith("COMMIT;"), true);
  assert.ok(migration.indexOf('CREATE TABLE IF NOT EXISTS "orders"') < migration.indexOf('FOREIGN KEY ("order-id") REFERENCES "orders"'));
  assert.match(migration, /INSERT INTO domainspec_migrations \(id\).*ON CONFLICT \(id\) DO NOTHING/);
  assert.match(verification, /information_schema\.columns/);
  assert.match(verification, /pg_constraint/);
  assert.match(verification, /missing index: orders_customer_id_idx/);
  assert.match(verification, /missing index: domainspec_outbox_pending_idx/);
  assert.match(verification, /missing index: domainspec_inbox_subscription_idx/);
  assert.match(verification, /missing index: domainspec_dead_letter_channel_idx/);
  assert.match(verification, /missing migration ledger row: migration:orders-v1-to-v2/);
  assert.match(verification, /column contract mismatch: customers/);
  assert.match(verification, /column contract mismatch: orders/);
});

test("L2 provider artifacts expose environment references without embedding secret values", () => {
  const forbidden = ["postgres://user:password", "nats://token@", "super-secret-webhook"];
  for (const language of ["typescript", "python", "rust"] as const) {
    const bytes = plan(language).artifacts.map(item => item.content).join("\n");
    for (const name of ["DATABASE_URL", "INBOUND_BIND_ADDRESS", "NATS_URL", "PAYMENT_BASE_URL", "WEBHOOK_SECRET", "ORDER_EVENTS_TOPIC"]) assert.match(bytes, new RegExp(name));
    for (const value of forbidden) assert.doesNotMatch(bytes, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});

test("L2 signed webhook adapters authenticate raw bytes before invoking application handlers", () => {
  const expectations = {
    typescript: {
      inbound: "src/providers/reference/inbound-http.ts",
      bootstrap: "src/providers/reference/bootstrap.ts",
      verify: "timingSafeEqual(received,expected)",
      guard: "if(!isValidWebhookSignature(body,signature,secret))",
      handler: "await onWebhook(body.toString(\"utf8\"))",
    },
    python: {
      inbound: "src/commerce_corpus/providers/reference/inbound_http.py",
      bootstrap: "src/commerce_corpus/providers/reference/bootstrap.py",
      verify: "hmac.compare_digest(expected, signature.lower())",
      guard: "if not is_valid_webhook_signature(body, request.headers.get(_SIGNATURE_HEADER), secret):",
      handler: "await on_webhook(body)",
    },
    rust: {
      inbound: "src/providers/reference/inbound_http.rs",
      bootstrap: "src/providers/reference/bootstrap.rs",
      verify: "mac.verify_slice(&received).is_ok()",
      guard: "if !is_valid_webhook_signature(&body,signature,&state.secret)",
      handler: "(state.on_webhook)(body.to_vec())",
    },
  } as const;
  for (const language of ["typescript", "python", "rust"] as const) {
    const formed = plan(language);
    const expected = expectations[language];
    const inbound = formed.artifacts.find(item => item.relative_path === expected.inbound)!.content;
    const bootstrap = formed.artifacts.find(item => item.relative_path === expected.bootstrap)!.content;
    assert.match(inbound, /x-domainspec-signature/);
    assert.match(inbound, /sha256|Sha256/);
    assert.equal(inbound.includes(expected.verify), true, `${language}:constant-time-verification`);
    assert.equal(inbound.indexOf(expected.guard) >= 0, true, `${language}:signature-guard`);
    assert.equal(inbound.indexOf(expected.handler) > inbound.indexOf(expected.guard), true, `${language}:handler-after-guard`);
    assert.match(bootstrap, /WEBHOOK_SECRET|webhook_secret/);
  }
  const rust = plan("rust");
  const cargo = rust.artifacts.find(item => item.relative_path === "Cargo.toml")!.content;
  const lock = rust.artifacts.find(item => item.relative_path === "Cargo.lock")!.content;
  assert.match(cargo, /hmac = \{ version = "=0\.13\.0", default-features = false \}/);
  assert.match(cargo, /sha2 = \{ version = "=0\.11\.0", default-features = false \}/);
  assert.match(lock, /name = "hmac"\nversion = "0\.13\.0"/);
  assert.match(lock, /name = "sha2"\nversion = "0\.11\.0"/);
});

test("L2 generated TypeScript webhook rejects invalid signatures before its handler", async t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-webhook-ts-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const formed = plan("typescript");
  const source = formed.artifacts.find(item => item.relative_path === "src/providers/reference/inbound-http.ts")!.content;
  const modulePath = path.join(temporary, "inbound-http.ts");
  fs.writeFileSync(modulePath, source);
  const generated = await import(pathToFileURL(modulePath).href) as {
    createWebhookServer(bindAddress: string, secret: string, handler: (body: string) => Promise<void>): import("node:http").Server;
  };
  const secret = "domainspec-reference-secret";
  const body = "{\"order\":\"ord-á\"}";
  const observed: string[] = [];
  const server = generated.createWebhookServer("127.0.0.1:0", secret, async value => { observed.push(value); });
  await new Promise<void>((resolve, reject) => server.listen(0, "127.0.0.1", resolve).once("error", reject));
  t.after(() => new Promise<void>((resolve, reject) => server.close(error => error ? reject(error) : resolve())));
  const address = server.address();
  assert.ok(address !== null && typeof address === "object");
  const endpoint = `http://127.0.0.1:${address.port}/webhook`;
  const missing = await fetch(endpoint, { method: "POST", body });
  assert.equal(missing.status, 401);
  const invalid = await fetch(endpoint, { method: "POST", headers: { "x-domainspec-signature": "0".repeat(64) }, body });
  assert.equal(invalid.status, 401);
  assert.deepEqual(observed, []);
  const signature = createHmac("sha256", secret).update(Buffer.from(body, "utf8")).digest("hex");
  const valid = await fetch(endpoint, { method: "POST", headers: { "x-domainspec-signature": signature }, body });
  assert.equal(valid.status, 202);
  assert.deepEqual(observed, [body]);
});

test("L2 generated Python webhook rejects invalid signatures before its handler", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-webhook-py-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const formed = plan("python");
  const source = formed.artifacts.find(item => item.relative_path === "src/commerce_corpus/providers/reference/inbound_http.py")!.content;
  const modulePath = path.join(temporary, "inbound_http.py");
  fs.writeFileSync(modulePath, source);
  const probe = String.raw`
import asyncio
import hashlib
import hmac
import importlib.util
import sys
import types

class Starlette:
    def __init__(self, routes): self.routes = routes
class Request: pass
class Response:
    def __init__(self, status_code): self.status_code = status_code
class JSONResponse(Response): pass
class Route:
    def __init__(self, path, endpoint, methods): self.path, self.endpoint, self.methods = path, endpoint, methods

starlette = types.ModuleType("starlette")
applications = types.ModuleType("starlette.applications"); applications.Starlette = Starlette
requests = types.ModuleType("starlette.requests"); requests.Request = Request
responses = types.ModuleType("starlette.responses"); responses.Response = Response; responses.JSONResponse = JSONResponse
routing = types.ModuleType("starlette.routing"); routing.Route = Route
sys.modules.update({"starlette": starlette, "starlette.applications": applications, "starlette.requests": requests, "starlette.responses": responses, "starlette.routing": routing})

spec = importlib.util.spec_from_file_location("generated_inbound", sys.argv[1])
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
secret = "domainspec-reference-secret"
body = "{\"order\":\"ord-á\"}".encode("utf-8")
observed = []
async def on_webhook(value): observed.append(value)
application = module.create_webhook_application(secret, on_webhook)
endpoint = application.routes[0].endpoint
class Incoming:
    def __init__(self, signature): self.headers = {} if signature is None else {"x-domainspec-signature": signature}
    async def body(self): return body

async def run():
    assert (await endpoint(Incoming(None))).status_code == 401
    assert (await endpoint(Incoming("0" * 64))).status_code == 401
    assert observed == []
    signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert (await endpoint(Incoming(signature))).status_code == 202
    assert observed == [body]
asyncio.run(run())
`;
  const result = spawnSync("python3", ["-c", probe, modulePath], { encoding: "utf8" });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
});

test("L2 unselected whole-application plans remain byte-identical and contain no provider pack", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const left = planWholeApplicationV1(path.join(example, "source"), json(`selections/${language}.json`), structuredClone(integration));
    const right = planWholeApplicationV1(path.join(example, "source"), json(`selections/${language}.json`), structuredClone(integration));
    assert.deepEqual(right, left);
    assert.equal(left.artifacts.some(item => item.relative_path.includes("/providers/reference/") || item.relative_path.startsWith(".domainspec/providers/")), false);
  }
});
