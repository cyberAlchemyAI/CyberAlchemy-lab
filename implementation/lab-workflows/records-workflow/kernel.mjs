import {readFileSync,mkdirSync,existsSync,mkdtempSync,renameSync,rmSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {implementationRoot} from '../../../workspaces/products/craft/implementation/source-bindings.mjs';
import {createSourceOperationCompiler} from '../../artifact-runtime/compile-source-operation.mjs';
import {evaluateArtifact} from '../../artifact-runtime/pure-operation.mjs';
const here=import.meta.dirname,sha=x=>createHash('sha256').update(x).digest('hex');
export const source=sha(JSON.stringify(['workflow.alch','application.alch','../../lab-runtime/alchlang/shared-records/contracts/bounds.json'].map(f=>[f,sha(readFileSync(path.join(here,f)))])));
const operations=new Set(['EnforceRead','EnforceDirectory','EnforceViews','EnforceEvolution','EnforceHost','PlanLifecycle','EnforceViewPublication','EnforceCoverage','PlanRecordCustody']);
export async function enforce(operation,value,{cacheRoot=path.join(here,'.local')}={}){
 if(!operations.has(operation))throw Error('unsupported-records-workflow-operation');
 const output=path.join(cacheRoot,source,operation);
 if(!existsSync(path.join(output,'manifest.json'))){
  mkdirSync(path.dirname(output),{recursive:true});
  const staging=mkdtempSync(path.join(path.dirname(output),'.compile-'));
  try{
   const c=await createSourceOperationCompiler(path.join(implementationRoot,'cli')),artifact=path.join(staging,'artifact');
   c.compile({modelRoot:path.resolve(here,'../../..'),applicationPath:'implementation/lab-workflows/records-workflow/application.alch',pureSources:true,selector:'Lab.RecordsWorkflow.'+operation,outputDirectory:artifact});
   try{renameSync(artifact,output);}catch(error){if(!['EEXIST','ENOTEMPTY'].includes(error.code)||!existsSync(path.join(output,'manifest.json')))throw error;}
  }finally{rmSync(staging,{recursive:true,force:true});}
 }
 const evaluated=await evaluateArtifact(output,'operation.mjs',{value},{manifest_sha256:sha(readFileSync(path.join(output,'manifest.json')))});
 if(!evaluated.ok)throw Error(JSON.stringify(evaluated.error));
 const result=JSON.parse(new TextDecoder().decode(evaluated.wire));
 if(result.tag!=='Returned')throw Error(result.fields.code);
 return result.fields.value;
}
