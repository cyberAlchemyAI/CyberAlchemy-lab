import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { compileCarrier, parseDomainSource, writeCompilation } from "../src/index.js";

const source = `domain writer-test "Writer test"\nowner writer-owner\nentity Record:\n  id: identifier required\nactor Writer\nstates Record:\n  initial ready\nboundary local-write:\n  owner writer-owner\n`;

test("writer materializes generated files and a digest manifest", () => {
  const parsed = parseDomainSource(source); const compiled = compileCarrier(parsed.carrier);
  const directory = path.join(mkdtempSync(path.join(tmpdir(), "domainspec-writer-")), "generated");
  const receipt = writeCompilation(compiled, directory, { carrier: parsed.carrier });
  assert.ok(existsSync(path.join(directory, "domain.types.ts"))); assert.ok(existsSync(path.join(directory, "domain.carrier.json")));
  const manifest = JSON.parse(readFileSync(path.join(directory, "manifest.json"), "utf8")); assert.equal(manifest.plan_digest, compiled.plan_digest); assert.equal(receipt.files["domain.types.ts"], manifest.files["domain.types.ts"]);
  assert.throws(() => writeCompilation(compiled, directory), /OUTPUT_EXISTS/);
  assert.doesNotThrow(() => writeCompilation(compiled, directory, { force: true }));
});
