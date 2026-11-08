import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

const cliRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.join(cliRoot, "fixtures/input-roots/canonical-project");

function certify(toolPath: string, target: string) {
  return spawnSync(process.execPath, ["--disable-warning=DEP0205", "--import", "tsx", path.join(cliRoot, "src/cli/main.ts"), "certify", source, "--target", target], {
    cwd: cliRoot, encoding: "utf8", env: { ...process.env, PATH: toolPath }, timeout: 20_000,
  });
}

test("missing Lean reports a certification diagnostic and publishes no target", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-no-lean-"));
  const target = path.join(parent, "proof");
  try {
    const result = certify(parent, target);
    assert.equal(result.status, 22, result.error?.message ?? result.stderr);
    const diagnostic = JSON.parse(result.stderr);
    assert.equal(diagnostic.code, "MTCLI_CERTIFY_LEAN_UNAVAILABLE");
    assert.match(diagnostic.message, /lean.*ENOENT/);
    assert.equal(fs.existsSync(target), false);
    assert.deepEqual(fs.readdirSync(parent), []);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});

test("a different Lean version is rejected before any certificate is published", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-wrong-lean-"));
  const target = path.join(parent, "proof");
  try {
    fs.writeFileSync(path.join(parent, "lean"), '#!/bin/sh\nprintf "Lean (version 0.0.0, test fixture)\\n"\n', { mode: 0o755 });
    const result = certify(parent, target);
    assert.equal(result.status, 22, result.error?.message ?? result.stderr);
    assert.equal(JSON.parse(result.stderr).code, "MTCLI_CERTIFY_LEAN_VERSION");
    assert.equal(fs.existsSync(target), false);
    assert.deepEqual(fs.readdirSync(parent), ["lean"]);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});

test("missing psql reports the unavailable client without a secondary TypeError", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-no-psql-"));
  try {
    const module = pathToFileURL(path.join(cliRoot, "src/runtime/postgres-outbox.ts")).href;
    const script = `import { PostgresTransactionalOutbox } from ${JSON.stringify(module)};
try { new PostgresTransactionalOutbox({host:"127.0.0.1",port:5432,database:"isolated-test",user:"isolated-test",password:"unused-test-value"}); process.exitCode=1; }
catch(error) { console.log(JSON.stringify({name:error.name,message:error.message})); }`;
    const result = spawnSync(process.execPath, ["--disable-warning=DEP0205", "--import", "tsx", "--input-type=module", "-e", script], {
      cwd: cliRoot, encoding: "utf8", env: { ...process.env, PATH: parent }, timeout: 20_000,
    });
    assert.equal(result.status, 0, result.error?.message ?? result.stderr);
    const diagnostic = JSON.parse(result.stdout);
    assert.equal(diagnostic.name, "Error");
    assert.match(diagnostic.message, /^OUTBOX_POSTGRES:.*psql.*ENOENT/);
    assert.doesNotMatch(diagnostic.message, /trim|TypeError|unused-test-value/);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});
