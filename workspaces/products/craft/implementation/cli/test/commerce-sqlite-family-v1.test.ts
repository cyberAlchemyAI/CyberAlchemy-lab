/** Real generated SQLite schema/statement/conversion controls in private fixtures.
 * No Auth/transaction/row capability or live business DB is constructed.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,readFileSync,writeFileSync,cpSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
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
import {createCommerceSqliteFamilyOwnerV1,assertCommerceSqliteFamilyOwnerV1} from '../src/commerce/commerce-sqlite-family-v1.js';
import {deriveCommerceSqliteTableV1,deriveCommerceSqliteQueryV1} from '../src/commerce/commerce-sqlite-generation-v1.js';
import {compilePersistenceCompositionV2} from '../src/system-integration/persistence-v2.js';
const cli=fileURLToPath(new URL('../',import.meta.url)),repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),base=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC16'),candidate=path.join(repo,'examples/ecommerce-target-candidate');
let root:string,sourceRoot:string,sources:any,capture:any,semantics:any,semantic:any,stage:any,source:any,domain:any,baseline:any,plans:any,models:any,families:any,family:any,variantFamily:any,owner:any,variant:any,values:any;
const services=new Map<string,any>(),components=new Map<string,any>(),bundles=new Map<string,any>(),dbs=new Map<string,DatabaseSync>();
const code=(c:string)=>(e:any)=>e?.code===c||e?.diagnostics?.[0]?.code===c;
before(async()=>{
 root=mkdtempSync(path.join(base,'sqlite-family-controls-'));sourceRoot=path.join(root,'source');cpSync(candidate,sourceRoot,{recursive:true,force:false,errorOnExist:true});
 sources=createCoreCommerceSourceOwner();capture=sources.prepare(sourceRoot);const actual=sources.inspect(capture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),texts=actual.files.filter((f:any)=>paths.has(f.path)),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 semantics=createCoreCommerceSemanticOwner(sources);semantic=semantics.check(capture);stage=createCoreCommerceStageSourceOwner(sources,semantics);source=await stage.prepare(sourceRoot,'application.alch');domain=createCommerceComputationDomainOwner(stage,source);baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));values=domain.inspect(baseline).contract.values;plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 models=createCommerceTechnicalModelOwnerV5();families=createCommerceFamilyOwnerV5(models);const model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),scope={kind:'local-effects' as const,omitted_capabilities:'unsupported-not-silently-executed' as const,targets:[{module:'Orders',name:'PlaceOrder',role:'Operation' as const}]},parameters=stage.inspect(source).application.parameters;family=families.derive(model,parameters,scope);variantFamily=families.derive(model,{...parameters,tablePrefix:'sample_'},scope);
 owner=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,family);variant=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,variantFamily);
 for(const id of ['catalog','orders','inventory','payments','fulfillment']){const h=owner.bindService(id),bundle=owner.materialize(h,path.join(root,id)),data=await owner.loadDataComponent(bundle),db=new DatabaseSync(':memory:');db.exec(owner.inspectService(h).migration_sql);services.set(id,h);bundles.set(id,bundle);components.set(id,data);dbs.set(id,db);}
 const v=variant.bindService('orders'),b=variant.materialize(v,path.join(root,'variant-orders')),data=await variant.loadDataComponent(b),db=new DatabaseSync(':memory:');db.exec(variant.inspectService(v).migration_sql);services.set('variant-orders',v);bundles.set('variant-orders',b);components.set('variant-orders',data);dbs.set('variant-orders',db);
});
after(()=>{for(const db of dbs.values())db.close();owner?.dispose();variant?.dispose();plans?.dispose();});
function sample(type:any,seed=1,depth=0):any {
 if(depth>12)throw Error('fixture recursion');
 if(type.kind==='scalar')return type.name==='Bool'?false:1n;
 if(type.kind==='literal')return type.value;
 if(type.kind==='string')return 'value-'+seed;
 if(type.kind==='refinement'){const r=values.refinements.find((r:any)=>r.name===type.name);if(r.pattern==='^[a-f0-9]{64}$')return 'a'.repeat(64);if(r.pattern==='^evt_[a-f0-9]{64}$')return 'evt_'+'a'.repeat(64);if(r.pattern==='^[a-z][a-z0-9_]{0,15}$')return 'shop_';if(r.pattern===null)return 'id-'+seed;throw Error('unknown fixture pattern '+r.pattern);}
 if(type.kind==='optional')return {kind:'none'};
 if(type.kind==='list')return Array.from({length:Math.min(type.max_items,Math.max(2,type.min_items))},(_,i)=>sample(type.element,seed*10+i,depth+1));
 if(type.kind==='record'){const r=values.records.find((r:any)=>r.name===type.name),v=Object.fromEntries(Object.entries(r.fields).map(([name,t])=>[name,sample(t,seed,depth+1)]));if(type.name==='Inventory.Stock'){v.onHand=5n;v.reserved=1n;v.allocated=1n;}if(type.name==='Orders.ReplayRecord')v.state='Pending';return v;}
 if(type.kind==='enum'||type.kind==='variant'){const e=values.enums.find((e:any)=>e.name===(type.kind==='variant'?type.enum_name:type.name)),v=type.kind==='variant'?e.variants.find((v:any)=>v.name===type.variant):e.variants[0];return e.variants.every((v:any)=>!Object.keys(v.fields).length)?v.name:{kind:v.name,...Object.fromEntries(Object.entries(v.fields).map(([n,t])=>[n,sample(t,seed,depth+1)]))};}
 throw Error('unknown fixture value shape '+type.kind);
}
function structural(value:any):any {if(Array.isArray(value))return value.map(structural);if(value&&typeof value==='object'){assert.ok([Object.prototype,null].includes(Object.getPrototypeOf(value)),'source value dictionaries must have an admitted data prototype');return Object.fromEntries(Object.entries(value).map(([key,child])=>[key,structural(child)]));}return value;}
function sameValue(actual:any,expected:any,message?:string):void {assert.deepEqual(structural(actual),structural(expected),message);}
function insert(service:string,entity:string,value:any){const c=components.get(service),t=c.inspect().tables.find((t:any)=>t.entity===entity),row=c.encodeStoredRecord(entity,value);dbs.get(service)!.prepare(t.insert_sql).run(...t.columns.map((f:any)=>row[f.name]));return {c,t,row};}
function queryValues(c:any,id:string,parameters:any,contexts:any={}){const q=c.inspect().queries.find((q:any)=>q.id===id),out:any={};for(const s of q.slots){const e=s.expression;if(e.op==='var')out[s.id]=parameters[e.name];else if(e.op==='field'&&e.value.op==='private_context')out[s.id]=contexts[e.value.binding][e.field];else if(e.op==='literal')out[s.id]=e.value;else throw Error('unexpected actual fixture slot '+JSON.stringify(e));}return c.prepareQueryValues(id,out);}
test('genuine family emits all20 explicitly owned tables and initial migrations in actual SQLite',()=>{
 assertCommerceSqliteFamilyOwnerV1(owner);let count=0;
 for(const [id,h]of services){if(id==='variant-orders')continue;const schema=owner.inspectService(h),db=dbs.get(id)!;count+=schema.tables.length;assert.equal(schema.native_runtime_qualified,false);assert.equal(schema.persistence.runtime_guarantees_observed,false);const {composition_digest,integration_kernel,...raw}=schema.persistence,{kernel_digest,...rawKernel}=integration_kernel;assert.deepEqual(compilePersistenceCompositionV2({...raw,integration_kernel:rawKernel}),schema.persistence);const actual=db.prepare("SELECT name FROM sqlite_schema WHERE type='table'").all().map((r:any)=>r.name).sort();assert.deepEqual(actual,schema.tables.map((t:any)=>t.physical_name).sort());const actualIndexes=db.prepare("SELECT name FROM sqlite_schema WHERE type='index'").all().map((r:any)=>r.name).sort(),mappedIndexes=schema.persistence.persistence_mappings.flatMap((m:any)=>m.index_mappings.map((i:any)=>i.physical_name)).sort();assert.deepEqual(actualIndexes,mappedIndexes,'generated index metadata must name actual physical SQLite indexes');for(const t of schema.tables)assert.equal(t.owner,id);}
 assert.equal(count,20);const orders=owner.inspectService(services.get('orders'));assert.ok(orders.tables.some((t:any)=>t.entity==='Shop.Application.StepJournal'&&t.physical_name==='shop_orders_step_journal'));assert.ok(!orders.tables.some((t:any)=>t.entity==='Shop.Implementation.TransportRealization'));
});
test('every generated Entity roundtrips through actual generated insert/key SELECT and native codecs',()=>{
 for(const [id,c]of components){if(id==='variant-orders')continue;for(const t of c.inspect().tables){const value=sample({kind:'record',name:t.entity},20),{row}=insert(id,t.entity,value),key=Object.fromEntries(t.keys[0].map((k:string)=>[k,value[k]])),params=c.encodeStoredKey(t.entity,0,key),stored=dbs.get(id)!.prepare(t.select_key_sql[0]).get(...params);assert.ok(stored,t.entity);sameValue(c.decodeStoredRecord(t.entity,stored),value,t.entity);assert.deepEqual(c.encodeStoredRecord(t.entity,value),row);}}
});
test('UInt64 max and values above safe Number preserve exact SQLite roundtrips without coercion',()=>{
 const entity='Inventory.Stock',v=sample({kind:'record',name:entity},31);v.onHand=18446744073709551615n;v.reserved=0n;v.allocated=0n;v.version=18446744073709551615n;const {c,t}=insert('inventory',entity,v),stored=dbs.get('inventory')!.prepare(t.select_key_sql[0]).get(...c.encodeStoredKey(entity,0,{sku:v.sku}));sameValue(c.decodeStoredRecord(entity,stored),v);assert.throws(()=>c.encodeStoredRecord(entity,{...v,onHand:Number.MAX_SAFE_INTEGER}),code('StorageType'));assert.throws(()=>c.encodeStoredRecord(entity,{...v,onHand:18446744073709551616n}),code('StorageType'));
});
test('ordered nested lists and enums retain original order and full native values',()=>{
 const entity='Catalog.Quote',v=sample({kind:'record',name:entity},32);v.lines=[{sku:'sku-z',quantity:2n,unitPriceMinor:9007199254740993n},{sku:'sku-a',quantity:1n,unitPriceMinor:0n}];const {c,t}=insert('catalog',entity,v),stored=dbs.get('catalog')!.prepare(t.select_key_sql[0]).get(...c.encodeStoredKey(entity,0,{id:v.id})),back=c.decodeStoredRecord(entity,stored);sameValue(back,v);assert.deepEqual(back.lines.map((x:any)=>x.sku),['sku-z','sku-a']);assert.equal(back.currency,'USD');
});
test('optional SQL NULL and algebraic payloads roundtrip without flattening or extra fields',()=>{
 const c=components.get('orders'),entity='Shop.Application.StepJournal',v=sample({kind:'record',name:entity},33),type=values.records.find((r:any)=>r.name===entity).fields.observation;v.observation={kind:'some',value:sample(type.element,33)};const {t}=insert('orders',entity,v),key=Object.fromEntries(t.keys[0].map((n:string)=>[n,v[n]])),stored=dbs.get('orders')!.prepare(t.select_key_sql[0]).get(...c.encodeStoredKey(entity,0,key));sameValue(c.decodeStoredRecord(entity,stored),v);const progress=sample({kind:'record',name:'Orders.CheckoutProgress'},34),row=c.encodeStoredRecord('Orders.CheckoutProgress',progress);assert.equal(row.workerOwner,null);assert.equal(c.decodeStoredRecord('Orders.CheckoutProgress',row).workerOwner.kind,'none');assert.throws(()=>c.decodeStoredRecord('Orders.CheckoutProgress',{...row,workerOwner:'null'}),code('NonCanonicalStorage'));assert.throws(()=>c.decodeStoredRecord('Orders.CheckoutProgress',{...row,unexpected:'true'}),code('StorageType'));
});
test('generated unique indexes and composite replay identity enforce actual SQLite constraints',()=>{
 const c=components.get('orders'),entity='Orders.ReplayRecord',v=sample({kind:'record',name:entity},35),t=c.inspect().tables.find((t:any)=>t.entity===entity);insert('orders',entity,v);assert.throws(()=>c.encodeStoredRecord(entity,{...v,state:'Fresh'}),code('StorageType'));assert.throws(()=>insert('orders',entity,v));const other={...v,logicalEntryId:'different-entry'};insert('orders',entity,other);assert.equal(dbs.get('orders')!.prepare(t.select_key_sql[0]).all(...c.encodeStoredKey(entity,0,Object.fromEntries(t.keys[0].map((n:string)=>[n,v[n]])))).length,1);
 const shipment=sample({kind:'record',name:'Fulfillment.Shipment'},36);insert('fulfillment','Fulfillment.Shipment',shipment);assert.throws(()=>insert('fulfillment','Fulfillment.Shipment',{...shipment,shipmentId:'different-shipment-same-order'}));
});
test('four required Queries bind actual source read owners and preserve missing/unavailable/result mapping',()=>{
 for(const [service,id]of [['catalog','Catalog.ReadQuote'],['orders','Orders.GetOrder'],['payments','Payments.ReadPayment'],['inventory','Inventory.ReadReservation']]){const read=plans.bindRead(id),h=owner.bindQuery(services.get(service!),read),q=owner.inspectQuery(h),c=components.get(service!);assert.equal(q.id,id);assert.equal(q.service,service);assert.equal(q.residual.length,0);const missing=c.queryDisposition(id,'missing'),unavailable=c.queryDisposition(id,'unavailable');assert.equal(missing.kind,service==='orders'?'reject':'return');if(service==='orders')assert.equal(missing.code,'resource-not-found');else assert.equal(missing.value.expression.op,'none');assert.equal(unavailable.kind,'fail');assert.ok(c.queryResultMapping(id).original_native_scope_required);assert.throws(()=>owner.inspectQuery({...h}),code('ForeignOwner'));}
});
test('generated GetOrder and ReadQuote SQL excludes foreign customer rows before exposing candidates',()=>{
 for(const [service,entity,id,key]of [['orders','Orders.Order','Orders.GetOrder','orderId'],['catalog','Catalog.Quote','Catalog.ReadQuote','quoteId']]){const v=sample({kind:'record',name:entity},40),c=components.get(service!);v.customerId='customer-foreign';insert(service!,entity!,v);const params={[key!]:v.id,...service==='catalog'?{customerId:'customer-own'}:{}},ctx={customer:{customerId:'customer-own'}},wrong=queryValues(c,id!,params,ctx);assert.equal(dbs.get(service!)!.prepare(wrong.sql).all(...wrong.values).length,0);const right=queryValues(c,id!,{...params,...service==='catalog'?{customerId:'customer-foreign'}:{}},{customer:{customerId:'customer-foreign'}});assert.equal(dbs.get(service!)!.prepare(right.sql).all(...right.values).length,1);assert.equal(right.requires_original_context_owner,service==='orders');}
});
test('generated ReadPayment and ReadReservation bind exact order/attempt unique-key scope',()=>{
 for(const [service,entity,id]of [['payments','Payments.PaymentAttempt','Payments.ReadPayment'],['inventory','Inventory.Reservation','Inventory.ReadReservation']]){const v=sample({kind:'record',name:entity},41),c=components.get(service!);insert(service!,entity!,v);const wrong=queryValues(c,id!,{orderId:'foreign-order',attemptKey:v.attemptKey});assert.equal(dbs.get(service!)!.prepare(wrong.sql).all(...wrong.values).length,0);const right=queryValues(c,id!,{orderId:v.orderId,attemptKey:v.attemptKey});assert.equal(dbs.get(service!)!.prepare(right.sql).all(...right.values).length,1);}
});
test('private schema/query/bundle handles and data APIs reject foreign-service and JSON substitutions',async()=>{
 assert.throws(()=>owner.inspectService({...services.get('orders')}),code('ForeignOwner'));assert.throws(()=>assertCommerceSqliteFamilyOwnerV1({...owner}),code('ForeignOwner'));assert.throws(()=>owner.bindQuery(services.get('orders'),plans.bindRead('Catalog.ReadQuote')),code('ForeignOwner'));await assert.rejects(owner.loadDataComponent({...bundles.get('orders')}),code('ForeignOwner'));const c=components.get('orders');assert.throws(()=>c.encodeStoredRecord('Inventory.Stock',sample({kind:'record',name:'Inventory.Stock'})),code('ForeignServiceScope'));assert.throws(()=>c.prepareQueryValues('Payments.ReadPayment',{}),code('ForeignServiceScope'));assert.equal(c.qualification,'generated-repository-data-only;not-store-query-row-or-authorization-custody');assert.equal('open'in c,false);assert.equal('execute'in c,false);
});
test('unsupported storage shapes and dropped complete key predicates cannot generate permissive mappings',()=>{
 const service=owner.inspectService(services.get('orders')),t=service.tables[0],bad={...t.record,fields:{...t.record.fields,unimplemented:{kind:'outcome',state:{kind:'scalar',name:'Bool'},intent:{kind:'scalar',name:'Bool'},max_intents:1}}};assert.throws(()=>deriveCommerceSqliteTableV1(bad,'orders','shop_',t.source,values),code('UnsupportedCapability'));const q=owner.inspectQuery(owner.bindQuery(services.get('orders'),plans.bindRead('Orders.GetOrder'))).plan,changed={...q,predicate:{...q.predicate,expression:{op:'literal',type:{kind:'scalar',name:'Bool'},value:true}}};assert.throws(()=>deriveCommerceSqliteQueryV1(changed,service.tables,'orders'),code('UnsupportedCapability'));assert.throws(()=>deriveCommerceSqliteQueryV1(q,owner.inspectService(services.get('catalog')).tables,'orders'),code('InvalidContract'));
});
test('actual checked profile prefix variant changes emitted SQL and actual physical tables',()=>{
 const a=owner.inspectService(services.get('orders')),b=variant.inspectService(services.get('variant-orders'));assert.equal(a.prefix,'shop_');assert.equal(b.prefix,'sample_');assert.notEqual(a.migration_sql,b.migration_sql);assert.notEqual(a.schema_sha256,b.schema_sha256);assert.deepEqual(a.tables.map((t:any)=>t.entity),b.tables.map((t:any)=>t.entity));const actual=dbs.get('variant-orders')!.prepare("SELECT name FROM sqlite_schema WHERE type='table'").all().map((r:any)=>r.name);assert.ok(actual.length>0&&actual.every((n:string)=>n.startsWith('sample_')));assert.ok(!actual.some((n:string)=>n.startsWith('shop_')));const v=sample({kind:'record',name:'Orders.Order'},44),{c,t}=insert('variant-orders','Orders.Order',v),row=dbs.get('variant-orders')!.prepare(t.select_key_sql[0]).get(...c.encodeStoredKey(t.entity,0,{id:v.id}));sameValue(c.decodeStoredRecord(t.entity,row),v);
});
test('generated repository and codec TypeScript check as emitted standalone files',()=>{
 execFileSync(process.execPath,[path.join(cli,'node_modules/typescript/bin/tsc'),'--noEmit','--incremental','false','--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--types','node','--typeRoots',path.join(cli,'node_modules/@types'),path.join(root,'orders/service-repositories.ts'),path.join(root,'orders/commerce-domain-values.ts'),path.join(root,'orders/values-and-codecs.ts')],{cwd:root,encoding:'utf8',stdio:'pipe'});
});
test('original generated module mutation retires its bundle while another source-bound bundle stays current',()=>{
 const b=bundles.get('orders'),row=owner.inspectBundle(b).members.find((m:any)=>m.path.endsWith('/service-repositories.js'));writeFileSync(row.path,readFileSync(row.path,'utf8')+'\n');assert.throws(()=>owner.assertBundleCurrent(b),code('StaleOwner'));owner.assertBundleCurrent(bundles.get('catalog'));
});
test('matching source digest from a second private capture cannot substitute local-plan parents',async()=>{
 const otherCapture=sources.prepare(sourceRoot),otherSemantic=semantics.check(otherCapture),
  otherSource=await stage.prepare(sourceRoot,'application.alch'),
  otherDomain=createCommerceComputationDomainOwner(stage,otherSource),
  actual=sources.inspect(otherCapture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),
  texts=actual.files.filter((f:any)=>paths.has(f.path)),
  limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits,
  otherBaseline=otherDomain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits)),
  otherPlans=createCommerceLocalPlanOwnerV1(sources,otherCapture,semantics,otherSemantic,stage,otherSource,otherDomain,otherBaseline);
 try{
  assert.equal(actual.capture_sha256,sources.inspect(capture).capture_sha256);
  assert.throws(()=>createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,otherPlans,families,family),code('ForeignOwner'));
  owner.assertBundleCurrent(bundles.get('catalog'));
 }finally{otherPlans.dispose();}
});
test('disposed derived family revokes its SQLite owner without retiring a sibling family',()=>{
 families.dispose(variantFamily);assert.throws(()=>variant.assertCurrent(),code('DisposedOwner'));
 owner.assertBundleCurrent(bundles.get('catalog'));
});
test('disposed schema and changed captured source profile revoke dependent repository/query capabilities',()=>{
 const temporary=owner.bindService('catalog');owner.disposeService(temporary);assert.throws(()=>owner.inspectService(temporary),code('DisposedOwner'));const file=path.join(sourceRoot,'profiles/selection.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>owner.assertCurrent(),code('StaleOwner'));assert.throws(()=>owner.assertBundleCurrent(bundles.get('catalog')),code('StaleOwner'));
});
