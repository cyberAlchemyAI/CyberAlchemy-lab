// Invoke the published adapter without starting a server or contacting its API.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const root='/tmp/cal-paperclip-package-inspection-0140';
const integrity={
  'paperclipai-server-2026.1005.0.tgz':'sha512-aqOP7l0yong2VAeIWOq5Gfvi4LYi3/iYlyMsMakDW0raDDida+6QKRZ7a41wO2mxId5OfEz1Gqh9/M0gs7QcnQ=='
};
const archives=[];
for (const name of ['server','adapter-utils','shared']) {
  const metadata=JSON.parse(await readFile(root+'/'+name+'-metadata.json','utf8'))[0];
  assert.equal(metadata.version,'2026.1005.0');
  const bytes=await readFile(root+'/'+metadata.filename);
  const actual='sha512-'+createHash('sha512').update(bytes).digest('base64');
  assert.equal(actual,metadata.integrity);
  if (integrity[metadata.filename]) assert.equal(actual,integrity[metadata.filename]);
  archives.push({package:metadata.id,filename:metadata.filename,integrity:actual});
}
const {execute}=await import(root+'/package/dist/adapters/process/execute.js');
const logs=[];
process.env.PAPERCLIP_API_KEY='isolated-inherited-marker';
const result=await execute({
  runId:'isolated-process-probe-0140',agent:{id:'isolated-agent-0140',companyId:'isolated-company-0140'},
  config:{command:process.execPath,args:['-e',
    'process.stdout.write(JSON.stringify({agent:process.env.PAPERCLIP_AGENT_ID,company:process.env.PAPERCLIP_COMPANY_ID,run:process.env.PAPERCLIP_RUN_ID,key_present:Boolean(process.env.PAPERCLIP_API_KEY)}))'],
    cwd:root,timeoutSec:20,graceSec:2},
  onLog:async(stream,chunk)=>logs.push({stream,chunk})
});
assert.equal(result.exitCode,0);assert.equal(result.timedOut,false);
const observed=JSON.parse(result.resultJson.stdout);
assert.deepEqual(observed,{agent:'isolated-agent-0140',company:'isolated-company-0140',run:'isolated-process-probe-0140',key_present:false});
const output=new URL('Paperclip-process-adapter-probe-0140.json',import.meta.url);
const value={schema_version:'lab-published-paperclip-process-adapter-probe/v1-candidate',result:'PASS',archives,
  actual_adapter_result:result,actual_child_observation:observed,server_started:false,company_created:false,
  Paperclip_API_called:false,Lab_API_called:false,human_pilot_complete:false,actual_owner_outcome:null,
  source_binding:{path:fileURLToPath(import.meta.url),sha256:createHash('sha256').update(await readFile(fileURLToPath(import.meta.url))).digest('hex')},
  authority_effect:'none',task_complete:false,goal_complete:false,
  claim_ceiling:'Actual published process adapter command/args and inherited-token handling only. No running Paperclip server, Lab integration or human usefulness qualification.'};
await writeFile(output,JSON.stringify(value,null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({result:'PASS',report:fileURLToPath(output)})+'\n');
