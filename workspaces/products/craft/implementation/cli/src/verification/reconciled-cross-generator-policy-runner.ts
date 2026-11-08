import {RULE_SEMANTIC_RUNNER} from './reconciled-rule-runner.js';

/** Private instrumented native observer. Expected answers never enter this child. */
export const CROSS_GENERATOR_POLICY_RUNNER = String.raw`
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const payload=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),root=path.resolve(process.argv[3]),require=createRequire(import.meta.url);
const safe=p=>{if(typeof p!=='string'||!p.endsWith('.ts')||path.posix.normalize(p)!==p||p.startsWith('../')||path.isAbsolute(p)||p.includes('\\'))throw Error('POLICY_PROBE_PATH');return path.join(root,p.replace(/\.ts$/,'.js'));};
const wire=(v,depth=0)=>{
 if(depth>64)throw Error('POLICY_PROBE_VALUE_DEPTH');
 if(v===null)return ['null'];
 if(typeof v==='bigint')return ['bigint',v.toString()];
 if(typeof v==='function'||typeof v==='symbol')throw Error('POLICY_PROBE_ACTIVE_VALUE');
 if(typeof v!=='object')return [typeof v,v];
 const d=Object.getOwnPropertyDescriptors(v);
 if(Reflect.ownKeys(d).some(k=>typeof k!=='string'||!Object.hasOwn(d[k],'value')))throw Error('POLICY_PROBE_ACTIVE_VALUE');
 if(Array.isArray(v)){
  if(Object.getPrototypeOf(v)!==Array.prototype||Reflect.ownKeys(d).length!==v.length+1)throw Error('POLICY_PROBE_ARRAY');
  return ['array',Array.from({length:v.length},(_,i)=>{if(!d[i]||!d[i].enumerable)throw Error('POLICY_PROBE_ARRAY');return wire(d[i].value,depth+1);})];
 }
 if(Object.getPrototypeOf(v)!==null&&Object.getPrototypeOf(v)!==Object.prototype)throw Error('POLICY_PROBE_PROTOTYPE');
 return ['object',Object.keys(d).sort().map(k=>{if(!d[k].enumerable)throw Error('POLICY_PROBE_HIDDEN');return [k,wire(d[k].value,depth+1)];})];
};
let active=null,stack=[],caseTraces=[],policyPath='',policyCallable='';
const enumImport=async p=>{
 const native=require(safe(p));
 if(p!==policyPath)throw Error('POLICY_PROBE_ROOT');
 const original=native[policyCallable];
 return {[policyCallable]:(...args)=>{active=[];stack=[];caseTraces.push(active);return original(...args);}};
};
${RULE_SEMANTIC_RUNNER}
const rows=[];
for(const row of payload.rows){
 // Fresh module instances for each Policy prevent instrumentation leaking between families.
 for(const m of row.modules)delete require.cache[safe(m.relative_path)];
 caseTraces=[];policyPath=row.relative_path;policyCallable=row.callable;
 const originals=[];
 try{
  for(const r of row.rules){
   const native=require(safe(r.relative_path)),original=native[r.callable];
   if(typeof original!=='function')throw Error('POLICY_PROBE_RULE');
   originals.push([native,r.callable,original]);
   native[r.callable]=(...args)=>{
    if(!active||active.length>=65536)throw Error('POLICY_PROBE_CALL_LIMIT');
    const index=active.length,call={selector:r.selector,parent:stack.at(-1)??null,arity:args.length,input:wire(args[0]),result:null};
    active.push(call);stack.push(index);
    try{const value=original(...args);if(typeof value!=='boolean')throw Error('POLICY_PROBE_RULE_RESULT');call.result=value;return value;}finally{stack.pop();}
   };
  }
  const observed=await observeRule(row);
  if(observed.cases.length!==caseTraces.length)throw Error('POLICY_PROBE_CASE_TRACE_ALIGNMENT');
  rows.push({selector:row.selector,cases:observed.cases.map((c,i)=>({...c,calls:caseTraces[i]}))});
 }finally{active=null;for(const [native,name,original]of originals)native[name]=original;}
}
console.log(JSON.stringify({controls_sha256:payload.controls_sha256,rows}));
`;
