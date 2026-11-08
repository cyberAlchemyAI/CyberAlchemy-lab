/** Source-site + real service-store read ownership. Bound key data alone does
 * not prove its evaluation or a complete authorized Operation invocation.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {dataDigest} from '../../../src/profile-engine/contracts.js';
import {pinCoreImplementation} from '../../../src/commerce/commerce-core-physical.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1,type CommerceLocalOperationInspectionV1} from '../../../src/commerce/commerce-local-plan-owner-v1.js';
import {assertCommerceSqliteFamilyOwnerV1,type CommerceSqliteFamilyOwnerV1,type CommerceRepositoryBundleHandleV1} from '../../../src/commerce/commerce-sqlite-family-v1.js';
import {assertCommerceSqliteUnitOfWorkV1,type CommerceSqliteUnitOfWorkV1,type CommerceSqliteRowV1} from './sqlite-unit-of-work.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceInvocationAuthorizationV1} from '../../../src/commerce/commerce-entry-context-v1.js';
import {isCommerceSourceInvocationOwnerV1,assertCommerceSourceInvocationOwnerV1,type CommerceSourceInvocationOwnerV1} from '../../../src/commerce/commerce-source-invocation-owner-v1.js';
import type {CommerceOperationInvocationHandle} from '../../../src/commerce/commerce-stages-v1.js';
import type {CommerceSqliteTableV1} from '../../../src/commerce/commerce-sqlite-generation-v1.js';
import type {CommerceNativeValue} from '../../../src/commerce/commerce-native-v1.js';
import type {OperationControlStepV1,FlowExprV1} from '../../../src/commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['../../../src/commerce/commerce-local-plan-owner-v1'+ext,'../../../src/commerce/commerce-sqlite-family-v1'+ext,'../../../src/commerce/commerce-core-physical'+ext,'../../../src/commerce/commerce-entry-context-v1'+ext,'../../../src/commerce/commerce-source-invocation-owner-v1'+ext,'sqlite-unit-of-work'+ext,'../../../src/profile-engine/contracts'+ext]);
export class CommerceSqliteSourceReadErrorV1 extends Error {readonly code:string;constructor(code:string){super(code);this.name='CommerceSqliteSourceReadErrorV1';this.code=code;}}
function fail(code:string):never {throw new CommerceSqliteSourceReadErrorV1(code);}
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
function closed(v:unknown,keys:readonly string[]):void {if(!v||typeof v!=='object'||Array.isArray(v)||host.isProxy(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail('InputType');const ds=Object.getOwnPropertyDescriptors(v),names=Reflect.ownKeys(v);if(names.length!==keys.length||names.some(k=>typeof k!=='string'||!keys.includes(k))||keys.some(k=>!ds[k]?.enumerable||!Object.hasOwn(ds[k]!,'value')))fail('InputType');}
export interface CommerceSqliteSourceReadSiteV1 {readonly kind:'original-commerce-native-source-read-site/v1-candidate'}
export interface CommerceSqliteSourceReadObservationV1 {readonly kind:'original-commerce-native-source-read-observation/v1-candidate'}
export type CommerceSqliteSourceReadAuthorizationV1={readonly owner:CommerceEntryContextOwnerV1;readonly invocation:CommerceInvocationAuthorizationV1}|{readonly owner:CommerceSourceInvocationOwnerV1;readonly invocation:CommerceOperationInvocationHandle};
export interface CommerceSqliteSourceReadInspectionV1 {
 readonly operation:string;readonly source_path:string;readonly kind:'read'|'count';readonly entity:string;
 readonly key_index:number|null;readonly key_fields:readonly string[];readonly private_key_fields:readonly string[];
 readonly source_capture_sha256:string;readonly plan_sha256:string;readonly service:string;readonly store_id:string;readonly schema_sha256:string;
 readonly qualification:'source-site-and-native-store-only;bound-arguments-and-full-invocation-required';readonly authority_effect:'none';
}
export type CommerceSqliteSourceReadResultV1={readonly kind:'found';readonly value:CommerceNativeValue;readonly row:CommerceSqliteRowV1}|{readonly kind:'missing'}|{readonly kind:'count';readonly value:bigint};
export interface CommerceSqliteSourceReadOwnerV1 {
 paths(operation:CommerceLocalOperationHandleV1):readonly string[];
 bind(operation:CommerceLocalOperationHandleV1,sourcePath:string):CommerceSqliteSourceReadSiteV1;
 inspect(site:CommerceSqliteSourceReadSiteV1):CommerceSqliteSourceReadInspectionV1;
 read(site:CommerceSqliteSourceReadSiteV1,boundKey:CommerceNativeValue,authorization?:CommerceSqliteSourceReadAuthorizationV1):CommerceSqliteSourceReadObservationV1;
 count(site:CommerceSqliteSourceReadSiteV1,authorization?:CommerceSqliteSourceReadAuthorizationV1):CommerceSqliteSourceReadObservationV1;
 inspectObservation(observation:CommerceSqliteSourceReadObservationV1):CommerceSqliteSourceReadResultV1;
 retire(site:CommerceSqliteSourceReadSiteV1):void;
 assertCurrent():void;dispose():void;
}
type Step=Extract<OperationControlStepV1,{kind:'read'|'count'}>;
type Site={op:CommerceLocalOperationHandleV1;operation:CommerceLocalOperationInspectionV1;step:Step;table:CommerceSqliteTableV1;view:CommerceSqliteSourceReadInspectionV1;privateKeys:readonly {field:string;context:Extract<FlowExprV1,{op:'private_context'}>;property:string;context_path:string}[];retired:boolean};
const owners=new WeakSet<object>();
export function assertCommerceSqliteSourceReadOwnerV1(owner:CommerceSqliteSourceReadOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner');owner.assertCurrent();}

/** Constructs no DB, Query declaration, actor or invocation. Real DB access uses
 * only the source-selected table's generated prepared lookup/count operations. */
export async function createCommerceSqliteSourceReadOwnerV1(plans:CommerceLocalPlanOwnerV1,family:CommerceSqliteFamilyOwnerV1,bundle:CommerceRepositoryBundleHandleV1,store:CommerceSqliteUnitOfWorkV1):Promise<CommerceSqliteSourceReadOwnerV1> {
 assertCommerceLocalPlanOwnerV1(plans);assertCommerceSqliteFamilyOwnerV1(family);assertCommerceSqliteUnitOfWorkV1(store);store.assertRepository(family,bundle);pin.assertCurrent();
 const description=family.inspectBundle(bundle),data=await family.loadDataComponent(bundle),model=data.inspect(),original=store.inspect();store.assertRepository(family,bundle);
 if(model.service!==description.service||original.service!==description.service||original.schema_sha256!==description.schema_sha256)fail('ForeignStore');
 let disposed=false;const sites=new WeakMap<object,Site>(),observations=new WeakMap<object,{site:Site;result:CommerceSqliteSourceReadResultV1}>();
 const base=()=>{if(disposed)fail('DisposedOwner');pin.assertCurrent();plans.assertCurrent();family.assertBundleCurrent(bundle);};
 const current=()=>{base();store.assertRepository(family,bundle);};
 const walk=(op:CommerceLocalOperationHandleV1)=>{base();const view=plans.inspectOperation(op);if(view.source_capture_sha256!==description.source_capture_sha256)fail('ForeignSourceCapture');if(view.plan.service!==description.service)fail('ForeignServiceScope');const found:{path:string;step:Step}[]=[];let nodes=0;
  const scan=(body:readonly OperationControlStepV1[],p:string)=>{for(let i=0;i<body.length;i++){if(++nodes>65536)fail('SourceBound');const step=body[i]!,at=p+'['+i+']';if(step.kind==='count'||step.kind==='read'&&step.entity!==null)found.push({path:at,step});else if(step.kind==='conditional'){scan(step.then,at+'.then');scan(step.otherwise,at+'.otherwise');}else if(step.kind==='read-set')scan(step.body,at+'.body');}};scan(view.plan.body,'$.body');return {view,found};};
 const owned=(handle:CommerceSqliteSourceReadSiteV1)=>{base();const s=handle&&typeof handle==='object'?sites.get(handle):undefined;if(!s)fail('ForeignSite');if(s.retired)fail('RetiredSite');plans.assertOperationCurrent(s.op);return s;};
 const authorization=(s:Site,auth:CommerceSqliteSourceReadAuthorizationV1|undefined,key:CommerceNativeValue|null)=>{
  if(!auth){if(s.privateKeys.length)fail('NativeContextCustodyRequired');return;}
  closed(auth,['owner','invocation']);if(isCommerceSourceInvocationOwnerV1(auth.owner)){assertCommerceSourceInvocationOwnerV1(auth.owner);const original=auth.invocation as CommerceOperationInvocationHandle;auth.owner.assertTarget(original,plans,s.view.source_capture_sha256,s.view.operation);for(const p of s.privateKeys){const projected=auth.owner.context(original,p.context_path) as Readonly<Record<string,CommerceNativeValue>>;if(!Object.hasOwn(projected,p.property)||key===null||dataDigest((key as Readonly<Record<string,CommerceNativeValue>>)[p.field])!==dataDigest(projected[p.property]))fail('ForeignPrivateKey');}return;}assertCommerceEntryContextOwnerV1(auth.owner);const invocation=auth.owner.inspectInvocation(auth.invocation as CommerceInvocationAuthorizationV1);if(invocation.source_sha256!==s.view.source_capture_sha256||invocation.operation!==s.view.operation)fail('ForeignInvocation');
  const principal=auth.owner.inspectScope(auth.owner.principalScope(auth.invocation as CommerceInvocationAuthorizationV1));
  for(const p of s.privateKeys){const expected=p.context.source_type==='Shop.Values.CustomerContext'?'customer':p.context.source_type==='Shop.Values.ServiceContext'?'service':fail('NativeContextCustodyRequired');if(principal.kind!==expected||!Object.hasOwn(principal,p.property))fail('NativeContextCustodyRequired');if(key===null||dataDigest((key as Readonly<Record<string,CommerceNativeValue>>)[p.field])!==dataDigest(principal[p.property]))fail('ForeignPrivateKey');}
 };
 const observe=(site:Site,result:CommerceSqliteSourceReadResultV1)=>{const h=Object.freeze({kind:'original-commerce-native-source-read-observation/v1-candidate' as const});observations.set(h,{site,result:freeze(result)});return h;};
 const native=<T>(f:()=>T):T=>{try{return f();}catch(e){if(e&&typeof e==='object'&&(e as {code?:unknown}).code==='ERR_SQLITE_ERROR'&&typeof(e as {errcode?:unknown}).errcode==='number'&&[5,6].includes((e as {errcode:number}).errcode&255))fail('NativeReadUnavailable');throw e;}};
 const owner:CommerceSqliteSourceReadOwnerV1=Object.freeze({
  paths(op:CommerceLocalOperationHandleV1){return freeze(walk(op).found.map(s=>s.path));},
  bind(op:CommerceLocalOperationHandleV1,p:string){const {view,found}=walk(op),selected=found.find(s=>s.path===p)??fail('UnknownSourceReadSite'),step=selected.step,table=model.tables.find((t:CommerceSqliteTableV1)=>t.entity===step.entity) as CommerceSqliteTableV1|undefined;if(!table||table.owner!==description.service)fail('ForeignServiceScope');
   let index:number|null=null;const privateKeys:Site['privateKeys'][number][]=[];
   if(step.kind==='read'){if(!step.key||step.call!==null)fail('UnknownSourceReadSite');index=table.keys.findIndex(k=>dataDigest(k)===dataDigest(step.key!.key));if(index<0)fail('UnsupportedSourceKey');for(const [valueIndex,v] of step.key.values.entries()){const column=table.columns.find(c=>c.name===v.field);if(!column||dataDigest(column.type)!==dataDigest(v.value.result))fail('SourceKeyTypeMismatch');const e=v.value.expression;const contains=(value:unknown):boolean=>!!value&&typeof value==='object'&&(Object.hasOwn(value,'op')&&(value as {op:string}).op==='private_context'||Object.values(value).some(contains));if(contains(e)){if(e.op!=='field'||e.value.op!=='private_context')fail('UnsupportedPrivateKeyExpression');privateKeys.push({field:v.field,context:e.value,property:e.field,context_path:p+'.key.values['+valueIndex+'].value.expression.value'});}}}
   const inspection:CommerceSqliteSourceReadInspectionV1=freeze({operation:view.operation,source_path:p,kind:step.kind,entity:table.entity,key_index:index,key_fields:index===null?[]:table.keys[index]!,private_key_fields:privateKeys.map(p=>p.field),source_capture_sha256:view.source_capture_sha256,plan_sha256:view.plan_sha256,service:description.service,store_id:original.store_id,schema_sha256:description.schema_sha256,qualification:'source-site-and-native-store-only;bound-arguments-and-full-invocation-required',authority_effect:'none'}),h=Object.freeze({kind:'original-commerce-native-source-read-site/v1-candidate' as const});sites.set(h,{op,operation:view,step,table,view:inspection,privateKeys,retired:false});return h;
  },
  inspect(h:CommerceSqliteSourceReadSiteV1){const s=owned(h);current();return s.view;},
  read(h:CommerceSqliteSourceReadSiteV1,key:CommerceNativeValue,auth?:CommerceSqliteSourceReadAuthorizationV1){const s=owned(h);if(s.step.kind!=='read'||s.view.key_index===null)fail('WrongSourceReadKind');closed(key,s.view.key_fields);authorization(s,auth,key);data.encodeStoredKey(s.table.entity,s.view.key_index,key);return native(()=>{current();const row=store.readRow(s.table.entity,s.view.key_index!,key);const result:CommerceSqliteSourceReadResultV1=row?{kind:'found',value:store.inspectRow(row).value,row}:{kind:'missing'};current();return observe(s,result);});},
  count(h:CommerceSqliteSourceReadSiteV1,auth?:CommerceSqliteSourceReadAuthorizationV1){const s=owned(h);if(s.step.kind!=='count')fail('WrongSourceReadKind');authorization(s,auth,null);return native(()=>{current();const n=store.countRows(s.table.entity);if(!Number.isSafeInteger(n)||n<0)fail('NativeCountRejected');current();return observe(s,{kind:'count',value:BigInt(n)});});},
  inspectObservation(h:CommerceSqliteSourceReadObservationV1){base();const s=h&&typeof h==='object'?observations.get(h):undefined;if(!s)fail('ForeignObservation');if(s.site.retired)fail('RetiredSite');plans.assertOperationCurrent(s.site.op);current();if(s.result.kind==='found')store.inspectRow(s.result.row);return s.result;},
  retire(h:CommerceSqliteSourceReadSiteV1){owned(h).retired=true;},assertCurrent:current,dispose(){disposed=true;},
 });owners.add(owner);current();return owner;
}
