import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {runData} from './meta-types/data.mjs';
import {runDecisions} from './meta-types/decisions.mjs';
import {runBehavior} from './meta-types/behavior.mjs';

const exampleRoot = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(exampleRoot, '../..');
const cli = path.join(packageRoot, 'dist/cli/main.js');
const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--help') {
  console.log('Usage: node test-meta-types.mjs --output <new-absolute-directory>\nRequires consumer dependencies typescript@6.0.3 and @types/node@26.4.0. Runs local generated functions; no server or provider required.');
  process.exit(0);
}
if (args.length !== 2 || args[0] !== '--output' || !path.isAbsolute(args[1])) throw Error('Expected --output <new-absolute-directory>');
const output = args[1];
assert.equal(fs.existsSync(output), false, 'output must be absent');
assert.ok(fs.statSync(path.dirname(output)).isDirectory(), 'output parent must exist');
const tsPackage = require.resolve('typescript/package.json');
const tsc = path.join(path.dirname(tsPackage), 'bin/tsc');
const nodeTypesPackage = require.resolve('@types/node/package.json');
assert.equal(JSON.parse(fs.readFileSync(tsPackage)).version, '6.0.3', 'exact consumer compiler required');
assert.equal(JSON.parse(fs.readFileSync(nodeTypesPackage)).version, '26.4.0', 'exact consumer Node types required');
fs.mkdirSync(output, {mode:0o700});
const write = (relative, value) => fs.writeFileSync(path.join(output, relative), JSON.stringify(value,null,2)+'\n', {flag:'wx'});
write('package.json', {type:'module'});
const source = path.join(output, 'source');
fs.cpSync(path.join(exampleRoot, 'source'), source, {recursive:true});
const selection = path.join(exampleRoot, 'selections/typescript.json');
const observations = [];
function command(name, executable, argv, expectedSuccess = true) {
  const result = spawnSync(executable, argv, {cwd:output, encoding:'utf8', maxBuffer:32*1024*1024});
  write(name+'.json', {executable, arguments:argv, status:result.status, stdout:result.stdout, stderr:result.stderr});
  assert.equal(typeof result.status,'number', `${name} must execute, not fail to spawn`);
  if (expectedSuccess) assert.equal(result.status,0, `${name}: ${result.stderr || result.stdout}`);
  else {
    assert.notEqual(result.status,0, `${name} must reject`);
    const diagnostic = JSON.parse(result.stderr || result.stdout);
    assert.equal(diagnostic.result,'fail');
    if (diagnostic.code) observations.push({id:name+'-diagnostic',result:'pass',code:diagnostic.code,pointer:diagnostic.pointer});
    else {
      assert.equal(diagnostic.schema_version,'domainspec.reconciled-output-verification/v1-candidate');
      assert.ok(diagnostic.checks.some(c=>c.result==='fail'),'verification must identify a failed check');
      observations.push({id:name+'-diagnostic',result:'pass',failed_checks:diagnostic.checks.filter(c=>c.result==='fail')});
    }
  }
  observations.push({id:name,result:'pass',expected:expectedSuccess?'success':'rejection',exit_code:result.status});
  return result;
}
function build(name) {
  const target = path.join(output,name);
  command(name+'-build',process.execPath,[cli,'build',source,'--language','typescript','--target-root',target,'--compilation-selection',selection]);
  command(name+'-verify',process.execPath,[cli,'verify',source,'--language','typescript','--target-root',target,'--compilation-selection',selection]);
  const compiled = path.join(output,name+'-js');
  const config = {compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',types:['node'],typeRoots:[path.dirname(path.dirname(nodeTypesPackage))],rootDir:target,outDir:compiled},include:[target+'/**/*.ts']};
  write(name+'-tsconfig.json', config);
  command(name+'-compile',process.execPath,[tsc,'--project',path.join(output,name+'-tsconfig.json')]);
  return {target,compiled};
}
const first = build('generated-1');
const noOverwrite = command('existing-target-rejects',process.execPath,[cli,'build',source,'--language','typescript','--target-root',first.target,'--compilation-selection',selection],false);
assert.equal(JSON.parse(noOverwrite.stderr).code,'DS_RECONCILED_OUTPUT_EXISTS');
for (const [name,nodeId,mutate,expectedCode] of [
  ['unsupported-rule','allowed',n=>{n.body.typed_contract.expression.op='power';},'MTCLI_TYPED_RULE'],
  ['optional-query-limit','find-optional',n=>{n.body.typed_contract.limit=1;},'MTCLI_BACKEND_QUERY'],
]) {
  const invalidSource=path.join(output,name+'-source');fs.cpSync(source,invalidSource,{recursive:true});
  const invalidNode=path.join(invalidSource,'specs/commerce/nodes/'+nodeId+'.json');const value=JSON.parse(fs.readFileSync(invalidNode));mutate(value);fs.writeFileSync(invalidNode,JSON.stringify(value,null,2)+'\n');
  const invalidTarget=path.join(output,name+'-target');
  const rejected=command(name+'-rejects',process.execPath,[cli,'build',invalidSource,'--language','typescript','--target-root',invalidTarget,'--compilation-selection',selection],false);
  assert.equal(JSON.parse(rejected.stderr).code,expectedCode);assert.equal(fs.existsSync(invalidTarget),false,'invalid compilation must not create target');
}
const calculationFile=path.join(first.target,'commerce-corpus/features/commerce/src/domain/calculations/total.ts');
const untampered=fs.readFileSync(calculationFile);fs.appendFileSync(calculationFile,'\n// caller tampering\n');
const tampered=command('tampered-target-rejects',process.execPath,[cli,'verify',source,'--language','typescript','--target-root',first.target,'--compilation-selection',selection],false);
assert.ok(JSON.parse(tampered.stdout).checks.some(c=>c.id==='artifact:commerce-corpus/features/commerce/src/domain/calculations/total.ts'&&c.result==='fail'));
fs.writeFileSync(calculationFile,untampered);
command('restored-target-verifies',process.execPath,[cli,'verify',source,'--language','typescript','--target-root',first.target,'--compilation-selection',selection]);
const witnesses = [await runData({generatedRoot:first.compiled,exampleRoot}),await runDecisions({generatedRoot:first.compiled,exampleRoot}),await runBehavior({generatedRoot:first.compiled,exampleRoot})];
for (let i=0;i<witnesses.length;i++) {assert.equal(witnesses[i].result,'pass');write('witness-'+i+'.json',witnesses[i]);}
const nodePath = path.join(source,'specs/commerce/nodes/total.json');
const node = JSON.parse(fs.readFileSync(nodePath));
assert.equal(node.body.typed_contract.expression.op,'subtract');
node.body.typed_contract.expression.op='add';
node.body.description='Add the reviewed gross and adjustment inputs in the edited user example.';
fs.writeFileSync(nodePath,JSON.stringify(node,null,2)+'\n');
const stale=command('edited-source-old-target-rejects',process.execPath,[cli,'verify',source,'--language','typescript','--target-root',first.target,'--compilation-selection',selection],false);
assert.ok(JSON.parse(stale.stdout).checks.some(c=>c.id==='receipt-current'&&c.result==='fail'));
const second = build('generated-2');
const {calculateTotal} = await import(pathToFileURL(path.join(second.compiled,'commerce-corpus/features/commerce/src/domain/calculations/total.js')).href);
assert.equal(calculateTotal({gross:'100',adjustment:'7'}),107n);
const summary = {schema_version:'domainspec.meta-types-user-journey/v1-candidate',result:'pass',profile:'domainspec.reconciled-typescript/v1-candidate',meta_types:['Entity','Value Object','Enum','Rule','Calculation','Mapping','Query','Policy','Interface','Event','State Machine','Operation','Workflow'],witnesses,observations,edit:{before:'93',after:'107',old_target_rejected:true},tools:{node:process.version,typescript:'6.0.3',node_types:'26.4.0'},runtime_scope:'local generated functions with explicit mock bindings; no hosting, remote transport or durable recovery qualification',authority_effect:'none'};
write('summary.json',summary);
console.log(JSON.stringify(summary,null,2));
