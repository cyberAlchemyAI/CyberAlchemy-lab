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

function nativeExisting(root:string,p:ReturnType<typeof planResolvedArtifacts>) {
  const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:[path.join(project,'impl'),...process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))]}),deps=path.dirname(path.dirname(path.dirname(types)));
  const image=nativeToolchainImage();
  const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--mount','type=bind,source='+deps+',target='+deps+',readonly','--workdir',root,image];
  const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...p.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});
  try {compile();} catch(e:any) {throw Error(String(e.stdout)+String(e.stderr));}
  const load=(suffix:string)=>{const a=p.artifacts.find(a=>a.relative_path.endsWith(suffix))!;assert.ok(a,suffix);return require(path.join(root,'js',a.relative_path.replace(/\.ts$/,'.js')));};
  return {root,load,docker,compile};
}


import {runCli,RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE,planCompiledReconciledProject,selectReconciledArtifacts,publishReconciledProject,verifyReconciledProject,readReconciledCompilationSelection,createReconciledOutputReceipt,RECONCILED_OUTPUT_RECEIPT_PATH} from '../../src/index.ts';
import {RECONCILED_OUTPUT_DEFINITION_SHA256} from '../../src/generation/reconciled-output.ts';
function authored(f:ReturnType<typeof allTypesFixture>):any{
 const action=f.requests.find(r=>r.kind==='operations')!.selection;
 const w=f.requests.find(r=>r.kind==='workflows')!.selection.workflow.bindings;
 const strip=(call:any)=>{const {action_sha256,...rest}=call;return rest;};
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:action.factories,operations:action.actions.map((a:any)=>a.bindings),workflows:[{selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:w.steps.map(strip),compensations:w.compensations.map(strip),result:w.result,recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
}
function prepared(t:any){const f=allTypesFixture(t),selection=authored(f),file=path.join(f.temp,'selection.json');fs.writeFileSync(file,JSON.stringify(selection));return {...f,selection,file,compiled:planCompiledReconciledProject(f.graph,selection)};}
function cli(args:string[]){const out:string[]=[],err:string[]=[];const code=runCli(args,{stdout:s=>out.push(s),stderr:s=>err.push(s)});return {code,out:out.length?JSON.parse(out.join('')):null,error:err.length?JSON.parse(err.join('')):null};}
function args(f:ReturnType<typeof prepared>,command:string,target:string,node?:string){return [command,f.source,'--compilation-selection',f.file,...(command==='instantiate-project'?['--languages','typescript']:['--language','typescript']),'--target-root',target,...(node?['--node',node]:[])];}
test('selected public commands and APIs publish byte-identical whole-project and node artifacts',t=>{
 const f=prepared(t),baseline=canonicalJson(f.graph);
 assert.equal(sha256(bytes(base+'reconciled-output-contract.json')),RECONCILED_OUTPUT_DEFINITION_SHA256);
 for(const command of ['build','instantiate-project']){
  const target=path.join(f.temp,command),result=cli(args(f,command,target));assert.equal(result.code,0,JSON.stringify(result.error));
  assert.deepEqual(result.out.receipt,createReconciledOutputReceipt(f.compiled));
  const verify=cli(args(f,'verify',target));assert.equal(verify.code,0);assert.equal(verify.out.verification_scope,'artifact-currentness');
  for(const key of ['native_compilation','semantic_observation','formal_verification'])assert.equal(verify.out[key],'not-performed');
  for(const a of f.compiled.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
 }
 const target=path.join(f.temp,'node'),result=cli(args(f,'instantiate',target,'alpha:flow'));assert.equal(result.code,0,JSON.stringify(result.error));
 const view=selectReconciledArtifacts(f.compiled,['alpha:flow']);assert.equal(result.out.receipt.view_sha256,view.view_sha256);
 assert.equal(cli(args(f,'verify',target,'alpha:flow')).code,0);assert.equal(cli(args(f,'verify',target)).code,1);
 const apiTarget=path.join(f.temp,'api'),published=publishReconciledProject(f.compiled,apiTarget,['alpha:flow']);
 assert.deepEqual(published.receipt,result.out.receipt);assert.equal(verifyReconciledProject(f.compiled,apiTarget,['alpha:flow']).result,'pass');
 assert.equal(canonicalJson(loadCompiledProjectGraph(f.source)),baseline);
});
test('real CLI process builds a native compound project and node closure',async t=>{
 const f=prepared(t);
 for(const [name,command,node] of [['whole','build',null],['single','instantiate','alpha:flow']] as const){
  const target=path.join(f.temp,name),argv=args(f,command,target,node??undefined);
  const raw=execFileSync(process.execPath,[...process.execArgv,path.join(project,'impl/cli/src/cli/main.ts'),...argv],{encoding:'utf8'});
  assert.equal(JSON.parse(raw).result,'pass');
  const view=selectReconciledArtifacts(f.compiled,node?[node]:null),n=nativeExisting(target,{...f.compiled.resolved,artifacts:view.artifacts});
  const plain={id:'order-one',amount:'4',money:{amount:'4'},mode:{variant:'On'}},trace:string[]=[];
  const dependency={store:{begin:async()=>({read:async()=>{throw Error('no read');},rollback:async()=>{trace.push('rollback');},commit:async()=>{trace.push('commit');return {status:'committed'};}})}};
  const result=await n.load('/workflows/flow.ts').workflowFlow({order:plain,notice:{occurrence:{'event-id':'event-one'},occurredAt:'2026-09-09',payload:{}}},{workflow_execution_id:'run-one',failure_occurrence_id:'failure-one'},{'alpha:post':dependency});
  assert.equal(result.status,'succeeded');assert.deepEqual(trace,['commit']);
  if(!node)assert.equal(n.load('/alpha/src/domain/calculations/total.ts').calculateTotal({}),18446744073709551615n);
 }
});
test('malformed selections and unsupported combinations reject before output or source mutation',t=>{
 const f=prepared(t),target=path.join(f.temp,'never-created'),original=canonicalJson(f.graph);
 const attempt=(argv:string[])=>{const result=cli(argv);assert.notEqual(result.code,0,JSON.stringify(argv));assert.equal(fs.existsSync(target),false);return result;};
 const baseArgs=args(f,'build',target);
 for(const suffix of [['--compilation-selection',f.file],['--unknown','value'],['--output-layout','domainspec.application-layout/unknown']])attempt([...baseArgs,...suffix]);
 attempt(baseArgs.slice(0,-2).concat(['--target-root']));
 attempt(baseArgs.map(s=>s==='typescript'?'rust':s));
 // Selected stronger verification requires explicit validator locations.
 attempt(['verify-project',f.source,'--target-root',target,'--compilation-selection',f.file]);
 attempt(['instantiate-project',f.source,'--languages','typescript,python','--target-root',target,'--compilation-selection',f.file]);
 attempt([...args(f,'instantiate',target,'alpha:flow'),'--integration-profile','x','--integration-binding-set','y']);
 attempt([...args(f,'verify',target),'--node','alpha:flow','--node','alpha:post']);
 for(const text of ['{',JSON.stringify({...f.selection,profile_id:'unknown'}),JSON.stringify({...f.selection,operations:[]})]){fs.writeFileSync(f.file,text);assert.equal(attempt(baseArgs).code,22);}
 fs.writeFileSync(f.file,JSON.stringify(f.selection));const link=path.join(f.temp,'linked.json');fs.symlinkSync(f.file,link);
 assert.equal(attempt(baseArgs.map(s=>s===f.file?link:s)).code,22);
 const large=path.join(f.temp,'large.json'),fd=fs.openSync(large,'w');fs.ftruncateSync(fd,8*1024*1024+1);fs.closeSync(fd);
 assert.throws(()=>readReconciledCompilationSelection(large),/bounded regular/);
 assert.equal(canonicalJson(loadCompiledProjectGraph(f.source)),original);
});
test('currentness rejects changed bytes, receipts, links, extra entries and wrong views without writing',t=>{
 const f=prepared(t),target=path.join(f.temp,'published');publishReconciledProject(f.compiled,target);
 const artifact=f.compiled.resolved.artifacts[0]!,file=path.join(target,artifact.relative_path),receiptFile=path.join(target,RECONCILED_OUTPUT_RECEIPT_PATH),receiptBytes=fs.readFileSync(receiptFile);
 const check=()=>{const before=fs.readFileSync(receiptFile);assert.equal(verifyReconciledProject(f.compiled,target).result,'fail');assert.deepEqual(fs.readFileSync(receiptFile),before);};
 fs.appendFileSync(file,' ');check();fs.writeFileSync(file,artifact.content);
 fs.appendFileSync(receiptFile,' ');check();fs.writeFileSync(receiptFile,receiptBytes);
 fs.mkdirSync(path.join(target,'extra'));check();fs.rmdirSync(path.join(target,'extra'));
 fs.unlinkSync(file);const outside=path.join(f.temp,'outside.ts');fs.writeFileSync(outside,artifact.content);fs.symlinkSync(outside,file);check();fs.unlinkSync(file);fs.writeFileSync(file,artifact.content);
 fs.symlinkSync(target,path.join(f.temp,'alias'));assert.equal(verifyReconciledProject(f.compiled,path.join(f.temp,'alias')).result,'fail');
 assert.equal(verifyReconciledProject(f.compiled,target).result,'pass');assert.equal(verifyReconciledProject(f.compiled,path.join(f.temp,'missing')).result,'fail');
 assert.throws(()=>publishReconciledProject(structuredClone(f.compiled),path.join(f.temp,'forged')),/registered reconciled/);
});
test('existing targets and output failures preserve owner files and clean only own staging',t=>{
 const f=prepared(t),target=path.join(f.temp,'owned');fs.mkdirSync(target);fs.writeFileSync(path.join(target,'keep'),'owner');
 assert.throws(()=>publishReconciledProject(f.compiled,target),/already exists/);assert.equal(fs.readFileSync(path.join(target,'keep'),'utf8'),'owner');
 const dangling=path.join(f.temp,'dangling');fs.symlinkSync(path.join(f.temp,'absent'),dangling);assert.throws(()=>publishReconciledProject(f.compiled,dangling),/already exists/);assert.ok(fs.lstatSync(dangling).isSymbolicLink());
 const parent=path.join(f.temp,'alias-parent');fs.symlinkSync(f.temp,parent);assert.throws(()=>publishReconciledProject(f.compiled,path.join(parent,'new')),/real directory/);
 const original=fs.writeFileSync;
 const isStageFile=(file:any)=>typeof file==='number'&&fs.readlinkSync('/proc/self/fd/'+file).includes('.domainspec-reconciled-');
 (fs as any).writeFileSync=(file:any,...rest:any[])=>{if(isStageFile(file))throw Error('injected write failure');return (original as any)(file,...rest);};
 try{assert.throws(()=>publishReconciledProject(f.compiled,path.join(f.temp,'failed')),/injected write failure/);}finally{fs.writeFileSync=original;}
 assert.equal(fs.existsSync(path.join(f.temp,'failed')),false);assert.deepEqual(fs.readdirSync(f.temp).filter(s=>s.startsWith('.domainspec-reconciled-')),[]);assert.equal(fs.readFileSync(path.join(target,'keep'),'utf8'),'owner');
 const appeared=path.join(f.temp,'appeared');let once=false;
 (fs as any).writeFileSync=(file:any,...rest:any[])=>{
  if(!once&&isStageFile(file)){once=true;fs.mkdirSync(appeared);original(path.join(appeared,'keep'),'concurrent-owner');}
  return (original as any)(file,...rest);
 };
 try{assert.throws(()=>publishReconciledProject(f.compiled,appeared),/appeared during publication/);}finally{fs.writeFileSync=original;}
 assert.equal(fs.readFileSync(path.join(appeared,'keep'),'utf8'),'concurrent-owner');assert.deepEqual(fs.readdirSync(f.temp).filter(s=>s.startsWith('.domainspec-reconciled-')),[]);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
