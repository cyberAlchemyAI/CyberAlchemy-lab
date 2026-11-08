import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import test from 'node:test';
import {testTsx} from './toolchain.js';

const root=path.resolve(import.meta.dirname,'..');
const extension=path.resolve(root,'../extensions');
const tsx=testTsx();
function cli(entry:string,args:string[]){
  return spawnSync(tsx,[path.join(root,'src',entry),...args],{cwd:root,encoding:'utf8'});
}

test('core CLI rejects Rust and local-host profiles with an installation direction',()=>{
  const rust=cli('core-cli.ts',['check',path.join(extension,'rust-function-v1/quantity-price.alch')]);
  assert.notEqual(rust.status,0);assert.match(rust.stderr,/ALCHLANG_OPTIONAL_FEATURE_REQUIRED:rust: use alchlang-rust/);
  const host=cli('core-cli.ts',['check',path.join(extension,'local-host-v1/orders.alch')]);
  assert.notEqual(host.status,0);assert.match(host.stderr,/ALCHLANG_OPTIONAL_FEATURE_REQUIRED:local-host: use alchlang-local-host/);
});

test('optional entry points accept only their declared capability boundary',()=>{
  const rust=cli('rust-cli.ts',['check',path.join(extension,'rust-function-v1/quantity-price.alch')]);
  assert.equal(rust.status,0,rust.stderr);
  const hostFromRust=cli('rust-cli.ts',['check',path.join(extension,'local-host-v1/orders.alch')]);
  assert.notEqual(hostFromRust.status,0);assert.match(hostFromRust.stderr,/ALCHLANG_OPTIONAL_FEATURE_REQUIRED:local-host/);
  const host=cli('local-host-cli.ts',['check',path.join(extension,'local-host-v1/orders.alch')]);
  assert.equal(host.status,0,host.stderr);
});

test('release plan physically removes optional code and Cargo templates from core',()=>{
  const result=spawnSync(process.execPath,[path.join(root,'scripts/package-release.mjs'),'--plan'],{cwd:root,encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);const plan=JSON.parse(result.stdout);
  const core=plan.find((item:any)=>item.id==='core'),rust=plan.find((item:any)=>item.id==='rust'),host=plan.find((item:any)=>item.id==='local-host');
  assert.equal(core.name,'@cyberalchemy/alchlang');assert.equal(core.omits_cargo_templates,true);
  for(const module of ['rust-function-builder','rust-toolchain','local-host','ontology-host','state-migration'])assert.ok(core.omitted_modules.includes(module));
  assert.equal(rust.name,'@cyberalchemy/alchlang-rust');assert.ok(rust.omitted_modules.includes('local-host'));
  assert.equal(host.status,'experimental-repository-bound');
});
