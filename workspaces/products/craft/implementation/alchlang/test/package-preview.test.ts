import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import test from 'node:test';
import {parseReleaseArguments,packRelease,releasePlan} from '../scripts/package-release.mjs';

test('preview packaging selects the core boundary without optional layer artifacts',()=>{
  assert.deepEqual(parseReleaseArguments(['--package','core','--plan']),{mode:'plan',packages:['core']});
  assert.deepEqual(parseReleaseArguments(['output','--package','core']),{mode:'pack',output:'output',packages:['core']});
  assert.deepEqual(releasePlan(['core']).map((p:any)=>p.name),['@cyberalchemy/alchlang']);
  for(const args of [['--package'],['--package','unknown'],['--package','core','--package','core']])assert.throws(()=>parseReleaseArguments(args),/ALCHLANG_RELEASE_USAGE/);
});

test('preview archives include the complete starter and refuse replacing qualified bytes',()=>{
  const output=fs.mkdtempSync(path.join(os.tmpdir(),'alch-cli-preview-pack-'));
  try{
    const result=packRelease(output,['core']);assert.equal(result.artifacts.length,1);
    const artifact=result.artifacts[0];assert.equal(artifact.id,'core');
    assert.deepEqual(fs.readdirSync(output),[path.basename(artifact.file)]);
    const before=createHash('sha256').update(fs.readFileSync(artifact.file)).digest('hex');
    assert.throws(()=>packRelease(output,['core']),/ALCHLANG_RELEASE_OUTPUT_EXISTS/);
    assert.equal(createHash('sha256').update(fs.readFileSync(artifact.file)).digest('hex'),before);
    assert.equal(result.publication_performed,false);assert.equal(result.installation_performed,false);
    assert.ok(artifact.file_count>0);
  }finally{fs.rmSync(output,{recursive:true,force:true});}
});
