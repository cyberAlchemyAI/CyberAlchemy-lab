/** Source-delegation qualification only; installed archive qualification belongs to R_PKG.
 * Open questions: goals/plans/craft-alchlang-generic-applications-2026-10-18-r5/DESIGN.md.
 */
import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, writeFileSync, symlinkSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../../../../../');
const core = path.join(repo, 'craft/projects/domainspec-v2/impl/cli');
const fixture = JSON.parse(readFileSync(path.join(core, '../system-integration/fixtures/external-api-composition-v2/payments-http.json'), 'utf8'));
const copy = () => structuredClone(fixture);

test('Alch delegates exact external contract references to the current real Core source API', async t => {
  const stage = mkdtempSync(path.join(tmpdir(), 'alch-api-source-delegation-'));
  t.after(() => rmSync(stage, {recursive:true, force:true}));
  const manifest = JSON.parse(readFileSync(path.join(core, 'package.json'), 'utf8'));
  manifest.exports['.'].import = './src/index.ts';
  writeFileSync(path.join(stage, 'package.json'), JSON.stringify(manifest));
  symlinkSync(path.join(core,'src'),path.join(stage,'src'),'dir');
  // The loader imports the actual public source API. No mock compiler/validator or stale dist.
  const compiler = await loadDomainSpecCompiler(stage);
  const valid = compiler.compileExternalApiComposition(copy());
  assert.equal(valid.runtime_calls_observed, false);
  const renamed=JSON.parse(JSON.stringify(fixture).replaceAll(fixture.external_api_contracts[0].contract_id,'contract:sample-directory'));
  renamed.external_api_contracts[0].operations[0].operation_id='publish-sample';
  renamed.external_api_bindings[0].contract_operation_ref='contract:sample-directory#publish-sample';
  assert.equal(compiler.compileExternalApiComposition(renamed).external_api_bindings[0].contract_operation_ref,'contract:sample-directory#publish-sample');
  const binding = fixture.external_api_bindings[0];
  const operation = fixture.external_api_contracts[0].operations[0].operation_id;
  const contract = binding.external_api_contract_ref;
  for (const ref of [`${contract.slice(0,-1)}X#${operation}`, `${contract}/${operation}`, `${contract}#missing`]) {
    const input = copy();input.external_api_bindings[0].contract_operation_ref=ref;
    assert.throws(()=>compiler.compileExternalApiComposition(input), {code:'API_REFERENCE_UNRESOLVED'});
  }
  const input=copy();const foreign=structuredClone(input.external_api_contracts[0]);
  foreign.contract_id='contract:other-gateway';foreign.operations[0].operation_id='foreign-operation';input.external_api_contracts.push(foreign);
  const failure=structuredClone(input.api_failure_mappings[0]);failure.mapping_id='api-failure-mapping:foreign';failure.external_api_contract_ref=foreign.contract_id;input.api_failure_mappings.push(failure);
  assert.equal(compiler.compileExternalApiComposition(input).runtime_calls_observed,false);
  input.external_api_bindings[0].failure_mapping_ref=failure.mapping_id;
  assert.throws(()=>compiler.compileExternalApiComposition(input), {code:'API_REFERENCE_UNRESOLVED'});
  input.external_api_bindings[0].failure_mapping_ref=binding.failure_mapping_ref;
  input.external_api_bindings[0].contract_operation_ref=`${foreign.contract_id}#foreign-operation`;
  assert.throws(()=>compiler.compileExternalApiComposition(input), {code:'API_REFERENCE_UNRESOLVED'});
});
