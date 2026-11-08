import {OPERATION_FIXTURE_RUNNER} from './reconciled-operation-fixture.js';

/** Reuse only inert fixture-input construction, not an expected-behavior oracle. */
const boundary = OPERATION_FIXTURE_RUNNER.indexOf('export async function observeOperationFixture');
if (boundary < 0) throw new TypeError('WORKFLOW_FIXTURE:Operation input builder boundary');
export const WORKFLOW_FIXTURE_RUNNER = OPERATION_FIXTURE_RUNNER.slice(0, boundary) + String.raw`
export async function observeWorkflowFixture(fn, sourceSteps, selected){
 let getter_reads=0,settled=false,rejected=false,outcome,position=0,settled_while_pending=false,overlapping_ports=false;
 const input=buildOperationFixtureInput(selected.input,()=>getter_reads++),pending=[],port_trace=[],batches=[],read_requests=[],clock_calls=[];
 const rows=selected.steps.map((s,i)=>({...s,operation_ref:sourceSteps[i].operation_ref,reads:s.reads.map(r=>({...r,value:buildOperationFixtureInput(r.value,()=>getter_reads++)}))}));
 const inputObjects=new Set(),ids=new Map();let nextId=1;
 const id=v=>{if(!ids.has(v))ids.set(v,nextId++);return ids.get(v);};
 const collect=(v,seen=new Set())=>{
  if(!v||typeof v!=='object'||seen.has(v))return;seen.add(v);inputObjects.add(v);
  for(const p of Object.values(Object.getOwnPropertyDescriptors(v)))if(Object.hasOwn(p,'value'))collect(p.value,seen);
 };
 collect(input);rows.forEach(r=>r.reads.forEach(x=>collect(x.value)));
 const fingerprint=v=>{
  let visits=0;const seen=new Set();
  const walk=(v,depth=0)=>{
   if(++visits>65536||depth>128)throw Error('WORKFLOW_FIXTURE_INPUT_CAPACITY');
   if(typeof v==='symbol'||typeof v==='function')return [typeof v,id(v)];
   if(v===null||typeof v!=='object')return [typeof v,typeof v==='bigint'?String(v):typeof v==='number'?Object.is(v,-0)?'-0':String(v):v];
   const n=id(v);if(seen.has(v))return ['ref',n];seen.add(v);
   const proto=Object.getPrototypeOf(v),d=Object.getOwnPropertyDescriptors(v);
   return [n,proto===null?null:id(proto),Object.isExtensible(v),Reflect.ownKeys(d).map(k=>{const p=d[k];return [typeof k==='symbol'?['symbol',id(k)]:k,p.enumerable,p.configurable,
    Object.hasOwn(p,'value')?['value',p.writable,walk(p.value,depth+1)]:['accessor',p.get?id(p.get):null,p.set?id(p.set):null]];})];
  };return JSON.stringify(walk(v));
 };
 const inspect=v=>{
  let visits=0;const active=new Set();
  const walk=(v,depth=0)=>{
   if(++visits>65536||depth>128)throw Error('WORKFLOW_FIXTURE_OUTPUT_CAPACITY');
   if(v===null)return ['null'];if(typeof v==='bigint')return ['bigint',String(v)];
   if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
   if(!v||typeof v!=='object'||inputObjects.has(v)||active.has(v)||!Object.isFrozen(v))throw Error('WORKFLOW_FIXTURE_OUTPUT');
   active.add(v);const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);let value;
   if(Array.isArray(v)){
    if(Object.getPrototypeOf(v)!==Array.prototype||keys.length!==d.length.value+1)throw Error('WORKFLOW_FIXTURE_OUTPUT');
    value=['array',Array.from({length:d.length.value},(_,i)=>{const p=d[String(i)];if(!p?.enumerable||!Object.hasOwn(p,'value'))throw Error('WORKFLOW_FIXTURE_OUTPUT');return walk(p.value,depth+1);})];
   }else{
    if(Object.getPrototypeOf(v)!==Object.prototype||keys.some(k=>typeof k!=='string'))throw Error('WORKFLOW_FIXTURE_OUTPUT');
    value=['record',keys.sort().map(k=>{const p=d[k];if(!p.enumerable||!Object.hasOwn(p,'value'))throw Error('WORKFLOW_FIXTURE_OUTPUT');return [k,walk(p.value,depth+1)];})];
   }active.delete(v);return value;
  };return walk(v);
 };
 const defer=(row,phase,value,throws=false)=>{
  overlapping_ports ||= pending.length>0;port_trace.push(row.step_id+':'+phase);
  return new Promise((resolve,reject)=>pending.push(()=>{port_trace.push(row.step_id+':'+phase+(throws?'-rejected':'-resolved'));if(throws)reject(Error('workflow-fixture-port'));else resolve(value);}));
 };
 const receipt=mode=>{
  if(mode==='receipt-empty')return {};if(mode==='receipt-unknown')return {status:'unknown'};if(mode==='receipt-extra')return {status:'committed',extra:true};
  if(mode==='receipt-null')return null;if(mode==='receipt-undefined')return undefined;if(mode==='receipt-array')return ['committed'];
  if(mode==='receipt-inherited')return Object.assign(Object.create({extra:true}),{status:'committed'});
  if(mode==='receipt-symbol')return {status:'committed',[Symbol('extra')]:true};
  if(mode==='receipt-getter')return Object.defineProperty({},'status',{enumerable:true,get(){getter_reads++;return 'committed';}});
  if(mode==='receipt-hidden')return Object.defineProperty({},'status',{enumerable:false,value:'committed'});
  return {status:mode==='rejected'?'rejected':mode==='indeterminate'?'indeterminate':'committed'};
 };
 const active=new Map();
 const dependencies=Object.fromEntries([...new Set(sourceSteps.map(s=>s.operation_ref))].map(selector=>{
  const first=rows.find(r=>r.operation_ref===selector);
  const clocks=Object.fromEntries(first.clocks.filter(c=>c.mode!=='missing').map(c=>[c.slot,()=>{
   const row=active.get(selector),clock=row?.clocks.find(x=>x.slot===c.slot);if(!clock)throw Error('WORKFLOW_FIXTURE_CLOCK');
   clock_calls.push(row.step_id+':'+c.slot);if(clock.mode==='throw')throw Error('workflow-fixture-clock');return clock.value;
  }]));
  const store=Object.freeze({begin:()=>{
   const row=rows[position++];if(!row||row.operation_ref!==selector)throw Error('WORKFLOW_FIXTURE_OCCURRENCE');active.set(selector,row);
   const transaction=Object.freeze({read:request=>{
    read_requests.push({step_id:row.step_id,value:inspect(request)});const value=row.reads.find(r=>r.slot===request.slot);
    if(!value)throw Error('WORKFLOW_FIXTURE_UNDECLARED_READ');return defer(row,'read:'+request.slot,value.value,value.throws===true);
   },commit:batch=>{batches.push({step_id:row.step_id,value:inspect(batch)});return defer(row,'commit',receipt(row.mode),row.mode==='commit-throw');},
   rollback:()=>defer(row,'rollback',undefined,row.mode==='rollback-throw')});
   return defer(row,'begin',transaction,row.mode==='begin-throw');
  }});
  return [selector,Object.freeze({store,clocks})];
 }));
 const readBaselines=rows.flatMap(r=>r.reads.map(v=>fingerprint(v.value)));
 let baseline=fingerprint(input);const promise=fn(input,selected.identity,dependencies);
 if(!promise||typeof promise.then!=='function')throw Error('WORKFLOW_FIXTURE_PROMISE');
 promise.then(v=>{settled=true;outcome=v;},()=>{settled=true;rejected=true;});
 const synchronousChanged=baseline!==fingerprint(input);
 if(selected.capture){
  for(const k of Object.keys(input)){const p=Object.getOwnPropertyDescriptor(input,k);if(p&&Object.hasOwn(p,'value')&&p.writable)input[k]=typeof p.value==='string'?p.value+'-changed':typeof p.value==='bigint'?p.value+1n:typeof p.value==='boolean'?!p.value:null;}
  for(const k of Object.keys(dependencies))dependencies[k]=Object.freeze({store:Object.freeze({begin:()=>{throw Error('late-workflow-dependency');}})});
  baseline=fingerprint(input);
 }
 for(let turn=0;turn<(sourceSteps.length+1)*1024;turn++){
  for(let n=0;n<8;n++)await Promise.resolve();
  if(pending.length){settled_while_pending ||= settled;pending.shift()();continue;}
  if(settled)break;
 }
 if(!settled||pending.length)throw Error('WORKFLOW_FIXTURE_STALLED');
 return {rejected,outcome:rejected?null:inspect(outcome),port_trace,batches,read_requests,clock_calls,settled_while_pending,overlapping_ports,getter_reads,
  input_changed:synchronousChanged||baseline!==fingerprint(input),read_changed:rows.flatMap(r=>r.reads.map(v=>fingerprint(v.value))).some((v,i)=>v!==readBaselines[i])};
}
`;
