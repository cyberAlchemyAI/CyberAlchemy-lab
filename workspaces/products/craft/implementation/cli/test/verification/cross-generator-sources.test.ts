import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {getReconciledSource, getReconciledSourceCapsule, validateReconciledSourceCapsule, RECONCILED_SOURCE_CAPSULE_SHA256} from '../../src/generation/reconciled-sources.ts';
import {getCrossGeneratorSource, getCrossGeneratorSourceCapsule, validateCrossGeneratorSourceCapsule, CROSS_GENERATOR_SOURCE_CAPSULE_SHA256} from '../../src/verification/cross-generator-sources.ts';
import {materializeCrossGeneratorSources} from '../../tools/materialize-cross-generator-sources.mjs';
import {materializeReconciledSources} from '../../tools/materialize-reconciled-sources.mjs';
import {workflowFixture} from '../helpers/workflow-verification.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), cli = path.join(project, 'impl/cli');
const selection = JSON.parse(fs.readFileSync(path.join(cli, 'contracts/cross-generator-source-selection.json'), 'utf8'));
const read = (p: string) => fs.readFileSync(path.join(project, p), 'utf8');

test('versioned Operation policy preserves exact predecessors and the historical compiler-capsule record', () => {
  const capsule = getCrossGeneratorSourceCapsule();
  assert.equal(capsule.sources.length, 18);
  const protocol = JSON.parse(getCrossGeneratorSource('operation_protocol'));
  assert.equal(protocol.schema_version, 'domainspec.cross-generator-operation-protocol/v2-candidate');
  const originalProtocol = read('development/reconciliation-v1/profile-compiler-reconciliation/' + protocol.predecessor.path);
  assert.equal(sha256(originalProtocol), '001b5a1eb2d0d35c42b50463280eda66e19f3077812079542ebf84250122edb0');
  assert.equal(protocol.predecessor.sha256, sha256(originalProtocol));
  const predecessorSelection = {...selection, sources: selection.sources.filter((s: any) => s.id !== 'workflow_public_evidence').map((s: any) => s.id === 'operation_protocol' ? {...s, sha256: sha256(originalProtocol)} : s)};
  const predecessor = {schema_version: capsule.schema_version, authority_effect: capsule.authority_effect,
    selection_sha256: sha256(canonicalJson(predecessorSelection)), sources: capsule.sources.filter(s => s.id !== 'workflow_public_evidence').map(s => s.id === 'operation_protocol' ? {...s, content: originalProtocol, sha256: sha256(originalProtocol), size_bytes: Buffer.byteLength(originalProtocol)} : s)};
  assert.equal(predecessor.sources.length, 17);
  assert.equal(sha256(canonicalJson(predecessor)), '898f5ad74d0c88f7786246c697506240973055241c4c8d2c4667136412b4c208');
  const workflow = JSON.parse(getCrossGeneratorSource('workflow_public_evidence'));
  assert.equal(sha256(getCrossGeneratorSource('workflow_public_evidence')), '570cecbca7c0a926ce24ec010ddf1a7499649e5edcba535efdb222da6ada0335');
  assert.equal(workflow.task, 'R08ae14');
  assert.equal(workflow.invariants.length, 6); assert.equal(workflow.validation.length, 10);
  assert.equal(capsule.capsule_sha256, CROSS_GENERATOR_SOURCE_CAPSULE_SHA256);
  assert.equal(capsule.selection_sha256, sha256(canonicalJson(selection)));
  // This binds the historical record, not reproduced source bytes or current runtime evidence.
  const historicalBytes = read('development/reconciliation-v1/profile-compiler-reconciliation/evidence/r08ae2-policy/qualification.json');
  assert.equal(sha256(historicalBytes), 'c014ae8a17c0a21a86a993ce12463af1ca99d4ae06447e3f6199ce04a0512877');
  assert.deepEqual(JSON.parse(historicalBytes).capsule, {
    source_count: 70, sha256: '2a9f76fd9b352c45cfd8eac36a56adddd0ac86a58097f8106c627e3dd7a553bc', changed: false,
  });
  for (const row of capsule.sources) {
    assert.ok(Object.isFrozen(row));
    assert.equal(row.content, read(row.path));
    assert.equal(getCrossGeneratorSource(row.id), row.content);
    assert.equal(sha256(row.content), row.sha256);
    assert.equal(Buffer.byteLength(row.content), row.size_bytes);
  }
  assert.ok(Object.isFrozen(capsule) && Object.isFrozen(capsule.sources));
  assert.equal(materializeCrossGeneratorSources(selection, read), fs.readFileSync(path.join(cli, 'src/verification/cross-generator-sources.generated.ts'), 'utf8'));
  assert.match(execFileSync(process.execPath, ['tools/materialize-cross-generator-sources.mjs', '--check'], {cwd: cli, encoding: 'utf8'}), /"status":"pass"/);
  const pkg = JSON.parse(fs.readFileSync(path.join(cli, 'package.json'), 'utf8'));
  for (const k of ['build', 'typecheck']) {
    const steps: string[] = pkg.scripts[k].split(/\s*&&\s*/);
    assert.deepEqual(steps.slice(0, -1), [
      'catalog', 'relationships', 'integration-profile', 'reconciled-sources', 'cross-generator-sources', 'atomic-publication', 'schemas',
    ].map(name => `npm run ${name}:check`), 'all mandatory source checks precede compilation in order');
    assert.equal(steps.at(-1), k === 'build' ? 'tsc -p tsconfig.json' : 'tsc -p tsconfig.json --noEmit --pretty false');
  }
  assert.equal(pkg.scripts['reconciled-sources:check'], 'node tools/materialize-reconciled-sources.mjs --check');
  assert.equal(pkg.scripts['cross-generator-sources:check'], 'node tools/materialize-cross-generator-sources.mjs --check');
  assert.deepEqual(JSON.parse(getCrossGeneratorSource('public')).families, ['policy', 'state-machine', 'factory-rule', 'owned-values', 'value-producer', 'operation', 'workflow']);
});

test('current reconciled capsule matches exact selected sources and rejects resealed substitutes', () => {
  const selected = JSON.parse(fs.readFileSync(path.join(cli, 'contracts/reconciled-source-selection.json'), 'utf8'));
  const capsule = getReconciledSourceCapsule();
  const selectionDigest = '82294850ace4cd271c704ecc4bfe8c3b5b021618e89534f3469ace901feab8ca';
  assert.equal(sha256(canonicalJson(selected)), selectionDigest, 'selection digest binds its original unsorted order');
  assert.equal(capsule.selection_sha256, selectionDigest);
  assert.equal(selected.sources.length, 136);
  assert.equal(new Set(selected.sources.map((row: any) => row.id)).size, 136);
  assert.equal(new Set(selected.sources.map((row: any) => row.path)).size, 136);
  const expected = [...selected.sources].sort((a, b) => a.id < b.id ? -1 : 1);
  assert.deepEqual(capsule.sources.map(({id, path, sha256}) => ({id, path, sha256})), expected, 'compare runtime order directly; sort only the selection copy');
  assert.equal(sha256(canonicalJson(selected)), selectionDigest, 'deriving runtime order must not mutate the selection');
  const {capsule_sha256, ...body} = capsule;
  assert.equal(RECONCILED_SOURCE_CAPSULE_SHA256, '39ac2a9238417e27091a41a0e0a587806f7338927ce82abe229803fad0a62c00');
  assert.equal(capsule_sha256, RECONCILED_SOURCE_CAPSULE_SHA256);
  assert.equal(sha256(canonicalJson(body)), RECONCILED_SOURCE_CAPSULE_SHA256);
  assert.ok(Object.isFrozen(capsule) && Object.isFrozen(capsule.sources));
  for (const row of capsule.sources) {
    assert.ok(Object.isFrozen(row));
    assert.equal(row.content, read(row.path));
    assert.equal(getReconciledSource(row.id), row.content);
    assert.equal(row.sha256, sha256(row.content));
    assert.equal(row.size_bytes, Buffer.byteLength(row.content));
  }
  assert.equal(materializeReconciledSources(selected, read), fs.readFileSync(path.join(cli, 'src/generation/reconciled-sources.generated.ts'), 'utf8'));
  assert.match(execFileSync(process.execPath, ['tools/materialize-reconciled-sources.mjs', '--check'], {cwd: cli, encoding: 'utf8'}), /"status":"pass"/);
  for (const mutate of [
    (value: any) => {value.sources.pop();},
    (value: any) => {value.sources.reverse();},
    (value: any) => {value.sources[0].content += ' '; value.sources[0].sha256 = sha256(value.sources[0].content); value.sources[0].size_bytes = Buffer.byteLength(value.sources[0].content);},
    (value: any) => {value.selection_sha256 = '0'.repeat(64);},
  ]) {
    const changed = structuredClone(capsule); mutate(changed);
    const {capsule_sha256: ignored, ...changedBody} = changed;
    Object.assign(changed, {capsule_sha256: sha256(canonicalJson(changedBody))});
    assert.throws(() => validateReconciledSourceCapsule(changed), /DS_RECONCILED_SOURCES/);
  }
  const reorderedSelection = {...selected, sources: [...selected.sources].reverse()};
  assert.notEqual(sha256(canonicalJson(reorderedSelection)), selectionDigest);
  assert.notEqual(materializeReconciledSources(reorderedSelection, read), materializeReconciledSources(selected, read), 'selection order remains bound even when runtime source order is normalized');
  let reads = 0;
  const active = {...capsule};
  Object.defineProperty(active, 'sources', {enumerable: true, get() {reads++; return capsule.sources;}});
  assert.throws(() => validateReconciledSourceCapsule(active), /inert data/);
  assert.equal(reads, 0);
  assert.deepEqual(validateReconciledSourceCapsule(structuredClone(capsule)), capsule);
});

test('recomputed hashes, missing sources, unexpected fields and active values cannot replace installed definitions', () => {
  const capsule = getCrossGeneratorSourceCapsule();
  for (const id of ['missing', '../escape', '__proto__', null, {}]) assert.throws(() => getCrossGeneratorSource(id as any), /CROSS_GENERATOR_SOURCES/);
  for (const mutate of [
    (v: any) => {v.sources[0].content += ' ';},
    (v: any) => {v.sources.pop();},
    (v: any) => {v.sources.reverse();},
    (v: any) => {v.extra = true;},
    (v: any) => {v.sources[0].content += ' '; v.sources[0].sha256 = sha256(v.sources[0].content); v.sources[0].size_bytes = Buffer.byteLength(v.sources[0].content); const {capsule_sha256, ...body} = v; v.capsule_sha256 = sha256(canonicalJson(body));}
  ]) {
    const changed = structuredClone(capsule); mutate(changed);
    assert.throws(() => validateCrossGeneratorSourceCapsule(changed), /CROSS_GENERATOR_SOURCES/);
  }
  let reads = 0;
  const active: any = {...capsule};
  Object.defineProperty(active, 'sources', {enumerable: true, get() {reads++; return capsule.sources;}});
  assert.throws(() => validateCrossGeneratorSourceCapsule(active), /inert data/);
  assert.equal(reads, 0);
  assert.deepEqual(validateCrossGeneratorSourceCapsule(structuredClone(capsule)), capsule);
});

test('build materializer rejects incomplete selections, escaping paths, source drift, cycles and getters before reading files', () => {
  for (const mutate of [
    (v: any) => {v.sources.pop();},
    (v: any) => {v.sources[0].id = 'unknown';},
    (v: any) => {v.sources.push(v.sources[0]);},
    (v: any) => {v.sources[0].path = '../escape';},
    (v: any) => {v.sources[0].path = '/absolute';},
    (v: any) => {v.sources[0].path = 'part\\file';},
    (v: any) => {v.sources[0].path = 'part/../file';},
    (v: any) => {v.extra = true;},
    (v: any) => {v.sources[0].sha256 = 'x';}
  ]) {
    const changed = structuredClone(selection); mutate(changed);
    assert.throws(() => materializeCrossGeneratorSources(changed, read), /MATERIALIZATION/);
  }
  assert.throws(() => materializeCrossGeneratorSources(selection, (p: string) => read(p) + ' '), /source drift/);
  let reads = 0;
  const active: any = {...selection};
  Object.defineProperty(active, 'sources', {enumerable: true, get() {reads++; return selection.sources;}});
  assert.throws(() => materializeCrossGeneratorSources(active, () => {reads++; return '';}), /inert data/);
  const cycle: any = {...selection}; cycle.extra = cycle;
  assert.throws(() => materializeCrossGeneratorSources(cycle, read), /inert data/);
  assert.equal(reads, 0);
});

test('compiled relocated preparation runs all seven families with development-tree access denied', t => {
  const f = workflowFixture(t), require = createRequire(import.meta.url);
  const types = fs.realpathSync(require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}));
  const deps = path.dirname(path.dirname(path.dirname(types))), undici = path.dirname(createRequire(types).resolve('undici-types/package.json'));
  const src = path.join(cli, 'src'), dist = path.join(f.root, 'dist'), image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const args = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + cli + ',target=' + cli + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly',
    '--mount', 'type=bind,source=' + undici + ',target=' + undici + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root,
    '--workdir', f.root, image, 'tsc', '--ignoreConfig', '--strict', '--types', 'node', '--typeRoots', path.join(deps, '@types'),
    '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', src, '--outDir', dist, path.join(src, 'verification/reconciled-cross-generator-public.ts')];
  try {execFileSync('docker', args, {encoding: 'utf8', timeout: 120000});} catch (e: any) {throw Error(String(e.stdout) + String(e.stderr));}
  fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const moved = path.join(f.root, 'relocated'); fs.renameSync(dist, moved);
  const url = (p: string) => JSON.stringify(pathToFileURL(path.join(moved, p)).href);
  const check = 'import assert from "node:assert/strict"; import fs from "node:fs";\n' +
    'import {getCrossGeneratorSourceCapsule} from ' + url('verification/cross-generator-sources.js') + ';\n' +
    'import {prepareCrossGeneratorVerification} from ' + url('verification/reconciled-cross-generator-public.js') + ';\n' +
    'import {loadCompiledProjectGraph} from ' + url('input/project-model.js') + ';\n' +
    'import {planCompiledReconciledProject} from ' + url('generation/reconciled-project.js') + ';\n' +
    'assert.throws(()=>fs.readFileSync(' + JSON.stringify(path.join(project, selection.sources[0].path)) + '),{code:"ERR_ACCESS_DENIED"});\n' +
    'const graph=loadCompiledProjectGraph(' + JSON.stringify(path.join(f.root, 'source')) + ');const plan=planCompiledReconciledProject(graph,' + JSON.stringify(f.selection) + ');\n' +
    'const p=prepareCrossGeneratorVerification(graph,plan);assert.equal(p.families.length,7);assert.ok(p.families.every(f=>f.state==="prepared"));\n' +
    'assert.equal(p.rows.find(r=>r.family==="workflow").case_count,133);assert.equal(p.behavior_status,"not_evaluable");\n' +
    'const capsule=getCrossGeneratorSourceCapsule();assert.equal(capsule.sources.length,18);\n' +
    'assert.equal(JSON.parse(capsule.sources.find(s=>s.id==="workflow_public_evidence").content).task,"R08ae14");console.log("relocated-preparation-pass");';
  assert.equal(execFileSync(process.execPath, ['--permission', '--allow-fs-read=' + f.root, '--input-type=module', '--eval', check], {cwd: f.root, encoding: 'utf8', timeout: 120000}).trim(), 'relocated-preparation-pass');
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
