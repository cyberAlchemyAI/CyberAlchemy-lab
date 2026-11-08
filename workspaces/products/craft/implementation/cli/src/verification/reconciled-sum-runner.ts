/** Fixed native observer for source-derived sum recipes; no renderer is used. */
export const SUM_SEMANTIC_RUNNER=String.raw`
async function createOwnedValueObserver(row){
 const modules=new Map();
 const load=async(selector,foreign=false)=>{
  const id=selector+(foreign?'?foreign':''),d=row.dependencies[selector];
  if(!modules.has(id))modules.set(id,(await enumImport(d.relative_path,foreign?'?semantic-foreign':''))[d.symbol]);
  return modules.get(id);
 };
 const root=await load(row.selector),foreignRoot=await load(row.selector,true);
 let getter_reads=0,construction_changed=false;
 const recordInput=async r=>Object.fromEntries(await Promise.all(Object.entries(r.fields).map(async([name,value])=>[name,await build(value)])));
 const constructRecord=async(r,foreign=false)=>{
  const d=row.dependencies[r.selector],native=await enumImport(d.relative_path,foreign?'?semantic-foreign':''),input=await recordInput(r),before=fingerprint(input);
  const result=native[d.callable]().create(input);
  construction_changed ||= before!==fingerprint(input);
  if(result.ok!==true)throw Error('source-valid record witness rejected');
  return result.value;
 };
 const build=async r=>{
  if(r.tag==='null')return null;
  if(r.tag==='scalar')return r.format==='bigint'?BigInt(r.value):r.format==='number'?Number(r.value):r.value;
  if(r.tag==='list'||r.tag==='set')return Promise.all(r.items.map(build));
  if(r.tag==='sum')return {variant:r.variant,...(r.payload?{payload:await build(r.payload)}:{})};
  if(r.tag==='enum')return (await load(r.selector)).fromVariant(r.variant);
  if(r.tag==='named')return (await load(r.selector)).create(await build(r.input));
  if(r.tag==='record')return constructRecord(r);
  if(r.tag==='fields')return recordInput(r);
  if(r.tag!=='bad')throw Error('unknown sum recipe');
  const base=await build(r.base);
  switch(r.mode){
   case 'null':return null;case 'undefined':return undefined;case 'number':return 0;case 'string':return 'invalid';case 'array':return [];case 'object':return {};
   case 'negative':return '-1';case 'overflow':return '18446744073709551616';case 'padded':return '01';case 'unsafe':return 9007199254740992;case 'fraction':return 1.5;
   case 'coercion':return {valueOf(){getter_reads++;return 1;},toString(){getter_reads++;return '1';}};
   case 'extra':{let name='extra';while(Object.hasOwn(base,name))name+='_';return {...base,[name]:true};}case 'symbol':return {...base,[Symbol('extra')]:true};
   case 'getter':{const name=r.field??'variant';return Object.defineProperty({...base},name,{enumerable:true,get(){getter_reads++;return base[name];}});}
   case 'non-enumerable':return Object.defineProperty({...base},r.field,{enumerable:false,value:base[r.field]});
   case 'missing-field':{const copy={...base};delete copy[r.field];return copy;}
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
   case 'duplicate':return [...base,base[0]];
   case 'raw-named':return r.base.tag==='record'?recordInput(r.base):r.base.tag==='enum'?{variant:r.base.variant}:build(r.base.input);
   case 'clone-named':return {...base};
   case 'foreign-named':return r.base.tag==='record'?constructRecord(r.base,true):r.base.tag==='enum'?(await load(r.base.selector,true)).fromVariant(r.base.variant):(await load(r.base.selector,true)).create(await build(r.base.input));
   default:throw Error('unknown invalid sum recipe');
  }
 };
 const field=(value,name)=>{
  const descriptor=Object.getOwnPropertyDescriptor(value,name);
  if(!descriptor||!Object.hasOwn(descriptor,'value'))throw Error('non-data native sum output');
  return descriptor.value;
 };
 const view=async(t,v)=>{
  if(t.kind==='scalar'){
   const required=t.name==='UInt64'?'bigint':t.name==='Bool'?'boolean':'string';
   if(typeof v!==required)throw Error('wrong scalar carrier');
   return {kind:t.name,value:t.name==='UInt64'?v.toString():v};
  }
  if(t.kind==='optional')return v===null?null:view(t.element,v);
  if(t.kind==='list'||t.kind==='set'){
   if(!Array.isArray(v))throw Error('wrong collection carrier');
   return {kind:t.kind,frozen:Object.isFrozen(v),plain:Object.getPrototypeOf(v)===Array.prototype,items:await Promise.all(v.map(x=>view(t.element,x)))};
  }
  if(t.kind==='sum'){
   const variant=field(v,'variant'),definition=t.variants.find(x=>x.name===variant);
   if(!definition)throw Error('unknown observed variant');
   return {kind:'sum',variant,frozen:Object.isFrozen(v),keys:Object.keys(v).sort(),...(definition.payload?{payload:await view(definition.payload,field(v,'payload'))}:{})};
  }
  const d=row.dependencies[t.selector],component=await load(t.selector);
  if(d.kind!=='Enum'){
   const fields=field(v,'fields'),entries=await Promise.all(d.record.properties.map(async p=>[p.name,await view(p.type,field(fields,p.name))]));
   return {kind:'named-record',selector:t.selector,record_kind:d.kind,owned:component.isOwned(v),frozen:Object.isFrozen(v),fields_frozen:Object.isFrozen(fields),fields_keys:Object.keys(fields).sort(),fields:Object.fromEntries(entries)};
  }
  return d.plain?{kind:'named-enum',selector:t.selector,owned:component.isOwned(v),frozen:Object.isFrozen(v),variant:field(v,'variant')}:
   {kind:'named-sum',selector:t.selector,owned:component.isOwned(v),value:await view({kind:'sum',variants:d.contract.variants},v)};
 };
 // Descriptor-only graph fingerprint: preserve identities, keys, prototypes and
 // data/accessor descriptors without calling user-shaped getters or coercions.
 const objects=new WeakMap(),symbols=new Map();let next=1;
 const identity=v=>{const ids=typeof v==='symbol'?symbols:objects;if(!ids.has(v))ids.set(v,next++);return ids.get(v);};
 const fingerprint=input=>{
  const seen=new Set();
  const visit=v=>{
   if(typeof v==='symbol')return ['symbol',identity(v)];
   if(typeof v==='function')return ['function',identity(v)];
   if(v===null||typeof v!=='object')return [typeof v,typeof v==='bigint'?v.toString():v];
   const id=identity(v);if(seen.has(id))return ['ref',id];seen.add(id);
   const proto=Object.getPrototypeOf(v),descriptors=Object.getOwnPropertyDescriptors(v);
   return ['object',id,proto===null?null:identity(proto),Reflect.ownKeys(descriptors).map(k=>{
    const d=descriptors[k];return [typeof k==='symbol'?['symbol',identity(k)]:k,d.enumerable,d.configurable,
     Object.hasOwn(d,'value')?['data',d.writable,visit(d.value)]:['accessor',d.get?identity(d.get):null,d.set?identity(d.set):null]];
   })];
  };return JSON.stringify(visit(input));
 };
 const rejects=component=>value=>component.isOwned(value)===false&&caught(()=>component.key(value)).name==='TypeError'&&component.equals(value,value)===false;
 // Factory witnesses are checked before they may serve as owned sum inputs.
 for(const d of Object.values(row.dependencies))if(d.kind!=='Enum'){
  const native=await enumImport(d.relative_path);
  for(const probe of d.probes){
   getter_reads=0;construction_changed=false;
   const input=await recordInput(probe.recipe),before=fingerprint(input),result=native[d.callable]().create(input);
   const observed={ok:result.ok,failure_codes:result.failure_codes,trace:{route:result.trace.route,phases:result.trace.phases,validators:result.trace.validators.map(v=>({rule:v.rule,outcome:v.outcome}))}};
   if(semanticJson(observed)!==semanticJson(probe.expected)||getter_reads!==0||construction_changed||before!==fingerprint(input))throw Error('factory witness observation mismatch');
  }
 }
 return {load,root,foreignRoot,recordInput,constructRecord,build,view,fingerprint,rejects,
  reset:()=>{getter_reads=0;construction_changed=false;},
  metrics:()=>({getter_reads,construction_changed})};
}
async function observeSum(row){
 const {root,foreignRoot,build,view,fingerprint,rejects,reset,metrics}=await createOwnedValueObserver(row);
 const results=[];
 for(const c of row.cases){
  reset();let input,before=null,outcome;
  try{
   const recipe=JSON.parse(c.values[0]);input=await build(recipe);before=fingerprint(input);
   const value=root.create(input),copy=root.create(await build(recipe)),baseline=root.create(await build(row.baseline)),foreign=foreignRoot.create(await build(recipe));
   const observed={view:await view(row.shape,value),key:root.key(value),owned:root.isOwned(value),frozen:Object.isFrozen(value),fresh:value!==copy,equal_copy:root.equals(value,copy),equals_baseline:root.equals(value,baseline),
    clone_rejected:rejects(root)({...value}),foreign_rejected:rejects(root)(foreign),
    metadata:{protocol_id:root.protocol_id,concept:root.concept,contract_sha256:root.contract_sha256,frozen:Object.isFrozen(root)}};
   outcome={kind:'value',value:semanticJson(observed)};
  }catch(e){outcome={kind:'error',name:e?.name,message:e?.message};}
  results.push({id:c.id,outcome,getter_reads:metrics().getter_reads,input_changed:metrics().construction_changed||(before!==null&&before!==fingerprint(input))});
 }
 return {selector:row.selector,cases:results};
}
`;
