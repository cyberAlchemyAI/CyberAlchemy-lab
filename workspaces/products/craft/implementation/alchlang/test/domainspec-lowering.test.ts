import { testTsx } from "./toolchain.js";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdtempSync, rmSync, readdirSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { lowerDomainSpec } from "../src/lower-domainspec.js";
import { buildDomainSpec, checkDomainSpec } from "../src/domainspec-project-writer.js";
import { parseDomainSource } from "../src/parser.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const fixture=path.join(root,"examples/domainspec-order.alch");
const source=readFileSync(fixture,"utf8");const bindings=JSON.parse(readFileSync(fixture+".domainspec.json","utf8"));
const lower=(text=source,b=structuredClone(bindings))=>lowerDomainSpec(parseDomainSource(text).carrier,{...b,source_sha256:digest(text)},text);
const temp=(t:{after(fn:()=>void):void})=>{const p=mkdtempSync(path.join(os.tmpdir(),"alch-lowering-test-"));t.after(()=>rmSync(p,{recursive:true,force:true}));return p;};
const allFiles=(p:string):string[]=>readdirSync(p,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>e.isDirectory()?allFiles(path.join(p,e.name)):[path.join(p,e.name)]);

test("lowering produces identical real project bytes, exact contract bindings and complete traces",()=>{
 const a=lower();assert.deepEqual(a,lower());assert.equal(Object.keys(a.symbols).length,10);
 const mapping=JSON.parse(a.files["specs/delivery-example/nodes/order-to-message.json"]);
 assert.equal(mapping.body.typed_contract.schema_version,"domainspec.typed-mapping/v1");
 assert.equal(mapping.body.typed_contract.fields[0].source,"order_id");
 assert.equal(mapping.body.typed_contract.fields[0].target,"message_id");
 assert.equal(mapping.body.typed_contract.total,true);
 const policy=JSON.parse(a.files["specs/delivery-example/nodes/choose-delivery-fee.json"]);
 assert.deepEqual(policy.body.typed_contract.cases.map((c:any)=>c.target),["delivery-example:express-fee","delivery-example:priority-fee"]);
 const vo=JSON.parse(a.files["specs/delivery-example/nodes/urgent-flag.json"]);
 assert.deepEqual(vo.body.invariant_refs,["delivery-example:urgent-required"]);
 assert.ok(vo.body.typed_contract.properties.every((p:any)=>!p.identity));
});

test("new-directory builds replay byte-for-byte including compiler and input inventories",async t=>{
 const p=temp(t);const a=path.join(p,"a"),b=path.join(p,"b");
 await buildDomainSpec(fixture,a,{generate:true});await buildDomainSpec(fixture,b,{generate:true});
 const files=allFiles(a).map(f=>path.relative(a,f));assert.deepEqual(files,allFiles(b).map(f=>path.relative(b,f)));
 for(const f of files)assert.deepEqual(readFileSync(path.join(a,f)),readFileSync(path.join(b,f)),f);
 const m=JSON.parse(readFileSync(path.join(a,"manifest.json"),"utf8"));
 assert.equal(m.compiler.version,"1.3.0");assert.ok(Object.keys(m.files).length>20);
 for(const [f,h] of Object.entries(m.files))assert.equal(digest(readFileSync(path.join(a,f))),h);
 assert.equal(Object.keys(m.files).length,files.length-1);
 assert.ok(Object.keys(JSON.parse(readFileSync(path.join(a,"compiler-files.json"),"utf8"))).some(p=>p==="dist/generation/generators.js"));
 await assert.rejects(buildDomainSpec(fixture,a),/DS_OUTPUT_EXISTS/);
 const empty=path.join(p,"empty");mkdirSync(empty);await assert.rejects(buildDomainSpec(fixture,empty),/DS_OUTPUT_EXISTS/);assert.deepEqual(readdirSync(empty),[]);
});

test("profile rejects source drift, unsafe numbers, missing bindings, wrong scope and incomplete metadata",()=>{
 const carrier=parseDomainSource(source).carrier;
 assert.throws(()=>lowerDomainSpec(carrier,bindings,source+"\n"),/DS_SOURCE_DRIFT/);
 assert.throws(()=>lower(source.replace("expression 1000","expression 9007199254740992")),/DS_NUMERIC_PROFILE/);
 const missing=structuredClone(bindings);delete missing.declarations.Order.identity;assert.throws(()=>lower(source,missing),/DS_IDENTITY/);
 const noInvariant=structuredClone(bindings);delete noInvariant.declarations.UrgentFlag.invariants;assert.throws(()=>lower(source,noInvariant),/DS_INVARIANT/);
 assert.throws(()=>lower(source.replace("currency: string","currency: record")),/TYPE_MISMATCH|DS_UNSUPPORTED_TYPE/);
 assert.throws(()=>lower(source.replace("logic sfol-v1","logic sfol-v1\nactor Operator")),/DS_UNSUPPORTED/);
 const wrong=structuredClone(bindings);wrong.owner="other";assert.throws(()=>lower(source,wrong),/DS_OWNER/);
 const extra=structuredClone(bindings);extra.declarations.Other={ontology:"EXAMPLE-OTHER",meaning:"extra"};assert.throws(()=>lower(source,extra),/DS_BINDINGS/);
 const total=source.replace("mapping PartialMessage:\n  source Order\n  target Message\n  total false","mapping PartialMessage:\n  source Order\n  target Message\n  total true");assert.throws(()=>lower(total),/DS_MAPPING_TOTALITY/);
});

test("normalization collisions and endpoint field mismatches reject explicitly",()=>{
 const colliding=source+"\nentity order:\n  anotherId: identifier required\n";assert.throws(()=>lower(colliding),/DS_SYMBOL_COLLISION/);
 const mismatch=source.replace("field messageId <- orderId","field messageId <- messageId");assert.throws(()=>lower(mismatch),/DS_MAPPING_REFERENCE/);
 const unknown=source.replace("target Message","target Missing");assert.throws(()=>lower(unknown),/UNRESOLVED_REFERENCE/);
 const metadata=structuredClone(bindings);metadata.declarations.Order.properties.orderId.ontology="WRONG-ID#orderId";assert.throws(()=>lower(source,metadata),/DS_ONTOLOGY/);
});

test("failed input or upstream validation leaves no completed or partial output",async t=>{
 const p=temp(t),s=path.join(p,"bad.alch");writeFileSync(s,source);writeFileSync(s+".domainspec.json",json({...bindings,source_sha256:"bad"}));
 await assert.rejects(buildDomainSpec(s,path.join(p,"out")),/DS_SOURCE_DRIFT/);assert.equal(existsSync(path.join(p,"out")),false);assert.ok(!readdirSync(p).some(n=>n.startsWith(".alchlang")));
 const badPackage=path.join(p,"package");mkdirSync(badPackage);writeFileSync(path.join(badPackage,"package.json"),json({name:"@domainspec-v2/cli",version:"0.1.0"}));
 await assert.rejects(buildDomainSpec(fixture,path.join(p,"out"),{packageRoot:badPackage}),/DOMAINSPEC_VERSION_MISMATCH/);assert.equal(existsSync(path.join(p,"out")),false);
 const before=readFileSync(fixture);assert.equal((await checkDomainSpec(fixture)).status,"valid");assert.deepEqual(readFileSync(fixture),before);
});

test("CLI supports explicit profile and output commands and rejects force and unsupported flags",async t=>{
 const p=temp(t);const tsx=testTsx();
 const run=(...args:string[])=>spawnSync(tsx,[path.join(root,"src/cli.ts"),...args],{cwd:p,encoding:"utf8"});
 const check=run("check",fixture,"--profile","domainspec-1.0.0");assert.equal(check.status,0,check.stderr);assert.equal(JSON.parse(check.stdout).nodes,13);
 const emit=run("emit-domainspec",fixture,"--out",path.join(p,"emit"));assert.equal(emit.status,0,emit.stderr);assert.ok(existsSync(path.join(p,"emit/project/project.json")));
 for(const flags of [["--force"],["--language","rust"],["--profile","wrong"],["--out",path.join(p,"duplicate")]]){const result=run("build",fixture,"--backend","domainspec","--out",path.join(p,"bad"),...flags);assert.notEqual(result.status,0);assert.equal(existsSync(path.join(p,"bad")),false);}
});

test("self-model successor compiles and every predecessor node and relationship is accounted for",async()=>{
 const base=path.resolve(root,"..");const dir=path.join(base,"extensions/domainspec-lowering-v1/self-model");const m=JSON.parse(readFileSync(path.join(dir,"migration.json"),"utf8"));const compiler=await loadDomainSpecCompiler();const result=compiler.compileProject(path.join(dir,"project"));
 assert.equal(result.graph.nodes.length,53);assert.equal(result.graph.relationships.length,45);
 const old=path.join(base,"domainspec");const oldNodes=allFiles(old).filter(f=>f.includes("/nodes/"));const oldEdges=allFiles(old).filter(f=>f.includes("/edges/"));assert.equal(m.nodes.length,oldNodes.length);assert.equal(m.edges.length,oldEdges.length);
 for(const [rows,paths,key] of [[m.nodes,oldNodes,"old_selector"],[m.edges,oldEdges,"old_edge"]] as const){assert.equal(new Set(rows.map((r:any)=>r[key])).size,paths.length);for(const f of paths){const n=JSON.parse(readFileSync(f,"utf8"));const id=n.feature_id+":"+(n.node_id??n.edge_id);const row=rows.find((r:any)=>r[key]===id);assert.ok(row,id);assert.equal(row.old_sha256,digest(readFileSync(f)));}}
 const newNodes=new Set(result.graph.nodes.map(n=>n.selector));const newEdges=new Set(result.graph.relationships.map(e=>e.source.feature_id+":"+e.edge_id));
 for(const row of m.nodes)for(const s of row.new_selectors)assert.ok(newNodes.has(s),s);
 for(const row of m.edges)for(const s of row.new_edges)assert.ok(newEdges.has(s),s);
 for(const kind of ["query","calculation","mapping","policy"]){const n=result.graph.nodes.find(n=>n.selector===`typed-backend:${kind}-contract`)!;assert.equal(n.kind,"Entity");}
 assert.equal(m.nodes.filter((r:any)=>r.disposition==="replace").length,4);
});
