/** Original callsite/callee components; no original Operation execution claim.
 * Open Questions: docs/COMMERCE-COMPUTATION-CALLS.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,cpSync,rmSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {stripTypeScriptTypes} from 'node:module';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCoreCommerceEffectContracts} from '../../src/commerce/commerce-core-role-contracts.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommercePureCallOwner,assertCommercePureCallOwner} from '../../src/commerce/commerce-computation-call-owner.js';
import {compileCommercePureCallBundle} from '../../src/commerce/commerce-computation-call-native.js';
const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),limits=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/pure-producer-model-09.json',import.meta.url),'utf8')).limits,bytes=(v:unknown)=>new TextEncoder().encode(JSON.stringify(v)),sha=(v:string|Uint8Array)=>createHash('sha256').update(v).digest('hex');
async function setup(root:string){
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root),data=sources.inspect(capture),modulePaths=new Set(data.reconstruction.modules.map(m=>m.path)),texts=data.files.filter(f=>modulePaths.has(f.path)),assets=data.files.filter(f=>f.path.endsWith('.json')),plans=createCoreCommerceEffectContracts(texts,assets),semantics=createCoreCommerceSemanticOwner(sources),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(root,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits)),calls=createCommercePureCallOwner(stage,source,domain,baseline),cache=new Map<string,any>();
 return {stage,source,domain,baseline,calls,plans,plan(name:string){return plans.find(p=>p.operation.module+'.'+p.operation.name===name)!;},bind(name:string,path:string){const key=name+path;if(!cache.has(key))cache.set(key,calls.bind(this.plan(name),path));return cache.get(key);}};
}
let actual:Awaited<ReturnType<typeof setup>>,fixture:Awaited<ReturnType<typeof setup>>,fixtureRoot:string;
const extra=`
rule BridgePositive:
  input value UInt64
  expression value > 0
calculation BridgeDivide:
  pure
  input value UInt64
  result UInt64
  expression 6 / value
  on-evaluation-error fail inner-failed
operation BridgeComposed:
  input value UInt64
  output UInt64
  requires BridgePositive(value) and value < 5 on-false reject no-pass
  let result = BridgeDivide(value) on-error reject caller-failed
  return result
operation BridgeDirect:
  input value UInt64
  output UInt64
  requires BridgePositive(value) on-false reject no-pass
  return value
operation BridgeNamed:
  input value UInt64
  output UInt64
  let result = BridgeDivide(value=value) on-error reject caller-failed
  return result
operation BridgeHandler:
  input value UInt64
  output UInt64
  let result = BridgeDivide(value) on-error return BridgeDivide(0)
  return result
operation BridgeReturn:
  input value UInt64
  output UInt64
  requires BridgePositive(value) on-false return 7
  return value
entity BridgeCounter:
  id UInt64
  amount UInt64
  version UInt64
  identity id
  immutable id
operation BridgeTransactional:
  input id UInt64
  input value UInt64
  output UInt64
  transaction Change:
    atomic-participants BridgeCounter
    requires BridgePositive(value) on-false reject tx-invalid
    let amount = BridgeDivide(value) on-error fail tx-calc-failed
    create counter BridgeCounter:
      id <- id
      amount <- amount
      version <- 1
  return value
`;
before(async()=>{actual=await setup(candidate);fixtureRoot=mkdtempSync(path.join(tmpdir(),'commerce-source-calls-'));cpSync(candidate,fixtureRoot,{recursive:true});const file=path.join(fixtureRoot,'application.alch');writeFileSync(file,readFileSync(file,'utf8')+extra);const ids=path.join(fixtureRoot,'contracts/contract-identities.json'),v=JSON.parse(readFileSync(ids,'utf8')),r=v.modules.find((r:any)=>r.artifact.path==='application.alch'),content=readFileSync(file);r.artifact.sha256=sha(content);r.artifact.bytes=content.length;writeFileSync(ids,JSON.stringify(v,null,2)+'\n');fixture=await setup(fixtureRoot);});
after(()=>{if(fixtureRoot)rmSync(fixtureRoot,{recursive:true,force:true});});
const value=(r:any)=>{assert.equal(r.observation.result.ok,true,JSON.stringify(r));return JSON.parse(new TextDecoder().decode(r.observation.result.wire));};
const failure=(r:any,code:string)=>{assert.equal(r.observation.result.ok,false);assert.equal(r.observation.result.error.code,code);return r;};
test('original PlaceOrder call layouts bind source selector/span,exact arguments and original caller actions',()=>{
 const plan=actual.plan('Orders.PlaceOrder'),paths=actual.calls.paths(plan);for(const index of [18,19,20])assert.ok(paths.includes('$.body['+index+'].'+(index===19?'condition':'value')+'.expression'));
 const subtotal=actual.calls.inspect(actual.bind('Orders.PlaceOrder','$.body[18].value.expression'));assertCommercePureCallOwner(actual.calls);assert.equal(subtotal.callee.declaration,'Orders.MerchandiseSubtotal');assert.equal(subtotal.caller,'Orders.PlaceOrder');assert.equal(subtotal.source.module,'Orders');assert.equal(subtotal.span.path,'services/orders.alch');assert.deepEqual(subtotal.arguments,[{op:'field',value:{op:'var',name:'quote'},field:'lines'}]);assert.equal(subtotal.adapter.on_error!.code,'calculation-failed');assert.equal(subtotal.direct_role_call,true);assert.ok(Object.isFrozen(subtotal.role_expression));assert.match(subtotal.qualification,/not-operation-native-or-application-execution/);
 const guard=actual.calls.inspect(actual.bind('Orders.PlaceOrder','$.body[19].condition.expression'));assert.equal(guard.adapter.direct_guard,true);assert.equal(guard.adapter.on_false!.code,'quote-ineligible');assert.equal(guard.acquisition_requirements.length,1);assert.equal(guard.acquisition_requirements[0]!.node.op,'private_context');assert.match(guard.input_contract,/original-argument-evaluation-order-and-native-custody-required/);
});
test('actual bound subtotal and payable computations evaluate declared business values',()=>{
 const subtotal=actual.bind('Orders.PlaceOrder','$.body[18].value.expression'),r=actual.calls.evaluateBoundParameters(subtotal,bytes({lines:[{sku:'A',quantity:'2',unitPriceMinor:'1200'},{sku:'B',quantity:'1',unitPriceMinor:'600'}]}));assert.equal(value(r),'3000');assert.equal(r.decision,'value');assert.equal(r.source_action,null);
 const payable=actual.bind('Orders.PlaceOrder','$.body[20].value.expression'),out=actual.calls.evaluateBoundParameters(payable,bytes({subtotal:'3000',discountMinor:'200',taxMinor:'216',shippingMinor:'300'}));assert.equal(value(out),'3316');
});
const quote={id:'q1',customerId:'c1',currency:'USD',lines:[{sku:'A',quantity:'1',unitPriceMinor:'100'}],discountMinor:'0',taxMinor:'0',shippingMinor:'0',expiresAtEpochMs:'20',version:'1'};
test('actual completed guard true/false differs from validation and evaluation errors',()=>{
 const h=actual.bind('Orders.PlaceOrder','$.body[19].condition.expression'),input={quote,customerId:'c1',nowEpochMs:'10',subtotal:'100'},good=actual.calls.evaluateBoundParameters(h,bytes(input)),bad=actual.calls.evaluateBoundParameters(h,bytes({...input,customerId:'c2'}));assert.equal(value(good),true);assert.equal(good.decision,'guard-true');assert.equal(value(bad),false);assert.equal(bad.decision,'guard-false');assert.equal(bad.source_action.code,'quote-ineligible');assert.equal(bad.action_requirement,'requires-original-caller-to-apply-source-action');
 const malformed=failure(actual.calls.evaluateBoundParameters(h,bytes({...input,subtotal:100})),'InputType');assert.equal(malformed.decision,'parameter-validation-error');assert.equal(malformed.source_action,null);
});
test('actual arithmetic failure keeps source fault and both callee/caller error information',()=>{const h=actual.bind('Orders.PlaceOrder','$.body[20].value.expression'),r=failure(actual.calls.evaluateBoundParameters(h,bytes({subtotal:'0',discountMinor:'1',taxMinor:'0',shippingMinor:'0'})),'ArithmeticUnderflow');assert.equal(r.decision,'evaluation-error');assert.equal(r.source_action.code,'calculation-failed');assert.deepEqual(r.observation.declared_actions,[{declaration:'Orders.PayableTotal',action:{kind:'fail',code:'calculation-failed'}}]);assert.deepEqual(r.observation.result.error.call_path,['Orders.PayableTotal']);});
test('composed guards do not mistake one callee Bool for the enclosing condition',()=>{const path=fixture.calls.paths(fixture.plan('Shop.Application.BridgeComposed')).find(p=>p.includes('.condition.expression.left'))!,h=fixture.bind('Shop.Application.BridgeComposed',path),r=fixture.calls.evaluateBoundParameters(h,bytes({value:'0'}));assert.equal(value(r),false);assert.equal(r.decision,'value');assert.equal(r.source_action,null);assert.equal(fixture.calls.inspect(h).direct_role_call,false);});
test('named arguments retain whole hygienic lets and exact invocation site',()=>{const p=fixture.calls.paths(fixture.plan('Shop.Application.BridgeNamed'))[0]!,h=fixture.bind('Shop.Application.BridgeNamed',p),v=fixture.calls.inspect(h);assert.equal(v.role_expression.expression.op,'let');assert.match(v.expression_path,/\.body$/);assert.equal(v.direct_role_call,true);const r=failure(fixture.calls.evaluateBoundParameters(h,bytes({value:'0'})),'DivideByZero');assert.equal(r.source_action.kind,'reject');assert.equal(r.source_action.code,'caller-failed');assert.equal(r.observation.declared_actions[0].action.code,'inner-failed');});
test('transaction false/error action proposals require original proven rollback',()=>{const name='Shop.Application.BridgeTransactional',paths=fixture.calls.paths(fixture.plan(name));for(const p of paths){const h=fixture.bind(name,p),v=fixture.calls.inspect(h),r=fixture.calls.evaluateBoundParameters(h,bytes({value:'0'}));assert.equal(v.adapter.requires_rollback,true);assert.equal(r.action_requirement,'requires-original-proven-rollback-before-source-action');assert.equal(r.source_action.code,v.callee.kind==='Rule'?'tx-invalid':'tx-calc-failed');}});
test('return source actions stay references and are never executed by the pure adapter',()=>{const name='Shop.Application.BridgeReturn',p=fixture.calls.paths(fixture.plan(name))[0]!,h=fixture.bind(name,p),r=fixture.calls.evaluateBoundParameters(h,bytes({value:'0'}));assert.equal(value(r),false);assert.equal(r.source_action.kind,'return');assert.equal(r.source_action.code,null);assert.match(r.source_action.subject_sha256,/^[a-f0-9]{64}$/);assert.ok(!Object.hasOwn(r.source_action,'value'));});
for(const [label,edit]of [
 ['caller branch',(p:any)=>p.body[19].on_false.code='invented'],['source argument',(p:any)=>p.body[18].value.expression.arguments[0].field='invented'],['native custody',(p:any)=>p.body[19].condition.expression.arguments[1].value.custody='caller-says-so'],['pure callback',(p:any)=>p.body[18].value.callback=()=>0],['fabricated budget',(p:any)=>p.limits=limits],
]as const)test('source correspondence rejects changed '+label,()=>{const p=structuredClone(actual.plan('Orders.PlaceOrder'));edit(p);assert.throws(()=>actual.calls.bind(p,'$.body[18].value.expression'));});
test('accessors and proxies reject before invoking user code',()=>{let invoked=false;const plan=actual.plan('Orders.PlaceOrder'),bad={get operation(){invoked=true;return plan.operation;}};assert.throws(()=>actual.calls.bind(bad as any,'$.body[18].value.expression'));assert.throws(()=>actual.calls.bind(new Proxy(plan,{ownKeys(){invoked=true;return [];}}),'$.body[18].value.expression'));assert.equal(invoked,false);});
test('owner and token clones,serialized inspections and foreign factories cannot supply custody',()=>{const h=actual.bind('Orders.PlaceOrder','$.body[18].value.expression');for(const fake of [{...h},new Proxy(h,{}),actual.calls.inspect(h)])assert.throws(()=>actual.calls.inspect(fake as any),(e:any)=>e.diagnostics[0].code==='ForeignOwner');assert.throws(()=>assertCommercePureCallOwner({...actual.calls}));const other=createCommercePureCallOwner(actual.stage,actual.source,actual.domain,actual.baseline);assert.throws(()=>other.inspect(h));assert.throws(()=>compileCommercePureCallBundle({...actual.calls},h));assert.throws(()=>createCommercePureCallOwner({...actual.stage},actual.source,actual.domain,actual.baseline));assert.throws(()=>createCommercePureCallOwner(actual.stage,actual.source,{...actual.domain},actual.baseline));});
test('non-call metadata and unknown paths cannot manufacture a source call',()=>{for(const path of ['$.body[18]','$.body[18].value','$.body[19].condition.expression.arguments[1].value','$.body[999].value.expression'])assert.throws(()=>actual.calls.bind(actual.plan('Orders.PlaceOrder'),path));});
test('disposing one derived binding leaves another original binding usable',()=>{const plan=actual.plan('Orders.PlaceOrder'),one=actual.calls.bind(plan,'$.body[18].value.expression'),two=actual.calls.bind(plan,'$.body[18].value.expression');actual.calls.dispose(one);assert.throws(()=>actual.calls.assertCurrent(one),(e:any)=>e.diagnostics[0].code==='DisposedOwner');actual.calls.assertCurrent(two);});
test('generated callee/adapter bundles execute their own members with source-bound outcomes',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-call-generated-'));try{writeFileSync(path.join(root,'package.json'),'{"type":"module"}');for(const [caller,p,input]of [['Orders.PlaceOrder','$.body[20].value.expression',{subtotal:'0',discountMinor:'1',taxMinor:'0',shippingMinor:'0'}],['Orders.PlaceOrder','$.body[19].condition.expression',{quote,customerId:'c2',nowEpochMs:'10',subtotal:'100'}],['Shop.Application.BridgeNamed',fixture.calls.paths(fixture.plan('Shop.Application.BridgeNamed'))[0]!,{value:'0'}]]as const){const f=caller==='Orders.PlaceOrder'?actual:fixture,h=f.bind(caller,p),bundle=compileCommercePureCallBundle(f.calls,h),template='function '+readFileSync(new URL('../../src/commerce/commerce-computation-call-runtime.ts',import.meta.url),'utf8').split('export function ')[1]!;const adapter=bundle.files.find(x=>x.path===bundle.manifest.entrypoint)!;assert.ok(adapter.text.includes(template));assert.doesNotMatch(adapter.text,/"op":|eval\(|new Function\(/);for(const member of bundle.files){const expected=bundle.manifest.members.find(m=>m.path===member.path)!;assert.equal(sha(member.text),expected.sha256);writeFileSync(path.join(root,member.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(member.text));}const generated=await import(pathToFileURL(path.join(root,bundle.manifest.entrypoint.replace(/\.ts$/,'.js'))).href);assert.deepEqual(generated.evaluateBoundParameters(bytes(input)),f.calls.evaluateBoundParameters(h,bytes(input)));assert.equal(bundle.manifest.members.length,2);assert.equal(bundle.manifest.source_call.caller,caller);}}finally{rmSync(root,{recursive:true,force:true});}
});
test('a call inside an error handler cannot recursively inherit that same handler',()=>{const name='Shop.Application.BridgeHandler',paths=fixture.calls.paths(fixture.plan(name)),body=paths.find(p=>p.includes('.value.expression'))!,handler=paths.find(p=>p.includes('.on_error.value.expression'))!;assert.ok(handler);const bh=fixture.bind(name,body),hh=fixture.bind(name,handler),fromBody=failure(fixture.calls.evaluateBoundParameters(bh,bytes({value:'0'})),'DivideByZero'),fromHandler=failure(fixture.calls.evaluateBoundParameters(hh,bytes({value:'0'})),'DivideByZero');assert.equal(fromBody.source_action.kind,'return');assert.equal(fromHandler.source_action,null);assert.equal(fixture.calls.inspect(hh).adapter.on_error,null);});
test('original parent disposal invalidates call evaluation and generation',()=>{const name='Shop.Application.BridgeDirect',p=fixture.calls.paths(fixture.plan(name))[0]!,h=fixture.bind(name,p);fixture.domain.dispose(fixture.baseline);for(const run of [()=>fixture.calls.inspect(h),()=>fixture.calls.evaluateBoundParameters(h,bytes({value:'1'})),()=>compileCommercePureCallBundle(fixture.calls,h)])assert.throws(run,(e:any)=>e.diagnostics[0].code==='DisposedOwner');});
