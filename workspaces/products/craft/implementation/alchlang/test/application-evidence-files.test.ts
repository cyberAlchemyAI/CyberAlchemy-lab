import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, rmSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { digest } from "../src/domainspec-profile.js";
import { loadApplicationEvidenceFiles } from "../src/application-evidence-files.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";

test("exact evidence loader reads selected bytes only, deduplicates and never writes", t => {
  const root = mkdtempSync(path.join(tmpdir(), "alch-evidence-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, "evidence"));
  const bytes = Buffer.from("explicit meaning — not inferred acceptance\n");
  writeFileSync(path.join(root, "evidence/meaning.txt"), bytes);
  writeFileSync(path.join(root, "unselected.txt"), "unselected");
  const ref = { path: "evidence/meaning.txt", sha256: digest(bytes), size_bytes: bytes.length, current: true };
  const before = readdirSync(root, { recursive: true });
  const result = loadApplicationEvidenceFiles(root, [ref, { ...ref }]);
  assert.deepEqual([...result.keys()], [ref.path]);
  assert.deepEqual(result.get(ref.path), bytes);
  for (const invalid of ["../outside", "/etc/passwd", "C:/outside", "evidence\\meaning.txt", "evidence//meaning.txt", "evidence/./meaning.txt", "bad\u0000path"]) {
    assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, path: invalid }]), /FORMAL_BINDING_PATH/);
  }
  assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, current: false }]), /FORMAL_BINDING_CURRENTNESS/);
  assert.throws(() => loadApplicationEvidenceFiles(root, [ref, { ...ref, sha256: "0".repeat(64) }]), /conflicting reference/);
  assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, sha256: "0".repeat(64) }]), /FORMAL_BINDING_STALE/);
  assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, size_bytes: bytes.length + 1 }]), /size\/type changed/);
  assert.deepEqual(readdirSync(root, { recursive: true }), before);
});

test("evidence loader rejects symlink files, symlink parents, directories and missing inputs", t => {
  const root = mkdtempSync(path.join(tmpdir(), "alch-evidence-links-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, "data"));
  writeFileSync(path.join(root, "data/value"), "x");
  symlinkSync(path.join(root, "data/value"), path.join(root, "linked"));
  symlinkSync(path.join(root, "data"), path.join(root, "linked-parent"));
  const ref = { sha256: digest("x"), size_bytes: 1, current: true };
  for (const relative of ["linked", "linked-parent/value", "data"]) {
    assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, path: relative }]), /APPLICATION_EVIDENCE_FILE/);
  }
  assert.throws(() => loadApplicationEvidenceFiles(root, [{ ...ref, path: "missing" }]), /ENOENT/);
});

test("file-loaded exact evidence preserves domain formation and rejects subsequent source drift", t => {
  const root = mkdtempSync(path.join(tmpdir(), "alch-evidence-domain-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const fixture = executableFixture();
  const references = [...fixture.sources].map(([relative, bytes]) => {
    const target = path.join(root, relative);
    mkdirSync(path.dirname(target), { recursive: true });
    writeFileSync(target, bytes);
    return { path: relative, sha256: digest(bytes), size_bytes: bytes.length, current: true };
  });
  const loaded = loadApplicationEvidenceFiles(root, references);
  assert.deepEqual(lowerApplicationDomain(fixture.source, fixture.bindings, loaded),
    lowerApplicationDomain(fixture.source, fixture.bindings, fixture.sources));
  const first = references[0]!;
  writeFileSync(path.join(root, first.path), Buffer.alloc(first.size_bytes, 32));
  assert.throws(() => loadApplicationEvidenceFiles(root, references), /FORMAL_BINDING_STALE/);
  // The earlier snapshot is not a live filesystem view or an acceptance grant.
  assert.deepEqual(loaded.get(first.path), fixture.sources.get(first.path));
});
