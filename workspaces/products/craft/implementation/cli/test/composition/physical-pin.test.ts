import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,statSync,utimesSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {pinCoreImplementation,pinCorePhysicalCaptures,readCorePhysicalFile} from '../../src/commerce/commerce-core-physical.js';

test('physical captures reject same-size in-place edits even when mtime is restored',()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'craft-physical-pin-'));
 try{
  const file=path.join(directory,'model.json');writeFileSync(file,'{"a":1}\n');
  const captured=readCorePhysicalFile(file),pin=pinCorePhysicalCaptures([captured]);pin.assertCurrent();
  const before=statSync(file);writeFileSync(file,'{"a":2}\n');utimesSync(file,before.atime,before.mtime);
  assert.equal(readFileSync(file,'utf8').length,captured.file.bytes);
  assert.throws(()=>pin.assertCurrent(),(error:any)=>error?.diagnostics?.[0]?.code==='StaleOwner');
 }finally{rmSync(directory,{recursive:true,force:true});}
});

test('implementation pin rejects a same-size edit with restored mtime',()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'craft-code-pin-'));
 try{
  const file=path.join(directory,'module.mjs');writeFileSync(file,'export const x=1;\n');
  const pin=pinCoreImplementation(pathToFileURL(file).href,[]);pin.assertCurrent();
  const before=statSync(file);writeFileSync(file,'export const x=2;\n');utimesSync(file,before.atime,before.mtime);
  assert.throws(()=>pin.assertCurrent(),(error:any)=>error?.diagnostics?.[0]?.code==='StaleOwner');
 }finally{rmSync(directory,{recursive:true,force:true});}
});
