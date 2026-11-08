import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
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
import {NativeProcessFailure,nativeProcessFailure,isLeanDecideFailure} from '../helpers/native-process.ts';
import {nodeExecutable,typeScriptToolchain} from '../helpers/local-toolchain.ts';

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
import {RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE,planCompiledReconciledProject,createReconciledFormalization,validateReconciledFormalization,renderReconciledFormalization} from '../../src/index.ts';
import {RECONCILED_FORMALIZATION_DEFINITION_SHA256} from '../../src/formalization/reconciled.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
const lean=process.env.DOMAINSPEC_LEAN ?? 'lean';
function runLean(f:any,source:string,suffix='Current'){
 const filename=path.join(f.temp,suffix+'.lean');fs.writeFileSync(filename,source);
 try{return execFileSync(lean,[filename],{encoding:'utf8',timeout:60000,maxBuffer:32*1024*1024});}
 catch(error){throw nativeProcessFailure('Lean kernel',error);}
}
function prepared(t:any){const f=allTypesFixture(t),selection=authored(f),plan=planCompiledReconciledProject(f.graph,selection);return {...f,selection,compiled:plan,bundle:createReconciledFormalization(f.graph,plan)};}
test('successor formalization is source bound and preserves old guard boundaries',t=>{
 const f=prepared(t),b=f.bundle;
 assert.equal(sha256(bytes(base+'reconciled-formalization-contract.json')),RECONCILED_FORMALIZATION_DEFINITION_SHA256);
 assert.equal(b.formal_verification,'not-performed');assert.equal(b.authority_effect,'none');
 assert.equal(b.artifact.sha256,sha256(b.artifact.content));
 assert.equal(renderReconciledFormalization(b),b.artifact.content);
 assert.deepEqual(validateReconciledFormalization(structuredClone(b),f.graph,f.compiled),b);
 assert.throws(()=>createMetaTypeFormalizationProjection(f.graph),/requires successor formalization/);
 for(const mutate of [(x:any)=>{x.artifact.content+='\n';},(x:any)=>{x.checked_predicates.pop();},(x:any)=>{x.formal_verification='pass';},(x:any)=>{x.input.compilation_selection.operations=[];}]){
  const clone=structuredClone(b);mutate(clone);const {bundle_sha256,...body}=clone;clone.bundle_sha256=sha256(canonicalJson(body));
  assert.throws(()=>validateReconciledFormalization(clone,f.graph,f.compiled),/RECONCILED_FORMALIZATION/);
 }
 assert.throws(()=>renderReconciledFormalization(structuredClone(b)),/registered/);
 assert.throws(()=>createReconciledFormalization(f.graph,structuredClone(f.compiled)),/registered/);
});
test('Lean kernel checks real all-thirteen graph and round-trips every source and selection field',t=>{
 const f=prepared(t),source=renderReconciledFormalization(f.bundle);
 assert.match(execFileSync(lean,['--version'],{encoding:'utf8'}),/version 4\.33\.1/);
 assert.doesNotMatch(source,/\b(?:sorry|axiom|native_decide)\b/);
 const output=runLean(f,source+'\n#eval IO.println (DomainSpec.Reconciled.toJson DomainSpec.Reconciled.sourceData)\n');
 assert.deepEqual(JSON.parse(output),{graph:f.bundle.input.semantic_graph,selection:f.bundle.input.compilation_selection});
});
test('well-formed Lean mutants of typed references fail the structural theorem',t=>{
 const f=prepared(t),source=renderReconciledFormalization(f.bundle);
 runLean(f,source,'Mutant-control');
 const units=(s:string)=>'(key '+JSON.stringify(s)+')';
 const pair=(key:string,value:string)=>'('+units(key)+', .str '+units(value)+')';
 for(const [key,value,replacement] of [['trigger_event_ref','alpha:posted','alpha:allowed'],['operation_ref','alpha:post','alpha:allowed'],['interface_selector','alpha:api','alpha:order']] as const){
  const from=pair(key,value),to=pair(key,replacement);assert.ok(source.includes(from));
  const mutant=source.replace(from,to);
  assert.throws(()=>runLean(f,mutant+'\n#eval DomainSpec.Reconciled.structureHolds (DomainSpec.Reconciled.field DomainSpec.Reconciled.sourceData "graph") (DomainSpec.Reconciled.field DomainSpec.Reconciled.sourceData "selection") DomainSpec.Reconciled.signatures\n','Mutant-'+key),e=>isLeanDecideFailure(e,true));
 }
 const coverage=source.replace(pair('step_id','post'),pair('step_id','missing'));
 assert.notEqual(coverage,source);assert.throws(()=>runLean(f,coverage,'Mutant-coverage'),e=>isLeanDecideFailure(e));
});
test('source order is preserved while authored occurrence binding order remains unconstrained',t=>{
 const f=allTypesFixture(t),selection=structuredClone(authored(f)),filename='specs/alpha/nodes/flow.json';
 const source=JSON.parse(fs.readFileSync(path.join(f.source,filename),'utf8'));
 source.body.typed_contract.steps=[{step_id:'first',operation_ref:'alpha:post'},{step_id:'second',operation_ref:'alpha:post'}];
 source.body.typed_contract.compensations=[{compensation_id:'undo-first',for_step:'first',operation_ref:'alpha:post',depends_on:[]},{compensation_id:'undo-second',for_step:'second',operation_ref:'alpha:post',depends_on:['undo-first']}];
 f.write(filename,source);
 const binding=selection.workflows[0],{step_id,...call}=binding.steps[0];
 binding.steps=[{...call,step_id:'second'},{...call,step_id:'first'}];
 binding.compensations=[{...call,compensation_id:'undo-second'},{...call,compensation_id:'undo-first'}];
 binding.result.value.step_id='second';
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,selection),b=createReconciledFormalization(graph,plan);
 assert.equal(runLean(f,b.artifact.content),'');
 assert.deepEqual((b.input.semantic_graph.nodes.find(n=>n.selector==='alpha:flow')!.body.typed_contract as any).steps.map((s:any)=>s.step_id),['first','second']);
 assert.deepEqual(b.input.compilation_selection.workflows[0]!.steps.map(s=>s.step_id),['second','first']);
});
test('Lean round-trip preserves hostile text, Unicode representations and lone UTF-16 surrogates',t=>{
 const f=allTypesFixture(t),filename='specs/alpha/nodes/total.json',source=JSON.parse(fs.readFileSync(path.join(f.source,filename),'utf8'));
 source.body.description='é e\u0301 \ud83d\ude80 \ud800 \udfff \u0000 \b \f " \\ \nend DomainSpec.Reconciled\n#eval IO.println "injected"';
 f.write(filename,source);
 const asciiFile='specs/alpha/nodes/mode.json',asciiNode=JSON.parse(fs.readFileSync(path.join(f.source,asciiFile),'utf8'));
 const asciiText='line one\r\n\t"quoted" \\ path\nend DomainSpec.Reconciled\n#eval IO.println "injected"';
 asciiNode.body.description=asciiText;f.write(asciiFile,asciiNode);
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,authored(f)),b=createReconciledFormalization(graph,plan);
 assert.ok(b.artifact.content.includes('.str (key '+JSON.stringify(asciiText)+')'),'ASCII whitespace must use compact escaped data, not a large unit list');
 const output=runLean(f,b.artifact.content+'\n#eval IO.println (DomainSpec.Reconciled.toJson DomainSpec.Reconciled.sourceData)\n');
 assert.deepEqual(JSON.parse(output),{graph:b.input.semantic_graph,selection:b.input.compilation_selection});
});
test('formalization construction is immutable, root-independent and does not reload checked source',t=>{
 const f=prepared(t),copy=path.join(f.temp,'copy');fs.cpSync(f.source,copy,{recursive:true});
 const g=loadCompiledProjectGraph(copy),p=planCompiledReconciledProject(g,f.selection);
 assert.deepEqual(createReconciledFormalization(g,p),f.bundle);
 const before=canonicalJson(f.graph),read=fs.readFileSync;(fs as any).readFileSync=()=>{throw Error('unexpected source read');};
 try{assert.deepEqual(createReconciledFormalization(f.graph,f.compiled),f.bundle);assert.deepEqual(validateReconciledFormalization(structuredClone(f.bundle),f.graph,f.compiled),f.bundle);}finally{fs.readFileSync=read;}
 assert.equal(canonicalJson(f.graph),before);assert.ok(Object.isFrozen(f.bundle)&&Object.isFrozen(f.bundle.artifact));
 let calls=0;const active={...f.bundle};Object.defineProperty(active,'artifact',{enumerable:true,get(){calls++;return f.bundle.artifact;}});
 assert.throws(()=>validateReconciledFormalization(active,f.graph,f.compiled),/inert/);assert.equal(calls,0);
});
test('compiled public formalization API works without repository source or definition access',t=>{
 const f=prepared(t),cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const node=nodeExecutable(),{compiler,typeRoots}=typeScriptToolchain();
 const compile=(args:string[])=>{try{return execFileSync(node,[compiler,'--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',typeRoots,'--target','ES2022','--module','NodeNext',...args],{encoding:'utf8',timeout:60000,maxBuffer:32*1024*1024});}catch(error){throw nativeProcessFailure('formalization API TypeScript compiler',error);}};
 fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));compile(['--declaration','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')]);
 fs.writeFileSync(path.join(f.temp,'consumer.ts'),`import {createReconciledFormalization,type CompiledProjectGraph,type ReconciledProjectPlan,type ReconciledFormalization} from './dist/index.js';
 export function create(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
  const bundle:ReconciledFormalization=createReconciledFormalization(graph,plan);
  const status:'not-performed'=bundle.formal_verification;
  // @ts-expect-error Construction is not a proof receipt.
  const forged:{formal_verification:'pass'}=bundle;
  return {bundle,status};
 }`);compile(['--noEmit',path.join(f.temp,'consumer.ts')]);
 const forged=path.join(f.temp,'forged-proof.ts');
 fs.writeFileSync(forged,`import type {ReconciledFormalization} from './dist/index.js';
 declare const bundle:ReconciledFormalization;
 const forged:{formal_verification:'pass'}=bundle;`);
 assert.throws(()=>compile(['--noEmit',forged]),error=>error instanceof NativeProcessFailure
  &&error.failure_kind==='exit'&&error.status!==null&&error.status>0&&error.code===null&&error.signal===null
  &&error.diagnostic.match(/\berror TS\d+:/g)?.length===1
  &&/forged-proof\.ts\(3,\d+\): error TS2322:/.test(error.diagnostic)
  &&/Type '"not-performed"' is not assignable to type '"pass"'/.test(error.diagnostic));
 const script=`import assert from 'node:assert/strict';import fs from 'node:fs';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,createReconciledFormalization,renderReconciledFormalization,validateReconciledFormalization} from './dist/index.js';
 assert.throws(()=>fs.readFileSync(${JSON.stringify(path.join(project,base+'reconciled-formalization-contract.json'))}),{code:'ERR_ACCESS_DENIED'});
 assert.throws(()=>fs.readFileSync(${JSON.stringify(path.join(src,'index.ts'))}),{code:'ERR_ACCESS_DENIED'});
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),bundle=createReconciledFormalization(graph,plan);
 assert.equal(renderReconciledFormalization(validateReconciledFormalization(JSON.parse(JSON.stringify(bundle)),graph,plan)),bundle.artifact.content);
 process.stdout.write(JSON.stringify(bundle));`;
 const actual=JSON.parse(execFileSync(node,['--permission','--allow-fs-read='+f.temp,'--input-type=module','--eval',script],{cwd:f.temp,encoding:'utf8',timeout:60000,maxBuffer:32*1024*1024}));
 assert.deepEqual(actual,f.bundle);
});
test('structural theorem uses only Lean standard foundations, without project axioms or native oracle',t=>{
 const f=prepared(t),output=runLean(f,f.bundle.artifact.content+'\n#print axioms DomainSpec.Reconciled.currentStructuralReferencesHold\n');
 assert.equal(output.trim(),"'DomainSpec.Reconciled.currentStructuralReferencesHold' depends on axioms: [propext, Classical.choice, Quot.sound]");
});
