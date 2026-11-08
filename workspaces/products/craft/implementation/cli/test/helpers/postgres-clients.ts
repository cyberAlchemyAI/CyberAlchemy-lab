// Real clients for owned Linux Docker fixtures. Open questions: C4-CLI-RESOURCE-HARNESS.v1.md.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {nodeExecutable} from './local-toolchain.ts';

export const POSTGRES_TEST_IMAGE = 'postgres:16@sha256:71e27bf60b70bded003791b5573f8b808365613f341df20ffcf0c1ed7bc13ddf';
const OWNER_LABEL = 'org.cyberalchemy.c4.postgres.owner';
const DOCKER_SOCKET = 'unix:///var/run/docker.sock';

export function createPostgresDocker(root: string) {
  assert.equal(fs.statSync('/var/run/docker.sock').isSocket(), true, 'local Docker socket required');
  const docker = '/usr/bin/docker';
  fs.accessSync(docker, fs.constants.X_OK);
  const config = path.join(root, 'docker-config');
  fs.mkdirSync(config, {mode: 0o700});
  fs.writeFileSync(path.join(config, 'config.json'), '{}\n', {mode: 0o600});
  const owner = randomUUID();
  const prefix = ['--config', config, '--host', DOCKER_SOCKET];
  const environment = {PATH: '/usr/bin:/bin', LANG: 'C.UTF-8'};
  const execute = (args: readonly string[]) => spawnSync(docker, [...prefix, ...args], {encoding: 'utf8', env: environment, timeout: 15000, maxBuffer: 1048576});
  const run = (args: readonly string[]) => {
    const name = args[0] === 'run' ? args[args.indexOf('--name') + 1] : undefined;
    const cid = name ? args[args.indexOf('--cidfile') + 1] : undefined;
    const record = name ? path.join(root, name + '.launch.json') : undefined;
    if (record) {
      assert.equal(name, `domainspec-pg-${owner}`);
      assert.equal(cid, path.join(root, 'server.cid'));
      fs.writeFileSync(record, JSON.stringify({owner, name, cid, phase: 'pending', normal: false}), {mode: 0o600, flag: 'wx'});
    }
    const result = execute(args);
    if (record) {
      const id = cid && fs.existsSync(cid) ? fs.readFileSync(cid, 'utf8').trim() : null;
      const normal = !result.error && !result.signal && result.status === 0 && /^[0-9a-f]{64}$/.test(id ?? '') && result.stdout.trim() === id;
      fs.writeFileSync(record, JSON.stringify({owner, name, cid, id, phase: 'terminal', normal, status: result.status, signal: result.signal, error: result.error?.message ?? null}), {mode: 0o600});
    }
    return result;
  };
  const cached = run(['image', 'inspect', '--format', '{{.Id}}', POSTGRES_TEST_IMAGE]);
  assert.equal(cached.status, 0, cached.stderr || cached.error?.message);
  assert.equal(cached.stdout.trim(), POSTGRES_TEST_IMAGE.split('@')[1], 'exact cached PostgreSQL image required');

  const {cleanupAll} = createPostgresCleanup(root, owner, execute);
  return {docker, config, owner, prefix, environment, run, cleanupAll, label: `${OWNER_LABEL}=${owner}`};
}

// Test-only transport seam: fault controls are not observations of a real daemon.
export function createPostgresCleanup(root: string, owner: string,
  execute: (args: readonly string[]) => {status: number | null; stdout: string; stderr: string; error?: Error},
  pause = () => { Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 250); }) {

  function cleanup(recordFile: string): void {
    const record = JSON.parse(fs.readFileSync(recordFile, 'utf8'));
    assert.equal(record.owner, owner);
    assert.ok(record.name === `domainspec-pg-${owner}` || record.name.startsWith(`domainspec-pg-client-${owner}-`));
    assert.equal(path.dirname(record.cid), root);
    if (record.phase === 'cleaned') return;
    for (let attempt = 0; attempt < 10; attempt++) {
      const id = fs.existsSync(record.cid) ? fs.readFileSync(record.cid, 'utf8').trim() : record.id;
      if (id) assert.match(id, /^[0-9a-f]{64}$/);
      const inspected = execute(['container', 'inspect', id || record.name]);
      if (inspected.status === 0) {
        const [container] = JSON.parse(inspected.stdout);
        assert.equal(container.Name, '/' + record.name, 'cleanup name must match the owned resource');
        assert.equal(container.Config.Labels?.[OWNER_LABEL], owner, 'cleanup must not remove a foreign container');
        assert.match(container.Id, /^[0-9a-f]{64}$/);
        const removed = execute(['container', 'rm', '--force', container.Id]);
        assert.equal(removed.status, 0, removed.stderr || removed.error?.message);
        const absent = execute(['container', 'inspect', container.Id]);
        assert.notEqual(absent.status, 0, 'owned container must be absent after cleanup');
        assert.match(absent.stderr, /No such (container|object)/i);
        fs.writeFileSync(recordFile, JSON.stringify({...record, id: container.Id, phase: 'cleaned'}));
        return;
      }
      assert.match(inspected.stderr, /No such (container|object)/i, inspected.error?.message);
      if (record.normal === true && id) {
        fs.writeFileSync(recordFile, JSON.stringify({...record, id, phase: 'cleaned'}));
        return;
      }
      pause();
    }
    throw new Error(`DS_TEST_PG_LAUNCH_UNCERTAIN: retained ${recordFile}`);
  }

  function cleanupAll(): void {
    const errors: string[] = [];
    for (const file of fs.readdirSync(root).filter(file => file.endsWith('.launch.json'))) {
      try { cleanup(path.join(root, file)); } catch (error) { errors.push(String(error)); }
    }
    const remaining = execute(['container', 'ls', '--all', '--quiet', '--filter', `label=${OWNER_LABEL}=${owner}`]);
    if (remaining.status !== 0 || remaining.stdout.trim()) errors.push('DS_TEST_PG_OWNED_FAMILY_NOT_EMPTY');
    if (errors.length) throw new Error(errors.join('\n'));
  }

  return {cleanupAll};
}

export function installPostgresClients(root: string, control: Pick<ReturnType<typeof createPostgresDocker>, 'docker' | 'config' | 'owner'>, port: number): string {
  assert.ok(Number.isSafeInteger(port) && port >= 1 && port <= 65535, 'owned PostgreSQL port required');
  const bin = path.join(root, 'postgres-client-bin');
  fs.mkdirSync(bin, {mode: 0o700});
  for (const tool of ['psql', 'pg_isready'] as const) {
    const expected = tool === 'psql'
      ? ['-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-p', String(port), '-U', 'postgres', '-d', 'domainspec']
      : ['-h', '127.0.0.1', '-p', String(port), '-U', 'postgres', '-d', 'domainspec'];
    const script = `#!${nodeExecutable()}
const fs = require('node:fs'), path = require('node:path');
const {spawnSync} = require('node:child_process'), {randomUUID} = require('node:crypto');
const tool = ${JSON.stringify(tool)}, expected = ${JSON.stringify(expected)};
if (JSON.stringify(process.argv.slice(2)) !== JSON.stringify(expected) || (tool === 'psql' && process.env.PGPASSWORD !== 'domainspec-test')) {
  process.stderr.write('DS_TEST_PG_TARGET_MISMATCH\\n'); process.exit(64);
}
const docker = ${JSON.stringify(control.docker)}, owner = ${JSON.stringify(control.owner)};
const prefix = ['--config', ${JSON.stringify(control.config)}, '--host', ${JSON.stringify(DOCKER_SOCKET)}];
const env = {PATH:'/usr/bin:/bin', LANG:'C.UTF-8'};
const name = 'domainspec-pg-client-' + owner + '-' + randomUUID(), cid = path.join(${JSON.stringify(root)}, name + '.cid');
const recordFile = path.join(${JSON.stringify(root)}, name + '.launch.json');
const input = tool === 'psql' ? fs.readFileSync(0) : undefined;
function command(args) { return spawnSync(docker, [...prefix, ...args], {encoding:'utf8', env, timeout:5000, maxBuffer:1048576}); }
let result;
fs.writeFileSync(recordFile, JSON.stringify({owner, name, cid, phase:'pending', normal:false}), {mode:0o600, flag:'wx'});
try {
  result = spawnSync(docker, [...prefix, 'run', '--rm', '--pull', 'never', '--name', name, '--label', ${JSON.stringify(OWNER_LABEL)} + '=' + owner, '--cidfile', cid,
    '--network', 'host', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534',
    '--tmpfs', '/tmp:rw,nosuid,noexec', '--tmpfs', '/var/lib/postgresql/data:rw,nosuid,noexec', '--env', 'PGPASSWORD=domainspec-test',
    '--entrypoint', tool, '-i', ${JSON.stringify(POSTGRES_TEST_IMAGE)}, ...expected], {input, encoding:'utf8', env, timeout:10000, maxBuffer:1048576});
} finally {
  const id = fs.existsSync(cid) ? fs.readFileSync(cid,'utf8').trim() : null;
  if (id && !/^[0-9a-f]{64}$/.test(id)) throw Error('DS_TEST_PG_CID_INVALID');
  const normal = Boolean(result && !result.error && !result.signal && result.status !== null && id);
  const record = {owner, name, cid, id, phase:'terminal', normal, status:result?.status ?? null, signal:result?.signal ?? null, error:result?.error?.message ?? null};
  fs.writeFileSync(recordFile, JSON.stringify(record));
  let cleaned = false;
  for (let attempt=0;attempt<10;attempt++) {
    const lateId = fs.existsSync(cid) ? fs.readFileSync(cid,'utf8').trim() : id;
    if (lateId && !/^[0-9a-f]{64}$/.test(lateId)) throw Error('DS_TEST_PG_CID_INVALID');
    const inspected = command(['container','inspect',lateId || name]);
    if (inspected.status === 0) {
      const [container] = JSON.parse(inspected.stdout);
      if (container.Name !== '/' + name || container.Config.Labels?.[${JSON.stringify(OWNER_LABEL)}] !== owner || !/^[0-9a-f]{64}$/.test(container.Id)) throw Error('DS_TEST_PG_CLEANUP_OWNER_MISMATCH');
      const removed = command(['container','rm','--force',container.Id]);
      if (removed.status !== 0) throw Error('DS_TEST_PG_CLEANUP_FAILED');
      const absent = command(['container','inspect',container.Id]);
      if (absent.status === 0 || !/No such (container|object)/i.test(absent.stderr)) throw Error('DS_TEST_PG_CLEANUP_FAILED');
      fs.writeFileSync(recordFile, JSON.stringify({...record,id:container.Id,phase:'cleaned'})); cleaned = true; break;
    }
    if (!/No such (container|object)/i.test(inspected.stderr)) throw Error('DS_TEST_PG_CLEANUP_INSPECT_FAILED');
    if (normal && lateId) { fs.writeFileSync(recordFile, JSON.stringify({...record,id:lateId,phase:'cleaned'})); cleaned = true; break; }
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,250);
  }
  if (!cleaned) throw Error('DS_TEST_PG_LAUNCH_UNCERTAIN: retain ' + recordFile);
}
if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);
if (result.error || result.signal) { process.stderr.write('DS_TEST_PG_CLIENT_PROCESS_FAILED\\n'); process.exit(1); }
process.exit(result.status ?? 1);
`;
    fs.writeFileSync(path.join(bin, tool), script, {mode: 0o700, flag: 'wx'});
  }
  return bin;
}
