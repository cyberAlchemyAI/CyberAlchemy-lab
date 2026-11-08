import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {createProfileFixture} from './profile-fixture.js';
import {loadProfileProject} from '../../src/profile-engine/loader.js';
import {assertNativeImportClosure,qualifyNativeFiles} from '../../src/profile-engine/native-check.js';
import {prepareProfileBusinessInput} from '../../src/profile-engine/business-input.js';
// Open questions: final complete frozen/current installed qualification PE19/23.
const compiler=path.resolve(import.meta.dirname,'../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules/typescript/bin/tsc');
test('static native imports cannot escape owned output, hide computed imports or load ambient packages',t=>{
 const f=createProfileFixture(t),snapshot=loadProfileProject(path.join(f.root,'project.json'),{engine:f.identity.engine,tools:[{key:'tsc',path:compiler},{key:'parser',path:path.join(path.dirname(path.dirname(compiler)),'lib/typescript.js')}]});
 const cases:[string,string][]=[['import "../../outside.js";','PROFILE_NATIVE_IMPORT_ESCAPE'],['import "./missing.js";','PROFILE_NATIVE_IMPORT_MISSING'],['const moduleName="./safe.js";import(moduleName);','PROFILE_NATIVE_IMPORT_DYNAMIC'],['import "ambient-package";','PROFILE_NATIVE_IMPORT_UNSUPPORTED'],['import "node:fs";','PROFILE_NATIVE_IMPORT_UNSUPPORTED']];
 for(const [source,code]of cases)assert.throws(()=>assertNativeImportClosure(snapshot,{'src/index.mjs':source,'src/safe.js':'export const safe=true;'},compiler),{code});
 assertNativeImportClosure(snapshot,{'src/index.mjs':'import {value} from "./safe.js";export {value};','src/safe.js':'export const value=1;'},compiler);
 assert.throws(()=>qualifyNativeFiles(snapshot,{'src/index.ts':'const broken:number="wrong";'},compiler),/PROFILE_NATIVE_CHECK_FAILED/);
});
test('integration configuration cannot smuggle computation, permissions, writes or failure reclassification',t=>{
 for(const change of ['code','permission','write','unit-conversion','failure-reclassification']){const f=createProfileFixture(t),file=path.join(f.root,'provider.json'),provider=JSON.parse(readFileSync(file,'utf8'));
  if(change==='code')provider.bindings[0].correspondence.stock={compute:'process.exit()'};
  else if(change==='permission')provider.bindings[0].authorization='allow-all';
  else if(change==='write')provider.bindings[0].operation.method='POST';
  else if(change==='unit-conversion')provider.bindings[0].unit_conversion='multiply(price,100)';
  else provider.bindings[0].failure_mapping={remoteFailure:'quoted'};
  writeFileSync(file,JSON.stringify(provider));assert.throws(()=>prepareProfileBusinessInput(f.load()),/PROFILE_WIRE_CORRESPONDENCE|PROFILE_WIRE_SHAPE|PROFILE_WIRE_OPERATION_UNSUPPORTED/,change);
 }
});
