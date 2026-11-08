import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import test from 'node:test';
import {prepareServicePlan,planPreparedService,assertPreparedServiceCurrent,disposePreparedService} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/service-builder.ts';
// Open questions: PE08 native qualification and PE10 output completion.
const repo=path.resolve(import.meta.dirname,'../../../../../../../');
test('registered preparation separates pure generation planning from disk/compiler/publication',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'profile-plan-extraction-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(repo,'research/craft-alchlang-user-readiness-2026-10-12/profile-composition-orodi-research-2026-10-13/example/source'),root,{recursive:true});
 const prepared=await prepareServicePlan(path.join(root,'service.alch'));t.after(()=>disposePreparedService(prepared));assertPreparedServiceCurrent(prepared);
 const require=createRequire(import.meta.url),undo:Array<()=>void>=[];let attempts=0;
 const trap=(object:any,key:string)=>{const old=object[key];object[key]=()=>{attempts++;throw Error('PLAN_FORBIDDEN:'+key);};undo.push(()=>object[key]=old);};
 for(const key of ['readFileSync','writeFileSync','mkdirSync','openSync','statSync','lstatSync','mkdtempSync','linkSync','renameSync'])trap(require('node:fs'),key);
 for(const key of ['execFileSync','spawnSync','exec','spawn'])trap(require('node:child_process'),key);trap(globalThis,'fetch');syncBuiltinESMExports();
 let plan:ReturnType<typeof planPreparedService>;
 try{plan=planPreparedService(prepared);assert.equal(attempts,0);}finally{for(const restore of undo)restore();syncBuiltinESMExports();}
 assert.equal(plan.functions.length,2);assert.ok(plan.functions[0]!.artifacts[plan.functions[0]!.paths.entry!]!.includes('export const {invoke,handler}'));
 assert.ok(Object.keys(plan.functions[0]!.artifacts).some(p=>p.endsWith('.ts')));
 assert.throws(()=>planPreparedService(JSON.parse(JSON.stringify(prepared))),/SERVICE_PLAN_UNREGISTERED_OR_CHANGED/);
 const before=readFileSync(path.join(root,'quote.alch'),'utf8');writeFileSync(path.join(root,'quote.alch'),before+'\n# changed source\n');assert.throws(()=>assertPreparedServiceCurrent(prepared),/FUNCTION_PLAN_SOURCE_STALE/);
 writeFileSync(path.join(root,'quote.alch'),before);assertPreparedServiceCurrent(prepared);
 const fn=prepared.functions[0]!;writeFileSync(path.join(fn.workspace,'project.json'),readFileSync(path.join(fn.workspace,'project.json'),'utf8')+'\n');assert.throws(()=>assertPreparedServiceCurrent(prepared),/FUNCTION_PLAN_PROJECT_STALE/);
});
