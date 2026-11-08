import {typescriptCompiler,tsxLoader,tsxCli} from '../helpers/node-toolchain.ts';
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";

const cliRoot = path.resolve(import.meta.dirname, "../..");
const example = path.join(cliRoot, "examples/reconciled-commerce");

test("graph-derived handlers retain renamed Operations, distinct source paths and pre-effect failures", t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-graph-handlers-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const renamed = (text: string) => text.replaceAll("commerce", "fulfillment").replaceAll("perform", "submit");
  const write = (relative: string, content: string) => { const target = path.join(root, relative); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, content); };
  function copy(dir: string, relative = "") {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const current = path.join(dir, entry.name), name = relative + entry.name;
      if (entry.isDirectory()) copy(current, name + "/");
      else write("source/" + renamed(name), renamed(fs.readFileSync(current, "utf8")));
    }
  }
  copy(path.join(example, "source"));
  const read = (name: string) => JSON.parse(renamed(fs.readFileSync(path.join(example, name), "utf8")));
  const selection = read("selections/typescript.json"), integration = read("integrations/application.json");
  const inbound = integration.external_api.api_mappings.find((row: any) => row.mapping_id === "api-mapping:payment-webhook-request");
  const subscription = integration.messaging.message_mappings.find((row: any) => row.mapping_id === "message-mapping:order-submitted-in");
  inbound.input_paths[0].path = ["envelope", "purchase"];
  inbound.request_parameters[1].source.path = ["envelope", "event"];
  subscription.input_paths[0].path = ["payload", "incoming"];
  subscription.request_parameters[1].source.path = ["payload", "notice"];
  const plan = planWholeApplicationV1(path.join(root, "source"), selection, integration);
  const generated = path.join(root, "generated");
  for (const file of plan.artifacts) write("generated/" + file.relative_path, file.content);
  const handler = plan.artifacts.find(row => row.relative_path === "src/integrations/application-request-handlers.ts")!;
  assert.match(handler.content, /operationSubmit/);
  assert.doesNotMatch(handler.content, /commerce|operationPerform|requestFrom/);
  assert.match(handler.content, /\["envelope","purchase"\]/);
  assert.match(handler.content, /\["payload","incoming"\]/);
  const compiled = spawnSync(process.execPath, [typescriptCompiler, "-p", "tsconfig.json", "--noEmit"], { cwd: generated, encoding: "utf8" });
  assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
  const runner = `import assert from 'node:assert/strict';
import {APPLICATION_REQUEST_HANDLERS as handlers} from './src/integrations/application-request-handlers.ts';
async function main(){
const order={billing_customer_id:'7',choice:{variant:'Some',payload:{quantity:'5',note:null}},customer:{id:'7',name:'Ada'},id:'9',labels:['priority'],lines:[{quantity:'2',note:'first'}],money:{quantity:'25',note:null},tags:['new','paid']};
const notice={occurrence:{'event-id':'evt-9'},occurredAt:'2026-09-16T12:00:00Z',payload:{'order-id':'9',delta:'1',ratio:1}};
const calls=[];const dependencies={store:{begin:async()=>{calls.push('begin');return{read:async()=>{throw Error('unexpected read')},commit:async batch=>{calls.push('commit');assert.equal(batch.writes[0].target,'fulfillment:order');return{status:'committed'}},rollback:async()=>{calls.push('rollback')}}}}};
const http=handlers['api-mapping:payment-webhook-request'];const message=handlers['message-mapping:order-submitted-in'];
const left=await http({envelope:{purchase:order,event:notice}},dependencies);const right=await message({payload:{incoming:order,notice}},dependencies);
assert.equal(left.status,'committed');assert.equal(right.status,'committed');assert.equal(left.value.id,9n);assert.deepEqual(calls,['begin','commit','begin','commit']);
for(const body of [null,{}, {amount:order,notice_input:notice}, {envelope:Object.create({purchase:order,event:notice})}])await assert.rejects(http(body,dependencies),/APPLICATION_REQUEST_PATH/);
let getters=0;const envelope={event:notice};Object.defineProperty(envelope,'purchase',{get(){getters++;return order}});await assert.rejects(http({envelope},dependencies),/APPLICATION_REQUEST_PATH/);assert.equal(getters,0);
assert.deepEqual(calls,['begin','commit','begin','commit']);
const uncertain={store:{begin:async()=>({read:async()=>{throw Error('unexpected read')},commit:async()=>({status:'indeterminate'}),rollback:async()=>{throw Error('must not roll back an uncertain commit')}})}};
assert.equal((await http({envelope:{purchase:order,event:notice}},uncertain)).status,'indeterminate');
}
main().catch(error=>{console.error(error);process.exitCode=1});`;
  const executed = spawnSync(process.execPath, [tsxCli, "--eval", runner], { cwd: generated, encoding: "utf8" });
  assert.equal(executed.status, 0, executed.stdout + executed.stderr);
  const changed = structuredClone(integration);
  changed.external_api.api_mappings.find((row: any) => row.mapping_id === inbound.mapping_id).input_paths[0].path = ["other", "purchase"];
  const other = planWholeApplicationV1(path.join(root, "source"), selection, changed);
  assert.notEqual(other.artifacts.find(row => row.relative_path === handler.relative_path)!.sha256, handler.sha256);
});
