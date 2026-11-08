import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {createPostgresCleanup, installPostgresClients} from './postgres-clients.ts';

function fixture(t: test.TestContext) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-pg-clients-controls-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  // No Docker call is permitted by these negative controls. If the target
  // guard were removed, this nonexistent executable makes that visible.
  const control = {docker: path.join(root, 'must-not-execute'), config: path.join(root, 'config'), owner: randomUUID()};
  const port = 54321, bin = installPostgresClients(root, control, port);
  return {root, control, port, bin};
}

test('real-client adapters reject every hostile target or extra argument before launching Docker', t => {
  const {bin, port} = fixture(t);
  for (const tool of ['psql', 'pg_isready']) {
    const expected = [...(tool === 'psql' ? ['-X', '-qAt', '-v', 'ON_ERROR_STOP=1'] : []), '-h', '127.0.0.1', '-p', String(port), '-U', 'postgres', '-d', 'domainspec'];
    const variants = [[], [...expected, '-c', 'select 1'], [...expected, 'postgresql://foreign/db'], [...expected, ...expected.slice(-2)], expected.map(x => x === '127.0.0.1' ? 'example.invalid' : x), expected.map(x => x === String(port) ? '5432' : x), expected.map(x => x === 'postgres' ? 'foreign-user' : x), expected.map(x => x === 'domainspec' ? 'foreign' : x), expected.slice().reverse()];
    for (const args of variants) {
      const rejected = spawnSync(path.join(bin, tool), args, {encoding: 'utf8', input: 'select 1;', env: {PGPASSWORD: 'domainspec-test'}, timeout: 5000});
      assert.equal(rejected.status, 64, `${tool}: ${rejected.error?.message ?? rejected.stderr}`);
      assert.equal(rejected.stdout, '');
      assert.equal(rejected.stderr, 'DS_TEST_PG_TARGET_MISMATCH\n');
    }
  }
});

test('a different password rejects before the SQL client can launch', t => {
  const {bin, port} = fixture(t);
  const args = ['-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-p', String(port), '-U', 'postgres', '-d', 'domainspec'];
  const rejected = spawnSync(path.join(bin, 'psql'), args, {encoding: 'utf8', input: 'select 1;', env: {PGPASSWORD: 'foreign'}, timeout: 5000});
  assert.equal(rejected.status, 64);
  assert.equal(rejected.stderr, 'DS_TEST_PG_TARGET_MISMATCH\n');
});

test('invalid published ports cannot form a PostgreSQL client adapter', t => {
  const {root, control} = fixture(t);
  for (const port of [0, -1, 65536, 1.5, NaN]) assert.throws(() => installPostgresClients(root, control, port), /owned PostgreSQL port required/);
});

function cleanupFixture(t: test.TestContext, normal = false, hasCid = false) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-pg-cleanup-controls-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const owner = randomUUID(), name = `domainspec-pg-${owner}`, cid = path.join(root, 'server.cid');
  const id = 'a'.repeat(64), file = path.join(root, name + '.launch.json');
  fs.writeFileSync(file, JSON.stringify({owner, name, cid, id: hasCid ? id : null, normal, phase: 'terminal'}));
  if (hasCid) fs.writeFileSync(cid, id);
  const calls: string[][] = [];
  const absent = {status: 1, stdout: '', stderr: 'Error: No such container'};
  const present = {status: 0, stdout: JSON.stringify([{Id: id, Name: '/' + name, Config: {Labels: {'org.cyberalchemy.c4.postgres.owner': owner}}}]), stderr: ''};
  return {root, owner, name, cid, id, file, calls, absent, present, record: () => JSON.parse(fs.readFileSync(file, 'utf8'))};
}

test('normal acknowledged launch can establish exact CID absence without removal', t => {
  const f = cleanupFixture(t, true, true);
  createPostgresCleanup(f.root, f.owner, args => { f.calls.push([...args]); return args[1] === 'ls' ? {status: 0, stdout: '', stderr: ''} : f.absent; }, () => {}).cleanupAll();
  assert.equal(f.record().phase, 'cleaned');
  assert.deepEqual(f.calls[0], ['container', 'inspect', f.id]);
  assert.equal(f.calls.some(a => a[1] === 'rm'), false);
});

test('interrupted launches and missing acknowledgements never become clean from repeated absence', t => {
  for (const [normal, hasCid] of [[false, false], [false, true], [true, false]]) {
    const f = cleanupFixture(t, normal, hasCid);
    const cleanup = createPostgresCleanup(f.root, f.owner, args => { f.calls.push([...args]); return args[1] === 'ls' ? {status: 0, stdout: '', stderr: ''} : f.absent; }, () => {});
    assert.throws(() => cleanup.cleanupAll(), /DS_TEST_PG_LAUNCH_UNCERTAIN/);
    assert.equal(f.record().phase, 'terminal');
    assert.equal(f.calls.filter(a => a[1] === 'inspect').length, 10);
    assert.equal(f.calls.some(a => a[1] === 'rm'), false);
    assert.deepEqual(f.calls.at(-1), ['container', 'ls', '--all', '--quiet', '--filter', `label=org.cyberalchemy.c4.postgres.owner=${f.owner}`]);
  }
});

test('late creation must be positively inspected and removed by its owned ID', t => {
  const f = cleanupFixture(t);
  let inspected = 0;
  createPostgresCleanup(f.root, f.owner, args => {
    f.calls.push([...args]);
    if (args[1] === 'inspect') return ++inspected === 2 ? f.present : f.absent;
    return {status: 0, stdout: '', stderr: ''};
  }, () => {}).cleanupAll();
  assert.equal(f.record().phase, 'cleaned');
  assert.deepEqual(f.calls.find(a => a[1] === 'rm'), ['container', 'rm', '--force', f.id]);
  assert.equal(inspected, 3);
});

test('foreign ownership, invalid identity and daemon failures reject without false cleanup', t => {
  for (const kind of ['foreign-name', 'foreign-label', 'invalid-container-id', 'invalid-cid', 'inspect-error', 'remove-error', 'still-present', 'family-residue']) {
    const f = cleanupFixture(t, true, true);
    if (kind === 'invalid-cid') fs.writeFileSync(f.cid, 'not-an-id');
    let inspections = 0;
    const cleanup = createPostgresCleanup(f.root, f.owner, args => {
      f.calls.push([...args]);
      if (args[1] === 'ls') return {status: 0, stdout: kind === 'family-residue' ? f.id : '', stderr: ''};
      if (args[1] === 'rm') return {status: kind === 'remove-error' ? 1 : 0, stdout: '', stderr: 'removal failed'};
      if (kind === 'inspect-error') return {status: 1, stdout: '', stderr: 'daemon unavailable'};
      if (++inspections > 1 && kind !== 'still-present') return f.absent;
      const row = JSON.parse(f.present.stdout)[0];
      if (kind === 'foreign-name') row.Name = '/foreign';
      if (kind === 'foreign-label') row.Config.Labels['org.cyberalchemy.c4.postgres.owner'] = 'foreign';
      if (kind === 'invalid-container-id') row.Id = 'invalid';
      return {...f.present, stdout: JSON.stringify([row])};
    }, () => {});
    assert.throws(() => cleanup.cleanupAll(), kind);
    if (kind !== 'family-residue') assert.equal(f.record().phase, 'terminal', kind);
    if (['foreign-name', 'foreign-label', 'invalid-container-id', 'invalid-cid', 'inspect-error'].includes(kind)) assert.equal(f.calls.some(a => a[1] === 'rm'), false, kind);
    assert.equal(f.calls.at(-1)![1], 'ls', kind);
  }
});

test('one uncertain record cannot suppress cleanup of another record or final family audit', t => {
  const f = cleanupFixture(t);
  const other = `domainspec-pg-client-${f.owner}-${randomUUID()}`, otherFile = path.join(f.root, other + '.launch.json');
  fs.writeFileSync(otherFile, JSON.stringify({owner: f.owner, name: other, cid: path.join(f.root, other + '.cid'), id: 'b'.repeat(64), normal: true, phase: 'terminal'}));
  const cleanup = createPostgresCleanup(f.root, f.owner, args => { f.calls.push([...args]); return args[1] === 'ls' ? {status: 0, stdout: '', stderr: ''} : f.absent; }, () => {});
  assert.throws(() => cleanup.cleanupAll(), /DS_TEST_PG_LAUNCH_UNCERTAIN/);
  assert.equal(f.record().phase, 'terminal');
  assert.equal(JSON.parse(fs.readFileSync(otherFile, 'utf8')).phase, 'cleaned');
  assert.equal(f.calls.at(-1)![1], 'ls');
});

test('generated facades retain uncertainty and reject foreign cleanup in synthetic Docker fault protocol', t => {
  // This executable simulates Docker metadata/process faults, NEVER real SQL.
  for (const scenario of ['normal', 'signal', 'missing-cid', 'foreign-label']) {
    const f = cleanupFixture(t);
    fs.unlinkSync(f.file);
    const docker = path.join(f.root, 'synthetic-docker-fault-protocol'), trace = path.join(f.root, 'trace.jsonl');
    const script = `#!${process.execPath}
const fs=require('node:fs');const args=process.argv.slice(6),scenario=${JSON.stringify(scenario)},trace=${JSON.stringify(trace)};
fs.appendFileSync(trace,JSON.stringify(args)+'\\n');
if(args[0]==='run'){
 const name=args[args.indexOf('--name')+1],cid=args[args.indexOf('--cidfile')+1];
 fs.writeFileSync(${JSON.stringify(path.join(f.root, 'identity.json'))},JSON.stringify({name,cid}));
 if(scenario!=='missing-cid')fs.writeFileSync(cid,${JSON.stringify(f.id)});
 if(scenario==='signal')process.kill(process.pid,'SIGTERM');else process.exit(0);
}else if(args[1]==='inspect'){
 const identity=JSON.parse(fs.readFileSync(${JSON.stringify(path.join(f.root, 'identity.json'))}));
 if(scenario==='foreign-label'){process.stdout.write(JSON.stringify([{Id:${JSON.stringify(f.id)},Name:'/'+identity.name,Config:{Labels:{'org.cyberalchemy.c4.postgres.owner':'foreign'}}}]));process.exit(0);}
 process.stderr.write('Error: No such container');process.exit(1);
}else{process.stderr.write('unexpected fault-protocol command');process.exit(65);}
`;
    fs.writeFileSync(docker, script, {mode: 0o700});
    const bin = installPostgresClients(f.root, {docker, config: path.join(f.root, 'config'), owner: f.owner}, 54321);
    const result = spawnSync(path.join(bin, 'pg_isready'), ['-h','127.0.0.1','-p','54321','-U','postgres','-d','domainspec'], {encoding: 'utf8', timeout: 10000});
    const file = fs.readdirSync(f.root).find(x => x.endsWith('.launch.json'))!;
    const record = JSON.parse(fs.readFileSync(path.join(f.root, file), 'utf8'));
    const calls = fs.readFileSync(trace, 'utf8').trim().split('\n').map(x => JSON.parse(x));
    assert.equal(calls.some((a: string[]) => a[1] === 'rm'), false, scenario);
    if (scenario === 'normal') { assert.equal(result.status, 0, result.stderr); assert.equal(record.phase, 'cleaned'); }
    else { assert.notEqual(result.status, 0, scenario); assert.equal(record.phase, 'terminal'); assert.match(result.stderr, scenario === 'foreign-label' ? /CLEANUP_OWNER_MISMATCH/ : /LAUNCH_UNCERTAIN/); }
    if (scenario === 'signal') { assert.equal(record.normal, false); assert.equal(record.signal, 'SIGTERM'); }
  }
});
