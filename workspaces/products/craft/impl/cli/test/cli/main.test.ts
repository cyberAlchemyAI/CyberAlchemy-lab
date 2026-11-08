import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { runCli } from "../../src/cli/main.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");
const authOperationSource = path.resolve(testDir, "../../../../../auth-foundation/implementation/operation-source");
const capacityOperationSource = path.resolve(testDir, "../fixtures/capacity-decision");

function fixture(): { parent: string; source: string; target: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-e2e-"));
  const source = path.join(parent, "source");
  fs.cpSync(fixtureRoot, source, { recursive: true });
  return { parent, source, target: path.join(parent, "target") };
}

function snapshot(root: string): string {
  const rows: string[] = [];
  function visit(relative: string): void {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isDirectory()) visit(child);
      else rows.push(`${child}\0${fs.readFileSync(path.join(root, child), "hex")}`);
    }
  }
  visit("");
  return rows.join("\n");
}

const addCreateOrderArgs = (source: string): string[] => [
  "add", "operation", source,
  "--feature", "alpha",
  "--name", "create-order",
  "--description", "Create an order from the current cart.",
  "--reads", "customer.status,cart.total",
  "--writes", "order.id,order.status,order.total",
  "--effects", "OrderCreated",
  "--guard", "customer-is-active-and-cart-is-valid",
  "--failure-continuation", "return-create-order-error",
];

test("add operation authors, validates, saves, and instantiates one canonical Operation", () => {
  const { parent, source, target } = fixture();
  try {
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };

    assert.equal(runCli(addCreateOrderArgs(source), io), 0);
    const authored = JSON.parse(out.pop()!);
    assert.equal(authored.result, "pass");
    assert.equal(authored.selector, "alpha:create-order");
    assert.equal(authored.node_path, "specs/alpha/nodes/create-order.json");
    assert.equal(authored.source_count, 22);
    assert.match(authored.source_manifest_sha256, /^[a-f0-9]{64}$/);
    assert.deepEqual(errors, []);

    const feature = JSON.parse(fs.readFileSync(path.join(source, "specs/alpha/feature.json"), "utf8"));
    assert.deepEqual(feature.nodes, ["create-order", "customer", "settle", "settlement-api"]);
    const node = JSON.parse(fs.readFileSync(path.join(source, authored.node_path), "utf8"));
    assert.deepEqual(node, {
      schema_version: "domainspec.node/v1",
      node_id: "create-order",
      feature_id: "alpha",
      kind: "Operation",
      body: {
        description: "Create an order from the current cart.",
        reads: ["customer.status", "cart.total"],
        writes: ["order.id", "order.status", "order.total"],
        effects: ["OrderCreated"],
        guard: "customer-is-active-and-cart-is-valid",
        failure_continuation: "return-create-order-error",
      },
    });

    assert.equal(runCli(["lint", source], io), 0);
    const sourceLint = JSON.parse(out.pop()!);
    assert.equal(sourceLint.result, "pass");
    assert.equal(sourceLint.source_manifest.manifest_sha256, authored.source_manifest_sha256);

    assert.equal(runCli(["instantiate", source, "--node", "alpha:create-order", "--language", "typescript", "--target-root", target], io), 0);
    const instantiated = JSON.parse(out.pop()!);
    assert.equal(instantiated.result, "pass");
    assert.equal(instantiated.observation.result, "pass");
    const artifact = instantiated.observation.observed_artifacts[0].relative_path;
    const content = fs.readFileSync(path.join(target, artifact), "utf8");
    assert.match(content, /export function createOrder\(/);
    assert.match(content, /const outbox = CreateOrderContract\.effects\.map/);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("add operation is deterministic for byte-identical roots", () => {
  const left = fixture();
  const right = fixture();
  try {
    const outputs: Record<string, unknown>[] = [];
    for (const source of [left.source, right.source]) {
      const out: string[] = [];
      const errors: string[] = [];
      assert.equal(runCli(addCreateOrderArgs(source), { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0);
      outputs.push(JSON.parse(out.pop()!));
      assert.deepEqual(errors, []);
    }
    assert.equal(outputs[0]?.source_manifest_sha256, outputs[1]?.source_manifest_sha256);
    assert.equal(
      fs.readFileSync(path.join(left.source, "specs/alpha/nodes/create-order.json"), "utf8"),
      fs.readFileSync(path.join(right.source, "specs/alpha/nodes/create-order.json"), "utf8"),
    );
    assert.equal(
      fs.readFileSync(path.join(left.source, "specs/alpha/feature.json"), "utf8"),
      fs.readFileSync(path.join(right.source, "specs/alpha/feature.json"), "utf8"),
    );
  } finally {
    fs.rmSync(left.parent, { recursive: true, force: true });
    fs.rmSync(right.parent, { recursive: true, force: true });
  }
});

test("add operation conflicts and invalid arguments leave the source unchanged", () => {
  const { parent, source } = fixture();
  try {
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    const before = snapshot(source);

    const missingFeature = addCreateOrderArgs(source);
    missingFeature[missingFeature.indexOf("alpha")] = "missing";
    assert.equal(runCli(missingFeature, io), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_AUTHORING_FEATURE_MISSING");
    assert.equal(snapshot(source), before);

    const duplicateRead = addCreateOrderArgs(source);
    duplicateRead[duplicateRead.indexOf("customer.status,cart.total")] = "cart.total,cart.total";
    assert.equal(runCli(duplicateRead, io), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_USAGE");
    assert.equal(snapshot(source), before);

    assert.equal(runCli(addCreateOrderArgs(source), io), 0);
    out.pop();
    const authored = snapshot(source);
    assert.equal(runCli(addCreateOrderArgs(source), io), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_AUTHORING_NODE_EXISTS");
    assert.equal(snapshot(source), authored);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("add operation honors the exclusive source-authoring lock", () => {
  const { parent, source } = fixture();
  const lockPath = path.join(parent, ".source.domainspec-authoring.lock");
  try {
    const before = snapshot(source);
    fs.writeFileSync(lockPath, "owned\n", { flag: "wx" });
    const errors: string[] = [];
    assert.equal(runCli(addCreateOrderArgs(source), { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_AUTHORING_LOCKED");
    assert.equal(snapshot(source), before);
  } finally {
    fs.rmSync(lockPath, { force: true });
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("instantiate, lint, and receipt form an isolated read-only-source end-to-end path", () => {
  const { parent, source, target } = fixture();
  try {
    const before = snapshot(source);
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli(["instantiate", source, "--node", "alpha:customer", "--language", "typescript", "--target-root", target], io), 0);
    const commandResult = JSON.parse(out.pop()!);
    assert.equal(commandResult.result, "pass");
    assert.equal(commandResult.observation.result, "pass");
    assert.equal(snapshot(source), before);
    assert.deepEqual(errors, []);

    assert.equal(runCli(["lint", target], io), 0);
    assert.equal(JSON.parse(out.pop()!).result, "pass");
    assert.equal(runCli(["receipt", target], io), 0);
    const receiptResult = JSON.parse(out.pop()!);
    assert.equal(receiptResult.receipt.input.meta_type_id, "DS-D1.1");
    assert.equal(receiptResult.observation.result, "pass");
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("standard CLI instantiates the property-closed Auth Operation as compilable Rust", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-e2e-"));
  const target = path.join(parent, "target");
  try {
    const before = snapshot(authOperationSource);
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli(["instantiate", authOperationSource, "--node", "auth-exact-permission:authorize", "--language", "rust", "--target-root", target], io), 0);
    const commandResult = JSON.parse(out.pop()!);
    assert.equal(commandResult.result, "pass");
    assert.equal(commandResult.observation.result, "pass");
    assert.equal(snapshot(authOperationSource), before);
    assert.deepEqual(errors, []);

    assert.equal(runCli(["receipt", target], io), 0);
    const receiptResult = JSON.parse(out.pop()!);
    const closure = receiptResult.receipt.semantic_contract.typed_closure;
    assert.equal(closure.properties.length, 22);
    assert.equal(closure.variants.length, 15);
    assert.equal(closure.rules.length, 8);
    const artifact = path.join(target, receiptResult.receipt.artifacts[0].relative_path);
    const compiled = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", "-D", "warnings", artifact, "-o", path.join(parent, "auth-operation.rlib")], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr);
    const formatted = spawnSync("rustfmt", ["--edition", "2024", "--check", artifact], { encoding: "utf8" });
    assert.equal(formatted.status, 0, formatted.stderr);
    const cargoCheck = spawnSync("cargo", ["check"], { cwd: target, encoding: "utf8" });
    assert.equal(cargoCheck.status, 0, cargoCheck.stderr);
    const cargoTest = spawnSync("cargo", ["test"], { cwd: target, encoding: "utf8" });
    assert.equal(cargoTest.status, 0, cargoTest.stderr);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("standard CLI instantiates and executes a second non-Auth typed Operation", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-capacity-e2e-"));
  const target = path.join(parent, "target");
  try {
    const before = snapshot(capacityOperationSource);
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli(["instantiate", capacityOperationSource, "--node", "capacity-decision:decide-capacity", "--language", "rust", "--target-root", target], io), 0);
    const commandResult = JSON.parse(out.pop()!);
    assert.equal(commandResult.result, "pass");
    assert.equal(commandResult.observation.result, "pass");
    assert.equal(snapshot(capacityOperationSource), before);
    assert.deepEqual(errors, []);

    assert.equal(runCli(["receipt", target], io), 0);
    const receipt = JSON.parse(out.pop()!).receipt;
    assert.equal(receipt.semantic_contract.typed_closure.properties.length, 3);
    assert.equal(receipt.semantic_contract.typed_closure.variants.length, 2);
    assert.equal(receipt.semantic_contract.typed_closure.rules.length, 1);
    const artifact = path.join(target, receipt.artifacts[0].relative_path);
    const compiled = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", "-D", "warnings", artifact, "-o", path.join(parent, "capacity-operation.rlib")], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr);
    const formatted = spawnSync("rustfmt", ["--edition", "2024", "--check", artifact], { encoding: "utf8" });
    assert.equal(formatted.status, 0, formatted.stderr);
    const cargoCheck = spawnSync("cargo", ["check"], { cwd: target, encoding: "utf8" });
    assert.equal(cargoCheck.status, 0, cargoCheck.stderr);

    const harness = path.join(parent, "capacity-behavior.rs");
    fs.writeFileSync(harness, `#![allow(dead_code)]\n#[path = ${JSON.stringify(artifact)}]\nmod generated;\nuse generated::*;\n#[test]\nfn capacity_boundary() {\n    assert_eq!(decide_capacity(&CapacitySnapshot { request_id: \"below\".into(), requested_units: 2, available_units: 3 }), CapacityDecision::Accept);\n    assert_eq!(decide_capacity(&CapacitySnapshot { request_id: \"equal\".into(), requested_units: 3, available_units: 3 }), CapacityDecision::Reject);\n}\n`);
    const behavior = spawnSync("rustc", ["--edition", "2024", "--test", harness, "-o", path.join(parent, "capacity-behavior")], { encoding: "utf8" });
    assert.equal(behavior.status, 0, behavior.stderr);
    const executed = spawnSync(path.join(parent, "capacity-behavior"), [], { encoding: "utf8" });
    assert.equal(executed.status, 0, executed.stderr);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("typed Operation rejects deferred languages before creating a target", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-e2e-"));
  const target = path.join(parent, "target");
  try {
    const errors: string[] = [];
    assert.notEqual(runCli(["instantiate", authOperationSource, "--node", "auth-exact-permission:authorize", "--language", "typescript", "--target-root", target], { stdout: () => undefined, stderr: (value) => errors.push(value) }), 0);
    assert.equal(fs.existsSync(target), false);
    assert.match(JSON.parse(errors.pop()!).message, /typed Operation realization is not supported/);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("instantiate explicitly selects and observes a provider-neutral system-integration profile", () => {
  const { parent, source, target } = fixture();
  try {
    const before = snapshot(source);
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli([
      "instantiate",
      source,
      "--node", "alpha:settle",
      "--language", "typescript",
      "--target-root", target,
      "--integration-profile", "provider-neutral-v1",
      "--integration-binding-set", "settle-runtime",
    ], io), 0);
    const commandResult = JSON.parse(out.pop()!);
    assert.equal(commandResult.result, "pass");
    assert.match(commandResult.system_integration_binding_digest, /^[a-f0-9]{64}$/);
    assert.equal(commandResult.observation.observed_artifacts.length, 2);
    assert.equal(commandResult.observation.checks.includes("system-integration-profile-when-selected"), true);
    assert.equal(snapshot(source), before);
    assert.deepEqual(errors, []);

    assert.equal(runCli(["receipt", target], io), 0);
    const receiptResult = JSON.parse(out.pop()!);
    assert.equal(receiptResult.receipt.system_integration.profile_selector, "provider-neutral-v1");
    assert.equal(receiptResult.receipt.system_integration.manifest.runtime_guarantees_observed, false);
    assert.equal(receiptResult.observation.result, "pass");
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("system-integration profile options are an explicit pair", () => {
  const { parent, source, target } = fixture();
  try {
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli([
      "instantiate", source,
      "--node", "alpha:settle",
      "--language", "typescript",
      "--target-root", target,
      "--integration-profile", "provider-neutral-v1",
    ], io), 22);
    assert.equal(fs.existsSync(target), false);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_USAGE");
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("unknown language and existing targets fail without source or target mutation", () => {
  const { parent, source, target } = fixture();
  try {
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    const before = snapshot(source);
    assert.notEqual(runCli(["instantiate", source, "--node", "alpha:customer", "--language", "java", "--target-root", target], io), 0);
    assert.equal(fs.existsSync(target), false);
    assert.equal(snapshot(source), before);
    fs.mkdirSync(target);
    fs.writeFileSync(path.join(target, "sentinel"), "preserve");
    assert.notEqual(runCli(["instantiate", source, "--node", "alpha:customer", "--language", "typescript", "--target-root", target], io), 0);
    assert.equal(fs.readFileSync(path.join(target, "sentinel"), "utf8"), "preserve");
    assert.equal(errors.length, 2);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("lint and receipt emit causal failure receipts with nonzero status", () => {
  const { parent, source, target } = fixture();
  try {
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli(["instantiate", source, "--node", "alpha:customer", "--language", "typescript", "--target-root", target], io), 0);
    const created = JSON.parse(out.pop()!);
    const artifact = created.observation.observed_artifacts[0].relative_path;
    fs.appendFileSync(path.join(target, artifact), "// drift\n");

    assert.equal(runCli(["lint", target], io), 1);
    const lint = JSON.parse(out.pop()!);
    assert.equal(lint.schema_version, "domainspec.target-observation/v1");
    assert.equal(lint.result, "fail");
    assert.equal(lint.code, "MTCLI_OBSERVE_EXACT_REALIZATION");

    assert.equal(runCli(["receipt", target], io), 1);
    const receipt = JSON.parse(out.pop()!);
    assert.equal(receipt.observation.result, "fail");
    assert.equal(receipt.observation.code, "MTCLI_OBSERVE_EXACT_REALIZATION");
    assert.deepEqual(errors, []);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("source lint and receipt execute project-wide relationship validation", () => {
  const { parent, source } = fixture();
  try {
    const edgePath = path.join(source, "specs/alpha/edges/customer-performs-settle.json");
    const edge = JSON.parse(fs.readFileSync(edgePath, "utf8"));
    edge.relationship = "announces";
    fs.writeFileSync(edgePath, `${JSON.stringify(edge, null, 2)}\n`);
    const out: string[] = [];
    const errors: string[] = [];
    const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
    assert.equal(runCli(["lint", source], io), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_RELATIONSHIP_UNKNOWN");
    assert.equal(runCli(["receipt", source], io), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_RELATIONSHIP_UNKNOWN");
    assert.deepEqual(out, []);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});
