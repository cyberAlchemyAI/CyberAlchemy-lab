/** Separate source-to-producer contracts; no runtime/native owner claims.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test,{after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {createCoreCommerceReadContracts,createCoreCommerceEffectContracts,createCoreCommerceWorkflowContracts,createCoreCommerceEntryContracts,checkCoreCommerceReadContractsProposal,checkCoreCommerceEffectContractsProposal,checkCoreCommerceWorkflowContractsProposal,checkCoreCommerceEntryContractsProposal} from '../../src/commerce/commerce-core-role-contracts.js';
const model=`module Demo version 1
entity Counter:
  id UInt64
  amount UInt64
  version UInt64
  identity id
  immutable id
interface Native:
  kind native-producer
  abi craft.fixture/v1-candidate
  custody private-registered-source-profile-callsite
  fields context.json#/context/properties
  signatures context.json#/context/methods
interface Application:
  kind application-composition
  service demo module Demo
  formal-claims optional
query Read:
  input id UInt64
  context native Native
  source counter Counter
  output optional<UInt64>
  where counter.id == id and counter.id == native.tenantId and native.allowed(counter.amount)
  project counter.amount
  on-missing return none
  on-unavailable fail unavailable
query Wrapper:
  input id UInt64
  context native Native
  output optional<UInt64>
  delegates Read(id=id)
  effects none
operation Apply:
  input id UInt64
  input increment UInt64
  context native Native
  output UInt64
  read counter Counter by id=id
    on-missing reject missing
    on-unavailable fail outcome-unknown
  requires increment > 0 and native.allowed(increment)
  transaction Change:
    atomic-participants Counter
    update changed Counter by id=id expected-version counter.version:
      amount <- counter.amount + increment
      version <- counter.version + 1
    on-version-conflict reject contention
    on-unknown-commit fail outcome-unknown
  return changed.amount
`;
const sources=()=>[{path:'application.alch',text:model}];
const assets=()=>[{path:'context.json',text:JSON.stringify({source_module:'Demo@1',context:{abi:'craft.fixture/v1-candidate',properties:{tenantId:'UInt64'},methods:{allowed:{parameters:['UInt64'],result:'Bool'}}}})}];
const clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
const find=(value:any,op:string):any=>{if(!value||typeof value!=='object')return undefined;if(value.op===op)return value;for(const child of Object.values(value)){const result=find(child,op);if(result)return result;}return undefined;};
const invalid=(run:()=>unknown)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&e.diagnostics[0]!.code==='InvalidContract');
let physical:ReturnType<typeof loadActual>|undefined;
function loadActual(){
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),owner=createCoreCommerceSourceOwner(),handle=owner.prepare(root),capture=owner.inspect(handle),paths=new Set(capture.reconstruction.modules.map(m=>m.path)),source=capture.files.filter(f=>paths.has(f.path)),asset=capture.files.filter(f=>f.path.endsWith('.json'));
 const contracts={reads:createCoreCommerceReadContracts(source,asset),effects:createCoreCommerceEffectContracts(source,asset),workflows:createCoreCommerceWorkflowContracts(source,asset),entries:createCoreCommerceEntryContracts(source,asset)};owner.assertCurrent(handle);return {owner,handle,capture,source,asset,contracts};
}
const actual=()=>physical??=loadActual();after(()=>{if(physical){physical.owner.assertCurrent(physical.handle);physical.owner.dispose(physical.handle);}});
test('physical zero-claim ecommerce source produces 55 separate role contracts',()=>{const f=actual(),c=f.contracts;assert.deepEqual(Object.values(c).map(rows=>rows.length),[13,19,1,22]);assert.equal(f.capture.reconstruction.modules.flatMap(m=>m.declarations).filter(d=>d.surface==='FormalClaim').length,0);assert.ok(Object.values(c).flat().every(r=>r.qualification==='independent-source-role-contract-data-only'&&!Object.hasOwn(r,'native_owner')));assert.ok(Object.values(c).every(rows=>Object.isFrozen(rows)));});
test('local Query retains its scoped read, original keys, lazy native predicate and private fields',()=>{const q=createCoreCommerceReadContracts(sources(),assets())[0]!;assert.equal(q.kind,'local');if(q.kind==='local'){assert.deepEqual(q.sources[0]!.lookup_key,['id']);assert.equal(q.wrap_projection_some,true);assert.equal(q.cross_service_tables,false);assert.equal(q.predicate.expression.op,'binary');assert.equal(find(q.predicate.expression,'native_observation').method,'allowed');assert.deepEqual(find(q.predicate.expression,'private_context').fields,{tenantId:{kind:'scalar',name:'UInt64'}});assert.equal(Object.hasOwn(q.predicate,'native_calls'),false);assert.equal(Object.hasOwn(q.predicate,'source'),false);}});
test('delegation retains typed source-ordered inputs and original context forwarding',()=>{const q=createCoreCommerceReadContracts(sources(),assets())[1]!;assert.equal(q.kind,'delegated');if(q.kind==='delegated'){assert.equal(q.target,'Demo.Read');assert.deepEqual(q.arguments.map(a=>a.parameter),['id']);assert.deepEqual(q.forwarded_contexts,[{parameter:'native',binding:'native',source_type:'Demo.Native'}]);}});
test('native protocol Query keeps declared comparison/binding without an invented service',()=>{const q=actual().contracts.reads.find(q=>q.kind==='native-protocol')!;assert.equal(q.service,null);if(q.kind==='native-protocol'){assert.equal(q.protocol,'DemoPay-v1');assert.equal(q.native_qualification,'requires-original-producer-and-profile');assert.ok(q.compare_rule.length);assert.ok(q.binding_path.length);}});
test('Operation source order and transaction boundaries remain separate',()=>{const o=createCoreCommerceEffectContracts(sources(),assets())[0]!;assert.deepEqual(o.body.map(s=>s.kind),['read','guard','transaction','action']);const step=o.body[2]!;assert.equal(step.kind,'transaction');if(step.kind==='transaction'){const mutation=step.transaction.body[0]!;assert.equal(mutation.kind,'mutation');if(mutation.kind==='mutation'){assert.equal(mutation.version_validation,'original-row+expected-version+exact-one-increment-before-write');assert.equal(mutation.original_row,'required-for-exact-key-and-store');assert.ok(mutation.expected_version);}}});
test('transaction rollback and unresolved commit channels retain their original evidence requirements',()=>{const step=createCoreCommerceEffectContracts(sources(),assets())[0]!.body.find(s=>s.kind==='transaction')!;if(step.kind!=='transaction')assert.fail();const t=step.transaction;assert.equal(t.handlers.find(h=>h.channel==='on-version-conflict')!.requires,'original-proven-rollback');const unknown=t.handlers.find(h=>h.channel==='on-unknown-commit')!;assert.equal(unknown.requires,'original-unresolved-commit');assert.equal(unknown.retain_original,true);assert.ok(t.defaults.length>0);});
test('native-capture and replay conformance retain explicit noninvoking/owner-required modes',()=>{const rows=actual().contracts.effects.filter(o=>o.protocol);assert.equal(rows.length,2);assert.ok(rows.some(o=>o.protocol!.kind==='ordered-replay'&&o.protocol!.invocation==='forbidden-conformance-only'));assert.ok(rows.some(o=>o.protocol!.kind==='native-capture'&&o.protocol!.invocation==='requires-original-external-producer'));assert.ok(rows.every(o=>o.service===null));});
test('Workflow preserves ownership fields, drivers, original observations and fixed suspension defaults',()=>{const w=actual().contracts.workflows[0]!;assert.equal(w.service,'orders');assert.deepEqual(w.drivers.map(d=>d.kind),['snapshot','claim','observation']);assert.ok(w.ownership.every(o=>Object.hasOwn(o,'field')&&Object.hasOwn(o,'type')));const observation=w.drivers.find(d=>d.kind==='observation')!;assert.ok(observation.inspection);assert.equal(observation.call.authorization,'fresh-original-entry-decision-before-invocation');assert.equal(w.defaults.max_transitions_per_resume,64);assert.equal(w.defaults.transition_limit,'suspend-retaining-original-journal');assert.equal(w.steps.length,15);assert.equal(w.resume.length,16);assert.equal(w.terminals.length,2);assert.ok(w.terminals.every(t=>t.effects==='none'&&t.on_false==='suspend-same-state'));});
test('entry contracts keep permission inline, exact private fields/origins and fresh decision requirements',()=>{const entries=actual().contracts.entries;assert.ok(entries.every(e=>e.access.permission&&e.access.auth_permission.resource&&e.access.resource_condition));assert.ok(entries.some(e=>e.access.permission==='orders.read-own'));assert.ok(entries.every(e=>e.access.current_action==='before-replay-and-effects'&&e.access.invocation_decision==='fresh-separate-original-entry-decision'));const bindings=entries.flatMap(e=>e.access.resource_bindings);assert.ok(bindings.some(b=>b.type.kind==='private-projection'&&Object.keys(b.fields).length>0));assert.ok(bindings.every(b=>b.custody==='required-from-original-registered-owner'&&b.public_constructor==='forbidden'));assert.ok(entries.some(e=>e.access.resource_condition!.local_records.length>0));});
test('event entries retain concrete Event inputs and committed completion evidence',()=>{const entries=actual().contracts.entries.filter(e=>e.interaction==='event');assert.equal(entries.length,2);assert.ok(entries.every(e=>e.event_argument!==null&&e.access.producer!==null&&e.access.event_completion==='requires-original-consumer-inbox-and-result-commit'));});
test('matching Query proposal is freshly reconstructed data, without restored ownership',()=>{const proposal=clone(createCoreCommerceReadContracts(sources(),assets())),checked=checkCoreCommerceReadContractsProposal(sources(),assets(),proposal);assert.deepEqual(checked,proposal);assert.notEqual(checked,proposal);assert.equal(Object.hasOwn(checked,'accepted'),false);});
for(const [name,edit]of [
 ['native ABI',(p:any)=>find(p,'native_observation').abi='foreign'],
 ['native method position',(p:any)=>{const q=p[0];q.predicate.expression={op:'literal',type:{kind:'scalar',name:'Bool'},value:true};}],
 ['private context fields',(p:any)=>find(p,'private_context').fields={}],
 ['key selection',(p:any)=>p[0].sources[0].lookup_key=['amount']],
 ['claimed owner',(p:any)=>p[0].native_owner={accepted:true}],
]as const)test('fresh Query proposal rejects altered '+name,()=>{const p=clone(createCoreCommerceReadContracts(sources(),assets()));edit(p);invalid(()=>checkCoreCommerceReadContractsProposal(sources(),assets(),p));});
for(const [name,edit]of [
 ['source order',(p:any)=>p[0].body.reverse()],
 ['unknown-commit retention',(p:any)=>p[0].body[2].transaction.handlers.find((h:any)=>h.channel==='on-unknown-commit').retain_original=false],
 ['expected version',(p:any)=>p[0].body[2].transaction.body[0].expected_version=null],
]as const)test('fresh Operation proposal rejects altered '+name,()=>{const p=clone(createCoreCommerceEffectContracts(sources(),assets()));edit(p);invalid(()=>checkCoreCommerceEffectContractsProposal(sources(),assets(),p));});
test('Workflow proposal cannot erase observation requirements or recover ownership from matching JSON',()=>{const f=actual(),p=clone(f.contracts.workflows);(p[0]!.drivers[2]!.requirements as string[]).splice(0);invalid(()=>checkCoreCommerceWorkflowContractsProposal(f.source,f.asset,p));const checked=checkCoreCommerceWorkflowContractsProposal(f.source,f.asset,clone(f.contracts.workflows));assert.notEqual(checked,f.contracts.workflows);assert.equal(Object.hasOwn(checked,'native_owner'),false);});
test('entry proposal rejects permission changes and erased private projection fields',()=>{const f=actual(),p=clone(f.contracts.entries) as any[];p[0].access.auth_permission.action='other-action';invalid(()=>checkCoreCommerceEntryContractsProposal(f.source,f.asset,p));const altered=clone(f.contracts.entries) as any[];altered.find(e=>e.access.resource_bindings.some((b:any)=>b.type.kind==='private-projection')).access.resource_bindings.find((b:any)=>b.type.kind==='private-projection').fields={};invalid(()=>checkCoreCommerceEntryContractsProposal(f.source,f.asset,altered));});
test('proposal getters reject without invocation',()=>{let called=false;const proposal={get reads(){called=true;return [];}};invalid(()=>checkCoreCommerceReadContractsProposal(sources(),assets(),proposal));assert.equal(called,false);});
test('closed expression schemas reject native/private/unknown-key strengthening and preserve the pure boundary',()=>{
 const q=createCoreCommerceReadContracts(sources(),assets())[0]!;if(q.kind!=='local')assert.fail();const value=clone(q.predicate),native=find(value,'native_observation'),privateContext=find(value,'private_context');
 const cases:{file:string;definition:string;value:any;expected:boolean}[]=[];const add=(definition:string,value:any,expected:boolean,file='commerce-read-v1.schema.json')=>cases.push({file,definition,value,expected});
 add('RoleExpression',value,true);add('FlowExpr',native,true);add('FlowExpr',privateContext,true);
 add('FlowExpr',{...native,custody:'granted'},false);add('FlowExpr',{...privateContext,public_constructor:true},false);add('FlowExpr',{...native,executable_callback:'process'},false);add('FlowExpr',{op:'unknown'},false);
 add('Expr',native,false,'iteration-expression-v2.schema.json');add('Expr',privateContext,false,'iteration-expression-v2.schema.json');
 const missing=clone(value) as any;delete missing.result;add('RoleExpression',missing,false);const local={...value,local_records:[{name:'Demo.Private',fields:{version:{kind:'scalar',name:'UInt64'}},public_constructor:false,qualification:'source-local-projection-data-only'}]};add('RoleExpression',local,true);add('RoleExpression',{...local,local_records:[{...local.local_records[0],public_constructor:true}]},false);
 const cwd=fileURLToPath(new URL('../../',import.meta.url)),code='import json,jsonschema,sys,pathlib\nr=pathlib.Path(sys.argv[1]);items=json.load(sys.stdin);out=[]\nfor x in items:\n s=json.loads((r/"contracts"/x["file"]).read_text());s["$ref"]="#/$defs/"+x["definition"];out.append(jsonschema.Draft202012Validator(s).is_valid(x["value"]))\nprint(json.dumps(out))';
 const result=spawnSync('python3',['-c',code,cwd],{input:JSON.stringify(cases),encoding:'utf8',maxBuffer:1048576});assert.equal(result.status,0,result.stderr);assert.deepEqual(JSON.parse(result.stdout),cases.map(c=>c.expected));
});
