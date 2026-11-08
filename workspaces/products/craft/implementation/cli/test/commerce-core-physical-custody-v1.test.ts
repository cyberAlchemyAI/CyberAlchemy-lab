/** Physical capture must reject replacement of a shared parent or a restored file. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,renameSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {pinCoreImplementation,pinCorePhysicalCaptures,readCorePhysicalFile,withCorePhysicalIdentityPhase} from '../src/commerce/commerce-core-physical.js';

const stale=(error:any)=>error?.code==='StaleOwner'||error?.diagnostics?.[0]?.code==='StaleOwner';

test('two captured files retain their shared physical parent and individual file identities',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-physical-custody-'));
 try{
  const directory=path.join(root,'source');mkdirSync(directory);
  const first=path.join(directory,'first.alch'),second=path.join(directory,'second.alch');
  writeFileSync(first,'first\n');writeFileSync(second,'second\n');
  const captured=pinCorePhysicalCaptures([readCorePhysicalFile(first),readCorePhysicalFile(second)]);
  captured.assertCurrent();
  const original=readFileSync(first);
  writeFileSync(first,'changed\n');writeFileSync(first,original);
  assert.throws(()=>captured.assertCurrent(),stale,'restoring bytes cannot restore the original file identity');

  const fresh=pinCorePhysicalCaptures([readCorePhysicalFile(first),readCorePhysicalFile(second)]);
  fresh.assertCurrent();
  renameSync(directory,path.join(root,'removed-source'));
  mkdirSync(directory);
  writeFileSync(first,original);writeFileSync(second,'second\n');
  assert.throws(()=>fresh.assertCurrent(),stale,'a replacement directory cannot inherit the captured parent identity');
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('implementation pin rejects a replaced module in the same captured directory',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-implementation-custody-'));
 try{
  const module=path.join(root,'owner.mjs'),dependency=path.join(root,'dependency.mjs');
  writeFileSync(module,'export const owner = true;\n');
  writeFileSync(dependency,'export const dependency = true;\n');
  const pinned=pinCoreImplementation(pathToFileURL(module).href,['./dependency.mjs']);
  pinned.assertCurrent();
  renameSync(dependency,path.join(root,'retired-dependency.mjs'));
  writeFileSync(dependency,'export const dependency = true;\n');
  assert.throws(()=>pinned.assertCurrent(),stale,'same bytes at a new inode must not become trusted implementation');
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('synchronous source validation resamples nested pins at return and never caches a later call',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-physical-phase-'));
 try{
  const file=path.join(root,'source.alch');writeFileSync(file,'original\n');
  const first=pinCorePhysicalCaptures([readCorePhysicalFile(file)]),second=pinCorePhysicalCaptures([readCorePhysicalFile(file)]);
  withCorePhysicalIdentityPhase(()=>{first.assertCurrent();withCorePhysicalIdentityPhase(()=>second.assertCurrent());});
  assert.throws(()=>withCorePhysicalIdentityPhase(()=>{first.assertCurrent();second.assertCurrent();writeFileSync(file,'changed\n');first.assertCurrent();}),stale,'a change after the first sample fails before the source validation returns');
  assert.throws(()=>withCorePhysicalIdentityPhase(()=>first.assertCurrent()),stale,'no successful sample survives into the next validation call');
  assert.throws(()=>withCorePhysicalIdentityPhase(()=>Promise.resolve()),error=>(error as any)?.diagnostics?.[0]?.code==='InvalidContract','source validation cannot span an await');
 }finally{rmSync(root,{recursive:true,force:true});}
});
