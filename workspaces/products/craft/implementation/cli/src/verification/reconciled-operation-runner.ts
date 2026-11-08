import {OPERATION_FIXTURE_RUNNER} from './reconciled-operation-fixture.js';
/** Inert descriptor observation and deterministic fixture execution, never a production port. */
export const OPERATION_BINDING_RUNNER=String.raw`
function operationDescriptor(fn){
 if(typeof fn!=='function'||!Object.isFrozen(fn))throw Error('OPERATION_BINDING');
 const property=Object.getOwnPropertyDescriptor(fn,'descriptor');
 if(!property||!Object.hasOwn(property,'value')||!property.enumerable)throw Error('OPERATION_BINDING');
 const active=new Set();let visits=0;
 const read=(v,depth=0)=>{
  if(++visits>65536||depth>64)throw Error('OPERATION_BINDING_CAPACITY');
  if(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return v;
  if(!v||typeof v!=='object'||!Object.isFrozen(v)||active.has(v))throw Error('OPERATION_BINDING');
  active.add(v);const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);let value;
  if(Array.isArray(v)){
   if(Object.getPrototypeOf(v)!==Array.prototype||!Object.hasOwn(d.length??{},'value')||d.length.value>65536||keys.length!==d.length.value+1)throw Error('OPERATION_BINDING');
   value=Array.from({length:d.length.value},(_,i)=>{const p=d[String(i)];if(!p||!p.enumerable||!Object.hasOwn(p,'value'))throw Error('OPERATION_BINDING');return read(p.value,depth+1);});
  }else{
   if(Object.getPrototypeOf(v)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('OPERATION_BINDING');
   value=Object.fromEntries(keys.map(k=>{const p=d[k];if(!p.enumerable||!Object.hasOwn(p,'value'))throw Error('OPERATION_BINDING');return [k,read(p.value,depth+1)];}));
  }active.delete(v);return value;
 };return read(property.value);
}
`;
export const OPERATION_SEMANTIC_RUNNER=OPERATION_BINDING_RUNNER+
 OPERATION_FIXTURE_RUNNER.replace(/^export (async )?function /gm,(_,async:string|undefined)=>(async??'')+'function ')+String.raw`
async function observeOperation(row){
 const native=await enumImport(row.relative_path),fn=native[row.callable],results=[];
 if(typeof fn!=='function')throw Error('OPERATION_CALLABLE');
 const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
 const expand=id=>{
  let visits=0;const active=new Set();
  const read=(r,depth=0)=>{
   if(++visits>65536||depth>64)throw Error('OPERATION_RECIPE_CAPACITY');
   if(r.tag==='ref'){
    const n=Number(r.value);if(!Number.isSafeInteger(n)||n<0||n>=row.recipes.length||active.has(n))throw Error('OPERATION_RECIPE');
    active.add(n);const value=read(row.recipes[n],depth);active.delete(n);return value;
   }
   return {...r,...(r.base?{base:read(r.base,depth+1)}:{}),...(r.input?{input:read(r.input,depth+1)}:{}),...(r.payload?{payload:read(r.payload,depth+1)}:{}),...(r.items?{items:r.items.map(x=>read(x,depth+1))}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,read(x,depth+1)]))}:{})};
  };return read({tag:'ref',value:String(id)});
 };
 for(const c of row.cases){
  let outcome;
  try{
   if(c.mode==='operation-descriptor')outcome={kind:'value',value:canonical(operationDescriptor(fn))};
   else{
    const data=JSON.parse(c.values[0]),recipe=expand(data.input),effects={reads:data.reads.map(r=>({...r,value:expand(r.value)})),clocks:data.clocks};
    const mutate=data.capture?(input,dependencies)=>{
     for(const key of Object.keys(input))input[key]=typeof input[key]==='boolean'?!input[key]:typeof input[key]==='string'?input[key]+'-changed':typeof input[key]==='bigint'?input[key]+1n:typeof input[key]==='number'?input[key]+1:null;
     for(const key of Object.keys(dependencies.clocks))dependencies.clocks[key]=()=>{throw Error('late-operation-clock');};
    }:null;
    outcome={kind:'value',value:canonical(await observeOperationFixture(fn,recipe,data.mode,mutate,effects))};
   }
  }catch{outcome={kind:'unexpected-error'};}
  results.push({id:c.id,outcome,getter_reads:0,input_changed:false});
 }return {selector:row.selector,cases:results};
}
`;
