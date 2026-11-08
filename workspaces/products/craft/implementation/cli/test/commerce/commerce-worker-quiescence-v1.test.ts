import assert from 'node:assert/strict';
import {spawn,type ChildProcessWithoutNullStreams} from 'node:child_process';
import {mkdtempSync,chmodSync,copyFileSync,rmSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import test from 'node:test';
import {acquireCommerceWorkerQuiescenceV1,CommerceWorkerQuiescenceErrorV1} from '../../src/commerce/commerce-worker-quiescence-v1.js';

const digest='a'.repeat(64);
const ownFile=fileURLToPath(import.meta.url);
function target(storePath:string){return {storePath,storeId:'store-test-1',schemaSha256:digest};}
function fixture(){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-worker-quiescence-'));
 chmodSync(directory,0o700);
 const storePath=path.join(directory,'service.sqlite');
 const db=new DatabaseSync(storePath);db.exec('CREATE TABLE sample (id INTEGER PRIMARY KEY)');db.close();chmodSync(storePath,0o600);
 return {directory,storePath,close:()=>rmSync(directory,{recursive:true,force:true})};
}
function code(expected:CommerceWorkerQuiescenceErrorV1['code']){
 return (error:unknown)=>error instanceof CommerceWorkerQuiescenceErrorV1&&error.code===expected;
}
async function childReady(child:ChildProcessWithoutNullStreams):Promise<void>{
 await new Promise<void>((resolve,reject)=>{
  let output='';
  const timer=setTimeout(()=>reject(new Error('child did not acquire custody')),5000);
  const onData=(chunk:Buffer)=>{output+=chunk.toString();if(output.includes('READY\n')){clearTimeout(timer);child.stdout.off('data',onData);resolve();}};
  child.stdout.on('data',onData);
  child.once('exit',(exitCode,signal)=>{clearTimeout(timer);reject(new Error(`child exited before READY: ${exitCode} ${signal} ${output}`));});
 });
}
async function childExit(child:ChildProcessWithoutNullStreams):Promise<void>{
 if(child.exitCode!==null||child.signalCode!==null)return;
 await new Promise<void>((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('child did not exit')),5000);child.once('exit',()=>{clearTimeout(timer);resolve();});});
}

if(process.argv[2]==='--hold-custody'){
 const storePath=process.argv[3];
 if(!storePath)throw new Error('missing store path');
 acquireCommerceWorkerQuiescenceV1(target(storePath),'reopen');
 process.stdout.write('READY\n');
 setInterval(()=>{},1000);
}else{
 test('whole-process custody refuses a concurrent claimant and releases after abrupt termination',async()=>{
  const f=fixture();let child:ChildProcessWithoutNullStreams|undefined;
  try{
   const initial=acquireCommerceWorkerQuiescenceV1(target(f.storePath),'create');initial.close();
   child=spawn(process.execPath,['--import','tsx',ownFile,'--hold-custody',f.storePath],{stdio:['pipe','pipe','pipe']});
   await childReady(child);
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1(target(f.storePath),'reopen'),code('PredecessorActive'));
   child.kill('SIGKILL');await childExit(child);
   const successor=acquireCommerceWorkerQuiescenceV1(target(f.storePath),'reopen');
   assert.equal(successor.inspect().authority_effect,'none');
   successor.close();
  }finally{if(child&&child.exitCode===null&&child.signalCode===null){child.kill('SIGKILL');await childExit(child);}f.close();}
 });
 test('reopen rejects missing, changed, and physically replaced lock identity',()=>{
  const f=fixture();
  try{
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1(target(f.storePath),'reopen'),code('LockIdentityMissing'));
   const owner=acquireCommerceWorkerQuiescenceV1(target(f.storePath),'create');
   const lockPath=owner.inspect().lockPath;
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1({...target(f.storePath),storeId:'different'},'reopen'),code('PredecessorActive'));
   renameSync(lockPath,lockPath+'.moved');
   assert.throws(()=>owner.assertCurrent(),code('LockIdentityMissing'));
   owner.close();
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1(target(f.storePath),'reopen'),code('LockIdentityMissing'));
   renameSync(lockPath+'.moved',lockPath);
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1({...target(f.storePath),storeId:'different'},'reopen'),code('LockIdentityChanged'));
   copyFileSync(lockPath,lockPath+'.copy');
   renameSync(lockPath+'.copy',lockPath);
   assert.throws(()=>acquireCommerceWorkerQuiescenceV1(target(f.storePath),'reopen'),code('LockIdentityChanged'));
  }finally{f.close();}
 });
}
