import * as legacy from '../../src/generation/configured-operations.ts';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings,OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {planConfiguredPythonOperations, PYTHON_OPERATION_VERSION} from '../../src/generation/configured-python-operations.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const rules={configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),python:bytes('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const sources={operation_contract:bytes(base+'operation-generation-contract.json'),factory_contract:bytes(base+'factory-structured-rule-contract.json'),rules,
  events:{configuration:rules.configuration,base:rules.base,python:rules.python,event_contract:bytes(base+'event-generation-contract.json')}};
const boundarySource=bytes('development/reconciliation-v1/contracts/composition-boundary.json'),actionSource=bytes(base+'operation-action-contract.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'commerce:'+id});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:any):any=>({op:'literal',type,value});
const arg=(parameter:string,value:any)=>({parameter,value});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operations-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2));};
  const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
  const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',edge_id:id,feature_id:'commerce',relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
  const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters,expression}});
  const property=(id:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+id.toUpperCase()+'#'+name,name,type,identity,meaning:name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
  rule('positive',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','0'),right:at('amount')});
  rule('can-post',[{name:'current',type:named('account')},{name:'amount',type:scalar('UInt64')}],{op:'lt',left:at('amount'),right:at('current','FIXTURE-ACCOUNT#balance')});
  rule('receipt-matches',[{name:'expected',type:scalar('UInt64')},{name:'actual',type:scalar('UInt64')}],{op:'eq',left:at('expected'),right:at('actual')});
  node('detail','Value Object',{fields:['amount'],invariant_refs:['commerce:positive'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-DETAIL',properties:[property('detail','amount',scalar('UInt64'))]}});
  node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
  const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-CHOICE#Some',payload:named('detail')}]};
  const props=[property('account','id',scalar(),true),property('account','balance',scalar('UInt64')),property('account','detail',named('detail')),property('account','labels',{kind:'set',element:scalar()}),property('account','status',named('status')),property('account','choice',choice)];
  node('account','Entity',{fields:props.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ACCOUNT',properties:props}});
  node('receipt','Entity',{fields:['id','amount'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-RECEIPT',properties:[property('receipt','id',scalar(),true),property('receipt','amount',scalar('UInt64'))]}});
  node('posted','Event',{event_type:'posted',version:'1',occurrence_id:{field_id:'occurrence-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'generated',payload:[{field_id:'account-id',type_ref:{kind:'reference',selector:'commerce:account'},required:true},{field_id:'amount',type_ref:{kind:'primitive',name:'integer'},required:true}]});
  node('post','Operation',{reads:['current-account'],writes:['account-state','receipt-state'],effects:['posted-fact','audit-fact'],guard:'can-post',failure_continuation:'return-post-error'});
  edge('post-reads-account','reads','post','account');edge('post-creates-receipt','creates','post','receipt');edge('post-produces-posted','produces','post','posted');edge('can-post-enforces-post','enforces','can-post','post');edge('receipt-matches-enforces-post','enforces','receipt-matches','post');
  const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'native-operations',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
  const bindings:any={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'commerce:post',inputs:[{name:'account_id',type:scalar()},{name:'amount',type:scalar('UInt64')},{name:'replacement',type:named('account')},{name:'receipt',type:named('receipt')},{name:'response',type:scalar()}],
    reads:[{slot:'current-account',target:'commerce:account',parameter:'current',key:at('account_id')}],
    guards:[{selector:'commerce:can-post',arguments:[arg('current',at('current')),arg('amount',at('amount'))]},{selector:'commerce:receipt-matches',arguments:[arg('expected',at('amount')),arg('actual',at('receipt','FIXTURE-RECEIPT#amount'))]}],
    writes:[{slot:'account-state',target:'commerce:account',mode:'replace',value:at('replacement')},{slot:'receipt-state',target:'commerce:receipt',mode:'create',value:at('receipt')}],
    events:[{slot:'posted-fact',target:'commerce:posted',parameter:'posted_input'},{slot:'audit-fact',target:'commerce:posted',parameter:'audit_input'}],result:{type:scalar(),value:at('response')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
  const factories=['account','receipt','detail'].map(id=>({selector:'commerce:'+id,base_validators:[{rule:'commerce:positive',arguments:[{parameter:'amount',field:id==='account'?'balance':'amount'}]}],extensions:[]}));
  const compile=()=>{
    const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundarySource);
    const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:account','commerce:receipt'],bindings:[]},rules.field_contract);
    const action=compileOperationActionBindings(graph,boundary,fields,bindings,actionSource),selection:any={schema_version:PYTHON_OPERATION_VERSION,language:'python',module_root:'application',actions:[action],factories};
    return {graph,boundary,fields,action,selection,plan:()=>planConfiguredPythonOperations(graph,boundary,fields,selection,sources)};
  };
  return {temp,source,write,node,edge,save,bindings,factories,compile,...compile()};
}

function native(root:string, plan:any, scenario='full') {
  for(const a of plan.artifacts) {const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
  return execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'python-operation-runtime.py'),root,plan.modules[0].import_name,plan.modules[0].callable,scenario],{encoding:'utf8',stdio:['pipe','pipe','pipe'],env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
}

function observe(root:string, plan:any, f:ReturnType<typeof fixture>, modules=plan.modules, model=plan.field_compilation_sha256===null?null:f.fields.model) {
  for(const a of plan.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
  const graph=loadCompiledProjectGraph(f.source),module_root=plan.selection.module_root.replaceAll('-','_');
  const excluded=new Set(plan.modules.flatMap((m:any)=>[m.relative_path,m.provider_path]));
  const dependencyPlans=[plan.rule_plan,plan.factory_plan,plan.algebraic_plan,plan.event_plan].filter(Boolean);
  const dependencyArtifacts=new Map(dependencyPlans.flatMap(p=>p.artifacts).map((a:any)=>[a.relative_path,a]));
  for(const a of plan.artifacts)if(a.relative_path.endsWith('/__init__.py'))dependencyArtifacts.set(a.relative_path,{...a,sha256:sha256('')});
  const payload={root,module_root,model,modules,
    actions:Object.fromEntries(plan.selection.actions.map((a:any)=>[a.bindings.selector,a])),
    nodes:Object.fromEntries(graph.nodes.map(n=>[n.selector,{kind:n.kind,body:n.body}])),
    rule_modules:plan.rule_plan.modules,event_modules:plan.event_plan?.modules??[],
    dependencies:[...dependencyArtifacts.values()].filter((a:any)=>!excluded.has(a.relative_path)).map(({relative_path,sha256}:any)=>({relative_path,sha256}))};
  return JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'../../src/verification/python-operation-observer.py')],{input:JSON.stringify(payload),encoding:'utf8',stdio:['pipe','pipe','pipe']}));
}

test('Python Operation executes ordered atomic state/outbox batches and preserves all failure boundaries in two roots',t=>{
  const f=fixture(t);
  for(const module_root of ['application','relocated/kernel']) {
    const plan=planConfiguredPythonOperations(f.graph,f.boundary,f.fields,{...f.selection,module_root},sources);
    assert.match(native(path.join(f.temp,module_root.replaceAll('/','-')),plan),/OPERATION_RUNTIME_OK/);
    assert.equal(observe(path.join(f.temp,'observe-'+module_root.replaceAll('/','-')),plan,f).observed,1);
    assert.equal(plan.modules[0].descriptor.provider_durability_claim,false);
    assert.equal(plan.modules[0].descriptor.publication,false);
    assert.ok(Object.isFrozen(plan));
    for(const a of plan.artifacts) assert.equal(a.sha256,sha256(a.content));
  }
});

test('Python Operation rejects forged/stale inputs, active selections, missing factories and drift without changing legacy selection',t=>{
  const f=fixture(t),build=(selection:any=f.selection,s:any=sources,fields:any=f.fields)=>planConfiguredPythonOperations(f.graph,f.boundary,fields,selection,s);
  assert.throws(()=>build({...f.selection,actions:[structuredClone(f.action)]}),/UNVALIDATED/);
  assert.throws(()=>build({...f.selection,actions:[f.action,f.action]}),/duplicate action/);
  for(const module_root of ['../escape','asyncio','class','typing','con','application/../x']) assert.throws(()=>build({...f.selection,module_root}));
  assert.throws(()=>build({...f.selection,factories:[]}),/binding list|coverage/);
  assert.throws(()=>build(f.selection,{...sources,operation_contract:sources.operation_contract+' '}),/source drift/);
  assert.throws(()=>build(f.selection,{...sources,events:{...sources.events,event_contract:sources.events.event_contract+' '}}),/source drift/);
  assert.throws(()=>build(f.selection,sources,null),/stale/);
  let reads=0;
  const actionList=[f.action];Object.defineProperty(actionList,'0',{get(){reads++;throw Error('active');}});
  assert.throws(()=>build({...f.selection,actions:actionList}),/inert array/);assert.equal(reads,0);
  assert.throws(()=>build({...f.selection,language:'typescript'}),/unsupported selection/);
  const {planConfiguredOperations,CONFIGURED_OPERATION_VERSION}=legacy;
  const tsRules={...rules,typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')};delete (tsRules as any).python;
  const tsSources={...sources,enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts'),rules:tsRules,events:{configuration:rules.configuration,base:rules.base,typescript:tsRules.typescript,event_contract:sources.events.event_contract}};
  const selection={...f.selection,schema_version:CONFIGURED_OPERATION_VERSION,language:'typescript'} as any;
  const before=planConfiguredOperations(f.graph,f.boundary,f.fields,selection,tsSources);
  build();
  assert.deepEqual(planConfiguredOperations(f.graph,f.boundary,f.fields,selection,tsSources),before);
});

test('Compiling Operation behavior mutations are killed by independent native store and outcome assertions',t=>{
  const f=fixture(t),plan=f.plan(),m=plan.modules[0];
  const mutations=[
    ['wrong-result',(s:string)=>s.replace('OperationSuccess("committed", result)','OperationSuccess("committed", "wrong")')],
    ['skip-guard',(s:string)=>s.replace('if not _guard0(', 'if False and not _guard0(')],
    ['skip-factory',(s:string)=>s.replace(/        _own\d+\(write0\)/,'        pass')],
    ['duplicate-commit',(s:string)=>s.replace('receipt = await transaction.commit(batch)','receipt = await transaction.commit(batch)\n        receipt = await transaction.commit(batch)')],
    ['rollback-after-commit',(s:string)=>s.replace('if commit_attempted:\n            return failure','if commit_attempted:\n            await transaction.rollback()\n            return failure')],
    ['false-success',(s:string)=>s.replace('return failure("rejected", "COMMIT_REJECTED")','return OperationSuccess("committed", result)')],
    ['mutable-batch',(s:string)=>s.replace('@_dataclass(frozen=True, slots=True)\nclass OperationBatch','@_dataclass(slots=True)\nclass OperationBatch')],
    ['late-capture',(s:string)=>s.replace('transaction = await dependencies["store"].begin()','transaction = await dependencies["store"].begin()\n        captured = _capture(parameters)')],
    ['wrong-identity',(s:string)=>s.replace('if _fact_type0.key(p5["id"]) != _fact_type0.key(key0):','if False:')],
  ] as const;
  for(const [label,change] of mutations) {
    const copy=structuredClone(plan),provider=copy.artifacts.find(a=>a.relative_path===m.provider_path)!;
    const changed=change(provider.content);assert.notEqual(changed,provider.content,label);provider.content=changed;
    // Compile each mutation first: failure must be behavioral, not syntax rejection.
    execFileSync('/usr/bin/python3',['-c','import ast,sys; compile(ast.parse(sys.stdin.read()), "<mutant>", "exec")'],{input:changed});
    assert.throws(()=>native(path.join(f.temp,'mutant-'+label),copy),undefined,label);
    // Refresh the provider binding, so AST rejection cannot be explained by a
    // stale content hash alone. The observer never executes these modules.
    provider.sha256=sha256(changed);provider.size_bytes=Buffer.byteLength(changed);
    copy.modules[0].descriptor.provider.sha256=provider.sha256;
    assert.throws(()=>observe(path.join(f.temp,'observe-mutant-'+label),copy,f),(error:any)=>{assert.match(String(error.stderr??error),/PYTHON_OPERATION_OBSERVER:Operation semantics\/types\/effects/,label+': observer rejection');return true;},label);
  }
});

test('Python Operation supports minimal scalar contexts, validated record results and dependency-order-independent modules',t=>{
  const f=fixture(t);
  f.node('accept','Operation',{reads:[],writes:[],effects:[],guard:'positive',failure_continuation:'return-accept-error'});
  f.edge('positive-enforces-accept','enforces','positive','accept');f.save();
  const next=f.compile(),bindings={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'commerce:accept',inputs:[{name:'amount',type:scalar('UInt64')}],reads:[],guards:[{selector:'commerce:positive',arguments:[arg('amount',at('amount'))]}],writes:[],events:[],result:{type:scalar('UInt64'),value:at('amount')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
  const scalarAction=compileOperationActionBindings(next.graph,next.boundary,null,bindings,actionSource);
  const minimal=planConfiguredPythonOperations(next.graph,next.boundary,null,{...next.selection,actions:[scalarAction],factories:[]},sources);
  assert.equal(minimal.factory_plan,null);assert.equal(minimal.event_plan,null);
  assert.match(native(path.join(f.temp,'scalar'),minimal,'scalar'),/SCALAR_OPERATION_OK/);
  assert.equal(observe(path.join(f.temp,'observe-scalar'),minimal,f).observed,1);
  assert.throws(()=>planConfiguredPythonOperations(next.graph,next.boundary,null,{...next.selection,actions:[scalarAction],factories:f.factories},sources),/no factories/);
  const sibling=compileOperationActionBindings(next.graph,next.boundary,next.fields,bindings,actionSource);
  const single=next.plan(),combined=planConfiguredPythonOperations(next.graph,next.boundary,next.fields,{...next.selection,actions:[next.action,sibling]},sources);
  const chosen=combined.modules.find(m=>m.selector==='commerce:post')!;
  for(const file of [chosen.relative_path,chosen.provider_path]) assert.deepEqual(combined.artifacts.find(a=>a.relative_path===file),single.artifacts.find(a=>a.relative_path===file));
  assert.equal(observe(path.join(f.temp,'observe-combined'),combined,f).observed,2);
  f.bindings.inputs.push({name:'result_account',type:named('account')});
  f.bindings.result={type:named('account'),value:at('result_account')};
  const record=f.compile().plan();
  assert.match(native(path.join(f.temp,'record'),record,'record'),/RECORD_OPERATION_OK/);
  assert.equal(observe(path.join(f.temp,'observe-record'),record,f).observed,1);
  f.node('decision','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-DECISION',variants:[{name:'None',ontology_variant:'FIXTURE-DECISION#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-DECISION#Some',payload:scalar('UInt64')}]}});f.save();
  const enums=f.compile();
  for(const selector of ['commerce:status','commerce:decision']) {
    const fields=compileSelectedProjectFields(enums.graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:enums.fields.certificate.graph_sha256,roots:[selector],bindings:[]},rules.field_contract);
    const enumBindings={...bindings,inputs:[...bindings.inputs,{name:'choice',type:{kind:'named',selector}}],result:{type:{kind:'named',selector},value:at('choice')}};
    const action=compileOperationActionBindings(enums.graph,enums.boundary,fields,enumBindings,actionSource);
    const plan=planConfiguredPythonOperations(enums.graph,enums.boundary,fields,{...enums.selection,actions:[action],factories:[]},sources);
    assert.equal(plan.factory_plan,null);assert.ok(plan.algebraic_plan);
    assert.match(native(path.join(f.temp,selector.replace(':','-')),plan,selector.endsWith('status')?'plain-enum':'sum-enum'),/ENUM_OPERATION_OK/);
    assert.equal(observe(path.join(f.temp,'observe-'+selector.replace(':','-')),plan,f,plan.modules,fields.model).observed,1);
  }
});

test('Whole-source Operation observer rejects invisible effects, type lies, mutable bindings and dependency tampering',t=>{
  const f=fixture(t),plan=f.plan(),m=plan.modules[0];
  const mutations=[
    ['global-write',(s:string)=>s.replace('async def execute(', '_counter = 0\nasync def execute(').replace('    stage = "input"','    global _counter\n    _counter += 1\n    stage = "input"')],
    ['write-restore',(s:string)=>s.replace('async def execute(', '_counter = 0\nasync def execute(').replace('    stage = "input"','    global _counter\n    prior = _counter\n    _counter += 1\n    _counter = prior\n    stage = "input"')],
    ['wrong-result-type',(s:string)=>s.replace('OperationValue = str','OperationValue = bool')],
    ['hidden-function',(s:string)=>s+'\ndef undeclared_effect():\n    open("not-executed", "w")\n'],
  ] as const;
  for(const [label,change] of mutations){
    const copy=structuredClone(plan),provider=copy.artifacts.find(a=>a.relative_path===m.provider_path)!;
    const content=change(provider.content);assert.notEqual(content,provider.content,label);provider.content=content;
    execFileSync('/usr/bin/python3',['-c','import ast,sys; compile(ast.parse(sys.stdin.read()), "<mutant>", "exec")'],{input:content});
    provider.sha256=sha256(content);copy.modules[0].descriptor.provider.sha256=provider.sha256;
    // These counterexamples preserve the native oracle's visible outcomes.
    // Structural observation supplies distinct evidence, not another happy path.
    assert.match(native(path.join(f.temp,'invisible-'+label),copy),/OPERATION_RUNTIME_OK/);
    assert.throws(()=>observe(path.join(f.temp,'observe-invisible-'+label),copy,f),(error:any)=>/PYTHON_OPERATION_OBSERVER:Operation semantics\/types\/effects/.test(error.stderr),label);
  }
  const mutable=structuredClone(plan),wrapper=mutable.artifacts.find(a=>a.relative_path===m.relative_path)!;
  wrapper.content=wrapper.content.replace('@_dataclass(frozen=True, slots=True)','@_dataclass(slots=True)');
  assert.throws(()=>observe(path.join(f.temp,'observe-mutable'),mutable,f),(error:any)=>/frozen callable\/export boundary/.test(error.stderr));
  const changedDescriptor=structuredClone(plan);changedDescriptor.modules[0].descriptor.bindings=structuredClone(changedDescriptor.modules[0].descriptor.bindings);changedDescriptor.modules[0].descriptor.bindings.result.value={op:'literal',type:'String',value:'other'};
  assert.throws(()=>observe(path.join(f.temp,'observe-descriptor'),changedDescriptor,f),(error:any)=>/checked action binding/.test(error.stderr));
  const support=structuredClone(plan);support.artifacts.find(a=>a.relative_path.endsWith('/runtime/facts.py'))!.content+='\n# changed support\n';
  assert.throws(()=>observe(path.join(f.temp,'observe-support'),support,f),(error:any)=>/reviewed fact support/.test(error.stderr));
  const factory=structuredClone(plan),factoryPath=factory.factory_plan!.modules[0].relative_path,artifact=factory.artifacts.find(a=>a.relative_path===factoryPath)!;
  artifact.content+='\n# changed factory\n';artifact.sha256=sha256(artifact.content);
  assert.throws(()=>observe(path.join(f.temp,'observe-dependency'),factory,f),(error:any)=>/dependency artifact binding/.test(error.stderr));
});
