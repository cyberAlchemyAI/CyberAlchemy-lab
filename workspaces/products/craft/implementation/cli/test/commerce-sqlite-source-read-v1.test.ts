/** Genuine checked source + generated schemas + actual private SQLite reads.
 * Bound keys are explicit data fixtures; no full invocation/entry/argument claim.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,cpSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceSqliteFamilyOwnerV1} from '../src/commerce/commerce-sqlite-family-v1.js';
import {openCommerceSqliteUnitOfWorkV1} from '../profiles/commerce-local-v1-candidate/runtime/sqlite-unit-of-work.js';
import {createCommerceSqliteSourceReadOwnerV1,assertCommerceSqliteSourceReadOwnerV1} from '../profiles/commerce-local-v1-candidate/runtime/source-read-owner.js';
const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),base=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17');
let root:string,plans:any,family:any,effects:any[],reserve:any,stockSite:any;const resources=new Map<string,any>(),bound=new Map<string,any>();
const code=(c:string)=>(e:any)=>e?.code===c||e?.diagnostics?.[0]?.code===c;
const plain=(v:any):any=>Array.isArray(v)?v.map(plain):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,plain(x)])):v;
before(async()=>{
 root=mkdtempSync(path.join(base,'native-source-read-controls-'));const sourceRoot=path.join(root,'source');cpSync(path.join(repo,'examples/ecommerce-target-candidate'),sourceRoot,{recursive:true,errorOnExist:true,force:false});
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),actual=sources.inspect(capture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),texts=actual.files.filter((f:any)=>paths.has(f.path)),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits,semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);effects=semantics.inspect(semantic).effects.filter((p:any)=>p.protocol===null);
 const models=createCommerceTechnicalModelOwnerV5(),families=createCommerceFamilyOwnerV5(models),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),selected=families.derive(model,stage.inspect(source).application.parameters,{kind:'local-effects',omitted_capabilities:'unsupported-not-silently-executed',targets:[{module:'Orders',name:'PlaceOrder',role:'Operation'}]});
 family=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,selected);
 for(const service of ['orders','inventory','payments','fulfillment']){const schema=family.bindService(service),bundle=family.materialize(schema,path.join(root,'repository-'+service)),unit=await openCommerceSqliteUnitOfWorkV1(family,bundle,path.join(root,service+'.sqlite'),'create'),reader=await createCommerceSqliteSourceReadOwnerV1(plans,family,bundle,unit);resources.set(service,{schema,bundle,unit,reader});}
 reserve=plans.bindOperation('Inventory.ReserveStock');stockSite=resources.get('inventory').reader.bind(reserve,'$.body[9].body[0]');
});
after(()=>{for(const r of resources.values()){r.reader.dispose();r.unit.close();}family?.dispose();plans?.dispose();});
const stock={sku:'sku-one',onHand:100n,reserved:0n,allocated:0n,version:1n};
function claim(unit:any,id:string){const result=unit.claimCommand({logicalEntryId:'source-read-fixture',principalId:'component-only',commandId:id,fingerprint:'a'.repeat(64),transactionNamespace:'1'.repeat(64)});assert.equal(result.kind,'claimed');return result.command;}

test('all25 source-local read/count sites bind to original source and actual same-service stores',()=>{
 let count=0;const views:any[]=[];
 for(const effect of effects){const id=effect.operation.module+'.'+effect.operation.name,op=plans.bindOperation(id),r=resources.get(effect.service);assert.ok(r);for(const p of r.reader.paths(op)){const h=r.reader.bind(op,p),v=r.reader.inspect(h);count++;assert.equal(v.operation,id);assert.equal(v.service,effect.service);assert.equal(v.store_id,r.unit.inspect().store_id);assert.equal(v.schema_sha256,r.unit.inspect().schema_sha256);assert.equal(v.qualification,'source-site-and-native-store-only;bound-arguments-and-full-invocation-required');bound.set(id+'/'+p,{op,handle:h,reader:r.reader});views.push(v);}}
 assert.equal(count,25);assert.equal(views.filter(v=>v.kind==='count').length,1);writeFileSync(path.join(root,'source-read-views.json'),JSON.stringify(views,null,2)+'\n');
});
test('source-bound key reads distinguish actual missing row and native stored value with original row custody',()=>{
 const {reader,unit}=resources.get('inventory'),missing=reader.read(stockSite,{sku:'sku-one'});assert.deepEqual(reader.inspectObservation(missing),{kind:'missing'});
 const inserted=unit.apply(claim(unit,'seed-stock'),[{kind:'create',entity:'Inventory.Stock',value:stock}],true);assert.equal(inserted.kind,'committed');const observation=reader.read(stockSite,{sku:'sku-one'}),result=reader.inspectObservation(observation);assert.equal(result.kind,'found');assert.deepEqual(plain(result.value),stock);assert.deepEqual(plain(unit.inspectRow(result.row).value),stock);assert.throws(()=>unit.inspectRow({...result.row}),code('ForeignRow'));
});
test('native count is UInt64 BigInt and read/count observations cannot be interchanged',()=>{
 const site=bound.get('Orders.PlaceOrder/$.body[5]'),r=resources.get('orders'),observation=site.reader.count(site.handle);assert.deepEqual(site.reader.inspectObservation(observation),{kind:'count',value:0n});assert.throws(()=>site.reader.read(site.handle,{}),code('WrongSourceReadKind'));assert.throws(()=>resources.get('inventory').reader.count(stockSite),code('WrongSourceReadKind'));assert.equal(r.unit.countRows('Orders.ReplayRecord'),0);
});
test('repository identity requires the exact original bundle, not an equal-schema replacement',async()=>{
 const r=resources.get('inventory'),other=family.materialize(r.schema,path.join(root,'same-schema-different-bundle'));assert.equal(family.inspectBundle(other).schema_sha256,family.inspectBundle(r.bundle).schema_sha256);assert.throws(()=>r.unit.assertRepository(family,other),code('ForeignRepository'));await assert.rejects(()=>createCommerceSqliteSourceReadOwnerV1(plans,family,other,r.unit),code('ForeignRepository'));assert.throws(()=>r.unit.assertRepository({...family},r.bundle),code('ForeignRepository'));r.unit.assertRepository(family,r.bundle);
});
test('source/store/handle clones and unknown or delegated paths cannot select a lookup',()=>{
 const r=resources.get('inventory'),orders=resources.get('orders'),orderOp=plans.bindOperation('Orders.PlaceOrder');assert.throws(()=>assertCommerceSqliteSourceReadOwnerV1({...r.reader}),code('ForeignOwner'));assert.throws(()=>r.reader.bind({...reserve},'$.body[9].body[0]'),code('ForeignOwner'));assert.throws(()=>r.reader.bind(orderOp,'$.body[3]'),code('ForeignServiceScope'));assert.throws(()=>r.reader.bind(reserve,'$.body[0]'),code('UnknownSourceReadSite'));assert.throws(()=>orders.reader.bind(orderOp,'$.body[15]'),code('UnknownSourceReadSite'));assert.throws(()=>r.reader.read({...stockSite},{sku:'sku-one'}),code('ForeignSite'));assert.throws(()=>orders.reader.read(stockSite,{sku:'sku-one'}),code('ForeignSite'));const observed=r.reader.read(stockSite,{sku:'sku-one'});assert.throws(()=>r.reader.inspectObservation({...observed}),code('ForeignObservation'));assert.throws(()=>orders.reader.inspectObservation(observed),code('ForeignObservation'));
});
test('private source key fields require an original context owner before a row can be read',()=>{
 const r=resources.get('orders'),op=plans.bindOperation('Orders.PlaceOrder'),site=r.reader.bind(op,'$.body[3]'),v=r.reader.inspect(site),key={logicalEntryId:'Orders.Checkout',customerId:'customer-one',checkoutKey:'key-one'};assert.deepEqual(v.private_key_fields,['logicalEntryId','customerId']);assert.throws(()=>r.reader.read(site,key),code('NativeContextCustodyRequired'));assert.throws(()=>r.reader.read(site,key,{owner:{inspectInvocation(){throw Error('fake owner must never execute');}},invocation:{}}),code('ForeignOwner'));assert.equal(r.unit.countRows('Orders.ReplayRecord'),0);
});
test('typed exact keys reject extra fields, JS numbers, accessors and proxies; SQL-like text stays a value',()=>{
 const r=resources.get('inventory');assert.throws(()=>r.reader.read(stockSite,{sku:'sku-one',sql:'DROP TABLE any'}),code('InputType'));assert.throws(()=>r.reader.read(stockSite,{sku:7}),code('StorageType'));let accessed=false;assert.throws(()=>r.reader.read(stockSite,{get sku(){accessed=true;return 'sku-one';}}),code('InputType'));assert.equal(accessed,false);assert.throws(()=>r.reader.read(stockSite,new Proxy({sku:'sku-one'},{})),code('InputType'));const missing=r.reader.read(stockSite,{sku:"sku-one'; DROP TABLE any; --"});assert.deepEqual(r.reader.inspectObservation(missing),{kind:'missing'});assert.equal(r.unit.countRows('Inventory.Stock'),1);
});
test('an actual SQLite exclusive reader conflict is unavailable rather than a fabricated missing row',()=>{
 const r=resources.get('inventory'),db=new DatabaseSync(r.unit.inspect().path,{timeout:0});try{db.exec('BEGIN EXCLUSIVE');assert.throws(()=>r.reader.read(stockSite,{sku:'sku-one'}),code('NativeReadUnavailable'));}finally{db.exec('ROLLBACK');db.close();}const result=r.reader.inspectObservation(r.reader.read(stockSite,{sku:'sku-one'}));assert.equal(result.kind,'found');
});
test('a genuine read snapshot cannot overwrite a later committed version',()=>{
 const r=resources.get('inventory'),old=r.reader.inspectObservation(r.reader.read(stockSite,{sku:'sku-one'}));assert.equal(old.kind,'found');const first=r.unit.apply(claim(r.unit,'advance-stock'),[{kind:'update',row:old.row,expected_version:1n,changes:{reserved:1n,version:2n}}],true);assert.equal(first.kind,'committed');const stale=r.unit.apply(claim(r.unit,'stale-stock'),[{kind:'update',row:old.row,expected_version:1n,changes:{reserved:2n,version:2n}}],true);assert.equal(stale.kind,'version-conflict');const fresh=r.reader.inspectObservation(r.reader.read(stockSite,{sku:'sku-one'}));assert.equal(fresh.value.reserved,1n);assert.equal(fresh.value.version,2n);
});
test('retiring a site or its actual Operation revokes its observations without renewing from data',()=>{
 const r=resources.get('inventory'),op=plans.bindOperation('Inventory.ReserveStock'),site=r.reader.bind(op,'$.body[9].body[0]'),observed=r.reader.read(site,{sku:'sku-one'});r.reader.retire(site);assert.throws(()=>r.reader.inspectObservation(observed),code('RetiredSite'));assert.throws(()=>r.reader.read(site,{sku:'sku-one'}),code('RetiredSite'));const another=plans.bindOperation('Inventory.ReserveStock'),derived=r.reader.bind(another,'$.body[9].body[0]'),snapshot=r.reader.read(derived,{sku:'sku-one'});plans.disposeOperation(another);assert.throws(()=>r.reader.inspectObservation(snapshot),code('DisposedOwner'));
});
