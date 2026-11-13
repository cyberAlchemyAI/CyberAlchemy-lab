import {readFileSync,writeFileSync,mkdtempSync,rmSync,readdirSync} from 'node:fs';
import {spawn,spawnSync} from 'node:child_process';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {isDeepStrictEqual} from 'node:util';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {inspectPackage,materializeCli} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
import {verifyLocations} from '../../lab-runtime/alchlang/shared-records/locations.mjs';
import {enforce} from './kernel.mjs';
const assetNames={body:'definition.json',projection:'DEFINITION.md',lineage:'field-lineage.json',evidence:'evidence.json'};
export async function verifyDirectoryPackages(source,registry,read,{singleProcess=false}={}){
 const current=registry.entries.filter(e=>registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version);
 if(!singleProcess)await verifyLocations(source,registry,read,{requiredProtocol:'workspace-definition-layout/v2'});
 if(!singleProcess && current.length>4){
  const temp=mkdtempSync(path.join(tmpdir(),'lab-directory-workers-')),files={};
  try{
   for(const entry of current){
    const d=source.locations[entry.definition_id+'@'+entry.version].directory;
    for(const key of ['body','projection','lineage','evidence','verification']){const b=d[key];files[b.ref??b.path]=read(b).toString('base64');}
    const verification=JSON.parse(read(d.verification)),archive=verification.package_archive;
    files[archive.ref??archive.path]=read(archive).toString('base64');
   }
   const input=path.join(temp,'input.json');writeFileSync(input,JSON.stringify({source,registry,files}));
   const children=[];let failure=null;const fail=error=>{failure??=error;for(const child of children)child.kill('SIGTERM');};
   const settled=await Promise.allSettled(Array.from({length:4},(_,index)=>new Promise((resolve,reject)=>{
    const p=spawn(process.execPath,[path.join(import.meta.dirname,'directory-worker.mjs'),input,String(index),'4'],{stdio:['ignore','pipe','pipe']});
    children.push(p);let out='',err='';p.stdout.on('data',x=>{out+=x;if(out.length>8*1024*1024)p.kill();});p.stderr.on('data',x=>{err=(err+x).slice(-8192);});
    p.on('error',error=>{fail(error);reject(error);});p.on('close',code=>{if(code!==0){const error=Error('directory-worker-refused:'+err);fail(error);reject(error);}else{try{resolve(JSON.parse(out));}catch(e){fail(e);reject(e);}}});
   })));
   if(failure)throw failure;const results=settled.map(r=>{if(r.status!=='fulfilled')throw r.reason;return r.value;});
   const directories=results.flatMap(r=>r.directories).sort((a,b)=>a.version.localeCompare(b.version));
   if(JSON.stringify(directories.map(d=>d.version).sort())!==JSON.stringify(current.map(e=>e.definition_id+'@'+e.version).sort()))throw Error('directory-worker-coverage-mismatch');
   await enforceCompleteDirectory();return {status:'PASS',verification_scope:'complete-directory-and-workspace-layout',directories};
  }finally{rmSync(temp,{recursive:true,force:true});}
 }

 if(source.layout_protocol!=='workspace-definition-layout/v2')throw Error('directory-layout-v2-required');
 const temporary=mkdtempSync(path.join(tmpdir(),'lab-directory-verification-')),archives=new Map(),results=[];
 const original=b=>{const raw=read(b);if(digest(raw)!==b.sha256||raw.length!==Number(b.bytes))throw Error('directory-material-binding-mismatch');return raw;};
 try{
  for(const entry of registry.entries.filter(e=>registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version)){
   const key=entry.definition_id+'@'+entry.version,location=source.locations?.[key],directory=location?.directory;
   if(!directory)throw Error('definition-directory-required');
   const receipt=JSON.parse(original(directory.verification)),archive=receipt.package_archive;
   let extracted=archives.get(archive.sha256);
   if(!extracted){
    extracted=path.join(temporary,'archive-'+archives.size);
    const p=spawnSync('python3',['-B',path.join(import.meta.dirname,'archive.py')],{input:JSON.stringify({archive:original(archive).toString('base64'),output:extracted}),encoding:'utf8',maxBuffer:1024*1024});
    if(p.status!==0)throw Error('directory-archive-invalid:'+p.stderr);
    archives.set(archive.sha256,extracted);
   }
   if(!/^[A-Za-z0-9._:-]+\/pack$/.test(receipt.package_prefix))throw Error('directory-package-prefix-invalid');
   const pack=path.join(extracted,receipt.package_prefix),inspection=await inspectPackage(pack);
   const output=path.join(temporary,'materialized-'+results.length);
   await materializeCli(pack,output);
   const dirs=readdirSync(path.join(output,'definitions'));
   if(dirs.length!==1)throw Error('directory-package-single-definition-required');
   const produced=path.join(output,'definitions',dirs[0]);
   for(const [role,name]of Object.entries(assetNames)){
    const actual=original(directory[role]);
    if(role!=='evidence'&&!readFileSync(path.join(produced,name)).equals(actual))throw Error('directory-materialization-mismatch:'+role);
   }
   if(receipt.definition_id!==entry.definition_id||receipt.version!==entry.version||!isDeepStrictEqual(receipt.assets,Object.fromEntries(Object.keys(assetNames).map(k=>[k,directory[k]]))))throw Error('directory-receipt-substitution');

   results.push({version:key,package_manifest_sha256:digest(readFileSync(path.join(pack,'manifest.json'))),inspection});
  }
  if(!singleProcess)await enforceCompleteDirectory();
  return {status:'PASS',verification_scope:singleProcess?'package-assets-only':'complete-directory-and-workspace-layout',directories:results};
 }finally{rmSync(temporary,{recursive:true,force:true});}
}

async function enforceCompleteDirectory(){
 // Called only after global location checks and exact all-worker coverage/materialization.
 return enforce('EnforceDirectory',{policy_requires_layout:true,protocol_supported:true,current_coverage_exact:true,home_assignments_verified:true,body_bound:true,projection_bound:true,lineage_bound:true,evidence_bound:true,package_verified:true});
}
