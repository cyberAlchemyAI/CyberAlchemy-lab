import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planResolvedArtifacts,assertResolvedArtifactPlan,RESOLVED_ARTIFACT_SELECTION_VERSION,RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {planConfiguredCalculationsV2,CONFIGURED_CALCULATION_V2_VERSION} from '../../src/generation/configured-calculations-v2.ts';
import {STRUCTURED_RULE_VERSION,planConfiguredRules} from '../../src/generation/configured-rules.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {compileOperationActionBindings,OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings,WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {WORKFLOW_OCCURRENCES_VERSION} from '../../src/typed-backend/workflow-occurrences.ts';
import {selectWorkflowRecoveryPolicy,WORKFLOW_RECOVERY_POLICY_VERSION,WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
const base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const common={configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')};
const calculationSources={...common,calculation_contract:bytes(base+'calculation-v2-contract.json')};
const ruleSources={...common,rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const definition=bytes(base+'resolved-artifact-plan-contract.json');
function fixture(t:any) {
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-resolved-plan-'));
  t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  write('project.json',{schema_version:'domainspec.project/v1',project_id:'resolved-artifacts',features:['alpha','beta'],cross_feature_edges:[]});
  for (const feature of ['alpha','beta']) {
    write('specs/'+feature+'/feature.json',{schema_version:'domainspec.feature/v1',feature_id:feature,nodes:['total','allowed','mode'],edges:[]});
    const node=(id:string,kind:string,body:any)=>write('specs/'+feature+'/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:feature,node_id:id,kind,body:{description:id,...body}});
    node('total','Calculation',{inputs:[],typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'FIXTURE-'+feature.toUpperCase()+'-TOTAL',inputs:[],result:{kind:'scalar',name:'UInt64'},division_rounding:'reject',expression:{op:'literal',value:feature==='alpha'?'18446744073709551615':'7'}}});
    node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+feature.toUpperCase()+'-RULE',parameters:[{name:'value',type:{kind:'scalar',name:'Bool'}}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'literal',type:'Bool',value:true}}}});
    node('mode','Enum',{values:['On','Off'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-'+feature.toUpperCase()+'-MODE',variants:[{name:'On',ontology_variant:'FIXTURE-'+feature.toUpperCase()+'-MODE#On',payload:null},{name:'Off',ontology_variant:'FIXTURE-'+feature.toUpperCase()+'-MODE#Off',payload:null}]}});
  }
  const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph);
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},bytes('development/reconciliation-v1/contracts/composition-boundary.json'));
  const requests:any[]=[
    {kind:'calculations-v2',fields:null,selection:{schema_version:CONFIGURED_CALCULATION_V2_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,module_root:'application',boundary_sha256:boundary.boundary_sha256,roots:['alpha:total','beta:total']},sources:calculationSources},
    {kind:'rules',fields:null,selection:{schema_version:STRUCTURED_RULE_VERSION,language:'typescript',module_root:'application',value_profile:EXACT_UINT64_PROFILE,roots:['alpha:allowed','beta:allowed']},sources:ruleSources},
  ];
  const selection:any={schema_version:RESOLVED_ARTIFACT_SELECTION_VERSION,language:'typescript',layout_version:RESOLVED_ARTIFACT_LAYOUT,module_root:'application',graph_sha256:certificate.graph_sha256,boundary_sha256:boundary.boundary_sha256,requests};
  const plan=()=>planResolvedArtifacts(graph,boundary,selection,definition);
  return {temp,source,write,graph,boundary,selection,requests,plan};
}

function allTypesFixture(t:any) {
  const f=fixture(t),feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/feature.json'),'utf8'));
  const scalar=(name='String'):any=>({kind:'scalar',name}),named=(name:string):any=>({kind:'named',selector:'alpha:'+name});
  const at=(root:string,...properties:string[]):any=>({op:'path',root,properties});
  const lit=(type:string,value:any):any=>({op:'literal',type,value});
  const node=(id:string,kind:string,body:any)=>{if(!feature.nodes.includes(id))feature.nodes.push(id);f.write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
  const edge=(id:string,relationship:string,from:string,to:string)=>{feature.edges.push(id);f.write('specs/alpha/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
  const prop=(owner:string,name:string,type:any,identity=false)=>({name,type,identity,cardinality:'one',meaning:name,ontology_property:'FIXTURE-'+owner.toUpperCase()+'#'+name});
  const rule=(id:string,name:string,type:any,expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters:[{name,type}],expression}});
  rule('id-valid','id',scalar(),{op:'lt',left:lit('String',''),right:at('id')});
  rule('amount-valid','amount',scalar('UInt64'),{op:'eq',left:at('amount'),right:at('amount')});
  const money=[prop('money','amount',scalar('UInt64'))];
  node('money','Value Object',{fields:['amount'],invariant_refs:['alpha:amount-valid'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-MONEY',properties:money}});
  const order=[prop('order','id',scalar(),true),prop('order','amount',scalar('UInt64')),prop('order','money',named('money')),prop('order','mode',named('mode'))];
  node('order','Entity',{fields:order.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties:order}});
  node('find','Query',{reads:['alpha:order'],typed_contract:{schema_version:'domainspec.typed-query/v1',ontology_query:'FIXTURE-FIND',source:'alpha:order',inputs:[],filter:null,projection:['id','amount'],order_by:null,limit:null}});
  edge('find-reads-order','reads','find','order');
  node('adjust','Mapping',{target:'alpha:order',typed_contract:{schema_version:'domainspec.typed-mapping/v2',ontology_mapping:'FIXTURE-ADJUST',inputs:[{name:'total',type:scalar('UInt64')}],target:'alpha:order',fields:[{target:'amount',value:at('total'),default:null}],total:false}});
  edge('adjust-maps-order','maps','adjust','order');
  node('posted','Event',{event_type:'posted',version:'1',occurrence_id:{field_id:'event-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[]});
  node('post','Operation',{reads:[],writes:[],effects:['notice'],guard:'allowed',failure_continuation:'return-error'});
  node('legacy-total','Calculation',{inputs:['amount'],typed_contract:{schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'FIXTURE-LEGACY-TOTAL',inputs:[{name:'amount',type:scalar('UInt64')}],result:scalar('UInt64'),division_rounding:'reject',expression:{op:'input',name:'amount'}}});
  edge('legacy-calculates-post','calculates','legacy-total','post');
  node('answer','Enum',{values:['None','Amount'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-ANSWER',variants:[{name:'None',ontology_variant:'FIXTURE-ANSWER#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-ANSWER#Amount',payload:scalar('UInt64')}]}});
  edge('post-guard','enforces','allowed','post');edge('post-event','produces','post','posted');
  node('choose','Policy',{typed_contract:{schema_version:'domainspec.typed-policy/v2',ontology_policy:'FIXTURE-CHOOSE',inputs:[{name:'value',type:scalar('Bool')}],cases:[{target:'alpha:post',rule:{selector:'alpha:allowed',arguments:[{parameter:'value',value:at('value')}]}}],default_target:'alpha:total'}});
  edge('choose-post','applies','choose','post');edge('choose-total','applies','choose','total');
  node('lifecycle','State Machine',{typed_contract:{schema_version:'domainspec.typed-state-machine/v1',ontology_state_machine:'FIXTURE-LIFECYCLE',inputs:[{name:'value',type:scalar('Bool')}],states:['draft','posted'],initial:'draft',transitions:[{transition_id:'post',source_state:'draft',target_state:'posted',trigger_event_ref:'alpha:posted',guard:{selector:'alpha:allowed',arguments:[{parameter:'value',value:at('value')}]},output_intents:[]}]}});
  edge('posted-transitions','transitions','posted','lifecycle');
  node('flow','Workflow',{typed_contract:{schema_version:WORKFLOW_OCCURRENCES_VERSION,ontology_workflow:'FIXTURE-FLOW',steps:[{step_id:'post',operation_ref:'alpha:post'}],compensations:[]}});
  edge('flow-post','orchestrates','flow','post');
  node('api','Interface',{typed_contract:{schema_version:'domainspec.typed-interface/v1',ontology_interface:'FIXTURE-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'response',ontology_contract:'FIXTURE-RESPONSE',fields:[{name:'id',ontology_field:'FIXTURE-RESPONSE#id',meaning:'identity',type:scalar()},{name:'total',ontology_field:'FIXTURE-RESPONSE#total',meaning:'computed total',type:scalar('UInt64')}]}],operations:[{operation_id:'find',operation_ref:'alpha:find',request:scalar(),result:{kind:'contract',contract_id:'response'}}]}});
  edge('api-find','exposes','api','find');
  node('summary','Mapping',{target:'alpha:api',typed_contract:{schema_version:'domainspec.typed-mapping/v3',ontology_mapping:'FIXTURE-SUMMARY',inputs:[{name:'order',type:named('order'),use:null},{name:'total',type:scalar('UInt64'),use:null}],target:{kind:'contract',interface_selector:'alpha:api',contract_id:'response'},target_use:{interface_selector:'alpha:api',operation_id:'find',side:'result'},fields:[{target:'id',value:at('order','FIXTURE-ORDER#id'),default:null},{target:'total',value:at('total'),default:null}],total:true}});
  edge('summary-api','maps','summary','api');f.write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(f.source),certificate=createCompiledProjectCertificate(graph);
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},bytes('development/reconciliation-v1/contracts/composition-boundary.json'));
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['alpha:order'],bindings:[]},ruleSources.field_contract);
  const sumFields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['alpha:answer'],bindings:[]},ruleSources.field_contract);
  const inputs=[{name:'order',type:named('order')}];
  const action=compileOperationActionBindings(graph,boundary,fields,{schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'alpha:post',inputs,reads:[],writes:[],guards:[{selector:'alpha:allowed',arguments:[{parameter:'value',value:lit('Bool',true)}]}],events:[{slot:'notice',target:'alpha:posted',parameter:'notice_input'}],result:{type:named('order'),value:at('order')},atomicity:'state-and-outbox',continuation:'awaited-settlement'},bytes(base+'operation-action-contract.json'));
  const workflow=compileWorkflowBindings(graph,boundary,fields,[action],{schema_version:WORKFLOW_BINDINGS_VERSION,selector:'alpha:flow',inputs,event_inputs:[{name:'notice',event_ref:'alpha:posted'}],steps:[{step_id:'post',action_sha256:action.action_sha256,arguments:[{parameter:'order',value:{op:'input',name:'order',properties:[]}}],events:[{parameter:'notice_input',input:'notice'}]}],compensations:[],result:{type:named('order'),value:{op:'step-result',step_id:'post',properties:[]}}},bytes(base+'workflow-binding-contract.json'));
  const policy=selectWorkflowRecoveryPolicy(workflow,{schema_version:WORKFLOW_RECOVERY_POLICY_VERSION,workflow_sha256:workflow.workflow_sha256,contract_sha256:WORKFLOW_RECOVERY_CONTRACT_SHA256,dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'},bytes(base+'workflow-recovery-policy-contract.json'));
  const factories=[{selector:'alpha:order',base_validators:[{rule:'alpha:id-valid',arguments:[{parameter:'id',field:'id'}]}],extensions:[]},{selector:'alpha:money',base_validators:[{rule:'alpha:amount-valid',arguments:[{parameter:'amount',field:'amount'}]}],extensions:[]}];
  const eventSources={...common,event_contract:bytes(base+'event-generation-contract.json')};
  const operationSources={operation_contract:bytes(base+'operation-generation-contract.json'),factory_contract:bytes(base+'factory-structured-rule-contract.json'),enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts'),rules:ruleSources,events:eventSources};
  const layout={language:'typescript',module_root:'application'},exact={...layout,value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256};
  const request=(kind:string,selection:any,sources:any,data:any=fields)=>({kind,fields:data,selection,sources});
  const requests:any[]=[
    request('calculations-v2',{...f.requests[0].selection,boundary_sha256:boundary.boundary_sha256},calculationSources,null),
    request('calculations-v1',{...f.requests[0].selection,schema_version:'domainspec.configured-calculations-selection/v1-candidate',boundary_sha256:boundary.boundary_sha256,roots:['alpha:legacy-total']},{...common,calculation_contract:bytes(base+'calculation-generation-contract.json')},null),
    request('algebraic-enums',{schema_version:'domainspec.configured-algebraic-enums-selection/v1-candidate',...layout,field_compilation_sha256:sumFields.compilation_sha256,factories:[]},{standalone_contract:bytes(base+'standalone-sum-contract.json'),factories:{...ruleSources,factory_contract:operationSources.factory_contract,enum_provider:operationSources.enum_provider}},sumFields),
    request('rules',{...f.requests[1].selection,roots:['alpha:allowed','alpha:id-valid','alpha:amount-valid','beta:allowed']},ruleSources,null),
    request('factories',{schema_version:'domainspec.configured-factories-selection/v12-candidate',...layout,field_compilation_sha256:fields.compilation_sha256,rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE},factories},{...ruleSources,factory_contract:operationSources.factory_contract,enum_provider:operationSources.enum_provider}),
    request('queries',{schema_version:'domainspec.configured-queries-selection/v1-candidate',...exact,roots:['alpha:find']},{...common,query_contract:bytes(base+'query-generation-contract.json')}),
    request('mappings',{schema_version:'domainspec.configured-mappings-selection/v1-candidate',...exact,roots:['alpha:adjust']},{...common,mapping_contract:bytes(base+'mapping-generation-contract.json')}),
    request('policies',{schema_version:'domainspec.configured-policies-selection/v1-candidate',...exact,rule_selection:STRUCTURED_RULE_VERSION,roots:['alpha:choose']},{policy_contract:bytes(base+'policy-generation-contract.json'),rules:ruleSources}),
    request('events',{schema_version:'domainspec.configured-events-selection/v1-candidate',...layout,value_profile:'domainspec.event-values/v1-candidate',boundary_sha256:boundary.boundary_sha256,roots:['alpha:posted']},eventSources,null),
    request('operations',{schema_version:'domainspec.configured-operations-selection/v1-candidate',...layout,actions:[action],factories},operationSources),
    request('workflows',{schema_version:'domainspec.configured-workflow-selection/v1-candidate',...layout,workflow,policy,actions:[action],factories},{workflow_contract:bytes(base+'workflow-generation-contract.json'),materialization_contract:bytes(base+'workflow-materialization-contract.json'),outcome_contract:bytes(base+'workflow-outcome-contract.json'),recovery_contract:bytes(base+'workflow-recovery-policy-contract.json'),operations:operationSources}),
    request('state-machines',{schema_version:'domainspec.configured-state-machines-selection/v1-candidate',...layout,roots:['alpha:lifecycle'],boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256},{state_machine_contract:bytes(base+'state-machine-contract.json'),rules:ruleSources}),
    request('public-boundaries',{schema_version:'domainspec.configured-public-boundaries-selection/v1-candidate',...layout,value_profile:EXACT_UINT64_PROFILE,roots:['alpha:summary','alpha:api']},{...common,generation_contract:bytes(base+'public-boundary-generation-contract.json'),public_mapping_contract:bytes(base+'public-mapping-contract.json'),interface_contract:bytes(base+'named-interface-contract.json')}),
  ];
  const selection:any={...f.selection,graph_sha256:certificate.graph_sha256,boundary_sha256:boundary.boundary_sha256,requests};
  return {...f,graph,boundary,fields,requests,selection,plan:()=>planResolvedArtifacts(graph,boundary,selection,definition)};
}

function nativeJoined(root:string,p:ReturnType<typeof planResolvedArtifacts>) {
  fs.mkdirSync(root,{recursive:true});
  for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
  const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:[path.join(project,'impl'),...process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))]}),deps=path.dirname(path.dirname(path.dirname(types)));
  const image=nativeToolchainImage();
  const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--mount','type=bind,source='+deps+',target='+deps+',readonly','--workdir',root,image];
  const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...p.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});
  try {compile();} catch(e:any) {throw Error(String(e.stdout)+String(e.stderr));}
  const load=(suffix:string)=>{const a=p.artifacts.find(a=>a.relative_path.endsWith(suffix))!;assert.ok(a,suffix);return require(path.join(root,'js',a.relative_path.replace(/\.ts$/,'.js')));};
  return {root,load,docker,compile};
}


import {RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE,decodeReconciledCompilationSelection,planCompiledReconciledProject,planReconciledProject,selectReconciledArtifacts,assertReconciledProjectPlan} from '../../src/index.ts';
import {planCompiledComposedReconciledProject,planComposedReconciledProject,decodeComposedReconciledCompilationSelection} from '../../src/index.ts';
import {assertSelectedReconciledProject,selectSelectedReconciledArtifacts,selectedReconciledIdentity} from '../../src/generation/selected-reconciled-project.ts';
function authored(f:ReturnType<typeof allTypesFixture>):any{
 const action=f.requests.find(r=>r.kind==='operations')!.selection;
 const w=f.requests.find(r=>r.kind==='workflows')!.selection.workflow.bindings;
 const strip=(call:any)=>{const {action_sha256,...rest}=call;return rest;};
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:action.factories,operations:action.actions.map((a:any)=>a.bindings),workflows:[{selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:w.steps.map(strip),compensations:w.compensations.map(strip),result:w.result,recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
}
test('public source and checked-snapshot APIs compile all thirteen metatypes from authored JSON',t=>{
 const f=allTypesFixture(t),input=JSON.parse(JSON.stringify(authored(f))),before=canonicalJson(input);
 assert.equal(JSON.stringify(input).includes('action_sha256'),false);
 const p=planCompiledReconciledProject(f.graph,input);assertReconciledProjectPlan(p);
 assertSelectedReconciledProject(p);
 assert.deepEqual(selectSelectedReconciledArtifacts(p),selectReconciledArtifacts(p));
 assert.deepEqual(planReconciledProject(f.source,input),p);
 assert.equal(new Set(p.resolved.modules.flatMap(m=>m.metatypes)).size,13);
 assert.equal(p.checking_scope,'whole-project');assert.equal(canonicalJson(input),before);assert.equal(Object.isFrozen(input),false);
 for(const selector of p.node_selectors)assert.ok(p.resolved.modules.some(m=>m.qualified_selectors.includes(selector)),selector);
 fs.renameSync(f.source,path.join(f.temp,'source-gone'));assert.deepEqual(planCompiledReconciledProject(f.graph,input),p);
 assert.throws(()=>planCompiledReconciledProject(structuredClone(f.graph),input));
 assert.throws(()=>selectReconciledArtifacts(structuredClone(p),['alpha:flow']),/registered reconciled/);
});
test('explicit composed project retains all thirteen metatypes without weakening the v1 decoder',t=>{
 const f=allTypesFixture(t),old=authored(f);
 const selection={...old,schema_version:'domainspec.reconciled-compilation/v2-candidate',profile_id:'domainspec.reconciled-typescript/v2-candidate',
  value_compositions:old.operations.map((a:any)=>({composition:{schema_version:'domainspec.operation-value-composition/v1-candidate',operation_ref:a.selector,bindings:[]},absence_failures:[]}))};
 assert.throws(()=>decodeReconciledCompilationSelection(selection));assert.throws(()=>decodeComposedReconciledCompilationSelection(old));
 const plan=planCompiledComposedReconciledProject(f.graph,selection);
 assertReconciledProjectPlan(plan);
 for(const legacy of [assertSelectedReconciledProject,selectSelectedReconciledArtifacts,selectedReconciledIdentity]){
  assert.throws(()=>legacy(plan as never),/explicit composed project API/);
 }
 assert.deepEqual(planComposedReconciledProject(f.source,selection),plan);
 assert.equal(new Set(plan.resolved.modules.flatMap(m=>m.metatypes)).size,13);
 for(const node of f.graph.nodes)assert.ok(plan.resolved.modules.some(m=>m.qualified_selectors.includes(node.selector)),node.selector);
 assert.deepEqual(selectReconciledArtifacts(plan).artifacts,plan.resolved.artifacts);
 assert.equal(plan.resolved.requests.some(r=>r.kind==='composed-operations'),true);
 assert.equal(plan.resolved.requests.some(r=>r.kind==='composed-workflows'),true);
 assert.equal(plan.resolved.requests.some(r=>r.kind==='operations'||r.kind==='workflows'),false);
 nativeJoined(path.join(f.temp,'composed-all-types'),plan.resolved);
});
test('each qualified node view is exactly its independent native import closure and preserves bytes',t=>{
 const f=allTypesFixture(t),p=planCompiledReconciledProject(f.graph,authored(f));
 for(const selector of p.node_selectors){
  const view=selectReconciledArtifacts(p,[selector]),byPath=new Map(p.resolved.modules.map(m=>[m.relative_path,m]));
  const visited=new Set<string>(),queue=p.resolved.modules.filter(m=>m.qualified_selectors.includes(selector)).map(m=>m.relative_path);
  while(queue.length){const file=queue.shift()!;if(visited.has(file))continue;visited.add(file);for(const i of byPath.get(file)!.imports)if(i.target_path)queue.push(i.target_path);}
  assert.deepEqual(view.artifacts.map(a=>a.relative_path).sort(),[...visited].sort());
  for(const a of view.artifacts)assert.equal(a,p.resolved.artifacts.find(x=>x.relative_path===a.relative_path));
 }
 const policy=selectReconciledArtifacts(p,['alpha:choose']);
 assert.ok(policy.artifacts.every(a=>!a.relative_path.includes('/operations/')&&!a.relative_path.includes('/calculations/')));
 const machine=selectReconciledArtifacts(p,['alpha:lifecycle']);assert.ok(machine.artifacts.every(a=>!a.relative_path.includes('/events/')));
 assert.deepEqual(selectReconciledArtifacts(p).artifacts,p.resolved.artifacts);
 assert.deepEqual(selectReconciledArtifacts(p,['alpha:total','beta:total']),selectReconciledArtifacts(p,['beta:total','alpha:total']));
 for(const roots of [[],['total'],['missing:node'],['alpha:flow','alpha:flow']])assert.throws(()=>selectReconciledArtifacts(p,roots),/unique existing qualified/);
});
test('public authored compiler generates runnable compound code and isolated selected views',async t=>{
 const f=allTypesFixture(t),p=planCompiledReconciledProject(f.graph,authored(f));
 for(const folder of ['first','second']){
  const n=nativeJoined(path.join(f.temp,folder),p.resolved);
  const total=n.load('/alpha/src/domain/calculations/total.ts').calculateTotal({});
  const plain={id:'order-one',amount:'4',money:{amount:'4'},mode:{variant:'On'}};
  assert.equal(total,18446744073709551615n);assert.equal(n.load('/beta/src/domain/calculations/total.ts').calculateTotal({}),7n);
  assert.deepEqual(n.load('/mappings/summary.ts').mappingSummary({order:plain,total}),{id:'order-one',total});
  assert.deepEqual(n.load('/queries/find.ts').queryFind([plain,plain],{}),[{id:'order-one',amount:4n},{id:'order-one',amount:4n}]);
  assert.equal(n.load('/policies/choose.ts').policyChoose({value:true}),'alpha:post');
  assert.equal(n.load('/state-machines/lifecycle.ts').transitionLifecycle('draft','alpha:posted',{value:true}).state,'posted');
  const calls:any[]=[];
  const dependencies={store:{begin:async()=>({read:async()=>{throw Error('no reads');},rollback:async()=>{},commit:async(batch:any)=>{calls.push(batch);return {status:'committed'};}})}};
  const out=await n.load('/workflows/flow.ts').workflowFlow({order:plain,notice:{occurrence:{'event-id':'event-one'},occurredAt:'2026-09-09',payload:{}}},{workflow_execution_id:'run-one',failure_occurrence_id:'failure-one'},{'alpha:post':dependencies});
  assert.equal(out.status,'succeeded');assert.equal(out.value.id,'order-one');assert.equal(calls.length,1);
 }
 const view=selectReconciledArtifacts(p,['alpha:flow']),n=nativeJoined(path.join(f.temp,'selected'),{...p.resolved,artifacts:view.artifacts});
 assert.equal(typeof n.load('/workflows/flow.ts').workflowFlow,'function');
 assert.ok(view.artifacts.length<p.resolved.artifacts.length);
});
test('selection rejects unknown combinations, digest injection, incomplete bindings and active inputs',t=>{
 const f=allTypesFixture(t),input=authored(f);
 for(const [key,value] of [['schema_version','unknown'],['profile_id','unknown'],['language','python'],['layout_version','domainspec.application-layout/v1'],['value_profile','unknown'],['module_root','../escape'],['sources',{}],['graph_sha256','0'.repeat(64)]] as readonly (readonly [string,unknown])[]){
  assert.throws(()=>planCompiledReconciledProject(f.graph,{...input,[key]:value}),/DS_RECONCILED_COMPILATION/);
 }
 for(const key of ['factories','operations','workflows'])assert.throws(()=>planCompiledReconciledProject(f.graph,{...input,[key]:[]}),/exact qualified binding coverage/);
 for(const factories of [[null],[{selector:'alpha:order',base_validators:[],extensions:[],provider:()=>{throw Error('must not run');}}]])assert.throws(()=>planCompiledReconciledProject(f.graph,{...input,factories}));
 const injected=structuredClone(input);injected.workflows[0].steps[0].action_sha256='0'.repeat(64);
 assert.throws(()=>planCompiledReconciledProject(f.graph,injected),/unknown or missing fields/);
 const wrong=structuredClone(input);wrong.workflows[0].steps[0].step_id='another-step';assert.throws(()=>planCompiledReconciledProject(f.graph,wrong),/unknown source occurrence/);
 let touched=0;const active={...input};Object.defineProperty(active,'operations',{enumerable:true,get(){touched++;return input.operations;}});
 assert.throws(()=>decodeReconciledCompilationSelection(active),/inert data/);assert.equal(touched,0);
});
test('explicit profile does not add a record to an Enum and scalar-only project',t=>{
 const f=fixture(t),selection={schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:[],operations:[],workflows:[]};
 const p=planCompiledReconciledProject(f.graph,selection);
 assert.ok(p.resolved.artifacts.every(a=>!a.relative_path.includes('/entities/')&&!a.relative_path.includes('/value-objects/')));
 assert.equal(new Set(p.resolved.modules.flatMap(m=>m.metatypes)).size,3);
 for(const feature of ['alpha','beta']){
  f.write('specs/'+feature+'/feature.json',{schema_version:'domainspec.feature/v1',feature_id:feature,nodes:['total','allowed'],edges:[]});
  fs.unlinkSync(path.join(f.source,'specs/'+feature+'/nodes/mode.json'));
 }
 const withoutData=planReconciledProject(f.source,selection);
 assert.equal(new Set(withoutData.resolved.modules.flatMap(m=>m.metatypes)).size,2);
 assert.ok(withoutData.resolved.artifacts.every(a=>!a.relative_path.includes('/enums/')));
});

test('authored source ordering preserves thirteen-type surfaces and runnable domain behavior',async t=>{
 const f=allTypesFixture(t),input=authored(f),before=planReconciledProject(f.source,input);
 const projectFile=JSON.parse(fs.readFileSync(path.join(f.source,'project.json'),'utf8'));
 projectFile.features.reverse();projectFile.cross_feature_edges.reverse();f.write('project.json',projectFile);
 for(const feature of projectFile.features){
  const relative='specs/'+feature+'/feature.json',file=JSON.parse(fs.readFileSync(path.join(f.source,relative),'utf8'));
  file.nodes.reverse();file.edges.reverse();f.write(relative,file);
 }
 const after=planReconciledProject(f.source,input);
 assert.equal(new Set(after.resolved.modules.flatMap(m=>m.metatypes)).size,13);
 assert.deepEqual(after.node_selectors,before.node_selectors);
 const surfaces=(p:typeof before)=>p.resolved.modules.map(m=>({path:m.relative_path,imports:m.imports.map(({target_sha256,...i})=>{
  assert.equal(target_sha256,i.target_path===null?null:p.resolved.artifacts.find(a=>a.relative_path===i.target_path)!.sha256);
  return i;
 }),exports:m.exports,selectors:m.qualified_selectors}));
 assert.deepEqual(surfaces(after),surfaces(before));
 // Changed source bytes may change provenance digests; those are not domain semantics.
 await observeRelocatedDomain(nativeJoined(path.join(f.temp,'order-before'),before.resolved));
 await observeRelocatedDomain(nativeJoined(path.join(f.temp,'order-after'),after.resolved));
});

test('module-root relocation preserves thirteen-type surfaces and runnable domain behavior',async t=>{
 const f=allTypesFixture(t),input=authored(f),before=planCompiledReconciledProject(f.graph,input);
 const moduleRoot='relocated/kernel',after=planCompiledReconciledProject(f.graph,{...input,module_root:moduleRoot});
 const relative=(p:typeof before,root:string)=>p.resolved.modules.map(m=>{
  assert.ok(m.relative_path.startsWith(root+'/'));
  return {path:m.relative_path.slice(root.length+1),exports:m.exports,selectors:m.qualified_selectors,
   imports:m.imports.map(({target_sha256,...i})=>{
    assert.equal(target_sha256,i.target_path===null?null:p.resolved.artifacts.find(a=>a.relative_path===i.target_path)!.sha256);
    return {...i,target_path:i.target_path?.slice(root.length+1)??null};
   })};
 });
 assert.deepEqual(relative(after,moduleRoot),relative(before,input.module_root));
 assert.deepEqual(after.node_selectors,before.node_selectors);
 assert.equal(new Set(after.resolved.modules.flatMap(m=>m.metatypes)).size,13);
 await observeRelocatedDomain(nativeJoined(path.join(f.temp,'root-before'),before.resolved));
 await observeRelocatedDomain(nativeJoined(path.join(f.temp,'root-after'),after.resolved));
});

async function observeRelocatedDomain(n:ReturnType<typeof nativeJoined>){
 const total=n.load('/alpha/src/domain/calculations/total.ts').calculateTotal({});
 assert.equal(total,18446744073709551615n);
 const order={id:'order-one',amount:'4',money:{amount:'4'},mode:{variant:'On'}};
 assert.deepEqual(n.load('/mappings/summary.ts').mappingSummary({order,total}),{id:'order-one',total});
 assert.deepEqual(n.load('/queries/find.ts').queryFind([order,order],{}),[{id:'order-one',amount:4n},{id:'order-one',amount:4n}]);
 assert.equal(n.load('/policies/choose.ts').policyChoose({value:true}),'alpha:post');
 assert.equal(n.load('/policies/choose.ts').policyChoose({value:false}),'alpha:total');
 assert.equal(n.load('/state-machines/lifecycle.ts').transitionLifecycle('draft','alpha:posted',{value:true}).state,'posted');
 const batches:any[]=[];
 const dependencies={store:{begin:async()=>({read:async()=>{throw Error('no reads');},rollback:async()=>{},commit:async(batch:any)=>{batches.push(batch);return {status:'committed'};}})}};
 const out=await n.load('/workflows/flow.ts').workflowFlow({order,notice:{occurrence:{'event-id':'event-one'},occurredAt:'2026-09-09',payload:{}}},{workflow_execution_id:'run-one',failure_occurrence_id:'failure-one'},{'alpha:post':dependencies});
 assert.equal(out.status,'succeeded');assert.equal(out.value.id,'order-one');assert.equal(batches.length,1);
}

test('public thirteen-type selection rejects portable aliases and reserved or escaping roots without writes',t=>{
 const f=allTypesFixture(t),input=authored(f),before=fs.readdirSync(f.temp);
 for(const module_root of ['con','aux','lpt9','package/class','../escape','a/../b','/absolute','a\\b','Application','caf\u00e9','cafe\u0301']){
  assert.throws(()=>planReconciledProject(f.source,{...input,module_root}),module_root);
  assert.deepEqual(fs.readdirSync(f.temp),before,module_root);
 }
});

test('distinct qualified typed references cannot collapse to one generated type identifier',t=>{
 const f=allTypesFixture(t);
 const manifest=JSON.parse(fs.readFileSync(path.join(f.source,'project.json'),'utf8'));
 manifest.features.push('alpha-a');f.write('project.json',manifest);
 const feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/feature.json'),'utf8'));
 feature.nodes.push('a-b');f.write('specs/alpha/feature.json',feature);
 f.write('specs/alpha-a/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha-a',nodes:['b'],edges:[]});
 for(const [feature_id,node_id] of [['alpha','a-b'],['alpha-a','b']])
  f.write('specs/'+feature_id+'/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id,node_id,kind:'Enum',body:{description:'collision fixture',values:['On','Off']}});
 const order=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/nodes/order.json'),'utf8'));
 for(const [name,selector] of [['left','alpha:a-b'],['right','alpha-a:b']]){
  order.body.fields.push(name);
  order.body.typed_contract.properties.push({name,type:{kind:'named',selector},identity:false,cardinality:'one',meaning:name,ontology_property:'FIXTURE-ORDER#'+name});
 }
 f.write('specs/alpha/nodes/order.json',order);
 assert.throws(()=>planReconciledProject(f.source,authored(f)),(error:any)=>error.code==='MTCLI_TYPE_IDENTIFIER_COLLISION');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
