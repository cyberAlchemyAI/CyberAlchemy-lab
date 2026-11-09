/** Bounded conductor for source-compiled pure components. No business expressions. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {evaluateArtifact} from './pure-operation.mjs';
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const encoder=new TextEncoder();
export async function evaluatePipeline(directory,manifest_sha256,input){
 const raw=readFileSync(path.join(directory,'manifest.json'));
 if(hash(raw)!==manifest_sha256)throw Error('pipeline-manifest-drift');
 const manifest=JSON.parse(raw),files=new Map(manifest.files.map(row=>[row.path,row]));
 function exact(name){
  if(typeof name!=='string'||path.posix.normalize(name)!==name||path.posix.isAbsolute(name)||name.split('/').includes('..')||name.includes('\\'))throw Error('invalid-pipeline-member');
  const selected=files.get(name);if(!selected)throw Error('unselected-pipeline-member');
  const value=readFileSync(path.join(directory,name));if(value.length!==selected.bytes||hash(value)!==selected.sha256)throw Error('pipeline-member-drift');return value;
 }
 const plan=JSON.parse(exact('plan.json'));
 if(!Array.isArray(plan.steps)||plan.steps.length>100)throw Error('pipeline-step-bound');
 const fuelLimit=BigInt(plan.max_fuel);if(fuelLimit<=0n||fuelLimit>20000000n)throw Error('pipeline-fuel-bound');
 const bindings=new Map(Object.entries(input));let fuel=0;
 for(const step of plan.steps){
  const selected=manifest.selections[step.selector];if(!selected)throw Error('unselected-pipeline-stage');
  const componentPath=selected+'/manifest.json',componentRaw=exact(componentPath),component=JSON.parse(componentRaw);
  if(component.selector!==step.selector||!['Operation','Mapping','Calculation','Policy','Rule'].includes(component.role))throw Error('pipeline-stage-role-mismatch');
  const args=Object.create(null);
  for(const arg of step.arguments){if(!bindings.has(arg.binding)||Object.hasOwn(args,arg.parameter))throw Error('pipeline-binding-missing-or-duplicate');args[arg.parameter]=bindings.get(arg.binding);}
  if(bindings.has(step.bind))throw Error('pipeline-binding-overwrite');
  const result=await evaluateArtifact(path.join(directory,selected),'operation.mjs',args,{manifest_sha256:hash(componentRaw)});
  fuel+=result.fuel_used??0;
  if(BigInt(fuel)>fuelLimit)return {ok:false,error:{code:'ResourceLimit'},fuel_used:fuel};
  if(!result.ok)return {...result,fuel_used:fuel};
  const value=JSON.parse(new TextDecoder().decode(result.wire));
  if(component.role==='Operation'){
   if(value.tag!=='Returned')return {ok:true,wire:encoder.encode(JSON.stringify(value)),fuel_used:fuel};
   bindings.set(step.bind,value.fields.value);
  }else bindings.set(step.bind,value);
 }
 if(!bindings.has(plan.result))throw Error('pipeline-result-missing');
 return {ok:true,wire:encoder.encode(JSON.stringify({tag:'Returned',fields:{value:bindings.get(plan.result)}})),fuel_used:fuel};
}