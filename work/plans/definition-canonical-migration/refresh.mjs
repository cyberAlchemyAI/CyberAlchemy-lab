import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import path from 'node:path';
import {here,root,trustFile,database,scope,cut,load,put} from './operator.mjs';
import {Snapshots,bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';import {build} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
export function refresh(){
 const t=load(trustFile),snapshots=new Snapshots(database,{readOnly:true}),selected={...snapshots.current(scope)},material=snapshots.material(selected.digest,'registry.json'),registry=JSON.parse(material.bytes);snapshots.close();
 const original=load(path.join(root,'authority/admissions/shared-definitions-records-0076/registry.json')),auth=load(path.join(root,'docs/decisions/0077-definition-v2-canonical-migration/authorization.json'));
 const expected=Object.fromEntries(original.entries.map(e=>[e.definition_id+'@'+e.version,{sha256:e.body.sha256,bytes:e.body.bytes,carrier:e.carrier.ref}]));
 const current_lookup={...original.current_lookup};
 for(const target of auth.accepted_definitions)if(registry.entries.some(e=>e.definition_id+'@'+e.version===target.version)){
  expected[target.version]={sha256:target.source.sha256,bytes:target.source.bytes,carrier:'cal.artifact-type.definition/v2'};current_lookup[target.version.split('@')[0]]=target.version;
 }
 const qualify=(ref,file,raw=readFileSync(file))=>{t.materials[ref]={path:path.relative(root,file),sha256:digest(raw)};return bind(ref,raw);};
 const registryFile=put('operational/registry.json',registry),registryRef='registry:shared-definitions',registryBinding=qualify(registryRef,registryFile);
 const subjects=registry.entries.map(e=>{const ref='definition:'+e.definition_id+'@'+e.version;return {ref,binding:qualify(ref,path.join(root,e.body.path)),dependencies:[]};});
 subjects.push({ref:registryRef,binding:registryBinding,dependencies:subjects.map(s=>s.ref)});
 for(const [ref,file]of [['reader:lab.catalog-reader','implementation/lab-runtime/alchlang/shared-records/catalog.mjs'],['reader:define.catalog-reader','workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs'],['runtime:shared-definitions',path.relative(root,path.join(here,'EXECUTION-MANIFEST.json'))]])subjects.push({ref,binding:qualify(ref,path.join(root,file)),dependencies:[registryRef]});
 for(const file of Object.values(load(path.join(root,'implementation/lab-workspaces/v2/catalog.json')).profiles)){const w=load(path.join(root,file));subjects.push({ref:w.workspace_ref,binding:qualify(w.workspace_ref,path.join(root,file)),dependencies:['reader:lab.catalog-reader',...(w.primary_subject.key==='product/define'?['reader:define.catalog-reader']:[])]});}
 const sourceCut=snapshotsSource(selected);
 const universeFile=put('operational/consumer-universe.json',{version:1,scope,source_cut:cut,registry_cut:sourceCut,cursor:'snapshot:'+selected.revision+':'+selected.digest,unresolved:0,subjects,declared_scope:'Every retained/current Definition, shared registry, two maintained readers, runtime closure and seven selected workspace profiles.'});t.consumer_universe={path:path.relative(root,universeFile),sha256:digest(readFileSync(universeFile))};
 const model=build(),files=Object.fromEntries(Object.entries(model.files).map(([name,sha256])=>{const raw=readFileSync(path.join(model.output,name));assert.equal(digest(raw),sha256);return [name,{sha256,bytes_base64:raw.toString('base64')}];}));
 const out=put('operational/generation-output.json',{version:1,registry:{binding:registryBinding,bytes_base64:material.bytes.toString('base64')},generation:{source:model.source,manifest_sha256:model.manifest_sha256,files},chain:['definitions','artifacts','ontology','business-system bridge ontology','system-ontology','AlchLang','generation']});
 const output=qualify('generation:shared-records-0077',out),executorPath=path.join(root,'implementation/lab-runtime/alchlang/shared-records/qualified_registry_check.py'),executor=bind('check:shared-registry-output',readFileSync(executorPath));
 t.executors[executor.ref]={path:path.relative(root,executorPath),sha256:executor.sha256,command:'python3',timeout_ms:30000};
 const contract=qualify('contract:shared-records',path.join(root,'work/plans/shared-definitions-records-r5/CONTRACTS.json')),specifications=[];
 for(const check of ['membership','original-bodies','standing','generation']){const fixture=put('operational/fixture-'+check+'.json',{check,expected,current_lookup,model_source:model.source,manifest_sha256:model.manifest_sha256});specifications.push({obligation:'shared-registry:'+check,source:contract,executor,fixture:qualify('fixture:shared-registry:'+check,fixture)});}
 t.conformance={output,specifications};put('operational/assessment.json',{output,specifications});put(trustFile,t);
 const configFile=path.join(root,'implementation/lab-runtime/shared-workflow.json'),config=load(configFile);config.selector=selected;put(configFile,config);
 return {registry,selected,universe:subjects.length,source_cut:cut};
}
function snapshotsSource(selected){const snapshots=new Snapshots(database,{readOnly:true});try{return snapshots.material(selected.digest,'registry.json').manifest.cut;}finally{snapshots.close();}}
if(process.argv[1]===import.meta.filename)console.log(JSON.stringify(refresh()));
