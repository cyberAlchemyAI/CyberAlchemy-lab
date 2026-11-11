import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,readdirSync,cpSync} from 'node:fs';
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
const sourceOf=application=>sha(JSON.stringify({application:application.source,manifest:application.files['manifest.json'],selector:'Define.AuthorPlan',definition_resources:['schema.json','artifact.json','generator.py','validate.py'].map(name=>[name,sha(readFileSync(path.resolve(genericRoot,'../../authority/artifact-types/definition/v2',name)))]),runtime:['runtime.mjs','cli.mjs','package.mjs','wire.mjs','native.mjs'].map(name=>[name,sha(readFileSync(path.join(root,name)))]),adapters:readdirSync(genericRoot).filter(name=>name.endsWith('.mjs')||name.endsWith('.py')).sort().map(name=>[name,sha(readFileSync(path.join(genericRoot,name)))]),preparation:['contracts.alch','semantics.alch','design.alch','sources.json','profile.json','contracts/bounds.json','contracts/transactions.json','native.mjs','journal.mjs','cli.mjs','validation.mjs','build.mjs'].map(name=>[name,sha(readFileSync(path.join(root,'../preparation',name)))]),builder:sha(readFileSync(import.meta.filename))}));
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
 const roleCache=path.join(base,'selected-roles');mkdirSync(roleCache,{recursive:true});
 function compileRole(selector,destination){
  const key=sha(application.source+selector+sha(readFileSync(path.join(genericRoot,'compile-source-operation.mjs')))),cache=path.join(roleCache,key),index=cache+'.json';
  if(existsSync(index)){
   const saved=JSON.parse(readFileSync(index)),raw=readFileSync(path.join(cache,'manifest.json'));if(sha(raw)!==saved.manifest_sha256)throw Error('role-cache-manifest-drift');for(const row of JSON.parse(raw).files){const member=readFileSync(path.join(cache,row.path));if(member.length!==row.bytes||sha(member)!==row.sha256)throw Error('role-cache-member-drift');}cpSync(cache,destination,{recursive:true,errorOnExist:true,force:false});
  }else{compiler.compile({modelRoot,selector,outputDirectory:destination});let claimed=false;try{mkdirSync(cache);claimed=true;}catch(error){if(error.code!=='EEXIST')throw error;}if(claimed){cpSync(destination,cache,{recursive:true,errorOnExist:false,force:true});writeFileSync(index,JSON.stringify({manifest_sha256:sha(readFileSync(path.join(cache,'manifest.json')))}),{flag:'wx'});}}
 }

 for(const selector of new Set([...plan.steps.map(step=>step.selector),'Define.Work.SemanticPreparationFacts','Define.Work.SelectedCandidateCount','Define.Work.ParameterApplicationCount'])){
  const relative='stages/'+String(Object.keys(selections).length).padStart(3,'0');
  compileRole(selector,path.join(output,relative));selections[selector]=relative;
 }
 if(sourceOf(buildApplication())!==digest)throw Error('source-changed-during-build');
 const rows=[];
 function inventory(dir,prefix=''){for(const item of readdirSync(dir,{withFileTypes:true})){const name=prefix+item.name;if(item.isDirectory())inventory(path.join(dir,item.name),name+'/');else if(item.isFile()){const raw=readFileSync(path.join(dir,item.name));rows.push({path:name,sha256:sha(raw),bytes:raw.length});}else throw Error('unexpected-projection-file');}}
 inventory(output);
 writeFileSync(path.join(output,'manifest.json'),JSON.stringify({schema_version:'generic-compiled-pipeline/v1',source:digest,application_source:application.source,selections,files:rows,authority_effect:'none'},null,2)+'\n',{flag:'wx'});
 const files=Object.fromEntries(rows.map(row=>[row.path,row.sha256]));files['manifest.json']=sha(readFileSync(path.join(output,'manifest.json')));
 const result={source:digest,application_source:application.source,output,files,toolchain:application.toolchain,session_engine:'current-authored-source',selected_plan:'Define.AuthorPlan'};
 try{writeFileSync(index,JSON.stringify(result,null,2)+'\n',{flag:'wx'});}catch(error){if(error.code!=='EEXIST')throw error;return build();}return result;
}