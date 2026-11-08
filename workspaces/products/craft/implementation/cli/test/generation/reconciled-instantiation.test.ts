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

import {planInstantiation,planProjectInstantiation,publishInstantiation,publishProjectInstantiation,planReconciledProject,planCompiledReconciledProject,selectReconciledArtifacts,createReconciledOutputReceipt,verifyReconciledProject,planProjectBuild,runCli,loadProjectNode,RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE} from '../../src/index.ts';
import {RECONCILED_INSTANTIATION_API_DEFINITION_SHA256} from '../../src/generation/reconciled-instantiation.ts';
function authored(f:ReturnType<typeof allTypesFixture>):any{
 const action=f.requests.find(r=>r.kind==='operations')!.selection;
 const w=f.requests.find(r=>r.kind==='workflows')!.selection.workflow.bindings;
 const strip=(call:any)=>{const {action_sha256,...rest}=call;return rest;};
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:action.factories,operations:action.actions.map((a:any)=>a.bindings),workflows:[{selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:w.steps.map(strip),compensations:w.compensations.map(strip),result:w.result,recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
}
test('every qualified node API uses exactly the checked native import view without source reload',t=>{
 const f=allTypesFixture(t),projectPlan=planCompiledReconciledProject(f.graph,authored(f));
 assert.equal(sha256(bytes(base+'reconciled-instantiation-api-contract.json')),RECONCILED_INSTANTIATION_API_DEFINITION_SHA256);
 assert.equal(new Set(f.graph.nodes.map(n=>n.kind)).size,13);
 const plans=projectPlan.node_selectors.map(selector=>{
  const read=fs.readFileSync;(fs as any).readFileSync=()=>{throw Error('unexpected source reload');};
  try{return planInstantiation(selector,'typescript',null,undefined,projectPlan);}finally{fs.readFileSync=read;}
 });
 for(const [i,p]of plans.entries()){
  const selector=projectPlan.node_selectors[i]!,view=selectReconciledArtifacts(projectPlan,[selector]);
  assert.equal(p.instantiation_scope,'node');assert.deepEqual(p.artifacts,view.artifacts);
  assert.deepEqual(p.receipt,createReconciledOutputReceipt(projectPlan,[selector]));
  assert.equal(p.receipt.checking_scope,'whole-project');assert.ok(Object.isFrozen(p)&&Object.isFrozen(p.artifacts));
  const out=path.join(f.temp,'node-'+i),publication=publishInstantiation(p,out);
  assert.deepEqual(publication.receipt,p.receipt);assert.equal(verifyReconciledProject(projectPlan,out,[selector]).result,'pass');
  for(const a of p.artifacts)assert.equal(fs.readFileSync(path.join(out,a.relative_path),'utf8'),a.content);
 }
 fs.renameSync(f.source,path.join(f.temp,'relocated'));
 assert.deepEqual(planInstantiation('alpha:flow','typescript',null,EXACT_UINT64_PROFILE,projectPlan),plans[projectPlan.node_selectors.indexOf('alpha:flow')]);
});
test('project instantiation shares exact compiler/build output and preserves source currentness',t=>{
 const f=allTypesFixture(t),selection=authored(f),direct=planReconciledProject(f.source,selection);
 const p=planProjectInstantiation(f.source,['typescript'],selection),build=planProjectBuild(f.source,'typescript',undefined,undefined,selection);
 assert.equal(p.instantiation_scope,'project');assert.deepEqual(p.project,direct);assert.deepEqual(p.artifacts,build.artifacts);assert.deepEqual(p.receipt,build.receipt);
 assert.deepEqual(planProjectInstantiation(f.source,['typescript','typescript'],selection),p);
 const out=path.join(f.temp,'project-out');assert.deepEqual(publishProjectInstantiation(p,out).receipt,p.receipt);
 assert.equal(verifyReconciledProject(direct,out).result,'pass');
 const file=path.join(f.source,'project.json'),original=fs.readFileSync(file,'utf8'),read=fs.readFileSync;let changed=false;
 (fs as any).readFileSync=(name:any,...args:any[])=>{const result=(read as any)(name,...args);if(!changed&&String(name)===file){changed=true;fs.writeFileSync(file,original+' ');}return result;};
 try{assert.throws(()=>planProjectInstantiation(f.source,['typescript'],selection),/changed|drift/i);}finally{fs.readFileSync=read;fs.writeFileSync(file,original);}
 assert.equal(changed,true);
});
test('missing contexts, malformed selectors, mismatched scopes and forged plans reject before output',t=>{
 const f=allTypesFixture(t),selection=authored(f),projectPlan=planCompiledReconciledProject(f.graph,selection),target=path.join(f.temp,'never');
 for(const value of [null,{},structuredClone(projectPlan)])assert.throws(()=>planInstantiation('alpha:flow','typescript',null,undefined,value as any),/registered reconciled/);
 for(const selector of ['', 'flow','alpha:missing', {feature_id:'alpha',node_id:'flow'}])assert.throws(()=>planInstantiation(selector as any,'typescript',null,undefined,projectPlan),/qualified/);
 assert.throws(()=>planInstantiation('alpha:flow' as any,'typescript'),/checked project/);
 assert.throws(()=>planInstantiation('alpha:flow','python',null,undefined,projectPlan),/conflicts/);
 assert.throws(()=>planInstantiation('alpha:flow','typescript',null,'unknown' as any,projectPlan),/conflicts/);
 assert.throws(()=>planInstantiation('alpha:flow','typescript',{} as any,undefined,projectPlan),/overlay/);
 for(const langs of [[],['python'],['typescript','rust'],null])assert.throws(()=>planProjectInstantiation(path.join(f.temp,'missing'),langs as any,selection),/single selected language|inert/);
 for(const value of [null,{}, {...selection,profile_id:'unknown'}])assert.throws(()=>planProjectInstantiation(path.join(f.temp,'missing'),['typescript'],value as any),/DS_RECONCILED/);
 const node=planInstantiation('alpha:flow','typescript',null,undefined,projectPlan),whole=planProjectInstantiation(f.source,['typescript'],selection);
 for(const [value,publish,legacySchema]of [[node,publishInstantiation,'domainspec.instantiation-plan/v1'],[whole,publishProjectInstantiation,'domainspec.project-instantiation-plan/v1']] as const){
  for(const forged of [structuredClone(value),{...value},{...value,artifacts:[]},{...value,schema_version:legacySchema}]){assert.throws(()=>(publish as any)(forged,target),/registered.*instantiation/);assert.equal(fs.existsSync(target),false);}
 }
 assert.throws(()=>publishProjectInstantiation(node as any,target),/scope/);
 assert.throws(()=>publishInstantiation(whole as any,target),/scope/);assert.equal(fs.existsSync(target),false);
 const owner=path.join(f.temp,'owner');fs.mkdirSync(owner);fs.writeFileSync(path.join(owner,'keep'),'owner');
 assert.throws(()=>publishProjectInstantiation(whole,owner),/already exists/);assert.equal(fs.readFileSync(path.join(owner,'keep'),'utf8'),'owner');
});
test('selected CLI instantiate commands publish the exact public API receipts',t=>{
 const f=allTypesFixture(t),selection=authored(f),file=path.join(f.temp,'selection.json');fs.writeFileSync(file,JSON.stringify(selection));
 const original=canonicalJson(loadCompiledProjectGraph(f.source)),projectPlan=planReconciledProject(f.source,selection);
 for(const command of ['instantiate','instantiate-project']){
  const out=path.join(f.temp,'cli-'+command),stdout:string[]=[],stderr:string[]=[];
  const flags=command==='instantiate'?['--node','alpha:flow','--language','typescript']:['--languages','typescript'];
  assert.equal(runCli([command,f.source,...flags,'--target-root',out,'--compilation-selection',file],{stdout:s=>stdout.push(s),stderr:s=>stderr.push(s)}),0,stderr.join(''));
  const expected=command==='instantiate'?planInstantiation('alpha:flow','typescript',null,undefined,projectPlan):planProjectInstantiation(f.source,['typescript'],selection);
  assert.deepEqual(JSON.parse(stdout.join('')).receipt,expected.receipt);
 }
 assert.equal(canonicalJson(loadCompiledProjectGraph(f.source)),original);
});
test('legacy decoded-node and multi-language project calls retain their plans and publication receipts',t=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-instantiation-legacy-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source');fs.cpSync(path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project'),source,{recursive:true});
 const node=loadProjectNode(source,'alpha:settle');
 for(const language of ['typescript','python','rust'] as const){
  const old=planInstantiation(node,language);assert.equal(old.schema_version,'domainspec.instantiation-plan/v1');
  assert.deepEqual(planInstantiation(node,language,null,undefined,undefined),old);
  const publication=publishInstantiation(old,path.join(temp,language));assert.equal(publication.receipt.schema_version,'domainspec.instantiation-receipt/v1');
 }
 const p=planProjectInstantiation(source,['typescript','python','rust']);assert.equal(p.schema_version,'domainspec.project-instantiation-plan/v1');
 assert.deepEqual(planProjectInstantiation(source,['rust','typescript','python'],undefined),p);
 const out=publishProjectInstantiation(p,path.join(temp,'whole'));assert.equal(out.receipt.schema_version,'domainspec.project-publication-receipt/v1');
 assert.equal(out.receipt.plan_count,p.plan_count);
});

test('native declarations distinguish scopes and relocated APIs publish node and project views',t=>{
 const f=allTypesFixture(t),selection=authored(f),cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,image];
 const compile=(args:string[])=>{try{return execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext',...args],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));compile(['--declaration','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')]);
 const consumer=path.join(f.temp,'consumer.ts');
 fs.writeFileSync(consumer,`import {planInstantiation,planProjectInstantiation,publishInstantiation,publishProjectInstantiation,type DecodedProjectNode,type ReconciledProjectPlan,type ReconciledCompilationSelection,type ReconciledNodeInstantiationPlan,type ReconciledProjectInstantiationPlan,type ReconciledInstantiationPublication,type ProjectInstantiationPlanV1,type PublicationResult,type ProjectPublicationResult} from './dist/index.js';
 export function signatures(source:string,target:string,decoded:DecodedProjectNode,project:ReconciledProjectPlan,selection:ReconciledCompilationSelection,optional:ReconciledCompilationSelection|undefined){
  const old=planInstantiation(decoded,'typescript');
  const oldSchema:'domainspec.instantiation-plan/v1'=old.schema_version;
  const absent:typeof old=planInstantiation(decoded,'typescript',null,undefined,undefined);
  const oldPublished:PublicationResult=publishInstantiation(old,target);
  const node:ReconciledNodeInstantiationPlan=planInstantiation('alpha:flow','typescript',null,undefined,project);
  const nodePublished:ReconciledInstantiationPublication=publishInstantiation(node,target);
  const whole:ReconciledProjectInstantiationPlan=planProjectInstantiation(source,['typescript'],selection);
  const wholePublished:ReconciledInstantiationPublication=publishProjectInstantiation(whole,target);
  const oldProject:ProjectInstantiationPlanV1=planProjectInstantiation(source,['typescript','python','rust']);
  const oldProjectPublished:ProjectPublicationResult=publishProjectInstantiation(oldProject,target);
  const dynamic:ProjectInstantiationPlanV1|ReconciledProjectInstantiationPlan=planProjectInstantiation(source,['typescript'],optional);
  const dynamicPublished:ProjectPublicationResult|ReconciledInstantiationPublication=publishProjectInstantiation(dynamic,target);
  // @ts-expect-error Node and project publication scopes are not interchangeable.
  publishProjectInstantiation(node,target);
  // @ts-expect-error A project view is not a single-node instantiation.
  publishInstantiation(whole,target);
  // @ts-expect-error A currentness receipt is not a legacy conformance receipt.
  const falseLegacy:PublicationResult=nodePublished;
  return {oldSchema,absent,oldPublished,nodePublished,wholePublished,oldProjectPublished,dynamicPublished};
 }`);
 compile(['--noEmit',consumer]);
 const check=`import assert from 'node:assert/strict';import fs from 'node:fs';
 import {planReconciledProject,planInstantiation,planProjectInstantiation,publishInstantiation,publishProjectInstantiation,verifyReconciledProject} from './dist/index.js';
 assert.throws(()=>fs.readFileSync(${JSON.stringify(path.join(project,base+'reconciled-instantiation-api-contract.json'))}),{code:process.permission?'ERR_ACCESS_DENIED':'ENOENT'});
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(selection)},wholeTarget=${JSON.stringify(path.join(f.temp,'native-whole'))},nodeTarget=${JSON.stringify(path.join(f.temp,'native-node'))};
 const project=planReconciledProject(source,selection),whole=planProjectInstantiation(source,['typescript'],selection);
 if(process.permission){
  const before=fs.readdirSync(${JSON.stringify(f.temp)});
  const node=planInstantiation('alpha:flow','typescript',null,undefined,project);
  assert.equal(verifyReconciledProject(project,wholeTarget).result,'pass');
  assert.equal(verifyReconciledProject(project,nodeTarget,['alpha:flow']).result,'pass');
  assert.throws(()=>publishProjectInstantiation(whole,wholeTarget+'-blocked'),{code:'DS_RECONCILED_OUTPUT_UNAVAILABLE',exitCode:22,pointer:'/target-root'});
  assert.throws(()=>publishInstantiation(node,nodeTarget+'-blocked'),{code:'DS_RECONCILED_OUTPUT_UNAVAILABLE',exitCode:22,pointer:'/target-root'});
  assert.equal(fs.existsSync(wholeTarget+'-blocked'),false);assert.equal(fs.existsSync(nodeTarget+'-blocked'),false);
  assert.deepEqual(fs.readdirSync(${JSON.stringify(f.temp)}),before);
  console.log(JSON.stringify({restricted:'handled',artifacts:node.artifacts}));
 }else{
 const wholeOutput=publishProjectInstantiation(whole,wholeTarget);
 assert.equal(verifyReconciledProject(project,wholeTarget).result,'pass');
 fs.renameSync(source,source+'-moved');
 const node=planInstantiation('alpha:flow','typescript',null,undefined,project),nodeOutput=publishInstantiation(node,nodeTarget);
 assert.equal(verifyReconciledProject(project,nodeTarget,['alpha:flow']).result,'pass');
 assert.equal(node.receipt.formal_verification,'not-performed');
 console.log(JSON.stringify({whole:wholeOutput.receipt,node:nodeOutput.receipt,artifacts:node.artifacts}));}`;
 const expectedProject=planCompiledReconciledProject(f.graph,selection),expectedNode=planInstantiation('alpha:flow','typescript',null,undefined,expectedProject);
 const runtime=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+f.temp,image,'node','--input-type=module','--eval',check];
 const actual=JSON.parse(execFileSync('docker',runtime,{encoding:'utf8'}));
 assert.deepEqual(actual,{whole:createReconciledOutputReceipt(expectedProject),node:expectedNode.receipt,artifacts:expectedNode.artifacts});
 fs.renameSync(f.source+'-moved',f.source);
 const restricted=JSON.parse(execFileSync(process.execPath,['--permission','--allow-fs-read='+f.temp,'--input-type=module','--eval',check],{cwd:f.temp,encoding:'utf8'}));
 assert.deepEqual(restricted,{restricted:'handled',artifacts:expectedNode.artifacts});
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
