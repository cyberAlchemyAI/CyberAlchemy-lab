import assert from 'node:assert/strict';
import {test,before,after} from 'node:test';
import {mkdtempSync,readFileSync,readdirSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {callLab,composeDefineContext} from '../src/context-adapter.mjs';
const root=resolve(import.meta.dirname,'../../../..');
let temp,store,proposal;
function inventory(path){return readdirSync(path,{withFileTypes:true}).flatMap(e=>e.isDirectory()?inventory(join(path,e.name)):[[join(path,e.name),readFileSync(join(path,e.name)).toString('hex')]]);}
before(()=>{
 temp=mkdtempSync(join(tmpdir(),'lab-define-review-'));store=join(temp,'store');
 const source=`import json,sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1]+'/implementation/lab-runtime/v2')\nfrom lab_runtime.store import Store,keygen\nfrom lab_runtime.common import load\nfrom lab_runtime.cli import example\nr=Path(sys.argv[1]); t=Path(sys.argv[2]); k=keygen(t/'private.pem',t/'public.hex'); s=Store(t/'store',r); s.initialize(load(r/'implementation/lab-runtime/v2/profile.json'),'define-review-test','role:fixture-owner',k['public_key']); print(json.dumps(example(s,'define-review-test')))\n`;
 const p=spawnSync('python3',['-c',source,root,temp],{encoding:'utf8',timeout:60000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});assert.equal(p.status,0,p.stderr);proposal=JSON.parse(p.stdout);
});
after(()=>rmSync(temp,{recursive:true,force:true}));
test('Define reuses Lab review preparation without changing store files or HEAD',()=>{
 const before=inventory(store);const result=callLab('review',{store,proposal});assert.equal(result.approval_required,true);assert.equal(result.authority_effect,'none');assert.ok(result.planned_consequences);assert.deepEqual(inventory(store),before);
});
test('Context follows the explicitly selected Lab branch',()=>{
 const ctx=composeDefineContext({store,consumer:'fixture'});assert.equal(ctx.ok,true,JSON.stringify(ctx));assert.equal(ctx.lab_views.agent_session.scope_ref,'scope:lab-runtime-local:define-review-test');
});
test('Review rejects a proposal for another HEAD without changing state',()=>{
 const before=inventory(store);assert.throws(()=>callLab('review',{store,proposal:{...proposal,expected_head:'0'.repeat(64)}}),/HEAD|head/);assert.deepEqual(inventory(store),before);
});
