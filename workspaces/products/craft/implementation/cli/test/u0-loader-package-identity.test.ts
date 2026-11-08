import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Real public loader/captured files in isolated package copies; no shared-source drift.
// Open Questions: U10 CONTEXT; these are not installed archive observations.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),repo=path.resolve(root,'../../../../..'),frontend=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
function fixture(){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'u0-loader-closure-')),core=path.join(dir,'craft'),front=path.join(dir,'alch');fs.mkdirSync(core);fs.mkdirSync(front);for(const name of ['dist','contracts','package.json'])fs.cpSync(path.join(root,name),path.join(core,name),{recursive:true});fs.mkdirSync(path.join(core,'profiles'));fs.cpSync(path.join(root,'profiles/node-http-entry-u0-v4'),path.join(core,'profiles/node-http-entry-u0-v4'),{recursive:true});for(const name of ['dist','runtime-sources','package.json'])fs.cpSync(path.join(frontend,name),path.join(front,name),{recursive:true});return {dir,core,front};}
const api=async(core:string)=>(await import(pathToFileURL(path.join(core,'dist/index.js')).href)).profileEngine;
test('actual public loader accepts the concrete public frontend package identity and rejects unknown identity',async()=>{
 for(const accepted of [true,false]){const f=fixture();try{const file=path.join(f.front,'package.json'),pkg=JSON.parse(fs.readFileSync(file,'utf8'));pkg.name=accepted?'@cyberalchemy/alchlang':'@unknown/pretend-alch';fs.writeFileSync(file,JSON.stringify(pkg));const own=await api(f.core);if(accepted){const loaded=await own.loadBusinessU0ProfileV4({frontend_root:f.front});own.assertLoadedU0ProfileV4Current(loaded);assert.equal(loaded.basis.artifacts.length,7);own.disposeLoadedU0ProfileV4(loaded);}else await assert.rejects(()=>own.loadBusinessU0ProfileV4({frontend_root:f.front}),/actual AlchLang package required/);}finally{fs.rmSync(f.dir,{recursive:true,force:true});}}
});
test('every metadata validation pass detects later replacement and ancestry changes without ambient reuse',async()=>{
 for(const mode of ['replacement','parent','symlink']){const f=fixture();try{const own=await api(f.core),loaded=await own.loadBusinessU0ProfileV4({frontend_root:f.front});own.assertLoadedU0ProfileV4Current(loaded);own.assertLoadedU0ProfileV4Current(loaded);
  if(mode==='replacement'){const file=path.join(f.front,'dist/business-authoring-project-v2.js'),bytes=fs.readFileSync(file);fs.unlinkSync(file);fs.writeFileSync(file,bytes);}
  else {const folder=path.join(f.front,'runtime-sources'),moved=path.join(f.front,'original-runtime-sources');fs.renameSync(folder,moved);if(mode==='parent')fs.cpSync(moved,folder,{recursive:true});else fs.symlinkSync(moved,folder,'dir');}
  assert.throws(()=>own.assertLoadedU0ProfileV4Current(loaded),/physical closure changed|closure symlink|closure inventory/);
 }finally{fs.rmSync(f.dir,{recursive:true,force:true});}}
});
