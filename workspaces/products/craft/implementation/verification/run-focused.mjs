/** Rerun a repaired preference leaf or the complete portfolio through existing owners.
 * Keeps original and rerun counts separate. No package changes.
 */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {prepareInstalledConnectedChecks} from './installed-check-setup.mjs';
import {implementationRoot as root} from '../source-bindings.mjs';

const json=file=>JSON.parse(readFileSync(file,'utf8'));
const pin=file=>({path:file,sha256:createHash('sha256').update(readFileSync(file)).digest('hex')});
const original=json(path.join(root,'.local/broader-applications.json'));
assert.equal(original.status,'failed','complete the original matrix before a focused repair check');
const mode=process.argv[2]??'preference';assert(['preference','portfolio'].includes(mode));
const state=json(path.join(root,'.local/broader-distribution.json'));
const setup=prepareInstalledConnectedChecks({distributionReport:state.report,label:mode+'-'+Date.now()});
const env={...setup.environment,CRAFT_KEEP_PROFILE_INPUT_TEST_OUTPUT:'1',CRAFT_KEEP_PORTFOLIO_OUTPUT:'1',...(mode==='preference'?{CRAFT_CONNECTED_CASE:'query-permission-and-preference',CRAFT_CONNECTED_BRANCH:'preference'}:{})};
const inputs=[...setup.copied,...setup.copiedFixtures].map(x=>x.original).concat([pin(fileURLToPath(import.meta.url)),pin(path.join(root,'verification/installed-check-setup.mjs'))]);
const report={schema_version:'craft.installed-retest/v1',mode,status:'running',started_at:new Date().toISOString(),original_matrix_finished_at:original.finished_at,original_connected_log_sha256:original.checks.find(x=>x.id==='connected').log_sha256,scope:mode==='preference'?'Only the original query-permission-and-preference group/preference leaf after original-instance lease renewal; unchanged driver deadlines.':'All six original portfolio tests; fixture files remain until physical owners close. No source assertions are skipped.',fixture_lifetime:'Retain temporary files through owner close hooks; remove owned workspace after report collection.',source_inputs:inputs,test_copies:setup.copied,selectors:mode==='preference'?{CRAFT_CONNECTED_CASE:env.CRAFT_CONNECTED_CASE,CRAFT_CONNECTED_BRANCH:env.CRAFT_CONNECTED_BRANCH}:{},package_tuple:setup.distribution.archives.map(({name,version,sha256})=>({name,version,sha256})),authority_effect:'none'};
const output=path.join(root,'.local/broader-'+mode+'-retest.json'),log=path.join(root,'.local/broader-'+mode+'-retest.log');const save=()=>writeFileSync(output,JSON.stringify(report,null,2)+'\n');save();
let stdout='',stderr='';const begin=Date.now();
const result=await new Promise((resolve,reject)=>{const child=spawn(process.execPath,['--test','--test-reporter=tap','--test-concurrency=1',path.join(setup.testDirectory,mode==='preference'?'connected-applications-recovery.test.mjs':'portfolio-business-applications.test.mjs')],{cwd:setup.consumer,env,stdio:['ignore','pipe','pipe']});child.stdout.on('data',b=>{stdout+=b;writeFileSync(log,stdout+'\n'+stderr);});child.stderr.on('data',b=>{stderr+=b;writeFileSync(log,stdout+'\n'+stderr);});child.once('error',reject);child.once('close',(exit_code,signal)=>resolve({exit_code,signal}));});
Object.assign(report,result,{duration_ms:Date.now()-begin,counts:Object.fromEntries(['tests','pass','fail','skipped','cancelled','todo'].map(k=>[k,Number(stdout.match(new RegExp('^# '+k+' (\\d+)$','m'))?.[1]??0)])),log_sha256:pin(log).sha256});
for(const input of [...inputs,...setup.distribution.source_inputs,...setup.copied.map(x=>x.installed),...setup.copiedFixtures.map(x=>x.installed)])assert.equal(pin(input.path).sha256,input.sha256,'focused input changed: '+input.path);
const expected=mode==='preference'?3:6;report.inputs_unchanged=true;report.status=result.exit_code===0&&report.counts.tests===expected&&report.counts.pass===expected&&['fail','skipped','cancelled','todo'].every(k=>report.counts[k]===0)?'passed':'failed';report.finished_at=new Date().toISOString();save();
console.log(JSON.stringify({status:report.status,counts:report.counts,duration_ms:report.duration_ms}));if(report.status!=='passed')process.exitCode=1;
