import assert from 'node:assert/strict';import {readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';import {verifyLocations,currentLocation} from './locations.mjs';import {bind} from './snapshots.mjs';
const root=path.resolve(import.meta.dirname,'../../../..'),load=f=>JSON.parse(readFileSync(path.join(root,f))),mapping=load('work/plans/definition-catalog-v2-layout/MAPPING.json'),registry=load('authority/admissions/shared-definitions-records-0076/registry.json'),files=new Map(),checks=[];
function f(name){const raw=readFileSync(path.join(root,name));files.set(name,raw);return bind(name,raw);}
const source={layout_protocol:'workspace-definition-layout/v1',layout:{catalog:f('implementation/lab-workspaces/v2/catalog.json'),homes:f('authority/definitions/maintenance-homes.json')},locations:{}};
for(const e of registry.entries.filter(x=>x.carrier.ref==='cal.artifact-type.definition/v2')){const row=mapping.entries.find(x=>x.definition_id===e.definition_id);f(e.body.path);const profile=path.posix.join(row.workspace_home,'WORKSPACE.json'),p=load(profile);source.locations[e.definition_id+'@'+e.version]={body:f(row.target+'/definition.json'),profile:f(profile),workspace:p.workspace_ref};}
const read=b=>files.get(b.ref??b.path)??readFileSync(path.join(root,b.ref??b.path));
await verifyLocations(source,registry,read);checks.push('five-existing-v2-original-bindings-and-readable-aliases');
const first=Object.keys(source.locations)[0];
for(const [name,change,pattern]of [
 ['missing-current-location',s=>delete s.locations[first],/coverage-mismatch/],
 ['unapproved-extra-location',s=>s.locations['foreign@1']=s.locations[first],/coverage-mismatch/],
 ['body-substitution',s=>s.locations[first].body.sha256='0'.repeat(64),/binding-mismatch|body-substitution/],
 ['wrong-readable-path',s=>{const l=s.locations[first];files.set('wrong/definition.json',read(l.body));l.body.ref='wrong/definition.json';},/readable-path-mismatch/],
 ['unknown-workspace',s=>s.locations[first].profile.ref='unknown/WORKSPACE.json',/workspace-not-selected/],
 ['wrong-workspace-identity',s=>s.locations[first].workspace='workspace:other',/foreign-workspace/],
 ['protocol-omission',s=>delete s.layout_protocol,/protocol-required/]
 ]){const altered=structuredClone(source);change(altered);await assert.rejects(()=>verifyLocations(altered,registry,read),pattern);checks.push(name);}
const selected=registry.entries.find(e=>e.definition_id+'@'+e.version===first),location=currentLocation(selected,source,read);assert(location.expected.includes('/'+mapping.entries.find(x=>x.definition_id===selected.definition_id).folder_name+'/'));checks.push('reader-retains-original-binding-and-resolves-readable-current-home');
writeFileSync(path.join(import.meta.dirname,'LOCATION-VERIFICATION.json'),JSON.stringify({status:'PASS',check_count:checks.length,checks,scope:'Actual admitted v2 bodies and selected workspace records; no semantic admission or production mutation.'},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length}));
