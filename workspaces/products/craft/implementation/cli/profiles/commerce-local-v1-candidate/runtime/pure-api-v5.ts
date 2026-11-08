/** Fixed native ABI over original precompiled source functions. No AST evaluator,
 * user comparator or business callback. Open Questions: COMMERCE-SDK-V5.md. */
import {createHash} from 'node:crypto';
import {types} from 'node:util';
import {commerceNativeEntries as entries} from './commerce-entry-table.js';
const checked=new WeakMap<object,any>(),compiled=new WeakMap<object,any>();
function inert(value:any):any {
 let count=0,bytes=0;
 const walk=(v:any,depth:number):any=>{
  if(++count>100000||depth>64)throw new Error('InvalidContract');
  if(v===null||typeof v==='boolean')return v;
  if(typeof v==='number'){if(!Number.isSafeInteger(v))throw new Error('InvalidContract');return v;}
  if(typeof v==='string'){bytes+=Buffer.byteLength(v);if(bytes>16777216||Buffer.from(v,'utf8').toString('utf8')!==v)throw new Error('InvalidContract');return v;}
  if(!v||typeof v!=='object'||types.isProxy(v))throw new Error('InvalidContract');
  const array=Array.isArray(v),proto=Object.getPrototypeOf(v);if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)throw new Error('InvalidContract');
  const ds=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(ds);
  if(array){const n=ds.length?.value;if(!Number.isSafeInteger(n)||n<0||n>10000||keys.length!==n+1)throw new Error('InvalidContract');const out=[];for(let i=0;i<n;i++){const d=ds[String(i)];if(!d||!d.enumerable||!Object.hasOwn(d,'value'))throw new Error('InvalidContract');out.push(walk(d.value,depth+1));}return out;}
  if(keys.length>2048)throw new Error('InvalidContract');const out=Object.create(null);for(const key of keys){if(typeof key!=='string')throw new Error('InvalidContract');const d=ds[key]!;if(!d.enumerable||!Object.hasOwn(d,'value'))throw new Error('InvalidContract');bytes+=Buffer.byteLength(key);if(bytes>16777216)throw new Error('InvalidContract');out[key]=walk(d.value,depth+1);}return out;
 };return walk(value,0);
}
function canonical(v:any):string {if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';if(v&&typeof v==='object')return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';return JSON.stringify(v);}
const digest=(v:any)=>createHash('sha256').update(canonical(v)).digest('hex');
export function checkCommerceComputation(contract:any){
 try{const value=inert(contract),row=entries.find((r:any)=>r.contract_sha256===digest(value)&&r.source_node===value.source_node);if(!row)throw new Error('UnsupportedCapability');const token=Object.freeze({kind:'original-native-checked-commerce-computation/v5-candidate'});checked.set(token,row);return Object.freeze({ok:true,value:token});}
 catch{return Object.freeze({ok:false,diagnostics:[{code:'InvalidContract',path:'native-computation',start:0,end:0,message:'exact original source-selected computation contract required'}]});}
}
export function compileCommerceComputation(handle:object){const row=handle&&typeof handle==='object'?checked.get(handle):undefined;if(!row)throw new Error('ForeignOwner');const token=Object.freeze({kind:'original-native-compiled-commerce-computation/v5-candidate'});compiled.set(token,row);return token;}
export function evaluateCommerceComputation(handle:object,input:Uint8Array){const row=handle&&typeof handle==='object'?compiled.get(handle):undefined;if(!row)throw new Error('ForeignOwner');return row.evaluate(input);}
export function inspectCommerceNativeComputation(handle:object){const row=checked.get(handle)??compiled.get(handle);if(!row)throw new Error('ForeignOwner');return Object.freeze({source_node:row.source_node,contract_sha256:row.contract_sha256,qualification:'source-compiled-pure-native-component-only;not-original-application-or-effect-owner',authority_effect:'none'});}
