import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { execFileSync } from "node:child_process";
import test from "node:test";
import { compileEventProfile } from "../src/event-profile.js";
import { EventObservationCollector, LocalEventFlow } from "../src/event-observations.js";
import { DurableSqliteTransactionalOutbox, type DurableOutboxRecord } from "../src/durable-outbox-runtime.js";
import { SqliteIdempotentInbox } from "../src/outbox-integrations.js";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const source = readFileSync(new URL("../../extensions/event-bindings-v1/order-events.alch",import.meta.url),"utf8");
const compilation = compileEventProfile(source);
const time = "2026-09-06T12:00:00.000Z";
const request = {aggregateType:"OrderOperation",aggregateId:"o1",expectedVersion:0,state:{status:"committed"},messages:[{messageId:"m1",eventType:"order-placed",payload:{orderId:"o1"},occurredAt:time}]};

test("event profile delegates delivery validation and produces equivalent TS/Rust binding contracts",async()=>{
 const c=await compilation;const d=await compileEventProfile(source);assert.deepEqual(c.targets,d.targets);
 const ts=c.targets.typescript.manifest as any, rust=c.targets.rust.manifest as any;
 assert.deepEqual(ts.canonical_bindings,rust.canonical_bindings);
 assert.equal(ts.canonical_bindings.delivery_policies[0].acknowledgement_boundary,"provider-accepted");
 const dir=mkdtempSync(path.join(tmpdir(),"alch-event-rust-"));
 try{writeFileSync(path.join(dir,"bindings.rs"),c.targets.rust.source);execFileSync("rustc",["--crate-type","lib",path.join(dir,"bindings.rs"),"-o",path.join(dir,"bindings.rlib")]);}
 finally{rmSync(dir,{recursive:true,force:true});}
});

test("event profile rejects unsupported guarantees, reference drift and duplicate fields",async()=>{
 for(const [before,after] of [
  ["acknowledgement provider-accepted","acknowledgement application-committed"],
  ["semantics at-least-once","semantics exactly-once"],
  ["consumers record-order","consumers absent-operation"],
  ["event order-placed","event missing-event"],
  ["channel orders\n","channel unknown-channel\n"],
  ["max-attempts 5","max-attempts 0"],
  ["correlation message-id","correlation order-id"],
  ["evidence simulation","evidence live"],
  ["visibility-seconds 60","visibility-seconds 60\n  visibility-seconds 90"],
  ["event order-placed\n  channel","event order-placed\n  unknown true\n  channel"],
 ]) await assert.rejects(()=>compileEventProfile(source.replace(before,after)),(e: any) => e.message.startsWith("EVENT_PROFILE") || String(e.code).startsWith("SIC_") || e.name === "CompilationRejected",after);
});

async function fixture(publish:(m:DurableOutboxRecord)=>Promise<void>,budget=1000){
 const c=await compilation; const store=new DurableSqliteTransactionalOutbox(":memory:");const inbox=new SqliteIdempotentInbox(":memory:");
 inbox.database.exec("CREATE TABLE projection(order_id TEXT PRIMARY KEY)");let now=time;
 const observer=new EventObservationCollector({...c.observations[0],cardinalityBudget:budget},"run1",c.source_sha256);
 const flow=new LocalEventFlow(c,"order-transport",store,inbox,{publish},observer,()=>now);
 return {store,inbox,observer,flow,tick:(t:string)=>{now=t},close:()=>{store.close();inbox.close()}};
}
const insert=(db:any)=>{db.prepare("INSERT INTO projection VALUES(?)").run("o1")};

test("order outbox commit, provider acceptance and consumer commit remain separate; duplicate is harmless",async()=>{
 const queue:DurableOutboxRecord[]=[];const f=await fixture(async m=>{queue.push(m)});
 try{f.flow.commit(request);assert.deepEqual(f.observer.observations.map(o=>o.attributes.stage),["outbox-committed"]);
 assert.deepEqual(await f.flow.dispatch(),{published:1,failed:0,dead:0});
 assert.equal(f.inbox.database.prepare("SELECT COUNT(*) n FROM projection").get()!.n,0);
 assert.equal(f.flow.consume(queue[0],insert),"processed");assert.equal(f.flow.consume(queue[0],()=>assert.fail("duplicate executed handler")),"duplicate");
 assert.deepEqual(f.observer.observations.map(o=>o.attributes.stage),["outbox-committed","provider-accepted","consumer-received","consumer-committed","consumer-received","consumer-duplicate"]);
 assert(f.observer.observations.every(o=>o.correlation_id==="m1"&&o.mode==="simulation"&&!o.independently_observed));
 }finally{f.close()}
});

test("state rollback produces neither outbox message nor commit observation",async()=>{
 const f=await fixture(async()=>{});try{assert.throws(()=>f.flow.commit(request,true),/FAILPOINT/);assert.equal(f.store.state("OrderOperation","o1"),null);assert.equal(f.store.records().length,0);assert.equal(f.observer.observations.length,0);}finally{f.close()}
});

test("consumer transaction failure rolls back effect and inbox, then a redelivery commits",async()=>{
 const f=await fixture(async()=>{});try{f.flow.commit(request);const m=f.store.records()[0];
 assert.throws(()=>f.flow.consume(m,db=>{insert(db);throw Error("consumer failure")}),/consumer failure/);
 assert.equal(f.inbox.database.prepare("SELECT COUNT(*) n FROM projection").get()!.n,0);
 assert(!f.observer.observations.some(o=>o.attributes.stage==="consumer-committed"));
 assert.equal(f.flow.consume(m,insert),"processed");
 }finally{f.close()}
});

test("unknown provider outcome retries same message ID; inbox suppresses duplicate effects",async()=>{
 const queue:DurableOutboxRecord[]=[];let calls=0;const f=await fixture(async m=>{queue.push(m);if(++calls===1)throw Error("ack lost")});
 try{f.flow.commit(request);assert.equal((await f.flow.dispatch()).failed,1);assert.equal(f.flow.consume(queue[0],insert),"processed");
 assert(!f.observer.observations.some(o=>o.attributes.stage==="provider-accepted"));
 f.tick("2026-09-06T12:00:02.000Z");assert.equal((await f.flow.dispatch()).published,1);assert.equal(queue[0].messageId,queue[1].messageId);
 assert.equal(f.flow.consume(queue[1],()=>assert.fail("duplicate effect")),"duplicate");
 }finally{f.close()}
});

test("retry policy terminates after configured attempts and reports unknown outcomes",async()=>{
 const f=await fixture(async()=>{throw Error("unavailable")});try{f.flow.commit(request);
 for(let i=0;i<5;i++){f.tick(`2026-09-06T12:0${i}:00.000Z`);await f.flow.dispatch();}
 assert.equal(f.store.stats().dead,1);assert.equal(f.store.records()[0].attempts,5);assert.equal((await f.flow.dispatch()).failed,0);
 assert.equal(f.observer.observations.filter(o=>o.attributes.stage==="transport-unknown").length,5);
 }finally{f.close()}
});

test("missing telemetry and cardinality rejection stay explicit and ORODI derives missing vs conserved",async()=>{
 const f=await fixture(async()=>{},1);try{f.flow.commit(request);await f.flow.dispatch();assert.deepEqual(f.observer.accounting(),{offered:2,queued:1,rejected:1,exported:0,dropped:0,pending:1,partial_success:0});
 const base=path.resolve(defaultDomainSpecPackageRoot(),"../operational-resilience");
 const {deriveFoundationalControlSet}=await import(pathToFileURL(path.join(base,"src/derive-foundational-controls.ts")).href);
 const bundle=JSON.parse(readFileSync(path.join(base,"fixtures/valid/c01-c16-pass.json"),"utf8"));
 bundle.observations=[];assert.equal(deriveFoundationalControlSet(bundle,time).derived_controls.find((r:any)=>r.control_id==="C15").state,"missing");
 bundle.observations=f.observer.observations;assert.equal(deriveFoundationalControlSet(bundle,time).derived_controls.find((r:any)=>r.control_id==="C15").state,"passed");
 assert.equal(f.observer.accounting().exported,0); // Conservation does not prove export or business delivery.
 }finally{f.close()}
});
