/** Genuine source-bound v2 domain metadata; no native execution claim.
 * Open Questions: docs/COMMERCE-COMPUTATION-V2.md#open-questions. */
import test,{before} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync,mkdirSync,cpSync,copyFileSync,readdirSync,renameSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner,assertCommerceComputationDomainOwner,type CommerceComputationDomainHandle} from '../../src/commerce/commerce-computation-domain.js';
import {deriveCommerceComputationEnvironment} from '../../src/commerce/commerce-computation-environment.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),contract=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/pure-producer-model-09.json',import.meta.url),'utf8'));
const setup=async(root=candidate)=>{const sources=createCoreCommerceSourceOwner(),semantics=createCoreCommerceSemanticOwner(sources),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(root,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),handle=domain.check(contract);return {sources,semantics,stage,source,domain,handle};};
let f:Awaited<ReturnType<typeof setup>>;
before(async()=>{f=await setup();});
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
test('actual typed environment preserves32pure functions,closed domain values and every executable expression slot',()=>{
 const value=f.domain.inspect(f.handle),env=value.environment;assertCommerceComputationDomainOwner(f.domain);assert.equal(value.source.module,'Orders');assert.equal(value.contract.source_node,'Orders.PayableTotal');assert.equal(env.counts.functions,32);assert.equal(env.counts.records,56);assert.equal(env.counts.enums,38);assert.equal(env.counts.refinements,4);assert.ok(env.counts.expressions>1000);assert.ok(env.calls.some(c=>c.declaration==='Orders.PayableTotal'));assert.equal(new Set(env.expressions.map(e=>e.path)).size,env.expressions.length);assert.ok(env.expressions.every(e=>e.type&&e.owner));assert.equal(env.expressions.find(e=>e.path==='$.expression')!.type.kind,'scalar');assert.ok(Object.isFrozen(value.environment.calls));assert.match(value.qualification,/emitter-evaluator-native-and-call-runtime-not-established/);
});
test('per-declaration rounding/error actions and embedded-once preconditions remain exact',()=>{
 const value=f.domain.inspect(f.handle),call=value.environment.calls.find(c=>c.declaration==='Orders.PayableTotal')!;assert.deepEqual(call.on_evaluation_error,{kind:'fail',code:'calculation-failed'});assert.equal(call.rounding,'reject');assert.equal(call.evaluation_order,'source-order-arguments;original-hygienic-lets-retained');assert.ok(value.contract.functions.every(d=>d.precondition_mode==='embedded-once-in-body'));
});
test('all130pure/value declarations retain actual source identities and original declaration spans',()=>{const value=f.domain.inspect(f.handle);assert.equal(value.symbols.length,130);for(const s of value.symbols){assert.equal(s.source.artifact.path,s.span.path);assert.ok(s.span.end>s.span.start);assert.match(s.source.artifact.sha256,/^[a-f0-9]{64}$/);}assert.ok(value.symbols.some(s=>s.source.module==='Shop.Values'&&s.selector.role==='ValueObject'));assert.ok(value.symbols.some(s=>s.source.module==='Inventory'&&s.selector.name==='AvailableStock'));});
test('optional enum payload narrowing and state-machine outcomes have explicit checked type slots',()=>{
 const slots=f.domain.inspect(f.handle).environment.expressions;assert.ok(slots.some(s=>s.op==='require_some'&&s.type.kind==='record'));assert.ok(slots.some(s=>s.op==='match_variant'));assert.ok(slots.some(s=>s.op==='enum_value'&&s.type.kind==='enum'));assert.equal(slots.filter(s=>s.op==='state_machine'&&s.type.kind==='outcome').length,2);
});
test('matching DTOs,proxies,clones and another original domain factory cannot restore custody',()=>{
 for(const fake of [{...f.handle},Object.create(f.handle),JSON.parse(JSON.stringify(f.handle)),new Proxy(f.handle,{})])failure(()=>f.domain.inspect(fake),'ForeignOwner');failure(()=>f.domain.inspect(f.domain.inspect(f.handle) as any),'ForeignOwner');const other=createCommerceComputationDomainOwner(f.stage,f.source);failure(()=>other.inspect(f.handle),'ForeignOwner');failure(()=>assertCommerceComputationDomainOwner({...f.domain}),'ForeignOwner');failure(()=>createCommerceComputationDomainOwner({...f.stage},f.source),'ForeignOwner');
});
for(const [name,edit]of [
 ['source identity',(p:any)=>p.source_node='Other.Price'],
 ['budget',(p:any)=>p.limits.fuel++],
 ['calculation formula',(p:any)=>p.functions.find((d:any)=>d.name==='Orders.PayableTotal').body={op:'literal',type:{kind:'scalar',name:'UInt64'},value:'0'}],
 ['Rule kind',(p:any)=>p.functions[0].kind='Operation'],
 ['evaluation error action',(p:any)=>p.functions.find((d:any)=>d.name==='Orders.PayableTotal').on_evaluation_error=null],
 ['refinement minimum',(p:any)=>p.values.refinements[0].min_utf8_bytes=0],
 ['optional type erasure',(p:any)=>p.values.records.find((r:any)=>Object.values(r.fields).some((t:any)=>t.kind==='optional')).fields.forged={kind:'scalar',name:'Bool'}],
 ['native/effect expression',(p:any)=>p.expression={op:'native_observation',method:'readDatabase'}],
 ['invented native acceptance',(p:any)=>p.native_basis={accepted:true}],
]as const)test('source-bound domain refuses changed '+name,()=>{const p=JSON.parse(JSON.stringify(contract));edit(p);failure(()=>f.domain.check(p));});
test('accessors,functions and proxies reject without invoking user code',()=>{let called=false;const p={get source_node(){called=true;return contract.source_node;}};failure(()=>f.domain.check(p as any),'InvalidContract');failure(()=>f.domain.check(new Proxy(contract,{ownKeys(){called=true;return [];}})),'InvalidContract');const copy={...contract,callback:()=>{called=true;}};failure(()=>f.domain.check(copy),'InvalidContract');assert.equal(called,false);});
test('original domain disposal invalidates only its own token',()=>{const owner=createCommerceComputationDomainOwner(f.stage,f.source),h=owner.check(contract);owner.dispose(h);failure(()=>owner.inspect(h),'DisposedOwner');f.domain.assertCurrent(f.handle);});
test('configured executable AST/node/depth/call bounds are enforced while deriving layout',()=>{
 for(const limits of [{...contract.limits,max_ast_nodes:1},{...contract.limits,max_ast_depth:1},{...contract.limits,max_call_depth:1}])failure(()=>deriveCommerceComputationEnvironment({...contract,limits}),'ResourceLimit');
});
test('Policy selection binds its exact invocation path and loops retain their typed binders',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-domain-policy-'));try{
  cpSync(candidate,root,{recursive:true});const file=path.join(root,'application.alch'),extra=`
calculation Add:
  pure
  input first UInt64
  input second UInt64
  result UInt64
  expression first + second
policy Choose:
  input amount UInt64
  result UInt64
  ordered-cases:
    positive when amount > 0 -> Add(second=1,first=amount)
    otherwise -> Add(first=amount,second=0)
calculation PositiveTotal:
  pure
  input values List<UInt64,10>
  result UInt64
  expression fold(filter(values,item:UInt64 => item > 0),0,state:UInt64,item:UInt64 => state + item)
`;
  writeFileSync(file,readFileSync(file,'utf8')+extra);const identityPath=path.join(root,'contracts/contract-identities.json'),identities=JSON.parse(readFileSync(identityPath,'utf8')),row=identities.modules.find((r:any)=>r.artifact.path==='application.alch'),bytes=readFileSync(file);row.artifact.sha256=createHash('sha256').update(bytes).digest('hex');row.artifact.bytes=bytes.length;writeFileSync(identityPath,JSON.stringify(identities,null,2)+'\n');
  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root),inspected=sources.inspect(capture),paths=new Set(inspected.reconstruction.modules.map(m=>m.path)),texts=inspected.files.filter(x=>paths.has(x.path)),semantics=createCoreCommerceSemanticOwner(sources),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(root,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),checked=domain.check(createCoreCommerceComputationContract(texts,'Shop.Application.Choose',contract.limits)),env=domain.inspect(checked).environment;
  assert.equal(env.policy_actions.length,2);assert.ok(env.policy_actions.every(a=>a.invocation_path.includes('.expression.body.body')));assert.ok(env.policy_actions.every(a=>a.calculation==='Shop.Application.Add'&&a.invocation_entered.startsWith('must-be-observed')));assert.ok(env.expressions.some(e=>e.op==='filter'));assert.ok(env.expressions.some(e=>e.op==='fold'));stage.dispose(source);failure(()=>domain.inspect(checked),'DisposedOwner');sources.dispose(capture);
 }finally{rmSync(root,{recursive:true,force:true});}
});
test('same-byte source replacement invalidates derived domain custody',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-domain-source-'));try{cpSync(candidate,root,{recursive:true});const g=await setup(root),file=path.join(root,'application.alch');writeFileSync(file+'.replacement',readFileSync(file));renameSync(file+'.replacement',file);failure(()=>g.domain.assertCurrent(g.handle),'StaleOwner');}finally{rmSync(root,{recursive:true,force:true});}
});
test('shared schema and call DAG layout does not expand every repeated dependency path',()=>{
 const scalar={kind:'scalar',name:'UInt64'},literal={op:'literal',type:scalar,value:'0'},records=Array.from({length:30},(_,i)=>({name:'Stress.R'+i,role:'ValueObject',fields:i?Object.fromEntries(Array.from({length:32},(_,j)=>['f'+j,{kind:'record',name:'Stress.R'+(i-1)}])):{value:scalar},invariants:[],event_version:null,entity:null})),functions=Array.from({length:30},(_,i)=>({name:'Stress.F'+i,kind:'Calculation',pure:true,parameters:[],result:scalar,body:i?{op:'binary',operator:'add',left:{op:'call',declaration:'Stress.F'+(i-1),arguments:[]},right:{op:'call',declaration:'Stress.F'+(i-1),arguments:[]}}:literal,preconditions:[],precondition_mode:'embedded-once-in-body',rounding:'reject',on_evaluation_error:null}));
 const data={...contract,source_node:'Stress.F29',inputs:[],functions,values:{schema_version:'craft.commerce-values/v1-candidate',records,enums:[],refinements:[],collection_predicates:[],root:scalar},expression:{op:'call',declaration:'Stress.F29',arguments:[]},result:scalar};const env=deriveCommerceComputationEnvironment(data as any);assert.equal(env.counts.functions,30);assert.equal(env.counts.calls,59);assert.equal(env.counts.records,30);assert.equal(env.counts.expressions,89);
});
for(const mode of ['bytes','same-bytes-replacement']as const)test('loaded domain implementation pin rejects '+mode+' and new factories',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-domain-code-')),cli=fileURLToPath(new URL('../../',import.meta.url));try{
  for(const dir of ['src/commerce','src/profile-engine','contracts'])mkdirSync(path.join(root,dir),{recursive:true});for(const name of readdirSync(path.join(cli,'src/commerce')))if((name.startsWith('commerce-core-')||name.startsWith('commerce-computation-'))&&name.endsWith('.ts')||['commerce-data-v1.ts','commerce-registry-v1.ts','commerce-stages-v1.ts'].includes(name))copyFileSync(path.join(cli,'src/commerce',name),path.join(root,'src/commerce',name));copyFileSync(path.join(cli,'src/profile-engine/contracts.ts'),path.join(root,'src/profile-engine/contracts.ts'));for(const name of readdirSync(path.join(cli,'contracts')))if(name.endsWith('.json'))copyFileSync(path.join(cli,'contracts',name),path.join(root,'contracts',name));writeFileSync(path.join(root,'package.json'),'{"type":"module"}');writeFileSync(path.join(root,'contract.json'),JSON.stringify(contract));
  const code=`import assert from 'node:assert/strict';import {readFileSync,writeFileSync,renameSync} from 'node:fs';import {pathToFileURL} from 'node:url';const [root,candidate,mode]=process.argv.slice(1),load=n=>import(pathToFileURL(root+'/src/commerce/'+n+'.ts'));const {createCoreCommerceSourceOwner}=await load('commerce-core-source-owner'),{createCoreCommerceSemanticOwner}=await load('commerce-core-semantic-owner'),{createCoreCommerceStageSourceOwner}=await load('commerce-core-stage-owner'),{createCommerceComputationDomainOwner}=await load('commerce-computation-domain');const s=createCoreCommerceSourceOwner(),m=createCoreCommerceSemanticOwner(s),stage=createCoreCommerceStageSourceOwner(s,m),source=await stage.prepare(candidate,'application.alch'),o=createCommerceComputationDomainOwner(stage,source),h=o.check(JSON.parse(readFileSync(root+'/contract.json','utf8'))),file=root+'/src/commerce/commerce-computation-environment.ts',bytes=readFileSync(file);if(mode==='bytes')writeFileSync(file,Buffer.concat([bytes,Buffer.from(String.fromCharCode(10)+'//changed'+String.fromCharCode(10))]));else{writeFileSync(file+'.replacement',bytes);renameSync(file+'.replacement',file);}for(const run of [()=>o.assertCurrent(h),()=>createCommerceComputationDomainOwner(stage,source)])assert.throws(run,e=>e.diagnostics?.[0]?.code==='StaleOwner');console.log('domain-code-currentness-passed');`;
  const result=spawnSync(process.execPath,['--import','tsx','--input-type=module','-e',code,root,candidate,mode],{cwd:cli,encoding:'utf8',maxBuffer:2097152});assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/domain-code-currentness-passed/);
 }finally{rmSync(root,{recursive:true,force:true});}
});
