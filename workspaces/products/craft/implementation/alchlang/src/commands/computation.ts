import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {lowerComputationSource, COMPUTATION_CAPABILITY} from '../computation-source.js';
import {loadDomainSpecCompiler} from '../domainspec-cli.js';

const fail = (message: string): never => {throw new Error('ALCH_COMPUTATION:' + message);};
function read(file: string): Buffer {
  if (!path.isAbsolute(file)) fail('absolute input path required');
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 2097152) fail('ordinary bounded source/companion required');
  return fs.readFileSync(file);
}
const utf8 = (bytes: Buffer): string => {try {return new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes);} catch {return fail('invalid UTF-8 source/input');}};
const sha = (value: Buffer) => createHash('sha256').update(value).digest('hex');
async function checked(source: string, entry?: string) {
  if (!source.endsWith('.alch')) fail('canonical .alch source required');
  const bytes = read(source), companion = read(source + '.computation.json');
  const text = utf8(bytes);
  const companionText = utf8(companion);
  const lowered = lowerComputationSource(text, companionText, {capability: COMPUTATION_CAPABILITY});
  if (lowered.companion_identity_kind !== 'raw-utf8' || lowered.companion_text !== companionText || lowered.companion_sha256 !== sha(companion)) fail('companion byte identity differs from physical file');
  if (entry !== undefined && /^compute ([A-Za-z_][A-Za-z0-9_]*)$/m.exec(text)?.[1] !== entry) fail('entry differs from explicitly authored compute declaration');
  const compiler = await loadDomainSpecCompiler();
  const envelope = compiler.bindComputationSource(lowered.contract, lowered.source_binding);
  const {checked: program, source_binding} = compiler.unwrapComputationSource(envelope);
  const identity = {kind: 'alchlang-source' as const, source_sha256: sha(bytes), companion_sha256: lowered.companion_sha256, source_map: lowered.source_map, capability: COMPUTATION_CAPABILITY};
  return {lowered, compiler, program, identity, envelope, source_binding};
}
export async function checkAlchComputation(source: string, entry?: string) {
  const result = await checked(source, entry);
  return {result: 'pass', source_node: result.program.contract.source_node, stage: result.program.contract.stage, source_identity: result.identity, source_profile: result.lowered.source_profile, source_binding: result.source_binding, authority_effect: 'none'};
}
export async function buildAlchComputation(source: string, output: string, entry?: string) {
  const result = await checked(source, entry);
  return result.compiler.buildComputationArtifacts(result.envelope, result.identity, output);
}
export async function verifyAlchComputation(source: string, output: string, entry?: string) {
  const result = await checked(source, entry);
  return result.compiler.verifyComputationArtifacts(result.envelope, result.identity, output);
}
export async function runAlchComputationCommand(args: readonly string[]): Promise<number> {
  const [action, source, ...rest] = args;
  if (!action || !['check', 'build', 'verify', 'run'].includes(action) || !source || !path.isAbsolute(source)) fail('usage: computation check|build|verify|run <absolute-source.alch> [--out <absolute-directory>] [--input <absolute-json>] [--entry <declaredCalculation>]');
  const options = new Map<string, string>();
  for (let index = 0; index < rest.length; index += 2) {
    const key = rest[index]!, value = rest[index + 1];
    if (!['--out', '--input', '--entry'].includes(key) || !value || options.has(key) || key !== '--entry' && !path.isAbsolute(value)) fail('invalid or duplicate option:' + key);
    options.set(key, value);
  }
  if ((action === 'build' || action === 'verify') !== options.has('--out') || (action === 'run') !== options.has('--input')) fail('arguments do not match action');
  const entry = options.get('--entry');
  let result: any;
  if (action === 'check') result = await checkAlchComputation(source, entry);
  else if (action === 'build') result = await buildAlchComputation(source, options.get('--out')!, entry);
  else if (action === 'verify') result = await verifyAlchComputation(source, options.get('--out')!, entry);
  else {
    const loaded = await checked(source, entry);
    result = {evaluator: 'independent-reference', ...loaded.compiler.evaluateComputationJson(loaded.program, utf8(read(options.get('--input')!))), authority_effect: 'none'};
  }
  console.log(JSON.stringify(result, null, 2));
  return action === 'run' && result.ok !== true ? 1 : 0;
}
