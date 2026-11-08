import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync,spawnSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {planConfiguredEvents,CONFIGURED_EVENT_VERSION,EVENT_VALUE_PROFILE} from '../../src/generation/configured-events.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes=(p:string)=>fs.readFileSync(p,'utf8'),read=(p:string)=>JSON.parse(bytes(p));
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  typescript:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')),event_contract:bytes(path.join(pkg,'event-generation-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'));
const field=(field_id:string,name:string,required=true)=>({field_id,type_ref:{kind:'primitive',name},required});
const reference=(field_id:string,selector:string)=>({field_id,type_ref:{kind:'reference',selector},required:true});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-events-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=read(path.join(source,'specs/alpha/feature.json'));
  const node=(node_id:string,kind:string,body:any)=>{feature.nodes.push(node_id);write('specs/alpha/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id,kind,body});};
  node('valid-currency','Rule',{description:'Currency rule',predicate:'currency is valid'});
  node('currency','Value Object',{description:'Currency',fields:[field('code','string')],invariant_refs:['alpha:valid-currency']});
  node('status','Enum',{description:'Status',values:['ready','closed']});
  const bodies:any={};
  for(const [id,policy] of [['settled','required'],['clocked','generated'],['empty','required']]){
    const body={description:'An occurrence, not a database write',event_type:id,version:'2',occurrence_id:field('occurrence-id','uuid'),occurred_at_policy:policy,
      payload:id==='empty'?[]:[field('amount','integer'),field('ratio','decimal'),field('enabled','boolean'),field('label','string'),field('timestamp','timestamp'),field('uuid','uuid'),field('note','string',false),reference('entity','alpha:customer'),reference('value','alpha:currency'),reference('status','alpha:status'),reference('previous','alpha:'+id)]};
    bodies['alpha:'+id]=body;node(id!,'Event',body);
  }
  write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256},boundaryContract);
  const selection:any={schema_version:CONFIGURED_EVENT_VERSION,language:'typescript',value_profile:EVENT_VALUE_PROFILE,boundary_sha256:boundary.boundary_sha256,module_root:'application',roots:Object.keys(bodies)};
  return {temp,source,write,bodies,graph,boundary,selection,plan:()=>planConfiguredEvents(graph,boundary,selection,sources)};
}
function native(f:ReturnType<typeof fixture>,name='native'){
  const plan=f.plan(),root=path.join(f.temp,name);fs.mkdirSync(root,{recursive:true});
  for(const a of plan.artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
  const config=path.join(root,'tsconfig.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'commonjs'},files:plan.artifacts.map(a=>a.relative_path)}));
  const expected=plan.modules.map(m=>({...m,source_path:path.join(f.source,'specs/alpha/nodes/'+m.selector.split(':')[1]+'.json'),reference_paths:Object.fromEntries(m.descriptor.references.map(r=>[r.selector,path.join(f.source,'specs/'+r.selector.replace(':','/nodes/')+'.json')]))}));
  const expectedPath=path.join(root,'expected.json');fs.writeFileSync(expectedPath,JSON.stringify(expected));
  const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${f.temp},target=${f.temp}`,'--mount',`type=bind,source=${project}/impl/cli/tools,target=/observer,readonly`,'--workdir',root,image];
  assert.equal(execFileSync('docker',[...args,'tsc','--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  const compile=(extra:string[]=[])=>execFileSync('docker',[...args,'tsc','--ignoreConfig','--strict','--exactOptionalPropertyTypes','--skipLibCheck','--target','ES2022','--module','commonjs','--declaration','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8'});
  compile();
  const module=(id:string)=>plan.modules.find(m=>m.selector==='alpha:'+id)!;
  const js=(id:string)=>path.join(root,'js',module(id).relative_path.replace(/\.ts$/,'.js'));
  const load=(id:string)=>createRequire(import.meta.url)(js(id))[module(id).callable];
  const observe=()=>{const r=spawnSync('docker',[...args,'node','/observer/observe-configured-events.mjs',config,expectedPath],{encoding:'utf8'});return {status:r.status,...JSON.parse(r.stdout||'{}'),stderr:r.stderr};};
  return {root,plan,compile,module,js,load,observe};
}
const input=(amount:any=1)=>({occurrence:{'occurrence-id':'occurrence-1'},occurredAt:'supplied-time',payload:{amount,ratio:0.25,enabled:true,label:'',timestamp:'source-time',uuid:'source-id',entity:'customer-1',value:'currency-1',status:'ready',previous:'previous-occurrence'}});

test('Event planner binds exact graph source and references without manufacturing records or effects',t=>{
  const f=fixture(t),p=f.plan(),old=planCompiledProjectBuild(f.graph,'typescript');
  assert.equal(p.modules.length,3);assert.equal(p.artifacts.length,6);assert.deepEqual(f.plan(),p);
  assert.deepEqual(planConfiguredEvents(f.graph,f.boundary,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
  const alternate=planConfiguredEvents(f.graph,f.boundary,{...f.selection,module_root:'relocated'},sources);
  assert.deepEqual(alternate.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  assert.deepEqual(planConfiguredEvents(f.graph,f.boundary,{...f.selection,roots:['alpha:settled']},sources).artifacts,p.artifacts.filter(a=>a.relative_path.includes('/settled.')));
  assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript'),old);
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));assert.ok(Object.isFrozen(p.modules[0]!.descriptor.payload));
  for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.equal(d.provider.sha256,sha256(p.artifacts.find(a=>a.relative_path===m.provider_path)!.content));assert.equal(d.publication,false);}
  const references=p.modules.find(m=>m.selector==='alpha:settled')!.descriptor.references;
  assert.deepEqual(references.map(r=>r.kind).sort(),['Entity','Enum','Event','Value Object']);
  fs.renameSync(f.source,path.join(f.temp,'relocated-source'));assert.deepEqual(f.plan(),p);
});

test('Event configuration rejects source drift, forged boundaries and hostile selections',t=>{
  const f=fixture(t);
  for(const patch of [{schema_version:'future'},{language:'python'},{value_profile:'float'},{module_root:'../escape'},{module_root:'aux'},{module_root:'a//b'},{roots:[]},{roots:['alpha:settled','alpha:settled']},{roots:['alpha:customer']},{roots:['alpha:missing']},{boundary_sha256:'stale'},{ignore_errors:true}])assert.throws(()=>planConfiguredEvents(f.graph,f.boundary,{...f.selection,...patch},sources));
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredEvents(f.graph,f.boundary,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  assert.throws(()=>planConfiguredEvents(structuredClone(f.graph),f.boundary,f.selection,sources));
  assert.throws(()=>planConfiguredEvents(f.graph,structuredClone(f.boundary),f.selection,sources));
  const other=fixture(t);other.bodies['alpha:settled'].version='3';other.write('specs/alpha/nodes/settled.json',{schema_version:'domainspec.node/v1',node_id:'settled',feature_id:'alpha',kind:'Event',body:other.bodies['alpha:settled']});
  assert.throws(()=>planConfiguredEvents(loadCompiledProjectGraph(other.source),f.boundary,f.selection,sources),/cross-graph/);
  let reads=0;assert.throws(()=>planConfiguredEvents(f.graph,f.boundary,{...f.selection,get module_root(){reads++;return 'bad';}},sources));
  const roots:any=[];Object.defineProperty(roots,0,{get(){reads++;return 'alpha:settled';},enumerable:true});
  assert.throws(()=>planConfiguredEvents(f.graph,f.boundary,{...f.selection,roots},sources));
  assert.throws(()=>planConfiguredEvents(f.graph,f.boundary,f.selection,{...sources,get event_contract(){reads++;return sources.event_contract;}}));assert.equal(reads,0);
});

test('Native Event values retain identity, exact signed integers and immutable optional payloads',t=>{
  const f=fixture(t),n=native(f),make=n.load('settled'),min=-9223372036854775808n,max=9223372036854775807n;
  const mutable=input(max.toString()),event=make(mutable);
  assert.equal(event.payload.amount,max);assert.equal(make(input(min)).payload.amount,min);assert.equal(make(input(-0)).payload.amount,0n);
  assert.equal(event.type,'settled');assert.equal(event.version,'2');assert.equal(event.occurredAt,'supplied-time');
  assert.equal(event.occurrence['occurrence-id'],'occurrence-1');assert.equal(Object.hasOwn(event.payload,'note'),false);
  assert.notEqual(event.payload,mutable.payload);assert.notEqual(event.occurrence,mutable.occurrence);
  mutable.occurrence['occurrence-id']='changed';mutable.payload.entity='different';assert.equal(event.payload.entity,'customer-1');assert.equal(event.occurrence['occurrence-id'],'occurrence-1');
  for(const v of [event,event.occurrence,event.payload,make,make.descriptor,make.descriptor.references])assert.ok(Object.isFrozen(v));
  assert.throws(()=>{event.payload.entity='write';});
  assert.equal(make({...input(),payload:{...input().payload,note:'present'}}).payload.note,'present');
  const distinct=make({...input(),occurrence:{'occurrence-id':'occurrence-2'}});assert.deepEqual(distinct.payload,make(input()).payload);assert.notDeepEqual(distinct.occurrence,make(input()).occurrence);
  const sameOccurrence=make({...input(),payload:{...input().payload,label:'different facts'}});assert.deepEqual(sameOccurrence.occurrence,make(input()).occurrence);assert.equal(sameOccurrence.payload.label,'different facts','construction is not occurrence registration or deduplication');
  assert.equal(make({...input(),payload:{...input().payload,enabled:false,ratio:-0,note:''}}).payload.enabled,false);
  assert.equal(make({...input(),payload:{...input().payload,enabled:false,ratio:-0,note:''}}).payload.ratio,0);
  assert.deepEqual(n.load('empty')({occurrence:{'occurrence-id':'empty'},occurredAt:'time',payload:{}}).payload,{});
  const script=`const f=require(${JSON.stringify(n.js('settled'))}).eventSettled;const e=f(${JSON.stringify(input(min.toString()))});console.log(JSON.stringify({pid:process.pid,id:e.occurrence['occurrence-id'],amount:String(e.payload.amount)}));`;
  const run=()=>JSON.parse(execFileSync(process.execPath,['-e',script],{encoding:'utf8'}));const a=run(),b=run();assert.notEqual(a.pid,b.pid);assert.equal(a.amount,min.toString());assert.equal(a.amount,b.amount);
});

test('Native Event time policy separates supplied time from one explicit clock call',t=>{
  const f=fixture(t),n=native(f),make=n.load('clocked'),{occurredAt,...facts}=input();let calls=0;
  const event=make(facts,()=>{calls++;return 'clock-result';});assert.equal(calls,1);assert.equal(event.occurredAt,'clock-result');
  assert.throws(()=>make(input(),()=>{calls++;return 'ignored';}),/EVENT_INPUT/);assert.equal(calls,1);
  assert.throws(()=>make({...facts,payload:{...facts.payload,amount:'bad'}},()=>{calls++;return 'ignored';}),/EVENT_INPUT/);assert.equal(calls,1);
  for(const result of ['',null,undefined,{},1,Promise.resolve('later')])assert.throws(()=>make(facts,()=>result),/EVENT_INPUT/);
  assert.throws(()=>make(facts,null),/EVENT_INPUT/);
  const sentinel=new Error('clock failed');assert.throws(()=>make(facts,()=>{throw sentinel;}),e=>e===sentinel);
  assert.equal(n.load('settled')(input(),()=>{throw Error('must not call');}).occurredAt,'supplied-time');
});

test('Native Event hostile inputs reject without coercion, getters or caller writes',t=>{
  const f=fixture(t),n=native(f),make=n.load('settled');let calls=0;
  for(const amount of [9223372036854775808n,-9223372036854775809n,Number.MAX_SAFE_INTEGER+1,1.5,NaN,Infinity,'01','-0','+1','1\n',' 1','1.0',null,{},true])assert.throws(()=>make(input(amount)),/EVENT_INPUT/);
  for(const root of [null,[],{},Object.create(input()),{...input(),extra:1},{...input(),[Symbol()]:1}])assert.throws(()=>make(root),/EVENT_INPUT/);
  const getter={...input(),get payload(){calls++;return input().payload;}};assert.throws(()=>make(getter),/EVENT_INPUT/);
  const nested={...input().payload,get label(){calls++;return 'bad';}};assert.throws(()=>make({...input(),payload:nested}),/EVENT_INPUT/);
  const boxed={toString(){calls++;return 'id';},valueOf(){calls++;return 1;}};
  for(const [key,value] of [['ratio',NaN],['ratio',Infinity],['enabled',1],['label',boxed],['timestamp',''],['uuid',boxed],['entity',{}],['note',undefined],['note',null]])assert.throws(()=>make({...input(),payload:{...input().payload,[key as string]:value}}),/EVENT_INPUT/);
  const hidden={...input().payload};Object.defineProperty(hidden,'label',{value:'hidden',enumerable:false});assert.throws(()=>make({...input(),payload:hidden}),/EVENT_INPUT/);
  assert.equal(calls,0);
  const inert=input();Object.freeze(inert);Object.freeze(inert.payload);Object.freeze(inert.occurrence);assert.equal(make(inert).payload.amount,1n);
  assert.equal(make(Object.assign(Object.create(null),input())).payload.amount,1n);
});

test('Native declaration consumers reject payload, identity, reference and clock type collapse',t=>{
  const f=fixture(t),n=native(f),required='./'+n.module('settled').relative_path.replace(/\.ts$/,'.js'),generated='./'+n.module('clocked').relative_path.replace(/\.ts$/,'.js');
  const consumer=path.join(n.root,'consumer.ts');
  fs.writeFileSync(consumer,`import {eventSettled,type EventValue} from ${JSON.stringify(required)};\nimport {eventClocked} from ${JSON.stringify(generated)};\ndeclare const event:EventValue;\n// @ts-expect-error immutable payload\nevent.payload.amount=2n;\n// @ts-expect-error occurrence not Entity reference\nconst identity:typeof event.payload.entity=event.payload.value;\n// @ts-expect-error exact integer result is not number\nconst amount:number=event.payload.amount;\n// @ts-expect-error type discriminator is source-bound\nconst type:'clocked'=event.type;\n// @ts-expect-error clock required\neventClocked({occurrence:{'occurrence-id':'id'},payload:event.payload});\n// @ts-expect-error supplied-time constructor has no clock parameter\neventSettled({occurrence:event.occurrence,payload:event.payload,occurredAt:'time'},()=> 'clock');\n`);
  n.compile([consumer]);assert.ok(fs.existsSync(path.join(n.root,'js',n.module('settled').relative_path.replace(/\.ts$/,'.d.ts'))));
});

test('Independent native AST observer rejects compiling semantic, clock and binding mutations',t=>{
  const f=fixture(t),n=native(f),initial=n.observe();assert.equal(initial.result,'pass',JSON.stringify(initial));
  const m=n.module('settled'),provider=n.plan.artifacts.find(a=>a.relative_path===m.provider_path)!,wrapper=n.plan.artifacts.find(a=>a.relative_path===m.relative_path)!;
  const mutants=[provider.content.replace('eventInteger(p["amount"]!.value)','eventInteger(p["amount"]!.value)+1n'),provider.content.replace('eventText(o["occurrence-id"]!.value)','eventText(p["entity"]!.value)'),provider.content.replace('version:"2",occurrence','version:"3" as "2",occurrence'),provider.content.replace('return Object.freeze({type:','Date.now(); return Object.freeze({type:'),provider.content.replace('return Object.freeze({type:','queueMicrotask(()=>{(globalThis as any).leak=true;}); return Object.freeze({type:'),provider.content.replace('const payload=Object.freeze({','const payload=({')];
  for(const mutant of mutants){assert.notEqual(mutant,provider.content);fs.writeFileSync(path.join(n.root,m.provider_path),mutant);n.compile();assert.equal(n.observe().result,'fail');}
  fs.writeFileSync(path.join(n.root,m.provider_path),provider.content);
  for(const mutant of [wrapper.content.replace('Object.assign(make,','Object.assign((...args:Parameters<typeof make>)=>make(...args),'),wrapper.content.replace(m.descriptor.provider.sha256,'0'.repeat(64)),wrapper.content.replace('["publication"]:false','["publication"]:true')]){
    assert.notEqual(mutant,wrapper.content);fs.writeFileSync(path.join(n.root,m.relative_path),mutant);n.compile();assert.equal(n.observe().result,'fail');
  }
  fs.writeFileSync(path.join(n.root,m.relative_path),wrapper.content);
  const cm=n.module('clocked'),cp=n.plan.artifacts.find(a=>a.relative_path===cm.provider_path)!;
  for(const mutant of [cp.content.replace('eventText(clock())','eventText((clock(),clock()))'),cp.content.replace('eventText(clock())','eventText("fixed")')]){fs.writeFileSync(path.join(n.root,cm.provider_path),mutant);n.compile();assert.equal(n.observe().result,'fail');}
});

test('Changed Event source and reference targets causally change descriptor and runtime meaning',t=>{
  const f=fixture(t),before=f.plan();
  const currency=read(path.join(f.source,'specs/alpha/nodes/currency.json'));currency.body.description='Changed referenced contract';f.write('specs/alpha/nodes/currency.json',currency);
  const referenceGraph=loadCompiledProjectGraph(f.source),referenceBoundary=compileCompositionBoundary(referenceGraph,{schema_version:COMPOSITION_BOUNDARY_VERSION,graph_sha256:createCompiledProjectCertificate(referenceGraph).graph_sha256,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256},boundaryContract);
  const referencePlan=planConfiguredEvents(referenceGraph,referenceBoundary,{...f.selection,boundary_sha256:referenceBoundary.boundary_sha256},sources);
  const original=before.modules.find(m=>m.selector==='alpha:settled')!,referenced=referencePlan.modules.find(m=>m.selector==='alpha:settled')!;
  assert.notEqual(original.descriptor.descriptor_sha256,referenced.descriptor.descriptor_sha256);
  assert.equal(original.descriptor.provider.sha256,referenced.descriptor.provider.sha256,'reference target body changes evidence, not embedded data or lookup code');
  f.bodies['alpha:settled'].version='3';f.write('specs/alpha/nodes/settled.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'settled',kind:'Event',body:f.bodies['alpha:settled']});
  const graph=loadCompiledProjectGraph(f.source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256},boundaryContract);
  const plan=()=>planConfiguredEvents(graph,boundary,{...f.selection,boundary_sha256:boundary.boundary_sha256},sources),after=plan();assert.notEqual(before.plan_sha256,after.plan_sha256);
  const prior=before.modules.find(m=>m.selector==='alpha:settled')!,next=after.modules.find(m=>m.selector==='alpha:settled')!;
  assert.notEqual(prior.descriptor.references.find(r=>r.kind==='Value Object')!.body_sha256,next.descriptor.references.find(r=>r.kind==='Value Object')!.body_sha256);
  const n=native({...f,plan},'changed');assert.equal(n.load('settled')(input()).version,'3');assert.equal(n.observe().result,'pass');
});

test('Native Event field names remain separate from metadata and support every occurrence field carrier',t=>{
  const f=fixture(t),feature=read(path.join(f.source,'specs/alpha/feature.json'));
  const cases=[['string','id'],['boolean',false],['integer','-9223372036854775808'],['decimal',0.5],['timestamp','time'],['uuid','uuid'],['reference','entity-1']] as const;
  for(const [kind] of cases){
    const id='identity-'+kind;feature.nodes.push(id);
    f.write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind:'Event',body:{description:'Identity carrier',event_type:id,version:'1',occurrence_id:kind==='reference'?reference('payload','alpha:customer'):field('payload',kind),occurred_at_policy:'required',payload:[field('type','string'),field('version','integer'),field('payload','boolean',false)]}});
  }
  f.write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(f.source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256},boundaryContract);
  const plan=()=>planConfiguredEvents(graph,boundary,{...f.selection,boundary_sha256:boundary.boundary_sha256,roots:cases.map(([kind])=>'alpha:identity-'+kind)},sources);
  const n=native({...f,plan},'identities');
  for(const [kind,value] of cases){const e=n.load('identity-'+kind)({occurrence:{payload:value},occurredAt:'time',payload:{type:'user fact',version:'2',payload:false}});assert.equal(e.type,'identity-'+kind);assert.equal(e.payload.type,'user fact');assert.equal(e.version,'1');assert.equal(e.payload.version,2n);assert.equal(e.payload.payload,false);assert.equal(e.occurrence.payload,kind==='integer'?BigInt(value):value);}
  assert.equal(n.observe().result,'pass');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
