import test from 'node:test';
import assert from 'node:assert/strict';
import {staticCoreCommerceServiceFiles} from '../../src/generic/core-commerce-runtime-inventory.ts';

const file=(path,sha256='original')=>({path,sha256,bytes:8});
const immutable=[file('repository/service-repositories.js'),file('repository/schema.json')];
const equal=(left,right)=>assert.deepEqual(staticCoreCommerceServiceFiles(left),staticCoreCommerceServiceFiles(right));
const digest='a'.repeat(64);

test('C14 live SQLite and original owner-managed identity files do not invalidate immutable service artifacts',()=>{
 equal(immutable,[...immutable,file('store.sqlite','live'),file('store.sqlite-journal','live'),
  file(`identity/${digest}/commerce-identity-model.js`,'generated'),
  file(`identity/workflow-${digest}/identity-component.json`,'generated'),
  file(`identity-reopen-09e0ed14-15e6-4dbd-a178-9c9d65f41a40/${digest}/values-and-codecs.ts`,'generated')]);
});

test('C14 repository changes and other new files still invalidate immutable service artifacts',()=>{
 assert.notDeepEqual(staticCoreCommerceServiceFiles(immutable),staticCoreCommerceServiceFiles([
  file('repository/service-repositories.js','tampered'),immutable[1]]));
 for(const unexpected of ['new.js','repository/new.js','nested/store.sqlite','identity-extra/file.js',
  'identity-reopen-malformed/file.js',`identity/${digest}/unexpected.js`,
  'identity/transaction-codec.js',`identity/${'z'.repeat(64)}/commerce-identity-model.js`]){
  assert.notDeepEqual(staticCoreCommerceServiceFiles(immutable),staticCoreCommerceServiceFiles([...immutable,file(unexpected)]));
 }
});
