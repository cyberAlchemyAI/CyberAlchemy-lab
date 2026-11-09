import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../../../craft/implementation/source-bindings.mjs';
import {build as buildApplication,inputs as applicationInputs} from '../build.mjs';
import {createSourceOperationCompiler} from '../../../../../../../implementation/artifact-runtime/compile-source-operation.mjs';
export const root=import.meta.dirname;
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
export const sha=value=>createHash('sha256').update(value).digest('hex');
export const inputs=applicationInputs;
const compiler=await createSourceOperationCompiler(path.join(craftRoot,'cli'));
const genericRoot=path.resolve(root,'../../../../../../../implementation/artifact-runtime');
const sourceOf=application=>sha(JSON.stringify({application:application.source,manifest:application.files['manifest.json'],selector:'Define.AuthorPlan',adapters:['compile-source-operation.mjs','evaluate-pure.mjs','pure-operation.mjs','pure-pipeline.mjs'].map(name=>[name,sha(readFileSync(path.join(genericRoot,name)))]),builder:sha(readFileSync(import.meta.filename))}));
export const fingerprint=()=>sourceOf(buildApplication());
export function build(){
 const application=buildApplication(),digest=sourceOf(application),base=path.join(root,'.local');mkdirSync(base,{recursive:true});
 const index=path.join(base,'current-source-'+digest+'.json');
 if(existsSync(index)){
  const saved=JSON.parse(readFileSync(index));
  if(saved.source!==digest||saved.application_source!==application.source)throw Error('current-source-projection-drift');
  for(const [name,hash] of Object.entries(saved.files))if(sha(readFileSync(path.join(saved.output,name)))!==hash)throw Error('generated-artifact-drift');
  return saved;
 }
 const directory=mkdtempSync(path.join(base,'current-source-')),output=path.join(directory,'generated');mkdirSync(output);
 const modelRoot=path.join(application.output,'model'),planDirectory=path.join(directory,'planner');
 compiler.compile({modelRoot,selector:'Define.AuthorPlan',outputDirectory:planDirectory});
 const planned=spawnSync(node,[path.join(genericRoot,'evaluate-pure.mjs'),planDirectory,'operation.mjs',sha(readFileSync(path.join(planDirectory,'manifest.json')))],{input:JSON.stringify({marker:true}),encoding:'utf8',maxBuffer:1024*1024});
 if(planned.status!==0)throw Error('author-plan-evaluation-failed: '+planned.stderr);
 const plan=JSON.parse(planned.stdout).value;writeFileSync(path.join(output,'plan.json'),JSON.stringify(plan,null,2)+'\n',{flag:'wx'});
 const selections={};mkdirSync(path.join(output,'stages'));
 for(const selector of new Set(plan.steps.map(step=>step.selector))){
  const relative='stages/'+String(Object.keys(selections).length).padStart(3,'0');
  compiler.compile({modelRoot,selector,outputDirectory:path.join(output,relative)});selections[selector]=relative;
 }
 if(sourceOf(buildApplication())!==digest)throw Error('source-changed-during-build');
 const rows=[];
 function inventory(dir,prefix=''){for(const item of readdirSync(dir,{withFileTypes:true})){const name=prefix+item.name;if(item.isDirectory())inventory(path.join(dir,item.name),name+'/');else if(item.isFile()){const raw=readFileSync(path.join(dir,item.name));rows.push({path:name,sha256:sha(raw),bytes:raw.length});}else throw Error('unexpected-projection-file');}}
 inventory(output);
 writeFileSync(path.join(output,'manifest.json'),JSON.stringify({schema_version:'generic-compiled-pipeline/v1',source:digest,application_source:application.source,selections,files:rows,authority_effect:'none'},null,2)+'\n',{flag:'wx'});
 const files=Object.fromEntries(rows.map(row=>[row.path,row.sha256]));files['manifest.json']=sha(readFileSync(path.join(output,'manifest.json')));
 const result={source:digest,application_source:application.source,output,files,toolchain:application.toolchain,session_engine:'current-authored-source',selected_plan:'Define.AuthorPlan'};
 writeFileSync(index,JSON.stringify(result,null,2)+'\n',{flag:'wx'});return result;
}