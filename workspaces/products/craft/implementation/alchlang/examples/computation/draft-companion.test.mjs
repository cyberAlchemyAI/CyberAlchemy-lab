import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, writeFileSync, rmSync, symlinkSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { draftCompanion } from './draft-companion.mjs';
import { parseComputationSource, lowerComputationSource, COMPUTATION_CAPABILITY } from '../../dist/index.js';

const source = `profile application-v1
capability alchlang.computation/v1-candidate
semantics domainspec.iteration-expression/v1-candidate
revision ordered-metered-v1-candidate
stage full-computation
domain totals
owner sum_author
compute main
rounding reject
limits max_input_bytes=262144 max_output_bytes=65536 max_value_bytes=65536 max_items=100 max_iterations=100 max_ast_nodes=4096 max_ast_depth=32 max_call_depth=32 fuel=100000

calculation main:
  meaning "Sum item amounts in source order."
  pure
  input items:List<UInt64,100>
  result UInt64
  expression fold(items,0,state:UInt64,item:UInt64=>checked-add(state,item))
`;
function fixture(t, text = source) {
  const root = mkdtempSync(path.join(tmpdir(), 'draft-companion-')); t.after(() => rmSync(root, { recursive: true, force: true }));
  const file = path.join(root, 'sum.alch'), output = path.join(root, 'candidate.json'); writeFileSync(file, text);
  return { root, file, output, args: ['--source', file, '--out', output] };
}
test('draft derives exact source/declaration bindings and canonical bytes without source edits', t => {
  const f = fixture(t), before = readFileSync(f.file);
  const report = draftCompanion(f.args), text = readFileSync(f.output, 'utf8'), proposed = JSON.parse(text);
  assert.equal(report.result, 'proposal-created'); assert.equal(report.validation, 'syntax-and-binding-coverage');
  assert.equal(report.companion_sha256, createHash('sha256').update(text).digest('hex')); assert.equal(text.endsWith('\n'), false);
  assert.deepEqual(readFileSync(f.file), before);
  const parsed = parseComputationSource(source, { capability: COMPUTATION_CAPABILITY });
  assert.deepEqual(proposed.declarations.main, { kind: parsed.declarations[0].kind, meaning: parsed.declarations[0].meaning, source_sha256: parsed.declarations[0].source_sha256 });
  assert.equal(lowerComputationSource(source, text, { capability: COMPUTATION_CAPABILITY }).companion_sha256, report.companion_sha256);
});
test('existing output, source output and dangling output symlinks are never overwritten', t => {
  const f = fixture(t); writeFileSync(f.output, 'keep');
  assert.throws(() => draftCompanion(f.args), /EEXIST/); assert.equal(readFileSync(f.output, 'utf8'), 'keep');
  assert.throws(() => draftCompanion(['--source', f.file, '--out', f.file]), /EEXIST/); assert.equal(readFileSync(f.file, 'utf8'), source);
  const link = path.join(f.root, 'dangling.json'); symlinkSync(path.join(f.root, 'missing'), link);
  assert.throws(() => draftCompanion(['--source', f.file, '--out', link]), /EEXIST/); assert.equal(existsSync(path.join(f.root, 'missing')), false);
});
test('invalid syntax and UTF-8 reject before creating any proposal', t => {
  const f = fixture(t, source.replace('checked-add(state,item)', '@'));
  assert.throws(() => draftCompanion(f.args), /COMPUTATION_SYNTAX/); assert.equal(existsSync(f.output), false);
  writeFileSync(f.file, Buffer.from([0xff])); assert.throws(() => draftCompanion(f.args), /valid UTF-8/); assert.equal(existsSync(f.output), false);
});
test('oversized, directory and symbolic-link source inputs reject without output', t => {
  const f = fixture(t, ' '.repeat(262145)); assert.throws(() => draftCompanion(f.args), /262144/); assert.equal(existsSync(f.output), false);
  const dir = path.join(f.root, 'directory.alch'); mkdirSync(dir);
  assert.throws(() => draftCompanion(['--source', dir, '--out', f.output]), /ordinary source/);
  const link = path.join(f.root, 'linked.alch'); symlinkSync(f.file, link);
  assert.throws(() => draftCompanion(['--source', link, '--out', f.output]), /ordinary source/); assert.equal(existsSync(f.output), false);
});
test('explicit argument and output-parent requirements do not create directories', t => {
  const f = fixture(t);
  for (const args of [[], ['--source', 'relative.alch', '--out', f.output], ['--source', f.file, '--source', f.file], ['--source', f.file, '--force', f.output]]) assert.throws(() => draftCompanion(args), /DRAFT_COMPANION/);
  const output = path.join(f.root, 'absent-parent', 'proposal.json'); assert.throws(() => draftCompanion(['--source', f.file, '--out', output]), /ENOENT/); assert.equal(existsSync(path.dirname(output)), false);
});
test('proposal creation does not pretend to perform full Craft reference checking', t => {
  const f = fixture(t, source.replace('fold(items,0,state:UInt64,item:UInt64=>checked-add(state,item))', 'missing(items)'));
  assert.equal(draftCompanion(f.args).result, 'proposal-created'); assert.ok(existsSync(f.output));
});
test('the actual helper CLI works through a development package symlink', t => {
  const f = fixture(t), helper = path.join(f.root, 'helper.mjs');
  symlinkSync(fileURLToPath(new URL('./draft-companion.mjs', import.meta.url)), helper);
  const result = spawnSync(process.execPath, [helper, ...f.args], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).result, 'proposal-created'); assert.ok(existsSync(f.output));
});
