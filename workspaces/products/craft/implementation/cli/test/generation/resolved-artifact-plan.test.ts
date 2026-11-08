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
import {getReconciledSourceCapsule,RECONCILED_SOURCE_CAPSULE_SHA256} from '../../src/generation/reconciled-sources.ts';
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

test('joins all thirteen native metatypes against the source-fresh v2 baseline without source mutation',t=>{
  const f=allTypesFixture(t),before=canonicalJson(f.graph),p=f.plan();
  // Current-contract successor, not reproduction of the unavailable R07 source state.
  const fixtureBytes=bytes('impl/cli/test/generation/fixtures/resolved-artifact-baseline.v2.json');
  assert.equal(sha256(fixtureBytes),'7812ef2fa68f65f3097f08e69da6d4190ad41858ce8afcdb32c5afd29cc86fae','versioned fixture must not be caller-resealed');
  const baseline=JSON.parse(fixtureBytes);
  assert.deepEqual(Object.keys(baseline).sort(),['schema_version','fixture_prefix_sha256','configuration_sha256','capsule_sha256','metatype_count','artifact_count','artifacts_sha256','plan_sha256','graph_sha256','boundary_sha256','requests','source_blobs','artifact_rows','historical_record','provenance'].sort());
  assert.equal(baseline.schema_version,'domainspec.test-resolved-artifact-baseline/v2');
  const source=fs.readFileSync(import.meta.filename,'utf8'),first=source.indexOf('\ntest(');
  assert.ok(first>0);assert.equal(sha256(source.slice(0,first+1)),baseline.fixture_prefix_sha256);
  assert.equal(sha256(common.configuration),baseline.configuration_sha256);
  assert.equal(RECONCILED_SOURCE_CAPSULE_SHA256,baseline.capsule_sha256);
  assert.equal(getReconciledSourceCapsule().capsule_sha256,baseline.capsule_sha256);
  assert.equal(baseline.metatype_count,13);assert.equal(new Set(f.graph.nodes.map(n=>n.kind)).size,baseline.metatype_count);
  assert.equal(baseline.artifact_count,34);assert.equal(p.artifacts.length,baseline.artifact_count);
  assert.equal(new Set(baseline.artifact_rows.map((r:any)=>r.relative_path)).size,34);
  for(const row of baseline.artifact_rows)assert.deepEqual(Object.keys(row).sort(),['relative_path','content_sha256','size_bytes','declared_sha256','declared_size_bytes'].sort());
  assert.deepEqual(p.artifacts.map(a=>({relative_path:a.relative_path,content_sha256:sha256(a.content),size_bytes:Buffer.byteLength(a.content),declared_sha256:a.sha256,declared_size_bytes:a.size_bytes})),baseline.artifact_rows);
  assert.equal(sha256(canonicalJson(p.artifacts)),baseline.artifacts_sha256);
  assert.equal(p.plan_sha256,baseline.plan_sha256);assert.equal(p.certificate.graph_sha256,baseline.graph_sha256);assert.equal(p.boundary_sha256,baseline.boundary_sha256);
  assert.deepEqual(p.requests.map(r=>({kind:r.kind,request_sha256:r.request_sha256,selection_sha256:sha256(canonicalJson(r.selection)),child_plan_sha256:r.child_plan_sha256,sources:r.sources})),baseline.requests);
  for(const s of p.source_blobs){assert.equal(sha256(s.content),s.sha256);assert.equal(Buffer.byteLength(s.content),s.size_bytes);}
  assert.deepEqual(p.source_blobs.map(s=>({sha256:s.sha256,size_bytes:s.size_bytes})),baseline.source_blobs);
  assert.equal(new Set(f.graph.nodes.map(n=>n.kind)).size,13);
  assert.equal(canonicalJson(f.graph),before);assertResolvedArtifactPlan(p);
  assert.ok(p.modules.some(m=>m.imports.some(i=>i.specifier==='node:crypto')));
  assert.ok(p.modules.some(m=>m.request_sha256s.length>=3),'shared Rule/Factory artifacts joined');
  assert.deepEqual(planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[...f.requests].reverse()},definition),p);
  for(const request of f.requests){assert.equal(Object.isFrozen(request.selection),false);assert.equal(Object.isFrozen(request.sources),false);}
  fs.renameSync(f.source,path.join(f.temp,'source-moved'));assert.deepEqual(f.plan(),p);
});

test('preserves the exact R07 historical record without claiming source or runtime reproduction',()=>{
  const record=bytes(base+'SHARED-ARTIFACT-PLAN.md');
  assert.equal(sha256(record),'1c106f551e1797f4388901d2cc14088ec26a885ef7687957ebc34fdd143f6d62');
  assert.ok(record.includes('| Pre-change all-13 canonical native artifacts, rechecked after this change | `22a3931472b5663916e76ed0822c67dd1dfd9c9a8738f99a9fdce668d6faad7f` |'));
});

test('native dependencies follow selected generator semantics rather than every canonical relationship',t=>{
  const f=allTypesFixture(t);
  const select=(kind:string)=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:f.requests.filter(r=>r.kind===kind)},definition);
  const policy=select('policies');
  assert.deepEqual([...new Set(policy.modules.flatMap(m=>m.metatypes))].sort(),['Policy','Rule']);
  assert.ok(policy.artifacts.every(a=>!a.relative_path.includes('/operations/')&&!a.relative_path.includes('/calculations/')),'target selection is not invocation');
  const machine=select('state-machines');assert.ok(machine.artifacts.every(a=>!a.relative_path.includes('/events/')),'intent references do not construct Events');
  const query=select('queries');assert.deepEqual([...new Set(query.modules.flatMap(m=>m.metatypes))],['Query'],'projection is not factory construction');
});

test('registered but stale graph and exact-field dependencies cannot enter another checked plan',t=>{
  const f=allTypesFixture(t),other=fixture(t);
  assert.throws(()=>planResolvedArtifacts(other.graph,f.boundary,f.selection,definition),/stale graph or boundary/);
  const fieldRequest=f.requests.find(r=>r.kind==='queries')!;
  assert.throws(()=>planResolvedArtifacts(other.graph,other.boundary,{...other.selection,requests:[fieldRequest]},definition),/stale or nonexact fields/);
  const actionRequest=f.requests.find(r=>r.kind==='operations')!;
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[{...actionRequest,selection:{...actionRequest.selection,actions:structuredClone(actionRequest.selection.actions)}}]},definition),/OPERATION_ACTION_UNVALIDATED/);
});

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

test('complete joined TypeScript project compiles and runs real cross-metatype code in two output roots',async t=>{
  const f=allTypesFixture(t),p=f.plan();
  assert.equal(new Set(p.modules.flatMap(m=>m.metatypes)).size,13);
  for(const name of ['first','second']) {
    const n=nativeJoined(path.join(f.temp,name),p);
    const total=n.load('/alpha/src/domain/calculations/total.ts').calculateTotal({});
    assert.equal(n.load('/calculations/legacy-total.ts').calculateLegacyTotal({amount:'9007199254740993'}),9007199254740993n);
    const answer=n.load('/enums/answer.sum.ts').AnswerValueComponent.create({variant:'Amount',payload:total});
    assert.equal(answer.payload,total);assert.equal(answer.variant,'Amount');
    const plain={id:'order-one',amount:'4',money:{amount:'4'},mode:{variant:'On'}};
    const summary=n.load('/mappings/summary.ts').mappingSummary({order:plain,total});
    assert.deepEqual(summary,{id:'order-one',total:18446744073709551615n});
    assert.deepEqual(n.load('/mappings/adjust.ts').mappingAdjust({total}),{amount:total});
    assert.deepEqual(n.load('/queries/find.ts').queryFind([plain,plain],{}),[{id:'order-one',amount:4n},{id:'order-one',amount:4n}]);
    const choose=n.load('/policies/choose.ts').policyChoose;
    assert.equal(choose({value:true}),'alpha:post');assert.equal(choose({value:false}),'alpha:total');
    const reduce=n.load('/state-machines/lifecycle.ts').transitionLifecycle;
    assert.equal(reduce('draft','alpha:posted',{value:true}).state,'posted');
    assert.equal(reduce('draft','alpha:posted',{value:false}).state,'draft');
    const money=n.load('/value-objects/money.ts').createMoneyFactory().create({amount:'4'}).value;
    const mode=n.load('/enums/mode.component.ts').ModeValueComponent.fromVariant('On');
    const made=n.load('/entities/order.ts').createOrderFactory().create({id:'order-one',amount:'4',money,mode});
    assert.equal(made.ok,true);assert.equal(made.value.fields.amount,4n);
    assert.equal(n.load('/entities/order.ts').createOrderFactory().create({id:'',amount:'4',money,mode}).ok,false);
    const commits:any[]=[];
    const dependency={store:{begin:async()=>({read:async()=>{throw Error('unexpected read');},rollback:async()=>{},commit:async(batch:any)=>{commits.push(batch);return {status:'committed'};}})}};
    const out=await n.load('/workflows/flow.ts').workflowFlow({order:plain,notice:{occurrence:{'event-id':'e-one'},occurredAt:'2026-09-09',payload:{}}},{workflow_execution_id:'execution-one',failure_occurrence_id:'failure-one'},{'alpha:post':dependency});
    assert.equal(out.status,'succeeded');assert.equal(out.value.id,'order-one');assert.equal(commits.length,1);
    assert.equal(out.recovery_bindings,null);
  }
});

const nativeSurfaceObserver = String.raw`
import fs from 'node:fs';
import path from 'node:path';
import {API} from '/opt/node-toolchain/node_modules/typescript/dist/api/sync/api.js';
import {SyntaxKind as K} from '/opt/node-toolchain/node_modules/typescript/dist/ast/index.js';
const config=process.argv[2],settings=JSON.parse(fs.readFileSync(config,'utf8'));
if(JSON.parse(fs.readFileSync('/opt/node-toolchain/node_modules/typescript/package.json','utf8')).version!=='7.0.2')throw Error('native version drift');
const api=new API({cwd:path.dirname(config)});
try {
 const snapshot=api.updateSnapshot({openProjects:[config]}),project=snapshot.getProject(config),result=[];
 if(!project)throw Error('missing project');
 for(const relative_path of settings.files){
  const file=path.resolve(path.dirname(config),relative_path),source=project.program.getSourceFile(file);
  if(!source||project.program.getSyntacticDiagnostics(file).length)throw Error('native syntax failure');
  const imports=[],exports=[];
  for(const s of source.statements){
   const exported=s.modifiers?.some(m=>m.kind===K.ExportKeyword);
   if(s.kind===K.ImportDeclaration){
    const c=s.importClause,b=c?.namedBindings;
    if(c?.name)throw Error('unexpected default import');
    imports.push({specifier:s.moduleSpecifier.text,names:(b?.elements??[]).map(x=>(x.propertyName??x.name).getText()).sort(),namespace:b?.kind===K.NamespaceImport,type_only:c?.isTypeOnly===true,reexport:false});
   }else if(s.kind===K.ExportDeclaration){
    const elements=s.exportClause?.elements;if(!elements)throw Error('unsupported export declaration');
    for(const e of elements)exports.push({name:e.name.getText(),kind:s.isTypeOnly||e.isTypeOnly?'type':'value'});
    if(s.moduleSpecifier)imports.push({specifier:s.moduleSpecifier.text,names:elements.map(e=>(e.propertyName??e.name).getText()).sort(),namespace:false,type_only:s.isTypeOnly===true,reexport:true});
   }else if(exported){
    if(s.kind===K.VariableStatement)for(const d of s.declarationList.declarations)exports.push({name:d.name.getText(),kind:'value'});
    else if([K.InterfaceDeclaration,K.TypeAliasDeclaration,K.FunctionDeclaration,K.ClassDeclaration,K.EnumDeclaration].includes(s.kind))exports.push({name:s.name.getText(),kind:[K.InterfaceDeclaration,K.TypeAliasDeclaration].includes(s.kind)?'type':'value'});
    else throw Error('unknown native export');
   }
  }
  exports.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:a.kind<b.kind?-1:1);
  result.push({relative_path,imports,exports});
 }
 snapshot.dispose();process.stdout.write(JSON.stringify(result));
}finally{api.close();}
`;

test('independent native AST observes complete import/export manifests and catches compiling changes',t=>{
  const f=allTypesFixture(t),p=f.plan(),n=nativeJoined(path.join(f.temp,'observed'),p);
  const config=path.join(n.root,'tsconfig.json'),script=path.join(n.root,'observe.mjs');
  fs.writeFileSync(config,JSON.stringify({compilerOptions:{target:'ES2022',module:'commonjs',strict:true},files:p.artifacts.map(a=>a.relative_path)}));
  fs.writeFileSync(script,nativeSurfaceObserver);
  const observe=()=>JSON.parse(execFileSync('docker',[...n.docker,'node',script,config],{encoding:'utf8'}));
  const expected=p.modules.map(m=>({relative_path:m.relative_path,imports:m.imports.map(({specifier,names,namespace,type_only,reexport})=>({specifier,names,namespace,type_only,reexport})),exports:m.exports}));
  assert.deepEqual(observe(),expected);
  const provider=p.modules.find(m=>m.relative_path.endsWith('/policies/choose.provider.ts'))!;
  const file=path.join(n.root,provider.relative_path),original=fs.readFileSync(file,'utf8');
  fs.writeFileSync(file,original+'\nexport const unexpected = true;\n');n.compile();
  assert.notDeepEqual(observe(),expected,'compiling extra export is visible to independent parser');
  fs.writeFileSync(file,original);
  const imp=provider.imports.find(i=>i.names.includes('ruleAllowed'))!;
  const beta=p.modules.find(m=>m.relative_path.includes('/beta/')&&m.relative_path.endsWith('/rules/allowed.ts'))!;
  let relative=path.posix.relative(path.posix.dirname(provider.relative_path),beta.relative_path).replace(/\.ts$/,'.js');
  if(!relative.startsWith('.'))relative='./'+relative;
  const mutated=original.replace(JSON.stringify(imp.specifier),JSON.stringify(relative));assert.notEqual(mutated,original);
  fs.writeFileSync(file,mutated);n.compile();
  assert.notDeepEqual(observe(),expected,'same-type cross-feature import substitution is visible');
  fs.writeFileSync(file,original);
  const rule=p.modules.find(m=>m.relative_path.includes('/alpha/')&&m.relative_path.endsWith('/rules/allowed.ts'))!;
  const ruleFile=path.join(n.root,rule.relative_path);
  let backwards=path.posix.relative(path.posix.dirname(rule.relative_path),provider.relative_path).replace(/\.ts$/,'.js');
  if(!backwards.startsWith('.'))backwards='./'+backwards;
  fs.appendFileSync(ruleFile,'\nimport * as forbiddenPolicy from '+JSON.stringify(backwards)+';\nvoid forbiddenPolicy;\n');
  n.compile();
  const reversed=observe();
  assert.ok(reversed.find((m:any)=>m.relative_path===rule.relative_path).imports.some((i:any)=>i.specifier===backwards));
  assert.notDeepEqual(reversed,expected,'compiling Rule-to-Policy reverse dependency violates the selected Policy-to-Rule surface');
});

test('joins real generators without changing bytes; immutable source-pinned deterministic plan survives source removal',t=>{
  const f=fixture(t),p=f.plan();assertResolvedArtifactPlan(p);
  const expected=[...planConfiguredCalculationsV2(f.boundary,f.requests[0].selection,calculationSources).artifacts,...planConfiguredRules(f.graph,f.requests[1].selection,ruleSources).artifacts].sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  assert.deepEqual(p.artifacts,expected);assert.equal(p.modules.length,6);
  assert.deepEqual(f.plan(),p);
  assert.deepEqual(planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[...f.requests].reverse()},definition),p);
  assert.equal(p.plan_sha256,sha256(canonicalJson(Object.fromEntries(Object.entries(p).filter(([k])=>k!=='plan_sha256')))));
  assert.equal(p.source_blobs.filter(s=>s.content===common.typescript).length,1);
  for(const s of p.source_blobs)assert.equal(s.sha256,sha256(s.content));
  assert.ok(Object.isFrozen(p.source_blobs));assert.ok(Object.isFrozen(p.modules[0].exports));
  assert.ok(!Object.isFrozen(f.selection));assert.ok(!Object.isFrozen(f.requests));
  fs.renameSync(f.source,path.join(f.temp,'moved-source'));assert.deepEqual(f.plan(),p);
  const relocated=loadCompiledProjectGraph(path.join(f.temp,'moved-source'));
  const boundary=compileCompositionBoundary(relocated,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:f.selection.graph_sha256},bytes('development/reconciliation-v1/contracts/composition-boundary.json'));
  assert.deepEqual(planResolvedArtifacts(relocated,boundary,f.selection,definition),p);
  assert.equal(p.output_effect,'none');assert.equal(p.authority_effect,'none');
});

test('native project imports both qualified names and preserves exact runtime behavior in two roots',t=>{
  const f=fixture(t),p=f.plan(),toolchain=JSON.parse(fs.readFileSync(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'),'utf8'));
  const image=nativeToolchainImage(toolchain.container_image);
  for(const dir of ['first','second']) {
    const root=path.join(f.temp,dir);fs.mkdirSync(root);
    for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
    const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image,'tsc'];
    assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
    execFileSync('docker',[...args,'--ignoreConfig','--strict','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...p.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});
    const require=createRequire(import.meta.url);
    const total=(feature:string)=>require(path.join(root,'js/application/features/'+feature+'/src/domain/calculations/total.js')).calculateTotal;
    assert.equal(total('alpha')({}),18446744073709551615n);assert.equal(total('beta')({}),7n);
    const rule=require(path.join(root,'js/application/features/alpha/src/domain/rules/allowed.js')).ruleAllowed;
    assert.equal(rule({value:true}),true);assert.equal(rule({value:false}),false);
  }
});

test('rejects forged identities, stale selections, source drift, extra fields and inert-data attacks',t=>{
  const f=fixture(t);
  assert.throws(()=>assertResolvedArtifactPlan(structuredClone(f.plan())),/unregistered/);
  assert.throws(()=>planResolvedArtifacts(structuredClone(f.graph),f.boundary,f.selection,definition));
  assert.throws(()=>planResolvedArtifacts(f.graph,structuredClone(f.boundary),f.selection,definition));
  for(const patch of [{schema_version:'future'},{language:'python'},{layout_version:'future'},{graph_sha256:'stale'},{boundary_sha256:'stale'},{module_root:'other'},{requests:[]},{extra:true}])
    assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,...patch},definition));
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,f.selection,definition+' '),/definition drift/);
  for(const patch of [{kind:'unknown'},{selection:{...f.requests[0].selection,schema_version:'future'}},{sources:{...calculationSources,calculation_contract:calculationSources.calculation_contract+' '}}])
    assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[{...f.requests[0],...patch}]},definition));
  let calls=0;const request={...f.requests[0],get selection(){calls++;return f.requests[0].selection;}};
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[request]},definition));
  const requests:any=[];Object.defineProperty(requests,'0',{enumerable:true,get(){calls++;return f.requests[0];}});
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests},definition));assert.equal(calls,0);
});

test('deduplicates exact shared file bytes but rejects incompatible shared Enum definitions',t=>{
  const f=fixture(t),first=f.requests[1];
  const shared={...first,selection:{...first.selection,roots:['alpha:allowed']}};
  const p=planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[first,shared]},definition);
  assert.equal(p.artifacts.length,2);assert.equal(p.modules.find(m=>m.relative_path.includes('/alpha/'))!.request_sha256s.length,2);
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[first,first]},definition),/duplicate generator/);
  const fields=compileSelectedProjectFields(f.graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:f.selection.graph_sha256,roots:['alpha:mode'],bindings:[]},ruleSources.field_contract);
  const plain:any={kind:'enums',fields,selection:{schema_version:'domainspec.configured-enums-selection/v2-candidate',language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256},sources:{...common,provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts')}};
  const owned:any={kind:'algebraic-enums',fields,selection:{schema_version:'domainspec.configured-algebraic-enums-selection/v1-candidate',language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256,factories:[]},sources:{standalone_contract:bytes(base+'standalone-sum-contract.json'),factories:{...ruleSources,factory_contract:bytes(base+'factory-structured-rule-contract.json'),enum_provider:plain.sources.provider}}};
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[plain,owned]},definition),/conflicting definition/);
  assert.throws(()=>planResolvedArtifacts(f.graph,f.boundary,{...f.selection,requests:[{...plain,fields:structuredClone(fields)}]},definition));
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
