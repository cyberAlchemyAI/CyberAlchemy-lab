import {encodeSourceSqliteTypedTupleV1} from '../../../src/commerce/commerce-sqlite-generation-v1.js';
/** Fixed native storage representation over generated domain codecs; no DB,
 * invocation, row handle or authorization is issued by this data adapter.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import {types as host} from 'node:util';
import {dataDigest,canonicalJson,type Json} from '../../../src/profile-engine/contracts.js';
import type {CommerceRepositoryDataComponentV1} from '../../../src/commerce/commerce-sqlite-repository-runtime-v1.js';
import type {CommerceSqliteTableV1} from '../../../src/commerce/commerce-sqlite-generation-v1.js';
import type {CommerceNativeValue} from '../../../src/commerce/commerce-native-v1.js';
import type {ValueTypeV1} from '../../../src/commerce/commerce-data-v1.js';

export class CommerceSqlitePhysicalErrorV1 extends Error {
 readonly code:string;
 constructor(code:string){super(code);this.name='CommerceSqlitePhysicalErrorV1';this.code=code;}
}
function bad(code:string):never {throw new CommerceSqlitePhysicalErrorV1(code);}
const q=(s:string)=>'"'+s.replaceAll('"','""')+'"';
const quote=(s:string)=>'"'+s.replace(/["\\\u0000-\u001f]/g,c=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"';
const uint=(t:ValueTypeV1):boolean=>t.kind==='scalar'&&t.name==='UInt64';
const KEY_MAGIC=Buffer.from([0x43,0x4b,0x31,0]),ROW='_craft_row',keyName=(i:number)=>'_craft_key_'+i;
/** Data encoding only. Domain callers must first validate canonical cells with
 * the source codecs; native journal callers use their fixed private schema. */
export function encodeCommerceSqliteTypedTupleV1(entity:string,fields:readonly {readonly name:string;readonly type:ValueTypeV1;readonly cell:string}[],limit:number):Buffer {
 try{return encodeSourceSqliteTypedTupleV1(entity,fields,limit);}catch(error){if(error&&typeof error==='object'&&'code' in error&&typeof error.code==='string')bad(error.code);throw error;}
}
export type CommerceSqlitePhysicalCellV1=string|null|Uint8Array;
export interface CommerceSqlitePhysicalEncodingV1 {
 readonly cells:Readonly<Record<string,string|null>>;
 readonly bindings:readonly CommerceSqlitePhysicalCellV1[];
}
export interface CommerceSqlitePhysicalLayoutV1 {
 readonly tables:readonly CommerceSqliteTableV1[];
 readonly schema_sha256:string;
 encode(entity:string,value:CommerceNativeValue):CommerceSqlitePhysicalEncodingV1;
 decode(entity:string,row:unknown):CommerceNativeValue;
 key(entity:string,index:number,value:CommerceNativeValue):readonly Uint8Array[];
}

/** The caller that opens a store must separately establish original data and
 * bundle ownership. All SQL here is fixed and uses generated names only. */
export function deriveCommerceSqlitePhysicalLayoutV1(data:CommerceRepositoryDataComponentV1):CommerceSqlitePhysicalLayoutV1 {
 const model=data.inspect(),sources=model.tables as readonly CommerceSqliteTableV1[],limit=model.limits.max_value_bytes as number;
 if(!Number.isSafeInteger(limit)||limit<1||limit>524288)bad('UnsupportedPhysicalLayout');
 const source=(id:string)=>sources.find(t=>t.entity===id)??bad('ForeignServiceScope');
 const keyParts=(t:CommerceSqliteTableV1,index:number,cells:readonly (string|null)[]):Buffer=>{
  const fields=t.keys[index];if(!fields||fields.length!==cells.length)bad('UnknownStorageKey');
  return encodeCommerceSqliteTypedTupleV1(t.entity,fields.map((name,i)=>{const cell=cells[i];if(typeof cell!=='string')bad('StorageType');return {name,type:t.columns.find(c=>c.name===name)!.type,cell};}),limit);
 };
 const nativeCell=(t:ValueTypeV1,cell:string|null):string|null=>{
  if(!uint(t))return cell;
  if(typeof cell!=='string')bad('StorageType');
  const value:unknown=JSON.parse(cell);
  if(typeof value!=='string'||! /^(0|[1-9][0-9]{0,19})$/.test(value)||BigInt(value)>18446744073709551615n)bad('StorageType');
  return value;
 };
 const rowBytes=(cells:Readonly<Record<string,string|null>>):Buffer=>{
  const text='{'+Object.keys(cells).sort().map(k=>quote(k)+':'+(cells[k]===null?'null':cells[k])).join(',')+'}',bytes=Buffer.from(text,'utf8');
  if(bytes.length>limit)bad('StorageBound');return bytes;
 };
 const encode=(id:string,value:CommerceNativeValue):CommerceSqlitePhysicalEncodingV1=>{
  const t=source(id),cells=data.encodeStoredRecord(id,value),keys=t.keys.map(fields=>keyParts(t,t.keys.indexOf(fields),fields.map(n=>cells[n]!)));
  return {cells,bindings:[...t.columns.map(c=>nativeCell(c.type,cells[c.name]!)),rowBytes(cells),...keys]};
 };
 const tables=sources.map(t=>{
  const columns=t.columns.map(c=>{
   const name=q(c.sql_name),canonicalUint="instr("+name+",char(0))=0 AND length("+name+") BETWEEN 1 AND 20 AND "+name+" NOT GLOB '*[^0-9]*' AND (length("+name+")=1 OR substr("+name+",1,1)<>'0') AND (length("+name+")<20 OR "+name+"<='18446744073709551615')";
   return name+' TEXT'+(c.nullable?'':' NOT NULL')+' CHECK ('+(c.nullable?name+' IS NULL OR ':'')+(uint(c.type)?'('+canonicalUint+')':'json_valid('+name+')')+')';
  });
  const hidden=[q(ROW)+' BLOB NOT NULL CHECK(length('+q(ROW)+')<='+limit+')',...t.keys.map((_,i)=>q(keyName(i))+' BLOB NOT NULL CHECK(length('+q(keyName(i))+')<='+limit+')')];
  const names=[...t.columns.map(c=>c.sql_name),ROW,...t.keys.map((_,i)=>keyName(i))];
  return Object.freeze({...t,
   create_sql:'CREATE TABLE '+q(t.physical_name)+' ('+[...columns,...hidden,'PRIMARY KEY ('+q(keyName(0))+')'].join(', ')+') STRICT;',
   indexes:t.keys.slice(1).map((_,i)=>'CREATE UNIQUE INDEX '+q(t.physical_name+'_unique_'+i)+' ON '+q(t.physical_name)+' ('+q(keyName(i+1))+');'),
   insert_sql:'INSERT INTO '+q(t.physical_name)+' ('+names.map(q).join(',')+') VALUES ('+names.map(()=>'?').join(',')+')',
   select_key_sql:t.keys.map((_,i)=>'SELECT * FROM '+q(t.physical_name)+' WHERE '+q(keyName(i))+'=? LIMIT 2'),
  });
 });
 const layout:CommerceSqlitePhysicalLayoutV1={tables:Object.freeze(tables),schema_sha256:dataDigest({representation:'craft-native-row-key-storage/v1-candidate',tables:tables.map(t=>({entity:t.entity,create_sql:t.create_sql,indexes:t.indexes}))}),encode,
  key(id,index,value){const cells=data.encodeStoredKey(id,index,value);return [keyParts(source(id),index,cells)];},
  decode(id,raw){
   const t=source(id),names=[...t.columns.map(c=>c.sql_name),ROW,...t.keys.map((_,i)=>keyName(i))];
   if(!raw||typeof raw!=='object'||Array.isArray(raw)||host.isProxy(raw)||![Object.prototype,null].includes(Object.getPrototypeOf(raw)))bad('CorruptStore');
   const ds=Object.getOwnPropertyDescriptors(raw),keys=Reflect.ownKeys(raw);
   if(keys.length!==names.length||keys.some(k=>typeof k!=='string'||!names.includes(k))||names.some(n=>!ds[n]?.enumerable||!Object.hasOwn(ds[n]!,'value')))bad('CorruptStore');
   const cells=Object.create(null);
   for(const c of t.columns){const v=ds[c.sql_name]!.value;if(v!==null&&typeof v!=='string')bad('CorruptStore');cells[c.name]=uint(c.type)?JSON.stringify(v):v;}
   const value=data.decodeStoredRecord(id,cells),encoded=encode(id,value);
   const actual=[...t.columns.map(c=>ds[c.sql_name]!.value),ds[ROW]!.value,...t.keys.map((_,i)=>ds[keyName(i)]!.value)];
   for(let i=0;i<actual.length;i++){
    const a=actual[i],e=encoded.bindings[i];
    if(e instanceof Uint8Array){if(!a||typeof a!=='object'||host.isProxy(a)||!(a instanceof Uint8Array)||!Buffer.from(e).equals(a))bad('CorruptStore');}
    else if(a!==e)bad('CorruptStore');
   }
   return value;
  },
 };
 return Object.freeze(layout);
}
