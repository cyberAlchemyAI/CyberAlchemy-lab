import test from 'node:test';
import assert from 'node:assert/strict';
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {existsSync} from 'node:fs';
import {createBusinessApplicationFixture} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/test/helpers/business-profile.js';
import {prepareProfileProject,planProfileProject,disposeProfileProject} from '../src/profile-engine.js';

// Open questions: BA19 final audit. Planning owns scratch and never runs business/native code.
test('public v2 planning performs no network/compiler invocation and rejects forged or disposed handles',async t=>{
 const fixture=createBusinessApplicationFixture(t,'node-http-entry-local-v2');
 const original={fetch:globalThis.fetch,spawn:childProcess.spawn,spawnSync:childProcess.spawnSync,execFile:childProcess.execFile,execFileSync:childProcess.execFileSync};
 let effects=0;const forbidden=()=>{effects++;throw Error('planning effect forbidden');};
 globalThis.fetch=forbidden as typeof fetch;childProcess.spawn=forbidden as typeof childProcess.spawn;childProcess.spawnSync=forbidden as typeof childProcess.spawnSync;childProcess.execFile=Object.assign(forbidden,{__promisify__:forbidden}) as typeof childProcess.execFile;childProcess.execFileSync=forbidden as typeof childProcess.execFileSync;syncBuiltinESMExports();
 try {
  const prepared=await prepareProfileProject(fixture.file);let disposed=false;t.after(()=>{if(!disposed)disposeProfileProject(prepared);});
  assert.equal(planProfileProject(prepared).composition.components.filter((c:any)=>c.role==='domain-function').length,0);assert.equal(effects,0);
  assert.throws(()=>planProfileProject({...prepared}),/PROFILE_PROJECT_UNREGISTERED/);assert.throws(()=>disposeProfileProject({...prepared}),/PROFILE_PROJECT_UNREGISTERED/);
  const workspace=prepared.workspace;assert.ok(existsSync(workspace));disposeProfileProject(prepared);disposed=true;assert.equal(existsSync(workspace),false);
  assert.throws(()=>planProfileProject(prepared),/PROFILE_PROJECT_UNREGISTERED/);assert.throws(()=>disposeProfileProject(prepared),/PROFILE_PROJECT_UNREGISTERED/);
 }finally {globalThis.fetch=original.fetch;childProcess.spawn=original.spawn;childProcess.spawnSync=original.spawnSync;childProcess.execFile=original.execFile;childProcess.execFileSync=original.execFileSync;syncBuiltinESMExports();}
});
