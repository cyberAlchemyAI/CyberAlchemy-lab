import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {node} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..');
function call(cli,args){const p=spawnSync(node,[cli,...args],{encoding:'utf8',timeout:300000,maxBuffer:16*1024*1024});if(p.status!==0)throw Error(p.stderr+p.stdout);return JSON.parse(p.stdout);}
const lab=path.join(root,'implementation/lab-runtime/lab.mjs');
const status=call(lab,['shared','status']);assert.equal(status.readiness.status,'ready');assert.equal(status.versions,194);assert.equal(status.current,188);
const activated=call(lab,['shared','activate']);assert.equal(activated.status,'ready');
const native=call(lab,['status']);
const cli=path.join(root,'workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs'),home=mkdtempSync(path.join(tmpdir(),'lab-r5-default-define-'));
const input=path.join(here,'.local/define-start.json');call(cli,['start','--work',home,'--file',input,'--actor','person:<vrondelli>','--id','live:start']);
const definitions=JSON.parse(readFileSync(path.join(here,'DEFINITIONS.json'))).definitions,lookups=[];
for(const d of definitions)lookups.push({definition:d.definition_id,result:call(cli,['discover','--work',home,'--query',d.definition_id,'--actor','person:<vrondelli>','--id','live:reuse:'+d.definition_id])});
const replay=call(cli,['replay','--work',home]);
writeFileSync(path.join(here,'DEFAULT-WORKFLOW.json'),JSON.stringify({status:'PASS',shared:status,activation:activated,native,Define:{implementation:'define-alch',lookups,replay},shared_responsibilities_inside_Define:false},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',versions:status.versions,current:status.current,readiness:status.readiness.status,Define_lookups:lookups.length}));
