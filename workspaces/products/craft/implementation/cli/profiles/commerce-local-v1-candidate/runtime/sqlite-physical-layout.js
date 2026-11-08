import {encodeSourceSqliteTypedTupleV1} from '../../../dist/commerce/commerce-sqlite-generation-v1.js';
/** Fixed native storage representation over generated domain codecs; no DB,
 * invocation, row handle or authorization is issued by this data adapter.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import {types as host} from 'node:util';
import {dataDigest,canonicalJson,         } from '../../../dist/profile-engine/contracts.js';
                                                                                                                      
                                                                                                  
                                                                                     
                                                                           

export class CommerceSqlitePhysicalErrorV1 extends Error {
          code       ;
 constructor(code       ){super(code);this.name='CommerceSqlitePhysicalErrorV1';this.code=code;}
}
function bad(code       )       {throw new CommerceSqlitePhysicalErrorV1(code);}
const q=(s       )=>'"'+s.replaceAll('"','""')+'"';
const quote=(s       )=>'"'+s.replace(/["\\\u0000-\u001f]/g,c=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"';
const uint=(t            )        =>t.kind==='scalar'&&t.name==='UInt64';
const KEY_MAGIC=Buffer.from([0x43,0x4b,0x31,0]),ROW='_craft_row',keyName=(i       )=>'_craft_key_'+i;
/** Data encoding only. Domain callers must first validate canonical cells with
 * the source codecs; native journal callers use their fixed private schema. */
export function encodeCommerceSqliteTypedTupleV1(entity       ,fields                                                                                 ,limit       )        {
 try{return encodeSourceSqliteTypedTupleV1(entity,fields,limit);}catch(error){if(error&&typeof error==='object'&&'code' in error&&typeof error.code==='string')bad(error.code);throw error;}
}
                                                                
                                                   
                                                     
                                                           
 
                                                 
                                                  
                               
                                                                                  
                                                       
                                                                                 
 

/** The caller that opens a store must separately establish original data and
 * bundle ownership. All SQL here is fixed and uses generated names only. */
export function deriveCommerceSqlitePhysicalLayoutV1(data                                  )                                {
 const model=data.inspect(),sources=model.tables                                    ,limit=model.limits.max_value_bytes          ;
 if(!Number.isSafeInteger(limit)||limit<1||limit>524288)bad('UnsupportedPhysicalLayout');
 const source=(id       )=>sources.find(t=>t.entity===id)??bad('ForeignServiceScope');
 const keyParts=(t                      ,index       ,cells                         )       =>{
  const fields=t.keys[index];if(!fields||fields.length!==cells.length)bad('UnknownStorageKey');
  return encodeCommerceSqliteTypedTupleV1(t.entity,fields.map((name,i)=>{const cell=cells[i];if(typeof cell!=='string')bad('StorageType');return {name,type:t.columns.find(c=>c.name===name) .type,cell};}),limit);
 };
 const nativeCell=(t            ,cell            )            =>{
  if(!uint(t))return cell;
  if(typeof cell!=='string')bad('StorageType');
  const value        =JSON.parse(cell);
  if(typeof value!=='string'||! /^(0|[1-9][0-9]{0,19})$/.test(value)||BigInt(value)>18446744073709551615n)bad('StorageType');
  return value;
 };
 const rowBytes=(cells                                     )       =>{
  const text='{'+Object.keys(cells).sort().map(k=>quote(k)+':'+(cells[k]===null?'null':cells[k])).join(',')+'}',bytes=Buffer.from(text,'utf8');
  if(bytes.length>limit)bad('StorageBound');return bytes;
 };
 const encode=(id       ,value                    )                                 =>{
  const t=source(id),cells=data.encodeStoredRecord(id,value),keys=t.keys.map(fields=>keyParts(t,t.keys.indexOf(fields),fields.map(n=>cells[n] )));
  return {cells,bindings:[...t.columns.map(c=>nativeCell(c.type,cells[c.name] )),rowBytes(cells),...keys]};
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
 const layout                               ={tables:Object.freeze(tables),schema_sha256:dataDigest({representation:'craft-native-row-key-storage/v1-candidate',tables:tables.map(t=>({entity:t.entity,create_sql:t.create_sql,indexes:t.indexes}))}),encode,
  key(id,index,value){const cells=data.encodeStoredKey(id,index,value);return [keyParts(source(id),index,cells)];},
  decode(id,raw){
   const t=source(id),names=[...t.columns.map(c=>c.sql_name),ROW,...t.keys.map((_,i)=>keyName(i))];
   if(!raw||typeof raw!=='object'||Array.isArray(raw)||host.isProxy(raw)||![Object.prototype,null].includes(Object.getPrototypeOf(raw)))bad('CorruptStore');
   const ds=Object.getOwnPropertyDescriptors(raw),keys=Reflect.ownKeys(raw);
   if(keys.length!==names.length||keys.some(k=>typeof k!=='string'||!names.includes(k))||names.some(n=>!ds[n]?.enumerable||!Object.hasOwn(ds[n] ,'value')))bad('CorruptStore');
   const cells=Object.create(null);
   for(const c of t.columns){const v=ds[c.sql_name] .value;if(v!==null&&typeof v!=='string')bad('CorruptStore');cells[c.name]=uint(c.type)?JSON.stringify(v):v;}
   const value=data.decodeStoredRecord(id,cells),encoded=encode(id,value);
   const actual=[...t.columns.map(c=>ds[c.sql_name] .value),ds[ROW] .value,...t.keys.map((_,i)=>ds[keyName(i)] .value)];
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
