import {OPERATION_FIXTURE_RUNNER} from './reconciled-operation-fixture.js';
import {WORKFLOW_FIXTURE_RUNNER} from './reconciled-workflow-fixture.js';

// The public runner already includes Operation's inert input builder. Reuse its
// exact shared prefix once; a changed construction hook must fail, not duplicate globals.
const boundary = OPERATION_FIXTURE_RUNNER.indexOf('export async function observeOperationFixture');
if (boundary < 0 || !WORKFLOW_FIXTURE_RUNNER.startsWith(OPERATION_FIXTURE_RUNNER.slice(0, boundary))) throw new TypeError('WORKFLOW_RUNNER:fixture builder drift');
const observer = WORKFLOW_FIXTURE_RUNNER.slice(boundary).replace(/^export (async )?function /gm, (_, async: string | undefined) => (async ?? '') + 'function ');
export const WORKFLOW_SEMANTIC_RUNNER = observer + String.raw`
function expandWorkflowCase(row,data){
 let visits=0,bytes=0;const active=new Set();
 const charge=v=>{bytes+=Buffer.byteLength(JSON.stringify(v),'utf8')+1;if(bytes>8388608)throw Error('WORKFLOW_RECIPE_CAPACITY');};
 const read=(r,depth=0)=>{
  if(++visits>65536||depth>128)throw Error('WORKFLOW_RECIPE_CAPACITY');
  if(!r||typeof r!=='object'||Array.isArray(r))throw Error('WORKFLOW_RECIPE');
  if(r.tag==='ref'){
   if(typeof r.value!=='string'||!/^(0|[1-9][0-9]*)$/.test(r.value))throw Error('WORKFLOW_RECIPE');
   const index=Number(r.value);if(!Number.isSafeInteger(index)||index>=row.recipes.length||active.has(index))throw Error('WORKFLOW_RECIPE');
   active.add(index);const value=read(row.recipes[index],depth+1);active.delete(index);return value;
  }
  const out={};charge({});
  for(const [key,value]of Object.entries(r)){
   charge(key);
   if(['base','input','payload'].includes(key))out[key]=read(value,depth+1);
   else if(key==='items'){if(!Array.isArray(value))throw Error('WORKFLOW_RECIPE');charge([]);out.items=value.map(v=>read(v,depth+1));}
   else if(key==='fields'){
    if(!value||typeof value!=='object'||Array.isArray(value))throw Error('WORKFLOW_RECIPE');
    charge({});out.fields=Object.fromEntries(Object.entries(value).map(([k,v])=>{charge(k);return [k,read(v,depth+1)];}));
   }else{charge(value);out[key]=value;}
  }return out;
 };
 const expand=index=>{if(!Number.isSafeInteger(index)||index<0)throw Error('WORKFLOW_RECIPE');return read({tag:'ref',value:String(index)});};
 if(!data||typeof data!=='object'||!Array.isArray(data.steps)||data.steps.length!==row.workflow_steps.length||data.steps.some((s,i)=>s.step_id!==row.workflow_steps[i].step_id))throw Error('WORKFLOW_OCCURRENCES');
 const {input,steps,...metadata}=data;charge(metadata);
 return {...data,input:expand(input),steps:steps.map(step=>{
  const {reads,...metadata}=step;charge(metadata);if(!Array.isArray(reads))throw Error('WORKFLOW_RECIPE');
  return {...step,reads:reads.map(r=>{const {value,...metadata}=r;charge(metadata);return {...r,value:expand(value)};})};
 })};
}
async function observeWorkflow(row){
 const native=await enumImport(row.relative_path),fn=native[row.callable],results=[];
 if(typeof fn!=='function')throw Error('WORKFLOW_CALLABLE');
 const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
 for(const c of row.cases){
  let outcome;
  try{
   if(c.mode==='workflow-descriptor')outcome={kind:'value',value:canonical(operationDescriptor(fn))};
   else if(c.mode==='workflow'){
    const data=JSON.parse(c.values[0]),selected=expandWorkflowCase(row,data);
    outcome={kind:'value',value:canonical(await observeWorkflowFixture(fn,row.workflow_steps,selected))};
   }else throw Error('WORKFLOW_CASE_MODE');
  }catch{outcome={kind:'unexpected-error'};}
  results.push({id:c.id,outcome,getter_reads:0,input_changed:false});
 }
 return {selector:row.selector,cases:results};
}
`;
