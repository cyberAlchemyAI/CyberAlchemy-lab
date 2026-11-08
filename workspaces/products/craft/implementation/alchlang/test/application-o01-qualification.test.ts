import assert from "node:assert/strict";
import crypto from "node:crypto";
import {spawnSync} from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const checkoutRoot = path.resolve(import.meta.dirname, "../../../../../../..");
const qualificationPath = path.join(checkoutRoot, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/o01-portable-toolchain/qualification.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

function validate(value: any, checkImage = true): void {
  assert.equal(value.schema_version, "alchlang.o01-toolchain-parity/v1-candidate");
  assert.equal(value.task, "O01"); assert.equal(value.result, "pass"); assert.equal(value.authority_effect, "none");
  assert.equal(value.dag.node, "O01"); assert.equal(sha256(path.join(checkoutRoot, value.dag.path)), value.dag.sha256);
  for (const binding of Object.values(value.bindings) as Array<{path: string; sha256: string}>) {
    assert.equal(sha256(path.join(checkoutRoot, binding.path)), binding.sha256, binding.path);
  }
  for (const lane of [value.host, value.container]) {
    assert.deepEqual({tests: lane.tests, passed: lane.passed, failed: lane.failed, skipped: lane.skipped}, {tests: 5, passed: 5, failed: 0, skipped: 0});
    assert.deepEqual(lane.identities.map((item: any) => item.tool), ["tsc", "tsx", "cargo", "rustc"]);
    assert.ok(lane.identities.slice(0, 2).every((item: any) => item.source === "package-lock" && item.executable_relative.startsWith("node_modules/")));
    assert.ok(lane.identities.slice(2).every((item: any) => item.source === "explicit-version-bound" && item.expected_version === "1.98.1" && item.observed_version === "1.98.1"));
  }
  assert.deepEqual([value.host.identities[0].package_version, value.host.identities[1].package_version], ["6.0.3", "4.20.6"]);
  assert.equal(value.container.network, "none"); assert.equal(value.container.root_filesystem, "read-only");
  assert.equal(value.container.source_mount, "read-only"); assert.equal(value.container.rust_mount, "read-only");
  const toolchain = JSON.parse(fs.readFileSync(path.join(checkoutRoot, value.bindings.node_toolchain.path), "utf8"));
  assert.equal(value.container.image, toolchain.container_image);
  if (checkImage) {
    const current = spawnSync("docker", ["image", "inspect", value.container.image, "--format", "{{.Id}}"], {encoding: "utf8"});
    assert.equal(current.status, 0, current.stderr); assert.equal(current.stdout.trim(), value.container.image_id);
  }
  assert.ok(Object.values(value.hard_stops).every((item) => item === false));
  assert.match(value.claim_ceiling, /O01 host\/container tool-resolution parity only/u);
  assert.equal(value.open_questions.length, 2);
}

test("O01 qualification binds exact host and container tool identities", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("O01 qualification rejects drift, ambient fallback, path repair and weaker parity", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.bindings.runner.sha256 = "0".repeat(64); },
    (value: any) => { value.container.passed = 4; },
    (value: any) => { value.container.identities[0].source = "PATH"; },
    (value: any) => { value.container.identities[2].observed_version = "1.98.0"; },
    (value: any) => { value.hard_stops.path_repair_or_symlink_created = true; },
  ]) {
    const changed = structuredClone(original); mutate(changed); assert.throws(() => validate(changed, false));
  }
});
