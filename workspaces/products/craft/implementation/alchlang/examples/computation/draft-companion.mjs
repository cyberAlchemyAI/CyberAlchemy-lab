#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseComputationSource, serializeComputationCompanion, lowerComputationSource, COMPUTATION_BINDINGS, COMPUTATION_CAPABILITY, COMPUTATION_SEMANTICS } from '../../dist/index.js';

const fail = message => { throw new Error('DRAFT_COMPANION:' + message); };

/** Draft syntax/binding data. Full Craft checking and authored meaning review follow. */
export function draftCompanion(argv) {
  if (!Array.isArray(argv) || argv.length !== 4 || argv.some(value => typeof value !== 'string')) fail('usage: --source <absolute.alch> --out <absolute-new-file>');
  const args = new Map();
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index], value = argv[index + 1];
    if (!['--source', '--out'].includes(flag) || !path.isAbsolute(value) || args.has(flag)) fail('explicit source and new absolute output required');
    args.set(flag, value);
  }
  const sourceFile = args.get('--source'), output = args.get('--out');
  if (!sourceFile || !output || !sourceFile.endsWith('.alch')) fail('ordinary .alch source and explicit new output required');
  const stat = lstatSync(sourceFile);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 262144) fail('ordinary source file within 262144 bytes required');
  const bytes = readFileSync(sourceFile);
  let source;
  try { source = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes); }
  catch { fail('source must contain valid UTF-8'); }
  const parsed = parseComputationSource(source, { capability: COMPUTATION_CAPABILITY });
  const declarations = Object.create(null);
  for (const declaration of parsed.declarations) {
    declarations[declaration.name] = { kind: declaration.kind, meaning: declaration.meaning, source_sha256: declaration.source_sha256 };
  }
  const proposal = { schema_version: COMPUTATION_BINDINGS, capability: COMPUTATION_CAPABILITY, semantics: COMPUTATION_SEMANTICS, source_sha256: createHash('sha256').update(bytes).digest('hex'), owner: parsed.owner, declarations };
  const text = serializeComputationCompanion(proposal);
  const lowered = lowerComputationSource(source, text, { capability: COMPUTATION_CAPABILITY });
  if (lowered.source_sha256 !== proposal.source_sha256 || lowered.companion_text !== text) fail('source or proposed byte identity differs');
  // No mkdir, source edits, companion replacement or partial write before validation.
  writeFileSync(output, text, { flag: 'wx', mode: 0o600 });
  return { result: 'proposal-created', source: sourceFile, output, source_sha256: lowered.source_sha256, companion_sha256: lowered.companion_sha256, declaration_count: parsed.declarations.length, validation: 'syntax-and-binding-coverage', next: 'Review the source and proposal, adopt the companion, then run alchlang computation check.', authority_effect: 'none' };
}

let invokedFile;
try { if (process.argv[1]) invokedFile = realpathSync(process.argv[1]); } catch { /* Library import is not a CLI invocation. */ }
if (invokedFile === fileURLToPath(import.meta.url)) {
  try { console.log(JSON.stringify(draftCompanion(process.argv.slice(2)), null, 2)); }
  catch (error) { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; }
}
