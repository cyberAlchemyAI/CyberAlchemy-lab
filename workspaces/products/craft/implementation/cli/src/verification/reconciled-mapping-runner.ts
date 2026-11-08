/** Data-only Mapping observer; no factories, Rules, Calculations or endpoint calls. */
export const MAPPING_SEMANTIC_RUNNER=String.raw`
async function observeMapping(row){
 const native=await enumImport(row.relative_path),fn=native[row.callable],results=[];
 if(typeof fn!=='function')throw Error('MAPPING_CALLABLE');
 let getter_reads=0;
 const build=r=>{
  if(r.tag==='ref')return build(row.recipes[Number(r.value)]);
  if(r.tag==='null')return null;
  if(r.tag==='scalar')return r.format==='bigint'?BigInt(r.value):r.format==='number'?Number(r.value):r.value;
  if(r.tag==='fields'||r.tag==='record')return Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,build(v)]));
  if(r.tag==='list'||r.tag==='set')return r.items.map(build);
  if(r.tag==='sum')return {variant:r.variant,...(r.payload?{payload:build(r.payload)}:{})};
  if(r.tag==='named')return build(r.input);
  if(r.tag!=='bad')throw Error('unknown Rule fact recipe');
  const base=build(r.base),field=r.field??'variant';
  switch(r.mode){
   case 'null':return null;case 'undefined':return undefined;case 'number':return 0;case 'boolean':return false;case 'string':return 'invalid';case 'array':return [];case 'object':return {};
   case 'negative':return '-1';case 'overflow':return '18446744073709551616';case 'padded':return '01';case 'unsafe':return 9007199254740992;case 'fraction':return 1.5;case 'nan':return NaN;case 'infinity':return Infinity;
   case 'coercion':return {valueOf(){getter_reads++;return 1;},toString(){getter_reads++;return '1';}};
   case 'extra':{let name='extra';while(Object.hasOwn(base,name))name+='_';return {...base,[name]:true};}
   case 'symbol':return {...base,[Symbol('extra')]:true};
   case 'getter':return Object.defineProperty({...base},field,{enumerable:true,get(){getter_reads++;return base[field];}});
   case 'non-enumerable':return Object.defineProperty({...base},field,{enumerable:false,value:base[field]});
   case 'missing-field':{const copy={...base};delete copy[field];return copy;}
   case 'null-prototype':return Object.assign(Object.create(null),base);
   case 'frozen':return Object.freeze(base);
   case 'inherited':return Object.assign(Object.create({extra:true}),base);
   case 'missing-variant':{const copy={...base};delete copy.variant;return copy;}
   case 'unknown-variant':return {...base,variant:'__semantic_unknown__'};
   case 'missing-payload':{const copy={...base};delete copy.payload;return copy;}
   case 'surplus-payload':return {...base,payload:null};
   case 'collection-extra':return Object.assign([...base],{extra:true});
   case 'collection-symbol':{const copy=[...base];copy[Symbol('extra')]=true;return copy;}
   case 'collection-inherited':return Object.setPrototypeOf([...base],Object.create(Array.prototype));
   case 'sparse':{const copy=[...base];delete copy[0];return copy;}
   case 'collection-getter':return Object.defineProperty([...base],'0',{enumerable:true,get(){getter_reads++;return base[0];}});
   case 'collection-hidden':return Object.defineProperty([...base],'0',{enumerable:false,value:base[0]});
   case 'duplicate':return [...base,base[0]];
   default:throw Error('unknown invalid Rule fact recipe');
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
 const binding=()=>{
  if(!Object.isFrozen(fn))throw Error('MAPPING_BINDING');const property=Object.getOwnPropertyDescriptor(fn,'descriptor');
  if(!property||!Object.hasOwn(property,'value')||!property.enumerable)throw Error('MAPPING_BINDING');
  const seen=new Set();let visits=0;
  const read=(v,depth=0)=>{
   if(++visits>65536||depth>64)throw Error('MAPPING_BINDING_CAPACITY');
   if(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return v;
   if(!v||typeof v!=='object'||!Object.isFrozen(v)||seen.has(v))throw Error('MAPPING_BINDING');seen.add(v);
   const descriptors=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(descriptors);let result;
   if(Array.isArray(v)){
    if(Object.getPrototypeOf(v)!==Array.prototype||!Object.hasOwn(descriptors.length??{},'value'))throw Error('MAPPING_BINDING');
    const length=descriptors.length.value;if(length>65536||keys.length!==length+1)throw Error('MAPPING_BINDING');result=[];
    for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable)throw Error('MAPPING_BINDING');result.push(read(d.value,depth+1));}
   }else{
    if(Object.getPrototypeOf(v)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('MAPPING_BINDING');
    result=Object.fromEntries(keys.map(k=>{const d=descriptors[k];if(!Object.hasOwn(d,'value')||!d.enumerable)throw Error('MAPPING_BINDING');return [k,read(d.value,depth+1)];}));
   }
   seen.delete(v);return result;
  };return read(property.value);
 };

 const observe=(v,input,root=false)=>{
  const owned=new Set(),collect=x=>{if(!x||typeof x!=='object'||owned.has(x))return;owned.add(x);for(const d of Object.values(Object.getOwnPropertyDescriptors(x)))if(Object.hasOwn(d,'value'))collect(d.value);};collect(input);
  let visits=0;const active=new Set();
  const read=(x,depth,top=false)=>{
   if(++visits>65536||depth>64)throw Error('MAPPING_OUTCOME_CAPACITY');
   if(x===null)return ['null'];
   if(['bigint','string','boolean'].includes(typeof x))return [typeof x,String(x)];
   if(!x||typeof x!=='object'||!Object.isFrozen(x)||owned.has(x)||active.has(x))throw Error('MAPPING_OUTCOME');
   active.add(x);const d=Object.getOwnPropertyDescriptors(x),keys=Reflect.ownKeys(d);let out;
   if(Array.isArray(x)){
    if(top||Object.getPrototypeOf(x)!==Array.prototype||!Object.hasOwn(d.length??{},'value'))throw Error('MAPPING_OUTCOME');
    const n=d.length.value;if(n>65536||keys.length!==n+1)throw Error('MAPPING_OUTCOME');out=['array',[]];
    for(let i=0;i<n;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable)throw Error('MAPPING_OUTCOME');out[1].push(read(p.value,depth+1));}
   }else{
    if(Object.getPrototypeOf(x)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('MAPPING_OUTCOME');
    const entries=(top?keys:keys.sort()).map(k=>{const p=d[k];if(!Object.hasOwn(p,'value')||!p.enumerable)throw Error('MAPPING_OUTCOME');return [k,read(p.value,depth+1)];});out=top?entries:['record',entries];
   }
   active.delete(x);return out;
  };return read(v,0,root);
 };
 for(const c of row.cases){
  getter_reads=0;let input,before=null,outcome;
  try{
   if(c.mode==='mapping-descriptor')outcome={kind:'value',value:canonical(binding())};
   else{input=build(row.recipes[Number(c.values[0])]);before=fingerprint(input);outcome={kind:'value',value:canonical(observe(fn(input),input,true))};}
  }catch(e){
   if(e&&Object.getPrototypeOf(e)===TypeError.prototype&&Object.hasOwn(Object.getOwnPropertyDescriptor(e,'message')??{},'value'))outcome={kind:'error',name:'TypeError',message:Object.getOwnPropertyDescriptor(e,'message').value};
   else outcome={kind:'unexpected-error'};
  }
  results.push({id:c.id,outcome,getter_reads,input_changed:before!==null&&before!==fingerprint(input)});
 }
 return {selector:row.selector,cases:results};
}
`;
