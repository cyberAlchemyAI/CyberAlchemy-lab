/** Exercise existing test owners against isolated unpacked packages. No providers or listeners. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {spawn} from 'node:child_process';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {prepareInstalledConnectedChecks} from './installed-check-setup.mjs';
import {implementationRoot as root} from '../source-bindings.mjs';

const state=JSON.parse(readFileSync(path.join(root,'.local/broader-distribution.json'),'utf8'));
const setup=prepareInstalledConnectedChecks({distributionReport:state.report,label:'local-'+Date.now()});
// Original physical owners must close before their fixture files are removed.
// Remove this task's entire temporary workspace after report collection.
const env={...setup.environment,CRAFT_KEEP_PROFILE_INPUT_TEST_OUTPUT:'1',CRAFT_KEEP_PORTFOLIO_OUTPUT:'1'};
const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');
const report={schema_version:'craft.local-installed-applications/v1',status:'running',started_at:new Date().toISOString(),
  distribution:setup.distribution,source_inputs:[...setup.copied,...setup.copiedFixtures].map(x=>x.original),
  test_copies:[...setup.copied,...setup.copiedFixtures],checks:[],authority_effect:'none',
  scope:'Existing connected six-application and two-portfolio tests against unpublished unpacked packages. Recorded providers/models, local injected resources; no live provider or process-crash certification.'};
const output=path.join(root,'.local/broader-applications.json'),save=()=>writeFileSync(output,JSON.stringify(report,null,2)+'\n');save();
for(const [id,names,expected] of [
  ['finite',['application-system-bindings.test.mjs','gateway-source-subjects.test.mjs','recorded-marketing-fixture.test.mjs'],8],
  ['connected',['connected-applications-recovery.test.mjs'],9],
  ['portfolio',['portfolio-business-applications.test.mjs'],6],
]){
  const row={id,status:'running',expected_tests:expected,started_at:new Date().toISOString()},begin=Date.now();report.checks.push(row);save();console.log('stage '+id);
  const args=['--test','--test-reporter=tap','--test-concurrency=1',...names.map(n=>path.join(setup.testDirectory,n))];
  const log=path.join(root,'.local/broader-applications-'+id+'.log');let stdout='',stderr='';
  const result=await new Promise((resolve,reject)=>{const child=spawn(process.execPath,args,{cwd:setup.consumer,env,stdio:['ignore','pipe','pipe']});child.stdout.on('data',b=>{stdout+=b;writeFileSync(log,stdout+'\n'+stderr);});child.stderr.on('data',b=>{stderr+=b;writeFileSync(log,stdout+'\n'+stderr);});child.once('error',reject);child.once('close',(exit_code,signal)=>resolve({exit_code,signal}));});
  Object.assign(row,result,{duration_ms:Date.now()-begin,counts:Object.fromEntries(['tests','pass','fail','skipped','cancelled','todo'].map(k=>[k,Number(stdout.match(new RegExp('^# '+k+' (\\d+)$','m'))?.[1]??0)])),log_sha256:sha(log)});
  row.status=result.exit_code===0&&row.counts.tests===expected&&row.counts.pass===expected&&['fail','skipped','cancelled','todo'].every(k=>row.counts[k]===0)?'passed':'failed';save();console.log(JSON.stringify(row));
}
for(const pin of [...report.source_inputs,...report.distribution.source_inputs,...report.test_copies.map(x=>x.installed)])assert.equal(sha(pin.path),pin.sha256,'source/package input drift: '+pin.path);
report.inputs_unchanged=true;report.status=report.checks.every(x=>x.status==='passed')?'passed':'failed';report.finished_at=new Date().toISOString();save();
console.log(JSON.stringify({status:report.status,checks:report.checks.map(x=>({id:x.id,status:x.status,counts:x.counts}))}));if(report.status!=='passed')process.exitCode=1;
