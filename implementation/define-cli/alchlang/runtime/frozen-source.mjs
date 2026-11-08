// Immutable source input for existing journal replay, extracted only into ignored cache.
import {readFileSync,existsSync,mkdirSync,mkdtempSync,renameSync,lstatSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
const root=import.meta.dirname;
const snapshot=JSON.parse(readFileSync(path.join(root,'frozen-source.json')));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export const frozenInputs=['define.alch','profile.json','contracts/bounds.json'];
export function frozenSourceRoot(){
 const archive=path.resolve(root,snapshot.archive);
 if(sha(readFileSync(archive))!==snapshot.archive_sha256)throw Error('frozen-source-archive-drift');
 const base=path.join(root,'.local');mkdirSync(base,{recursive:true});
 const destination=path.join(base,'replay-source-'+snapshot.archive_sha256);
 function checked(directory){
  const source=path.join(directory,'v2');
  for(const name of frozenInputs){
   const file=path.join(source,name),stat=lstatSync(file);
   if(!stat.isFile()||stat.isSymbolicLink()||sha(readFileSync(file))!==snapshot.files[name].sha256)throw Error('frozen-replay-source-drift');
  }
  const digest=sha(JSON.stringify(frozenInputs.map(name=>[name,sha(readFileSync(path.join(source,name)))])));
  if(digest!==snapshot.model_sha256)throw Error('frozen-journal-model-mismatch');
  return source;
 }
 if(!existsSync(destination)){
  const temporary=mkdtempSync(path.join(base,'replay-source-'));
  const extracted=spawnSync('tar',['--extract','--gzip','--file',archive,'--directory',temporary,'--no-same-owner','--no-same-permissions',...frozenInputs.map(name=>snapshot.files[name].member)],{encoding:'utf8'});
  if(extracted.status!==0)throw Error('frozen-source-extraction-failed: '+(extracted.stderr||extracted.error));
  checked(temporary);
  try{renameSync(temporary,destination);}catch(error){if(!existsSync(destination))throw error;}
 }
 return checked(destination);
}
