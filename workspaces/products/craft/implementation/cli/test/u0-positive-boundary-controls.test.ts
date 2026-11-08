import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Actual portable generated native boundary; no handwritten business callback.
// Open Questions: V02 CONTEXT; synchronous in-call cancellation is separately component-only.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),repo=path.resolve(core,'../../../../..'),out=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/V02'),run=fs.mkdtempSync(path.join(out,'boundaries-')),app=path.join(run,'application'),sha=(b:Buffer)=>crypto.createHash('sha256').update(b).digest('hex'),original=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/V01/run-f5vSFQ/application');
fs.cpSync(original,app,{recursive:true});for(const row of JSON.parse(fs.readFileSync(path.join(app,'outputs/code.json'),'utf8')).files)assert.equal(sha(fs.readFileSync(path.join(app,row.path))),row.sha256);
const entry=await import(pathToFileURL(path.join(app,'entry.mjs')).href),native=await import(pathToFileURL(path.join(app,'runtime/application-http.mjs')).href);
test('actual selected handler accepts exactly4096 bytes and preserves settled native outcomes after abort',async()=>{
 const canonical='{"id":"18446744073709551615","verified":true}',body=canonical+' '.repeat(4096-Buffer.byteLength(canonical));assert.equal(Buffer.byteLength(body),4096);const controller=new AbortController(),req=new Request('https://qualification.invalid/confirm-delivery',{method:'POST',headers:{'content-type':'application/json','content-length':'4096'},body,signal:controller.signal}),response=await entry.handler(req),local=native.inspectU0HttpResponse(response);controller.abort();assert.equal(response.status,200);const text=await response.text();assert.equal(text,'{"kind":"completed","value":{"id":"18446744073709551615","verified":true}}');assert.equal(local.invoked,true);assert.equal(local.acquired_bytes,4096);assert.equal(local.reader_released,true);assert.equal(local.timer_clear_count,1);assert.equal(local.peer_delivery,'not-observed');assert.equal(req.body!.locked,false);
 fs.writeFileSync(path.join(run,'positive-boundary-observation.json'),JSON.stringify({schema_version:'craft.u0-positive-boundaries/v1-candidate',exact_request_bytes:4096,status:response.status,body:text,response_bytes:Buffer.byteLength(text),local,post_settlement_abort:'completed response unchanged; in-call cancellation checked separately at native component seam',authority_effect:'none',open_questions_ref:'../CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
});
