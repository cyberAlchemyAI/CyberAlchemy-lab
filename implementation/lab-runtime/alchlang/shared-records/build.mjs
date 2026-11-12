import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,renameSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../../workspaces/products/craft/implementation/source-bindings.mjs';
export {craftRoot};
export const root=import.meta.dirname;
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
export const sha=v=>createHash('sha256').update(v).digest('hex');
export const inputs=['sources.json','profile.json','contracts/bounds.json','contracts/transactions.json','build.mjs'];
const sourceRoot=root;
const sourceSelection=()=>JSON.parse(readFileSync(path.join(root,'sources.json')));
export const fingerprint=()=>sha(JSON.stringify([
 ...inputs.map(name=>[name,sha(readFileSync(path.join(root,name)))]),
 ...[sourceSelection().primary,...sourceSelection().additional].map(name=>[name,sha(readFileSync(path.join(sourceRoot,name)))])
]));
export function build(){
 if(JSON.parse(readFileSync(path.join(craftRoot,'alchlang/package.json'))).version!=='0.7.0-candidate.0'||JSON.parse(readFileSync(path.join(craftRoot,'cli/package.json'))).version!=='1.3.0')throw Error('pinned-toolchain-mismatch');
 const source=fingerprint();const saved=path.join(root,'.local/BUILD.json');
 if(existsSync(saved)){
  const b=JSON.parse(readFileSync(saved));
  if(b.source===source && b.files && Object.entries(b.files).every(([name,digest])=>sha(readFileSync(path.join(b.output,name)))===digest))return b;
 }const selection=JSON.parse(readFileSync(path.join(root,'sources.json'))),base=path.join(root,'.local');mkdirSync(base,{recursive:true});const directory=mkdtempSync(path.join(base,'build-')),output=path.join(directory,'generated');
 const p=spawnSync(node,[path.join(craftRoot,'alchlang/dist/generic-composition-cli.js'),'generate','--source',path.join(sourceRoot,selection.primary),...selection.additional.flatMap(s=>['--additional-source',path.join(sourceRoot,s)]),'--profile',path.join(root,selection.profile),'--entry',selection.entry,'--out',output,'--accept-local-review','shared-lab-runtime-technical-review'],{encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:path.join(craftRoot,'cli')}});
 writeFileSync(path.join(directory,'stdout.log'),p.stdout??'');writeFileSync(path.join(directory,'stderr.log'),p.stderr??'');if(p.status!==0)throw Error('Design compilation failed '+directory+'\n'+p.stderr);if(fingerprint()!==source)throw Error('design-source-changed-during-build');
 const files={};
 function inventory(home,prefix=''){
  for(const item of readdirSync(home,{withFileTypes:true})){
   const name=prefix+item.name;
   if(item.isDirectory())inventory(path.join(home,item.name),name+'/');
   else if(item.isFile())files[name]=sha(readFileSync(path.join(home,item.name)));
   else throw Error('generated-file-kind-invalid');
  }
 }
 inventory(output);
 const result={source,output,directory,files,manifest_sha256:sha(readFileSync(path.join(output,'manifest.json'))),toolchain:{craft:JSON.parse(readFileSync(path.join(craftRoot,'cli/package.json'))).version,alchlang:JSON.parse(readFileSync(path.join(craftRoot,'alchlang/package.json'))).version}};writeFileSync(path.join(base,'BUILD.json'),JSON.stringify(result,null,2)+'\n');return result;
}
if(process.argv[1]===import.meta.filename)console.log(JSON.stringify(build()));

export function buildHistorical(archive){
 const raw=readFileSync(archive.path);
 if(sha(raw)!==archive.sha256)throw Error('historical-model-archive-drift');
 const saved=JSON.parse(raw),selection=JSON.parse(Buffer.from(saved.files['sources.json'],'base64'));
 const named=[...inputs,selection.primary,...selection.additional];
 const source=sha(JSON.stringify(named.map(name=>[name,sha(Buffer.from(saved.files[name],'base64'))])));
 if(source!==saved.source)throw Error('historical-model-source-mismatch');
 const directory=path.join(root,'.local','historical-models',source),output=path.join(directory,'generated');
 const receipt=path.join(directory,'BUILD.json');
 if(existsSync(receipt)){
  const result=JSON.parse(readFileSync(receipt));
  if(result.source===source&&Object.entries(result.files).every(([name,hash])=>sha(readFileSync(path.join(output,name)))===hash))return result;
 }
 const authored=path.join(directory,'authored');mkdirSync(authored,{recursive:true});
 for(const [name,base64] of Object.entries(saved.files)){
  const file=path.resolve(authored,name);
  if(!file.startsWith(authored+path.sep))throw Error('historical-source-path-invalid');
  mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,Buffer.from(base64,'base64'));
 }
 const run=spawnSync(node,[path.join(craftRoot,'alchlang/dist/generic-composition-cli.js'),'generate','--source',path.join(authored,selection.primary),
 ...selection.additional.flatMap(name=>['--additional-source',path.join(authored,name)]),'--profile',path.join(authored,selection.profile),
 '--entry',selection.entry,'--out',output,'--accept-local-review','qualified-original-shared-model'],{
 encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:path.join(craftRoot,'cli')}});
 if(run.status!==0)throw Error('historical-generation-failed:'+run.stderr);
 const files={};function inventory(home,prefix=''){for(const item of readdirSync(home,{withFileTypes:true})){
  const name=prefix+item.name;if(item.isDirectory())inventory(path.join(home,item.name),name+'/');else files[name]=sha(readFileSync(path.join(home,item.name)));
 }}inventory(output);
 const result={source,output,files};writeFileSync(receipt,JSON.stringify(result));return result;
}
