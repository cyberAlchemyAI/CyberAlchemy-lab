import {publishAtomicDirectory} from '../generation/atomic-publication.js';
// Fresh authoring outputs preserve failed private stages; no path deletion.
// Open questions: docs/BUSINESS-AUTHORING.md.
export function publishBusinessAuthoringDirectory(target:string,artifacts:readonly {relative_path:string;content:string}[],prefix:string,beforeCommit?:(stagePath:string)=>void):void {
 publishAtomicDirectory(target,artifacts,prefix,beforeCommit,{preserveFailedStage:true});
}

// U11 successor: current original producers, finite required outputs, exact fresh
// tree and no replacement. Open Questions: J01/V02 real selected bundle witness.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {types as nativeTypes} from 'node:util';
import {captureJson,dataDigest,reject,sha256} from './contracts.js';
import {planBusinessOutputsV2,type BusinessOutputPlanV2,type BusinessOutputResultV2,type BusinessOutputKindV2,type BusinessOutputRequestV2} from './business-authoring-coverage-contract-v2.js';
import type {BusinessFreshOutputRequestV2,BusinessOutputArtifactInputV2,BusinessOutputWriterOwnerV2,BusinessCoverageViewsOwnerV2,BusinessPureGenerationOwnerV2,CheckedDirectApplicationV2,BoundU0EntryV2,BusinessCheckedViewsV2,U0SourceArtifactV2} from './business-authoring-stages-v2.js';
import type {BusinessDirectApplicationImplementationV2} from './business-authoring-application.js';
import type {createBusinessRequestStagesOwnerV2,U0RequestNativeAssetsOwnerV2} from './business-authoring-request.js';
import type {createDirectPureSourceComponentOwnerV2,GeneratedDirectPureSourceComponentV2} from './application-adapter.js';
import {composeDirectRequestApplicationPlanDataV2} from '../generation/request-application-plan-v1.js';
import {U0_ADAPTER_FAILURES,checkU0WireConfiguration,type U0WireConfiguration} from './u0-realization-contract.js';
import {assertDirectBusinessSourceGraphV2Current,type CheckedDirectBusinessSourceGraphV2} from '../formalization/direct-condition-binding.js';

type OutputFileV2=Readonly<{relative_path:string;content:string}>;
interface OutputPhysicalV2 {readonly path:string;readonly content:string;readonly bytes:number;readonly sha256:string;readonly fingerprint:string}
function outputFail(code:string,at:string,message:string):never{return reject('BUSINESS_OUTPUT_'+code,at,message);}
function outputPathV2(value:string,absolute=false):string {
 if(typeof value!=='string'||!value||value.length>4096||/[\\\u0000-\u001f\u007f]/.test(value)||value.split('/').some(part=>part==='.'||part==='..')||(absolute?(!path.isAbsolute(value)||path.normalize(value)!==value||value===path.parse(value).root):(path.isAbsolute(value)||path.posix.normalize(value)!==value||value.split('/').some(part=>!part))))outputFail('PATH',String(value),'normalized contained path required');return value;
}
function outputReadV2(file:string):OutputPhysicalV2 {
 outputPathV2(file,true);
 const ancestry=()=>{let at=path.parse(file).root;const rows:string[]=[];for(const part of ['',...path.dirname(file).slice(at.length).split(path.sep).filter(Boolean)]){if(part)at=path.join(at,part);const s=fs.lstatSync(at,{bigint:true});if(!s.isDirectory()||s.isSymbolicLink())outputFail('FILE',file,'original nonsymlink ancestry required');rows.push(at+':'+s.dev+':'+s.ino);}return rows;};
 const parents=ancestry(),before=fs.lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||before.size<1n||before.size>16777216n)outputFail('FILE',file,'bounded regular UTF8 artifact required');
 const physical=(s:typeof before)=>[s.dev,s.ino,s.mode,s.size,s.mtimeNs,s.ctimeNs].map(String),fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK),chunks:Buffer[]=[];let size=0;
 try{if(dataDigest(physical(fs.fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))outputFail('STALE',file,'file changed while opening');for(;;){const b=Buffer.alloc(65536),n=fs.readSync(fd,b,0,b.length,null);if(!n)break;size+=n;if(size>16777216)outputFail('FILE',file,'artifact byte bound exceeded');chunks.push(b.subarray(0,n));}if(dataDigest(physical(fs.fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))outputFail('STALE',file,'file changed while reading');}finally{fs.closeSync(fd);}
 if(size!==Number(before.size)||dataDigest(physical(fs.lstatSync(file,{bigint:true})))!==dataDigest(physical(before))||dataDigest(ancestry())!==dataDigest(parents))outputFail('STALE',file,'original physical artifact changed');
 const bytes=Buffer.concat(chunks),content=bytes.toString('utf8');if(!Buffer.from(content).equals(bytes))outputFail('FILE',file,'exact UTF8 source required');
 const hash=sha256(bytes);return {path:file,content,bytes:size,sha256:hash,fingerprint:dataDigest({file,parents,physical:physical(before),sha256:hash})};
}
const outputExtensionV2=path.extname(fileURLToPath(import.meta.url));
const outputImplementationPathsV2=[import.meta.url,...['../generation/atomic-publication','../generation/atomic-publication-native','../generation/atomic-publication-native.generated','../generation/request-application-plan-v1','./business-authoring-coverage-contract-v2'].map(relative=>new URL(relative+outputExtensionV2,import.meta.url).href)];
const outputImplementationV2=()=>dataDigest({node:process.version,files:outputImplementationPathsV2.map(url=>outputReadV2(fileURLToPath(url)).fingerprint)});
const executingOutputImplementationV2=outputImplementationV2();
function assertOutputImplementationV2():void {if(outputImplementationV2()!==executingOutputImplementationV2)outputFail('IMPLEMENTATION_STALE','/output','reload changed output/native implementation');}
function checkedFilesV2(input:readonly OutputFileV2[]):readonly OutputFileV2[] {
 const data=captureJson(input) as unknown as readonly OutputFileV2[];
 if(!Array.isArray(data)||!data.length||data.length>1024)outputFail('FILES','/files','nonempty bounded complete output inventory required');
 const names=new Set<string>();for(const row of data){if(!row||Object.keys(row).sort().join(',')!=='content,relative_path'||typeof row.content!=='string'||!row.content||Buffer.byteLength(row.content)>16777216||/[\uD800-\uDFFF]/u.test(row.content))outputFail('FILES','/files','closed exact UTF8 output source required');const name=outputPathV2(row.relative_path);if(names.has(name))outputFail('FILES',name,'one exact artifact per path required');names.add(name);}
 for(const name of names){let parent=path.posix.dirname(name);while(parent!=='.'){if(names.has(parent))outputFail('FILES',name,'file/directory namespace collision');parent=path.posix.dirname(parent);}}
 return Object.freeze([...data].sort((a,b)=>a.relative_path<b.relative_path?-1:a.relative_path>b.relative_path?1:0));
}
/** Reads exact tree bytes/inventory without repairing anything or following links. */
function assertOutputTreeV2(target:string,files:readonly OutputFileV2[]):void {
 outputPathV2(target,true);const before=fs.lstatSync(target,{bigint:true});if(!before.isDirectory()||before.isSymbolicLink()||fs.realpathSync(target)!==target)outputFail('TREE',target,'original real output directory required');
 const dirs=new Set(['']);for(const row of files){let at=path.posix.dirname(row.relative_path);while(at!=='.'){dirs.add(at);at=path.posix.dirname(at);}}
 for(const dir of dirs){const at=path.join(target,dir),s=fs.lstatSync(at,{bigint:true});if(!s.isDirectory()||s.isSymbolicLink())outputFail('TREE',at,'only actual owned directory entries allowed');const expected=[...files.filter(row=>path.posix.dirname(row.relative_path)===(dir||'.')).map(row=>path.posix.basename(row.relative_path)),...[...dirs].filter(child=>child&&path.posix.dirname(child)===(dir||'.')).map(child=>path.posix.basename(child))].sort();if(dataDigest(fs.readdirSync(at).sort())!==dataDigest(expected))outputFail('TREE',at,'exact required file/directory inventory differs');}
 for(const row of files){const actual=outputReadV2(path.join(target,row.relative_path));if(actual.content!==row.content||actual.sha256!==sha256(row.content)||actual.bytes!==Buffer.byteLength(row.content))outputFail('TREE',row.relative_path,'actual required artifact differs');}
 const after=fs.lstatSync(target,{bigint:true});if(before.dev!==after.dev||before.ino!==after.ino||after.isSymbolicLink()||fs.realpathSync(target)!==target)outputFail('STALE',target,'output root identity changed');
}
function freshOutputV2(target:string,filesInput:readonly OutputFileV2[],assertCurrent:()=>void):void {
 const files=checkedFilesV2(filesInput);outputPathV2(target,true);assertCurrent();
 publishBusinessAuthoringDirectory(target,files,'.domainspec-business-uout-',stage=>{assertCurrent();assertOutputTreeV2(stage,files);assertCurrent();});
 assertCurrent();assertOutputTreeV2(target,files);assertCurrent();
}
function normalizedOutputPlanV2(input:BusinessOutputPlanV2):BusinessOutputPlanV2 {
 const data=captureJson(input) as unknown as BusinessOutputPlanV2;
 if(!data||!Array.isArray(data.outputs))outputFail('PLAN','/plan','explicit finite code-only output plan required');
 const expected=planBusinessOutputsV2(data.outputs.map(row=>({kind:row.kind,requiredness:row.requiredness})));
 if(dataDigest(data)!==dataDigest(expected))outputFail('PLAN','/plan','exact declared plan states required; readiness data cannot mint output');return expected;
}
function outputSourceV2(file:string,content:string):U0SourceArtifactV2 {outputPathV2(file);return Object.freeze({path:file,content,sha256:sha256(content)});}
const jsonOutputV2=(file:string,value:unknown)=>outputSourceV2(file,JSON.stringify(captureJson(value),null,2)+'\n');
const primaryOutputPathV2:Readonly<Partial<Record<BusinessOutputKindV2,string>>>=Object.freeze({code:'outputs/code.json','api-contracts':'api/contracts.json','business-graph':'views/business.json','system-graph':'views/system.json','business-system-bridge':'views/bridge.json'});
function outputResultV2(plan:BusinessOutputPlanV2,files:readonly BusinessOutputArtifactInputV2[],state:'produced'|'pending-producer'|'failed'|'stale'):BusinessOutputResultV2 {
 const rows=plan.outputs.map(row=>{
  if(row.state==='unsupported-optional')return {kind:row.kind,requiredness:row.requiredness,state:'unsupported-optional',artifact:null};
  if(state!=='produced')return {kind:row.kind,requiredness:row.requiredness,state:state==='failed'?(row.requiredness==='required'?'failed-required':'failed-optional'):state,artifact:null};
  const item=files.find(item=>item.kind===row.kind&&item.artifact.path===primaryOutputPathV2[row.kind]);if(!item)outputFail('INCOMPLETE',row.kind,'actual primary output producer missing');
  return {kind:row.kind,requiredness:row.requiredness,state:'produced',artifact:{path:item.artifact.path,sha256:item.artifact.sha256,bytes:Buffer.byteLength(item.artifact.content),checked_owner_sha256:item.checked_owner_sha256,producer_sha256:item.producer_sha256}};
 });return captureJson({schema_version:'craft.business-output-result/v2-candidate',rows,authority_effect:'none'}) as unknown as BusinessOutputResultV2;
}
/** Pure relocation data only: production first checks the exact Q01 original
 * bytes and real captures. This function cannot create a bound/native handle. */
export function relocateU0EntrySourceDataV2(content:string,callablePath:string,handlerPath:string){
 outputPathV2(callablePath,true);outputPathV2(handlerPath,true);
 const name=path.basename(handlerPath);if(!/^[a-z][a-z0-9-]*\.m?js$/.test(name))outputFail('RELOCATION',handlerPath,'finite JavaScript runtime filename required');
 const relocations=Object.freeze([Object.freeze({from:pathToFileURL(callablePath).href,to:'./callable/invoke.mjs'}),Object.freeze({from:pathToFileURL(handlerPath).href,to:'./runtime/'+name})]);
 let portable=content;
 for(const row of relocations){const quoted=JSON.stringify(row.from);if(portable.split(quoted).length!==2)outputFail('RELOCATION','/entry','exact two original import literals required');portable=portable.replace(quoted,JSON.stringify(row.to));}
 return Object.freeze({kind:'u0-entry-relocation-data-v2' as const,content:portable,sha256:sha256(portable),relocations,authority_effect:'none' as const});
}
/** Checked source-to-wire API data; original accepted/native ownership is
 * additionally required by prepareArtifacts. No ready/realized handle here. */
export function deriveDirectApiOutputDataV2(source:CheckedDirectBusinessSourceGraphV2,configuration:U0WireConfiguration){
 assertDirectBusinessSourceGraphV2Current(source);const wire=checkU0WireConfiguration(configuration),spec=source.checked.transfer.spec,entity=spec.entities[0]!,flag=entity.fields.find(field=>field.type==='Bool')!;
 return captureJson({schema_version:'craft.business-api-contract/v2-candidate',interface:source.api,logical_entry:spec.entries[0],wire,wire_payload:{kind:'closed-record',unknown_members:'reject',decoded_duplicate_members:'reject',fields:[{name:'id',domain_field:entity.identity,json_type:'string',encoding:'canonical-decimal',minimum:'0',maximum:'18446744073709551615'},{name:'verified',domain_field:flag.name,json_type:'boolean'}]},mapping_owners:source.closures.filter(row=>row.role==='Mapping'),outcomes:{completed:{status:200,kind:'completed',value:'wire-payload'},rejected:{status:422,kind:'rejected',code:source.operation.rejection_code},adapter_errors:U0_ADAPTER_FAILURES},authority_effect:'none',open_questions:['Only the finite injected HTTP cell is represented; native binding, installed behavior, listener and other transports are separately qualified.']}) as Readonly<Record<string,unknown>>;
}
export interface BusinessOutputWriterImplementationV2 extends BusinessOutputWriterOwnerV2 {
 prepareArtifacts(plan:BusinessOutputPlanV2,application:CheckedDirectApplicationV2,bound:BoundU0EntryV2,views:BusinessCheckedViewsV2):readonly BusinessOutputArtifactInputV2[];
}
type OutputRequestOwnerV2=Pick<ReturnType<typeof createBusinessRequestStagesOwnerV2>,'source'|'assertEarlyCurrent'|'assertBoundCurrent'>;
/** Immutable trusted SDK producer instances; no host callback in a request. */
export function createBusinessOutputWriterOwnerV2(applications:BusinessDirectApplicationImplementationV2,requests:OutputRequestOwnerV2,generation:BusinessPureGenerationOwnerV2,viewsOwner:BusinessCoverageViewsOwnerV2,native:U0RequestNativeAssetsOwnerV2):BusinessOutputWriterImplementationV2 {
 const original=[applications.assertCurrent,applications.assertConditionCurrent,applications.source,requests.source,requests.assertEarlyCurrent,requests.assertBoundCurrent,generation.assertCurrent,viewsOwner.assertCurrent,native.assertCurrent,native.assertSelectionBasis,native.assets];
 const scopes=new WeakMap<object,{plan:BusinessOutputPlanV2;application:CheckedDirectApplicationV2;bound:BoundU0EntryV2;views:BusinessCheckedViewsV2;files:readonly OutputFileV2[];physical:readonly OutputPhysicalV2[];fingerprint:string}>();
 const assertOwners=()=>{assertOutputImplementationV2();if(original.some((method,i)=>method!==[applications.assertCurrent,applications.assertConditionCurrent,applications.source,requests.source,requests.assertEarlyCurrent,requests.assertBoundCurrent,generation.assertCurrent,viewsOwner.assertCurrent,native.assertCurrent,native.assertSelectionBasis,native.assets][i]))outputFail('OWNER_STALE','/output','exact original SDK output producer methods required');};
 const current=(application:CheckedDirectApplicationV2,bound:BoundU0EntryV2,views:BusinessCheckedViewsV2):void=>{
  assertOwners();applications.assertCurrent(application);applications.assertConditionCurrent(application.condition);requests.assertEarlyCurrent(application.input.early_requests);requests.assertBoundCurrent(bound);generation.assertCurrent(bound.callable);viewsOwner.assertCurrent(views);native.assertCurrent(bound.basis);native.assertSelectionBasis(application.input.selection,bound.basis);
  if(bound.early!==application.input.early_requests||bound.callable.source.application!==application||views.coverage.application!==application||views.coverage.bound!==bound||bound.subject.callable_sha256!==bound.callable.artifact.sha256||bound.subject.handler_sha256!==bound.handler_artifact.sha256||bound.subject.basis_sha256!==bound.basis.basis_sha256)outputFail('JOIN','/output','one identical original input/application/generation/native/bound/views scope required');
 };
 const prepareArtifacts=(planInput:BusinessOutputPlanV2,application:CheckedDirectApplicationV2,bound:BoundU0EntryV2,views:BusinessCheckedViewsV2):readonly BusinessOutputArtifactInputV2[]=>{
  current(application,bound,views);const plan=normalizedOutputPlanV2(planInput),checked=applications.source(application),earlySource=requests.source(bound.early),assets=native.assets(bound.basis);
  if(assets.length!==4||new Set(assets.map(row=>row.role)).size!==4)outputFail('NATIVE','/assets','all four original runtime roles required');
  const physical:OutputPhysicalV2[]=[],byRole=new Map<string,{file:OutputPhysicalV2;name:string;id:string}>(),names=new Set<string>();
  for(const asset of assets){const file=outputReadV2(asset.artifact.path),records=bound.basis.artifacts.filter(row=>row.requirement.artifact_id===asset.basis_artifact_id);if(records.length!==1||records[0]!.sha256!==file.sha256||records[0]!.bytes!==file.bytes||dataDigest(asset.artifact)!==dataDigest({path:file.path,sha256:file.sha256,bytes:file.bytes}))outputFail('NATIVE',file.path,'actual selected asset bytes required');const name=path.basename(file.path);if(!/^[a-z][a-z0-9-]*\.m?js$/.test(name)||names.has(name))outputFail('NATIVE',name,'distinct finite JavaScript runtime filenames required');names.add(name);physical.push(file);byRole.set(asset.role,{file,name,id:asset.basis_artifact_id});}
  const runtime=byRole.get('handler');if(!runtime)outputFail('NATIVE','/handler','actual selected handler required');
  // The four qualified native modules must form a closed builtin/local closure.
  for(const {file}of byRole.values()){if(/\b(?:import\s*\(|require\s*\()/.test(file.content))outputFail('NATIVE',file.path,'dynamic runtime imports are not a supported finite output closure');for(const match of file.content.matchAll(/\bfrom\s*['"]([^'"]+)['"]/g)){const target=match[1]!;if(target.startsWith('node:'))continue;if(!target.startsWith('./')||!names.has(target.slice(2)))outputFail('NATIVE',file.path,'all static native runtime imports must be included');}}
  const originPlan=composeDirectRequestApplicationPlanDataV2(earlySource,{executable_sha256:earlySource.executable_sha256,capture_sha256:application.input.capture.capture_sha256,basis_sha256:bound.basis.basis_sha256,callable:bound.callable.artifact,infrastructure_handler:{path:runtime.file.path,sha256:runtime.file.sha256,bytes:runtime.file.bytes},configuration:bound.basis.configuration,rejection_code:checked.operation.rejection_code,business_graph_sha256:application.graph.graph_sha256,entity_ref:checked.checked.roles.selectors.entity,closures:application.graph.closures});
  const entry=outputReadV2(bound.handler_artifact.path),graph=outputReadV2(originPlan.graph_file.path);physical.push(entry,graph);
  if(entry.path!==originPlan.entry.path||entry.content!==originPlan.entry.content||entry.sha256!==bound.subject.handler_sha256||graph.content!==originPlan.graph_file.content||graph.sha256!==bound.subject.request_graph_sha256)outputFail('JOIN','/entry','actual original late entry and request graph bytes required');
  const relocated=relocateU0EntrySourceDataV2(entry.content,bound.callable.artifact.path,runtime.file.path),portable=relocated.content,relocations=relocated.relocations;
  const codeSources=[jsonOutputV2('package.json',{type:'module',private:true,engines:{node:process.versions.node},exports:{'.':'./entry.mjs'}}),...bound.callable.source.files.map(file=>outputSourceV2('callable/'+file.path,file.content)),...assets.map(asset=>{const row=byRole.get(asset.role)!;return outputSourceV2('runtime/'+row.name,row.file.content);}),outputSourceV2('entry.mjs',portable),outputSourceV2('evidence/original-bound-entry.txt',entry.content),outputSourceV2('evidence/original-request-graph.json',graph.content)];
  const lineage=jsonOutputV2('evidence/output-lineage.json',{schema_version:'craft.business-output-lineage/v2-candidate',original_realization:bound.subject,native_basis:bound.basis,generated_source_sha256:bound.callable.source.source_sha256,relocations,portable_entry:{path:'entry.mjs',sha256:sha256(portable)},native_assets:assets,authority_effect:'none',open_questions:['Relocated module behavior is independently observed at V02; this producer does not mint a new bound/native realization.']});codeSources.push(lineage);
  const codeIndex=jsonOutputV2('outputs/code.json',{schema_version:'craft.business-code-bundle/v2-candidate',entry:'entry.mjs',abi:bound.callable.source.abi,files:codeSources.map(file=>({path:file.path,sha256:file.sha256,bytes:Buffer.byteLength(file.content)})),original_realized_sha256:bound.subject.realized_sha256,authority_effect:'none',open_questions:['Native observations, installed qualification, hosting and publication are separate.']});
  const producer=outputReadV2(fileURLToPath(import.meta.url)).sha256,viewProducer=outputReadV2(fileURLToPath(new URL('./business-authoring-views'+outputExtensionV2,import.meta.url))).sha256;
  const api=jsonOutputV2('api/contracts.json',deriveDirectApiOutputDataV2(checked,bound.basis.configuration));
  const rows:BusinessOutputArtifactInputV2[]=[];const put=(kind:BusinessOutputKindV2,artifact:U0SourceArtifactV2,owner:string,producerHash=producer)=>rows.push(Object.freeze({kind,artifact,checked_owner_sha256:owner,producer_sha256:producerHash}));
  const selected=new Set(plan.outputs.filter(row=>row.state==='pending-producer').map(row=>row.kind));if(selected.has('code'))for(const file of [...codeSources,codeIndex])put('code',file,bound.subject.realized_sha256);
  if(selected.has('api-contracts'))put('api-contracts',api,checked.closures.find(row=>row.role==='Interface')!.typed_closure_sha256);
  for(const row of views.files)if(selected.has(row.kind))put(row.kind,row.artifact,views.views_sha256,viewProducer);
  for(const row of plan.outputs)if(row.state==='pending-producer'&&!rows.some(file=>file.kind===row.kind&&file.artifact.path===primaryOutputPathV2[row.kind]))outputFail('INCOMPLETE',row.kind,'every selected supported output requires an actual producer');
  const artifacts=Object.freeze(rows),files=checkedFilesV2(artifacts.map(row=>({relative_path:row.artifact.path,content:row.artifact.content})));
  scopes.set(artifacts,{plan,application,bound,views,files,physical,fingerprint:dataDigest(artifacts)});current(application,bound,views);return artifacts;
 };
 function requestState(request:BusinessFreshOutputRequestV2){
  if(!request||typeof request!=='object'||nativeTypes.isProxy(request)||![Object.prototype,null].includes(Object.getPrototypeOf(request)))outputFail('REQUEST','/request','plain original request structure required');
  const d=Object.getOwnPropertyDescriptors(request) as Record<string,PropertyDescriptor>;if(Reflect.ownKeys(d).some(key=>typeof key!=='string')||Object.keys(d).sort().join(',')!=='application,artifacts,bound,plan,target,views'||Object.values(d).some(row=>!Object.hasOwn(row,'value')||!row.enumerable))outputFail('REQUEST','/request','closed own-data request fields required');
  // Registry lookup precedes inspection of any caller artifact or app data.
  const state=scopes.get(d.artifacts!.value);if(!state)outputFail('HANDLE','/artifacts','original prepared output artifacts from this exact producer required');
  if(d.application!.value!==state.application||d.bound!.value!==state.bound||d.views!.value!==state.views||dataDigest(normalizedOutputPlanV2(d.plan!.value))!==dataDigest(state.plan))outputFail('JOIN','/request','original output scope and exact plan required');const target=outputPathV2(d.target!.value,true);return {...state,target,artifacts:d.artifacts!.value as readonly BusinessOutputArtifactInputV2[]};
 }
 const assertState=(state:ReturnType<typeof requestState>,artifacts:readonly BusinessOutputArtifactInputV2[])=>{
  current(state.application,state.bound,state.views);if(dataDigest(artifacts)!==state.fingerprint)outputFail('STALE','/artifacts','original immutable output artifacts changed');for(const file of state.physical)if(outputReadV2(file.path).fingerprint!==file.fingerprint)outputFail('STALE',file.path,'original selected native/bound bytes changed');
 };
 return Object.freeze({prepareArtifacts,publish(request:BusinessFreshOutputRequestV2):BusinessOutputResultV2{
  const state=requestState(request);assertState(state,state.artifacts);freshOutputV2(state.target,state.files,()=>assertState(state,state.artifacts));return outputResultV2(state.plan,state.artifacts,'produced');
 },check(request:BusinessFreshOutputRequestV2):BusinessOutputResultV2{
  const state=requestState(request);try{assertState(state,state.artifacts);}catch{return outputResultV2(state.plan,state.artifacts,'stale');}
  try{fs.lstatSync(state.target);}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return outputResultV2(state.plan,state.artifacts,'pending-producer');throw error;}
  try{assertOutputTreeV2(state.target,state.files);}catch{return outputResultV2(state.plan,state.artifacts,'failed');}
  try{assertState(state,state.artifacts);}catch{return outputResultV2(state.plan,state.artifacts,'stale');}return outputResultV2(state.plan,state.artifacts,'produced');
 }});
}

/** Same actual output primitive/currentness for a genuinely generated source
 * component. Its distinct result can never satisfy BusinessOutputResultV2. */
export function createDirectSourceOutputOwnerV2(generation:ReturnType<typeof createDirectPureSourceComponentOwnerV2>){
 const assertSource=generation.assertSourceCurrent;
 const current=(source:GeneratedDirectPureSourceComponentV2)=>{assertOutputImplementationV2();if(generation.assertSourceCurrent!==assertSource)outputFail('OWNER_STALE','/source-output','original source generation producer required');generation.assertSourceCurrent(source);};
 const files=(source:GeneratedDirectPureSourceComponentV2)=>checkedFilesV2(source.files.map(row=>({relative_path:row.path,content:row.content})));
 return Object.freeze({publish(source:GeneratedDirectPureSourceComponentV2,target:string){current(source);const artifacts=files(source);freshOutputV2(target,artifacts,()=>current(source));return Object.freeze({kind:'published-direct-source-output-component-v2' as const,target,source_sha256:source.source_sha256,files:artifacts.map(row=>({path:row.relative_path,sha256:sha256(row.content),bytes:Buffer.byteLength(row.content)})),authority_effect:'none' as const});},check(source:GeneratedDirectPureSourceComponentV2,target:string){current(source);assertOutputTreeV2(target,files(source));current(source);return Object.freeze({kind:'checked-direct-source-output-component-v2' as const,target,source_sha256:source.source_sha256,authority_effect:'none' as const});}});
}
