import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import test from "node:test";
import { buildDomainSpec, checkDomainSpec } from "../src/domainspec-project-writer.js";
import { lowerDomainSpec } from "../src/lower-domainspec.js";
import { parseDomainSource } from "../src/parser.js";
import { validateAndNormalize } from "../src/validate.js";
import { evaluateCalculation, evaluateMapping, evaluatePolicy, evaluateQuery } from "../src/typed-backend.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { EXACT_PROFILE, EXACT_REALIZATION, digest, json } from "../src/domainspec-profile.js";
import { testTypeScript } from "./toolchain.js";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const sourcePath=path.join(root,"examples/typed-backend.alch");
const source=readFileSync(sourcePath,"utf8");
const bindingsPath=path.join(root,"../extensions/domainspec-exact-uint64-v1/typed-commerce.bindings.json");
const bindings=JSON.parse(readFileSync(bindingsPath,"utf8"));
const files=(p:string):string[]=>readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(p,e.name)):[path.join(p,e.name)]);
const temp=(t:{after(fn:()=>void):void})=>{const p=mkdtempSync(path.join(os.tmpdir(),"alch-exact-"));t.after(()=>rmSync(p,{recursive:true,force:true}));return p;};
async function compiledApi(bundle:string,p:string){
 const tsc=testTypeScript();const js=path.join(p,"js");
 execFileSync(process.execPath,[tsc,"--strict","--skipLibCheck","--target","ES2022","--module","commonjs","--rootDir",bundle,"--outDir",js,...files(bundle).filter(f=>f.endsWith(".ts"))],{cwd:p,encoding:"utf8"});
 return import(pathToFileURL(path.join(js,"domain.js")).href);
}
function sameOutcome(actual:()=>unknown,expected:()=>unknown){
 let value:unknown;try{value=expected();}catch(error){const code=(error as any).issues?.[0]?.code;if(code)assert.throws(actual,new RegExp(code));else assert.throws(actual);return;}
 assert.deepEqual(actual(),value);
}

test("unchanged commerce application lowers, verifies and executes through exact UInt64 target",async t=>{
 const p=temp(t),bundle=path.join(p,"bundle");
 assert.equal((await checkDomainSpec(sourcePath,{bindingsPath,profile:EXACT_PROFILE})).nodes,9);
 await buildDomainSpec(sourcePath,bundle,{bindingsPath,profile:EXACT_PROFILE,generate:true});
 const api=await compiledApi(bundle,p),model=validateAndNormalize(parseDomainSource(source).carrier);
 const boundary=[0,100,101,140,Number.MAX_SAFE_INTEGER,9007199254740992n,18446744073709551610n,18446744073709551615n];
 for(const amount of boundary){for(const c of model.calculations)sameOutcome(()=>api.evaluateCalculation(c.id,{amount}),()=>evaluateCalculation(c,{amount}));
  assert.deepEqual(api.evaluateMapping("SummarizeOrder",{order_id:"order",amount}),evaluateMapping(model.mappings[0],{order_id:"order",amount}));
  assert.equal(api.selectPolicy("FeePolicy",{amount}),evaluatePolicy(model.policies[0],{amount}));
 }
 assert.equal(api.evaluateCalculation("ApplyFee",{amount:"9007199254740991"}),9007199254740996n);
 const cases=[[],[{order_id:"a",amount:1,status:"closed"}],[{order_id:"a",amount:140,status:"open"},{order_id:"b",amount:140,status:"open"},{order_id:"c",amount:200,status:"closed"},{order_id:"d",amount:20,status:"open"}],[{order_id:"a",amount:9007199254740992n,status:"open"},{order_id:"b",amount:18446744073709551615n,status:"open"}]];
 for(const rows of cases){const before=structuredClone(rows);assert.deepEqual(api.evaluateQuery("OpenOrders",rows),evaluateQuery(model.queries[0],rows));assert.deepEqual(rows,before);}
 for(const rows of [[{order_id:"a",amount:1}],[{amount:1,status:"open"}],[{order_id:"a",status:"open"},{order_id:"b",amount:2,status:"open"}]])sameOutcome(()=>api.evaluateQuery("OpenOrders",rows),()=>evaluateQuery(model.queries[0],rows));
 sameOutcome(()=>api.evaluateMapping("SummarizeOrder",{}),()=>evaluateMapping(model.mappings[0],{}));
 sameOutcome(()=>api.evaluateCalculation("ApplyFee",{}),()=>evaluateCalculation(model.calculations[0],{}));
 assert.throws(()=>api.evaluateCalculation("ApplyFee",{amount:9007199254740992}),/CALCULATION_INPUT_TYPE/);
 assert.throws(()=>api.evaluateQuery("OpenOrders",[{order_id:"a",amount:9007199254740992,status:"open"}]),/ALCH_INPUT_TYPE/);
 assert.throws(()=>api.selectPolicy("constructor",{}),/ALCH_UNKNOWN_POLICY/);
 assert.throws(()=>api.evaluateCalculation("constructor",{}),/ALCH_UNKNOWN_CALCULATION/);
 assert.throws(()=>api.evaluateQuery("constructor",[]),/ALCH_UNKNOWN_QUERY/);
 assert.throws(()=>api.evaluateCalculation("ApplyFee",Object.create({amount:1})),/ALCH_INPUT_RECORD/);
 const receipt=JSON.parse(readFileSync(path.join(bundle,"generated/.domainspec/project-build.json"),"utf8"));assert.equal(receipt.realization_profile,EXACT_REALIZATION);
 const compiler=await loadDomainSpecCompiler();let out="";const io={stdout(v:string){out+=v;},stderr(){}};
 assert.equal(compiler.runCli(["verify",path.join(bundle,"project"),"--language","typescript","--target-root",path.join(bundle,"generated"),"--realization-profile",EXACT_REALIZATION],io),0);
 out="";assert.notEqual(compiler.runCli(["verify",path.join(bundle,"project"),"--language","typescript","--target-root",path.join(bundle,"generated")],io),0);
 assert.equal(digest(readFileSync(sourcePath)),digest(source));
});

test("exact numeric expressions preserve every rounding mode, failures and full UInt64 literals",async t=>{
 const p=temp(t);let text=source;const b=structuredClone(bindings);
 const additions=[['Subtract','subtract(amount, 5)','reject'],['Multiply','multiply(amount, 5)','reject'],['Floor','divide(amount, 2)','floor'],['Ceil','divide(amount, 2)','ceil'],['RejectFraction','divide(amount, 2)','reject'],['ZeroDivide','divide(amount, 0)','reject'],['MaxLiteral','18446744073709551615','reject']];
 for(const [id,expression,rounding] of additions){text+=`\ncalculation ${id}:\n${id==='MaxLiteral'?'':'  inputs amount\n'}  expression ${expression}\n  rounding ${rounding}\n`;b.declarations[id]={ontology:`ALCH-EXACT-${id.toUpperCase()}`,meaning:`Arithmetic parity probe ${id}.`};}
 b.source_sha256=digest(text);const s=path.join(p,"arithmetic.alch"),bp=s+".domainspec.json";writeFileSync(s,text);writeFileSync(bp,json(b));const bundle=path.join(p,"bundle");await buildDomainSpec(s,bundle,{profile:EXACT_PROFILE,generate:true});const api=await compiledApi(bundle,p);const model=validateAndNormalize(parseDomainSource(text).carrier);
 for(const c of model.calculations)for(const amount of [0,1,2,3,5,100,Number.MAX_SAFE_INTEGER,9007199254740992n,18446744073709551615n,"18446744073709551615",-1,1.5,"01","-1",18446744073709551616n])sameOutcome(()=>api.evaluateCalculation(c.id,{amount}),()=>evaluateCalculation(c,{amount}));
 assert.equal(api.evaluateCalculation("MaxLiteral",{}),18446744073709551615n);
 const trace=JSON.parse(readFileSync(path.join(bundle,"trace.json"),"utf8"));assert.equal(trace.numeric_literal_encoding,"exact-base-2^32-safe-json-leaves");
});

test("exact profile requires explicit selection, rejects unsupported semantics and replays deterministically",async t=>{
 const p=temp(t);
 const oldPackage=path.join(p,"old-package");mkdirSync(oldPackage);
 writeFileSync(path.join(oldPackage,"package.json"),json({name:"@domainspec-v2/cli",version:"1.3.0",type:"module",exports:{".":{import:"./index.js"}}}));
 writeFileSync(path.join(oldPackage,"index.js"),'export const CLI_PACKAGE_NAME="@domainspec-v2/cli",CLI_VERSION="1.3.0"; export function runCli(args,io){io.stdout("1.3.0");return 0;} export function compileProject(){throw new Error("must not compile");}');
 await assert.rejects(checkDomainSpec(sourcePath,{bindingsPath,profile:EXACT_PROFILE,packageRoot:oldPackage}),/DS_EXACT_REALIZATION_UNAVAILABLE/);
 await assert.rejects(buildDomainSpec(sourcePath,path.join(p,"bad"),{bindingsPath}),/DS_PROFILE_BINDING_MISMATCH/);
 const wrong=structuredClone(bindings);wrong.profile="domainspec-1.0.0";assert.throws(()=>lowerDomainSpec(parseDomainSource(source).carrier,wrong,source),/DS_UNSUPPORTED/);
 const text=source.replace('order amount desc','order amount desc\n  order order_id asc');assert.throws(()=>lowerDomainSpec(parseDomainSource(text).carrier,{...bindings,source_sha256:digest(text)},text),/DS_QUERY_ORDER/);
 for(const name of ["a","b"])await buildDomainSpec(sourcePath,path.join(p,name),{bindingsPath,profile:EXACT_PROFILE,generate:true});
 const a=files(path.join(p,"a")).sort();for(const file of a)assert.deepEqual(readFileSync(file),readFileSync(path.join(p,"b",path.relative(path.join(p,"a"),file))));
 await assert.rejects(buildDomainSpec(sourcePath,path.join(p,"a"),{bindingsPath,profile:EXACT_PROFILE}),/DS_OUTPUT_EXISTS/);
 const compiler=await loadDomainSpecCompiler();assert.notEqual(compiler.runCli(["build",path.join(p,"a/project"),"--language","python","--realization-profile",EXACT_REALIZATION,"--target-root",path.join(p,"python")],{stdout(){},stderr(){}}),0);
});

test("parameterized query and numeric default preserve filtering, projection, stable order and causal missing inputs",async t=>{
 const p=temp(t);const text=source+`\nentity Settings:\n  settingsId: identifier required\n  minimum: integer required\n\nquery AtLeast:\n  source Order\n  inputs minimum\n  where amount >= minimum\n  order amount asc\n  project order_id, amount\n\nmapping DefaultAmount:\n  source Order\n  target OrderSummary\n  total false\n  field total default integer 5\n`;
 const b=structuredClone(bindings);b.source_sha256=digest(text);
 b.declarations.Settings={ontology:"ALCH-EXACT-SETTINGS",meaning:"Explicit query threshold supplied by the caller.",identity:"settingsId",properties:{settingsId:{ontology:"ALCH-EXACT-SETTINGS#settingsId",meaning:"Settings identity."},minimum:{ontology:"ALCH-EXACT-SETTINGS#minimum",meaning:"Minimum requested amount."}}};
 b.declarations.AtLeast={ontology:"ALCH-EXACT-AT-LEAST",meaning:"Select supplied orders at or above the supplied minimum."};
 b.declarations.DefaultAmount={ontology:"ALCH-EXACT-DEFAULT-AMOUNT",meaning:"Construct a partial summary with a default amount of five."};
 const s=path.join(p,"query.alch");writeFileSync(s,text);writeFileSync(s+".domainspec.json",json(b));const bundle=path.join(p,"bundle");await buildDomainSpec(s,bundle,{profile:EXACT_PROFILE,generate:true});const api=await compiledApi(bundle,p);const model=validateAndNormalize(parseDomainSource(text).carrier),q=model.queries.find(q=>q.id==="AtLeast")!;
 const rows=[{order_id:"a",amount:9007199254740992n},{order_id:"b",amount:100},{order_id:"c",amount:100}];
 for(const minimum of [0,100,101,18446744073709551615n])assert.deepEqual(api.evaluateQuery("AtLeast",rows,{minimum}),evaluateQuery(q,rows,{minimum}));
 sameOutcome(()=>api.evaluateQuery("AtLeast",rows,{}),()=>evaluateQuery(q,rows,{}));
 sameOutcome(()=>api.selectPolicy("FeePolicy",{}),()=>evaluatePolicy(model.policies[0],{}));
 assert.deepEqual(api.evaluateMapping("DefaultAmount",{}),evaluateMapping(model.mappings.find(m=>m.id==="DefaultAmount")!,{}));
 const input={amount:101};Object.defineProperty(input,"unused",{get(){throw new Error("side effect");}});assert.equal(api.selectPolicy("FeePolicy",input),"ApplyFee");
});
