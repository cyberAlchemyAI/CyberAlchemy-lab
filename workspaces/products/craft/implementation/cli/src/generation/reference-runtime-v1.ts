import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { PlannedArtifact } from "./contracts.js";
import { assertProviderApplicationPlanV1, type ProviderApplicationPlanV1 } from "./provider-application-v1.js";

export interface ReferenceRuntimePlanV1 {
  readonly schema_version: "domainspec.reference-runtime-plan/v1-candidate";
  readonly language: "typescript";
  readonly project_id: string;
  readonly provider_application_plan_sha256: string;
  readonly artifacts: readonly PlannedArtifact[];
  readonly path_owners: readonly Readonly<{ relative_path: string; owner: ProviderApplicationPlanV1["path_owners"][number]["owner"] | "reference-runtime"; sha256: string }>[];
  readonly runtime_guarantees_observed: false;
  readonly claim_ceiling: "generated-reference-runtime-formation-only";
  readonly authority_effect: "none";
  readonly plan_sha256: string;
}

export class ReferenceRuntimePlanError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ReferenceRuntimePlanError";
  }
}

const snapshots = new WeakMap<ReferenceRuntimePlanV1, string>();
const fail = (code: string, pointer: string, message: string): never => { throw new ReferenceRuntimePlanError(code, pointer, message); };
const freeze = <T>(value: T): T => { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; };
const artifact = (relative_path: string, content: string): PlannedArtifact => freeze({ relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });

const RUNTIME_MIGRATION = `CREATE TABLE IF NOT EXISTS domainspec_runtime_migrations (id TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS domainspec_runtime_inbox (consumer_id TEXT NOT NULL, message_id TEXT NOT NULL, result JSONB NOT NULL, committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (consumer_id, message_id));
CREATE TABLE IF NOT EXISTS domainspec_runtime_dead_letters (message_id TEXT PRIMARY KEY, source_subject TEXT NOT NULL, payload JSONB NOT NULL, failure_class TEXT NOT NULL, attempts INTEGER NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
INSERT INTO domainspec_runtime_migrations (id) VALUES ('0002_reference_runtime') ON CONFLICT DO NOTHING;
`;

const RUNTIME_SOURCE = `import {createHash,createHmac,timingSafeEqual} from "node:crypto";
import type {JetStreamClient,JetStreamManager,NatsConnection} from "nats";
import {headers,StringCodec} from "nats";
import type {Pool} from "pg";
import {operationPerform} from "../features/commerce/application/operations/perform.js";
import type {OperationDependencies,OperationInput,OperationOutcome,OperationValue} from "../features/commerce/application/operations/perform.js";
import {NatsJetStreamOrderPublisher} from "../providers/reference/messaging.js";
import {Postgresql16OrderStore} from "../providers/reference/persistence.js";

export const CHANNELS=Object.freeze({topic:"orders.submitted",queue:"orders.work",stream:"orders.stream",deadLetter:"orders.dead-letter"});
export type RuntimeStage="payment-provider"|"application-commit"|"broker-acceptance"|"consumer-completion";
export type StageReceipt=Readonly<{stage:RuntimeStage;outcome:"accepted"|"committed"|"rejected"|"not-observed";reference:string}>;
export type ExecutionReceipt=Readonly<{schema_version:"domainspec.reference-runtime-execution/v1-candidate";order_id:string;stages:readonly StageReceipt[];operation:OperationOutcome;authority_effect:"none"}>;
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
const digest=(value:unknown):string=>createHash("sha256").update(JSON.stringify(jsonValue(value))).digest("hex");
type PaymentGateway=Readonly<{authorize(input:OperationValue):Promise<OperationValue>}>;
type OperationStore=OperationDependencies["store"];
export class PostgresOperationStore extends Postgresql16OrderStore implements OperationStore {}

export async function applyRuntimeMigration(pool:Pool,sql:string):Promise<void>{await pool.query(sql);}

export function commerceOperationInput(orderId:string,eventId:string,occurredAt:string,quantity:string):OperationInput{return Object.freeze({
  amount:Object.freeze({billing_customer_id:"7",choice:Object.freeze({variant:"Some" as const,payload:Object.freeze({quantity,note:null})}),customer:Object.freeze({id:"7",name:"Ada"}),id:orderId,labels:Object.freeze(["priority","web"]),lines:Object.freeze([Object.freeze({quantity,note:"primary"})]),money:Object.freeze({quantity,note:null}),tags:Object.freeze(["new","paid"])}),
  notice_input:Object.freeze({occurrence:Object.freeze({"event-id":eventId}),occurredAt,payload:Object.freeze({"order-id":orderId,delta:"1",ratio:1})})
});}

export async function configureNats(jsm:JetStreamManager,namespace:string):Promise<Readonly<{stream:string;subjects:readonly string[]}>>{
  const safe=namespace.replace(/[^A-Za-z0-9_-]/g,"_");const stream=("ORDERS_"+safe).toUpperCase();const subjects=Object.freeze([CHANNELS.topic,CHANNELS.queue,CHANNELS.stream,CHANNELS.deadLetter]);
  try{await jsm.streams.info(stream);}catch{await jsm.streams.add({name:stream,subjects:[...subjects]});}
  return Object.freeze({stream,subjects});
}

export async function authorizePayment(provider:PaymentGateway,input:OperationInput):Promise<StageReceipt>{
  try{await provider.authorize(input.amount as OperationValue);return Object.freeze({stage:"payment-provider",outcome:"accepted",reference:"provider-response:accepted"});}catch(error){return Object.freeze({stage:"payment-provider",outcome:"rejected",reference:error instanceof Error?error.message:"http:malformed-response:commerce:perform"});}
}

export async function dispatchOutbox(pool:Pool,js:JetStreamClient):Promise<readonly StageReceipt[]>{
  const receipts=await new NatsJetStreamOrderPublisher(js,CHANNELS.topic).publishPending(pool);
  return Object.freeze(receipts.map(receipt=>Object.freeze({stage:"broker-acceptance" as const,outcome:"accepted" as const,reference:receipt.provider_acknowledgement_ref})));
}

export async function executeCommerce(pool:Pool,js:JetStreamClient,payments:PaymentGateway,input:OperationInput):Promise<ExecutionReceipt>{
  const orderId=String(input.amount.id);const payment=await authorizePayment(payments,input);const stages:StageReceipt[]=[payment];
  if(payment.outcome!=="accepted")return Object.freeze({schema_version:"domainspec.reference-runtime-execution/v1-candidate",order_id:orderId,stages:Object.freeze([...stages]),operation:Object.freeze({status:"failed",stage:"payment-provider",code:payment.reference,continuation:"return-perform-error",cleanupFailed:false}),authority_effect:"none"});
  const operation=await operationPerform(input,Object.freeze({store:new PostgresOperationStore(pool)}));stages.push(Object.freeze({stage:"application-commit",outcome:operation.status==="committed"?"committed":"rejected",reference:operation.status==="committed"?"transaction:committed":operation.code}));
  if(operation.status==="committed")stages.push(...await dispatchOutbox(pool,js));
  stages.push(Object.freeze({stage:"consumer-completion",outcome:"not-observed",reference:"not-inferred-from-provider-acceptance"}));
  return Object.freeze({schema_version:"domainspec.reference-runtime-execution/v1-candidate",order_id:orderId,stages:Object.freeze(stages),operation,authority_effect:"none"});
}

export function classifyContinuation(matcher:string):Readonly<{matcher:string;classification:"retryable"|"non-retryable";effect_selected:false}>{return Object.freeze({matcher,classification:matcher==="http:timeout"||matcher==="broker:throttled"?"retryable":"non-retryable",effect_selected:false});}
export async function deadLetter(pool:Pool,js:JetStreamClient,messageId:string,payload:unknown,attempts:number,failureClass:string):Promise<StageReceipt>{await pool.query('INSERT INTO domainspec_runtime_dead_letters (message_id,source_subject,payload,failure_class,attempts) VALUES ($1,$2,$3::jsonb,$4,$5)',[messageId,CHANNELS.topic,JSON.stringify(jsonValue(payload)),failureClass,attempts]);const h=headers();h.set("Nats-Msg-Id","dead-"+messageId);const ack=await js.publish(CHANNELS.deadLetter,StringCodec().encode(JSON.stringify(jsonValue(payload))),{headers:h});return Object.freeze({stage:"broker-acceptance",outcome:"accepted",reference:"dead-letter-sequence:"+ack.seq});}
export function webhookSignature(secret:string,body:string):string{return createHmac("sha256",secret).update(body).digest("hex");}
export function verifyWebhookSignature(secret:string,body:string,provided:string|undefined):boolean{if(!provided)return false;const expected=Buffer.from(webhookSignature(secret,body));const actual=Buffer.from(provided);return expected.length===actual.length&&timingSafeEqual(expected,actual);}
export function projectOrodiObservation(receipt:ExecutionReceipt):Readonly<{schema_version:"domainspec.orodi-observation-input/v1-candidate";order_id:string;stage_outcomes:readonly string[];receipt_sha256:string;return_edge:"prohibited";authority_effect:"none"}>{return Object.freeze({schema_version:"domainspec.orodi-observation-input/v1-candidate",order_id:receipt.order_id,stage_outcomes:Object.freeze(receipt.stages.map(stage=>stage.stage+":"+stage.outcome)),receipt_sha256:digest(receipt),return_edge:"prohibited",authority_effect:"none"});}
export async function closeRuntime(pool:Pool,nc:NatsConnection):Promise<void>{await Promise.all([pool.end(),nc.drain()]);}
`;

const SCENARIO = `${canonicalJson({
  schema_version: "domainspec.reference-runtime-scenario/v1-candidate",
  scenario_id: "commerce-reference-runtime",
  semantic_operation: "commerce:perform",
  logical_event: "commerce:posted",
  message_type: "message-type:order-submitted-v1",
  channels: { topic: "channel:order-events-topic", queue: "channel:order-events-queue", stream: "channel:order-events-stream", dead_letter: "channel:order-events-dead-letter" },
  success: ["payment-provider-accepted", "application-transaction-committed", "outbox-message-formed", "broker-provider-accepted", "independent-topic-subscribers-observe", "queue-consumers-compete", "consumer-commit-precedes-ack", "duplicate-is-distinct-from-first-processing"],
  failures: ["duplicate-order-rolls-back-state-and-outbox", "payment-unauthorized-does-not-start-operation", "timeout-is-classified-without-selecting-retry", "bounded-terminal-failure-enters-dead-letter", "invalid-webhook-signature-does-not-invoke-operation"],
  stage_non_collapse: ["event-is-not-message", "commit-is-not-provider-acceptance", "provider-acceptance-is-not-consumer-completion"],
  orodi: { edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false } },
  authority_effect: "none",
})}\n`;

const PROOF_SOURCE = `import {createServer} from "node:http";
import {readFile} from "node:fs/promises";
import {connect,consumerOpts,createInbox,headers,StringCodec} from "nats";
import {Pool} from "pg";
import {applyRuntimeMigration,CHANNELS,classifyContinuation,closeRuntime,commerceOperationInput,configureNats,deadLetter,executeCommerce,projectOrodiObservation,webhookSignature} from "./runtime.js";
import {composeReferenceApplication} from "../providers/reference/bootstrap.js";
const assert:(condition:unknown,message:string)=>asserts condition=(condition,message)=>{if(!condition)throw new Error("REFERENCE_RUNTIME_ASSERTION:"+message);};
const wait=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
const withTimeout=async<T>(promise:Promise<T>,label:string):Promise<T>=>Promise.race([promise,new Promise<T>((_,reject)=>setTimeout(()=>reject(new Error("REFERENCE_RUNTIME_TIMEOUT:"+label)),5000))]);
const databaseUrl=process.env.DATABASE_URL,natsUrl=process.env.NATS_URL,secret=process.env.WEBHOOK_SECRET,runId=process.env.RUN_ID,mode=process.env.SCENARIO_MODE;
assert(databaseUrl&&natsUrl&&secret&&runId&&(mode==="success"||mode==="failure"),"configuration");
let paymentMode:"accept"|"unauthorized"="accept",webhookInvocations=0,providerWebhook:ReturnType<typeof composeReferenceApplication>["webhooks"]|undefined;
const fixtureOrder=commerceOperationInput("1","fixture-response","2026-09-15T11:58:00Z","25").amount;
const fixture=createServer(async(req,res)=>{for await(const _chunk of req){}if(req.url==="/authorize"){res.writeHead(paymentMode==="accept"?202:401,{"content-type":"application/json"}).end(JSON.stringify(fixtureOrder));return;}res.writeHead(404).end();});
await new Promise<void>((resolve,reject)=>{fixture.once("error",reject);fixture.listen(0,"127.0.0.1",resolve);});
const address=fixture.address();assert(address&&typeof address!=="string","fixture-address");const baseUrl="http://127.0.0.1:"+address.port;
const pool=new Pool({connectionString:databaseUrl});const nc=await connect({servers:natsUrl});const js=nc.jetstream();const jsm=await nc.jetstreamManager();
try{
  for(let attempt=1;attempt<=20;attempt++){try{await pool.query("SELECT 1");break;}catch(error){if(attempt===20)throw error;await wait(100);}}
  const providers=composeReferenceApplication({DATABASE_URL:databaseUrl,NATS_URL:natsUrl,PAYMENT_BASE_URL:baseUrl,INBOUND_BIND_ADDRESS:"127.0.0.1:0",WEBHOOK_SECRET:secret,ORDER_EVENTS_TOPIC:CHANNELS.topic},{database:pool,messaging:js,onWebhook:async()=>{webhookInvocations++;}});await providers.migrate();assert(providers.health().status==="unverified","provider-bootstrap-health");await providers.publisher.publish(Object.freeze({type:"posted" as const,version:"1" as const,occurrence:Object.freeze({"event-id":"provider-probe"}),occurredAt:"2026-09-15T11:59:00Z",payload:Object.freeze({"order-id":9000n})}));
  providerWebhook=providers.webhooks;await new Promise<void>((resolve,reject)=>{providerWebhook!.once("error",reject);providerWebhook!.listen(0,"127.0.0.1",resolve);});const providerAddress=providerWebhook.address();assert(providerAddress&&typeof providerAddress!=="string","provider-inbound-address");const providerBaseUrl="http://127.0.0.1:"+providerAddress.port;
  await applyRuntimeMigration(pool,await readFile("migrations/0002_domainspec_reference_runtime.sql","utf8"));const channelReceipt=await configureNats(jsm,runId);
  if(mode==="success"){
    const webhookBody=JSON.stringify(commerceOperationInput("9000","evt-webhook","2026-09-15T11:59:30Z","25"));const providerInbound=await fetch(new URL("/webhook",providerBaseUrl),{method:"POST",headers:{"x-domainspec-signature":webhookSignature(secret,webhookBody)},body:webhookBody});assert(providerInbound.status===200&&webhookInvocations===1,"provider-signed-inbound-http");await providers.flushOutbox();
    const counts={topicA:0,topicB:0,queueA:0,queueB:0};const topicA=nc.subscribe(CHANNELS.topic,{callback:()=>{counts.topicA++;}});const topicB=nc.subscribe(CHANNELS.topic,{callback:()=>{counts.topicB++;}});const queueA=nc.subscribe(CHANNELS.queue,{queue:"workers",callback:()=>{counts.queueA++;}});const queueB=nc.subscribe(CHANNELS.queue,{queue:"workers",callback:()=>{counts.queueB++;}});
    const opts=consumerOpts();opts.durable("billing_"+runId.replace(/[^A-Za-z0-9_-]/g,"_"));opts.manualAck();opts.ackExplicit();opts.deliverTo(createInbox());const subscription=await js.subscribe(CHANNELS.topic,opts);
    let ackAfterCommit=false;const consumer=withTimeout((async()=>{for await(const message of subscription){const id=message.headers?.get("Nats-Msg-Id");assert(id,"consumer-message-id");await pool.query("BEGIN");try{await pool.query("INSERT INTO domainspec_runtime_inbox (consumer_id,message_id,result) VALUES ($1,$2,$3::jsonb)",["billing-order-submitted",id,JSON.stringify({status:"committed"})]);await pool.query("COMMIT");message.ack();ackAfterCommit=true;return id;}catch(error){await pool.query("ROLLBACK");throw error;}}throw new Error("CONSUMER_CLOSED");})(),"consumer");
    const success=await executeCommerce(pool,js,providers.payments,commerceOperationInput("1001","evt-1001","2026-09-15T12:00:00Z","25"));const consumedId=await consumer;await wait(200);assert(success.operation.status==="committed","success-operation");assert(consumedId==="evt-1001"&&ackAfterCommit,"ack-after-commit");assert(counts.topicA===1&&counts.topicB===1,"topic-fanout");
    nc.publish(CHANNELS.queue,StringCodec().encode("queue-probe"));await js.publish(CHANNELS.stream,StringCodec().encode("stream-probe"));await wait(200);assert(counts.queueA+counts.queueB===1,"queue-competing-consumers");const database=await pool.query("SELECT (SELECT count(*)::int FROM orders) AS orders,(SELECT count(*)::int FROM domainspec_outbox) AS outbox,(SELECT count(*)::int FROM domainspec_runtime_inbox) AS inbox");assert(database.rows[0].orders===2&&database.rows[0].outbox===2&&database.rows[0].inbox===1,"database-effects");
    const h=headers();h.set("Nats-Msg-Id","evt-1001");const duplicate=await js.publish(CHANNELS.topic,StringCodec().encode("duplicate-probe"),{headers:h});assert(duplicate.duplicate===true,"deduplication-provider-ack");const observation=projectOrodiObservation(success);const serialized=JSON.stringify(observation);assert(observation.return_edge==="prohibited"&&!serialized.includes(secret)&&!serialized.includes("select_retries")&&!serialized.includes("payload"),"orodi-disclosure");const streamInfo=await jsm.streams.info(channelReceipt.stream);
    const report=Object.freeze({case:"success",run_id:runId,services:Object.freeze({postgresql:"ready",nats:"ready",http_fixture:"ready",provider_webhook:"ready"}),success:Object.freeze({receipt:success,database:database.rows[0],topic_counts:Object.freeze({a:counts.topicA,b:counts.topicB}),queue_total:counts.queueA+counts.queueB,ack_after_commit:ackAfterCommit,provider_duplicate:duplicate.duplicate,valid_webhook_status:providerInbound.status,webhook_invocations:webhookInvocations,stream_messages:streamInfo.state.messages}),orodi:observation});process.stdout.write(JSON.stringify(report,(_key,value)=>typeof value==="bigint"?value.toString():value)+"\\n");topicA.unsubscribe();topicB.unsubscribe();queueA.unsubscribe();queueB.unsubscribe();subscription.unsubscribe();
  }else{
    const baseline=await executeCommerce(pool,js,providers.payments,commerceOperationInput("2001","evt-baseline","2026-09-15T12:00:00Z","25"));assert(baseline.operation.status==="committed","failure-fixture-baseline");const before=await pool.query("SELECT count(*)::int AS orders,(SELECT count(*)::int FROM domainspec_outbox) AS outbox FROM orders");const duplicateOrder=await executeCommerce(pool,js,providers.payments,commerceOperationInput("2001","evt-baseline","2026-09-15T12:01:00Z","25"));const after=await pool.query("SELECT count(*)::int AS orders,(SELECT count(*)::int FROM domainspec_outbox) AS outbox FROM orders");assert(duplicateOrder.operation.status==="rejected"&&after.rows[0].orders===before.rows[0].orders&&after.rows[0].outbox===before.rows[0].outbox,"rollback-state-and-outbox");
    paymentMode="unauthorized";const unauthorized=await executeCommerce(pool,js,providers.payments,commerceOperationInput("2002","evt-2002","2026-09-15T12:02:00Z","25"));const afterUnauthorized=await pool.query("SELECT count(*)::int AS orders FROM orders");assert(unauthorized.operation.status==="failed"&&unauthorized.stages[0]?.reference==="http:unauthorized:commerce:perform"&&afterUnauthorized.rows[0].orders===1,"provider-rejection-before-operation");const retry=classifyContinuation("http:timeout");assert(retry.classification==="retryable"&&retry.effect_selected===false,"classification-only");const dlq=await deadLetter(pool,js,"evt-terminal",{safe:"payload"},5,"integration:max-attempts");const dead=await pool.query("SELECT attempts,failure_class FROM domainspec_runtime_dead_letters WHERE message_id='evt-terminal'");assert(dead.rows[0].attempts===5&&dead.rows[0].failure_class==="integration:max-attempts","dead-letter");const invalid=await fetch(new URL("/webhook",providerBaseUrl),{method:"POST",headers:{"x-domainspec-signature":"invalid"},body:"{}"});assert(invalid.status===401&&webhookInvocations===0,"invalid-signature-no-operation");
    const report=Object.freeze({case:"failure",run_id:runId,services:Object.freeze({postgresql:"ready",nats:"ready",http_fixture:"ready",provider_webhook:"ready"}),failures:Object.freeze({duplicate_order:duplicateOrder.operation.status,unauthorized:unauthorized.operation.status,unauthorized_reference:unauthorized.stages[0]?.reference,retry_classification:retry,dead_letter:dlq.reference,invalid_webhook_status:invalid.status,webhook_invocations:webhookInvocations})});process.stdout.write(JSON.stringify(report)+"\\n");
  }
}finally{if(providerWebhook?.listening)await new Promise<void>(resolve=>providerWebhook!.close(()=>resolve()));await new Promise<void>(resolve=>fixture.close(()=>resolve()));await closeRuntime(pool,nc);}
`;

export function assertReferenceRuntimePlanV1(value: unknown): asserts value is ReferenceRuntimePlanV1 {
  if (value === null || typeof value !== "object" || snapshots.get(value as ReferenceRuntimePlanV1) !== sha256(canonicalJson(value))) fail("DS_REFERENCE_RUNTIME_SNAPSHOT", "/plan", "runtime plan was not formed by this process or changed");
}

export function planReferenceRuntimeV1(provider: ProviderApplicationPlanV1): ReferenceRuntimePlanV1 {
  assertProviderApplicationPlanV1(provider);
  if (provider.language !== "typescript") fail("DS_REFERENCE_RUNTIME_LANGUAGE", "/language", "the bounded L3 reference runtime is TypeScript");
  const additions = Object.freeze([
    artifact("migrations/0002_domainspec_reference_runtime.sql", RUNTIME_MIGRATION),
    artifact("src/reference-runtime/runtime.ts", RUNTIME_SOURCE),
    artifact("src/reference-runtime/proof.ts", PROOF_SOURCE),
    artifact(".domainspec/runtime/scenario.json", SCENARIO),
  ]);
  const rows = [
    ...provider.artifacts.map(item => ({ artifact: item, owner: provider.path_owners.find(row => row.relative_path === item.relative_path)!.owner })),
    ...additions.map(item => ({ artifact: item, owner: "reference-runtime" as const })),
  ].sort((left, right) => left.artifact.relative_path.localeCompare(right.artifact.relative_path));
  const exact = new Set<string>(); const folded = new Map<string, string>();
  for (const row of rows) {
    const relative = row.artifact.relative_path;
    if (!relative || path.posix.normalize(relative) !== relative || relative.startsWith("/") || relative.includes("\\") || relative.split("/").includes("..")) fail("DS_REFERENCE_RUNTIME_PATH", `/artifacts/${relative}`, "unsafe path");
    if (exact.has(relative)) fail("DS_REFERENCE_RUNTIME_COLLISION", `/artifacts/${relative}`, "exact path collision");
    const fold = relative.toLocaleLowerCase("en-US"); if (folded.has(fold)) fail("DS_REFERENCE_RUNTIME_CASE_COLLISION", `/artifacts/${relative}`, `case collision with ${folded.get(fold)}`);
    exact.add(relative); folded.set(fold, relative);
  }
  const body = {
    schema_version: "domainspec.reference-runtime-plan/v1-candidate" as const,
    language: "typescript" as const,
    project_id: provider.project_id,
    provider_application_plan_sha256: provider.plan_sha256,
    artifacts: Object.freeze(rows.map(row => row.artifact)),
    path_owners: Object.freeze(rows.map(row => freeze({ relative_path: row.artifact.relative_path, owner: row.owner, sha256: row.artifact.sha256 }))),
    runtime_guarantees_observed: false as const,
    claim_ceiling: "generated-reference-runtime-formation-only" as const,
    authority_effect: "none" as const,
  };
  const result = freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
  snapshots.set(result, sha256(canonicalJson(result)));
  return result;
}
