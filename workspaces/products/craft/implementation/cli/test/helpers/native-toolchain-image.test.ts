import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {checkoutRoot} from './local-toolchain.ts';
import {NATIVE_TEST_IMAGE_PROFILE as profile, NATIVE_TEST_IMAGE_ID, assertNativeTestProfile, assertNativeTestImageId,
  assertNativeTestProfileBytes, parseNativeTestInspectOutput, assertNativeTestTag, assertNativeTestSource, assertNativeTestSources, nativeToolchainImage} from './native-toolchain-image.ts';

test('current image profile is closed, source-bound and explicitly not historical equivalence', () => {
  assertNativeTestProfile(profile); assertNativeTestSources();
  assert.equal(profile.source_files.length, 12); assert.equal(profile.provenance.historical_equivalence, false);
  assert.notEqual(profile.image_id, profile.provenance.historical_image_id);
  for (const value of [profile, profile.versions, profile.provenance, profile.source_files, ...profile.source_files]) assert.ok(Object.isFrozen(value));
});
test('pure image and tag guards reject historical, alternate and malformed identities', () => {
  assert.equal(assertNativeTestImageId(NATIVE_TEST_IMAGE_ID), NATIVE_TEST_IMAGE_ID);
  for (const value of [profile.provenance.historical_image_id, 'sha256:' + '0'.repeat(64), profile.tag, null, 1, NATIVE_TEST_IMAGE_ID + '\nother', NATIVE_TEST_IMAGE_ID + ' ']) assert.throws(() => assertNativeTestImageId(value));
  assertNativeTestTag(profile.tag, profile.tag);
  for (const value of ['other:latest', NATIVE_TEST_IMAGE_ID, null, '']) assert.throws(() => assertNativeTestTag(value, profile.tag));
  assert.throws(() => assertNativeTestTag(profile.tag, 'other:latest'));
});
test('caller tag drift is rejected before any Docker inspection', () => {
  // The pure-test namespace intentionally provides no Docker socket; wrong tags still fail at this exact boundary.
  assert.throws(() => nativeToolchainImage('other:latest'), /DS_TEST_IMAGE_REQUESTED_TAG/);
});
test('reviewed raw profile bytes reject well-formed coordinated identity and hash changes', () => {
  const bytes = fs.readFileSync(new URL('./native-toolchain-image.v1.json', import.meta.url)); assertNativeTestProfileBytes(bytes);
  const altered = {...profile, image_id: 'sha256:' + '0'.repeat(64), source_files: profile.source_files.map(row => ({...row, sha256: '0'.repeat(64)}))};
  for (const changed of [Buffer.from(JSON.stringify(altered, null, 2) + '\n'), Buffer.concat([bytes, Buffer.from('\n')])]) assert.throws(() => assertNativeTestProfileBytes(changed), /DS_TEST_IMAGE_PROFILE_BYTES/);
});
test('inspection output requires exactly one immutable image ID and one Linux line terminator', () => {
  assert.equal(parseNativeTestInspectOutput(NATIVE_TEST_IMAGE_ID + '\n'), NATIVE_TEST_IMAGE_ID);
  for (const value of [NATIVE_TEST_IMAGE_ID, NATIVE_TEST_IMAGE_ID + ' \n', ' ' + NATIVE_TEST_IMAGE_ID + '\n', NATIVE_TEST_IMAGE_ID + '\n\n',
    NATIVE_TEST_IMAGE_ID + '\r\n', NATIVE_TEST_IMAGE_ID + '\nother\n', profile.provenance.historical_image_id + '\n', null]) assert.throws(() => parseNativeTestInspectOutput(value), /DS_TEST_IMAGE_INSPECT_LINE/);
});
test('pure profile guards reject extra keys, wrong versions, source paths and source hashes', () => {
  const first = profile.source_files[0]!;
  for (const value of [{...profile, extra: true}, {...profile, image_id: profile.provenance.historical_image_id},
    {...profile, tag: 'other:latest'}, {...profile, versions: {...profile.versions, node: '0.0.0'}},
    {...profile, versions: {...profile.versions, extra: '0.0.0'}}, {...profile, source_files: profile.source_files.slice(1)},
    {...profile, source_files: [{...first, path: '../outside'}, ...profile.source_files.slice(1)]},
    {...profile, source_files: [{...first, sha256: '0'.repeat(64)}, ...profile.source_files.slice(1)]},
    {...profile, provenance: {...profile.provenance, historical_equivalence: true}}, {...profile, schema_version: 'unknown'}]) assert.throws(() => assertNativeTestProfile(value));
});
test('pure source guards reject symlinks, nonregular files, undeclared paths, extra metadata and drift', () => {
  const first = profile.source_files[0]!, valid = {regular: true, symlink: false, sha256: first.sha256};
  assertNativeTestSource(first.path, valid);
  assert.throws(() => assertNativeTestSource('../outside', valid));
  for (const value of [{...valid, regular: false}, {...valid, symlink: true}, {...valid, sha256: '0'.repeat(64)}, {...valid, extra: true}, {...valid, [Symbol('extra')]: true}]) assert.throws(() => assertNativeTestSource(first.path, value));
  let accessed = 0; const accessor = Object.defineProperty({...valid}, 'regular', {get() {accessed++; return true;}});
  assert.throws(() => assertNativeTestSource(first.path, accessor)); assert.equal(accessed, 0);
});
test('actual owned source mirrors reject leaf and ancestor symlink substitutions and changed bytes', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-native-image-controls-')); t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  for (const row of profile.source_files) {const file = path.join(root, row.path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.copyFileSync(path.join(checkoutRoot, row.path), file);}
  assertNativeTestSources(root);
  const first = path.join(root, profile.source_files[0]!.path), moved = first + '.original'; fs.renameSync(first, moved);
  fs.symlinkSync(moved, first); assert.throws(() => assertNativeTestSources(root), /DS_TEST_IMAGE_SOURCE_SYMLINK/); fs.unlinkSync(first); fs.renameSync(moved, first);
  const parent = path.join(root, 'craft/toolchains/node-typescript'), shifted = parent + '-original'; fs.renameSync(parent, shifted);
  fs.symlinkSync(shifted, parent); assert.throws(() => assertNativeTestSources(root), /DS_TEST_IMAGE_SOURCE_SYMLINK/); fs.unlinkSync(parent); fs.renameSync(shifted, parent);
  fs.appendFileSync(first, '\n'); assert.throws(() => assertNativeTestSources(root), /DS_TEST_IMAGE_SOURCE_DRIFT/);
});
