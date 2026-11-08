import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,realpathSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../craft/implementation/source-bindings.mjs';
export const root=import.meta.dirname;
import {capabilitySha} from './ports/native-fixture.mjs';
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
export const sha=value=>createHash('sha256').update(value).digest('hex');
export const selection=JSON.parse(readFileSync(path.join(root,'sources.json')));
export const inputs=['sources.json',selection.profile??'profile.json','contracts/bounds.json','contracts/transactions.json','contracts/workflow-profile.json','native-source.json','ports/native-fixture.py','ports/native-fixture.mjs','ports/creation.py',selection.primary,...selection.additional];
export const fingerprint=()=>sha(JSON.stringify(inputs.map(name=>[name,sha(readFileSync(path.join(root,name)))])));
export function build(){
 if(JSON.parse(readFileSync(path.join(root,'contracts/workflow-profile.json'))).stages[0].capability_sha256!==capabilitySha())throw Error('native-capability-source-drift');
 const native=JSON.parse(readFileSync(path.join(root,'native-source.json')));
 for(const [name,hash]of Object.entries(native.files))if(sha(readFileSync(path.resolve(root,'../../..',name)))!==hash)throw Error('native-source-drift: '+name);
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
  '--source',path.join(root,selection.primary),...selection.additional.flatMap(file=>['--additional-source',path.join(root,file)]),'--profile',path.join(root,selection.profile??'profile.json'),
  '--entry',selection.entry,'--out',output,'--accept-local-review','lab-runtime-model-review'],
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
