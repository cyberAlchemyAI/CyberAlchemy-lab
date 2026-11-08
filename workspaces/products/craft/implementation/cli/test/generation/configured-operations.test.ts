import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings,OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {planConfiguredOperations,CONFIGURED_OPERATION_VERSION} from '../../src/generation/configured-operations.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const rules={configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
  rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const sources={operation_contract:bytes(base+'operation-generation-contract.json'),factory_contract:bytes(base+'factory-structured-rule-contract.json'),enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts'),rules,
  events:{configuration:rules.configuration,base:rules.base,typescript:rules.typescript,event_contract:bytes(base+'event-generation-contract.json')}};
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
    const action=compileOperationActionBindings(graph,boundary,fields,bindings,actionSource),selection:any={schema_version:CONFIGURED_OPERATION_VERSION,language:'typescript',module_root:'application',actions:[action],factories};
    return {graph,boundary,fields,action,selection,plan:()=>planConfiguredOperations(graph,boundary,fields,selection,sources)};
  };
  return {temp,source,write,node,edge,save,bindings,factories,compile,...compile()};
}
const account=(balance:any='100')=>({id:'account-a',balance,detail:{amount:'2'},labels:['b','a'],status:{variant:'Ready'},choice:{variant:'Some',payload:{amount:'3'}}});
const input=()=>({account_id:'account-a',amount:'10',replacement:account('90'),receipt:{id:'receipt-a',amount:'10'},response:'accepted',posted_input:{occurrence:{'occurrence-id':'one'},payload:{'account-id':'account-a',amount:'10'}},audit_input:{occurrence:{'occurrence-id':'two'},payload:{'account-id':'account-a',amount:'10'}}});
const frozen=(v:any):void=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));Object.values(v).forEach(frozen);}};
function referenceStore(options:any={}){
  let records=new Map<string,any>([['commerce:account/account-a',account()]]),outbox:any[]=[],revision=0;const trace:string[]=[],batches:any[]=[];
  const store={begin:async()=>{
    trace.push('begin');if(options.begin)throw Error('begin');const snapshot=new Map(records),readRevision=revision;let terminal=false;
    return {read:async(r:any)=>{trace.push('read:'+r.slot);assert.equal(terminal,false);if(options.read)throw Error('read');return options.missing?null:options.wrongIdentity?{...account(),id:'other'}:snapshot.get(r.target+'/'+r.key)??null;},
      rollback:async()=>{trace.push('rollback');assert.equal(terminal,false);terminal=true;if(options.rollback)throw Error('rollback');},
      commit:async(batch:any)=>{
        trace.push('commit');assert.equal(terminal,false);terminal=true;frozen(batch);batches.push(batch);if(readRevision!==revision)return {status:'rejected'};const draft=new Map(records),events=[...outbox];
        for(const w of batch.writes){const key=w.target+'/'+w.value.id;if(w.mode==='create'&&draft.has(key)||w.mode!=='create'&&!draft.has(key))return {status:'rejected'};if(w.mode==='delete')draft.delete(key);else draft.set(key,w.value);}
        for(const e of batch.events)events.push(e);
        if(options.commit==='reject')return {status:'rejected'};if(options.commit==='throw-before')throw Error('unknown commit');
        records=draft;outbox=events;revision++;
        if(options.commit==='throw-after')throw Error('lost acknowledgement');if(options.commit==='invalid')return {status:'nonsense'};
        if(options.commit==='indeterminate')return {status:'indeterminate'};
        if(options.settle)await options.settle;return {status:'committed'};
      }};
  }};
  return {store,trace,batches,records:()=>records,outbox:()=>outbox};
}
function native(root:string,plan:any){
  for(const a of plan.artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
  const chain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(chain.container_image);
  const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
  const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map((a:any)=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
  const m=plan.modules[0],js=path.join(root,'js',m.relative_path.replace(/\.ts$/,'.js')),load=()=>createRequire(import.meta.url)(js)[m.callable];
  return {root,plan,compile,load,docker,image,js,module:m};
}
function observer(f:ReturnType<typeof fixture>,n:ReturnType<typeof native>){
  const bindingsPath=path.join(n.root,'authored-bindings.json'),config=path.join(n.root,'tsconfig.json'),expected=path.join(n.root,'expected.json');
  fs.writeFileSync(bindingsPath,JSON.stringify(f.bindings));
  fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'commonjs'},files:n.plan.artifacts.map((a:any)=>a.relative_path)}));
  fs.writeFileSync(expected,JSON.stringify([{relative_path:n.module.relative_path,provider_path:n.module.provider_path,source_path:path.join(f.source,'specs/commerce/nodes/post.json'),bindings_path:bindingsPath,node_paths:fs.readdirSync(path.join(f.source,'specs/commerce/nodes')).map(p=>path.join(f.source,'specs/commerce/nodes',p))}]));
  const args=[...n.docker.slice(0,-1),'--mount','type=bind,source='+f.source+',target='+f.source+',readonly','--mount','type=bind,source='+path.join(project,'impl/cli/tools/observe-configured-operations.mjs')+',target=/observer.mjs,readonly',n.image,'node','/observer.mjs',config,expected];
  try{return JSON.parse(execFileSync('docker',args,{encoding:'utf8'}));}catch(e:any){if(e.stdout)return JSON.parse(e.stdout);throw e;}
}
function mutatePlan(plan:any,change:(content:string)=>string){
  const copy=structuredClone(plan),m=copy.modules[0],provider=copy.artifacts.find((a:any)=>a.relative_path===m.provider_path),wrapper=copy.artifacts.find((a:any)=>a.relative_path===m.relative_path),before=provider.content;
  provider.content=change(before);assert.notEqual(provider.content,before);provider.sha256=sha256(provider.content);provider.size_bytes=Buffer.byteLength(provider.content);
  const oldHash=m.descriptor.descriptor_sha256,oldProvider=m.descriptor.provider.sha256;m.descriptor.provider.sha256=provider.sha256;
  const {descriptor_sha256,...body}=m.descriptor;m.descriptor.descriptor_sha256=sha256(canonicalJson(body));
  wrapper.content=wrapper.content.replace(oldProvider,provider.sha256).replace(oldHash,m.descriptor.descriptor_sha256);wrapper.sha256=sha256(wrapper.content);wrapper.size_bytes=Buffer.byteLength(wrapper.content);return copy;
}
const dependencies=(s:any,calls:string[]=[])=>({store:s.store,clocks:{'posted-fact':()=>{calls.push('posted');return '2026-09-09T12:00:00Z';},'audit-fact':()=>{calls.push('audit');return '2026-09-09T12:00:01Z';}}});

test('Workflow settlement bridge agrees with real generated Operation outcomes and committed store state', async t => {
  const {inspectOperationSettlement} = await import('../../src/typed-operation/workflow-outcomes.ts');
  const f = fixture(t), run = native(path.join(f.temp, 'workflow-settlements'), f.plan()).load();
  const cases: any[] = [
    {expected: 'committed', durable: true},
    {options: {commit: 'reject'}, expected: 'not-committed', durable: false},
    ...['throw-before', 'throw-after', 'invalid', 'indeterminate'].map(commit => ({options: {commit}, expected: 'indeterminate', durable: commit !== 'throw-before'})),
    {options: {begin: true}, expected: 'not-committed', durable: false},
    {options: {read: true, rollback: true}, expected: 'not-committed', durable: false, cleanup: true},
    {edit: (v: any) => v.amount = '100', expected: 'not-committed', durable: false},
    {edit: (v: any) => v.amount = '-1', expected: 'not-committed', durable: false},
    {edit: (v: any) => v.replacement.balance = '0', expected: 'not-committed', durable: false},
    {edit: (v: any) => v.posted_input.payload.amount = 'bad', expected: 'not-committed', durable: false},
  ];
  for (const c of cases) {
    const store = referenceStore(c.options), parameters = input(); c.edit?.(parameters);
    const outcome = await run(parameters, dependencies(store));
    const settlement = inspectOperationSettlement(outcome, f.action.failure_continuation);
    assert.equal(settlement.commit_status, c.expected, JSON.stringify(c));
    assert.equal(settlement.origin, 'returned');
    assert.equal(store.outbox().length, c.durable ? 2 : 0);
    assert.equal(settlement.result_validation, 'not-performed');
    if (c.cleanup) assert.equal(settlement.cleanup_failed, true);
    if (c.options?.commit) {assert.equal(store.trace.filter(x => x === 'commit').length, 1); assert(!store.trace.includes('rollback'));}
  }
});

test('Operation planner preserves checked source, dependency identities, native actions and frozen defaults',async t=>{
  const f=fixture(t),p=f.plan();assert.deepEqual(f.plan(),p);frozen(p);assert.equal(p.modules[0]!.descriptor.provider_durability_claim,false);assert.equal(p.modules[0]!.descriptor.publication,false);
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));assert.equal(new Set(p.artifacts.map(a=>a.relative_path)).size,p.artifacts.length);
  const n=native(path.join(f.temp,'native'),p),run=n.load(),store=referenceStore(),calls:string[]=[];
  const result=await run(input(),dependencies(store,calls));assert.deepEqual(result,{status:'committed',value:'accepted'});frozen(result);
  assert.deepEqual(store.trace,['begin','read:current-account','commit']);assert.deepEqual(calls,['posted','audit']);
  assert.equal(store.records().get('commerce:account/account-a').balance,90n);assert.equal(store.records().get('commerce:receipt/receipt-a').amount,10n);
  assert.equal(store.outbox().length,2);assert.deepEqual(store.outbox().map(e=>e.value.occurrence['occurrence-id']),['one','two']);assert.equal(store.outbox()[0].value.payload.amount,10n);
  fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(f.plan(),p);
});

test('Operation planning rejects forged selections, cross-graph bindings, missing validators and unsafe paths',t=>{
  const f=fixture(t);let calls=0;
  for(const selection of [{...f.selection,language:'rust'},{...f.selection,module_root:'../escape'},{...f.selection,module_root:'app\n'},{...f.selection,actions:[structuredClone(f.action)]},{...f.selection,actions:[f.action,f.action]},{...f.selection,factories:[]},{...f.selection,extra:true}])assert.throws(()=>planConfiguredOperations(f.graph,f.boundary,f.fields,selection,sources));
  const hostile={...f.selection,get actions(){calls++;return [f.action];}};assert.throws(()=>planConfiguredOperations(f.graph,f.boundary,f.fields,hostile,sources));assert.equal(calls,0);
  assert.throws(()=>planConfiguredOperations(f.graph,f.boundary,f.fields,f.selection,{...sources,operation_contract:sources.operation_contract+' '}));
  assert.throws(()=>planConfiguredOperations(f.graph,f.boundary,f.fields,f.selection,{...sources,events:{...sources.events,base:'{}'}}));
  const changed=read(path.join(f.source,'specs/commerce/nodes/post.json'));changed.body.description='other evidence';f.write('specs/commerce/nodes/post.json',changed);const other=f.compile();
  assert.throws(()=>planConfiguredOperations(other.graph,other.boundary,other.fields,f.selection,sources));
});

test('Declared guards, read failures, owned invariants and Event failures cannot partially write',async t=>{
  const f=fixture(t),run=native(path.join(f.temp,'failures'),f.plan()).load();
  const cases:any[]=[{edit:(v:any)=>v.amount='100',status:'rejected',stage:'guard'},{edit:(v:any)=>v.receipt.amount='11',status:'rejected',stage:'guard'},
    {edit:(v:any)=>v.replacement.balance='0',status:'failed',stage:'write-validation'},{edit:(v:any)=>v.replacement.detail.amount='0',status:'failed',stage:'write-validation'},
    {edit:(v:any)=>v.replacement.choice.payload.amount='0',status:'failed',stage:'write-validation'},{edit:(v:any)=>v.posted_input.payload.amount='bad',status:'failed',stage:'event'},
    {options:{missing:true},status:'failed',stage:'read'},{options:{wrongIdentity:true},status:'failed',stage:'read'},{options:{read:true},status:'failed',stage:'read'}];
  for(const c of cases){const store=referenceStore(c.options),calls:string[]=[],v=input();c.edit?.(v);const r=await run(v,dependencies(store,calls));assert.equal(r.status,c.status);assert.equal(r.stage,c.stage);assert.equal(r.continuation,'return-post-error');assert.equal(store.batches.length,0);assert.equal(store.outbox().length,0);assert.equal(store.records().get('commerce:account/account-a').balance,'100');assert.equal(store.trace.filter(x=>x==='rollback').length,1);if(c.stage!=='event')assert.equal(calls.length,0);}
});

test('Commit rejection, exceptions and unknown acknowledgements retain distinct outcomes without retry',async t=>{
  const f=fixture(t),run=native(path.join(f.temp,'commit'),f.plan()).load();
  for(const mode of ['reject','throw-before','throw-after','invalid','indeterminate']){
    const store=referenceStore({commit:mode}),result=await run(input(),dependencies(store));assert.equal(result.status,mode==='reject'?'rejected':'indeterminate');
    assert.equal(store.trace.filter(x=>x==='commit').length,1);assert.equal(store.trace.includes('rollback'),false);
    assert.equal(store.outbox().length,['reject','throw-before'].includes(mode)?0:2);
  }
  const noBegin=referenceStore({begin:true}),failed=await run(input(),dependencies(noBegin));assert.equal(failed.stage,'begin');assert.deepEqual(noBegin.trace,['begin']);
  const missingClock=referenceStore(),clockFailure=await run(input(),{store:missingClock.store,clocks:{}});assert.equal(clockFailure.stage,'begin');assert.deepEqual(missingClock.trace,[]);
  const cleanup=referenceStore({missing:true,rollback:true}),r=await run(input(),dependencies(cleanup));assert.equal(r.status,'failed');assert.equal(r.cleanupFailed,true);assert.deepEqual(cleanup.trace,['begin','read:current-account','rollback']);
  const atomic=referenceStore();assert.equal((await run(input(),dependencies(atomic))).status,'committed');const conflict=input();conflict.replacement.balance='80';assert.equal((await run(conflict,dependencies(atomic))).status,'rejected');assert.equal(atomic.records().get('commerce:account/account-a').balance,90n);assert.equal(atomic.outbox().length,2,'second-write conflict leaves first write and outbox unchanged');
  const concurrent=referenceStore(),left=input(),right=input();right.receipt.id='receipt-b';right.replacement.balance='80';
  const outcomes=await Promise.all([run(left,dependencies(concurrent)),run(right,dependencies(concurrent))]);assert.deepEqual(outcomes.map(o=>o.status).sort(),['committed','rejected']);assert.equal(concurrent.records().size,2);assert.equal(concurrent.outbox().length,2,'optimistic reference provider rejects stale-read commit without automatic replay');
});

test('Inputs are captured before suspension, hostile data stays inert and commit settlement is awaited',async t=>{
  const f=fixture(t),run=native(path.join(f.temp,'capture'),f.plan()).load();let settle!:()=>void;const waiting=new Promise<void>(r=>{settle=r;}),store=referenceStore({settle:waiting}),v=input();
  let done=false;const promise=run(v,dependencies(store)).then((r:any)=>{done=true;return r;});v.response='changed';v.replacement.balance='1';v.posted_input.payload.amount='2';
  await new Promise(resolve=>setImmediate(resolve));assert.equal(done,false);assert.equal(store.batches[0].writes[0].value.balance,90n);assert.equal(store.batches[0].events[0].value.payload.amount,10n);settle();assert.equal((await promise).value,'accepted');
  let getters=0;for(const mutate of [(x:any)=>Object.defineProperty(x.replacement,'balance',{enumerable:true,get(){getters++;return 90;}}),(x:any)=>x.amount=Number.MAX_SAFE_INTEGER+1,(x:any)=>x.extra=true,(x:any)=>x.replacement.labels=new Array(4294967295),(x:any)=>x.posted_input.payload.amount={valueOf(){getters++;return 10;}},(x:any)=>x.response=x]){
    const s=referenceStore(),bad=input();mutate(bad);const result=await run(bad,dependencies(s));assert.equal(result.status,'failed');assert.equal(result.stage,'input');assert.deepEqual(s.trace,[]);
  }assert.equal(getters,0);
});

test('Independent native observation rejects compiling semantic mutations even with refreshed descriptor hashes',async t=>{
  const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'observed'),p);assert.deepEqual(observer(f,n).errors,[]);
  const mutations=[
    {name:'missing-guard',change:(s:string)=>s.replace(/^    if\(!guard0.*\n/m,'')},
    {name:'snapshot-write-substitution',change:(s:string)=>s.replace(/(const write0=\w+\.normalize\()p2(\);)/,'$1read0$2')},
    {name:'missing-owned-validation',change:(s:string)=>s.replace(/^    own\d+\(write0\);\n/m,'')},
    {name:'wrong-event-input',change:(s:string)=>s.replace('captured["audit_input"] as Event0Input','captured["posted_input"] as Event0Input')},
    {name:'missing-read-identity',change:(s:string)=>s.replace(/^    if\(.*READ_IDENTITY_MISMATCH.*\n/m,'')},
    {name:'uncaptured-input',change:(s:string)=>s.replace('captureData(parameters) as Record<string,unknown>','parameters as unknown as Record<string,unknown>')},
    {name:'wrong-batch-mode',change:(s:string)=>s.replaceAll('mode:"replace"','mode:"create"')},
    {name:'false-uncertain-success',change:(s:string)=>s.replace('return failure("indeterminate",d.status!.value===','return failure("rejected",d.status!.value===')},
    {name:'unawaited-commit',change:(s:string)=>s.replace('const receipt=await transaction.commit(batch);','const receipt=transaction.commit(batch);')},
  ];
  for(const m of mutations){const changed=mutatePlan(p,m.change),target=native(path.join(f.temp,m.name),changed),result=observer(f,target);assert.equal(result.result,'fail',m.name+':'+JSON.stringify(result));}
  const wrongWrite=native(path.join(f.temp,'witness-write'),mutatePlan(p,mutations[1]!.change)).load(),store=referenceStore();assert.equal((await wrongWrite(input(),dependencies(store))).status,'committed');assert.equal(store.records().get('commerce:account/account-a').balance,100n,'independent runtime exposes live-read substitution');
  const noValidation=native(path.join(f.temp,'witness-validation'),mutatePlan(p,mutations[2]!.change)).load(),bad=input(),s=referenceStore();bad.replacement.detail.amount='0';assert.equal((await noValidation(bad,dependencies(s))).status,'committed','compiling validation bypass wrongly accepts invalid Value Object');
  const noGuard=native(path.join(f.temp,'witness-guard'),mutatePlan(p,mutations[0]!.change)).load(),denied=input(),g=referenceStore();denied.amount='100';denied.receipt.amount='100';assert.equal((await noGuard(denied,dependencies(g))).status,'committed','compiling Rule omission wrongly accepts rejected action');
});

test('Native Operations preserve composite identities and nested optional list set and named-sum values',async t=>{
  const f=fixture(t),node=read(path.join(f.source,'specs/commerce/nodes/account.json')),properties=node.body.typed_contract.properties;
  const sum=properties.find((p:any)=>p.name==='choice').type;
  f.node('resolution','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-RESOLUTION',variants:sum.variants.map((v:any)=>({...v,ontology_variant:v.ontology_variant.replace('CHOICE','RESOLUTION')}))}});
  properties.find((p:any)=>p.name==='id').type=named('detail');
  for(const [name,kind]of [['maybe','optional'],['items','list'],['unique','set']])properties.push({name,ontology_property:'FIXTURE-ACCOUNT#'+name,type:{kind,element:named('detail')},identity:false,cardinality:kind==='optional'?'optional':kind==='list'?'many':'many-unique',meaning:name});
  properties.push({name:'resolution',ontology_property:'FIXTURE-ACCOUNT#resolution',type:named('resolution'),identity:false,cardinality:'one',meaning:'resolution'});node.body.fields=properties.map((p:any)=>p.name);
  f.write('specs/commerce/nodes/account.json',node);
  // Event references intentionally retain their scalar wire contract. This
  // case exercises the Operation store's composite Entity identity without
  // implicitly widening the separate Event reference protocol.
  const posted=read(path.join(f.source,'specs/commerce/nodes/posted.json'));
  posted.body.payload.find((field:any)=>field.field_id==='account-id').type_ref={kind:'primitive',name:'string'};
  f.write('specs/commerce/nodes/posted.json',posted);f.bindings.inputs[0].type=named('detail');f.bindings.result={type:named('account'),value:at('replacement')};f.save();
  const c=f.compile(),n=native(path.join(f.temp,'nested'),c.plan()),run=n.load(),v:any=input();
  const extra={id:{amount:'2'},maybe:null,items:[{amount:'4'},{amount:'4'}],unique:[{amount:'5'},{amount:'6'}],resolution:{variant:'Some',payload:{amount:'18446744073709551615'}}};
  v.account_id={amount:'2'};v.replacement={...v.replacement,...extra};let batch:any,reads=0;
  const store={begin:async()=>({read:async(request:any)=>{reads++;assert.deepEqual(request.key,{amount:2n});frozen(request);return {...account(),...extra};},rollback:async()=>{},commit:async(value:any)=>{batch=value;return {status:'committed'};}})};
  const result=await run(v,{...dependencies({store}),store});assert.equal(result.status,'committed',result.code+':'+result.stage);assert.equal(reads,1);assert.equal(result.value.id.amount,2n);assert.equal(result.value.maybe,null);assert.equal(result.value.items.length,2);assert.equal(result.value.unique.length,2);assert.equal(result.value.resolution.payload.amount,18446744073709551615n);frozen(result);frozen(batch);
  const duplicate=structuredClone(v);duplicate.replacement.unique[1]=duplicate.replacement.unique[0];assert.equal((await run(duplicate,{...dependencies({store}),store})).stage,'input');assert.equal(reads,1);
  const bad=structuredClone(v);bad.replacement.items[1].amount='0';batch=null;assert.equal((await run(bad,{...dependencies({store}),store})).stage,'write-validation');assert.equal(batch,null);
});

test('Generated delete and source-empty action variants keep their declared effects exact',async t=>{
  const deletion=fixture(t);deletion.bindings.writes[0].mode='delete';const del=deletion.compile(),runDelete=native(path.join(deletion.temp,'delete'),del.plan()).load(),s=referenceStore();
  assert.equal((await runDelete(input(),dependencies(s))).status,'committed');assert.equal(s.records().has('commerce:account/account-a'),false);assert.equal(s.outbox().length,2);
  for(const eventOnly of [true,false]){
    const f=fixture(t),node=read(path.join(f.source,'specs/commerce/nodes/post.json')),index=read(path.join(f.source,'specs/commerce/feature.json'));
    node.body.writes=[];f.bindings.writes=[];index.edges=index.edges.filter((e:string)=>e!=='post-creates-receipt');
    if(!eventOnly){node.body.effects=[];f.bindings.events=[];f.bindings.result={type:named('account'),value:at('replacement')};index.edges=index.edges.filter((e:string)=>e!=='post-produces-posted');}
    f.write('specs/commerce/nodes/post.json',node);f.write('specs/commerce/feature.json',index);
    const c=f.compile(),n=native(path.join(f.temp,eventOnly?'events-only':'guard-only'),c.plan()),store=referenceStore(),v:any=input();if(!eventOnly){delete v.posted_input;delete v.audit_input;}
    const result=await n.load()(v,eventOnly?dependencies(store):{store:store.store});assert.equal(result.status,'committed');assert.equal(store.batches[0].writes.length,0);assert.equal(store.outbox().length,eventOnly?2:0);assert.equal(store.records().size,1);
    if(!eventOnly){const bad=structuredClone(v),fresh=referenceStore();bad.replacement.detail.amount='0';const rejected=await n.load()(bad,{store:fresh.store});assert.equal(rejected.stage,'result');assert.equal(rejected.status,'failed');assert.equal(fresh.batches.length,0,'invalid returned domain value is rejected before commit');}
  }
});

test('Native declarations expose typed immutable requests batches events and explicit outcomes',t=>{
  const f=fixture(t),p=f.plan(),m=p.modules[0]!,consumer=`import {execute} from './${m.provider_path.replace(/\.ts$/,'.js')}';
import type {OperationInput,OperationDependencies,OperationBatch,Transaction,EventIntent} from './${m.provider_path.replace(/\.ts$/,'.js')}';
declare const input:OperationInput;declare const dependencies:OperationDependencies;declare const batch:OperationBatch;declare const transaction:Transaction;declare const event:EventIntent;
// @ts-expect-error immutable authored input
input.replacement.balance=0n;
// @ts-expect-error immutable prepared batch
batch.writes.push(batch.writes[0]!);
// @ts-expect-error read identity is String, not UInt64
transaction.read({slot:'current-account',target:'commerce:account',key:1n});
// @ts-expect-error Event integers are exact bigint after construction
const amount:number=event.value.payload['amount'];
// @ts-expect-error unacknowledged commit is not a terminal receipt
const badCommit:Transaction['commit']=async()=>{};
execute(input,dependencies).then(outcome=>{if(outcome.status==='committed'){const response:string=outcome.value;void response;}else{
  // @ts-expect-error failure cannot supply a committed value
  const value=outcome.value;void value;
}});
`;
  native(path.join(f.temp,'declarations'),{...p,artifacts:[...p.artifacts,{relative_path:'consumer.ts',content:consumer,sha256:sha256(consumer),size_bytes:Buffer.byteLength(consumer)}]});
});

test('Changed declared Rule and Event sources causally change bound Operation behavior',async t=>{
  const f=fixture(t),baseline=f.plan(),rulePath='specs/commerce/nodes/can-post.json',eventPath='specs/commerce/nodes/posted.json',original=read(path.join(f.source,rulePath));
  const changed=structuredClone(original);[changed.body.typed_contract.expression.left,changed.body.typed_contract.expression.right]=[changed.body.typed_contract.expression.right,changed.body.typed_contract.expression.left];f.write(rulePath,changed);
  const ruled=f.compile().plan();assert.notEqual(ruled.plan_sha256,baseline.plan_sha256);assert.notEqual(ruled.modules[0]!.descriptor.rule_plan_sha256,baseline.modules[0]!.descriptor.rule_plan_sha256);
  const guarded=native(path.join(f.temp,'changed-rule'),ruled).load(),store=referenceStore();assert.equal((await guarded(input(),dependencies(store))).status,'rejected');assert.equal(store.outbox().length,0);
  f.write(rulePath,original);const event=read(path.join(f.source,eventPath));event.body.version='2';f.write(eventPath,event);
  const eventPlan=f.compile().plan();assert.notEqual(eventPlan.modules[0]!.descriptor.event_plan_sha256,baseline.modules[0]!.descriptor.event_plan_sha256);
  const updated=native(path.join(f.temp,'changed-event'),eventPlan).load(),current=referenceStore();assert.equal((await updated(input(),dependencies(current))).status,'committed');assert.equal(current.outbox()[0].value.version,'2');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
