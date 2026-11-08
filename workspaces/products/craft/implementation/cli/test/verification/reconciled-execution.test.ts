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

function authored(f:ReturnType<typeof allTypesFixture>):any{
 const action=f.requests.find(r=>r.kind==='operations')!.selection;
 const w=f.requests.find(r=>r.kind==='workflows')!.selection.workflow.bindings;
 const strip=(call:any)=>{const {action_sha256,...rest}=call;return rest;};
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:action.factories,operations:action.actions.map((a:any)=>a.bindings),workflows:[{selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:w.steps.map(strip),compensations:w.compensations.map(strip),result:w.result,recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
}
import {RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE,planCompiledReconciledProject,executeReconciledVerification,renderReconciledVerificationExecution,publishReconciledProject} from '../../src/index.ts';
import {RECONCILED_VERIFICATION_EXECUTION_DEFINITION_SHA256} from '../../src/verification/reconciled-execution.ts';
const absent={typescript_root:'/absent/typescript',node_type_root:'/absent/types',lean_executable:'/absent/lean'};
test('execution requires bound checked inputs and closed options before writing or spawning',t=>{
 const f=allTypesFixture(t),plan=planCompiledReconciledProject(f.graph,authored(f));
 assert.equal(sha256(bytes(base+'reconciled-verification-execution-contract.json')),RECONCILED_VERIFICATION_EXECUTION_DEFINITION_SHA256);
 const before=fs.readdirSync(f.temp);
 assert.throws(()=>executeReconciledVerification(structuredClone(f.graph),plan,absent),/snapshot|unvalidated/);
 assert.throws(()=>executeReconciledVerification(f.graph,structuredClone(plan),absent),/registered/);
 for(const options of [{...absent,skip:true},{...absent,typescript_root:'relative'},{...absent,target_root:'../output'}]){
  assert.throws(()=>executeReconciledVerification(f.graph,plan,options),/RECONCILED_VERIFICATION_EXECUTION/);
 }
 let calls=0;const active={...absent};Object.defineProperty(active,'lean_executable',{enumerable:true,get(){calls++;return '/bin/true';}});
 assert.throws(()=>executeReconciledVerification(f.graph,plan,active),/inert/);assert.equal(calls,0);
 assert.deepEqual(fs.readdirSync(f.temp),before);
});
test('source drift prevents subprocess checks and never becomes a passing receipt',t=>{
 const f=allTypesFixture(t),plan=planCompiledReconciledProject(f.graph,authored(f));
 fs.appendFileSync(path.join(f.source,'project.json'),'\n');
 const report=executeReconciledVerification(f.graph,plan,absent);
 assert.equal(report.result,'fail');
 assert.equal(report.checks.find(c=>c.id==='source-currentness')!.result,'fail');
 assert.equal(report.checks.find(c=>c.id==='strict-native-compilation')!.executed,false);
 assert.ok(report.checks.some(c=>c.id==='cross-generator-behavior'&&c.result==='not_evaluable'));
 assert.throws(()=>renderReconciledVerificationExecution(structuredClone(report)),/registered/);
 assert.equal(renderReconciledVerificationExecution(report),canonicalJson(report)+'\n');
});
test('missing validators and mismatched existing output fail without changing the target',t=>{
 const f=allTypesFixture(t),plan=planCompiledReconciledProject(f.graph,authored(f)),target=path.join(f.temp,'output');
 const absentTarget=path.join(f.temp,'absent-target'),unavailable=executeReconciledVerification(f.graph,plan,{...absent,target_root:absentTarget});
 assert.equal(unavailable.result,'fail');assert.equal(fs.existsSync(absentTarget),false);
 assert.equal(unavailable.checks.find(c=>c.id==='strict-native-compilation')!.executed,false);
 publishReconciledProject(plan,target);
 const missing=executeReconciledVerification(f.graph,plan,{...absent,target_root:target});
 assert.equal(missing.result,'fail');
 assert.equal(missing.checks.find(c=>c.id==='toolchain-currentness')!.result,'fail');
 assert.equal(missing.checks.find(c=>c.id==='verification-workspace-cleanup')!.result,'pass');
 const artifact=path.join(target,plan.resolved.artifacts[0]!.relative_path);fs.appendFileSync(artifact,'\n// owner change\n');
 const before=fs.readFileSync(artifact),report=executeReconciledVerification(f.graph,plan,{...absent,target_root:target});
 assert.equal(report.result,'fail');
 assert.equal(report.checks.find(c=>c.id==='exact-output-currentness')!.result,'fail');
 assert.equal(report.checks.find(c=>c.id==='toolchain-currentness')!.executed,false);
 for(const id of ['strict-native-compilation','lean-structural-kernel']){
  const row=report.checks.find(c=>c.id===id)!;assert.equal(row.result,'not_evaluable');assert.equal(row.executed,false);
 }
 assert.equal(report.checks.find(c=>c.id==='verification-workspace-cleanup')!.executed,false);
 assert.deepEqual(fs.readFileSync(artifact),before);
 assert.ok(Object.isFrozen(report)&&Object.isFrozen(report.checks)&&Object.isFrozen(report.checks[0]!.evidence));
 assert.equal(new Set(report.checks.map(c=>c.id)).size,report.checks.length);
});
test('an interrupted workspace still rechecks source and cleans its owned directory',t=>{
 const f=allTypesFixture(t),plan=planCompiledReconciledProject(f.graph,authored(f)),original=fs.writeFileSync;
 fs.writeFileSync=((file:any,...args:any[])=>{
  if(String(file).includes('/domainspec-reconciled-verify-')&&String(file).endsWith('/native/package.json')){
   fs.appendFileSync(path.join(f.source,'project.json'),'\n');throw Error('injected workspace interruption');
  }
  return (original as any)(file,...args);
 }) as typeof fs.writeFileSync;
 let report;try{report=executeReconciledVerification(f.graph,plan,absent);}finally{fs.writeFileSync=original;}
 assert.equal(report.result,'fail');
 for(const id of ['source-currentness','verification-workspace-currentness'])assert.equal(report.checks.find(c=>c.id===id)!.result,'fail',id);
 assert.equal(report.checks.find(c=>c.id==='compiled-graph-obligations')!.result,'not_evaluable');
 assert.equal(report.checks.find(c=>c.id==='verification-workspace-cleanup')!.result,'pass');
});
test('an unavailable private workspace produces failed accounting without running tools',t=>{
 const f=allTypesFixture(t),plan=planCompiledReconciledProject(f.graph,authored(f)),original=fs.mkdtempSync;
 fs.mkdtempSync=(()=>{throw Error('injected private workspace unavailable');}) as typeof fs.mkdtempSync;
 let report;try{report=executeReconciledVerification(f.graph,plan,absent);}finally{fs.mkdtempSync=original;}
 assert.equal(report.result,'fail');assert.equal(report.checks.find(c=>c.id==='verification-workspace-currentness')!.result,'fail');
 for(const id of ['strict-native-compilation','lean-structural-kernel','verification-workspace-cleanup'])assert.equal(report.checks.find(c=>c.id===id)!.executed,false,id);
});
function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici=path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(JSON.stringify({message:String(e.message??'').slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}));}};
 return {run,options};
}
test('real native execution checks all artifacts, AST surfaces, replay and Lean without target writes',t=>{
 const f=allTypesFixture(t),selection=authored(f),plan=planCompiledReconciledProject(f.graph,selection),target=path.join(f.temp,'output');
 publishReconciledProject(plan,target);
 const n=nativeContext(f),report=n.run(`import fs from 'node:fs';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(selection)});
 process.env.NODE_OPTIONS='--require /absent/poison.cjs';process.env.LEAN_PATH='/absent/lean';
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));
 `);
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 for(const id of ['strict-native-compilation','independent-module-surface-observation','source-currentness','compiled-graph-obligations','isolated-exact-source-replay','source-and-selection-preservation','successor-formalization-currentness','exact-output-currentness','lean-structural-kernel','verification-workspace-currentness','toolchain-currentness','verification-workspace-cleanup'])assert.equal(report.checks.find((c:any)=>c.id===id)?.result,'pass',id);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass');assert.equal(semantic.evidence.tested_node_count,f.graph.nodes.length);assert.deepEqual(semantic.evidence.remaining,[]);
 assert.ok(semantic.evidence.tested.some((r:any)=>r.selector==='alpha:flow'&&r.kind==='Workflow'&&r.case_count>1));
 for(const id of ['workflow-source-effect-audit','workflow-native-effect-audit','workflow-effect-audit-currentness','workflow-source-orchestration-audit','workflow-native-orchestration-audit','workflow-orchestration-audit-currentness'])assert.equal(report.checks.find((c:any)=>c.id===id)?.result,'pass',id);
 assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['cross-generator-behavior','safe-output-separate-from-planning']);
 assert.equal(report.denominators.artifact_count,plan.resolved.artifacts.length);
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
 for(const a of plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});
test('native observation and late currentness controls reject compiling mutations and stale inputs',t=>{
 const f=allTypesFixture(t),selection=authored(f),n=nativeContext(f);
 const reports=n.run(String.raw`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(selection)},options=${JSON.stringify(n.options)},original=cp.spawnSync;
 const sourceFile=path.join(source,'project.json'),sourceBytes=fs.readFileSync(sourceFile),reports=[];
 for(const mode of ['extra-export','artifact-drift','config-drift','observer-drift','source-drift']){
  const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
  cp.spawnSync=(command,args,settings)=>{
   // Fail the expensive Lean dependency deliberately in these native TS controls;
   // the separate positive case executes the real kernel and round trip.
   if(command===options.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure'};
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&mode==='extra-export')fs.appendFileSync(path.join(settings.cwd,plan.resolved.artifacts[0].relative_path),'\nexport const UnexpectedSurface = 1;\n');
   if(result.status===0&&String(args[0]).endsWith('observe.mjs')){
    if(mode==='artifact-drift')fs.appendFileSync(path.join(settings.cwd,plan.resolved.artifacts[0].relative_path),'\n// late change\n');
    if(mode==='config-drift')fs.appendFileSync(path.join(settings.cwd,'tsconfig.json'),'\n');
    if(mode==='observer-drift')fs.appendFileSync(args[0],'\n');
    if(mode==='source-drift')fs.appendFileSync(sourceFile,'\n');
   }
   return result;
  };syncBuiltinESMExports();
  try{reports.push({mode,report:executeReconciledVerification(graph,plan,options)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();fs.writeFileSync(sourceFile,sourceBytes);}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report} of reports){
  assert.equal(report.result,'fail',mode);
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  assert.equal(check('lean-structural-kernel').result,'fail');
  assert.equal(check('source-and-selection-preservation').result,'not_evaluable');
  assert.equal(check('exact-output-currentness').result,'not_evaluable');
  if(mode==='extra-export')assert.equal(check('independent-module-surface-observation').result,'fail');
  else if(mode==='source-drift')assert.equal(check('source-currentness').result,'fail');
  else assert.equal(check('verification-workspace-currentness').result,'fail');
  assert.equal(check('strict-native-compilation').result,'not_evaluable',mode);
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
