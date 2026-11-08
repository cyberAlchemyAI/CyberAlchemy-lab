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
function native(root:string,plan:any){
  for(const a of plan.artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
  const chain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(chain.container_image);
  const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
  const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map((a:any)=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
  const m=plan.modules[0],js=path.join(root,'js',m.relative_path.replace(/\.ts$/,'.js')),load=()=>createRequire(import.meta.url)(js)[m.callable];
  return {root,plan,compile,load,docker,image,js,module:m};
}

import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {publicSelection} from '../helpers/composition-project.ts';
import {createEffectfulOperationReference} from '../../src/verification/reconciled-operation-effect-reference.ts';
import {OPERATION_FIXTURE_RUNNER} from '../../src/verification/reconciled-operation-fixture.ts';
import {captureOperationRecipe,operationReferenceEvent} from '../../src/verification/reconciled-operation-values.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
import {pathToFileURL} from 'node:url';
test('compiling effectful provider mutants cannot collapse reads, owned preparation, Event slots or clocks',async t=>{
 const f=fixture(t),r=reference(f),n=native(f.temp,f.plan()),observe=await runner(f);
 const provider=path.join(n.root,'js',n.module.provider_path.replace(/\.ts$/,'.js')),original=fs.readFileSync(provider,'utf8');
 const require=createRequire(import.meta.url),load=()=>{for(const key of Object.keys(require.cache))if(key.startsWith(path.join(n.root,'js')+path.sep))delete require.cache[key];return n.load();};
 const wrappers:Record<string,string>={
  'read-key':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,read:r=>tx.read(Object.freeze({...r,key:"foreign"}))};}}})',
  'read-target':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,read:r=>tx.read(Object.freeze({...r,target:"commerce:receipt"}))};}}})',
  'twice-read':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,read:async r=>{await tx.read(r);return tx.read(r);}};}}})',
  'read-mutation':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,read:async r=>{const value=await tx.read(r);if(value)value.detail.amount="77";return value;}};}}})',
  'clock-swap':'async(p,d)=>actualExecute(p,{...d,clocks:{"posted-fact":d.clocks["audit-fact"],"audit-fact":d.clocks["posted-fact"]}})',
  'clock-twice':'async(p,d)=>actualExecute(p,{...d,clocks:{"posted-fact":()=>{d.clocks["posted-fact"]();return d.clocks["posted-fact"]();},"audit-fact":d.clocks["audit-fact"]}})',
  'clock-after-begin':'async(p,d)=>{await Promise.resolve();return actualExecute(p,d);}',
  'drop-events':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:b=>tx.commit(Object.freeze({...b,events:Object.freeze([])}))};}}})',
  'duplicate-event-slot':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:b=>tx.commit(Object.freeze({...b,events:Object.freeze([b.events[0],b.events[0]])}))};}}})',
  'drop-second-write':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:b=>tx.commit(Object.freeze({...b,writes:Object.freeze(b.writes.slice(0,1))}))};}}})',
  'replace-create-mode':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:b=>tx.commit(Object.freeze({...b,writes:Object.freeze(b.writes.map(w=>Object.freeze({...w,mode:"create"})))}))};}}})',
  'no-clock-observation':'async(p,d)=>actualExecute(p,{...d,clocks:{"posted-fact":()=>"first-time","audit-fact":()=>"second-time"}})',
  'commit-without-await':'async(p,d)=>actualExecute(p,{...d,store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>{tx.commit(b);return {status:"committed"};}};}}})'
 };
 const mutations:Record<string,(s:string)=>string>=Object.fromEntries(Object.entries(wrappers).map(([name,wrapper])=>[name,s=>s+'\nconst actualExecute=exports.execute;exports.execute='+wrapper+';\n']));
 mutations['bypass-owned-writes']=s=>s.replace(/own\d+\(write\d+\);/g,'/* omitted owned write check */');
 mutations['skip-identity-comparison']=s=>s.replace(/if \([^\n]+\)\n\s+return abort\("failed", "READ_IDENTITY_MISMATCH"\);/,'/* omitted identity comparison */');
 mutations['reuse-first-event-value']=s=>s.replace(/value: event1/g,'value: event0');
 mutations['skip-second-guard']=s=>s.replace(/if \([^\n]+\)\n\s+return abort\("rejected", "RULE_REJECTED:commerce:receipt-matches"\);/,'/* omitted second guard */');
 const cases=samples(),reports:any[]=[];
 for(const [name,mutate]of Object.entries(mutations)){
  const code=mutate(original);assert.notEqual(code,original,name+' must change generated JavaScript');
  fs.writeFileSync(provider,code);execFileSync(process.execPath,['--check',provider],{encoding:'utf8'});
  const fn=load();let witness:string|null=null;
  for(const c of cases){
   try{assert.deepEqual(await observe(fn,c.recipe,c.mode,c.capture?capture:null,c.effects),r.oracle.expected(c.recipe,c.effects,c.mode));}
   catch{witness=c.id;break;}
  }
  assert.ok(witness,name+' must be detected');reports.push({name,witness});
 }
 fs.writeFileSync(provider,original);
 for(const c of cases)assert.deepEqual(await observe(load(),c.recipe,c.mode,c.capture?capture:null,c.effects),r.oracle.expected(c.recipe,c.effects,c.mode),c.id+' restored');
 assert.equal(reports.length,17);t.diagnostic(JSON.stringify({compiling_mutants:reports}));
});
const recipe=(v:any):any=>v===null?{tag:'null'}:typeof v==='bigint'?{tag:'scalar',value:String(v),format:'bigint'}:
 typeof v==='number'?{tag:'scalar',value:String(v),format:'number'}:typeof v!=='object'?{tag:'scalar',value:v}:
 Array.isArray(v)?{tag:'list',items:v.map(recipe)}:{tag:'fields',fields:Object.fromEntries(Object.entries(v).map(([k,x])=>[k,recipe(x)]))};
const effects=():any=>({reads:[{slot:'current-account',value:recipe(account())}],clocks:[{slot:'posted-fact',value:'first-time'},{slot:'audit-fact',value:'second-time'}]});
function reference(f:ReturnType<typeof fixture>){
 const plan=planCompiledReconciledProject(f.graph,{...publicSelection('application'),factories:f.factories,operations:[f.bindings]});
 const fields=compileSelectedProjectFields(f.graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:f.action.certificate.graph_sha256,roots:f.graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector).sort(),bindings:plan.selection.field_bindings},rules.field_contract);
 const action=compileOperationActionBindings(f.graph,f.boundary,fields,f.bindings,actionSource);
 return {plan,action,oracle:createEffectfulOperationReference(f.graph,plan,action)};
}
async function runner(f:ReturnType<typeof fixture>){
 const file=path.join(f.temp,'fixture.mjs');fs.writeFileSync(file,OPERATION_FIXTURE_RUNNER);
 return (await import(pathToFileURL(file).href)).observeOperationFixture;
}
function samples(){
 const cases:any[]=[],add=(id:string,change=(i:any,e:any)=>{},mode='committed',capture=false)=>{
  const i=recipe(input()),e=effects();change(i,e);cases.push({id,recipe:i,effects:e,mode,capture});
 };
 for(const mode of ['committed','rejected','indeterminate','begin-throw','commit-throw','rollback-throw','receipt-empty','receipt-unknown','receipt-extra','receipt-null','receipt-getter','receipt-inherited','receipt-symbol','receipt-hidden','receipt-array','receipt-undefined'])add(mode,undefined,mode);
 add('caller-and-clock-capture',undefined,'committed',true);
 add('read-missing',(_,e)=>e.reads[0].value=recipe(null));
 add('read-throws',(_,e)=>e.reads[0].throws=true);
 add('read-identity',(_,e)=>e.reads[0].value.fields.id=recipe('wrong'));
 add('read-shape',(_,e)=>e.reads[0].value.fields.balance=recipe('-1'));
 add('read-is-not-owned-validation',(_,e)=>e.reads[0].value.fields.detail.fields.amount=recipe('0'));
 add('read-is-not-input-capture',(_,e)=>e.reads[0].value.fields.labels=recipe(Array.from({length:1025},(_,i)=>'label-'+i)));
 add('guard-one',i=>i.fields.amount=recipe('100'));
 add('guard-two',i=>i.fields.receipt.fields.amount=recipe('9'));
 add('guards-both',i=>{i.fields.amount=recipe('100');i.fields.receipt.fields.amount=recipe('9');});
 add('guard-rollback-fails',i=>i.fields.amount=recipe('100'),'rollback-throw');
 add('write-top-level',i=>i.fields.replacement.fields.balance=recipe('0'));
 add('write-nested-value',i=>i.fields.replacement.fields.detail.fields.amount=recipe('0'));
 add('write-sum-payload',i=>i.fields.replacement.fields.choice.fields.payload.fields.amount=recipe('0'));
 add('write-second-entity',i=>{i.fields.amount=recipe('0');i.fields.receipt.fields.amount=recipe('0');});
 for(const value of ['-9223372036854775808','9223372036854775807',-2n,-0,0,1,1n])add('event-integer-'+String(value)+'-'+typeof value,i=>i.fields.posted_input.fields.payload.fields.amount=recipe(value));
 for(const value of ['-9223372036854775809','9223372036854775808','-0','01','+1',' 1',1.5,9007199254740992,null,true])add('event-invalid-'+String(value),i=>i.fields.posted_input.fields.payload.fields.amount=recipe(value));
 add('event-one-missing',i=>delete i.fields.posted_input.fields.payload.fields.amount);
 add('event-two-missing',i=>delete i.fields.audit_input.fields.payload.fields.amount);
 add('event-reference-empty',i=>i.fields.posted_input.fields.payload.fields['account-id']=recipe(''));
 add('event-generated-forbids-time',i=>i.fields.posted_input.fields.occurredAt=recipe('injected'));
 for(const slot of ['posted-fact','audit-fact']){
  for(const mode of ['throw','missing'])add('clock-'+slot+'-'+mode,(_,e)=>e.clocks.find((c:any)=>c.slot===slot).mode=mode);
  for(const value of ['',null,0])add('clock-'+slot+'-'+String(value),(_,e)=>e.clocks.find((c:any)=>c.slot===slot).value=value);
 }
 for(const mode of ['getter','non-enumerable','symbol','inherited','extra','missing-field','null-prototype','frozen']){
  add('root-'+mode,i=>{const base=structuredClone(i);Object.assign(i,{tag:'bad',mode,field:'amount',base});});
  add('read-'+mode,(_,e)=>e.reads[0].value={tag:'bad',mode,field:'balance',base:e.reads[0].value});
 }
 add('nested-event-getter',i=>i.fields.posted_input={tag:'bad',mode:'getter',field:'payload',base:i.fields.posted_input});
 add('nested-event-undefined',i=>i.fields.posted_input.fields.payload.fields.amount={tag:'bad',mode:'undefined',base:recipe('1')});
 return cases;
}
const capture=(i:any,d:any)=>{i.amount='100';i.replacement.balance='0';i.posted_input.payload.amount='wrong';d.clocks['posted-fact']=()=>{throw Error('late-clock');};};
test('effectful reference requires current branded action and selected public plan',t=>{
 const f=fixture(t),r=reference(f);
 assert.throws(()=>createEffectfulOperationReference(f.graph,r.plan,structuredClone(f.action)),/UNVALIDATED/);
 assert.throws(()=>createEffectfulOperationReference(f.graph,structuredClone(r.plan),r.action),/registered reconciled project required/);
 assert.throws(()=>createEffectfulOperationReference(f.graph,r.plan,f.action),/OPERATION_REFERENCE_ACTION/);
 const b=structuredClone(f.bindings);b.result.value=at('account_id');
 const action=compileOperationActionBindings(f.graph,f.boundary,f.fields,b,actionSource);
 assert.throws(()=>createEffectfulOperationReference(f.graph,r.plan,action),/OPERATION_REFERENCE_BINDING/);
 assert.equal(createReconciledSemanticControls(f.graph,r.plan).rows.find(r=>r.kind==='Operation')!.state,'ready');
});
test('native effectful Operation preserves typed reads, selected owned validators, event clocks and settlement',async t=>{
 const f=fixture(t),r=reference(f),n=native(f.temp,f.plan()),observe=await runner(f),fn=n.load();
 for(const c of samples()){
  const expected=r.oracle.expected(c.recipe,c.effects,c.mode);
  const actual=await observe(fn,c.recipe,c.mode,c.capture?capture:null,c.effects);
  assert.deepEqual(actual,expected,c.id);
 }
});
test('owned result validation happens after Event preparation but before commit',async t=>{
 const f=fixture(t);f.bindings.result={type:named('account'),value:at('current')};
 const compiled=f.compile(),r=reference({...f,...compiled}),n=native(f.temp,compiled.plan()),observe=await runner(f);
 for(const bad of [false,true]){
  const e=effects();if(bad)e.reads[0].value.fields.detail.fields.amount=recipe('0');
  const expected=r.oracle.expected(recipe(input()),e);
  assert.equal((expected.outcome as any)[1].find((p:any)=>p[0]==='status')[1][1],bad?'failed':'committed');
  assert.deepEqual(expected.clock_calls,['posted-fact','audit-fact']);
  assert.deepEqual(await observe(n.load(),recipe(input()),'committed',null,e),expected);
 }
});
test('required Event clocks and optional payload fields keep their own source contract',async t=>{
 const f=fixture(t),eventPath='specs/commerce/nodes/posted.json',event=read(path.join(f.source,eventPath));
 event.body.occurred_at_policy='required';event.body.payload.push({field_id:'note',type_ref:{kind:'primitive',name:'string'},required:false});
 f.write(eventPath,event);const compiled=f.compile(),r=reference({...f,...compiled}),n=native(f.temp,compiled.plan()),observe=await runner(f);
 for(const note of [undefined,'',null]){
  const i=input() as any;for(const key of ['posted_input','audit_input']){i[key].occurredAt='supplied';if(note!==undefined)i[key].payload.note=note;}
  const e=effects();e.clocks=[];const c=recipe(i),expected=r.oracle.expected(c,e);
  assert.deepEqual(expected.clock_calls,[]);
  assert.deepEqual(await observe(n.load(),c,'committed',null,e),expected);
 }
});
test('typed UInt64 read identities retain exact carriers and independent repeated read slots',async t=>{
 const f=fixture(t),accountPath='specs/commerce/nodes/account.json',operationPath='specs/commerce/nodes/post.json';
 const entity=read(path.join(f.source,accountPath));entity.body.typed_contract.properties.find((p:any)=>p.identity).type=scalar('UInt64');f.write(accountPath,entity);
 const operation=read(path.join(f.source,operationPath));operation.body.reads.push('second-account');f.write(operationPath,operation);
 f.bindings.inputs.find((p:any)=>p.name==='account_id').type=scalar('UInt64');
 f.bindings.reads.push({slot:'second-account',target:'commerce:account',parameter:'other',key:at('account_id')});
 f.bindings.result={type:scalar('UInt64'),value:at('other','FIXTURE-ACCOUNT#balance')};
 const compiled=f.compile(),r=reference({...f,...compiled}),n=native(f.temp,compiled.plan()),observe=await runner(f);
 for(const [i,id]of ['18446744073709551615',18446744073709551615n,9007199254740991,9007199254740992].entries()){
  for(const missing of [false,true]){
   const raw=input() as any;raw.account_id=id;raw.replacement.id=id;
   const first={...account(),id},second={...account('80'),id},e=effects();e.reads=[{slot:'current-account',value:recipe(first)},{slot:'second-account',value:recipe(missing?null:second)}];
   const c=recipe(raw),expected=r.oracle.expected(c,e);
   assert.equal(expected.read_calls,i===3?0:2);
   assert.deepEqual(await observe(n.load(),c,'committed',null,e),expected,'carrier '+i+' missing '+missing);
  }
 }
});
test('owned Entity, optional, list and set fields compose without treating them as database records',async t=>{
 const f=fixture(t),p='specs/commerce/nodes/account.json',entity=read(path.join(f.source,p));
 const extras=[
  {name:'related',type:named('receipt'),cardinality:'one'},
  {name:'maybe',type:{kind:'optional',element:named('detail')},cardinality:'optional'},
  {name:'sequence',type:{kind:'list',element:named('detail')},cardinality:'many'},
  {name:'unique',type:{kind:'set',element:named('detail')},cardinality:'many-unique'}
 ];
 for(const x of extras){entity.body.fields.push(x.name);entity.body.typed_contract.properties.push({...x,ontology_property:'FIXTURE-ACCOUNT#'+x.name,identity:false,meaning:x.name});}f.write(p,entity);
 const compiled=f.compile(),r=reference({...f,...compiled}),n=native(f.temp,compiled.plan()),observe=await runner(f);
 const enrich=(a:any)=>({...a,related:{id:'related',amount:'2'},maybe:{amount:'3'},sequence:[{amount:'4'},{amount:'4'}],unique:[{amount:'5'},{amount:'6'}]});
 for(const bad of ['none','related','maybe','sequence','unique','duplicate-set','omitted-optional']){
  const i=input() as any;i.replacement=enrich(i.replacement);
  if(['related','maybe'].includes(bad))i.replacement[bad].amount='0';
  if(['sequence','unique'].includes(bad))i.replacement[bad][1].amount='0';
  if(bad==='duplicate-set')i.replacement.unique.push({amount:'5'});
  if(bad==='omitted-optional')delete i.replacement.maybe;
  const e=effects();e.reads[0].value=recipe(enrich(account()));
  const c=recipe(i),expected=r.oracle.expected(c,e);
  assert.deepEqual(await observe(n.load(),c,'committed',null,e),expected,bad);
 }
});
test('declared delete write intents keep owned validation and exact mode in the batch',async t=>{
 const f=fixture(t);f.bindings.writes[0].mode='delete';
 const compiled=f.compile(),r=reference({...f,...compiled}),n=native(f.temp,compiled.plan()),observe=await runner(f);
 for(const bad of [false,true]){
  const i=input();if(bad)i.replacement.detail.amount='0';
  const c=recipe(i),e=effects();assert.deepEqual(await observe(n.load(),c,'committed',null,e),r.oracle.expected(c,e),String(bad));
 }
});
test('symbolic capture bounds and Event integer semantics do not depend on generated implementation',()=>{
 assert.throws(()=>captureOperationRecipe(recipe(Array.from({length:1025},()=>0))),/OPERATION_REFERENCE_VALUE/);
 assert.equal(captureOperationRecipe(recipe(-0)),0);
 const body={event_type:'x',version:'1',occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'uuid'}},occurred_at_policy:'generated',payload:[{field_id:'n',type_ref:{kind:'primitive',name:'integer'},required:true}]};
 let calls=0;
 assert.equal(operationReferenceEvent(body,{occurrence:{id:'x'},payload:{n:'-9223372036854775808'}},()=>{calls++;return 'time';}).payload.n,-9223372036854775808n);
 assert.throws(()=>operationReferenceEvent(body,{occurrence:{id:'x'},payload:{n:'9223372036854775808'}},()=>{calls++;return 'time';}));
 assert.equal(calls,1);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
