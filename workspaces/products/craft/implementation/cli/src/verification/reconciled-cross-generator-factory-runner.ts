import {CROSS_GENERATOR_POLICY_RUNNER} from './reconciled-cross-generator-policy-runner.js';
import {SUM_SEMANTIC_RUNNER} from './reconciled-sum-runner.js';
import {FACTORY_SEMANTIC_RUNNER} from './reconciled-factory-runner.js';

const replaceOnce = (source: string, before: string, after: string) => {
  if (source.split(before).length !== 2) throw new Error('FACTORY_PROBE:observer hook drift');
  return source.replace(before, after);
};
let observer = replaceOnce(FACTORY_SEMANTIC_RUNNER, '  reset();let input,previous,', '  beginFactoryCase();reset();let input,previous,');
observer = replaceOnce(observer, 'factory.extend(input);outcome=', 'captureFactoryCall(()=>factory.extend(input));outcome=');
observer = replaceOnce(observer,
  "const result=request.route==='transition'?factory.transition(previous,input):factory[request.route](input);",
  "const result=captureFactoryCall(()=>request.route==='transition'?factory.transition(previous,input):factory[request.route](input));");
const marker = 'let active=null,stack=[],caseTraces=[],policyPath=';
if (CROSS_GENERATOR_POLICY_RUNNER.split(marker).length !== 2) throw new Error('FACTORY_PROBE:wire prelude drift');
const prelude = CROSS_GENERATOR_POLICY_RUNNER.slice(0, CROSS_GENERATOR_POLICY_RUNNER.indexOf(marker));

/** Only target lifecycle calls are instrumented; helper construction remains separate. */
export const CROSS_GENERATOR_FACTORY_RUNNER = prelude + String.raw`
const semanticJson=value=>JSON.stringify(value&&typeof value==='object'?Array.isArray(value)?value.map(v=>JSON.parse(semanticJson(v))):Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(semanticJson(value[k]))])):value);
const caught=fn=>{try{fn();return {};}catch(e){return {name:e?.name,message:e?.message};}};
let active=null,stack=[],caseTraces=[],allowed=new Set(),foreign=new Map();
const enumImport=async(p,suffix='')=>{
 const file=safe(p);if(!allowed.has(file))throw Error('FACTORY_PROBE_MODULE');
 if(!suffix)return require(file);
 if(suffix!=='?semantic-foreign')throw Error('FACTORY_PROBE_SUFFIX');
 if(!foreign.has(file)){
  const saved=require.cache[file];delete require.cache[file];
  try{foreign.set(file,require(file));}finally{if(saved)require.cache[file]=saved;else delete require.cache[file];}
 }
 return foreign.get(file);
};
function beginFactoryCase(){if(active!==null)throw Error('FACTORY_PROBE_ACTIVE_CASE');caseTraces.push([]);}
function captureFactoryCall(fn){
 if(active!==null||!caseTraces.length)throw Error('FACTORY_PROBE_REENTRANT');
 active=caseTraces.at(-1);stack=[];
 try{return fn();}finally{active=null;stack=[];}
}
` + SUM_SEMANTIC_RUNNER + observer + String.raw`
if(!Array.isArray(payload.rows)||!payload.rows.length)throw Error('FACTORY_PROBE_EMPTY');
const rows=[];
for(const row of payload.rows){
 if(row.adapter!=='factory')throw Error('FACTORY_PROBE_ADAPTER');
 allowed=new Set(row.modules.map(m=>safe(m.relative_path)));foreign=new Map();
 for(const file of allowed)delete require.cache[file];
 caseTraces=[];active=null;stack=[];const originals=[];
 try{
  for(const r of row.rules){
   const native=await enumImport(r.relative_path),original=native[r.callable];
   if(typeof original!=='function')throw Error('FACTORY_PROBE_RULE');
   originals.push([native,r.callable,original]);
   native[r.callable]=(...args)=>{
    if(active===null)return original(...args);
    if(active.length>=65536)throw Error('FACTORY_PROBE_CALL_LIMIT');
    const index=active.length,call={selector:r.selector,parent:stack.at(-1)??null,arity:args.length,input:wire(args[0]),result:null};
    active.push(call);stack.push(index);
    try{const result=original(...args);if(typeof result!=='boolean')throw Error('FACTORY_PROBE_RULE_RESULT');call.result=result;return result;}finally{stack.pop();}
   };
  }
  const observed=await observeFactory(row);
  if(observed.cases.length!==caseTraces.length)throw Error('FACTORY_PROBE_ALIGNMENT');
  rows.push({selector:row.selector,cases:observed.cases.map((c,i)=>({...c,calls:caseTraces[i]}))});
 }finally{active=null;for(const [native,name,original]of originals)native[name]=original;}
}
console.log(JSON.stringify({controls_sha256:payload.controls_sha256,rows}));
`;

