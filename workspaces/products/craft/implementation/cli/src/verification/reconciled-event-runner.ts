/** Private deterministic Event fixture observer; no production clock or referenced module is used. */
export const EVENT_SEMANTIC_RUNNER=String.raw`
async function observeEvent(row){
 const native=await enumImport(row.relative_path),fn=native[row.callable],results=[];
 if(typeof fn!=='function')throw Error('EVENT_CALLABLE');
 let getter_reads=0;
 const build=a=>{
  if(a.kind==='string')return a.value;
  if(a.kind==='boolean')return a.value==='true';
  if(a.kind==='bigint')return BigInt(a.value);
  if(a.kind==='number')return Number(a.value);
  switch(a.value){
   case 'undefined':return undefined;case 'null':return null;case 'object':return {};case 'array':return [];case 'symbol':return Symbol('invalid');case 'function':return ()=>{};
   case 'promise':return Promise.resolve('late');
   case 'coercion':return {valueOf(){getter_reads++;return 1;},toString(){getter_reads++;return 'value';}};
   default:throw Error('EVENT_RECIPE');
  }
 };
 const change=(value,c)=>{
  const field=c.field??'extra',copy=()=>Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(value)).filter(([,d])=>Object.hasOwn(d,'value')).map(([k,d])=>[k,d.value]));
  switch(c.mode){
   case 'null-prototype':return Object.assign(Object.create(null),value);
   case 'frozen':return Object.freeze(value);
   case 'null':return null;case 'undefined':return undefined;case 'array':return [];
   case 'inherited':return Object.assign(Object.create({inherited:true}),value);
   case 'extra':{const v=copy();let k='extra';while(Object.hasOwn(v,k))k+='_';v[k]=true;return v;}
   case 'symbol':return {...copy(),[Symbol('extra')]:true};
   case 'getter':return Object.defineProperty(copy(),field,{enumerable:true,configurable:true,get(){getter_reads++;return value[field];}});
   case 'non-enumerable':return Object.defineProperty(copy(),field,{enumerable:false,configurable:true,value:value[field]});
   case 'missing':{const v=copy();delete v[field];return v;}
   default:throw Error('EVENT_CHANGE');
  }
 };
 const objects=new WeakMap(),symbols=new Map();let next=1;
 const identity=v=>{const ids=typeof v==='symbol'?symbols:objects;if(!ids.has(v))ids.set(v,next++);return ids.get(v);};
 const fingerprint=input=>{
  const seen=new Set();
  const visit=v=>{
   if(typeof v==='symbol')return ['symbol',identity(v)];
   if(typeof v==='function')return ['function',identity(v)];
   if(typeof v==='number')return ['number',Object.is(v,-0)?'-0':String(v)];
   if(v===null||typeof v!=='object')return [typeof v,typeof v==='bigint'?v.toString():v];
   const id=identity(v);if(seen.has(id))return ['ref',id];seen.add(id);
   const proto=Object.getPrototypeOf(v),descriptors=Object.getOwnPropertyDescriptors(v);
   return ['object',id,proto===null?null:identity(proto),Object.isExtensible(v),Reflect.ownKeys(descriptors).map(k=>{
    const d=descriptors[k];return [typeof k==='symbol'?['symbol',identity(k)]:k,d.enumerable,d.configurable,
     Object.hasOwn(d,'value')?['data',d.writable,visit(d.value)]:['accessor',d.get?identity(d.get):null,d.set?identity(d.set):null]];
   })];
  };return JSON.stringify(visit(input));
 };

 const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
 const record=(value,allowed,exact)=>{
  if(!value||typeof value!=='object'||Object.getPrototypeOf(value)!==Object.prototype||!Object.isFrozen(value))throw Error('EVENT_OUTCOME');
  const d=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(d);
  if(exact&&keys.length!==allowed.length||keys.some(k=>typeof k!=='string'||!allowed.includes(k)||!Object.hasOwn(d[k],'value')||!d[k].enumerable))throw Error('EVENT_OUTCOME');
  return Object.fromEntries(keys.map(k=>[k,d[k].value]));
 };
 const scalar=v=>{
  if(typeof v==='string'||typeof v==='boolean'||typeof v==='bigint'||typeof v==='number')return {kind:typeof v,value:typeof v==='number'&&Object.is(v,-0)?'-0':String(v)};
  throw Error('EVENT_OUTCOME');
 };
 const encode=value=>{
  const root=record(value,['type','version','occurrence','payload','occurredAt'],true),occurrence=record(root.occurrence,row.occurrence_fields,true),payload=record(root.payload,row.payload_fields,false);
  if(typeof root.type!=='string'||typeof root.version!=='string')throw Error('EVENT_OUTCOME');
  return {type:root.type,version:root.version,occurredAt:scalar(root.occurredAt),occurrence:Object.fromEntries(Object.entries(occurrence).map(([k,v])=>[k,scalar(v)])),payload:Object.fromEntries(Object.entries(payload).map(([k,v])=>[k,scalar(v)]))};
 };
 const binding=()=>{
  if(!Object.isFrozen(fn))throw Error('EVENT_BINDING');const property=Object.getOwnPropertyDescriptor(fn,'descriptor');
  if(!property||!Object.hasOwn(property,'value')||!property.enumerable)throw Error('EVENT_BINDING');
  const seen=new Set();let visits=0;
  const read=(v,depth=0)=>{
   if(++visits>65536||depth>64)throw Error('EVENT_BINDING_CAPACITY');
   if(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return v;
   if(!v||typeof v!=='object'||!Object.isFrozen(v)||seen.has(v))throw Error('EVENT_BINDING');seen.add(v);
   const descriptors=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(descriptors);let result;
   if(Array.isArray(v)){
    if(Object.getPrototypeOf(v)!==Array.prototype||!Object.hasOwn(descriptors.length??{},'value'))throw Error('EVENT_BINDING');
    const length=descriptors.length.value;if(length>65536||keys.length!==length+1)throw Error('EVENT_BINDING');result=[];
    for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable)throw Error('EVENT_BINDING');result.push(read(d.value,depth+1));}
   }else{
    if(Object.getPrototypeOf(v)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('EVENT_BINDING');
    result=Object.fromEntries(keys.map(k=>{const d=descriptors[k];if(!Object.hasOwn(d,'value')||!d.enumerable)throw Error('EVENT_BINDING');return [k,read(d.value,depth+1)];}));
   }
   seen.delete(v);return result;
  };return read(property.value);
 };
 for(const c of row.cases){
  if(c.mode==='event-descriptor'){
   let outcome;try{outcome={kind:'value',value:canonical(binding())};}catch{outcome={kind:'unexpected-binding'};}
   results.push({id:c.id,outcome,getter_reads:0,input_changed:false});continue;
  }
  getter_reads=0;const r=JSON.parse(c.values[0]);let input={occurrence:Object.fromEntries(Object.entries(r.input.occurrence).map(([k,a])=>[k,build(a)])),payload:Object.fromEntries(Object.entries(r.input.payload).map(([k,a])=>[k,build(a)])),...(Object.hasOwn(r.input,'occurredAt')?{occurredAt:build(r.input.occurredAt)}:{})};
  for(const c of r.changes)if(c.target==='input')input=change(input,c);else input[c.target]=change(input[c.target],c);
  const before=fingerprint(input),clockError=new Error('EVENT_CLOCK_SENTINEL');let clock_calls=0,clock;
  if(r.clock.kind==='return'||r.clock.kind==='throw')clock=()=>{clock_calls++;if(r.clock.kind==='throw')throw clockError;return build(r.clock.value);};
  else if(r.clock.kind==='null')clock=null;else if(r.clock.kind==='number')clock=0;
  let result;
  try{
   const originals=input&&typeof input==='object'?Object.getOwnPropertyDescriptors(input):{},seen=new Set(),values=[];let detached=true,fresh=true;
   for(let i=0;i<(r.repeat?2:1);i++){
    const value=r.clock.kind==='absent'?fn(input):fn(input,clock),encoded=encode(value),parts=Object.getOwnPropertyDescriptors(value);
    for(const part of [value,parts.occurrence.value,parts.payload.value]){if(seen.has(part))fresh=false;seen.add(part);if(part===input||part===originals.occurrence?.value||part===originals.payload?.value)detached=false;}
    values.push(encoded);
   }
   result={kind:'value',values,detached,fresh};
  }catch(e){
   if(e===clockError)result={kind:'error',name:'Error',message:'EVENT_CLOCK_SENTINEL',same_clock_error:true};
   else if(e&&Object.getPrototypeOf(e)===TypeError.prototype&&Object.hasOwn(Object.getOwnPropertyDescriptor(e,'message')??{},'value'))result={kind:'error',name:'TypeError',message:Object.getOwnPropertyDescriptor(e,'message').value,same_clock_error:false};
   else result={kind:'unexpected-error',same_clock_error:false};
  }
  results.push({id:c.id,outcome:{kind:'value',value:canonical({result,clock_calls})},getter_reads,input_changed:before!==fingerprint(input)});
 }
 return {selector:row.selector,cases:results};
}
`;
