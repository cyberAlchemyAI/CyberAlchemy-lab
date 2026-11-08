import { testTypeScript } from "./toolchain.js";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import test from "node:test";
import { buildDomainSpec } from "../src/domainspec-project-writer.js";
import { parseDomainSource } from "../src/parser.js";
import { validateAndNormalize } from "../src/validate.js";
import { evaluateMapping, evaluatePolicy, evaluateCalculation } from "../src/typed-backend.js";
import { evaluateRule } from "../src/runtime.js";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");const fixture=path.join(root,"examples/domainspec-order.alch");
const files=(p:string):string[]=>readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(p,e.name)):[path.join(p,e.name)]);

test("generated TypeScript and checked entry preserve Mapping, Policy, Rule and constant semantics",async t=>{
 const p=mkdtempSync(path.join(os.tmpdir(),"alch-parity-"));t.after(()=>rmSync(p,{recursive:true,force:true}));const bundle=path.join(p,"bundle");await buildDomainSpec(fixture,bundle,{generate:true});
 const generated=files(bundle).filter(f=>f.endsWith(".ts"));const tsc=testTypeScript();const js=path.join(p,"js");
 execFileSync(process.execPath,[tsc,"--strict","--skipLibCheck","--target","ES2022","--module","commonjs","--rootDir",bundle,"--outDir",js,...generated],{encoding:"utf8",cwd:p});
 const api=await import(pathToFileURL(path.join(js,"domain.js")).href);const model=validateAndNormalize(parseDomainSource(readFileSync(fixture,"utf8")).carrier);
 for(const id of ["OrderToMessage","PartialMessage"]){const mapping=model.mappings.find(m=>m.id===id)!;for(const value of [{orderId:"o-1",urgent:false,priority:false,unrelated:"not-copied"},{orderId:"o-2"},{}]){
  const before=structuredClone(value);let expected:unknown;try{expected=evaluateMapping(mapping,value);}catch{assert.throws(()=>api.evaluateMapping(id,value),/missing Mapping field/);continue;}
  assert.deepEqual(api.evaluateMapping(id,value),expected);assert.deepEqual(value,before);assert.ok(Object.isFrozen(api.evaluateMapping(id,value)));
 }}
 const policy=model.policies[0];for(const value of [{urgent:true,priority:true},{urgent:true,priority:false},{urgent:false,priority:true},{urgent:false,priority:false}])assert.equal(api.selectPolicy(policy.id,value),evaluatePolicy(policy,value));
 assert.equal(api.selectPolicy(policy.id,{urgent:true,priority:true}),"ExpressFee");
 assert.throws(()=>api.selectPolicy(policy.id,{urgent:true}),/ALCH_MISSING_INPUT/);
 assert.throws(()=>api.selectPolicy(policy.id,{urgent:"true",priority:false}),/ALCH_INPUT_TYPE/);
 assert.throws(()=>api.evaluateMapping("OrderToMessage",{orderId:12}),/ALCH_INPUT_TYPE/);
 assert.throws(()=>api.evaluateMapping("OrderToMessage",Object.create({orderId:"inherited"})),/ALCH_INPUT_RECORD/);
 assert.throws(()=>api.evaluateMapping("constructor",{}),/ALCH_UNKNOWN_MAPPING/);
 assert.throws(()=>api.selectPolicy("unknown",{}),/ALCH_UNKNOWN_POLICY/);
 // A getter on an ignored field must not run; selection does not invoke any target.
 const input={urgent:true,priority:true};Object.defineProperty(input,"effect",{get(){throw new Error("effect executed");}});assert.equal(api.selectPolicy(policy.id,input),"ExpressFee");
 for(const [id,name] of [["ExpressFee","expressFee"],["PriorityFee","priorityFee"],["StandardFee","standardFee"]]){const module=await import(pathToFileURL(path.join(js,"generated/src/domainspec/typescript/delivery-example",id.replace(/([a-z])([A-Z])/g,"$1-$2").toLowerCase()+".js")).href);assert.equal(BigInt(module[name]({})),evaluateCalculation(model.calculations.find(c=>c.id===id)!,{}));}
 const rule=await import(pathToFileURL(path.join(js,"generated/src/domainspec/typescript/delivery-example/urgent-required.js")).href);for(const urgent of [true,false])assert.equal(rule.urgentRequired({urgent}),evaluateRule(model.rules.find(r=>r.id==="UrgentRequired")!,{urgent}));
});
