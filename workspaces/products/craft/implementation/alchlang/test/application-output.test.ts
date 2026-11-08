import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { APPLICATION_MANIFEST, validateApplicationOutput, verifyApplicationOutput, writeApplicationOutput } from "../src/application-output.js";

function fixture(t: test.TestContext) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-output-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { root, out: path.join(root, "output"), files: { "src/main.ts": "export const value = 1;\n", ".alch/check.json": "{}\n", [APPLICATION_MANIFEST]: "manifest\n" } };
}

test("exclusive application output seals last and never overwrites existing targets", t => {
  const { root, out, files } = fixture(t); let calls = 0;
  writeApplicationOutput(out, files, () => {
    calls++;
    if (calls === 1) assert.equal(fs.existsSync(out), false);
    if (calls === 2) { assert.equal(fs.readFileSync(path.join(out, "src/main.ts"), "utf8"), files["src/main.ts"]); assert.equal(fs.existsSync(path.join(out, APPLICATION_MANIFEST)), false); }
    if (calls === 3) assert.equal(fs.existsSync(path.join(out, APPLICATION_MANIFEST)), true);
  });
  assert.equal(calls, 3); verifyApplicationOutput(out, files);
  assert.throws(() => writeApplicationOutput(out, files, () => {}), /already exists/);
  fs.symlinkSync(path.join(root, "missing"), path.join(root, "dangling"));
  assert.throws(() => writeApplicationOutput(path.join(root, "dangling"), files, () => {}), /already exists/);
  fs.symlinkSync(root, path.join(root, "linked"));
  assert.throws(() => writeApplicationOutput(path.join(root, "linked/other"), files, () => {}), /real output parent/);
  assert.throws(() => verifyApplicationOutput(path.join(root, "linked/output"), files), /real output directory/);
});

test("output validation rejects traversal, portable aliases and file/directory collisions before writes", t => {
  const { out, files } = fixture(t);
  for (const name of ["../escape", "/absolute", "a//b", "a/./b", "C:/file", "a\\b", "a\u0000b", "CON.txt", "folder./file", "trailing "]) {
    assert.throws(() => writeApplicationOutput(out, { ...files, [name]: "x" }, () => {}), /unsafe output path/);
    assert.equal(fs.existsSync(out), false);
  }
  const collisions: Record<string, string>[] = [{ "SRC/other.ts": "x" }, { "é/x": "x", "e\u0301/y": "x" },
    { "ＳＲＣ/other.ts": "x" }, { src: "x" }];
  for (const extra of collisions) {
    assert.throws(() => validateApplicationOutput({ ...files, ...extra }), /collision/);
  }
  assert.throws(() => writeApplicationOutput(out, files, () => { throw Error("input drift"); }), /input drift/);
  assert.equal(fs.existsSync(out), false);
});

test("verification rejects missing, altered, extra and linked output entries", t => {
  const { out, files } = fixture(t); writeApplicationOutput(out, files, () => {});
  const target = path.join(out, "src/main.ts");
  fs.writeFileSync(target, files["src/main.ts"].replace("1", "2"));
  assert.throws(() => verifyApplicationOutput(out, files), /bytes differ/);
  fs.unlinkSync(target); assert.throws(() => verifyApplicationOutput(out, files), /missing/);
  fs.symlinkSync(path.join(out, ".alch/check.json"), target); assert.throws(() => verifyApplicationOutput(out, files), /symlink/);
  fs.unlinkSync(target); fs.writeFileSync(target, files["src/main.ts"]);
  fs.mkdirSync(path.join(out, "foreign")); assert.throws(() => verifyApplicationOutput(out, files), /unexpected output directory/);
  fs.rmdirSync(path.join(out, "foreign")); fs.writeFileSync(path.join(out, "foreign"), "keep");
  assert.throws(() => verifyApplicationOutput(out, files), /unexpected output file/);
});

test("failed publication cleans only unchanged owned files and preserves foreign edits", t => {
  const { out, files } = fixture(t); let calls = 0;
  assert.throws(() => writeApplicationOutput(out, files, () => {
    if (++calls === 2) {
      fs.writeFileSync(path.join(out, "foreign.txt"), "foreign");
      fs.writeFileSync(path.join(out, "src/main.ts"), "foreign edit");
      throw Error("input changed before sealing");
    }
  }), /input changed/);
  assert.equal(fs.readFileSync(path.join(out, "foreign.txt"), "utf8"), "foreign");
  assert.equal(fs.readFileSync(path.join(out, "src/main.ts"), "utf8"), "foreign edit");
  assert.equal(fs.existsSync(path.join(out, ".alch/check.json")), false);
  assert.equal(fs.existsSync(path.join(out, APPLICATION_MANIFEST)), false);
});

test("replaced roots survive cleanup, and late input drift removes the completion marker", t => {
  const { root, out, files } = fixture(t); let calls = 0;
  assert.throws(() => writeApplicationOutput(out, files, () => {
    if (++calls === 2) {
      fs.renameSync(out, path.join(root, "displaced")); fs.mkdirSync(out); fs.writeFileSync(path.join(out, "foreign.txt"), "keep");
      throw Error("root replaced");
    }
  }), /root replaced/);
  assert.equal(fs.readFileSync(path.join(out, "foreign.txt"), "utf8"), "keep");
  assert.equal(fs.readFileSync(path.join(root, "displaced/src/main.ts"), "utf8"), files["src/main.ts"]);
  const late = path.join(root, "late"); calls = 0;
  assert.throws(() => writeApplicationOutput(late, files, () => { if (++calls === 3) throw Error("late drift"); }), /late drift/);
  assert.equal(fs.existsSync(late), false);
});
