import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {lstatSync,readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import test from 'node:test';

const root=import.meta.dirname;
const sha=path=>createHash('sha256').update(readFileSync(path)).digest('hex');

test('cutover Alch integration matches its release-retained manifest files',()=>{
  const manifest=JSON.parse(readFileSync(resolve(root,'generated/manifest.json')));
  assert.equal(manifest.schema_version,'alchlang.semantic-contract-build/v1');
  assert.equal(manifest.profile,'semantic-contract-v1');
  assert.equal(manifest.authority_effect,'none');
  assert.equal(manifest.ontology_admitted,false);
  assert.equal(manifest.constitution_adopted,false);
  assert.equal(sha(resolve(root,'cutover.alch')),manifest.source_sha256);
  assert.equal(sha(resolve(root,'cutover.fixtures.json')),manifest.fixture_sha256['cutover.fixtures.json']);
  for(const [relative,digest] of Object.entries(manifest.files)){
    if(relative.startsWith('evidence/'))continue;
    const path=resolve(root,'generated',relative),stat=lstatSync(path);
    assert.equal(stat.isFile()&&!stat.isSymbolicLink(),true,relative);
    assert.equal(sha(path),digest,relative);
  }
});
