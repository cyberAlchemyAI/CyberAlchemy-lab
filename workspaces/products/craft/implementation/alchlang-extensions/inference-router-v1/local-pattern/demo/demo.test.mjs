import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {runDemo,verifyBundle} from './run.mjs';
// Lifecycle tests for the demo wrapper. Open Questions: README.md.
test('complete API walkthrough closes all three listeners and preserves accepted bundle',async()=>{
 let addresses;const result=await runDemo({report:()=>{},onReady:a=>{addresses=a;}});
 assert.equal(result.checks,11);assert.equal(result.status,'passed');
 for(const address of [addresses.url,...addresses.engines])await assert.rejects(fetch(address,{signal:AbortSignal.timeout(1000)}));
 assert.ok(verifyBundle());
});
test('modified manifest rejects before listeners open',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'demo-invalid-'));let ready=false;
 try{writeFileSync(join(dir,'manifest.json'),'{}');await assert.rejects(runDemo({bundle:dir,report:()=>{},onReady:()=>{ready=true;}}),/ACCEPTED_MANIFEST_MISMATCH/);assert.equal(ready,false);}finally{rmSync(dir,{recursive:true,force:true});}
});
test('pre-aborted startup does not open listeners',async()=>{
 const c=new AbortController();c.abort();let ready=false;
 await assert.rejects(runDemo({signal:c.signal,report:()=>{},onReady:()=>{ready=true;}}));assert.equal(ready,false);
});
test('a failure after startup still closes the service and both engines',async()=>{
 let addresses;
 await assert.rejects(runDemo({report:()=>{},onReady:a=>{addresses=a;throw Error('STARTUP_WITNESS');}}),/STARTUP_WITNESS/);
 for(const address of [addresses.url,...addresses.engines])await assert.rejects(fetch(address,{signal:AbortSignal.timeout(1000)}));
});
test('SIGTERM stops the interactive CLI cleanly',async()=>{
 const child=spawn(process.execPath,[new URL('./run.mjs',import.meta.url).pathname,'--serve'],{stdio:['ignore','pipe','pipe']});
 const exit=once(child,'exit');let output='',url,timer;
 try{
  await new Promise((yes,no)=>{timer=setTimeout(()=>no(Error('DEMO_START_TIMEOUT')),15000);child.once('error',no);child.once('exit',()=>no(Error('DEMO_EARLY_EXIT')));child.stdout.on('data',chunk=>{output+=chunk;url=/http:\/\/127\.0\.0\.1:[0-9]+/.exec(output)?.[0];if(output.includes('Ready for API calls.')){clearTimeout(timer);yes();}});});
  assert.equal((await fetch(url+'/healthz')).status,200);child.kill('SIGTERM');assert.deepEqual(await exit,[0,null]);assert.match(output,/Stopped service and mock engines/);
  await assert.rejects(fetch(url,{signal:AbortSignal.timeout(1000)}));
 }finally{clearTimeout(timer);if(child.exitCode===null)child.kill('SIGKILL');}
});
