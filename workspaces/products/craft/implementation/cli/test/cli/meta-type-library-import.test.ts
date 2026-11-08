import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import test from 'node:test';
const require=createRequire(import.meta.url);
const entry=new URL('../../src/index.ts',import.meta.url).href;

test('public compiler API imports from Node stdin without invoking the CLI',()=>{
  const result=spawnSync(process.execPath,['--import',require.resolve('tsx'),'--input-type=module','-'],{
    input:`import * as craft from ${JSON.stringify(entry)}; console.log(craft.CLI_VERSION);`,encoding:'utf8',
  });
  assert.equal(result.status,0,result.stderr);assert.equal(result.stdout.trim(),'1.0.0');
});
