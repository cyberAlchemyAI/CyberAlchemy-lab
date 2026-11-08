import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { buildEventExecution, compileEventExecution } from './event-execution.js';

const fail = (message: string): never => { throw Error(`LOCAL_HOST: ${message}`); };
const hash = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
const fields = ['runtime', 'provisioner', 'listen', 'operation', 'timeout-ms', 'max-request-bytes'];
const optionalFields = ['events', 'isolation'];

export async function compileLocalHost(source: string) {
  const lines: string[] = []; const values: Record<string, string> = {};
  let id = ''; let block = false; let profiles = 0;
  for (const [index, line] of source.split(/\r?\n/).entries()) {
    if (line === 'profile local-host-v1') { profiles++; lines.push('profile event-execution-v1'); block = false; continue; }
    if (!line.trim() || line.trimStart().startsWith('#')) { lines.push(''); continue; }
    const header = /^deployment ([a-z][a-z0-9-]{0,63}):$/.exec(line);
    if (header) { if (id) fail('one deployment required'); id = header[1]; block = true; lines.push(''); continue; }
    if (block && /^\s/.test(line)) {
      const field = /^  ([a-z-]+) ([A-Za-z0-9][A-Za-z0-9-]*)$/.exec(line);
      if (!field || ![...fields, ...optionalFields].includes(field[1]) || Object.hasOwn(values, field[1])) fail(`invalid deployment field at line ${index + 1}`);
      values[field![1]] = field![2]; lines.push(''); continue;
    }
    block = false; lines.push(line);
  }
  if (profiles !== 1 || !id || fields.some(f => !values[f])) fail('profile and complete deployment required');
  if (values.runtime !== 'rust' || values.provisioner !== 'ansible-local-v1' || values.listen !== 'loopback') fail('unsupported runtime, provisioner or listener');
  if (values.events && !['local','disabled'].includes(values.events) || values.isolation && !['bubblewrap','trusted-process'].includes(values.isolation)) fail('unsupported events or isolation');
  const number = (key: string, max: number) => {
    if (!/^[1-9][0-9]*$/.test(values[key]) || !Number.isSafeInteger(Number(values[key])) || Number(values[key]) > max) fail(`invalid ${key}`);
    return Number(values[key]);
  };
  const normalized = lines.join('\n');
  const event = await compileEventExecution(normalized);
  const operation = event.config.model.actions.find(a => a.id === values.operation);
  if (!operation || !event.config.executions.some(e => e.operation === operation.id && e.kind === 'producer')) fail('exposed operation must be the declared producer');
  const consumerId = event.config.executions.find(e => e.kind === 'consumer')!.operation;
  const consumer = event.config.model.actions.find(a => a.id === consumerId)!;
  return { normalized, deployment: { profile: 'local-host-v1', id, runtime: 'rust', provisioner: values.provisioner,
    events: values.events ?? 'disabled', isolation: values.isolation ?? 'trusted-process',
    consumer: {operation:consumerId,actors:consumer.actor_refs,boundary:consumer.authority_boundary_ref}, transport:event.config.transport,
    listen: '127.0.0.1', operation: operation!.id, actors: operation!.actor_refs, boundary: operation!.authority_boundary_ref,
    timeout_ms: number('timeout-ms', 30000), max_request_bytes: number('max-request-bytes', 262144),
    endpoint: `/functions/${id}/${operation!.id}`, source_sha256: hash(source), authority_effect: 'none' } };
}

export async function buildLocalHost(file: string, output: string) {
  if (path.extname(file) !== '.alch' || existsSync(output)) fail('source extension or existing output');
  const source = readFileSync(file, 'utf8'); const plan = await compileLocalHost(source);
  const stage = mkdtempSync(path.join(path.dirname(path.resolve(output)), '.alch-host-'));
  try {
    const normalized = path.join(stage, 'execution.alch'); writeFileSync(normalized, plan.normalized);
    const bundle = path.join(stage, 'bundle'); await buildEventExecution(normalized, bundle);
    let repo = path.dirname(fileURLToPath(import.meta.url));
    while (!existsSync(path.join(repo, 'cyberAlchemy-v2/agent-routing/profile.json'))) {
      const next = path.dirname(repo); if (next === repo) fail('repository provisioning runtime not found'); repo = next;
    }
    const provisioner = path.join(repo, 'cyberAlchemy-v2/work-orchestration-implementation/extensions/alch-host-provisioning-v1');
    writeFileSync(path.join(bundle, 'authored.alch'), source);
    writeFileSync(path.join(bundle, 'host.json'), JSON.stringify({ ...plan.deployment, provisioner_root: provisioner,
      provisioner_host_sha256: hash(readFileSync(path.join(provisioner, 'host.py'))),
      provisioner_manifest_sha256: hash(readFileSync(path.join(provisioner, 'source-manifest.json'))) }, null, 2) + '\n');
    writeFileSync(path.join(bundle, 'host-plan.json'), JSON.stringify({profile: 'local-host-v1', source_sha256: hash(source),
      isolation: plan.deployment.isolation,
      local_delivery: {enabled:plan.deployment.events==='local',consumer:plan.deployment.consumer.operation,
        transport:plan.deployment.transport,steps:['claim','invoke-consumer','settle'],recovery:'same-message-id-and-lease-fencing'},
      nodes: [{id:'verify-bundle',depends_on:[]},{id:'verify-operator-policy',depends_on:['verify-bundle']},
        {id:'provision',depends_on:['verify-operator-policy'],binding:plan.deployment.provisioner},
        {id:'verify-storage',depends_on:['provision']},{id:'listen-loopback',depends_on:['verify-storage']},
        {id:'invoke',depends_on:['listen-loopback'],operation:plan.deployment.operation}], authority_effect:'none'}, null, 2) + '\n');
    writeFileSync(path.join(bundle, 'host-ontology.json'), JSON.stringify({status:'compiled-scaffold',source_sha256:hash(source),
      nodes:[{id:plan.deployment.id,type:'DeploymentBinding'},{id:plan.deployment.operation,type:'Operation'},
        {id:plan.deployment.provisioner,type:'ProvisioningBinding'},
        ...(plan.deployment.events==='local'?[{id:plan.deployment.consumer.operation,type:'Operation'}]:[])],
      relations:[{from:plan.deployment.id,type:'exposes',to:plan.deployment.operation},
        {from:plan.deployment.id,type:'requires',to:plan.deployment.provisioner},
        ...(plan.deployment.events==='local'?[{from:plan.deployment.id,type:'dispatches-to',to:plan.deployment.consumer.operation}]:[])],authority_effect:'none'},null,2)+'\n');
    cpSync(new URL('./event-templates/serve.py', import.meta.url), path.join(bundle, 'serve.py'));
    cpSync(new URL('./event-templates/local_worker.py', import.meta.url), path.join(bundle, 'local_worker.py'));
    const files = (dir: string): string[] => readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? files(path.join(dir, e.name)) : [path.join(dir, e.name)]);
    const inventory = Object.fromEntries(files(bundle).sort().map(p => [path.relative(bundle, p), hash(readFileSync(p))]));
    writeFileSync(path.join(bundle, 'host-manifest.json'), JSON.stringify({ profile: 'local-host-v1', files: inventory, authority_effect: 'none' }, null, 2) + '\n');
    if (readFileSync(file, 'utf8') !== source) fail('source changed during build');
    renameSync(bundle, output);
    return { status: 'built', output: path.resolve(output), profile: 'local-host-v1', endpoint: plan.deployment.endpoint, authority_effect: 'none' };
  } finally { rmSync(stage, { recursive: true, force: true }); }
}
