/** Batch ancestry checks must reject changes, including at the end of a batch.
 * Open Questions: docs/COMMERCE-OWNERS.md.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs,{mkdtempSync,mkdirSync,writeFileSync,renameSync,rmSync} from 'node:fs';
import {syncBuiltinESMExports} from 'node:module';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pinCorePhysicalCaptures,readCorePhysicalFile} from '../../src/commerce/commerce-core-physical.ts';
const stale=error=>error?.diagnostics?.[0]?.code==='StaleOwner';
test('physical batch retains every branch file and never reuses a parent observation in a later check',()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-physical-batch-'));
 try{
  const files=[];
  for(let n=0;n<8;n++){const dir=path.join(work,'shared','branch-'+n);mkdirSync(dir,{recursive:true});const file=path.join(dir,'model.json');writeFileSync(file,'{"value":'+n+'}\n');files.push(file);}
  const pin=pinCorePhysicalCaptures(files.map(file=>readCorePhysicalFile(file)));
  pin.assertCurrent();pin.assertCurrent();
  writeFileSync(files[7],'{"value":8}\n');
  assert.throws(()=>pin.assertCurrent(),stale);
 }finally{assert.ok(path.basename(work).startsWith('craft-physical-batch-'));rmSync(work,{recursive:true,force:true});}
});
test('physical batch rechecks a shared ancestor after the final file even when leaf directories and file inodes survive',()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-physical-batch-')),shared=path.join(work,'shared');
 const original=fs.lstatSync;let moved=false;
 try{
  const files=['first','last'].map(name=>{const dir=path.join(shared,name);mkdirSync(dir,{recursive:true});const file=path.join(dir,name+'.json');writeFileSync(file,'{"value":1}\n');return file;});
  const pin=pinCorePhysicalCaptures(files.map(file=>readCorePhysicalFile(file)));pin.assertCurrent();
  fs.lstatSync=function(...args){
   const result=Reflect.apply(original,this,args);
   if(!moved&&String(args[0]).startsWith('/proc/self/fd/')&&String(args[0]).endsWith('/last.json')){
    moved=true;
    const retired=path.join(work,'retired');renameSync(shared,retired);mkdirSync(shared);
    for(const name of ['first','last'])renameSync(path.join(retired,name),path.join(shared,name));
   }
   return result;
  };
  syncBuiltinESMExports();
  assert.throws(()=>pin.assertCurrent(),stale);
  assert.equal(moved,true,'negative must change the path after its final file observation');
 }finally{
  fs.lstatSync=original;syncBuiltinESMExports();
  assert.ok(path.basename(work).startsWith('craft-physical-batch-'));rmSync(work,{recursive:true,force:true});
 }
});
