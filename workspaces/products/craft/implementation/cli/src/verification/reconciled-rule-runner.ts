/** Data-only Rule, Policy and reducer observer; no factory or effect provider is loaded. */
export const RULE_SEMANTIC_RUNNER=String.raw`
async function observeRule(row){
 const native=await enumImport(row.relative_path),fn=native[row.callable],results=[];
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

 // Read only inert, closed, deeply frozen outcomes; never invoke output getters/toJSON.
 const stateMachineOutcome=value=>{
  const invalid=()=>{throw Error('STATE_MACHINE_OUTCOME');};
  const record=(v,keys)=>{
   if(!v||typeof v!=='object'||Object.getPrototypeOf(v)!==Object.prototype||!Object.isFrozen(v))return invalid();
   const d=Object.getOwnPropertyDescriptors(v),actual=Reflect.ownKeys(d);
   if(actual.length!==keys.length||actual.some(k=>typeof k!=='string'||!keys.includes(k)))return invalid();
   if(keys.some(k=>!d[k]||!Object.hasOwn(d[k],'value')||!d[k].enumerable))return invalid();
   return Object.fromEntries(keys.map(k=>[k,d[k].value]));
  };
  const d=value&&typeof value==='object'?Object.getOwnPropertyDescriptors(value):{},status=d.status?.value;
  const r=record(value,status==='transitioned'?['status','state','transition_id','output_intents']:['status','state','reason','output_intents']);
  if(!['transitioned','rejected'].includes(status)||typeof r.state!=='string'||(status==='transitioned'?typeof r.transition_id!=='string':!['guard','no-transition'].includes(r.reason)))return invalid();
  const a=r.output_intents;if(!Array.isArray(a)||Object.getPrototypeOf(a)!==Array.prototype||!Object.isFrozen(a))return invalid();
  const props=Object.getOwnPropertyDescriptors(a),length=props.length.value;
  if(length>128||Reflect.ownKeys(props).length!==length+1)return invalid();
  const intents=[];
  for(let i=0;i<length;i++){
   const p=props[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable)return invalid();
   const item=record(p.value,['event_ref','slot']);if(typeof item.event_ref!=='string'||typeof item.slot!=='string')return invalid();intents.push(item);
  }
  if(status==='rejected'&&intents.length)return invalid();
  const result={...r,output_intents:intents};
  return JSON.stringify(Object.fromEntries(Object.keys(result).sort().map(k=>[k,result[k]])));
 };

 for(const c of row.cases){
  getter_reads=0;let input,before=null,outcome;
  try{
   if(row.adapter==='state-machine'&&c.mode==='initial-state')outcome=typeof native.initialState==='string'?{kind:'value',value:native.initialState}:{kind:'unexpected',type:typeof native.initialState};
   else if(row.adapter==='state-machine'){
    input=[build(JSON.parse(c.values[1])),build(JSON.parse(c.values[2])),build(row.recipes[Number(c.values[0])])];before=fingerprint(input);
    outcome={kind:'value',value:stateMachineOutcome(fn(...input))};
   }else{input=build(row.recipes[Number(c.values[0])]);before=fingerprint(input);const value=fn(input);outcome=typeof value===(row.adapter==='policy'?'string':'boolean')?{kind:'value',value:String(value)}:{kind:'unexpected',type:typeof value};}
  }
  catch(e){outcome={kind:'error',name:e?.name,message:e?.message};}
  results.push({id:c.id,outcome,getter_reads,input_changed:before!==null&&before!==fingerprint(input)});
 }
 return {selector:row.selector,cases:results};
}
`;
