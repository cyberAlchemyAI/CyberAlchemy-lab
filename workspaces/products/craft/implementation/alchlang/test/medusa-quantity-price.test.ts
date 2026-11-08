import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const extension = new URL('../../extensions/medusa-quantity-price-v1/', import.meta.url);
const fixtures: unknown = JSON.parse(readFileSync(new URL('fixtures.json', extension), 'utf8'));
assert.ok(Array.isArray(fixtures));
assert.equal(fixtures.length, 20, 'fixture changes require a reviewed coverage update');
const observedFixtureNames = fixtures.map((fixture: {name: unknown}) => {
  assert.equal(typeof fixture.name, 'string');
  return fixture.name as string;
});
const fixtureNames = [
  'quantity_15', 'quantity_1', 'quantity_9', 'quantity_10', 'quantity_19',
  'quantity_20', 'quantity_21', 'cheaper_default', 'max_only', 'outside_max',
  'empty', 'no_currency', 'decimal', 'zero', 'beyond_safe_number',
  'uint64_max', 'overlap', 'tie', 'deleted', 'max_quantity',
];
function verifyFixtureNames(names: unknown) {
  assert.deepEqual(names, fixtureNames, 'fixture names require a reviewed coverage update');
}
verifyFixtureNames(observedFixtureNames);
const expectedNames = [
  'generated DomainSpec application quotes every quantity-price fixture',
  ...fixtureNames,
  'USD conversion is exact, bounded and refuses rounding or binary float input',
  'adapter rejects unsupported or malformed requests and price snapshots',
];
const expectedSummary = {tests: 23, suites: 0, pass: 23, fail: 0, cancelled: 0, skipped: 0, todo: 0};

function verifyChildCoverage(stdout: string, stderr: string) {
  assert.doesNotMatch(stdout + stderr, /node:test run\(\) is being called recursively|skipping running files/);
  const rows = [...stdout.matchAll(/^# (tests|suites|pass|fail|cancelled|skipped|todo) (\d+)$/gm)];
  assert.equal(rows.length, 7, 'require exactly one complete terminal TAP summary');
  assert.equal(new Set(rows.map(row => row[1])).size, 7, 'reject duplicate summary keys');
  assert.deepEqual(Object.fromEntries(rows.map(row => [row[1], Number(row[2])])), expectedSummary);
  assert.deepEqual([...stdout.matchAll(/^\s*# Subtest: (.*)$/gm)].map(row => row[1]), expectedNames);
  assert.equal([...stdout.matchAll(/^\s*ok \d+ - .+$/gm)].length, 23, 'require actual passing TAP results');
  assert.doesNotMatch(stdout, /^\s*not ok \d+|^\s*(?:not )?ok \d+.*#\s*(?:SKIP|TODO)\b/im);
}

// The local regression suite needs no Medusa install, Docker, or network.
// The separate oracle command exercises the actual pinned Medusa repository.
test('Medusa quantity-price generated application and exact USD boundary', () => {
  // Inheriting this marker makes a nested Node test runner skip its test files.
  // Preserve every other environment setting so real child failures stay visible.
  const env = {...process.env};
  delete env.NODE_TEST_CONTEXT;
  const child = spawnSync(process.execPath,
    ['--test', '--test-reporter=tap', fileURLToPath(new URL('module.test.mjs', extension))],
    {encoding: 'utf8', env, timeout: 120_000, maxBuffer: 4 * 1024 * 1024});
  assert.ifError(child.error);
  assert.equal(child.signal, null, child.stderr);
  assert.equal(child.status, 0, child.stdout + child.stderr);
  verifyChildCoverage(child.stdout, child.stderr);

  // Separating controls mutate the just-observed positive child output.
  for (const names of [
    ['substituted fixture', ...fixtureNames.slice(1)],
    [...fixtureNames].reverse(),
    [fixtureNames[1], ...fixtureNames.slice(1)],
  ]) assert.throws(() => verifyFixtureNames(names), {name: 'AssertionError'});
  const mutations: Array<[string, string, string]> = [
    ['empty output', '', ''],
    ['recursive skip', child.stdout, 'node:test run() is being called recursively within a test file. skipping running files.'],
    ['missing summary', child.stdout.replace(/^# tests .*\n/m, ''), child.stderr],
    ['duplicate summary', child.stdout + '# tests 23\n', child.stderr],
    ['missing fixture', child.stdout.replace(`    # Subtest: ${fixtureNames[0]}\n`, ''), child.stderr],
    ['substituted fixture', child.stdout.replace(`# Subtest: ${fixtureNames[0]}\n`, '# Subtest: unexpected fixture\n'), child.stderr],
    ['extra fixture', child.stdout + '# Subtest: unexpected fixture\n', child.stderr],
    ['missing parent', child.stdout.replace(`# Subtest: ${expectedNames[0]}\n`, ''), child.stderr],
    ['missing passing result', child.stdout.replace(/^\s*ok \d+ - .+\n/m, ''), child.stderr],
    ['failing result', child.stdout.replace(/^(\s*)ok (\d+ - .+)$/m, '$1not ok $2'), child.stderr],
    ['skipped result', child.stdout.replace(/^(\s*ok \d+ - .+)$/m, '$1 # SKIP'), child.stderr],
    ['todo result', child.stdout.replace(/^(\s*ok \d+ - .+)$/m, '$1 # TODO'), child.stderr],
    ...Object.keys(expectedSummary).map(key => [
      `wrong ${key}`, child.stdout.replace(new RegExp(`^# ${key} \\d+$`, 'm'), `# ${key} ${key === 'tests' || key === 'pass' ? 0 : 1}`), child.stderr,
    ] as [string, string, string]),
  ];
  for (const [name, stdout, stderr] of mutations) {
    assert.throws(() => verifyChildCoverage(stdout, stderr), {name: 'AssertionError'}, name);
  }
});
