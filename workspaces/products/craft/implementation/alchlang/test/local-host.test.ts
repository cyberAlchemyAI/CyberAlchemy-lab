import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, type ChildProcess } from 'node:child_process';
import { once } from 'node:events';
import { mkdtempSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildLocalHost, compileLocalHost } from '../src/local-host.js';

const sourcePath = fileURLToPath(new URL('../../extensions/local-host-v1/orders.alch', import.meta.url));
const source = readFileSync(sourcePath, 'utf8');
const fixture = JSON.parse(readFileSync(new URL('../../extensions/event-execution-v1/place-order.request.json', import.meta.url), 'utf8'));
const token = 'local_test_token_'.repeat(3);
const policy = {actor: 'OrderService', grants: ['order-transaction-authority'], operations: ['place-order']};
const work = mkdtempSync(path.join(tmpdir(), 'alch-host-build-'));
const bundle = path.join(work, 'bundle');
const roots: string[] = [];
const running = new Set<ChildProcess>();
const root = () => { const value = mkdtempSync(path.join(tmpdir(), 'alch-provision-')); roots.push(value); return value; };

async function start(runRoot: string, extra: Record<string,string> = {}) {
  const proc = spawn('/usr/bin/python3', [path.join(bundle, 'serve.py'), '--run-root', runRoot], {
    env: {...process.env, PYTHONDONTWRITEBYTECODE: '1', ALCH_HOST_TOKEN: token, ALCH_HOST_POLICY: JSON.stringify(policy), ...extra},
    stdio: ['ignore','pipe','pipe'],
  });
  running.add(proc);
  let out = ''; let err = '';
  proc.stderr!.on('data', data => { err += data; });
  return await new Promise<{proc: ChildProcess; url: string; endpoint: string; status: string; error?: string}>((resolve,reject) => {
    const timer = setTimeout(() => { proc.kill('SIGTERM'); reject(Error(`START_TIMEOUT:${err}`)); }, 30000);
    proc.stdout!.on('data', data => {
      out += data;
      if (out.includes('\n')) {
        clearTimeout(timer);
        try { resolve({proc, ...JSON.parse(out.split('\n')[0])}); } catch (error) { reject(error); }
      }
    });
    proc.once('exit', () => { clearTimeout(timer); if (!out.includes('\n')) reject(Error(`EARLY_EXIT:${out}:${err}`)); });
    proc.once('error', error => { clearTimeout(timer); reject(error); });
  });
}

async function stop(proc: ChildProcess) {
  if (proc.exitCode === null && proc.signalCode === null) { const done = once(proc, 'exit'); proc.kill('SIGTERM'); await done; }
  running.delete(proc);
}

async function call(server: {url:string;endpoint:string}, body: unknown, auth = token) {
  return fetch(server.url + server.endpoint, {method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${auth}`},body:JSON.stringify(body)});
}
const body = () => ({facts: structuredClone(fixture.request.facts), expected_version: 0});

before(async () => { await buildLocalHost(sourcePath, bundle); });
after(async () => { for (const proc of running) await stop(proc); for (const value of roots) rmSync(value,{recursive:true,force:true}); rmSync(work,{recursive:true,force:true}); });

test('profile resolves existing producer and bounded deployment intent', async () => {
  const result = await compileLocalHost(source);
  assert.equal(result.deployment.endpoint, '/functions/orders-local/place-order');
  assert.equal(result.deployment.boundary, 'order-transaction-authority');
  assert.match(result.normalized, /^profile event-execution-v1$/m);
  assert.doesNotMatch(result.normalized, /^deployment /m);
});

test('unsupported exposure, arbitrary grants, duplicate fields and invalid limits reject', async () => {
  for (const invalid of [source.replace('listen loopback','listen public'), source.replace('runtime rust','runtime shell'),
    source.replace('operation place-order\n  timeout-ms','operation record-order\n  timeout-ms'),
    source + '  grant administrator\n', source + '  listen loopback\n',
    source.replace('timeout-ms 5000','timeout-ms 0'), source.replace('max-request-bytes 65536','max-request-bytes 999999999999')]) {
    await assert.rejects(compileLocalHost(invalid), /LOCAL_HOST/);
  }
});

test('real provisioning and loopback Rust invocation survive host restart', async () => {
  const runRoot = root(); const first = await start(runRoot);
  assert.equal(first.status, 'listening', first.error ?? 'HOST_NOT_LISTENING'); assert.match(first.url, /^http:\/\/127\.0\.0\.1:/);
  const response = await call(first, body()); assert.equal(response.status,200); assert.equal((await response.json()).status,'committed');
  assert.ok(existsSync(path.join(runRoot,'history.sqlite')));
  await stop(first.proc);
  const second = await start(runRoot); const replay = await call(second,body());
  assert.equal(replay.status,200); assert.equal((await replay.json()).status,'already-committed');
  await stop(second.proc);
});

test('host credentials required before provisioning and authored roles cannot self-grant', async () => {
  const denied: Record<string,string>[] = [{ALCH_HOST_TOKEN:''}, {ALCH_HOST_POLICY:JSON.stringify({...policy,grants:[]})}];
  for (const env of denied) {
    const runRoot = root(); const server = await start(runRoot, env);
    assert.equal(server.status,'blocked'); assert.ok(!existsSync(path.join(runRoot,'history.sqlite'))); await stop(server.proc);
  }
});

test('HTTP rejects unauthorized calls, context injection and internal transport commands', async () => {
  const server = await start(root());
  assert.equal(server.status, 'listening', server.error ?? 'HOST_NOT_LISTENING');
  assert.equal((await call(server,body(),'wrong')).status,401);
  assert.equal((await call(server,{...body(),context:fixture.context})).status,400);
  assert.equal((await call(server,{command:'claim'})).status,400);
  assert.equal((await fetch(server.url+'/inspect',{headers:{Authorization:`Bearer ${token}`}})).status,404);
  const health = await fetch(server.url+'/health',{headers:{Authorization:`Bearer ${token}`}});
  assert.equal(health.status,200);
  await stop(server.proc);
});

test('request size and business rules are enforced before a commit', async () => {
  const server = await start(root());
  assert.equal(server.status, 'listening', server.error ?? 'HOST_NOT_LISTENING');
  assert.equal((await call(server,{facts:{payload:'x'.repeat(70000)},expected_version:0})).status,413);
  const invalid = body(); invalid.facts.status='committed';
  assert.equal((await call(server,invalid)).status,422);
  assert.equal((await call(server,body())).status,200);
  await stop(server.proc);
});

test('same run root cannot host competing servers', async () => {
  const runRoot = root(); const server = await start(runRoot); const competing = await start(runRoot);
  assert.equal(competing.status,'blocked'); await stop(competing.proc); await stop(server.proc);
});

test('bundle tampering fails before provisioning', async () => {
  const target = path.join(bundle,'host.json'); const original = readFileSync(target);
  try {
    writeFileSync(target, original.toString()+' ');
    const runRoot = root(); const server = await start(runRoot);
    assert.equal(server.status,'blocked'); assert.equal(server.error,'BUNDLE_DRIFT');
    assert.ok(!existsSync(path.join(runRoot,'history.sqlite'))); await stop(server.proc);
  } finally { writeFileSync(target,original); }
});
