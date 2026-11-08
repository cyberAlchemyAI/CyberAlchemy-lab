import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {getReconciledSource as source,MINIMAL_VALUE_CONTEXT_SHA256} from '../../src/generation/reconciled-sources.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings,OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings,WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {selectWorkflowRecoveryPolicy,WORKFLOW_RECOVERY_POLICY_VERSION,WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';
import {WORKFLOW_OCCURRENCES_VERSION} from '../../src/typed-backend/workflow-occurrences.ts';
import {planResolvedArtifacts,RESOLVED_ARTIFACT_SELECTION_VERSION,RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {compilePublicMapping} from '../../src/input/compiled-public-mapping.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
const common={configuration:source('configuration'),base:source('base'),typescript:source('typescript')};
const rules={...common,rule_contract:source('rule'),collection_contract:source('rule_collection'),predicate_contract:source('rule_predicate'),numeric_contract:source('rule_numeric'),exact_contract:source('rule_exact'),literal_contract:source('rule_literal'),structured_contract:source('rule_structured'),field_contract:source('field')};
const events={...common,event_contract:source('event')};
const operations={operation_contract:source('operation'),factory_contract:source('factory'),enum_provider:source('enum_provider'),rules,events};
const workflows={workflow_contract:source('workflow'),materialization_contract:source('workflow_materialization'),outcome_contract:source('workflow_outcome'),recovery_contract:source('workflow_recovery'),operations};
const publicSources={...common,generation_contract:source('public_boundary'),public_mapping_contract:source('public_mapping'),interface_contract:source('interface')};
const scalar=(name='UInt64'):any=>({kind:'scalar',name}),at=(root:string):any=>({op:'path',root,properties:[]});
function fixture(t:any,enumValues=false,typeOverride:any=null,eventFree=false){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-minimal-values-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const folder=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const file=path.join(folder,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
 const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/minimal/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'minimal',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/minimal/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'minimal',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 if(enumValues){
  node('status','Enum',{values:['Ready','Waiting'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'MINIMAL-STATUS',variants:['Ready','Waiting'].map(name=>({name,ontology_variant:'MINIMAL-STATUS#'+name,payload:null}))}});
  node('answer','Enum',{values:['None','Amount','Status'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'MINIMAL-ANSWER',variants:[{name:'None',ontology_variant:'MINIMAL-ANSWER#None',payload:null},{name:'Amount',ontology_variant:'MINIMAL-ANSWER#Amount',payload:scalar()},{name:'Status',ontology_variant:'MINIMAL-ANSWER#Status',payload:{kind:'named',selector:'minimal:status'}}]}});
 }
 const type=typeOverride??(enumValues?{kind:'named',selector:'minimal:answer'}:scalar());
 const inputs=[{name:'value',type},{name:'allowed',type:scalar('Bool')}];
 node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'MINIMAL-ALLOWED',parameters:[{name:'value',type:scalar('Bool')}],expression:{op:'eq',left:at('value'),right:{op:'literal',type:'Bool',value:true}}}});
 if(!eventFree)node('notice','Event',{event_type:'notice',version:'1',occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[]});
 node('perform','Operation',{reads:[],writes:[],effects:eventFree?[]:['notice'],guard:'allowed',failure_continuation:'return-error'});
 edge('guard-perform','enforces','allowed','perform');if(!eventFree)edge('perform-notice','produces','perform','notice');
 node('flow','Workflow',{typed_contract:{schema_version:WORKFLOW_OCCURRENCES_VERSION,ontology_workflow:'MINIMAL-FLOW',steps:[{step_id:'perform',operation_ref:'minimal:perform'}],compensations:[]}});
 edge('flow-perform','orchestrates','flow','perform');
 node('api','Interface',{typed_contract:{schema_version:'domainspec.typed-interface/v1',ontology_interface:'MINIMAL-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'response',ontology_contract:'MINIMAL-RESPONSE',fields:[{name:'value',ontology_field:'MINIMAL-RESPONSE#value',meaning:'value',type}]}],operations:[{operation_id:'perform',operation_ref:'minimal:perform',request:type,result:{kind:'contract',contract_id:'response'}}]}});
 edge('api-perform','exposes','api','perform');
 const mapping:any={schema_version:'domainspec.typed-mapping/v3',ontology_mapping:'MINIMAL-MAPPING',inputs:[{name:'value',type,use:null}],target:{kind:'contract',interface_selector:'minimal:api',contract_id:'response'},target_use:{interface_selector:'minimal:api',operation_id:'perform',side:'result'},fields:[{target:'value',value:at('value'),default:null}],total:true};
 node('summary','Mapping',{target:'minimal:api',typed_contract:mapping});edge('summary-api','maps','summary','api');
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'minimal-values',features:['minimal'],cross_feature_edges:[]});
 write('specs/minimal/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'minimal',nodes,edges});
 const graph=loadCompiledProjectGraph(folder),certificate=createCompiledProjectCertificate(graph);
 const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},source('composition'));
 const fields=enumValues?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:[type.kind==='named'?type.selector:'minimal:answer'],bindings:[]},source('field')):null;
 const actionInput:any={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'minimal:perform',inputs,reads:[],writes:[],guards:[{selector:'minimal:allowed',arguments:[{parameter:'value',value:at('allowed')}]}],events:eventFree?[]:[{slot:'notice',target:'minimal:notice',parameter:'notice_input'}],result:{type,value:at('value')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
 const action=compileOperationActionBindings(graph,boundary,fields,actionInput,source('operation_action'));
 const workflowInput:any={schema_version:WORKFLOW_BINDINGS_VERSION,selector:'minimal:flow',inputs,event_inputs:eventFree?[]:[{name:'notice',event_ref:'minimal:notice'}],steps:[{step_id:'perform',action_sha256:action.action_sha256,arguments:inputs.map(p=>({parameter:p.name,value:{op:'input',name:p.name,properties:[]}})),events:eventFree?[]:[{parameter:'notice_input',input:'notice'}]}],compensations:[],result:{type,value:{op:'step-result',step_id:'perform',properties:[]}}};
 const workflow=compileWorkflowBindings(graph,boundary,fields,[action],workflowInput,source('workflow_binding'));
 const policy=selectWorkflowRecoveryPolicy(workflow,{schema_version:WORKFLOW_RECOVERY_POLICY_VERSION,workflow_sha256:workflow.workflow_sha256,contract_sha256:WORKFLOW_RECOVERY_CONTRACT_SHA256,dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'},source('workflow_recovery'));
 const layout={language:'typescript',module_root:'application'};
 const requests:any[]=[
  {kind:'workflows',fields,selection:{schema_version:'domainspec.configured-workflow-selection/v1-candidate',...layout,workflow,policy,actions:[action],factories:[]},sources:workflows},
  {kind:'public-boundaries',fields,selection:{schema_version:'domainspec.configured-public-boundaries-selection/v1-candidate',...layout,value_profile:EXACT_UINT64_PROFILE,roots:['minimal:api','minimal:summary']},sources:publicSources}
 ];
 const selection:any={schema_version:RESOLVED_ARTIFACT_SELECTION_VERSION,...layout,layout_version:RESOLVED_ARTIFACT_LAYOUT,graph_sha256:certificate.graph_sha256,boundary_sha256:boundary.boundary_sha256,requests};
 return {temp,folder,write,graph,boundary,fields,action,actionInput,workflow,workflowInput,policy,selection,mapping,plan:()=>planResolvedArtifacts(graph,boundary,selection,source('resolved_artifact'))};
}
function native(t:any,f:ReturnType<typeof fixture>){
 const p=f.plan(),root=path.join(f.temp,'native');fs.mkdirSync(root);
 for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:[...process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))]}),deps=path.dirname(path.dirname(path.dirname(types)));
 const image=nativeToolchainImage();
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--mount','type=bind,source='+deps+',target='+deps+',readonly','--workdir',root,image];
 const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...p.artifacts.map(a=>a.relative_path)],{encoding:'utf8'});
 try{compile();}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 const load=(suffix:string)=>{const a=p.artifacts.find(a=>a.relative_path.endsWith(suffix))!;assert.ok(a,suffix);return require(path.join(root,'js',a.relative_path.replace(/\.ts$/,'.js')));};
 return {p,root,compile,load};
}
const notice={occurrence:{id:'event-one'},occurredAt:'2026-09-09',payload:{}};
const ids={workflow_execution_id:'execution-one',failure_occurrence_id:'failure-one'};
function provider(status='committed'){
 const trace:string[]=[];
 return {trace,dependency:{store:{begin:async()=>{trace.push('begin');return {read:async()=>{throw Error('no reads');},rollback:async()=>{trace.push('rollback');},commit:async(batch:any)=>{trace.push('commit');assert.equal(batch.writes.length,0);assert.equal(batch.events.length,1);return {status};}};}}}};
}
test('scalar-only checked construction and shared generation require no domain declaration or development file',async t=>{
 const original=fs.readFileSync;
 (fs as any).readFileSync=(file:any,...args:any[])=>{if(String(file).includes('/development/'))throw Error('forbidden development read');return (original as any)(file,...args);};
 let f:ReturnType<typeof fixture>;try{f=fixture(t);f.plan();}finally{fs.readFileSync=original;}
 assert.equal(f.fields,null);assert.equal(f.action.field_compilation_sha256,null);assert.equal(f.workflow.field_compilation_sha256,null);
 assert.ok(f.graph.nodes.every(n=>!['Entity','Value Object','Enum'].includes(n.kind)));
 const n=native(t,f),p=n.p;
 assert.ok(p.artifacts.every(a=>!a.relative_path.includes('/entities/')&&!a.relative_path.includes('/value-objects/')&&!a.relative_path.includes('/enums/')));
 assert.ok(p.source_blobs.some(s=>s.sha256===MINIMAL_VALUE_CONTEXT_SHA256));
 for(const id of ['operation_action','workflow_binding','workflow_recovery','workflow_materialization','workflow_outcome'] as const)assert.ok(p.source_blobs.some(s=>s.content===source(id)),id);
 const s=provider(),run=n.load('/workflows/flow.ts').workflowFlow,out=await run({value:'18446744073709551615',allowed:true,notice},ids,{'minimal:perform':s.dependency});
 assert.equal(out.status,'succeeded');assert.equal(out.value,18446744073709551615n);assert.deepEqual(s.trace,['begin','commit']);
 assert.deepEqual(n.load('/mappings/summary.ts').mappingSummary({value:out.value}),{value:18446744073709551615n});
 const no=provider(),rejected=await run({value:1,allowed:false,notice},ids,{'minimal:perform':no.dependency});
 assert.equal(rejected.status,'forward-stopped');assert.deepEqual(no.trace,['begin','rollback']);
 const uncertain={store:{begin:async()=>({read:async()=>null,rollback:async()=>{},commit:async()=>{throw Error('unknown commit');}})}};
 const unknown=await run({value:1,allowed:true,notice},ids,{'minimal:perform':uncertain});
 assert.notEqual(unknown.status,'succeeded');
 fs.renameSync(f.folder,path.join(f.temp,'moved'));assert.deepEqual(f.plan(),p);
});
test('Enum-only Operation and Workflow use real owned Enum/sum providers without a record factory',async t=>{
 const f=fixture(t,true),n=native(t,f);assert.ok(f.graph.nodes.every(n=>!['Entity','Value Object'].includes(n.kind)));
 assert.ok(n.p.artifacts.some(a=>a.relative_path.endsWith('/answer.sum.ts')));
 assert.ok(n.p.artifacts.some(a=>a.relative_path.endsWith('/status.component.ts')));
 assert.ok(n.p.source_blobs.some(s=>s.content===source('standalone_sum')));
 const run=n.load('/workflows/flow.ts').workflowFlow;
 for(const value of [{variant:'Amount',payload:'18446744073709551615'},{variant:'Status',payload:{variant:'Ready'}},{variant:'None'}]){
  const s=provider(),out=await run({value,allowed:true,notice},ids,{'minimal:perform':s.dependency});
  assert.equal(out.status,'succeeded');assert.equal(out.value.variant,value.variant);assert.equal(s.trace.filter(x=>x==='commit').length,1);
  assert.deepEqual(n.load('/mappings/summary.ts').mappingSummary({value:out.value}),{value:out.value});
 }
});
test('absent context preserves inline sum/list/set/optional value meanings',async t=>{
 const type={kind:'sum',variants:[{name:'None',ontology_variant:'MINIMAL-INLINE#None',payload:null},...(['list','set','optional'] as const).map(kind=>({name:{list:'Values',set:'Unique',optional:'Maybe'}[kind],ontology_variant:'MINIMAL-INLINE#'+kind,payload:{kind,element:scalar()}}))]};
 const f=fixture(t,false,type),n=native(t,f),run=n.load('/workflows/flow.ts').workflowFlow;
 for(const [value,expected] of [
  [{variant:'Values',payload:['9007199254740993','9007199254740993']},{variant:'Values',payload:[9007199254740993n,9007199254740993n]}],
  [{variant:'Unique',payload:['9007199254740993','2']},{variant:'Unique',payload:[9007199254740993n,2n]}],
  [{variant:'Maybe',payload:null},{variant:'Maybe',payload:null}],
  [{variant:'Maybe',payload:'18446744073709551615'},{variant:'Maybe',payload:18446744073709551615n}],
  [{variant:'None'},{variant:'None'}],
 ]){
  const s=provider(),out=await run({value,allowed:true,notice},ids,{'minimal:perform':s.dependency});
  assert.equal(out.status,'succeeded');assert.deepEqual(out.value,expected);
  assert.deepEqual(n.load('/mappings/summary.ts').mappingSummary({value:out.value}),{value:expected});
 }
 const s=provider();
 await assert.rejects(()=>run({value:{variant:'Unique',payload:['2',2]},allowed:true,notice},ids,{'minimal:perform':s.dependency}),/WORKFLOW_VALUE/);assert.deepEqual(s.trace,[]);
});
test('plain Enum-only closure does not acquire a sum or record provider',async t=>{
 const f=fixture(t,true,{kind:'named',selector:'minimal:status'}),n=native(t,f),s=provider();
 assert.deepEqual(f.fields!.model.declarations.map(d=>d.selector),['minimal:status']);
 assert.ok(n.p.artifacts.some(a=>a.relative_path.endsWith('/status.component.ts')));
 assert.ok(n.p.artifacts.every(a=>!a.relative_path.endsWith('.sum.ts')&&!a.relative_path.includes('/entities/')&&!a.relative_path.includes('/value-objects/')));
 const out=await n.load('/workflows/flow.ts').workflowFlow({value:{variant:'Ready'},allowed:true,notice},ids,{'minimal:perform':s.dependency});
 assert.equal(out.status,'succeeded');assert.deepEqual(out.value,{variant:'Ready'});
});
test('field-free guard-only Operations do not acquire synthetic Events or state writes',async t=>{
 const f=fixture(t,false,null,true),n=native(t,f),trace:string[]=[];
 assert.ok(f.graph.nodes.every(n=>!['Entity','Value Object','Enum','Event'].includes(n.kind)));
 assert.ok(n.p.artifacts.every(a=>!a.relative_path.includes('/events/')));
 const dependencies={store:{begin:async()=>{trace.push('begin');return {read:async()=>{throw Error('no read');},rollback:async()=>{throw Error('no rollback');},commit:async(batch:any)=>{trace.push('commit');assert.deepEqual(batch.writes,[]);assert.deepEqual(batch.events,[]);return {status:'committed'};}};}}};
 const out=await n.load('/workflows/flow.ts').workflowFlow({value:'18446744073709551615',allowed:true},ids,{'minimal:perform':dependencies});
 assert.equal(out.status,'succeeded');assert.equal(out.value,18446744073709551615n);assert.deepEqual(trace,['begin','commit']);
});
test('missing/forged fields and unresolved named dependencies remain fail closed',t=>{
 const f=fixture(t),g=fixture(t,true);
 assert.throws(()=>compileOperationActionBindings(f.graph,f.boundary,undefined as any,f.actionInput,source('operation_action')));
 assert.throws(()=>compileOperationActionBindings(f.graph,f.boundary,{} as any,f.actionInput,source('operation_action')));
 assert.throws(()=>compileOperationActionBindings(g.graph,g.boundary,null,g.actionInput,source('operation_action')));
 assert.throws(()=>compileWorkflowBindings(g.graph,g.boundary,null,[g.action],g.workflowInput,source('workflow_binding')));
 assert.throws(()=>compilePublicMapping(g.graph,g.boundary,null,'minimal:summary',source('public_mapping')));
 for(const fields of [undefined,{},g.fields])assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:f.selection.requests.map((r:any)=>({...r,fields}))},source('resolved_artifact')));
 const request=f.selection.requests[0];
 assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[{...request,selection:{...request.selection,factories:[{selector:'minimal:fake'}]}}]},source('resolved_artifact')));
 for(const key of ['factory_contract','enum_provider'])assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[{...request,sources:{...workflows,operations:{...operations,[key]:(operations as any)[key]+' '}}}]},source('resolved_artifact')));
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
