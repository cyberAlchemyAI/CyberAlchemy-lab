import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {checkoutRoot, assertPinnedVersion} from './local-toolchain.ts';

// Test-only current image binding. Open questions are owned by the profile's linked plan.
type NativeImageProfile = {
  readonly schema_version: string; readonly tag: string; readonly image_id: string;
  readonly versions: Readonly<{node: string; npm: string; pnpm: string; typescript: string}>;
  readonly source_files: ReadonlyArray<Readonly<{path: string; sha256: string}>>;
  readonly provenance: Readonly<{qualification_ref: string; qualification_summary_sha256: string; historical_image_id: string; historical_equivalence: false}>;
  readonly open_questions_ref: string;
};
const profileFile = new URL('./native-toolchain-image.v1.json', import.meta.url);
assert.ok(fs.lstatSync(profileFile).isFile() && !fs.lstatSync(profileFile).isSymbolicLink(), 'DS_TEST_IMAGE_PROFILE_REGULAR');
// Independent reviewed bytes, not a profile self-hash or caller-resealed expectation.
export function assertNativeTestProfileBytes(bytes: Uint8Array): void {
  assert.equal(createHash('sha256').update(bytes).digest('hex'), '26f072edad676592eaf019b46092ee8cde7b9eb543e5fc8b7ad9c88934bbf33e', 'DS_TEST_IMAGE_PROFILE_BYTES');
}
const profileBytes = fs.readFileSync(profileFile); assertNativeTestProfileBytes(profileBytes);
const profile: NativeImageProfile = JSON.parse(profileBytes.toString('utf8'));
const expectedPaths = ['toolchain.json', 'package.json', 'package-lock.json', 'migration-inventory.json', 'Dockerfile',
  'tsconfig/base.json', 'tsconfig/node.json', 'tsconfig/browser.json', 'scripts/validate-toolchain.mjs', 'scripts/doctor.mjs',
  'bin/container-entrypoint', 'bin/playwright'].map(p => 'craft/toolchains/node-typescript/' + p);
const keys = (value: object, expected: string[]) => {
  assert.deepEqual(Reflect.ownKeys(value).sort(), [...expected].sort(), 'DS_TEST_IMAGE_PROFILE_KEYS');
  for (const key of expected) assert.ok(Object.hasOwn(Object.getOwnPropertyDescriptor(value, key)!, 'value'), 'DS_TEST_IMAGE_PROFILE_DATA');
};
keys(profile, ['schema_version', 'tag', 'image_id', 'versions', 'source_files', 'provenance', 'open_questions_ref']);
assert.equal(profile.schema_version, 'domainspec.test-native-toolchain-image/v1');
assert.match(profile.tag, /^domainspec-node-toolchain:[0-9.]+-ts[0-9.]+$/);
assert.match(profile.image_id, /^sha256:[0-9a-f]{64}$/);
keys(profile.versions, ['node', 'npm', 'pnpm', 'typescript']);
for (const version of Object.values(profile.versions)) assert.match(version, /^\d+\.\d+\.\d+$/);
keys(profile.provenance, ['qualification_ref', 'qualification_summary_sha256', 'historical_image_id', 'historical_equivalence']);
assert.match(profile.provenance.qualification_summary_sha256, /^[0-9a-f]{64}$/);
assert.match(profile.provenance.historical_image_id, /^sha256:[0-9a-f]{64}$/);
assert.notEqual(profile.image_id, profile.provenance.historical_image_id);
assert.equal(profile.provenance.historical_equivalence, false);
assert.equal(profile.provenance.qualification_ref, 'goals/plans/domainspec-alchlang-review-repair/C4-NATIVE-TOOLCHAIN-PREREQUISITES.v1.md');
assert.equal(profile.open_questions_ref, 'goals/plans/domainspec-alchlang-review-repair/C4-CURRENT-NATIVE-TEST-BINDING.v1.md');
assert.deepEqual(profile.source_files.map(row => row.path), expectedPaths, 'DS_TEST_IMAGE_SOURCE_PATHS');
for (const row of profile.source_files) {keys(row, ['path', 'sha256']); assert.match(row.sha256, /^[0-9a-f]{64}$/); Object.freeze(row);}
Object.freeze(profile.source_files); Object.freeze(profile.versions); Object.freeze(profile.provenance); Object.freeze(profile);
export const NATIVE_TEST_IMAGE_PROFILE: Readonly<NativeImageProfile> = profile;
export const NATIVE_TEST_IMAGE_ID = profile.image_id;

/** Pure checks: no subprocess, filesystem mutation, alternate image or fallback. */
export function assertNativeTestProfile(candidate: unknown): void {
  assert.deepEqual(candidate, profile, 'DS_TEST_IMAGE_PROFILE_DRIFT');
}
export function assertNativeTestImageId(observed: unknown): string {
  assert.equal(observed, NATIVE_TEST_IMAGE_ID, 'DS_TEST_IMAGE_ID_MISMATCH'); return NATIVE_TEST_IMAGE_ID;
}
export function parseNativeTestInspectOutput(observed: unknown): string {
  assert.equal(observed, NATIVE_TEST_IMAGE_ID + '\n', 'DS_TEST_IMAGE_INSPECT_LINE'); return NATIVE_TEST_IMAGE_ID;
}
export function assertNativeTestTag(requested: unknown, canonical: unknown): void {
  assert.equal(canonical, profile.tag, 'DS_TEST_IMAGE_CANONICAL_TAG');
  assert.equal(requested, canonical, 'DS_TEST_IMAGE_REQUESTED_TAG');
}
export function assertNativeTestSource(relative: string, observed: {regular: boolean; symlink: boolean; sha256: string}): void {
  keys(observed, ['regular', 'symlink', 'sha256']);
  const row = profile.source_files.find(row => row.path === relative);
  assert.ok(row, 'DS_TEST_IMAGE_SOURCE_PATH');
  assert.equal(observed.regular, true, 'DS_TEST_IMAGE_SOURCE_REGULAR');
  assert.equal(observed.symlink, false, 'DS_TEST_IMAGE_SOURCE_SYMLINK');
  assert.equal(observed.sha256, row.sha256, 'DS_TEST_IMAGE_SOURCE_DRIFT');
}
/** Public only for real owned-fixture controls; native execution always uses checkoutRoot. */
export function assertNativeTestSources(root = checkoutRoot): void {
  assert.equal(fs.realpathSync(root), root, 'DS_TEST_IMAGE_ROOT_SYMLINK');
  for (const row of profile.source_files) {
    let file = root;
    for (const [index, component] of row.path.split('/').entries()) {
      file = path.join(file, component); const stat = fs.lstatSync(file);
      assert.equal(stat.isSymbolicLink(), false, 'DS_TEST_IMAGE_SOURCE_SYMLINK');
      assert.ok(index === row.path.split('/').length - 1 ? stat.isFile() : stat.isDirectory(), 'DS_TEST_IMAGE_SOURCE_REGULAR');
    }
    assertNativeTestSource(row.path, {regular: true, symlink: false, sha256: createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
  }
}
export function nativeToolchainImage(requestedTag: string = profile.tag): string {
  // Reject caller drift before any Docker request. Never run by a mutable tag.
  assertNativeTestTag(requestedTag, profile.tag);
  assertNativeTestSources();
  const manifest = JSON.parse(fs.readFileSync(path.join(checkoutRoot, expectedPaths[0]!), 'utf8'));
  assertNativeTestTag(requestedTag, manifest.container_image);
  assert.deepEqual({node: manifest.node.version, npm: manifest.package_managers.npm, pnpm: manifest.package_managers.pnpm, typescript: manifest.typescript}, profile.versions, 'DS_TEST_IMAGE_VERSION_DRIFT');
  assertPinnedVersion('node', process.versions.node, profile.versions.node);
  return parseNativeTestInspectOutput(execFileSync('docker', ['image', 'inspect', requestedTag, '--format', '{{.Id}}'], {encoding: 'utf8'}));
}
