/** Bounded inert native-port values. No authority is minted by serialized data.
 * Open Questions: ../README.md#open-questions. */
import {createHash} from 'node:crypto';
import {types} from 'node:util';
export class ProfileError extends Error {constructor(code,message=code){super(message);this.code=code;}}
export function fail(code,message){throw new ProfileError(code,message);}
export function assert(value,code,message){if(!value)fail(code,message);}
export function text(value,name='id',max=256){assert(typeof value==='string'&&value.length>0&&Buffer.byteLength(value)<=max&&value.isWellFormed()&&!/[\u0000-\u001f\u007f]/.test(value),'InvalidContract',name);return value;}
export function count(value,name='count',max=Number.MAX_SAFE_INTEGER){assert(Number.isSafeInteger(value)&&value>=0&&value<=max,'InvalidContract',name);return value;}
export function u64(value){assert(typeof value==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(value)&&BigInt(value)<=18446744073709551615n,'InvalidContract','exact UInt64 decimal string required');return BigInt(value);}
export function capture(value,{maxBytes=1048576,maxNodes=32768,maxDepth=32}={}){
 let nodes=0;const active=new WeakSet();
 const copy=(v,depth)=>{assert(++nodes<=maxNodes&&depth<=maxDepth,'ResourceLimit','finite inert value bound');
  if(v===null||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return v;
  if(typeof v==='string'){assert(v.isWellFormed(),'InvalidContract','Unicode scalar string');return v;}
  assert(v&&typeof v==='object'&&!types.isProxy(v)&&!active.has(v),'InvalidContract','inert JSON only');
  const array=Array.isArray(v);assert(Object.getPrototypeOf(v)===(array?Array.prototype:Object.prototype)||!array&&Object.getPrototypeOf(v)===null,'InvalidContract','plain inert JSON');
  const ds=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(ds);assert(keys.every(k=>typeof k==='string'),'InvalidContract','string keys only');active.add(v);try{
   if(array){const n=ds.length?.value;assert(Number.isSafeInteger(n)&&n>=0&&n<=maxNodes&&keys.length===n+1,'InvalidContract','dense finite array');return Array.from({length:n},(_,i)=>{const d=ds[i];assert(d?.enumerable&&Object.hasOwn(d,'value'),'InvalidContract','inert array');return copy(d.value,depth+1);});}
   const out=Object.create(null);for(const k of keys){const d=ds[k];assert(d.enumerable&&Object.hasOwn(d,'value')&&k.isWellFormed(),'InvalidContract','inert object');out[k]=copy(d.value,depth+1);}return out;
  }finally{active.delete(v);}};
 const out=copy(value,0);assert(Buffer.byteLength(JSON.stringify(out))<=maxBytes,'ResourceLimit','JSON byte bound');return out;
}
export function canonical(value){const v=capture(value);const emit=x=>Array.isArray(x)?'['+x.map(emit).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+emit(x[k])).join(',')+'}':JSON.stringify(x);return emit(v);}
export const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
export function freeze(value){if(value&&typeof value==='object'){for(const child of Object.values(value))freeze(child);Object.freeze(value);}return value;}
export function closed(value,keys,required=keys){const v=capture(value);assert(v&&!Array.isArray(v)&&typeof v==='object'&&Object.keys(v).every(k=>keys.includes(k))&&required.every(k=>Object.hasOwn(v,k)),'InvalidContract','closed contract fields required');return v;}
export function copyBytes(value,max=1048576){assert(!types.isProxy(value)&&types.isUint8Array(value),'InvalidContract','owned Uint8Array');const p=Object.getPrototypeOf(Uint8Array.prototype),get=k=>Object.getOwnPropertyDescriptor(p,k).get.call(value),n=get('byteLength'),buffer=get('buffer');assert(n<=max&&!types.isSharedArrayBuffer(buffer),'ResourceLimit','unshared byte bound');const out=new Uint8Array(n);out.set(new Uint8Array(buffer,get('byteOffset'),n));return out;}
