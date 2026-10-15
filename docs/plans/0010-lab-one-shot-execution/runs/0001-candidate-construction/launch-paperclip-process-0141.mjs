// Candidate adapter integration only; no Paperclip server, database or API.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const [path,pin]=process.argv.slice(2);
const raw=await readFile(path);assert.equal(createHash('sha256').update(raw).digest('hex'),pin);
const config=JSON.parse(raw);
assert.equal(config.command,'/tmp/cal-R02-environment-0001/bin/python');
assert.equal(config.cwd,'/home/vlad_/projects/CyberAlchemy-lab');
assert.equal(config.args[0],'-I');assert.equal(config.args[1],'-B');
assert.equal(config.args[2],config.cwd+'/product/lab/release-candidates/v1/interface/paperclip-runner-v3/runner.py');
assert.equal(config.timeoutSec,960);
const {execute}=await import('/tmp/cal-paperclip-package-inspection-0140/package/dist/adapters/process/execute.js');
const result=await execute({runId:'isolated-Lab-process-0141',
  agent:{id:'isolated-Lab-reader-0141',companyId:'isolated-Lab-pilot-0141'},config,
  authToken:'isolated-process-environment-marker',onLog:async()=>{}});
process.stdout.write(JSON.stringify({result,server_started:false,company_created:false,Paperclip_API_called:false})+'\n');
process.exitCode=result.exitCode===0&&!result.timedOut?0:1;
