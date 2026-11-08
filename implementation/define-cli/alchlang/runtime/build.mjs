import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,realpathSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../../craft/implementation/source-bindings.mjs';
export const root=import.meta.dirname;
import {frozenSourceRoot} from './frozen-source.mjs';
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
export const sha=value=>createHash('sha256').update(value).digest('hex');
export const inputs=['define.alch','profile.json','contracts/bounds.json'];
export const fingerprint=()=>sha(JSON.stringify(inputs.map(name=>[name,sha(readFileSync(path.join(frozenSourceRoot(),name)))])));
export function build(){
 const alch=JSON.parse(readFileSync(path.join(craftRoot,'alchlang/package.json')));
 const core=JSON.parse(readFileSync(path.join(craftRoot,'cli/package.json')));
 if(alch.version!=='0.7.0-candidate.0'||core.version!=='1.3.0'||alch.name!=='@cyberalchemy/alchlang'||core.name!=='@domainspec-v2/cli')throw Error('imported-toolchain-identity-mismatch');
 const digest=fingerprint(),base=path.join(root,'.local');mkdirSync(base,{recursive:true});
 const index=path.join(base,digest+'.json');
 if(existsSync(index)){
  const saved=JSON.parse(readFileSync(index));
  for(const [name,hash]of Object.entries(saved.files))if(sha(readFileSync(path.join(saved.output,name)))!==hash)throw Error('generated-artifact-drift');
  if(saved.source!==digest)throw Error('generated-source-drift');
  return saved;
 }
 const run=mkdtempSync(path.join(base,'build-')),output=path.join(run,'generated');
 const child=spawnSync(node,[path.join(craftRoot,'alchlang/dist/generic-composition-cli.js'),'generate',
  '--source',path.join(frozenSourceRoot(),'define.alch'),'--profile',path.join(frozenSourceRoot(),'profile.json'),
  '--operation','Define.Execute','--out',output,'--accept-local-review','define-local-authoring'],
  {encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:path.join(craftRoot,'cli')}});
 writeFileSync(path.join(run,'stdout.log'),child.stdout??'');writeFileSync(path.join(run,'stderr.log'),child.stderr??'');
 if(child.status!==0)throw Error('Compilation failed; '+run+'\n'+(child.stderr||child.error));
 if(fingerprint()!==digest)throw Error('source-changed-during-build');
 const files={};
 function inventory(directory,prefix=''){
  for(const entry of readdirSync(directory,{withFileTypes:true})){
   const name=prefix+entry.name;if(entry.isDirectory())inventory(path.join(directory,entry.name),name+'/');
   else if(entry.isFile())files[name]=sha(readFileSync(path.join(directory,entry.name)));
   else throw Error('unexpected-generated-file-kind');
  }
 }
 // Inventory the full generated closure, including captured model and manifests.
 inventory(output);
 const result={source:digest,output,files,toolchain:{alchlang:alch.version,craft:core.version,node:'26.12.1'}};
 writeFileSync(index,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 return result;
}
