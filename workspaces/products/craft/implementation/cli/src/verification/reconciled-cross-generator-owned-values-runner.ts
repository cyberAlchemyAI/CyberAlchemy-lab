import {CROSS_GENERATOR_POLICY_RUNNER} from './reconciled-cross-generator-policy-runner.js';
import {SUM_SEMANTIC_RUNNER} from './reconciled-sum-runner.js';
const marker='let active=null,stack=[],caseTraces=[],policyPath=';
if(CROSS_GENERATOR_POLICY_RUNNER.split(marker).length!==2)throw Error('OWNED_PROBE:prelude drift');
const prelude=CROSS_GENERATOR_POLICY_RUNNER.slice(0,CROSS_GENERATOR_POLICY_RUNNER.indexOf(marker));
/** Recipes construct inputs; only original target provider calls form the trace. */
export const CROSS_GENERATOR_OWNED_VALUES_RUNNER=prelude+String.raw`

const semanticJson=value=>JSON.stringify(value&&typeof value==='object'?Array.isArray(value)?value.map(v=>JSON.parse(semanticJson(v))):Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(semanticJson(value[k]))])):value);
const caught=fn=>{try{fn();return {};}catch(e){return {name:e?.name,message:e?.message};}};
let allowed=new Set(),foreign=new Map(),active=null,identities=new WeakMap();
const enumImport=async(p,suffix='')=>{
 const file=safe(p);if(!allowed.has(file))throw Error('OWNED_PROBE_MODULE');
 if(!suffix)return require(file);
 if(suffix!=='?semantic-foreign')throw Error('OWNED_PROBE_SUFFIX');
 if(!foreign.has(file)){const saved=require.cache[file];delete require.cache[file];try{foreign.set(file,require(file));}finally{if(saved)require.cache[file]=saved;else delete require.cache[file];}}
 return foreign.get(file);
};
`+SUM_SEMANTIC_RUNNER+String.raw`
const data=(v,k)=>{const d=v!==null&&(typeof v==='object'||typeof v==='function')?Object.getOwnPropertyDescriptor(v,k):null;if(!d||!Object.hasOwn(d,'value'))throw Error('OWNED_PROBE_DATA');return d.value;};
function indexInput(row,input){
 identities=new WeakMap();
 const walk=(type,value,p)=>{
  if(type.kind==='named'){
   if(value!==null&&(typeof value==='object'||typeof value==='function')){
    const paths=identities.get(value)||[];paths.push(p);paths.sort((a,b)=>JSON.stringify(a)<JSON.stringify(b)?-1:1);identities.set(value,paths);
   }return;
  }
  if(type.kind==='optional'){if(value!==null)walk(type.element,value,p);return;}
  if(type.kind==='list'||type.kind==='set'){for(let i=0;i<value.length;i++)walk(type.element,data(value,String(i)),[...p,i]);return;}
  if(type.kind==='sum'){const v=type.variants.find(v=>v.name===data(value,'variant'));if(v?.payload)walk(v.payload,data(value,'payload'),[...p,'payload']);}
 };
 for(const f of row.fields)walk(f.type,data(input,f.name),[f.name]);
}
if(!Array.isArray(payload.rows)||!payload.rows.length)throw Error('OWNED_PROBE_EMPTY');
const rows=[];
for(const row of payload.rows){
 allowed=new Set(row.modules.map(m=>safe(m.relative_path)));foreign=new Map();for(const file of allowed)delete require.cache[file];
 const originals=[],installed=new Set(),visiting=new Set();
 const install=async selector=>{
  if(installed.has(selector))return;if(visiting.has(selector))throw Error('OWNED_PROBE_CYCLE');visiting.add(selector);
  const d=row.dependencies[selector];if(!d)throw Error('OWNED_PROBE_DEPENDENCY');
  const children=new Set(),walk=t=>{if(t.kind==='named')children.add(t.selector);else if(t.kind==='sum')for(const v of t.variants){if(v.payload)walk(v.payload);}else if(t.element)walk(t.element);};
  if(d.kind==='Enum')walk({kind:'sum',variants:d.contract.variants});else for(const f of d.record.properties)walk(f.type);
  for(const child of [...children].sort())await install(child);
  const native=await enumImport(d.relative_path),original=native[d.symbol];
  if(!original||typeof original.isOwned!=='function'||typeof original.key!=='function')throw Error('OWNED_PROBE_PROVIDER');
  const wrapper={...original};
  for(const method of ['isOwned','key'])wrapper[method]=(...args)=>{
   if(active===null)return original[method](...args);
   if(active.length>=65536)throw Error('OWNED_PROBE_LIMIT');
   const value=args[0],call={provider:selector,method,arity:args.length,input_paths:value!==null&&(typeof value==='object'||typeof value==='function')?identities.get(value)??null:null,result:null};
   active.push(call);
   try{const result=original[method](...args);call.result=result;return result;}catch(e){call.result={error:{name:e?.name,message:e?.message}};throw e;}
  };
  originals.push([native,d.symbol,original]);native[d.symbol]=Object.freeze(wrapper);visiting.delete(selector);installed.add(selector);
 };
 try{
  await install(row.selector);
  const observer=await createOwnedValueObserver(row),native=await enumImport(row.relative_path),results=[];
  for(const c of row.cases){
   observer.reset();active=null;
   const input=await observer.recordInput(c.recipe),before=observer.fingerprint(input),factory=native[row.callable]();
   const previous=c.route==='transition'?await observer.constructRecord(c.previous):null,previousBefore=previous?observer.fingerprint(previous):null;
   indexInput(row,input);const calls=[];let result,outcome;
   try{active=calls;result=c.route==='transition'?factory.transition(previous,input):factory[c.route](input);}
   catch(e){outcome={error:{name:e?.name,message:e?.message}};}
   finally{active=null;}
   if(result){
    const ok=data(result,'ok'),trace=data(result,'trace');
    outcome={ok,failure_codes:data(result,'failure_codes'),trace:{route:data(trace,'route'),phases:data(trace,'phases'),validators:data(trace,'validators').map(v=>({rule:data(v,'rule'),outcome:data(v,'outcome')}))},value_key:null,value_view:null};
    if(ok===true){const value=data(result,'value');outcome.value_key=observer.root.key(value);outcome.value_view=await observer.view(row.shape,value);}
    else if(data(result,'value')!==null)throw Error('OWNED_PROBE_FAILED_VALUE');
   }
   results.push({id:c.id,outcome,calls,getter_reads:observer.metrics().getter_reads,input_changed:observer.metrics().construction_changed||before!==observer.fingerprint(input)||(previousBefore!==null&&previousBefore!==observer.fingerprint(previous))});
  }
  rows.push({selector:row.selector,cases:results});
 }finally{active=null;for(const [native,name,original]of originals)native[name]=original;}
}
console.log(JSON.stringify({controls_sha256:payload.controls_sha256,rows}));
`;
