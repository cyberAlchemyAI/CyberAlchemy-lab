import assert from 'node:assert/strict';
import {execFileSync, spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {domainSpecRoot} from '../helpers/reconciled-commerce-corpus.ts';
import {nodeExecutable, npmCli, repositoryToolchain, typeScriptToolchain} from '../helpers/local-toolchain.ts';

const node = nodeExecutable();
const npm = npmCli();
const {compiler: tsc, typeRoots} = typeScriptToolchain();
const python = '/usr/bin/python3';
const cargo = repositoryToolchain();
const reconciliationRoot = path.join(domainSpecRoot, 'development/reconciliation-v1/profile-compiler-reconciliation');
const evidenceRoot = path.join(reconciliationRoot, 'evidence/r16-installation-package');

function workspace(t: test.TestContext): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'domainspec-r17-installed-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  return root;
}

function run(file: string, args: readonly string[], cwd: string, environment: NodeJS.ProcessEnv = {}): string {
  return execFileSync(file, [...args], {
    cwd,
    encoding: 'utf8',
    env: {...process.env, npm_config_audit: 'false', npm_config_fund: 'false', npm_config_update_notifier: 'false', ...environment},
  });
}

function sourceFiles(root: string, extension: string): string[] {
  const files: string[] = [];
  const visit = (folder: string) => {
    for (const entry of fs.readdirSync(folder, {withFileTypes: true}).sort((left, right) => left.name.localeCompare(right.name))) {
      const candidate = path.join(folder, entry.name);
      if (entry.isDirectory()) visit(candidate);
      else if (candidate.endsWith(extension)) files.push(candidate);
    }
  };
  visit(root);
  return files;
}

test('R17 installed guide and example build, verify, compile and execute in every selected language', t => {
  const manifest = JSON.parse(fs.readFileSync(path.join(evidenceRoot, 'manifest.json'), 'utf8'));
  const tarball = path.join(evidenceRoot, manifest.package.filename);
  const root = workspace(t), consumer = path.join(root, 'consumer');
  fs.mkdirSync(consumer);
  fs.writeFileSync(path.join(consumer, 'package.json'), '{"private":true,"type":"module"}\n');
  const userConfig = path.join(root, 'npm-user.conf'), globalConfig = path.join(root, 'npm-global.conf');
  fs.writeFileSync(userConfig, ''); fs.writeFileSync(globalConfig, '');
  run(node, [npm, 'install', '--offline', '--ignore-scripts', '--no-audit', '--no-fund', tarball], consumer, {
    npm_config_cache: path.join(root, 'npm-cache'), npm_config_userconfig: userConfig, npm_config_globalconfig: globalConfig,
  });

  const packageRoot = path.join(consumer, 'node_modules/@domainspec-v2/cli');
  const exampleRoot = path.join(packageRoot, 'examples/reconciled-commerce');
  const sourceRoot = path.join(exampleRoot, 'source');
  const executable = path.join(consumer, 'node_modules/.bin/domainspec-v2');
  const help = run(executable, ['--help'], consumer);
  for (const phrase of ['TypeScript, Python, or Rust', 'verify-project', 'domainspec.application-layout/v1']) assert.match(help, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.doesNotMatch(help, /TypeScript only|do not yet/i);
  const guide = fs.readFileSync(path.join(packageRoot, 'USER-GUIDE.md'), 'utf8');
  for (const pattern of [/compilation-selection/, /Strong native verification/, /all 13 DomainSpec meta\s+types/, /authority_effect/]) assert.match(guide, pattern);
  assert.doesNotMatch(guide, /Open Questions|\.\.\/\.\.\/development/);

  const graph = JSON.parse(run(node, ['--input-type=module', '-e', "import {loadCompiledProjectGraph} from '@domainspec-v2/cli'; const graph=loadCompiledProjectGraph(process.argv[1]); console.log(JSON.stringify({nodes:graph.nodes.length,relationships:graph.relationships.length,kinds:new Set(graph.nodes.map(row=>row.kind)).size}));", sourceRoot], consumer));
  assert.deepEqual(graph, {nodes: 21, relationships: 14, kinds: 13});

  const targets: Record<string, string> = {};
  for (const language of ['typescript', 'python', 'rust']) {
    const target = path.join(root, language), selection = path.join(exampleRoot, 'selections', `${language}.json`);
    targets[language] = target;
    const build = JSON.parse(run(executable, ['build', sourceRoot, '--language', language, '--target-root', target, '--compilation-selection', selection], consumer));
    assert.equal(build.result, 'pass', language);
    const verification = JSON.parse(run(executable, ['verify', sourceRoot, '--language', language, '--target-root', target, '--compilation-selection', selection], consumer));
    assert.equal(verification.result, 'pass', language);
  }

  const generatedTypeScript = path.join(targets.typescript, 'commerce-corpus/features/commerce/src/domain/calculations/total.ts');
  const original = fs.readFileSync(generatedTypeScript);
  const changed = Buffer.concat([original, Buffer.from('\n')]);
  fs.writeFileSync(generatedTypeScript, changed);
  const drift = spawnSync(executable, ['verify', sourceRoot, '--language', 'typescript', '--target-root', targets.typescript, '--compilation-selection', path.join(exampleRoot, 'selections/typescript.json')], {cwd: consumer, encoding: 'utf8'});
  assert.equal(drift.status, 1);
  assert.equal(fs.readFileSync(generatedTypeScript).equals(changed), true, 'verification must not repair caller output');
  fs.writeFileSync(generatedTypeScript, original);

  const tsHarness = path.join(targets.typescript, 'installed-acceptance.ts');
  fs.writeFileSync(tsHarness, [
    "import {calculateTotal as netTotal} from './commerce-corpus/features/commerce/src/domain/calculations/total.js';",
    "import {calculateTotal as feeTotal} from './commerce-corpus/features/billing/src/domain/calculations/total.js';",
    "const net=netTotal({gross:'100',adjustment:'7'});",
    "const fee=feeTotal({gross:'2',adjustment:'3'});",
    "if(net!==93n||fee!==5n)throw new Error('generated TypeScript calculation mismatch');",
    "console.log(JSON.stringify({language:'typescript',net:String(net),fee:String(fee)}));",
    '',
  ].join('\n'));
  fs.writeFileSync(path.join(targets.typescript, 'package.json'), '{"type":"module"}\n');
  const tsDist = path.join(root, 'typescript-dist');
  run(node, [tsc, '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', typeRoots, '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', targets.typescript, '--outDir', tsDist, ...sourceFiles(targets.typescript, '.ts')], consumer);
  assert.deepEqual(JSON.parse(run(node, [path.join(tsDist, 'installed-acceptance.js')], consumer)), {language: 'typescript', net: '93', fee: '5'});

  run(python, ['-I', '-S', '-B', '-m', 'compileall', '-q', path.join(targets.python, 'commerce_corpus')], consumer);
  const pythonProgram = [
    'import json,sys',
    'sys.path.insert(0, sys.argv[1])',
    'from commerce_corpus.features.commerce.src.domain.calculations.total import calculate_total as net_total',
    'from commerce_corpus.features.billing.src.domain.calculations.total import calculate_total as fee_total',
    'net=net_total({"gross":"100","adjustment":"7"})',
    'fee=fee_total({"gross":"2","adjustment":"3"})',
    'assert (net,fee)==(93,5)',
    'print(json.dumps({"language":"python","net":net,"fee":fee},separators=(",",":")))',
  ].join(';');
  assert.deepEqual(JSON.parse(run(python, ['-I', '-S', '-B', '-c', pythonProgram, targets.python], consumer)), {language: 'python', net: 93, fee: 5});

  const crate = path.join(targets.rust, 'commerce-corpus');
  const rustHarness = path.join(crate, 'src/bin/installed_acceptance.rs');
  fs.mkdirSync(path.dirname(rustHarness), {recursive: true});
  fs.writeFileSync(rustHarness, [
    'use r13_commerce_candidate as ds;',
    'fn main() {',
    '  let net = ds::domain::calculations::f8_commerce_n5_total::total(&100, &7).unwrap();',
    '  let fee = ds::domain::calculations::f7_billing_n5_total::total(&2, &3).unwrap();',
    '  assert_eq!((net, fee), (93, 5));',
    '  println!("{{\\"language\\":\\"rust\\",\\"net\\":{},\\"fee\\":{}}}", net, fee);',
    '}',
    '',
  ].join('\n'));
  const rustResult = JSON.parse(run(cargo, ['cargo', 'run', '--offline', '--locked', '--quiet', '--bin', 'installed_acceptance'], crate, {CARGO_TARGET_DIR: path.join(root, 'cargo-target')}));
  assert.deepEqual(rustResult, {language: 'rust', net: 93, fee: 5});
});
