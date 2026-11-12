import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {DatabaseSync} from 'node:sqlite';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {captureImplementation,loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {Snapshots,bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {build} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
import {Journal} from '../../../implementation/lab-runtime/alchlang/shared-records/journal.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..');
const load=f=>JSON.parse(readFileSync(f)),bytes=x=>Buffer.from(JSON.stringify(x));
const put=(name,value)=>{const f=path.join(here,name);mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(value,null,2)+'\n');return f;};
const relative=f=>path.relative(root,f);
const binding=f=>({path:relative(f),sha256:digest(readFileSync(f)),bytes:readFileSync(f).length});
const old=path.join(root,'docs/decisions/0076-shared-definitions-records-activation');
const trust=load(path.join(old,'trust.json'));
const selection=captureImplementation();
const selectedFile=put('EXECUTION-MANIFEST.json',selection);
trust.implementation={path:relative(selectedFile),sha256:digest(readFileSync(selectedFile))};
trust.historical_artifacts={};
const modelArchive=binding(path.join(here,'HISTORICAL-SOURCE.json'));
function historical(request){
 const artifact=Buffer.from(request.artifact,'base64');
 trust.historical_artifacts[digest(artifact)]={operation:request.operation,scope:request.scope,cut:request.cut,
 implementation:'historical:4a779a683',model_archive:{path:modelArchive.path,sha256:modelArchive.sha256}};
}
historical(load(path.join(old,'publish.json')));
historical(load(path.join(old,'native-apply.json')).construction);
const db=new DatabaseSync(path.join(root,'.local/lab-runtime/shared/journal.sqlite'),{readOnly:true});
for(const row of db.prepare('SELECT evidence FROM commands').all())historical(JSON.parse(row.evidence));db.close();
const active=load(path.join(root,'implementation/lab-runtime/shared-workflow.json'));
const workspace=active.workspace,cut=active.native_source_cut;
const issuer='principal:lab-shared-operator';
for(const operation of ['AssessCarriedConstructionEntry','AssessReviewCarryForward','EnforceRegistryClosure','EnforceRuntimeReadiness']){
 const schemaPath=put('issuance/'+operation+'.schema.json',{type:'object',required:['value'],additionalProperties:false,properties:{value:{type:'object'}}});
 const selectionPath=put('issuance/'+operation+'.json',{version:1,operation,scope:workspace,input_schema:operation,
 requirements:[{predicate:'qualified-operator-observation',schema:operation,mappings:[{from:'/value',to:'/value'}]}]});
 trust.schemas[operation]={path:relative(schemaPath),sha256:digest(readFileSync(schemaPath))};
 trust.selections[operation]={path:relative(selectionPath),sha256:digest(readFileSync(selectionPath))};
 for(const predicate of ['qualified-operator-observation','verified-planning-input'])
  if(!trust.principals[issuer].grants.some(g=>g.operation===operation&&g.predicate===predicate&&g.cut===cut&&g.scope===workspace))
   trust.principals[issuer].grants.push({predicate,operation,scope:workspace,cut});
}
trust.materials={};trust.executors={};
function qualify(ref,file){const raw=readFileSync(file);trust.materials[ref]={path:relative(file),sha256:digest(raw)};return bind(ref,raw);}
const previous=load(path.join(root,'authority/definitions/registry.json'));
const auth=load(path.join(old,'authorization.json'));
const registryPath=path.join(root,'authority/admissions/shared-definitions-records-0076/registry.json');
const registry=load(registryPath);
const expected={};
for(const e of previous.entries){
 const raw=readFileSync(path.join(root,e.path));
 expected[e.definition_id+'@'+e.version]={sha256:e.sha256,bytes:raw.length,carrier:'cal.artifact-type.definition/v1'};
}
for(const item of auth.accepted_definitions)
 expected[item.version]={sha256:item.source.sha256,bytes:item.source.bytes,carrier:'cal.artifact-type.definition/v2'};
const current_lookup={...previous.current_lookup};
for(const item of auth.accepted_definitions)current_lookup[item.version.split('@')[0]]=item.version;
const subjects=[];
for(const e of registry.entries){
 const ref='definition:'+e.definition_id+'@'+e.version;
 subjects.push({ref,binding:qualify(ref,path.join(root,e.body.path)),dependencies:[]});
}
const registryRef='registry:shared-definitions';
const registryMaterial=qualify(registryRef,registryPath);
subjects.push({ref:registryRef,binding:registryMaterial,dependencies:subjects.map(s=>s.ref)});
for(const [ref,file]of [
 ['reader:lab.catalog-reader','implementation/lab-runtime/alchlang/shared-records/catalog.mjs'],
 ['reader:define.catalog-reader','workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs'],
 ['runtime:shared-definitions',relative(selectedFile)]]){
 subjects.push({ref,binding:qualify(ref,path.join(root,file)),dependencies:[registryRef]});
}
const catalog=load(path.join(root,'implementation/lab-workspaces/v2/catalog.json'));
for(const file of Object.values(catalog.profiles)){
 const profile=load(path.join(root,file));
 subjects.push({ref:profile.workspace_ref,binding:qualify(profile.workspace_ref,path.join(root,file)),
 dependencies:['reader:lab.catalog-reader',...(profile.primary_subject.key==='product/define'?['reader:define.catalog-reader']:[])]});
}
const universe=put('operational/consumer-universe.json',{version:1,scope:workspace,source_cut:cut,registry_cut:load(path.join(old,'publish.json')).cut,
 cursor:'snapshot:'+active.selector.revision+':'+active.selector.digest,unresolved:0,subjects,
 declared_scope:'Complete selected shared Definition catalog, its two maintained catalog readers, central CLI and all seven current workspace profiles. External consumers and historical inactive source references are outside this declared operational universe.'});
trust.consumer_universe={path:relative(universe),sha256:digest(readFileSync(universe))};
const executorPath=path.join(root,'implementation/lab-runtime/alchlang/shared-records/qualified_registry_check.py');
const executor=bind('check:shared-registry-output',readFileSync(executorPath));
trust.executors[executor.ref]={path:relative(executorPath),sha256:executor.sha256,command:'python3',timeout_ms:30000,
 qualified_scope:'Independent process, captured output/fixture/contract only, Python standard library'};
const contract=qualify('contract:shared-records-r5',path.join(here,'CONTRACTS.json'));
const model=build();
const generated=Object.fromEntries(Object.entries(model.files).map(([name,sha256])=>{
 const raw=readFileSync(path.join(model.output,name));assertDigest(raw,sha256);
 return [name,{sha256,bytes_base64:raw.toString('base64')}];
}));
function assertDigest(raw,expected){if(digest(raw)!==expected)throw Error('actual-generated-source-drift');}
const packagePath=put('operational/generation-output.json',{version:1,
 registry:{binding:registryMaterial,bytes_base64:readFileSync(registryPath).toString('base64')},
 generation:{source:model.source,manifest_sha256:model.manifest_sha256,files:generated},
 chain:['definitions','artifacts','ontology','business-system bridge ontology','system-ontology','AlchLang','generation']});
const output=qualify('generation:shared-records-r5',packagePath);
const specifications=[];
for(const check of ['membership','original-bodies','standing','generation']){
 const fixturePath=put('operational/fixture-'+check+'.json',{check,expected,current_lookup,model_source:model.source,manifest_sha256:model.manifest_sha256,
 authority_sources:[binding(path.join(root,'authority/definitions/registry.json')),binding(path.join(old,'authorization.json'))]});
 specifications.push({obligation:'shared-registry:'+check,source:contract,executor,fixture:qualify('fixture:shared-registry:'+check,fixturePath)});
}
trust.conformance={specifications,output};
put('operational/assessment.json',{specifications,output});
put('operational/impact.json',{root:'definition:cal.definition.definition-pack@1.0.0-candidate.1'});
// Make inherited qualification locators portable while retaining their exact source bytes.
for(const group of ['schemas','selections'])for(const item of Object.values(trust[group]))
 if(path.isAbsolute(item.path)&&item.path.startsWith(root+path.sep))item.path=relative(item.path);
if(path.isAbsolute(trust.initial_registry.path))trust.initial_registry.path=relative(trust.initial_registry.path);
const trustFile=put('runtime-trust.json',trust);
const qualified=loadTrust(trustFile);
const snapshots=new Snapshots(path.join(root,active.database),{trust:qualified});
const originalRequest=load(path.join(old,'publish.json'));
const originalReceipt=load(path.join(old,'receipts/publication.json'));
snapshots.qualifyPublication(workspace,originalRequest.operation==='PlanPublication'?JSON.parse(Buffer.from(originalRequest.artifact,'base64')).input.value.operation_ref:'',originalRequest,originalReceipt);
snapshots.close();
const journal=new Journal(path.join(root,active.journal),{trust:qualified});
const history=await journal.qualifyHistory(workspace,'join:shared-definitions-records-0076');
journal.close();
put('QUALIFIED-HISTORICAL-EVIDENCE.json',{status:'PASS',original_native_history:'ORIGINAL-NATIVE-STATE.json',
 original_model:modelArchive,publication:binding(path.join(old,'receipts/publication.json')),join_phase:history.phase,
 events:history.events.length,original_bytes_rewritten:false});
console.log(JSON.stringify({status:'PASS',implementation:selection.digest,qualified_materials:Object.keys(trust.materials).length,
 independent_checks:specifications.length,consumer_subjects:subjects.length,historical_events:history.events.length}));
