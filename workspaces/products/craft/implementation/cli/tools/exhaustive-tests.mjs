import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const identityKeys = ['dev', 'ino', 'mode', 'uid', 'gid', 'nlink', 'size', 'mtimeNs', 'ctimeNs'];
const sameIdentity = (a, b) => identityKeys.every(k => a[k] === b[k]);
const reporter = fileURLToPath(new URL('./test-events-reporter.mjs', import.meta.url));
const cliRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Match Node 26's NODE_OPTIONS space/double-quote/inside-quote escape grammar,
// rather than shell parsing. Preserve admitted preloads; never silently strip them.
export function parseNodeOptions(value) {
  assert.equal(typeof value, 'string');
  assert.ok(value.length <= 65536 && !value.includes('\0'), 'invalid NODE_OPTIONS');
  const args = []; let quoted = false, newArgument = true;
  for (let i = 0; i < value.length; i++) {
    let c = value[i];
    if (c === '\\' && quoted) { assert.ok(i + 1 < value.length, 'invalid NODE_OPTIONS escape'); c = value[++i]; }
    else if (c === ' ' && !quoted) { newArgument = true; continue; }
    else if (c === '"') { quoted = !quoted; continue; }
    if (newArgument) { args.push(c); newArgument = false; } else args[args.length - 1] += c;
  }
  assert.equal(quoted, false, 'unterminated NODE_OPTIONS quote');
  return args;
}

export function qualifyExhaustiveLaunch(execArgv, env) {
  assert.ok(Array.isArray(execArgv) && execArgv.length <= 64);
  for (let i = 0; i < execArgv.length; i++) {
    const flag = execArgv[i];
    assert.ok(typeof flag === 'string' && flag.length <= 65536 && !flag.includes('\0'));
    if (flag === '--import' || flag === '--require' || flag === '-r') {
      const value = execArgv[++i];
      assert.ok(typeof value === 'string' && value.length > 0 && value.length <= 65536 && !value.includes('\0'), 'preload requires a value');
    } else {
      assert.ok(/^--(?:import|require)=.+$/.test(flag), 'exhaustive launch permits preloads only, not test filters or alternate execution');
    }
  }
  for (const token of parseNodeOptions(env.NODE_OPTIONS ?? '')) {
    const name = token.split('=', 1)[0].replaceAll('_', '-');
    assert.ok(!/^--(?:no-)?test(?:-|$)/.test(name) && !/^--(?:no-)?watch(?:-|$)/.test(name)
      && !name.includes('config-file') && !/^--env-file(?:-|$)/.test(name),
    'inherited NODE_OPTIONS cannot change exhaustive selection or load indirect configuration');
  }
  const launchEnv = {...env}; delete launchEnv.NODE_TEST_CONTEXT;
  const argv = [...execArgv];
  return {env: launchEnv, execArgv: argv, launch: {
    node: {version: process.version, executable: process.execPath},
    exec_argv_sha256: sha(JSON.stringify(argv)), node_options_sha256: sha(launchEnv.NODE_OPTIONS ?? ''),
    runner_sha256: sha(fs.readFileSync(fileURLToPath(import.meta.url))), reporter_sha256: sha(fs.readFileSync(reporter)),
    selection_posture: 'unfiltered-entrypoints-and-cases', full_runtime_custody_qualified: false
  }};
}

export function discoverTests(root = cliRoot) {
  root = path.resolve(root);
  assert.equal(fs.realpathSync(root), root, 'canonical test root required');
  const rows = [];
  function walk(directory) {
    const st = fs.lstatSync(directory);
    assert.ok(st.isDirectory() && !st.isSymbolicLink(), 'test directories cannot be symlinks');
    for (const name of fs.readdirSync(directory).sort()) {
      const absolute = path.join(directory, name), before = fs.lstatSync(absolute, {bigint: true});
      assert.ok(!before.isSymbolicLink(), 'test tree cannot contain symlinks: ' + absolute);
      if (before.isDirectory()) { walk(absolute); continue; }
      if (!/\.test\.(ts|mjs)$/.test(name)) continue;
      assert.ok(before.isFile(), 'test entry must be regular');
      const fd = fs.openSync(absolute, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
      let bytes;
      try {
        assert.ok(sameIdentity(before, fs.fstatSync(fd, {bigint: true})), 'test changed at open');
        bytes = fs.readFileSync(fd);
        assert.ok(sameIdentity(before, fs.fstatSync(fd, {bigint: true})), 'test changed during read');
      } finally { fs.closeSync(fd); }
      assert.ok(sameIdentity(before, fs.lstatSync(absolute, {bigint: true})), 'test changed after read');
      rows.push({file: path.relative(root, absolute).split(path.sep).join('/'), sha256: sha(bytes), bytes: bytes.length});
    }
  }
  walk(path.join(root, 'test'));
  rows.sort((a, b) => a.file < b.file ? -1 : a.file > b.file ? 1 : 0);
  assert.ok(rows.length > 0, 'empty test selection refused');
  assert.equal(new Set(rows.map(r => r.file)).size, rows.length);
  return {schema_version: 'domainspec.exhaustive-test-inventory/v1', root, count: rows.length,
    test_epoch: sha(JSON.stringify(rows)), files: rows};
}

export function assertInventoryUnchanged(before, after) {
  assert.equal(after.root, before.root);
  assert.equal(after.test_epoch, before.test_epoch, 'test epoch changed (added, removed, or modified entry)');
  assert.deepEqual(after.files, before.files);
}

// Native case identity is independent of transport event sequence/testNumber.
// Node's file-wrapper events have no entryFile and are not authored cases.
export function createNativeCaseLedger(absoluteEntry) {
  const declared = new Map(), terminals = new Map(), errors = [];
  let entrySummary = null, rootSummary = null;
  const problem = message => { if (errors.length < 16) errors.push(message); };
  function metadata(data, kind) {
    assert.ok(Number.isSafeInteger(data.testId) && data.testId > 0, 'invalid native case ID');
    assert.ok(Number.isSafeInteger(data.parentId) && data.parentId >= 0, 'invalid native parent ID');
    assert.ok(Number.isSafeInteger(data.nesting) && data.nesting >= 0, 'invalid native nesting');
    assert.ok(kind === 'test' || kind === 'suite', 'invalid native case kind');
    assert.ok(typeof data.file === 'string' && data.file.length <= 4096, 'invalid native source file');
    assert.equal(typeof data.name, 'string');
    return {test_id: data.testId, parent_id: data.parentId, nesting: data.nesting, kind,
      file: data.file, line: data.line ?? null, column: data.column ?? null, name_sha256: sha(data.name)};
  }
  return {
    failed() { return errors.length > 0; },
    observe(event) {
      try {
        const data = event.data;
        if (event.type === 'test:summary') {
          if (data.entryFile !== undefined) {
            assert.equal(data.entryFile, absoluteEntry, 'foreign summary entry');
            assert.equal(data.file, absoluteEntry, 'foreign summary source');
            assert.equal(entrySummary, null, 'duplicate entry summary'); entrySummary = structuredClone(data);
          } else { assert.equal(rootSummary, null, 'duplicate root summary'); rootSummary = structuredClone(data); }
          return;
        }
        if (data.entryFile === undefined || !['test:enqueue', 'test:pass', 'test:fail'].includes(event.type)) return;
        assert.equal(data.entryFile, absoluteEntry, 'foreign native case entry');
        const row = metadata(data, event.type === 'test:enqueue' ? data.type : data.details?.type);
        if (event.type === 'test:enqueue') {
          assert.ok(!declared.has(row.test_id), 'duplicate native declaration');
          assert.ok(declared.size < 65536, 'bounded native case ledger exceeded');
          assert.ok(!entrySummary && !rootSummary, 'declaration after summary');
          if (row.parent_id === 0) assert.equal(row.nesting, 0, 'root nesting mismatch');
          else {
            const parent = declared.get(row.parent_id); assert.ok(parent, 'unknown native parent');
            assert.equal(row.nesting, parent.nesting + 1, 'native parent/nesting mismatch');
            assert.ok(!terminals.has(row.parent_id), 'child declared after parent completion');
          }
          declared.set(row.test_id, row);
        } else {
          assert.deepEqual(row, declared.get(row.test_id), 'terminal identity differs from native declaration');
          assert.ok(!terminals.has(row.test_id), 'duplicate native terminal');
          assert.ok(!entrySummary && !rootSummary, 'terminal after summary');
          assert.ok(Number.isSafeInteger(data.testNumber) && data.testNumber > 0, 'invalid local test number');
          terminals.set(row.test_id, {native_case_id: row.test_id, parent_id: row.parent_id, nesting: row.nesting,
            kind: row.kind, outcome: event.type === 'test:pass' ? 'pass' : 'fail', skipped: Boolean(data.skip), todo: Boolean(data.todo)});
        }
      } catch (error) { problem(error.message); }
    },
    finish() {
      const completed = [...terminals.values()], cases = completed.filter(r => r.kind === 'test');
      const expected = {tests: cases.length, suites: completed.length - cases.length,
        topLevel: completed.filter(r => r.parent_id === 0).length,
        passed: cases.filter(r => !r.skipped && !r.todo && r.outcome === 'pass').length,
        skipped: cases.filter(r => r.skipped).length, todo: cases.filter(r => !r.skipped && r.todo).length,
        failed_or_cancelled: cases.filter(r => !r.skipped && !r.todo && r.outcome === 'fail').length};
      try {
        assert.equal(declared.size, terminals.size, 'missing native terminal events');
        assert.ok(entrySummary && rootSummary, 'missing entry/root summary');
        assert.ok(cases.length > 0, 'no authored native cases');
        for (const summary of [entrySummary, rootSummary]) {
          assert.equal(typeof summary.success, 'boolean');
          for (const key of ['tests', 'suites', 'topLevel', 'passed', 'failed', 'cancelled', 'skipped', 'todo']) {
            assert.ok(Number.isSafeInteger(summary.counts?.[key]) && summary.counts[key] >= 0, 'invalid summary counter');
          }
          for (const key of ['tests', 'suites', 'topLevel', 'passed', 'skipped', 'todo']) {
            assert.equal(summary.counts[key], expected[key], 'native ledger/summary counter mismatch: ' + key);
          }
          assert.equal(summary.counts.failed + summary.counts.cancelled, expected.failed_or_cancelled, 'native failed/cancelled count mismatch');
          const success = completed.every(r => r.todo || r.skipped || r.outcome === 'pass');
          assert.equal(summary.success, success, 'native summary/outcome success mismatch');
        }
        assert.deepEqual(rootSummary.counts, entrySummary.counts, 'root/entry summary mismatch');
        assert.equal(rootSummary.success, entrySummary.success, 'root/entry success mismatch');
      } catch (error) { problem(error.message); }
      return {schema_version: 'domainspec.native-case-ledger/v1', complete: errors.length === 0,
        errors: [...errors], declared_cases_and_suites: declared.size, completed_cases_and_suites: terminals.size,
        case_count: cases.length, native_cases: completed};
    }
  };
}

// Executes original files unchanged, once each, serially. The enclosing qualified
// native harness still owns containment, provider admission and descendant effects.
// This runner's child process-group closure does not attest Docker/resource closure.
export async function runExhaustive(root = cliRoot, {emit = event => process.stdout.write(JSON.stringify(event) + '\n'),
  execArgv = ['--import', 'tsx'], signal, fileTimeoutMs = 300000} = {}) {
  assert.ok(Number.isSafeInteger(fileTimeoutMs) && fileTimeoutMs > 0);
  const launch = qualifyExhaustiveLaunch(execArgv, process.env);
  const inventory = discoverTests(root), outcomes = [];
  let sourceError = null;
  emit({type: 'exhaustive:inventory', data: inventory});
  emit({type: 'exhaustive:launch', data: launch.launch});
  for (const row of inventory.files) {
    if (signal?.aborted) break;
    try { assertInventoryUnchanged(inventory, discoverTests(root)); }
    catch (error) { sourceError = error.message; break; }
    const entryFile = row.file;
    const result = await executeEntry(path.resolve(root), entryFile, inventory.test_epoch, {emit,
      execArgv: launch.execArgv, env: launch.env, signal, fileTimeoutMs});
    outcomes.push(result);
    emit({type: 'exhaustive:file', data: result});
    // Ordinary failed assertions do not filter out subsequent files. Cancellation,
    // transport/closure failure stops effects; omitted files are explicit below.
    if (!result.transport_complete) break;
  }
  let sourceUnchanged = false;
  try { assertInventoryUnchanged(inventory, discoverTests(root)); sourceUnchanged = sourceError === null; }
  catch (error) { sourceError ??= error.message; }
  const completed = new Set(outcomes.map(r => r.entry_file));
  const missing = inventory.files.filter(r => !completed.has(r.file)).map(r => r.file);
  const result = {schema_version: 'domainspec.exhaustive-test-result/v1', test_epoch: inventory.test_epoch,
    selected_files: inventory.count, completed_files: outcomes.length, missing_files: missing,
    source_unchanged: sourceUnchanged, source_error: sourceError, cancelled: signal?.aborted ?? false,
    launch: launch.launch, files: outcomes, pass: sourceUnchanged && !signal?.aborted && missing.length === 0 && outcomes.every(r => r.pass),
    full_beta_qualified: false, native_effect_closure_qualified: false};
  emit({type: 'exhaustive:result', data: result});
  return result;
}

function executeEntry(root, entryFile, epoch, {emit, execArgv, env, signal, fileTimeoutMs}) {
  return new Promise(resolve => {
    const args = [...execArgv, '--test', '--test-concurrency=1', '--test-reporter=' + reporter, entryFile];
    const child = spawn(process.execPath, args, {cwd: root, env, detached: true, stdio: ['ignore', 'pipe', 'pipe']});
    const absoluteEntry = path.join(root, entryFile);
    const ledger = createNativeCaseLedger(absoluteEntry);
    let sequence = 0, summary = null, entrySummary = null, actualCaseEvents = 0, skips = 0, todos = 0, failures = 0, error = null, pending = '',
      timedOut = false, cancelled = false, force = null, settled = false;
    const stop = reason => {
      if (settled) return;
      if (reason === 'timeout') timedOut = true;
      if (reason === 'cancel') cancelled = true;
      try { process.kill(-child.pid, 'SIGTERM'); } catch (e) { if (e.code !== 'ESRCH') error ??= e.message; }
      force ??= setTimeout(() => { try { process.kill(-child.pid, 'SIGKILL'); } catch (e) { if (e.code !== 'ESRCH') error ??= e.message; } }, 1000);
    };
    const timeout = setTimeout(() => stop('timeout'), fileTimeoutMs);
    const abort = () => stop('cancel'); signal?.addEventListener('abort', abort, {once: true});
    if (signal?.aborted) abort();
    const dispatch = line => {
      if (!line) return;
      try {
        assert.ok(Buffer.byteLength(line) <= 1048576, 'event exceeds 1 MiB');
        const event = JSON.parse(line);
        assert.equal(typeof event.type, 'string'); assert.ok(event.data && typeof event.data === 'object');
        // Retain the raw event before validation; transport corruption must not
        // erase the record that explains why later entry effects were stopped.
        emit({type: 'exhaustive:event', test_epoch: epoch, entry_file: entryFile, event_id: ++sequence, event});
        ledger.observe(event);
        assert.equal(ledger.failed(), false, 'invalid native case ledger protocol');
        if (event.type === 'test:summary') {
          if (event.data.entryFile !== undefined) {
            assert.equal(event.data.entryFile, absoluteEntry, 'summary has foreign entry identity');
            assert.equal(entrySummary, null, 'duplicate selected-entry summary');
            assert.equal(event.data.file, absoluteEntry, 'summary source must match selected entry');
            entrySummary = event.data;
          } else {
            assert.equal(summary, null, 'duplicate root summary'); summary = event.data;
          }
        }
        if (event.type === 'test:pass' || event.type === 'test:fail') {
          if (event.data.entryFile !== undefined) {
            assert.equal(event.data.entryFile, absoluteEntry, 'case has foreign entry identity');
            if (event.data.details?.type === 'test') actualCaseEvents++;
          }
          if (event.data.skip) skips++;
          if (event.data.todo) todos++;
          if (event.type === 'test:fail') failures++;
        }
        // Sequence is unique within this selected entrypoint, even when an imported
        // file reports cases with a different source file/testNumber.
      } catch (e) { error ??= e.message; stop('protocol'); }
    };
    child.stdout.setEncoding('utf8');
    child.stdout.on('data', chunk => {
      pending += chunk;
      let newline;
      while ((newline = pending.indexOf('\n')) >= 0) { dispatch(pending.slice(0, newline)); pending = pending.slice(newline + 1); }
      if (Buffer.byteLength(pending) > 1048576) { error ??= 'unterminated oversized event'; pending = ''; stop('protocol'); }
    });
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', text => emit({type: 'exhaustive:stderr', test_epoch: epoch, entry_file: entryFile, text}));
    child.on('error', e => { error ??= e.message; });
    child.on('close', async (status, exitSignal) => {
      settled = true; clearTimeout(timeout); if (force) clearTimeout(force);
      signal?.removeEventListener('abort', abort);
      if (pending) error ??= 'incomplete final event';
      let groupAbsent = child.pid === undefined;
      if (child.pid !== undefined) {
        try { process.kill(-child.pid, 0); } catch (e) { if (e.code === 'ESRCH') groupAbsent = true; else error ??= e.message; }
      }
      if (!groupAbsent && child.pid !== undefined) {
        error ??= 'owned process group survives child stdio closure';
        try { process.kill(-child.pid, 'SIGKILL'); } catch (e) { if (e.code !== 'ESRCH') error = e.message; }
        // Reap/observe only the process group created for this invocation. A
        // surviving/zombie group is a failed closure, never a successful run.
        for (let i = 0; i < 100 && !groupAbsent; i++) {
          await new Promise(r => setTimeout(r, 10));
          try { process.kill(-child.pid, 0); } catch (e) { if (e.code === 'ESRCH') groupAbsent = true; else { error = e.message; break; } }
        }
      }
      const caseLedger = ledger.finish();
      if (!caseLedger.complete) error ??= 'incomplete native case ledger';
      const transportComplete = error === null && !timedOut && !cancelled && exitSignal === null && groupAbsent;
      resolve({test_epoch: epoch, entry_file: entryFile, pid: child.pid ?? null, status, signal: exitSignal,
        timed_out: timedOut, cancelled, error, process_group_absent: groupAbsent, event_count: sequence,
        summary, entry_summary: entrySummary, actual_case_events: actualCaseEvents,
        native_case_ledger: caseLedger,
        skipped_cases: skips, todo_cases: todos, failed_events: failures, transport_complete: transportComplete,
        pass: transportComplete && caseLedger.complete && status === 0 && summary?.success === true && entrySummary?.success === true
          && Number.isSafeInteger(entrySummary?.counts?.tests) && entrySummary.counts.tests > 0
          && entrySummary.counts.failed === 0 && entrySummary.counts.cancelled === 0
          && entrySummary.counts.skipped === 0 && entrySummary.counts.todo === 0
          && actualCaseEvents > 0 && failures === 0 && skips === 0 && todos === 0});
    });
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    assert.equal(process.argv.length, 3, 'exactly --inventory or --run; subset/filter arguments refused');
    const option = process.argv[2];
    assert.ok(option === '--inventory' || option === '--run', 'unknown argument');
    if (option === '--inventory') console.log(JSON.stringify(discoverTests(), null, 2));
    else {
      const controller = new AbortController(), abort = () => controller.abort();
      process.on('SIGINT', abort); process.on('SIGTERM', abort);
      try { if (!(await runExhaustive(cliRoot, {signal: controller.signal})).pass) process.exitCode = 1; }
      finally { process.removeListener('SIGINT', abort); process.removeListener('SIGTERM', abort); }
    }
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}

// Open Questions: final full-corpus native admission, required Lean/terraform/provider
// prerequisites, independent controls review and nested-effect closure remain in
// goals/plans/domainspec-alchlang-review-repair/C4-FULL236-RUNNER.v1-candidate.md.
