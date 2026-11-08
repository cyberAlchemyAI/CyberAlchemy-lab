import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {checkComputationContract, evaluateComputationJson, unwrapComputationSource} from '../computation/index.js';
import {parseComputationJson, inertSnapshot} from '../computation/data.js';
import {generateComputationTypeScript} from '../generation/computation-typescript.js';

export const COMPUTATION_ARTIFACT_VERSION = 'domainspec.computation-artifacts/v1-candidate';
export interface ComputationSourceIdentity {
  readonly kind: 'craft-json' | 'alchlang-source';
  readonly source_sha256: string;
  readonly companion_sha256?: string;
  readonly source_map?: unknown;
  readonly capability?: string;
}
const sha = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
const fail = (message: string): never => {
  throw Object.assign(new Error('DS_COMPUTATION:' + message), {code: 'DS_COMPUTATION', exitCode: 22});
};
function ordered(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(ordered);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, ordered((value as Record<string, unknown>)[key])]));
  return typeof value === 'bigint' ? value.toString() : value;
}
const json = (value: unknown) => JSON.stringify(ordered(value), null, 2) + '\n';
export function decodeComputationUtf8(bytes: Buffer): string {
  try { return new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes); }
  catch { return fail('invalid UTF-8 input'); }
}
export function readComputationFile(file: string): Buffer {
  if (!path.isAbsolute(file)) fail('absolute input path required');
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 2097152) fail('ordinary bounded input file required');
  return fs.readFileSync(file);
}
export function checkComputationSourceInput(input: unknown) {
  if (input && typeof input === 'object' && Object.getOwnPropertyDescriptor(input, 'schema_version')?.value === 'domainspec.computation-source/v1-candidate') return unwrapComputationSource(input);
  const checked = checkComputationContract(input);
  if (checked.contract.stage === 'full-computation') fail('full-computation requires explicit owned computation-source envelope');
  return {checked, source_binding: null};
}
function sourceIdentity(raw: ComputationSourceIdentity): ComputationSourceIdentity {
  const source = inertSnapshot(raw) as Record<string, unknown>;
  if (!source || typeof source !== 'object' || Array.isArray(source)) fail('ordinary source identity required');
  const keys = source.kind === 'craft-json' ? ['kind', 'source_sha256'] : source.kind === 'alchlang-source' ? ['kind', 'source_sha256', 'companion_sha256', 'source_map', 'capability'] : [];
  if (!keys.length || Object.keys(source).sort().join(',') !== keys.sort().join(',')) fail('exact source identity members required');
  for (const key of keys.filter(key => key.endsWith('_sha256'))) if (typeof source[key] !== 'string' || !/^[a-f0-9]{64}$/.test(source[key] as string)) fail('exact SHA256 source identity required');
  if (source.kind === 'alchlang-source') {
    if (source.capability !== 'alchlang.computation/v1-candidate') fail('unsupported source capability');
    const map = source.source_map;
    if (!map || typeof map !== 'object' || Array.isArray(map) || Object.keys(map).length > 4096) fail('bounded source map required');
    for (const [selector, location] of Object.entries(map as Record<string, unknown>)) {
      if (!selector.startsWith('$.') || selector.length > 1024 || !location || typeof location !== 'object' || Array.isArray(location) || Object.keys(location).sort().join(',') !== 'column,line') fail('exact source location required');
      for (const value of Object.values(location as Record<string, unknown>)) if (!Number.isSafeInteger(value) || (value as number) < 1 || (value as number) > 2097152) fail('bounded source position required');
    }
  }
  if (Buffer.byteLength(json(source)) > 2097152) fail('source identity byte bound');
  return source as unknown as ComputationSourceIdentity;
}
function artifacts(input: unknown, rawSource: ComputationSourceIdentity) {
  const source = sourceIdentity(rawSource);
  const {checked, source_binding} = checkComputationSourceInput(input);
  const generated = generateComputationTypeScript(checked);
  const files: Record<string, string> = {
    'computation.ts': generated.source,
    'source-contract.json': json(checked.contract),
    'package.json': json({private: true, type: 'module'}),
  };
  const manifest = {
    schema_version: COMPUTATION_ARTIFACT_VERSION,
    source_identity: source,
    source_binding,
    contract_sha256: sha(files['source-contract.json']!),
    generation: generated.manifest,
    files: Object.fromEntries(Object.entries(files).map(([name, content]) => [name, {sha256: sha(content), size: Buffer.byteLength(content)}])),
    authority_effect: 'none',
  };
  return {checked, files, manifest};
}
export function buildComputationArtifacts(input: unknown, source: ComputationSourceIdentity, output: string) {
  if (!path.isAbsolute(output)) fail('absolute output path required');
  const parent = path.dirname(output);
  if (fs.realpathSync(parent) !== parent) fail('real existing output parent required');
  const plan = artifacts(input, source);
  // Exclusive directory creation also refuses existing empty directories.
  try { fs.mkdirSync(output, {mode: 0o700}); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'EEXIST') fail('output already exists'); throw error; }
  for (const [relative, content] of Object.entries(plan.files)) fs.writeFileSync(path.join(output, relative), content, {flag: 'wx'});
  fs.writeFileSync(path.join(output, 'computation-manifest.json'), json(plan.manifest), {flag: 'wx'});
  return {result: 'pass', output, manifest: plan.manifest, authority_effect: 'none'};
}
export function verifyComputationArtifacts(input: unknown, source: ComputationSourceIdentity, output: string) {
  if (!path.isAbsolute(output) || fs.lstatSync(output).isSymbolicLink()) fail('ordinary absolute generated directory required');
  const plan = artifacts(input, source);
  const expected = [...Object.keys(plan.files), 'computation-manifest.json'].sort();
  if (json(fs.readdirSync(output).sort()) !== json(expected)) fail('generated file inventory changed');
  for (const [relative, content] of Object.entries({...plan.files, 'computation-manifest.json': json(plan.manifest)})) {
    const file = path.join(output, relative), stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink() || !fs.readFileSync(file).equals(Buffer.from(content))) fail('stale source or changed artifact:' + relative);
  }
  return {result: 'pass', output, contract_sha256: plan.manifest.contract_sha256, authority_effect: 'none'};
}
export function computationCommandArguments(args: readonly string[]) {
  const [action, file, ...rest] = args;
  if (!action || !['check', 'build', 'verify', 'run'].includes(action) || !file || !path.isAbsolute(file)) fail('usage: computation check|build|verify|run <absolute-contract.json> [--out <absolute-directory>] [--input <absolute-json>]');
  const options = new Map<string, string>();
  for (let index = 0; index < rest.length; index += 2) {
    const key = rest[index]!, value = rest[index + 1];
    if (!['--out', '--input'].includes(key) || !value || !path.isAbsolute(value) || options.has(key)) fail('invalid or duplicate argument:' + key);
    options.set(key, value!);
  }
  if ((action === 'build' || action === 'verify') !== options.has('--out') || (action === 'run') !== options.has('--input')) fail('arguments do not match action');
  return {action: action!, file: file!, output: options.get('--out'), input: options.get('--input')};
}
export function runComputationCommand(args: readonly string[], io: {stdout(value: string): void; stderr(value: string): void}): number {
  const parsed = computationCommandArguments(args);
  const bytes = readComputationFile(parsed.file);
  const input = parseComputationJson(decodeComputationUtf8(bytes));
  const {checked, source_binding} = checkComputationSourceInput(input);
  const source: ComputationSourceIdentity = {kind: 'craft-json', source_sha256: sha(bytes)};
  let result: unknown;
  if (parsed.action === 'check') result = {result: 'pass', source_node: checked.contract.source_node, stage: checked.contract.stage, source_identity: source, source_binding, authority_effect: 'none'};
  else if (parsed.action === 'build') result = buildComputationArtifacts(input, source, parsed.output!);
  else if (parsed.action === 'verify') result = verifyComputationArtifacts(input, source, parsed.output!);
  else {
    result = evaluateComputationJson(checked, decodeComputationUtf8(readComputationFile(parsed.input!)));
    io.stdout(json({evaluator: 'independent-reference', ...result as object, authority_effect: 'none'}));
    return (result as {ok: boolean}).ok ? 0 : 1;
  }
  io.stdout(json(result));
  return 0;
}
