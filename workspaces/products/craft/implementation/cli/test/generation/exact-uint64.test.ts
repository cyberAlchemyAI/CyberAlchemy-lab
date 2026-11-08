import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { stripTypeScriptTypes } from "node:module";
import { runCli } from "../../src/cli/main.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";
import { planProjectBuild, publishProjectBuild, verifyProjectBuild } from "../../src/generation/project-build.ts";
import { createInstantiationReceipt } from "../../src/conformance/receipt.ts";
import { EXACT_UINT64_PROFILE } from "../../src/generation/exact-uint64.ts";

const fixture=path.resolve(import.meta.dirname,"../../fixtures/input-roots/canonical-project");
async function moduleFor(content:string){return import(`data:text/javascript;base64,${Buffer.from(stripTypeScriptTypes(content)).toString("base64")}`);}

test("exact realization is opt-in, records its identity, and preserves default arithmetic",async t=>{
 const parent=fs.mkdtempSync(path.join(os.tmpdir(),"ds-exact-"));t.after(()=>fs.rmSync(parent,{recursive:true,force:true}));const source=path.join(parent,"source");fs.cpSync(fixture,source,{recursive:true});
 const contract={schema_version:"domainspec.typed-calculation/v1",ontology_calculation:"EXACT-COST",inputs:[{name:"amount",type:{kind:"scalar",name:"UInt64"}}],result:{kind:"scalar",name:"UInt64"},division_rounding:"reject",expression:{op:"add",left:{op:"input",name:"amount"},right:{op:"literal",value:5}}};
 let stderr="";assert.equal(runCli(["add","calculation",source,"--feature","alpha","--name","exact-cost","--description","Exact arithmetic fixture","--contract-json",JSON.stringify(contract),"--calculates","settle"],{stdout(){},stderr(v){stderr+=v;}}),0,stderr);
 const node=loadProjectNode(source,"alpha:exact-cost");
 const legacy=planInstantiation(node,"typescript"),exact=planInstantiation(node,"typescript",null,EXACT_UINT64_PROFILE);
 assert.equal(Object.hasOwn(legacy,"realization_profile"),false);assert.equal(exact.realization_profile,EXACT_UINT64_PROFILE);assert.notEqual(exact.generator_id,legacy.generator_id);assert.throws(()=>createInstantiationReceipt(exact),/whole-project build/);assert.notEqual(exact.plan_sha256,legacy.plan_sha256);
 const original=await moduleFor(legacy.artifacts[0]!.content),generated=await moduleFor(exact.artifacts[0]!.content);
 const legacyFn=Object.values(original).find(v=>typeof v==="function") as Function;const exactFn=Object.values(generated).find(v=>typeof v==="function") as Function;
 assert.equal(legacyFn({amount:140}),145);assert.throws(()=>legacyFn({amount:Number.MAX_SAFE_INTEGER}),/overflow/);
 assert.equal(exactFn({amount:Number.MAX_SAFE_INTEGER}),9007199254740996n);assert.equal(exactFn({amount:"18446744073709551610"}),18446744073709551615n);assert.throws(()=>exactFn({amount:18446744073709551615n}),/CALCULATION_OVERFLOW/);
 assert.throws(()=>planInstantiation(node,"python",null,EXACT_UINT64_PROFILE),/REALIZATION_PROFILE/);
 const plan=planProjectBuild(source,"typescript",EXACT_UINT64_PROFILE);const target=path.join(parent,"generated");publishProjectBuild(plan,target);
 assert.equal(plan.receipt.realization_profile,EXACT_UINT64_PROFILE);
 assert.equal(verifyProjectBuild(source,"typescript",target,EXACT_UINT64_PROFILE).result,"pass");assert.equal(verifyProjectBuild(source,"typescript",target).result,"fail");
 assert.notEqual(runCli(["build",source,"--language","typescript","--target-root",path.join(parent,"bad"),"--realization-profile","unknown"],{stdout(){},stderr(){}}),0);
 assert.equal(fs.existsSync(path.join(parent,"bad")),false);
});
