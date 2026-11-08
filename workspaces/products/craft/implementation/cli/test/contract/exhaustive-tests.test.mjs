import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {discoverTests, assertInventoryUnchanged, runExhaustive, parseNodeOptions, qualifyExhaustiveLaunch, createNativeCaseLedger} from '../../tools/exhaustive-tests.mjs';

const cliRoot = fileURLToPath(new URL('../../', import.meta.url));
function fixture(t, files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'domainspec-exhaustive-controls-'));
  fs.mkdirSync(path.join(root, 'test'));
  for (const [name, body] of Object.entries(files)) {
    const file = path.join(root, 'test', name);
    fs.mkdirSync(path.dirname(file), {recursive: true});
    fs.writeFileSync(file, body, {flag: 'wx'});
  }
  t.after(() => fs.rmSync(root, {recursive: true, force: true})); // Only this exclusive owned fixture.
  return root;
}
const positive = "import test from 'node:test';test('fixture pass',()=>{});\n";
const negative = "import test from 'node:test';import assert from 'node:assert/strict';test('fixture fail',()=>assert.fail('expected DATA failure'));\n";

test('recursive inventory is deterministic, covers TS and mjs, and ignores helpers', t => {
  const root = fixture(t, {'z.test.ts': '// ts fixture', 'a/b.test.mjs': positive, 'a/helper.ts': '// helper'});
  const inventory = discoverTests(root);
  assert.deepEqual(inventory.files.map(r => r.file), ['test/a/b.test.mjs', 'test/z.test.ts']);
  assert.equal(inventory.count, 2);
  assertInventoryUnchanged(inventory, discoverTests(root));
});

test('added, removed, edited and symlink entries cannot reuse an old epoch', t => {
  const root = fixture(t, {'a.test.mjs': positive}), initial = discoverTests(root);
  fs.writeFileSync(path.join(root, 'test', 'a.test.mjs'), positive + '// changed');
  assert.throws(() => assertInventoryUnchanged(initial, discoverTests(root)), /epoch changed/);
  fs.writeFileSync(path.join(root, 'test', 'a.test.mjs'), positive);
  fs.writeFileSync(path.join(root, 'test', 'b.test.mjs'), positive);
  assert.throws(() => assertInventoryUnchanged(initial, discoverTests(root)), /epoch changed/);
  fs.unlinkSync(path.join(root, 'test', 'a.test.mjs'));
  assert.throws(() => assertInventoryUnchanged(initial, discoverTests(root)), /epoch changed/);
  fs.symlinkSync(path.join(root, 'test', 'b.test.mjs'), path.join(root, 'test', 'link.test.mjs'));
  assert.throws(() => discoverTests(root), /symlink/);
});

test('empty inventories and subset CLI arguments are refused', t => {
  assert.throws(() => discoverTests(fixture(t, {})), /empty/);
  const runner = path.join(cliRoot, 'tools/exhaustive-tests.mjs');
  for (const args of [[], ['--run', 'test/only.test.ts'], ['--inventory', '--test-name-pattern=x'], ['--unknown']]) {
    const r = spawnSync(process.execPath, [runner, ...args], {encoding: 'utf8', timeout: 10000});
    assert.equal(r.status, 1); assert.equal(r.signal, null);
  }
});

test('all original entry files execute once, preserving entry and imported-case identities', async t => {
  const root = fixture(t, {'a.test.mjs': positive, 'sub/b.test.mjs': positive});
  const events = [], result = await runExhaustive(root, {execArgv: [], emit: e => events.push(e)});
  assert.equal(result.pass, true);
  assert.equal(result.selected_files, 2); assert.equal(result.completed_files, 2);
  assert.deepEqual(result.missing_files, []);
  assert.ok(result.files.every(r => r.status === 0 && r.process_group_absent && r.summary.success));
  const ids = events.filter(e => e.type === 'exhaustive:event').map(e => [e.test_epoch, e.entry_file, e.event_id].join(':'));
  assert.equal(new Set(ids).size, ids.length);
  assert.equal(result.full_beta_qualified, false);
});

test('assertion failures do not omit later files or become successful regression', async t => {
  const root = fixture(t, {'a.test.mjs': negative, 'z.test.mjs': positive});
  const result = await runExhaustive(root, {execArgv: [], emit: () => {}});
  assert.equal(result.pass, false); assert.equal(result.completed_files, 2);
  assert.equal(result.files[0].transport_complete, true);
  assert.notEqual(result.files[0].status, 0); assert.equal(result.files[1].pass, true);
});

test('imported case source is not miscounted as another selected entrypoint', async t => {
  const root = fixture(t, {'a.test.mjs': "import './cases/helper.mjs';", 'cases/helper.mjs': positive});
  const events = [], result = await runExhaustive(root, {execArgv: [], emit: e => events.push(e)});
  assert.equal(result.pass, true); assert.equal(result.selected_files, 1);
  const pass = events.find(e => e.type === 'exhaustive:event' && e.event.type === 'test:pass');
  assert.equal(pass.entry_file, 'test/a.test.mjs');
  assert.equal(pass.event.data.file, path.join(root, 'test/cases/helper.mjs'));
});

test('actual missing, duplicate or conflicting native events stop later entry effects and retain the corrupt record',async t=>{
 for(const fault of ['missing','duplicate','counts']){
  const root=fixture(t,{'a.test.mjs':positive,'z.test.mjs':positive});
  // Byte-identical production runner, but only this private DATA fixture gets a
  // corrupt reporter. Never replace the reporter for actual authored suite runs.
  const tools=path.join(root,'tools');fs.mkdirSync(tools);
  const runner=path.join(tools,'exhaustive-tests.mjs');
  fs.writeFileSync(runner,fs.readFileSync(path.join(cliRoot,'tools/exhaustive-tests.mjs')),{flag:'wx'});
  const reporter=pathToFileURL(path.join(cliRoot,'tools/test-events-reporter.mjs')).href;
  fs.writeFileSync(path.join(tools,'test-events-reporter.mjs'),`import events from ${JSON.stringify(reporter)};
export default async function* faulty(source){let injected=false;for await(const line of events(source)){const event=JSON.parse(line);
if(!injected&&event.data?.entryFile){
 if(${JSON.stringify(fault)}==='missing'&&event.type==='test:pass'){injected=true;continue;}
 if(${JSON.stringify(fault)}==='duplicate'&&event.type==='test:pass'){injected=true;yield line;yield line;continue;}
 if(${JSON.stringify(fault)}==='counts'&&event.type==='test:summary'){injected=true;event.data.counts.tests++;yield JSON.stringify(event)+'\\n';continue;}
}yield line;}}`,{flag:'wx'});
  const {runExhaustive:runFaultFixture}=await import(pathToFileURL(runner).href);
  const events=[],result=await runFaultFixture(root,{execArgv:[],emit:e=>events.push(e)});
  assert.equal(result.pass,false,fault);assert.equal(result.completed_files,1,fault);
  assert.equal(result.files[0].transport_complete,false,fault);
  assert.equal(result.files[0].native_case_ledger.complete,false,fault);
  assert.equal(result.files[0].process_group_absent,true,fault);
  assert.deepEqual(result.missing_files,['test/z.test.mjs'],fault);
  if(fault==='duplicate')assert.ok(events.filter(e=>e.type==='exhaustive:event'&&e.event.type==='test:pass').length>=2);
  if(fault==='counts')assert.ok(events.some(e=>e.type==='exhaustive:event'&&e.event.type==='test:summary'&&e.event.data.entryFile&&e.event.data.counts.tests===2));
 }
});

test('authored skips and todos cannot qualify exhaustive regression', async t => {
  for (const annotation of ['skip', 'todo']) {
    const root = fixture(t, {'a.test.mjs': `import test from 'node:test';test('${annotation}',{${annotation}:true},()=>{});`});
    const result = await runExhaustive(root, {execArgv: [], emit: () => {}});
    assert.equal(result.files[0].status, 0); assert.equal(result.pass, false);
    assert.ok(result.files[0][annotation === 'skip' ? 'skipped_cases' : 'todo_cases'] > 0);
  }
});

test('cancellation closes the actual child group and exposes unexecuted files', async t => {
  const root = fixture(t, {'a.test.mjs': "import test from 'node:test';test('slow',async()=>{await new Promise(r=>setTimeout(r,10000));});", 'z.test.mjs': positive});
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 100);
  try {
    const result = await runExhaustive(root, {execArgv: [], signal: controller.signal, emit: () => {}});
    assert.equal(result.pass, false); assert.equal(result.cancelled, true);
    assert.ok(result.files.every(r => r.process_group_absent));
    assert.ok(result.missing_files.includes('test/z.test.mjs'));
  } finally { clearTimeout(timer); }
});

test('source mutation during a child test cannot pass the final epoch check', async t => {
  const source = "import test from 'node:test';import fs from 'node:fs';import {fileURLToPath} from 'node:url';test('mutate',()=>fs.appendFileSync(fileURLToPath(import.meta.url),'\\n//changed'));";
  const root = fixture(t, {'a.test.mjs': source});
  const result = await runExhaustive(root, {execArgv: [], emit: () => {}});
  assert.equal(result.pass, false); assert.equal(result.source_unchanged, false);
  assert.match(result.source_error, /epoch changed/);
});

test('mid-run mutation stops later effects and retains the missing-file ledger', async t => {
  const source = "import test from 'node:test';import fs from 'node:fs';test('mutate sibling',()=>fs.appendFileSync('test/z.test.mjs','\\n//changed'));";
  const root = fixture(t, {'a.test.mjs': source, 'z.test.mjs': positive});
  const result = await runExhaustive(root, {execArgv: [], emit: () => {}});
  assert.equal(result.pass, false); assert.equal(result.completed_files, 1);
  assert.deepEqual(result.missing_files, ['test/z.test.mjs']);
  assert.equal(result.source_unchanged, false);
});

test('timeout cannot pass or filter away its unexecuted successors', async t => {
  const root = fixture(t, {'a.test.mjs': "import test from 'node:test';test('slow',async()=>{await new Promise(r=>setTimeout(r,10000));});", 'z.test.mjs': positive});
  const result = await runExhaustive(root, {execArgv: [], emit: () => {}, fileTimeoutMs: 100});
  assert.equal(result.pass, false); assert.equal(result.files[0].timed_out, true);
  assert.equal(result.files[0].process_group_absent, true);
  assert.deepEqual(result.missing_files, ['test/z.test.mjs']);
});

test('default and product scripts select exhaustive discovery with no duplicate contract phase', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(cliRoot, 'package.json')));
  assert.equal(pkg.scripts.test, 'npm run test:all');
  assert.equal(pkg.scripts['test:all'], 'node tools/exhaustive-tests.mjs --run');
  assert.equal(pkg.scripts['test:inventory'], 'node tools/exhaustive-tests.mjs --inventory');
  assert.ok(!pkg.scripts['verify:product'].includes('npm run test:contract'));
  const current = discoverTests(path.resolve(cliRoot));
  for (const file of ['test/contract/exhaustive-tests.test.mjs', 'test/cli/whole-application-installed-v1.test.ts',
    'test/contract/foundation-contract.test.mjs', 'test/contract/package-boundary.test.mjs']) {
    assert.ok(current.files.some(r => r.file === file), file);
  }
});

test('NODE_OPTIONS parser retains Node quotes, escaped characters and preload values', () => {
  assert.deepEqual(parseNodeOptions('--require "./my path/file.js" --no-warnings'), ['--require', './my path/file.js', '--no-warnings']);
  assert.deepEqual(parseNodeOptions('"--te\\st-name-pattern=x"'), ['--test-name-pattern=x']);
  assert.throws(() => parseNodeOptions('--require "unterminated'), /unterminated/);
  assert.throws(() => parseNodeOptions('"dangling\\'), /escape/);
  const input = {NODE_OPTIONS: '--require "./my path/file.js" --no-warnings', NODE_TEST_CONTEXT: 'child-v8', OTHER: 'retained'};
  const launch = qualifyExhaustiveLaunch(['--import', 'tsx'], input);
  assert.equal(launch.env.NODE_OPTIONS, input.NODE_OPTIONS); assert.equal(launch.env.OTHER, 'retained');
  assert.equal(launch.env.NODE_TEST_CONTEXT, undefined); assert.equal(input.NODE_TEST_CONTEXT, 'child-v8');
});

test('inherited filters, shards, only-mode, watch and indirect configuration fail before any child', async t => {
  const root = fixture(t, {'a.test.mjs': negative}), before = process.env.NODE_OPTIONS;
  try {
    for (const options of ['--test-name-pattern=does-not-match', '--test-skip-pattern=.', '--test-only',
      '--test-shard=1/2', '--test-rerun-failures=old.json', '"--test_name_pattern=does-not-match"',
      '"--te\\st-name-pattern=does-not-match"', '--watch', '--experimental-config-file=other.json',
      '--experimental-default-config-file', '--env-file=other.env']) {
      process.env.NODE_OPTIONS = options;
      let emitted = 0;
      await assert.rejects(runExhaustive(root, {execArgv: [], emit: () => emitted++}), /inherited NODE_OPTIONS/);
      assert.equal(emitted, 0);
    }
  } finally { if (before === undefined) delete process.env.NODE_OPTIONS; else process.env.NODE_OPTIONS = before; }
});

test('direct execution flags cannot override test selection, reporting or the selected entry', () => {
  for (const argv of [['--test-name-pattern=none'], ['--test-only'], ['--test-shard=1/2'],
    ['--test-reporter=tap'], ['--eval', ''], ['other-entry.mjs'], ['--experimental-config-file=a.json'],
    ['--import'], ['--import', '']]) assert.throws(() => qualifyExhaustiveLaunch(argv, {}));
  assert.deepEqual(qualifyExhaustiveLaunch(['--import=tsx'], {}).execArgv, ['--import=tsx']);
});

test('zero authored cases cannot pass on the native file-wrapper synthetic success', async t => {
  for (const source of ['// no cases', "import test from 'node:test';"]) {
    const root = fixture(t, {'a.test.mjs': source});
    const result = await runExhaustive(root, {execArgv: [], emit: () => {}});
    assert.equal(result.pass, false); assert.equal(result.files[0].status, 0);
    assert.equal(result.files[0].actual_case_events, 0);
  }
});

test('validated launch environment is fixed across entries and does not strip benign preloads', async t => {
  const root = fixture(t, {'a.test.mjs': positive, 'z.test.mjs': positive}), before = process.env.NODE_OPTIONS;
  try {
    process.env.NODE_OPTIONS = '--no-warnings';
    const result = await runExhaustive(root, {execArgv: [], emit: event => {
      if (event.type === 'exhaustive:file') process.env.NODE_OPTIONS = '--test-name-pattern=never';
    }});
    assert.equal(result.pass, true); assert.equal(result.completed_files, 2);
    assert.ok(result.files.every(r => r.entry_summary.counts.tests === 1 && r.actual_case_events === 1));
    assert.equal(result.launch.selection_posture, 'unfiltered-entrypoints-and-cases');
  } finally { if (before === undefined) delete process.env.NODE_OPTIONS; else process.env.NODE_OPTIONS = before; }
});

test('actual nested cases/suites reconcile native IDs, parentage and global/local counts', async t => {
  const source="import test from 'node:test';import{describe,it}from 'node:test';test('parent',async t=>{await t.test('child',()=>{});});describe('suite',()=>{it('leaf',()=>{});});";
  const root=fixture(t,{'a.test.mjs':source});
  const result=await runExhaustive(root,{execArgv:[],emit:()=>{}});
  assert.equal(result.pass,true);
  const ledger=result.files[0].native_case_ledger;
  assert.equal(ledger.complete,true);assert.equal(ledger.case_count,3);
  assert.equal(ledger.native_cases.length,4);assert.equal(new Set(ledger.native_cases.map(r=>r.native_case_id)).size,4);
  assert.equal(ledger.native_cases.filter(r=>r.nesting===1).length,2);
  assert.equal(result.files[0].entry_summary.counts.tests,ledger.case_count);
});

test('missing, duplicate, conflicting and mis-parented DATA events cannot qualify a ledger',()=>{
  const entry='/owned/test/a.test.mjs';
  const declaration={type:'test:enqueue',data:{entryFile:entry,file:entry,line:1,column:2,name:'case',type:'test',testId:1,parentId:0,nesting:0}};
  const terminal={type:'test:pass',data:{entryFile:entry,file:entry,line:1,column:2,name:'case',details:{type:'test'},testId:1,parentId:0,nesting:0,testNumber:1}};
  const counts={tests:1,suites:0,topLevel:1,passed:1,failed:0,cancelled:0,skipped:0,todo:0};
  const entrySummary={type:'test:summary',data:{entryFile:entry,file:entry,success:true,counts}};
  const rootSummary={type:'test:summary',data:{success:true,counts}};
  const base=[declaration,terminal,entrySummary,rootSummary];
  const run=events=>{const ledger=createNativeCaseLedger(entry);for(const event of events)ledger.observe(event);return ledger.finish();};
  assert.equal(run(base).complete,true);
  for(const events of [
    [declaration,entrySummary,rootSummary],
    [declaration,terminal,terminal,entrySummary,rootSummary],
    [terminal,entrySummary,rootSummary],
    [declaration,{...terminal,data:{...terminal.data,parentId:9}},entrySummary,rootSummary],
    [declaration,{...terminal,data:{...terminal.data,name:'other'}},entrySummary,rootSummary],
    [{...declaration,data:{...declaration.data,parentId:9,nesting:1}},terminal,entrySummary,rootSummary],
    [declaration,terminal,{...entrySummary,data:{...entrySummary.data,counts:{...counts,tests:2}}},rootSummary],
    [declaration,terminal,entrySummary,{...rootSummary,data:{...rootSummary.data,counts:{...counts,passed:2}}}],
    [declaration,terminal,entrySummary],
    [declaration,terminal,entrySummary,rootSummary,{...declaration,data:{...declaration.data,testId:2}}]
  ]){const result=run(events);assert.equal(result.complete,false);assert.ok(result.errors.length>0);}
});

// Open Questions: exhaustive-tests.mjs. Inert controls are not the full native run.
