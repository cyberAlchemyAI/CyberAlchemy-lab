// Generic bounded pure composition. Open questions: ../QUERY-ITERATION.md.
export type IterationPlan={sourceField:string;inputField:string;itemField:string;outputField:string;maxItems:number;maxOutputBytes:number;maxInputBytes:number;timeoutMs:number};
type Invoke=(input:any,env?:any,io?:any)=>Promise<any>;
const fault=(code:string):never=>{throw Object.assign(new Error(code),{code});};
export function createQueryIteration(plan:IterationPlan,source:Invoke,mapping:Invoke,item:Invoke){
 return async function invoke(input:any,_env:any={},io:{signal?:AbortSignal}={}){
  const deadline=performance.now()+plan.timeoutMs;
  const check=()=>{if(io.signal?.aborted)fault('QUERY_ITERATION_CANCELLED');if(performance.now()>=deadline)fault('QUERY_ITERATION_TIMEOUT');};
  const size=(value:any)=>{const json=JSON.stringify(value);if(json===undefined)fault('QUERY_ITERATION_VALUE');return new TextEncoder().encode(json).length;};
  check();if(size(input)>plan.maxInputBytes)fault('QUERY_ITERATION_INPUT_LIMIT');
  const context=structuredClone(input),control={signal:io.signal,localOnly:true,fetch:()=>fault('QUERY_ITERATION_EFFECT')};
  const selected=await source(context,{},control);check();const values=selected[plan.sourceField];
  if(!Array.isArray(values)||values.length>plan.maxItems)fault('QUERY_ITERATION_ITEM_LIMIT');
  const results:any[]=[];const output={[plan.outputField]:results};
  if(size(output)>plan.maxOutputBytes)fault('QUERY_ITERATION_OUTPUT_LIMIT');
  for(const value of values){
   // Yield to cancellation between items; no effectful work or partial result escapes.
   await new Promise<void>(resolve=>setTimeout(resolve,0));check();
   const mapped=await mapping({context,item:value},{},control);check();
   const result=await item(mapped[plan.inputField],{},control);check();
   if(!Object.hasOwn(result,plan.itemField))fault('QUERY_ITERATION_VALUE');
   results.push(result[plan.itemField]);if(size(output)>plan.maxOutputBytes)fault('QUERY_ITERATION_OUTPUT_LIMIT');
  }
  check();return output;
 };
}
