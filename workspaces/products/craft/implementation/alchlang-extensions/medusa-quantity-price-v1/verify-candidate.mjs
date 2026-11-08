import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {root,implementation} from './build.mjs';
const workspace=path.resolve(implementation,'../../../../../../../');
const sha=value=>createHash('sha256').update(value).digest('hex');
const candidate=JSON.parse(readFileSync(path.join(root,'candidate.json'),'utf8'));
assert.equal(sha(JSON.stringify(candidate.files)),candidate.scope_sha256,'candidate file-map digest');
for(const [relative,digest] of Object.entries(candidate.files)) {
  const absolute=path.resolve(workspace,relative);
  assert.ok(absolute.startsWith(workspace+path.sep),'candidate path escape');
  assert.equal(sha(readFileSync(absolute)),digest,relative);
}
const bundle=path.join(root,'evidence/application/bundle');
const manifest=JSON.parse(readFileSync(path.join(bundle,'manifest.json'),'utf8'));
for(const [relative,digest] of Object.entries(manifest.files)) assert.equal(sha(readFileSync(path.join(bundle,relative))),digest,relative);
assert.equal(sha(readFileSync(path.join(root,'quantity-price.alch'))),manifest.source_sha256,'current source');
assert.equal(sha(readFileSync(path.join(root,'quantity-price.alch.domainspec.json'))),manifest.bindings_sha256,'current bindings');
const compiler=JSON.parse(readFileSync(path.join(bundle,'compiler-files.json'),'utf8'));
for(const [relative,digest] of Object.entries(compiler)) assert.equal(sha(readFileSync(path.join(workspace,'projects/domainspec-v2/impl/cli',relative))),digest,'compiler: '+relative);
console.log(JSON.stringify({status:'pass',files:Object.keys(candidate.files).length,compiler_files:Object.keys(compiler).length,scope_sha256:candidate.scope_sha256,authority_effect:'none'},null,2));
