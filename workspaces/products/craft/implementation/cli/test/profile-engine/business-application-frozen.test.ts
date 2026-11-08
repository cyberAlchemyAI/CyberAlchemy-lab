import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import path from 'node:path';
// Open questions: BA18 installed replay; publication remains held.
test('frozen two-domain architectures, independently authored profile and composed repeats',async()=>{
 const root=path.resolve(import.meta.dirname,'../../../../../../..');
 const script=path.join(root,'research/craft-alchlang-user-readiness-2026-10-12/business-only-application-plan-2026-10-14/execution/freeze/frozen-matrix.mjs');
 const child=spawn(process.execPath,[script],{cwd:root,stdio:'inherit'});
 const status=await new Promise<number|null>((resolve,reject)=>{child.on('error',reject);child.on('exit',resolve);});
 assert.equal(status,0,'every frozen case and unchanged complete identity must pass');
});
