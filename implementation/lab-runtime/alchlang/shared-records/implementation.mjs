import {readFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {digest} from './verified-projection.mjs';
import {fingerprint} from './build.mjs';
export const repository=path.resolve(import.meta.dirname,'../../../..');
const bytes=value=>Buffer.from(JSON.stringify(value));
export function captureImplementation(root=repository){
 const shared='implementation/lab-runtime/alchlang/shared-records';
 const names=[];
 function collect(relative){
  for(const entry of readdirSync(path.join(root,relative),{withFileTypes:true})){
   if(entry.name.startsWith('.')||entry.name.startsWith('verify-'))continue;
   const name=relative+'/'+entry.name;
   if(entry.isDirectory())collect(name);
   else if(entry.isFile()&&/\.(mjs|py|alch|json)$/.test(entry.name)&&!/(VERIFICATION|QUALIFICATION|SOURCE-MANIFEST|IMPLEMENTATION-COVERAGE)/.test(entry.name))names.push(name);
  }
 }
 collect('implementation/lab-runtime/alchlang');
 collect('implementation/lab-workflows/definition-catalog');
 names.push('authority/definitions/maintenance-homes.json','workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs');
 names.push('implementation/lab-runtime/lab.mjs','implementation/artifact-runtime/compile-source-operation.mjs','implementation/artifact-runtime/pure-operation.mjs',
 'implementation/lab-runtime/alchlang/ports/creation.py','implementation/lab-runtime/alchlang/evaluate-creation.mjs',
 'implementation/lab-runtime/alchlang/creation-source.alch','implementation/lab-runtime/alchlang/native-source.json',
 'implementation/lab-workspaces/v2/workspaces.py','workspaces/products/craft/implementation/source-bindings.mjs');
 const native=JSON.parse(readFileSync(path.join(root,'implementation/lab-runtime/alchlang/native-source.json')));
 names.push(...Object.keys(native.files));
 const files=Object.fromEntries([...new Set(names)].sort().map(name=>[name,digest(readFileSync(path.join(root,name)))]));
 const manifest={schema_version:'lab-shared-execution-manifest/v1',model_source:fingerprint(),files};
 return {digest:digest(bytes(manifest)),manifest};
}
export function verifyImplementation(selected,root=repository){
 if(!selected?.manifest||selected.digest!==digest(bytes(selected.manifest)))throw Error('implementation-selection-required');
 for(const [name,sha] of Object.entries(selected.manifest.files)){
  const file=path.resolve(root,name);
  if(!file.startsWith(root+path.sep)||digest(readFileSync(file))!==sha)throw Error('implementation-source-drift:'+name);
 }
 const actualNames=Object.keys(captureImplementation(root).manifest.files);
 if(JSON.stringify(Object.keys(selected.manifest.files).sort())!==JSON.stringify(actualNames.sort()))throw Error('implementation-closure-incomplete');
 if(selected.manifest.model_source!==fingerprint())throw Error('implementation-model-drift');
 return selected.digest;
}
export function loadTrust(filename,root=repository){
 const trust=JSON.parse(readFileSync(filename));
 for(const group of ['schemas','selections','materials','executors']){
  for(const selected of Object.values(trust[group]??{})){
   if(selected.path)selected.path=path.resolve(root,selected.path);
  }
 }
 for(const entry of Object.values(trust.historical_artifacts??{}))if(entry.model_archive?.path)entry.model_archive.path=path.resolve(root,entry.model_archive.path);
 if(trust.initial_registry?.path)trust.initial_registry.path=path.resolve(root,trust.initial_registry.path);
 if(trust.consumer_universe?.path)trust.consumer_universe.path=path.resolve(root,trust.consumer_universe.path);
 if(trust.implementation?.path){
  const raw=readFileSync(path.resolve(root,trust.implementation.path));
  if(digest(raw)!==trust.implementation.sha256)throw Error('implementation-manifest-binding-mismatch');
  trust.implementation=JSON.parse(raw);
 }
 return trust;
}
