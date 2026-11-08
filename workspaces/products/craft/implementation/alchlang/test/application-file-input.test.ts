import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { loadApplicationFile, assertApplicationFileCurrent } from "../src/application-file-input.js";
import { compileApplicationExecutable } from "../src/application-executable.js";
import { compileApplicationWhole } from "../src/application-whole.js";
import { digest, json } from "../src/domainspec-profile.js";
import { realizationFixture } from "./fixtures/application-realization-fixture.js";
import { wholeApplicationFixture } from "./fixtures/application-whole-fixture.js";
import { checkApplicationFile } from "../src/application-file-check.js";
import { spawnSync, execFileSync } from "node:child_process";
import { testTsx, testTypeScript } from "./toolchain.js";
import { buildApplicationFile, verifyApplicationFile } from "../src/application-file-build.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { createRequire } from "node:module";
import { deriveApplicationIntegrationBindings } from "../src/application-integration-derivation.js";

function materialize(t: test.TestContext, f: { source: string; bindings: unknown; interpretation: unknown; execution: unknown; sources: ReadonlyMap<string, Buffer> }) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-file-input-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const write = (relative: string, bytes: string | Buffer) => {
    const target = path.join(root, relative); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, bytes);
    return { path: relative, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true };
  };
  write("commerce.alch", f.source);
  const manifest: any = { schema_version: "alchlang.application-file/v1-candidate", source_sha256: digest(f.source),
    bindings: write("inputs/bindings.json", json(f.bindings)), interpretation: write("inputs/interpretation.json", json(f.interpretation)),
    execution: write("inputs/execution.json", json(f.execution)), evidence: [...f.sources].map(([name, bytes]) => write(name, bytes)) };
  const save = () => write("commerce.alch.application.json", json(manifest));
  save();
  return { root, write, manifest, save, source: path.join(root, "commerce.alch") };
}

function providerWorkspace(root: string, output: string, packageRoot: string) {
  const workspace=path.join(root,"provider-native");fs.cpSync(output,workspace,{recursive:true,errorOnExist:true,force:false});
  const modules=path.join(workspace,"node_modules");fs.mkdirSync(path.join(modules,"@types"),{recursive:true});
  fs.symlinkSync(path.join(packageRoot,"node_modules/@types/node"),path.join(modules,"@types/node"),"dir");
  fs.mkdirSync(path.join(modules,"nats"),{recursive:true});
  fs.writeFileSync(path.join(modules,"nats/package.json"),JSON.stringify({name:"nats",type:"module",exports:{".":{types:"./index.d.ts",import:"./index.js"}}}));
  fs.writeFileSync(path.join(modules,"nats/index.js"),'export const headers=()=>({set(){}});export const connect=async()=>({jetstream:()=>({}),drain:async()=>{}});\n');
  fs.writeFileSync(path.join(modules,"nats/index.d.ts"),'export interface MsgHdrs{set(name:string,value:string):void} export function headers():MsgHdrs; export interface JetStreamClient{publish(subject:string,payload:Uint8Array,options?:{headers?:MsgHdrs}):Promise<{stream:string;seq:number}>} export interface NatsConnection{jetstream():JetStreamClient;drain():Promise<void>} export function connect(options:{servers:string}):Promise<NatsConnection>;\n');
  fs.mkdirSync(path.join(modules,"pg"),{recursive:true});
  fs.writeFileSync(path.join(modules,"pg/package.json"),JSON.stringify({name:"pg",type:"module",exports:{".":{types:"./index.d.ts",import:"./index.js"}}}));
  fs.writeFileSync(path.join(modules,"pg/index.js"),'export class Pool{constructor(_options){}async connect(){throw Error("stub")}async query(){return{rows:[]}}async end(){}}\n');
  fs.writeFileSync(path.join(modules,"pg/index.d.ts"),'export interface QueryResult<Row=Record<string,unknown>>{rows:Row[]} export interface PoolClient{query<Row=Record<string,unknown>>(sql:string,values?:readonly unknown[]):Promise<QueryResult<Row>>;release():void} export class Pool{constructor(options?:{connectionString?:string});connect():Promise<PoolClient>;query<Row=Record<string,unknown>>(sql:string,values?:readonly unknown[]):Promise<QueryResult<Row>>;end():Promise<void>}\n');
  return workspace;
}

test("public application loader prepares source-derived realization from exact file companions", async t => {
  const f = realizationFixture(), p = materialize(t, f);
  p.write("unselected-secret.txt", "must not be included");
  const before = fs.readdirSync(p.root, { recursive: true });
  const loaded = await loadApplicationFile(p.source);
  assert.deepEqual(loaded.candidate.selection.operations, f.expectedOperations);
  assert.equal(loaded.authority_effect, "none");
  assert.ok(!Object.hasOwn(loaded.inputs, "unselected-secret.txt"));
  assertApplicationFileCurrent(loaded);
  assert.throws(() => assertApplicationFileCurrent({ ...loaded }), /current file-loaded application/);
  assert.deepEqual(fs.readdirSync(p.root, { recursive: true }), before, "loading creates no files");
  const checked = await checkApplicationFile(p.source);
  assert.equal(checked.status, "valid");
  assert.equal(checked.scope, "executable");
  assert.ok(checked.generated_artifacts > 0);
  assert.deepEqual(await checkApplicationFile(p.source), checked);
  assert.deepEqual(fs.readdirSync(p.root, { recursive: true }), before);
  const entry = process.env.ALCHLANG_TEST_PUBLIC_CLI
    ? [path.resolve(process.env.ALCHLANG_TEST_PUBLIC_CLI)] : [testTsx(), path.resolve(import.meta.dirname, "../src/core-cli.ts")];
  const cli = (args: string[]) => spawnSync(process.execPath, [...entry, ...args], { encoding: "utf8", timeout: 60000 });
  const checkedCli = cli(["check", p.source]);
  assert.equal(checkedCli.status, 0, checkedCli.stderr);
  assert.deepEqual(JSON.parse(checkedCli.stdout), checked);
  for (const args of [["--force"], ["--application-bindings"], ["--application-bindings", "../outside.json"], ["--application-bindings", "commerce.alch.application.json", "--application-bindings", "commerce.alch.application.json"]]) {
    const rejected = cli(["check", p.source, ...args]);
    assert.notEqual(rejected.status, 0); assert.equal(rejected.stdout, "");
  }
  const output = path.join(p.root, "generated"), output2 = path.join(p.root, "generated-again");
  const built = await buildApplicationFile(p.source, output);
  assert.equal(built.status, "built");
  const verified = await verifyApplicationFile(p.source, output);
  assert.equal(verified.status, "verified"); assert.equal(verified.manifest_sha256, built.manifest_sha256);
  assert.equal((await buildApplicationFile(p.source, output2)).manifest_sha256, built.manifest_sha256);
  await assert.rejects(buildApplicationFile(p.source, output), /already exists/);
  const manifestPath = path.join(output, ".alch/manifest.json"), manifestBytes = fs.readFileSync(manifestPath, "utf8"), manifest = JSON.parse(manifestBytes);
  const typedFiles = Object.keys(manifest.files).filter(name => name.endsWith(".ts"));
  assert.ok(typedFiles.length > 0);
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs", "--rootDir", output, "--outDir", path.join(p.root, "native-js"), ...typedFiles.map(name => path.join(output, name))], { encoding: "utf8" });
  const artifact = typedFiles[0]!, originalArtifact = fs.readFileSync(path.join(output, artifact), "utf8"), altered = originalArtifact + "\n// altered\n";
  fs.writeFileSync(path.join(output, artifact), altered);
  manifest.files[artifact] = { sha256: digest(altered), size_bytes: Buffer.byteLength(altered) }; fs.writeFileSync(manifestPath, json(manifest));
  await assert.rejects(verifyApplicationFile(p.source, output), /APPLICATION_OUTPUT/);
  fs.writeFileSync(path.join(output, artifact), originalArtifact); fs.writeFileSync(manifestPath, manifestBytes);
  const cliOutput = path.join(p.root, "cli-generated");
  for (const command of ["build", "verify"]) {
    const result = cli([command, p.source, "--out", cliOutput]);
    assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).manifest_sha256, built.manifest_sha256);
    const missing = cli([command, p.source]); assert.notEqual(missing.status, 0); assert.equal(missing.stdout, "");
  }
  for (const [relative, bytes] of Object.entries(loaded.candidate.projectFiles)) p.write(`compiled-source/${relative}`, bytes);
  const graph = loaded.compiler.compileProject(path.join(p.root, "compiled-source")).graph;
  assert.ok(compileApplicationExecutable(loaded.candidate, graph, loaded.compiler).view.artifacts.length);
  for (const relative of ["commerce.alch", "commerce.alch.application.json", p.manifest.execution.path, p.manifest.evidence[0].path]) {
    const old = fs.readFileSync(path.join(p.root, relative));
    p.write(relative, Buffer.alloc(old.length, 32));
    assert.throws(() => assertApplicationFileCurrent(loaded), /changed|FORMAL_BINDING_STALE/);
    p.write(relative, old);
    assertApplicationFileCurrent(loaded);
  }
});

test("application loader rejects escaped, stale, malformed and linked companions without output", async t => {
  const f = realizationFixture(), p = materialize(t, f), original = structuredClone(p.manifest);
  const invalid = [
    { ...original, extra: true }, { ...original, schema_version: "unknown" },
    { ...original, source_sha256: "0".repeat(64) }, { ...original, evidence: null },
    { ...original, runtime_profile: "" }, { ...original, bindings: { ...original.bindings, current: false } },
    { ...original, execution: { ...original.execution, sha256: "0".repeat(64) } },
    { ...original, bindings: { ...original.bindings, size_bytes: 17 * 1024 * 1024 } },
    ...["../outside", "/etc/passwd", "C:/outside", "inputs\\bindings.json", "inputs/./bindings.json"].map(name => ({ ...original, bindings: { ...original.bindings, path: name } })),
  ];
  for (const manifest of invalid) {
    p.write("commerce.alch.application.json", json(manifest));
    await assert.rejects(loadApplicationFile(p.source), /APPLICATION_FILE_INPUT|FORMAL_BINDING/);
  }
  p.save();
  await assert.rejects(loadApplicationFile(p.source, { companion: "../outside.json" }), /FORMAL_BINDING_PATH/);
  fs.symlinkSync(path.join(p.root, "commerce.alch.application.json"), path.join(p.root, "linked.json"));
  await assert.rejects(loadApplicationFile(p.source, { companion: "linked.json" }), /symlink/);
  fs.symlinkSync(path.join(p.root, "inputs"), path.join(p.root, "linked-inputs"));
  p.manifest.bindings.path = "linked-inputs/bindings.json"; p.save();
  await assert.rejects(loadApplicationFile(p.source), /symlink/);
  p.manifest.bindings = original.bindings;
  p.manifest.interpretation = p.write("inputs/bad.json", Buffer.from([0xff])); p.save();
  await assert.rejects(loadApplicationFile(p.source), /invalid UTF-8 JSON/);
  p.manifest.interpretation = original.interpretation;
  p.manifest.execution = p.write("inputs/overridden.json", json({ ...f.execution, selection: { ...f.execution.selection, operations: f.expectedOperations } })); p.save();
  await assert.rejects(loadApplicationFile(p.source), /APPLICATION_REALIZATION_OVERRIDE/);
  await assert.rejects(buildApplicationFile(p.source, path.join(p.root, "generated")), /APPLICATION_REALIZATION_OVERRIDE/);
  assert.ok(!fs.existsSync(path.join(p.root, "generated")));
});

test("public file check derives composed optional Query policy exclusively from realization source", async t => {
  const f = realizationFixture();
  const source = f.source.replace("realization SubmitOrderExecution:", `query FindOrder:
  input id UInt64
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
realization SubmitOrderExecution:`)
    .replace("read current <- Order key request.id", "query current <- FindOrder(id <- request.id)\n  on-absence current fail ORDER_NOT_FOUND")
    .replace("write Order replace <- request", "write Order replace <- current").replace("result <- request", "result <- current");
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "Optional lookup of an eligible order." } } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)), selection: { ...f.execution.selection,
    schema_version: "domainspec.reconciled-compilation/v2-candidate", profile_id: "domainspec.reconciled-typescript/v2-candidate" } };
  const p = materialize(t, { source, bindings, interpretation, execution, sources: f.sources });
  const loaded = await loadApplicationFile(p.source);
  const row = loaded.candidate.selection.value_compositions[0];
  assert.equal(row.composition.bindings[0].absence, "require-present");
  assert.deepEqual(row.absence_failures, [{ binding: "current", code: "ORDER_NOT_FOUND" }]);
  assert.equal((await checkApplicationFile(p.source)).status, "valid");
  const output = path.join(p.root, "generated"), js = path.join(p.root, "native-js");
  await buildApplicationFile(p.source, output); await verifyApplicationFile(p.source, output);
  const manifest = JSON.parse(fs.readFileSync(path.join(output, ".alch/manifest.json"), "utf8"));
  const typed = Object.keys(manifest.files).filter(name => name.endsWith(".ts"));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs", "--rootDir", output, "--outDir", js, ...typed.map(name => path.join(output, name))], { encoding: "utf8" });
  const module = typed.find(name => name.endsWith("/operations/submit-order.ts"))!;
  const run = createRequire(import.meta.url)(path.join(js, module.replace(/\.ts$/, ".js"))).operationSubmitOrder;
  for (const rows of [[], [{ id: "7", accepted: true }]]) {
    const calls: string[] = [];
    const result = await run({ request: { id: "1", accepted: true } }, { store: { begin: async () => ({
      read: async () => { throw Error("not a keyed read"); }, querySource: async () => rows,
      commit: async () => { calls.push("commit"); return { status: "committed" }; }, rollback: async () => { calls.push("rollback"); },
    }) } });
    if (rows.length) { assert.equal(result.status, "committed"); assert.deepEqual(result.value, { id: 7n, accepted: true }); assert.deepEqual(calls, ["commit"]); }
    else { assert.equal(result.code, "ORDER_NOT_FOUND"); assert.deepEqual(calls, ["rollback"]); }
  }
});

test("file loader derives internal integration contracts and joins a provider application", async t => {
  const f = await wholeApplicationFixture("provider-selection:commerce-runtime", false, true);
  const p = materialize(t, f);
  p.manifest.runtime_profile = "CommerceRuntime";
  p.manifest.observation = p.write("inputs/observation.json", json(f.observation)); p.save();
  const loaded = await loadApplicationFile(p.source);
  assert.ok(Object.isFrozen(loaded.observation));
  assert.ok(loaded.integration_derivation);
  assert.equal(loaded.integration_derivation!.provider_pack, "domainspec.reference-postgresql16-nats-http/v1-candidate");
  assert.equal(loaded.integration_derivation!.runtime_guarantees_observed, false);
  assert.ok(!Object.keys(loaded.inputs).some(name => /persistence|messaging|external_api/.test(name)));
  assert.equal(loaded.candidate.selection.schema_version, f.candidate.selection.schema_version);
  for (const [relative, bytes] of Object.entries(loaded.candidate.projectFiles)) p.write(`compiled-source/${relative}`, bytes);
  const graph = loaded.compiler.compileProject(path.join(p.root, "compiled-source")).graph;
  const whole = compileApplicationWhole(loaded.candidate, graph, loaded.observation, loaded.compiler);
  assert.equal(whole.runtimeBinding.providers.length, 5);
  assert.equal(whole.trace.runtime_guarantees_observed, false);
  const checked = await checkApplicationFile(p.source);
  assert.equal(checked.scope, "provider-application-artifacts");
  assert.equal(checked.generated_artifacts, whole.application.artifacts.length);
  assert.equal(checked.runtime_guarantees_observed, false);
  const output = path.join(p.root, "whole-generated");
  assert.equal((await buildApplicationFile(p.source, output)).scope, "provider-application-artifacts");
  assert.equal((await verifyApplicationFile(p.source, output)).status, "verified");
  assert.ok(fs.existsSync(path.join(output, ".alch/whole/application-runtime-binding.json")));
  assert.ok(fs.existsSync(path.join(output, "src/integrations/application-request-handlers.ts")));
  assert.ok(fs.existsSync(path.join(output, "src/providers/reference/bootstrap.ts")));
  assert.ok(fs.existsSync(path.join(output, ".domainspec/providers/manifest.json")));
  assert.ok(fs.existsSync(path.join(output, "tsconfig.json")));
  const native=providerWorkspace(p.root,output,loaded.compiler.binding.package_root);
  const compiled=spawnSync(testTypeScript(), ["-p", path.join(native, "tsconfig.json"), "--noEmit", "--types", "node"], { encoding: "utf8" });
  assert.equal(compiled.status,0,compiled.stdout+compiled.stderr);
  const handlerPath=path.join(output,"src/integrations/application-request-handlers.ts");
  fs.appendFileSync(handlerPath,"\n// changed generated handler\n");
  await assert.rejects(verifyApplicationFile(p.source,output), /APPLICATION_OUTPUT/);
  assertApplicationFileCurrent(loaded);
  p.manifest.persistence = p.write("inputs/persistence.json", json(f.contexts[0].binding)); p.save();
  await assert.rejects(loadApplicationFile(p.source), /supplied together or derived together/);
});

test("internal integration derivation rejects unsupported packs and ambiguous failure ownership", async () => {
  const f=await wholeApplicationFixture();
  assert.throws(()=>deriveApplicationIntegrationBindings(
    f.source.replace("domainspec.reference-postgresql16-nats-http/v1-candidate","domainspec.unsupported/v1-candidate"),"CommerceRuntime",f.compiler),
    /APPLICATION_INTEGRATION_DERIVATION_PACK/);
  assert.throws(()=>deriveApplicationIntegrationBindings(
    f.source.replace("  accepts-writes-from SubmitOrder\n","  accepts-writes-from SubmitOrder\n  accepts-writes-from ReceiveNotice\n"),"CommerceRuntime",f.compiler),
    /exactly one authored persistence write Operation/);
});

test("whole file build executes source-authored composed handlers and explicit absence rollback", async t => {
  const f=await wholeApplicationFixture("provider-selection:commerce-runtime",true,true),p=materialize(t,f);
  p.manifest.runtime_profile="CommerceRuntime";
  p.manifest.observation=p.write("inputs/observation.json",json(f.observation));p.save();
  const loaded=await loadApplicationFile(p.source);
  assert.equal(loaded.candidate.selection.schema_version,"domainspec.reconciled-compilation/v2-candidate");
  assert.equal(Object.hasOwn(f.execution.selection,"operations"),false);
  const output=path.join(p.root,"whole-composed");
  const built=await buildApplicationFile(p.source,output);
  assert.equal(built.scope,"provider-application-artifacts");
  await verifyApplicationFile(p.source,output);
  const entry=process.env.ALCHLANG_TEST_PUBLIC_CLI?[path.resolve(process.env.ALCHLANG_TEST_PUBLIC_CLI)]:[testTsx(),path.resolve(import.meta.dirname,"../src/core-cli.ts")];
  const cliOutput=path.join(p.root,"whole-cli");
  for(const command of ["build","verify"]){
    const result=spawnSync(process.execPath,[...entry,command,p.source,"--out",cliOutput],{encoding:"utf8",timeout:60000});
    assert.equal(result.status,0,result.stderr);
    assert.equal(JSON.parse(result.stdout).scope,"provider-application-artifacts");
    assert.equal(JSON.parse(result.stdout).manifest_sha256,built.manifest_sha256);
  }
  const native=providerWorkspace(p.root,output,loaded.compiler.binding.package_root);
  const compiled=spawnSync(testTypeScript(),["-p",path.join(native,"tsconfig.json"),"--noEmit","--types","node"],{encoding:"utf8"});
  assert.equal(compiled.status,0,compiled.stdout+compiled.stderr);
  const graph=JSON.parse(fs.readFileSync(path.join(output,".domainspec/application-graph.json"),"utf8"));
  const request=graph.operation_requests.find((r:any)=>r.operation_ref==="commerce:submit-order");
  const connection=request.bindings[0],mapping=graph.runtime_bindings.find((r:any)=>r.binding_id===connection.mapping_binding_ref);
  const body:any={};let target=body;
  const parts=mapping.inputs[0].source.path;
  for(const part of parts.slice(0,-1))target=target[part]={};
  const value={id:"7",accepted:true};
  if(parts.length)target[parts.at(-1)]=value;else Object.assign(body,value);
  const wrongBody=structuredClone(body);let wrongTarget=wrongBody;
  for(const part of parts)wrongTarget=wrongTarget[part];
  wrongTarget.id="8";
  const runner=`import assert from 'node:assert/strict';
import {APPLICATION_REQUEST_HANDLERS as handlers} from './src/integrations/application-request-handlers.ts';
async function main(){
for(const [payload,row,expected] of [
 [${JSON.stringify(body)},null,'READ_NOT_FOUND'],
 [${JSON.stringify(body)},{id:'7',accepted:true},'committed'],
 [${JSON.stringify(wrongBody)},{id:'7',accepted:true},'READ_IDENTITY_MISMATCH']]){
 const calls=[];
 const result=await handlers[${JSON.stringify(connection.mapping_binding_ref)}](payload,{store:{begin:async()=>({
 read:async()=>row,querySource:async()=>{throw Error('unexpected Query source')},
 commit:async batch=>{calls.push('commit');assert.equal(batch.writes[0].value.id,7n);return {status:'committed'}},rollback:async()=>{calls.push('rollback')}
 })}});
 if(expected==='committed'){assert.equal(result.status,'committed');assert.equal(result.value.id,7n);assert.deepEqual(calls,['commit']);}
 else{assert.equal(result.code,expected);assert.deepEqual(calls,['rollback']);}
}}
main().catch(error=>{console.error(error);process.exitCode=1});`;
  const executed=spawnSync(testTsx(),["--eval",runner],{cwd:output,encoding:"utf8"});
  assert.equal(executed.status,0,executed.stdout+executed.stderr);
  const mutantNative=path.join(p.root,"provider-native-identity-mutant");fs.cpSync(native,mutantNative,{recursive:true});
  const operationRelative=(fs.readdirSync(mutantNative,{recursive:true,encoding:"utf8"}) as string[]).find(name=>name.endsWith("/operations/submit-order.provider.ts"));
  assert.ok(operationRelative,"generated keyed Operation source");
  const operationPath=path.join(mutantNative,operationRelative),operationSource=fs.readFileSync(operationPath,"utf8");
  const operationMutant=operationSource.replace('ruleUInt64.key(read0["id"])!==ruleUInt64.key(key0)','ruleUInt64.key(read0["id"])===ruleUInt64.key(key0)');
  assert.notEqual(operationMutant,operationSource,"identity mutant installed");fs.writeFileSync(operationPath,operationMutant);
  const mutantCompiled=spawnSync(testTypeScript(),["-p",path.join(mutantNative,"tsconfig.json"),"--noEmit","--types","node"],{encoding:"utf8"});
  assert.equal(mutantCompiled.status,0,mutantCompiled.stdout+mutantCompiled.stderr);
  const mutantRunner=`import {APPLICATION_REQUEST_HANDLERS as handlers} from './src/integrations/application-request-handlers.ts';
async function main(){
const result=await handlers[${JSON.stringify(connection.mapping_binding_ref)}](${JSON.stringify(wrongBody)},{store:{begin:async()=>({
 read:async()=>({id:'7',accepted:true}),querySource:async()=>{throw Error('unexpected Query source')},
 commit:async()=>({status:'committed'}),rollback:async()=>{}
})}});console.log(JSON.stringify({status:result.status,code:result.code??null}));}
main().catch(error=>{console.error(error);process.exitCode=1});`;
  const mutantExecuted=spawnSync(testTsx(),["--eval",mutantRunner],{cwd:mutantNative,encoding:"utf8"});
  assert.equal(mutantExecuted.status,0,mutantExecuted.stdout+mutantExecuted.stderr);
  const mutantObservation=JSON.parse(mutantExecuted.stdout);
  assert.notDeepEqual(mutantObservation,{status:"failed",code:"READ_IDENTITY_MISMATCH"},"independent public-flow oracle kills the compiling keyed-read identity mutant");
  assert.equal(mutantObservation.status,"committed");
  const emitted=spawnSync(testTypeScript(),["-p",path.join(native,"tsconfig.json"),"--noEmit","false","--outDir",path.join(native,"dist"),"--types","node"],{encoding:"utf8"});
  assert.equal(emitted.status,0,emitted.stdout+emitted.stderr);
  const scenario=path.join(loaded.compiler.binding.package_root,"examples/reconciled-commerce/scenarios/typescript-webhook.mjs");
  const loopback=spawnSync(process.execPath,[scenario,native,"/orders"],{encoding:"utf8",timeout:60000});
  assert.equal(loopback.status,0,loopback.stdout+loopback.stderr);
  assert.deepEqual(JSON.parse(loopback.stdout),{language:"typescript",startup:"http-listener",invalid_status:401,valid_status:202,handler_invocations:1,result:"pass"});
  assert.equal((await verifyApplicationFile(p.source,output)).status,"verified");
});
