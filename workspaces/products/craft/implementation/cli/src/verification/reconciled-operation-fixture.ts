/** Run-local deterministic transaction fixture; no filesystem, clocks or production ports. */
export const OPERATION_FIXTURE_RUNNER=String.raw`
export function buildOperationFixtureInput(recipe,onGetter=()=>{}){
 const build=r=>{
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
   case 'coercion':return {valueOf(){onGetter();return 1;},toString(){onGetter();return '1';}};
   case 'extra':{let name='extra';while(Object.hasOwn(base,name))name+='_';return {...base,[name]:true};}
   case 'symbol':return {...base,[Symbol('extra')]:true};
   case 'getter':return Object.defineProperty({...base},field,{enumerable:true,get(){onGetter();return base[field];}});
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
   case 'collection-getter':return Object.defineProperty([...base],'0',{enumerable:true,get(){onGetter();return base[0];}});
   case 'collection-hidden':return Object.defineProperty([...base],'0',{enumerable:false,value:base[0]});
   case 'duplicate':return [...base,base[0]];
   default:throw Error('unknown invalid Rule fact recipe');
  }

 };return build(recipe);
}
export async function observeOperationFixture(fn,recipe,mode='committed',mutate=null,effects=null){
 let getter_reads=0,read_calls=0,settled=false,rejected=false,outcome;
 const input=buildOperationFixtureInput(recipe,()=>getter_reads++),trace=[],batches=[],pending=[],read_requests=[],clock_calls=[];
 const rows=(effects?.reads??[]).map(r=>({...r,value:buildOperationFixtureInput(r.value,()=>getter_reads++)}));
 const objects=new Map(),symbols=new Map();let next=1;
 const id=v=>{const m=typeof v==='symbol'?symbols:objects;if(!m.has(v))m.set(v,next++);return m.get(v);};
 const fingerprint=value=>{
  const seen=new Set();let visits=0;
  const walk=(v,depth=0)=>{
   if(++visits>65536||depth>64)throw Error('OPERATION_FIXTURE_INPUT_CAPACITY');
   if(typeof v==='symbol'||typeof v==='function')return [typeof v,id(v)];
   if(v===null||typeof v!=='object')return [typeof v,typeof v==='bigint'?String(v):typeof v==='number'?Object.is(v,-0)?'-0':String(v):v];
   const n=id(v);if(seen.has(v))return ['ref',n];seen.add(v);
   const proto=Object.getPrototypeOf(v),d=Object.getOwnPropertyDescriptors(v);
   return [n,proto===null?null:id(proto),Object.isExtensible(v),Reflect.ownKeys(d).map(k=>{
    const p=d[k];return [typeof k==='symbol'?['symbol',id(k)]:k,p.enumerable,p.configurable,
     Object.hasOwn(p,'value')?['value',p.writable,walk(p.value,depth+1)]:['accessor',p.get?id(p.get):null,p.set?id(p.set):null]];
   })];
  };return JSON.stringify(walk(value));
 };
 const inputObjects=new Set();
 const collect=(v,seen=new Set())=>{
  if(!v||typeof v!=='object'||seen.has(v))return;seen.add(v);inputObjects.add(v);
  for(const p of Object.values(Object.getOwnPropertyDescriptors(v)))if(Object.hasOwn(p,'value'))collect(p.value,seen);
 };collect(input);rows.forEach(r=>collect(r.value));
 const inspect=value=>{
  const active=new Set();let visits=0;
  const walk=(v,depth=0)=>{
   if(++visits>65536||depth>64)throw Error('OPERATION_FIXTURE_OUTPUT_CAPACITY');
   if(v===null)return ['null'];
   if(typeof v==='bigint')return ['bigint',String(v)];
   if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
   if(!v||typeof v!=='object'||inputObjects.has(v)||active.has(v)||!Object.isFrozen(v))throw Error('OPERATION_FIXTURE_OUTPUT');
   active.add(v);const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);let result;
   if(Array.isArray(v)){
    if(Object.getPrototypeOf(v)!==Array.prototype||!Object.hasOwn(d.length??{},'value')||keys.length!==d.length.value+1)throw Error('OPERATION_FIXTURE_OUTPUT');
    result=['array',Array.from({length:d.length.value},(_,i)=>{const p=d[String(i)];if(!p||!p.enumerable||!Object.hasOwn(p,'value'))throw Error('OPERATION_FIXTURE_OUTPUT');return walk(p.value,depth+1);})];
   }else{
    if(Object.getPrototypeOf(v)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('OPERATION_FIXTURE_OUTPUT');
    result=['record',keys.sort().map(k=>{const p=d[k];if(!p.enumerable||!Object.hasOwn(p,'value'))throw Error('OPERATION_FIXTURE_OUTPUT');return [k,walk(p.value,depth+1)];})];
   }active.delete(v);return result;
  };return walk(value);
 };
 const defer=(phase,value,throws)=>{
  trace.push(phase);
  return new Promise((resolve,reject)=>pending.push({phase,release:()=>{
   trace.push(phase+(throws?'-rejected':'-resolved'));if(throws)reject(Error('fixture-'+phase));else resolve(value);
  }}));
 };
 const receipt=()=>{
  if(mode==='receipt-empty')return {};
  if(mode==='receipt-unknown')return {status:'unknown'};
  if(mode==='receipt-extra')return {status:'committed',extra:true};
  if(mode==='receipt-null')return null;
  if(mode==='receipt-undefined')return undefined;
  if(mode==='receipt-array')return ['committed'];
  if(mode==='receipt-inherited')return Object.assign(Object.create({extra:true}),{status:'committed'});
  if(mode==='receipt-symbol')return {status:'committed',[Symbol('extra')]:true};
  if(mode==='receipt-getter')return Object.defineProperty({},'status',{enumerable:true,get(){getter_reads++;return 'committed';}});
  if(mode==='receipt-hidden')return Object.defineProperty({},'status',{enumerable:false,value:'committed'});
  return Object.freeze({status:mode==='rejected'?'rejected':mode==='indeterminate'?'indeterminate':'committed'});
 };
 const transaction=Object.freeze({
  read:async request=>{
   read_calls++;if(!effects)throw Error('UNDECLARED_READ');
   read_requests.push(inspect(request));
   const row=rows.find(r=>r.slot===request.slot);
   if(!row)throw Error('UNDECLARED_READ');
   return defer('read:'+request.slot,row.value,row.throws===true);
  },
  commit:batch=>{batches.push(inspect(batch));return defer('commit',receipt(),mode==='commit-throw');},
  rollback:()=>defer('rollback',undefined,mode==='rollback-throw')
 });
 const clocks=Object.fromEntries((effects?.clocks??[]).filter(c=>c.mode!=='missing').map(c=>[c.slot,()=>{
  clock_calls.push(c.slot);if(c.mode==='throw')throw Error('fixture-clock');return c.value;
 }]));
 const dependencies=Object.freeze({store:Object.freeze({begin:()=>defer('begin',transaction,mode==='begin-throw')}),...(effects?{clocks}:{})});
 const readBaselines=rows.map(r=>fingerprint(r.value));
 let baseline=fingerprint(input);const promise=fn(input,dependencies);
 if(!promise||typeof promise.then!=='function')throw Error('OPERATION_FIXTURE_PROMISE');
 promise.then(v=>{settled=true;outcome=v;},()=>{settled=true;rejected=true;});
 // A caller-owned mutation between invocation and begin settlement tests capture.
 let synchronousChanged=baseline!==fingerprint(input);
 if(mutate){mutate(input,dependencies);baseline=fingerprint(input);}
 let settled_before_begin=false,settled_before_commit=false,settled_before_rollback=false,settled_before_read=false,turns=0;
 while(turns++<512){
  // Drain a fixed bounded number of native microtasks before releasing a port.
  for(let i=0;i<8;i++)await Promise.resolve();
  if(pending.length){
   const p=pending.shift();
   if(p.phase==='begin')settled_before_begin ||= settled;
   if(p.phase==='commit')settled_before_commit ||= settled;
   if(p.phase==='rollback')settled_before_rollback ||= settled;
   if(p.phase.startsWith('read:'))settled_before_read ||= settled;
   p.release();continue;
  }
  if(settled)break;
 }
 if(!settled||pending.length)throw Error('OPERATION_FIXTURE_STALLED');
 if(rejected)throw Error('OPERATION_FIXTURE_UNEXPECTED_REJECTION');
 return {outcome:inspect(outcome),trace,batches,read_calls,settled_before_begin,settled_before_commit,settled_before_rollback,getter_reads,input_changed:synchronousChanged||baseline!==fingerprint(input),
  ...(effects?{read_requests,clock_calls,settled_before_read,read_changed:rows.some((r,i)=>fingerprint(r.value)!==readBaselines[i])}:{})};
}
`;
