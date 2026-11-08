import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,rmSync,symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

test('generic CLI runs when npm launches it through a bin symlink',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'alchlang-generic-bin-'));
 try{
  const target=fileURLToPath(new URL('../src/generic-composition-cli.ts',import.meta.url));
  const bin=path.join(root,'alchlang-generic.ts');symlinkSync(target,bin);
  const result=spawnSync(process.execPath,['--import','tsx',bin,'--help'],{encoding:'utf8',timeout:30000});
  assert.equal(result.status,0,result.stderr);
  assert.match(result.stdout,/usage: generate --source FILE/);
  assert.doesNotMatch(result.stderr,/"ok":false/);
 }finally{rmSync(root,{recursive:true,force:true});}
});
