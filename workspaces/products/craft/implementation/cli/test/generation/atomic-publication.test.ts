import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {publishAtomicDirectory} from '../../src/generation/atomic-publication.ts';
import {loadAtomicPublicationNative} from '../../src/generation/atomic-publication-native.ts';

const artifacts=[{relative_path:'src/domain.ts',content:'export const value=7;\n'},{relative_path:'.domainspec/receipt.json',content:'{"complete":true}\n'}];
function fixture(run:(root:string,target:string)=>void){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-atomic-test-'));
 try{fs.writeFileSync(path.join(root,'sentinel'),'safe');loadAtomicPublicationNative();run(root,path.join(root,'target'));assert.equal(fs.readFileSync(path.join(root,'sentinel'),'utf8'),'safe');}
 finally{fs.rmSync(root,{recursive:true,force:true});}
}
const publish=(target:string)=>publishAtomicDirectory(target,artifacts,'.domainspec-test-');
test('atomic helper publishes exact nested artifacts and receipt without stage residue',()=>fixture((root,target)=>{
 publish(target);for(const file of artifacts)assert.equal(fs.readFileSync(path.join(target,file.relative_path),'utf8'),file.content);
 assert.deepEqual(fs.readdirSync(root).sort(),['sentinel','target']);
}));
test('atomic helper removes owned partial files after interruption',()=>fixture((root,target)=>{
 const write=fs.writeFileSync;let injected=false;
 fs.writeFileSync=((file:any,...args:any[])=>{if(typeof file==='number'){injected=true;throw Error('interrupted');}return (write as any)(file,...args);}) as any;
 try{assert.throws(()=>publish(target),/interrupted/);}finally{fs.writeFileSync=write;}
 assert.equal(injected,true);assert.deepEqual(fs.readdirSync(root),['sentinel']);
}));
test('directory-open failure cleans only the newly created empty directory',()=>fixture((root,target)=>{
 for(const child of [false,true]){
  const open=fs.openSync;let injected=false;
  fs.openSync=((file:any,...args:any[])=>{
   const name=path.basename(String(file));
   if(String(file).startsWith('/proc/self/fd/')&&(child?name==='src':name.startsWith('.domainspec-test-'))){injected=true;throw Error('directory open interrupted');}
   return (open as any)(file,...args);
  }) as any;
  try{assert.throws(()=>publish(target),/directory open interrupted/);}finally{fs.openSync=open;}
  assert.ok(injected);assert.deepEqual(fs.readdirSync(root),['sentinel']);
 }
}));
test('atomic helper preserves a competing empty directory after its last stage identity check',()=>fixture((root,target)=>{
 const lstat=fs.lstatSync;let stageChecks=0,inode:bigint|undefined;
 // This fixture's stage is checked seven times; inject after the final observed identity.
 fs.lstatSync=((file:any,...args:any[])=>{
  const result=(lstat as any)(file,...args);
  if(String(file).includes('/.domainspec-test-')&&++stageChecks===7){fs.mkdirSync(target);inode=lstat(target,{bigint:true}).ino;}
  return result;
 }) as any;
 try{assert.throws(()=>publish(target),{code:'DS_ATOMIC_EXISTS'});}finally{fs.lstatSync=lstat;}
 assert.ok(inode);assert.equal(fs.lstatSync(target,{bigint:true}).ino,inode);assert.deepEqual(fs.readdirSync(target),[]);
 assert.deepEqual(fs.readdirSync(root).sort(),['sentinel','target']);
}));
test('atomic helper does not follow or clean a substituted stage path',()=>fixture((root,target)=>{
 const write=fs.writeFileSync;let injected=false;
 fs.writeFileSync=((file:any,...args:any[])=>{
  const result=(write as any)(file,...args);
  if(typeof file==='number'&&!injected){injected=true;const stage=path.join(root,fs.readdirSync(root).find(n=>n.startsWith('.domainspec-test-'))!);
   fs.renameSync(stage,stage+'-owned');fs.mkdirSync(stage);write(path.join(stage,'foreign'),'preserve');}
  return result;
 }) as any;
 try{assert.throws(()=>publish(target),{code:'DS_ATOMIC_IDENTITY'});}finally{fs.writeFileSync=write;}
 assert.ok(injected);assert.equal(fs.existsSync(target),false);
 const foreign=fs.readdirSync(root).find(n=>n.startsWith('.domainspec-test-')&&!n.endsWith('-owned'))!;
 assert.equal(fs.readFileSync(path.join(root,foreign,'foreign'),'utf8'),'preserve');
}));
test('atomic helper detects foreign staged inventory and retains foreign files',()=>fixture((root,target)=>{
 const write=fs.writeFileSync;let injected=false;
 fs.writeFileSync=((file:any,...args:any[])=>{
  const result=(write as any)(file,...args);
  if(typeof file==='number'&&!injected){injected=true;const stage=fs.readdirSync(root).find(n=>n.startsWith('.domainspec-test-'))!;write(path.join(root,stage,'foreign'),'preserve');}
  return result;
 }) as any;
 try{assert.throws(()=>publish(target),{code:'DS_ATOMIC_IDENTITY'});}finally{fs.writeFileSync=write;}
 const stage=fs.readdirSync(root).find(n=>n.startsWith('.domainspec-test-'))!;
 assert.deepEqual(fs.readdirSync(path.join(root,stage)),['foreign']);assert.equal(fs.existsSync(target),false);
}));
test('atomic helper rejects renamed parent without redirecting writes or returning stale success',()=>fixture((root,target)=>{
 const parent=path.join(root,'parent'),moved=path.join(root,'moved'),outside=path.join(root,'outside');fs.mkdirSync(parent);fs.mkdirSync(outside);
 const write=fs.writeFileSync;let injected=false;
 fs.writeFileSync=((file:any,...args:any[])=>{const result=(write as any)(file,...args);if(typeof file==='number'&&!injected){injected=true;fs.renameSync(parent,moved);fs.symlinkSync(outside,parent);}return result;}) as any;
 try{assert.throws(()=>publish(path.join(parent,'target')),{code:'DS_ATOMIC_IDENTITY'});}finally{fs.writeFileSync=write;}
 assert.ok(injected);assert.deepEqual(fs.readdirSync(outside),[]);assert.deepEqual(fs.readdirSync(moved),[]);
}));
