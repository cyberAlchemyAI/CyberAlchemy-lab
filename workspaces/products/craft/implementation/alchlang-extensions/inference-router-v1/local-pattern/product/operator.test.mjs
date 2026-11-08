import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
import {createConnection} from 'node:net';
import {createRunner} from './process-runner.mjs';
import {validateSuites} from './validation.mjs';
// Open Questions: OPERATOR.md.
const temp=()=>mkdtempSync(join(tmpdir(),'inference-operator-'));
async function until(check){for(let i=0;i<200;i++){if(check())return;await delay(25);}throw Error('TIMED_OUT');}
function live(pid){try{return !/^State:\s+Z/m.test(readFileSync('/proc/'+pid+'/status','utf8'));}catch(e){if(e.code==='ENOENT')return false;throw e;}}
for(const signal of ['SIGINT','SIGTERM'])test(signal+' cancels nested workers and closes their listener',{timeout:15000},async()=>{
 const dir=temp(),ready=join(dir,'ready.json');
 const runner=createRunner({cwd:dir,env:process.env,graceMs:100});let info;
 try{
  const descendant=`import {createServer} from 'node:net';import {writeFileSync} from 'node:fs';process.on('SIGINT',()=>{});process.on('SIGTERM',()=>{});const server=createServer();server.listen(0,'127.0.0.1',()=>writeFileSync(${JSON.stringify(ready)},JSON.stringify({pid:process.pid,parent:process.ppid,port:server.address().port})));`;
  const parent=`import {spawnSync} from 'node:child_process';spawnSync(process.execPath,['--input-type=module','-e',${JSON.stringify(descendant)}],{stdio:'inherit'});`;
  const running=runner.run(['--input-type=module','-e',parent],join(dir,'cancel.log'));
  const rejected=assert.rejects(running,/VALIDATION_CANCELLED/);
  await until(()=>existsSync(ready));info=JSON.parse(readFileSync(ready));
  runner.stop(signal);await rejected;
  await until(()=>!live(info.pid)&&!live(info.parent));
  await new Promise((resolve,reject)=>{const socket=createConnection({host:'127.0.0.1',port:info.port});socket.on('connect',()=>{socket.destroy();reject(Error('LISTENER_LEAK'));});socket.on('error',e=>e.code==='ECONNREFUSED'?resolve():reject(e));});
  await assert.rejects(runner.run(['-e','process.exit(0)']),/VALIDATION_CANCELLED/);
 }finally{runner.stop('SIGTERM');if(info)for(const pid of [info.pid,info.parent])try{process.kill(pid,'SIGKILL');}catch{}rmSync(dir,{recursive:true,force:true});}
});
test('a failing suite preserves logs and prior results, writes failure, and stops later suites',async()=>{
 const dir=temp(),marker=join(dir,'should-not-run');
 const runner=createRunner({cwd:dir,env:process.env});let verified=false;
 try{
  await assert.rejects(validateSuites({output:dir,identity:{manifest_sha256:'fixture'},here:dir,run:runner.run,verifyProduct:()=>{verified=true;return {manifest_sha256:'fixture'};},suites:[
   ['passed',['-e',"console.log('# pass 1\\n# fail 0')"],1],
   ['broken',['-e',"console.error('intentional suite failure');process.exit(7)"],1],
   ['unreached',['-e',`require('node:fs').writeFileSync(${JSON.stringify(marker)},'bad')`],1]
  ]}),/COMMAND_FAILED: 7/);
  const receipt=JSON.parse(readFileSync(join(dir,'RESULT.json')));
  assert.equal(receipt.status,'failed');assert.match(receipt.error,/COMMAND_FAILED: 7/);
  assert.equal(receipt.suites.length,1);assert.equal(receipt.suites[0].name,'passed');
  assert.match(readFileSync(join(dir,'broken.log'),'utf8'),/intentional suite failure/);
  assert.equal(existsSync(marker),false);assert.equal(verified,false);assert.equal(receipt.tests_passed,undefined);
 }finally{rmSync(dir,{recursive:true,force:true});}
});
