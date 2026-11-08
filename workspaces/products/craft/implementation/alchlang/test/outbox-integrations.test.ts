import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import {
  FetchOutboxHttpClient,
  HttpOutboxTransport,
  SqliteIdempotentInbox,
} from "../src/index.js";
const message={messageId:"m-1",aggregateType:"Order",aggregateId:"o-1",eventType:"done",payload:{id:"o-1"},occurredAt:"2026-09-03T00:00:00.000Z",status:"leased",attempts:1,maxAttempts:5,availableAt:"2026-09-03T00:00:00.000Z",leaseOwner:"w",leaseUntil:"2026-09-03T00:01:00.000Z",leaseGeneration:0,lastError:null,publishedAt:null}as const;
test("HTTP transport carries stable idempotency key and rejects non-2xx",async()=>{const calls:any[]=[];const ok=new HttpOutboxTransport("https://allowed.test/events",{async send(input){calls.push(input);return{status:202}}});await ok.publish(message);assert.equal(calls[0].headers["idempotency-key"],"m-1");await assert.rejects(()=>new HttpOutboxTransport("https://allowed.test/events",{async send(){return{status:503}}}).publish(message),/HTTP_FAILED:503/)});
test("fetch client permits only an exact allowlisted loopback origin", async () => {
  const received: { idempotencyKey?: string; body?: string } = {};
  const server = createServer((request, response) => {
    const chunks: Buffer[] = [];
    request.on("data", (chunk: Buffer) => chunks.push(chunk));
    request.on("end", () => {
      received.idempotencyKey = request.headers["idempotency-key"] as string;
      received.body = Buffer.concat(chunks).toString("utf8");
      response.writeHead(202).end();
    });
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    const address = server.address();
    assert(address && typeof address === "object");
    const origin = `http://127.0.0.1:${address.port}`;
    const client = new FetchOutboxHttpClient([origin]);
    await new HttpOutboxTransport(`${origin}/events`, client).publish(message);
    assert.equal(received.idempotencyKey, "m-1");
    assert.match(received.body ?? "", /\"messageId\":\"m-1\"/);
    await assert.rejects(
      () => new FetchOutboxHttpClient([]).send({
        url: `${origin}/events`,
        headers: {},
        body: "{}",
      }),
      /OUTBOX_HTTP_ORIGIN_DENIED/,
    );
  } finally {
    await new Promise<void>((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve())),
    );
  }
});
test("SQLite inbox applies a local handler once and rolls it back with the receipt",()=>{const inbox=new SqliteIdempotentInbox(path.join(mkdtempSync(path.join(tmpdir(),"inbox-")),"db.sqlite"));try{inbox.database.exec("CREATE TABLE projection(value INTEGER NOT NULL)");assert.equal(inbox.consume(message,"2026-09-03T00:00:01.000Z",db=>{db.prepare("INSERT INTO projection VALUES(?)").run(1)}),"processed");assert.equal(inbox.consume(message,"2026-09-03T00:00:02.000Z",db=>{db.prepare("INSERT INTO projection VALUES(?)").run(2)}),"duplicate");assert.equal((inbox.database.prepare("SELECT COUNT(*) count FROM projection").get()as{count:number}).count,1);assert.throws(()=>inbox.consume({...message,messageId:"m-2"},"2026-09-03T00:00:03.000Z",()=>{throw new Error("handler")}),/handler/);assert.equal(inbox.consume({...message,messageId:"m-2"},"2026-09-03T00:00:04.000Z",()=>{}),"processed")}finally{inbox.close()}});
