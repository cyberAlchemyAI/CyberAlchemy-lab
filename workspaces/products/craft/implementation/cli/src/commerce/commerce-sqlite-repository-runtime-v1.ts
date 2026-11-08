/** Fixed generated repository data conversions; no DB or execution capability.
 * The emitter replaces only these two declarations with checked static data
 * and a fixed import from its generated codec. No application callback port.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import {types as nodeTypes} from 'node:util';
declare const commerceRepositoryModel:any;
declare const repositoryCodecs:any;
export class CommerceRepositoryDataErrorV1 extends Error {readonly code:string;constructor(code:string){super(code);this.code=code;this.name='CommerceRepositoryDataErrorV1';}}
function bad(code:string):never {throw new CommerceRepositoryDataErrorV1(code);}
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const child of Object.values(v))freeze(child);Object.freeze(v);}return v;}
function closed(v:any,keys:readonly string[]):void {if(!v||typeof v!=='object'||Array.isArray(v)||nodeTypes.isProxy(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))bad('StorageType');const ds=Object.getOwnPropertyDescriptors(v),names=Reflect.ownKeys(v);if(names.length!==keys.length||names.some(k=>typeof k!=='string'||!keys.includes(k))||keys.some(k=>!Object.hasOwn(ds,k)||!ds[k]!.enumerable||!Object.hasOwn(ds[k]!,'value')))bad('StorageType');}
const schemas=new Map<string,any>();
function schema(type:any):any {const key=JSON.stringify(type);let s=schemas.get(key);if(!s){const checked=repositoryCodecs.checkCommerceSchema({...commerceRepositoryModel.values,root:type});if(!checked.ok)bad('UnsupportedStorageShape');s=checked.value;schemas.set(key,s);}return s;}
function table(id:string):any {const t=commerceRepositoryModel.tables.find((t:any)=>t.entity===id);if(!t)bad('ForeignServiceScope');return t;}
function query(id:string):any {const q=commerceRepositoryModel.queries.find((q:any)=>q.id===id);if(!q)bad('ForeignServiceScope');return q;}
function encode(type:any,value:any):string|null {const r=repositoryCodecs.encodeCommerceValue(schema(type),value);if(!r.ok)bad('StorageType');const text=new TextDecoder('utf-8',{fatal:true}).decode(r.value);return type.kind==='optional'&&text==='null'?null:text;}
function decode(type:any,value:any):any {const wasNull=value===null;if(value===null){if(type.kind!=='optional')bad('StorageType');value='null';}if(typeof value!=='string'||Buffer.byteLength(value)>commerceRepositoryModel.limits.max_value_bytes)bad('StorageType');const r=repositoryCodecs.decodeCommerceValue(schema(type),new TextEncoder().encode(value));if(!r.ok)bad('StorageType');const encoded=encode(type,r.value);if(encoded===null?!wasNull:wasNull||encoded!==value)bad('NonCanonicalStorage');return r.value;}
export interface CommerceRepositoryDataComponentV1 {
 readonly qualification:'generated-repository-data-only;not-store-query-row-or-authorization-custody';
 inspect():Readonly<Record<string,any>>;
 encodeStoredRecord(entity:string,value:any):Readonly<Record<string,string|null>>;
 decodeStoredRecord(entity:string,row:any):any;
 encodeStoredKey(entity:string,keyIndex:number,value:any):readonly (string|null)[];
 prepareQueryValues(query:string,value:any):Readonly<{sql:string;values:readonly (string|null)[];requires_original_context_owner:boolean;residual_required:boolean;authority_effect:'none'}>;
 queryDisposition(query:string,channel:'missing'|'unavailable'):any;
 queryResultMapping(query:string):any;
}
/** Fixed generated functions format data only; they never receive a DB handle. */
export const commerceRepositoryData:CommerceRepositoryDataComponentV1=Object.freeze({
 qualification:'generated-repository-data-only;not-store-query-row-or-authorization-custody' as const,
 inspect(){return freeze(commerceRepositoryModel);},
 encodeStoredRecord(id:string,value:any){const t=table(id),r=repositoryCodecs.copyCommerceValue(schema({kind:'record',name:id}),value);if(!r.ok)bad('StorageType');const full=repositoryCodecs.encodeCommerceValue(schema({kind:'record',name:id}),r.value);if(!full.ok)bad('StorageType');const out=Object.create(null);for(const f of t.columns)out[f.name]=encode(f.type,r.value[f.name]);return Object.freeze(out);},
 decodeStoredRecord(id:string,row:any){const t=table(id);closed(row,t.columns.map((f:any)=>f.name));let bytes=0;const out=Object.create(null);for(const f of t.columns){if(typeof row[f.name]==='string')bytes+=Buffer.byteLength(row[f.name]);if(bytes>commerceRepositoryModel.limits.max_value_bytes)bad('StorageBound');out[f.name]=decode(f.type,row[f.name]);}const r=repositoryCodecs.copyCommerceValue(schema({kind:'record',name:id}),out);if(!r.ok)bad('StorageType');return r.value;},
 encodeStoredKey(id:string,keyIndex:number,value:any){const t=table(id);if(!Number.isSafeInteger(keyIndex)||!t.keys[keyIndex])bad('UnknownStorageKey');const fields=t.keys[keyIndex]as string[];closed(value,fields);return Object.freeze(fields.map(name=>encode(t.columns.find((f:any)=>f.name===name).type,value[name])));},
 prepareQueryValues(id:string,value:any){const q=query(id);closed(value,q.slots.map((s:any)=>s.id));const values=q.slots.map((s:any)=>encode(s.type,value[s.id]));return freeze({sql:q.sql,values,requires_original_context_owner:q.plan.contexts.length>0,residual_required:q.residual.length>0,authority_effect:'none' as const});},
 queryDisposition(id:string,channel:'missing'|'unavailable'){const q=query(id);if(channel!=='missing'&&channel!=='unavailable')bad('UnknownQueryChannel');return freeze(channel==='missing'?q.plan.on_missing:q.plan.on_unavailable);},
 queryResultMapping(id:string){const q=query(id);return freeze({projection:q.plan.projection,guards:q.plan.guards,wrap_projection_some:q.plan.wrap_projection_some,output:q.plan.output,source_bindings:q.plan.sources,contexts:q.plan.contexts,residual_predicates:q.residual,original_native_scope_required:true,authority_effect:'none'});},
});
