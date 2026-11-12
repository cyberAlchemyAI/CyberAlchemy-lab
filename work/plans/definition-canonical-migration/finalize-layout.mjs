import assert from 'node:assert/strict';import {readFileSync,writeFileSync,existsSync} from 'node:fs';import path from 'node:path';
import {Snapshots} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {currentLocation} from '../../../implementation/lab-runtime/alchlang/shared-records/locations.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),load=f=>JSON.parse(readFileSync(path.resolve(root,f))),put=(f,v)=>writeFileSync(path.resolve(root,f),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n'),binding=f=>{const raw=readFileSync(path.resolve(root,f));return {path:f,sha256:digest(raw),bytes:raw.length};};
const P=path.relative(root,here),mapping=load('work/plans/definition-catalog-v2-layout/MAPPING.json'),active=load('implementation/lab-runtime/shared-workflow.json'),trust=loadTrust(path.resolve(root,active.trust)),selection=load('authority/definitions/current.json');
const db=new Snapshots(path.resolve(root,active.database),{readOnly:true,trust}),selected=db.current(active.workspace),registry=JSON.parse(db.material(selected.digest,'registry.json').bytes),source=JSON.parse(db.material(selected.digest,'source.json').bytes);
assert.equal(registry.entries.length,377);assert.equal(Object.keys(registry.current_lookup).length,188);
for(let i=1;i<=23;i++)assert.equal(load(P+'/batches/unit-'+String(i).padStart(2,'0')+'/COMPLETED.json').status,'PASS');
const rows=[];
for(const row of mapping.entries){
 const version=row.definition_id+'@'+row.version,entry=registry.entries.find(e=>e.definition_id+'@'+e.version===version);assert(entry);assert.equal(registry.current_lookup[row.definition_id],version);assert.equal(entry.carrier.ref,'cal.artifact-type.definition/v2');
 const actual=currentLocation(entry,source,b=>db.material(selected.digest,b.ref??b.path).bytes),file=actual.expected;assert.equal(file,row.target+'/definition.json');const raw=readFileSync(path.resolve(root,file));assert.equal(digest(raw),entry.body.sha256);
 for(const name of ['definition.json','DEFINITION.md','field-lineage.json','evidence.json'])assert(existsSync(path.resolve(root,row.target,name)));
 const evidencePath=row.target+'/evidence.json',evidence=load(evidencePath);evidence.canonical_admission={status:'admitted-current',registry:selection.registry,source:selection.source,selector:{...selected},body:entry.body,owner_disposition:entry.owner_disposition,scope:'Reports the verified shared Lab admission; preceding generation evidence and its authority ceiling remain historical.'};put(evidencePath,evidence);
 rows.push({definition_id:row.definition_id,version:row.version,term:row.term,path:file,sha256:entry.body.sha256,workspace:source.locations[version].workspace,home:row.workspace_home,standing:'admitted-current',owner_disposition:entry.owner_disposition,original_binding:entry.body,predecessor:entry.predecessor});
}
const provenance={schema_version:'lab-canonical-definition-layout/v1',status:'canonical-current',authority_effect:'Projection of the verified shared Lab publication; acceptance remains in bound owner dispositions.',source_registry:selection.registry,source:selection.source,source_cut:active.native_source_cut,selector:{...selected}};
const catalog={...provenance,entries:rows};put('authority/definitions/V2-CATALOG.json',catalog);
const markdown=(localRows,home)=>['# Definitions','', 'Canonical current Definition/v2 records. Names identify folders; stable IDs remain in records and references.','', 'The shared Lab registry selects these admitted versions. Prior admitted versions remain immutable historical dependencies.','', '| Definition | Workspace | Version |','| --- | --- | --- |',...localRows.sort((a,b)=>a.term.localeCompare(b.term)).map(e=>'| ['+e.term+']('+path.relative(path.join(home,'authority/definitions'),path.join(path.dirname(e.path),'DEFINITION.md'))+') | '+e.workspace+' | '+e.version+' |'),''].join('\n');
put('authority/definitions/DEFINITIONS-INDEX.md',markdown([...rows],'.'));put('authority/definitions/V2-DEFINITIONS-INDEX.md',markdown([...rows],'.'));
for(const home of new Set(rows.map(e=>e.home)))if(home!=='.'){
 const local=rows.filter(e=>e.home===home);put(home+'/authority/definitions/V2-CATALOG.json',{...provenance,entries:local});put(home+'/authority/definitions/V2-DEFINITIONS-INDEX.md',markdown([...local],home));put(home+'/authority/definitions/DEFINITIONS-INDEX.md',markdown([...local],home));
}
const completion={schema_version:'lab-definition-canonical-migration-completion/v1',status:'applied-verification-pending',authorization:binding('docs/decisions/0077-definition-v2-canonical-migration/authorization.json'),decision:binding('docs/decisions/0077-definition-v2-canonical-migration/decision.json'),accepted_converted:183,reused_current_v2:5,current:188,retained_versions:377,selector:{...selected},registry:selection.registry,source:selection.source,source_cut:active.native_source_cut,layout:'<workspace>/authority/definitions/<readable-name>/<version>/',runtime_policy:active.runtime_policy,history:'Original 194 admitted version body bindings and original owner cuts remain retained.'};
put('docs/decisions/0077-definition-v2-canonical-migration/application.json',completion);put(P+'/CANONICAL-PUBLICATION.json',completion);
db.close();console.log(JSON.stringify(completion));
