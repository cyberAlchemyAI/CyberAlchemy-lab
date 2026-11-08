import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {stripTypeScriptTypes} from 'node:module';
import {test} from 'node:test';
import {ATOMIC_NATIVE} from '../../src/generation/atomic-publication-native.generated.ts';

const sources=path.resolve(import.meta.dirname,'../../src/generation');
function fixture(run:(root:string)=>void,mutate?:(text:string)=>string){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-native-adapter-test-'));
 try{
  fs.mkdirSync(path.join(root,'scratch'));
  fs.writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
  for(const name of ['atomic-publication-native','atomic-publication-native.generated']){
   const text=fs.readFileSync(path.join(sources,name+'.ts'),'utf8');
   fs.writeFileSync(path.join(root,name+'.js'),stripTypeScriptTypes(mutate?mutate(text):text));
  }
  run(root);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
}
function child(root:string,program:string,flags:string[]=[]):string {
 return execFileSync(process.execPath,[...flags,'--input-type=module','-e',program],{
  cwd:root,encoding:'utf8',timeout:10000,env:{PATH:'/absent',TMPDIR:path.join(root,'scratch'),NODE_NO_WARNINGS:'1'},stdio:['ignore','pipe','pipe'],
 });
}
const prelude="import assert from 'node:assert/strict';import fs from 'node:fs';import {loadAtomicPublicationNative as load} from './atomic-publication-native.js';";
test('relocated emitted adapter loads without compiler or source and removes extraction',()=>fixture(root=>{
 child(root,prelude+`
 const native=load();assert.equal(load(),native);assert.equal(Object.isFrozen(native),true);
 fs.mkdirSync('stage');fs.writeFileSync('stage/receipt','complete');
 const fd=fs.openSync('.',fs.constants.O_RDONLY|fs.constants.O_DIRECTORY);
 try{native.renameNoReplace(fd,'stage','target');}finally{fs.closeSync(fd);}
 assert.equal(fs.readFileSync('target/receipt','utf8'),'complete');
 assert.deepEqual(fs.readdirSync(process.env.TMPDIR),[]);`);
}));
test('import is read-only and permission-restricted loads fail before writes, even with addons allowed',()=>fixture(root=>{
 child(root,`import fs from 'node:fs';fs.mkdtempSync=()=>{throw Error('unexpected extraction');};await import('./atomic-publication-native.js');`);
 for(const flags of [[],['--allow-addons']])child(root,prelude+`assert.throws(load,{code:'DS_NATIVE_PERMISSION'});`,['--permission','--allow-fs-read='+root,...flags]);
 assert.deepEqual(fs.readdirSync(path.join(root,'scratch')),[]);
}));
test('embedded payload tampering rejects before extraction',()=>fixture(root=>{
 child(root,prelude+`assert.throws(load,{code:'DS_NATIVE_INTEGRITY'});assert.deepEqual(fs.readdirSync(process.env.TMPDIR),[]);`);
},text=>text.replace(ATOMIC_NATIVE.base64,'A'+ATOMIC_NATIVE.base64.slice(1))));
test('native loading uses the unlinked held inode despite replacement of its old pathname',()=>fixture(root=>{
 child(root,prelude+`
 const unlink=fs.unlinkSync;let injected;
 fs.unlinkSync=function(file){unlink(file);if(String(file).endsWith('/primitive.node')){fs.writeFileSync(file,'foreign');injected=String(file);}};
 const native=load();assert.equal(typeof native.renameNoReplace,'function');
 const directories=fs.readdirSync(process.env.TMPDIR);assert.equal(directories.length,1);
 assert.equal(fs.readFileSync(process.env.TMPDIR+'/'+directories[0]+'/primitive.node','utf8'),'foreign');
 assert.ok(injected);`);
}));
test('extraction file replacement rejects and cleanup preserves the foreign inode',()=>fixture(root=>{
 child(root,prelude+`
 const write=fs.writeFileSync;let injected=false;
 fs.writeFileSync=function(fd,...args){const result=write(fd,...args);if(typeof fd==='number'&&!injected){
  injected=true;const dir=fs.readdirSync(process.env.TMPDIR)[0],file=process.env.TMPDIR+'/'+dir+'/primitive.node';
  fs.unlinkSync(file);write(file,'foreign');}return result;};
 assert.throws(load,{code:'DS_NATIVE_IDENTITY'});
 const dirs=fs.readdirSync(process.env.TMPDIR);assert.equal(dirs.length,1);
 assert.equal(fs.readFileSync(process.env.TMPDIR+'/'+dirs[0]+'/primitive.node','utf8'),'foreign');`);
}));
test('dlopen failure cleans owned extraction and permits a later retry',()=>fixture(root=>{
 child(root,prelude+`
 const open=process.dlopen;process.dlopen=()=>{throw Error('injected load failure');};
 assert.throws(load,/injected load failure/);assert.deepEqual(fs.readdirSync(process.env.TMPDIR),[]);
 process.dlopen=open;assert.equal(typeof load().renameNoReplace,'function');
 assert.deepEqual(fs.readdirSync(process.env.TMPDIR),[]);`);
}));
test('renamed extraction directory cannot redirect loading or delete its replacement',()=>fixture(root=>{
 child(root,prelude+`
 const write=fs.writeFileSync;let injected=false,moved;
 fs.writeFileSync=function(fd,...args){const result=write(fd,...args);if(typeof fd==='number'&&!injected){
  injected=true;const dir=process.env.TMPDIR+'/'+fs.readdirSync(process.env.TMPDIR)[0];moved=dir+'-moved';
  fs.renameSync(dir,moved);fs.mkdirSync(dir);write(dir+'/sentinel','foreign');}return result;};
 assert.equal(typeof load().renameNoReplace,'function');
 const dirs=fs.readdirSync(process.env.TMPDIR);assert.equal(dirs.length,2);
 assert.deepEqual(fs.readdirSync(moved),[]);
 const original=dirs.find(d=>!d.endsWith('-moved'));assert.equal(fs.readFileSync(process.env.TMPDIR+'/'+original+'/sentinel','utf8'),'foreign');`);
}));
for(const kind of ['empty-directory','nonempty-directory','file','dangling-link','directory-link'])
 test('emitted adapter preserves preexisting '+kind,()=>fixture(root=>{
  child(root,prelude+`
  const native=load();fs.mkdirSync('stage');fs.writeFileSync('stage/receipt','candidate');fs.mkdirSync('outside');fs.writeFileSync('outside/sentinel','safe');
  const kind=${JSON.stringify(kind)};
  if(kind==='empty-directory'||kind==='nonempty-directory')fs.mkdirSync('target');
  if(kind==='nonempty-directory')fs.writeFileSync('target/sentinel','foreign');
  if(kind==='file')fs.writeFileSync('target','foreign');
  if(kind==='dangling-link')fs.symlinkSync('missing','target');
  if(kind==='directory-link')fs.symlinkSync('outside','target');
  const before=fs.lstatSync('target',{bigint:true}),fd=fs.openSync('.',fs.constants.O_RDONLY|fs.constants.O_DIRECTORY);
  try{assert.throws(()=>native.renameNoReplace(fd,'stage','target'),{code:'EEXIST'});}finally{fs.closeSync(fd);}
  const after=fs.lstatSync('target',{bigint:true});assert.equal(after.ino,before.ino);assert.equal(after.mode,before.mode);
  assert.equal(fs.readFileSync('stage/receipt','utf8'),'candidate');assert.equal(fs.readFileSync('outside/sentinel','utf8'),'safe');`);
 }));
test('emitted adapter validates descriptors, arity and bounded leaf names',()=>fixture(root=>{
 child(root,prelude+`
 const native=load();fs.mkdirSync('stage');const fd=fs.openSync('.',fs.constants.O_RDONLY|fs.constants.O_DIRECTORY);
 try{
  for(const name of ['', '.', '..', '../escape', 'a/b', 'x'.repeat(256), 'a\\0b'])assert.throws(()=>native.renameNoReplace(fd,name,'target'),{code:'R09_ARGUMENT'});
  for(const invalid of [-1,NaN,Infinity,0.5,2147483648,'0'])assert.throws(()=>native.renameNoReplace(invalid,'stage','target'),{code:'R09_ARGUMENT'});
  assert.throws(()=>native.renameNoReplace(fd,'stage'),{code:'R09_ARGUMENT'});assert.throws(()=>native.renameNoReplace(fd,'stage','target',0),{code:'R09_ARGUMENT'});
 }finally{fs.closeSync(fd);}
 assert.equal(fs.existsSync('stage'),true);assert.equal(fs.existsSync('target'),false);`);
}));
