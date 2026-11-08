import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync,spawnSync} from 'node:child_process';
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

import {planReconciledProject,planCompiledReconciledProject,RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE,createReconciledOutputReceipt,publishReconciledProject,verifyReconciledProject,planProjectBuild,planCompiledProjectBuild,publishProjectBuild,verifyProjectBuild,runCli,type ProjectBuildPlanV1,type ReconciledBuildPlan} from '../../src/index.ts';
import {RECONCILED_BUILD_API_DEFINITION_SHA256} from '../../src/generation/reconciled-build.ts';
function authored(f:ReturnType<typeof allTypesFixture>):any{
 const action=f.requests.find(r=>r.kind==='operations')!.selection;
 const w=f.requests.find(r=>r.kind==='workflows')!.selection.workflow.bindings;
 const strip=(call:any)=>{const {action_sha256,...rest}=call;return rest;};
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:action.factories,operations:action.actions.map((a:any)=>a.bindings),workflows:[{selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:w.steps.map(strip),compensations:w.compensations.map(strip),result:w.result,recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
}
test('existing source and snapshot build APIs preserve the exact checked plan, artifact bytes and receipt',t=>{
 const f=allTypesFixture(t),selection=authored(f),direct=planReconciledProject(f.source,selection);
 assert.equal(sha256(bytes(base+'reconciled-build-api-contract.json')),RECONCILED_BUILD_API_DEFINITION_SHA256);
 const source=planProjectBuild(f.source,'typescript',undefined,undefined,selection);
 const snapshot=planCompiledProjectBuild(f.graph,'typescript',EXACT_UINT64_PROFILE,undefined,selection);
 assert.deepEqual(source,snapshot);assert.deepEqual(source.project,direct);
 assert.deepEqual(source.artifacts,direct.resolved.artifacts);assert.deepEqual(source.receipt,createReconciledOutputReceipt(direct));
 assert.equal(source.schema_version,'domainspec.reconciled-build-plan/v1-candidate');
 assert.ok(Object.isFrozen(source)&&Object.isFrozen(source.artifacts)&&Object.isFrozen(source.receipt));
 assert.equal(source.receipt.native_compilation,'not-performed');assert.equal('compiled_certificate' in source.receipt,false);
 const out=path.join(f.temp,'api-out'),directOut=path.join(f.temp,'direct-out');
 const publication=publishProjectBuild(source,out),directPublication=publishReconciledProject(direct,directOut);
 assert.deepEqual(publication.receipt,directPublication.receipt);assert.equal(publication.receipt_path,directPublication.receipt_path);
 assert.deepEqual(verifyProjectBuild(f.source,'typescript',out,undefined,undefined,selection),verifyReconciledProject(direct,out));
 assert.equal(verifyProjectBuild(f.source,'typescript',directOut,EXACT_UINT64_PROFILE,undefined,selection).result,'pass');
 for(const a of source.artifacts)assert.equal(fs.readFileSync(path.join(out,a.relative_path),'utf8'),a.content);
 fs.renameSync(f.source,path.join(f.temp,'relocated-source'));
 assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript',undefined,undefined,selection),snapshot);
 assert.throws(()=>planProjectBuild(f.source,'typescript',undefined,undefined,selection));
 assert.throws(()=>planCompiledProjectBuild(structuredClone(f.graph),'typescript',undefined,undefined,selection),/unvalidated|registered|snapshot/);
});
test('explicit selection rejects unsupported API combinations before source reads or output mutation',t=>{
 const f=allTypesFixture(t),selection=authored(f),missing=path.join(f.temp,'missing');
 const rejected=(lang:any,profile:any,layout:any,choice:any)=>{
  assert.throws(()=>planProjectBuild(missing,lang,profile,layout,choice),/DS_RECONCILED/);
  assert.throws(()=>planCompiledProjectBuild(f.graph,lang,profile,layout,choice),/DS_RECONCILED/);
  assert.throws(()=>verifyProjectBuild(missing,lang,path.join(f.temp,'never'),profile,layout,choice),/DS_RECONCILED/);
  assert.equal(fs.existsSync(path.join(f.temp,'never')),false);
 };
 for(const choice of [null,{}, {...selection,profile_id:'unknown'}, {...selection,extra:true}])rejected('typescript',undefined,undefined,choice);
 rejected('python',undefined,undefined,selection);rejected('rust',undefined,undefined,selection);
 rejected('typescript','wrong',undefined,selection);rejected('typescript',undefined,'domainspec.application-layout/unknown',selection);
 rejected('typescript',undefined,'unknown',selection);
 const owner=path.join(f.temp,'owned');fs.mkdirSync(owner);fs.writeFileSync(path.join(owner,'keep'),'owner');
 const plan=planProjectBuild(f.source,'typescript',undefined,undefined,selection);
 assert.throws(()=>publishProjectBuild(plan,owner),/already exists/);assert.equal(fs.readFileSync(path.join(owner,'keep'),'utf8'),'owner');
 const {schema_version:ignored,...untagged}=plan;
 for(const forged of [structuredClone(plan),{...plan},{...plan,artifacts:[]},{...plan,receipt:{...plan.receipt,schema_version:'domainspec.project-build-receipt/v1'}},{...plan,schema_version:'foreign'},{...untagged,receipt:{...plan.receipt,schema_version:'domainspec.project-build-receipt/v1'}}]){
  assert.throws(()=>publishProjectBuild(forged as any,path.join(f.temp,'forged')),/registered reconciled build/);
  assert.equal(fs.existsSync(path.join(f.temp,'forged')),false);
 }
});
test('source API detects drift while snapshot API performs no filesystem reload',t=>{
 const f=allTypesFixture(t),selection=authored(f),file=path.join(f.source,'project.json'),original=fs.readFileSync(file,'utf8'),read=fs.readFileSync;
 let changed=false;
 (fs as any).readFileSync=(fileName:any,...rest:any[])=>{
  const result=(read as any)(fileName,...rest);
  if(!changed&&String(fileName)===file){changed=true;fs.writeFileSync(file,original+' ');}
  return result;
 };
 try{assert.throws(()=>planProjectBuild(f.source,'typescript',undefined,undefined,selection),/drift|changed/i);}finally{fs.readFileSync=read;fs.writeFileSync(file,original);}
 assert.equal(changed,true);
 const expected=planCompiledProjectBuild(f.graph,'typescript',undefined,undefined,selection);
 (fs as any).readFileSync=()=>{throw Error('unexpected source reload');};
 try{assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript',undefined,undefined,selection),expected);}finally{fs.readFileSync=read;}
});
test('selected CLI build and currentness verify use equivalent public wrapper receipts',t=>{
 const f=allTypesFixture(t),selection=authored(f),file=path.join(f.temp,'selection.json'),out=path.join(f.temp,'cli-out');fs.writeFileSync(file,JSON.stringify(selection));
 const call=(command:string)=>{const stdout:string[]=[],stderr:string[]=[];const code=runCli([command,f.source,'--language','typescript','--target-root',out,'--compilation-selection',file],{stdout:s=>stdout.push(s),stderr:s=>stderr.push(s)});assert.equal(code,0,stderr.join(''));return JSON.parse(stdout.join(''));};
 const build=call('build'),plan=planProjectBuild(f.source,'typescript',undefined,undefined,selection);
 assert.deepEqual(build.receipt,plan.receipt);
 assert.deepEqual(call('verify'),verifyProjectBuild(f.source,'typescript',out,undefined,undefined,selection));
 const artifact=plan.artifacts[0]!;fs.appendFileSync(path.join(out,artifact.relative_path),' ');
 assert.equal(verifyProjectBuild(f.source,'typescript',out,undefined,undefined,selection).result,'fail');
});
test('omitted selection preserves legacy API signatures and receipts for all three languages',t=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-legacy-build-api-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const f={temp,source:path.join(temp,'source')};
 fs.cpSync(path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project'),f.source,{recursive:true});
 const graph=loadCompiledProjectGraph(f.source);
 for(const language of ['typescript','python','rust'] as const){
  const legacy:ProjectBuildPlanV1=planProjectBuild(f.source,language);
  assert.deepEqual(legacy,planProjectBuild(f.source,language,undefined,undefined,undefined));
  assert.deepEqual(legacy,planCompiledProjectBuild(graph,language));
  assert.equal(legacy.receipt.schema_version,'domainspec.project-build-receipt/v1');
  assert.equal('schema_version' in legacy,false);
  const out=path.join(f.temp,language);const published=publishProjectBuild(legacy,out);
  assert.equal(published.receipt.schema_version,'domainspec.project-build-receipt/v1');
  assert.equal(verifyProjectBuild(f.source,language,out).result,'pass');
 }
});

test('native public declarations preserve overloads and relocated build APIs work without checkout access',t=>{
 const f=allTypesFixture(t),selection=authored(f),cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,image];
 const compile=(args:string[])=>{try{return execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext',...args],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 // The normal package includes Lean source assets even when no Lean process is run.
 fs.cpSync(path.join(cliRoot,'lean'),path.join(f.temp,'lean'),{recursive:true});
 fs.cpSync(path.join(cliRoot,'fixtures/input-roots/canonical-project'),path.join(f.temp,'legacy-source'),{recursive:true});
 compile(['--declaration','--rootDir',src,'--outDir',dist,path.join(src,'index.ts'),path.join(src,'cli/main.ts')]);
 const consumer=path.join(f.temp,'consumer.ts');
 fs.writeFileSync(consumer,`import {planProjectBuild,planCompiledProjectBuild,publishProjectBuild,verifyProjectBuild,type ReconciledCompilationSelection,type ReconciledBuildPlan,type ProjectBuildPlanV1,type ReconciledBuildPublication,type ProjectBuildPublicationV1,type ReconciledBuildVerification,type ProjectBuildVerificationV1,type CompiledProjectGraph} from './dist/index.js';
 export function signatures(source:string,target:string,graph:CompiledProjectGraph,selection:ReconciledCompilationSelection,optional:ReconciledCompilationSelection|undefined){
  const old:ProjectBuildPlanV1=planProjectBuild(source,'typescript');
  const absent:ProjectBuildPlanV1=planProjectBuild(source,'typescript',undefined,undefined,undefined);
  const selected:ReconciledBuildPlan=planProjectBuild(source,'typescript',undefined,undefined,selection);
  const snapshot:ReconciledBuildPlan=planCompiledProjectBuild(graph,'typescript',undefined,undefined,selection);
  const application:ReconciledBuildPlan=planCompiledProjectBuild(graph,'typescript',undefined,'domainspec.application-layout/v1',selection);
  const applicationPublished:ReconciledBuildPublication=publishProjectBuild(application,target);
  const dynamic:ProjectBuildPlanV1|ReconciledBuildPlan=planProjectBuild(source,'typescript',undefined,undefined,optional);
  const oldPublished:ProjectBuildPublicationV1=publishProjectBuild(old,target);
  const selectedPublished:ReconciledBuildPublication=publishProjectBuild(selected,target);
  const dynamicPublished:ProjectBuildPublicationV1|ReconciledBuildPublication=publishProjectBuild(dynamic,target);
  const oldVerified:ProjectBuildVerificationV1=verifyProjectBuild(source,'typescript',target);
  const selectedVerified:ReconciledBuildVerification=verifyProjectBuild(source,'typescript',target,undefined,undefined,selection);
  const dynamicVerified:ProjectBuildVerificationV1|ReconciledBuildVerification=verifyProjectBuild(source,'typescript',target,undefined,undefined,optional);
  // @ts-expect-error A selected receipt is not a legacy assurance receipt.
  const falseLegacy:ProjectBuildPlanV1=selected;
  // @ts-expect-error Currentness verification has no legacy observed_receipt_sha256 member.
  selectedVerified.observed_receipt_sha256;
  return {absent,snapshot,oldPublished,selectedPublished,dynamicPublished,oldVerified,selectedVerified,dynamicVerified};
 }`);
 compile(['--noEmit',consumer]);
 const check=`import assert from 'node:assert/strict';import fs from 'node:fs';
 import {planProjectBuild,planCompiledProjectBuild,publishProjectBuild,verifyProjectBuild,loadCompiledProjectGraph} from './dist/index.js';
 assert.throws(()=>fs.readFileSync(${JSON.stringify(path.join(project,base+'reconciled-build-api-contract.json'))}),{code:process.permission?'ERR_ACCESS_DENIED':'ENOENT'});
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(selection)},target=${JSON.stringify(path.join(f.temp,'native-output'))};
 const graph=loadCompiledProjectGraph(source);
 const plan=planProjectBuild(source,'typescript',undefined,undefined,selection);
 assert.deepEqual(planCompiledProjectBuild(graph,'typescript',undefined,undefined,selection),plan);
 if(process.permission){
  const before=fs.readdirSync(${JSON.stringify(f.temp)});
  for(const outputLayout of [undefined,'domainspec.application-layout/v1']){
   const selected=planProjectBuild(source,'typescript',undefined,outputLayout,selection);
   const existing=target+(outputLayout?'-application':'');
   assert.equal(verifyProjectBuild(source,'typescript',existing,undefined,outputLayout,selection).result,'pass');
   assert.throws(()=>publishProjectBuild(selected,existing+'-blocked'),{code:'DS_RECONCILED_OUTPUT_UNAVAILABLE',exitCode:22,pointer:'/target-root'});
   assert.equal(fs.existsSync(existing+'-blocked'),false);
  }
  const legacy=planProjectBuild(${JSON.stringify(path.join(f.temp,'legacy-source'))},'typescript');
  assert.throws(()=>publishProjectBuild(legacy,target+'-legacy-blocked'),{code:'MTCLI_PROJECT_BUILD_UNAVAILABLE',exitCode:22});
  assert.deepEqual(fs.readdirSync(${JSON.stringify(f.temp)}),before);
  console.log(JSON.stringify({restricted:'handled',artifacts:plan.artifacts}));
 }else{
 const output=publishProjectBuild(plan,target);
 assert.equal(verifyProjectBuild(source,'typescript',target,undefined,undefined,selection).result,'pass');
 assert.equal(output.receipt.native_compilation,'not-performed');
 const application=planProjectBuild(source,'typescript',undefined,'domainspec.application-layout/v1',selection);
 assert.deepEqual(planCompiledProjectBuild(graph,'typescript',undefined,'domainspec.application-layout/v1',selection),application);
 const appOutput=publishProjectBuild(application,target+'-application');
 assert.equal(appOutput.receipt_path,'evidence/project-build.json');
 assert.equal(verifyProjectBuild(source,'typescript',target+'-application',undefined,'domainspec.application-layout/v1',selection).result,'pass');
 console.log(JSON.stringify({receipt:output.receipt,artifacts:plan.artifacts,application:{receipt:appOutput.receipt,artifacts:application.artifacts}}));}`;
 // Runtime container mounts only the relocated fixture, not the source checkout or development dependencies.
 const runtime=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+f.temp,image,'node','--input-type=module','--eval',check];
 const actual=JSON.parse(execFileSync('docker',runtime,{encoding:'utf8'}));
 const expected=planProjectBuild(f.source,'typescript',undefined,undefined,selection);
 const application=planProjectBuild(f.source,'typescript',undefined,'domainspec.application-layout/v1',selection);
 assert.deepEqual(actual,{receipt:expected.receipt,artifacts:expected.artifacts,application:{receipt:application.receipt,artifacts:application.artifacts}});
 const restricted=JSON.parse(execFileSync(process.execPath,['--permission','--allow-fs-read='+f.temp,'--input-type=module','--eval',check],{cwd:f.temp,encoding:'utf8'}));
 assert.deepEqual(restricted,{restricted:'handled',artifacts:expected.artifacts});
 const selectionFile=path.join(f.temp,'permission-selection.json');fs.writeFileSync(selectionFile,JSON.stringify(selection));
 for(const command of ['build','instantiate','instantiate-project']){
  const target=path.join(f.temp,'cli-blocked-'+command);
  const argv=[command,f.source,'--compilation-selection',selectionFile,...(command==='instantiate-project'?['--languages','typescript']:['--language','typescript']),'--target-root',target,...(command==='instantiate'?['--node','alpha:flow']:[])];
  const result=spawnSync(process.execPath,['--permission','--allow-fs-read='+f.temp,path.join(dist,'cli/main.js'),...argv],{cwd:f.temp,encoding:'utf8',timeout:30000});
  assert.equal(result.status,22,result.stderr);assert.equal(result.stdout,'');
  assert.equal(JSON.parse(result.stderr).code,'DS_RECONCILED_OUTPUT_UNAVAILABLE');
  assert.equal(fs.existsSync(target),false);
 }
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
