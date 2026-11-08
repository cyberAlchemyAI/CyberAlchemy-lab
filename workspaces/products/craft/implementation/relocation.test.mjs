import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,symlinkSync,readFileSync,realpathSync,rmSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
// Open questions: README.md. This verifies the local compiled owners, not an upstream receipt.
const root=import.meta.dirname,example=path.join(root,'alchlang/examples/generic-http');
const command=(args,cwd=example)=>spawnSync(process.execPath,args,{cwd,encoding:'utf8',maxBuffer:8*1024*1024,
  env:{...process.env,PATH:path.dirname(process.execPath)+path.delimiter+process.env.PATH}});
const args=(entry,out)=>[path.join(root,'alchlang/dist/generic-composition-cli.js'),'generate',
  '--source','business.alch','--profile','contracts/selected-profile.json',
  '--http-profile','contracts/http-profile.json','--entry',entry,'--out',out,
  '--accept-local-review','lab-local-relocation-fixture'];

test('generated local API rejects missing Auth, commits SQLite state, replays and reads it',{timeout:180000},t=>{
  assert.equal(process.versions.node,'26.12.1');
  const scratch=mkdtempSync(path.join(tmpdir(),'craft-relocation-'));
  t.after(()=>rmSync(scratch,{recursive:true,force:true}));
  mkdirSync(path.join(scratch,'node_modules/@domainspec-v2'),{recursive:true});
  symlinkSync(path.join(root,'cli'),path.join(scratch,'node_modules/@domainspec-v2/cli'),'dir');
  const generated=path.join(scratch,'generated');
  const generation=command(args('ReviewDesk.CommitRequestApprovalEntry',generated));
  assert.equal(generation.status,0,generation.stderr);
  assert(existsSync(path.join(generated,'application.mjs')));
  const module=readFileSync(path.join(generated,'application.mjs'),'utf8');
  assert(module.includes("from '@domainspec-v2/cli/generic'"),'generated application must use the public Core import');
  const resolution=command(['--input-type=module','--eval',"console.log(import.meta.resolve('@domainspec-v2/cli/generic'))"],generated);
  assert.equal(resolution.status,0,resolution.stderr);
  assert.equal(fileURLToPath(resolution.stdout.trim()),path.join(root,'cli/dist/generic/index.js'));
  const execution=command([path.join(example,'exercise.mjs'),generated]);
  assert.equal(execution.status,0,execution.stderr);
  const end=execution.stdout.indexOf('\nGenerated protected');
  assert(end>0,'original exercise must report its checked outcomes');
  const outcome=JSON.parse(execution.stdout.slice(0,end));
  if(outcome.state_directory){
    assert(outcome.state_directory.startsWith(path.join(tmpdir(),'craft-generic-http-example-')));
    t.after(()=>rmSync(outcome.state_directory,{recursive:true,force:true}));
  }
  assert.equal(outcome.unauthenticated_status,401);
  assert.equal(outcome.committed.observation.kind,'committed');
  assert.equal(outcome.replayed.observation.kind,'replayed');
  assert.deepEqual(outcome.committed.value,outcome.replayed.value);
  assert.equal(outcome.stored.value.state,'Approved');
  assert.equal(outcome.stored.version,'7');
});

test('generation rejects a nonexistent Entry and leaves no published application',{timeout:120000},t=>{
  const scratch=mkdtempSync(path.join(tmpdir(),'craft-relocation-negative-'));
  t.after(()=>rmSync(scratch,{recursive:true,force:true}));
  const generated=path.join(scratch,'rejected');
  const result=command(args('ReviewDesk.NonexistentEntry',generated));
  assert.notEqual(result.status,0);
  assert.match(result.stderr,/entry|reference/i);
  assert.equal(existsSync(path.join(generated,'application.mjs')),false);
});

test('AI profiles and frontend resolve the local Core and retain public package identities',async()=>{
  const core=await import('@domainspec-v2/cli/generic');
  const profiles=await import('@craft/ai-profiles/application');
  assert.equal(typeof core.createGenericCompositionOwner,'function');
  assert.equal(typeof profiles.compileApplicationProfile,'function');
  assert.equal(fileURLToPath(import.meta.resolve('@domainspec-v2/cli/generic')),path.join(root,'cli/dist/generic/index.js'));
  assert.equal(fileURLToPath(import.meta.resolve('@craft/ai-profiles/application')),path.join(root,'profiles/ai/native/application/index.mjs'));
  assert.equal(realpathSync(path.join(root,'node_modules/.bin/alchlang-generic')),path.join(root,'alchlang/dist/generic-composition-cli.js'));
  assert.equal(realpathSync(path.join(root,'node_modules/.bin/domainspec-v2')),path.join(root,'cli/dist/cli/main.js'));
  const bin=spawnSync(path.join(root,'node_modules/.bin/domainspec-v2'),['--help'],{
    encoding:'utf8',env:{...process.env,PATH:path.dirname(process.execPath)+path.delimiter+process.env.PATH}});
  assert.equal(bin.status,0,String(bin.error||bin.stderr));
  assert.match(bin.stdout,/domainspec/i);
  for(const [home,name] of [['cli','@domainspec-v2/cli'],['alchlang','@cyberalchemy/alchlang'],['profiles/ai','@craft/ai-profiles']])
    assert.equal(JSON.parse(readFileSync(path.join(root,home,'package.json'))).name,name);
});
