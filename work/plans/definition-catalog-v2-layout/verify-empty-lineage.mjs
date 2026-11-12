import assert from 'node:assert/strict';import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,copyFileSync} from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {tmpdir} from 'node:os';
import {prepareCli,materializeCli} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),load=f=>JSON.parse(readFileSync(f)),sha=b=>createHash('sha256').update(b).digest('hex'),mapping=load(path.join(here,'MAPPING.json'));
function pointer(d,p){for(const s of p.slice(1).split('/'))d=d[s.replaceAll('~1','/').replaceAll('~0','~')];return d;}
let selected,removed;
for(const row of mapping.entries){const work=path.join(root,row.work),d=load(path.join(work,'definition.json')),l=load(path.join(work,'field-lineage.json'));const i=l.fields.findIndex(f=>{const v=pointer(d,f.target_selector);return v!==null&&typeof v==='object'&&Object.keys(v).length===0;});if(i>=0){selected={row,work,lineage:l,index:i};removed=l.fields[i].target_selector;break;}}
assert(selected);const temp=mkdtempSync(path.join(tmpdir(),'define-empty-lineage-regression-'));
for(const name of ['original.json','definition.json','transformation.json'])copyFileSync(path.join(selected.work,name),path.join(temp,name));
selected.lineage.fields.splice(selected.index,1);const line=Buffer.from(JSON.stringify(selected.lineage)+'\n');writeFileSync(path.join(temp,'field-lineage.json'),line);
const request=load(path.join(selected.work,'request.json')),bound={path:'field-lineage.json',sha256:sha(line),bytes:line.length,digest_kind:'original-file-sha256'};
request.source_bindings=request.source_bindings.map(b=>b.path==='field-lineage.json'?bound:b);request.materialization_selection[0].field_lineage_binding=bound;
await prepareCli(Buffer.from(JSON.stringify(request)),temp,path.join(temp,'pack'));
await assert.rejects(()=>materializeCli(path.join(temp,'pack'),path.join(temp,'materialized')),/incomplete-or-duplicate-field-lineage/);
writeFileSync(path.join(here,'EMPTY-LINEAGE-REGRESSION.json'),JSON.stringify({status:'PASS',definition_id:selected.row.definition_id,omitted_empty_container:removed,actual_native_rejection:'incomplete-or-duplicate-field-lineage',checks:1,scope:'Real Define preparation succeeds with exactly bound altered input; actual materialization refuses missing empty-container lineage.'},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',omitted_empty_container:removed}));
