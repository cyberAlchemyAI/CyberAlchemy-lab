import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { buildReleaseCandidate } from "../../tools/build-release-candidate.mjs";
import { canonicalJson, sha256, verifyReleaseCandidate, verifyQualificationEvidence } from "../../tools/verify-release-candidate.mjs";

function run(command, args, cwd, extraEnvironment = {}) {
  const result = spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    env: { ...process.env, npm_config_audit: "false", npm_config_fund: "false", npm_config_update_notifier: "false", ...extraEnvironment },
  });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout.trim();
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function createSource(root, fakeGit) {
  writeJson(path.join(root, "package.json"), {
    name: "@domainspec-v2/cli",
    version: "1.0.0",
    private: false,
    type: "module",
    bin: { "domainspec-v2": "./dist/cli/main.js" },
    exports: { ".": "./dist/index.js" },
    files: ["dist", "README.md"],
    engines: { node: "26.8.1", npm: "11.19.0" },
    packageManager: "npm@11.19.0",
    scripts: { build: "node synthetic-build.mjs" },
  });
  writeJson(path.join(root, "package-lock.json"), {
    name: "@domainspec-v2/cli",
    version: "1.0.0",
    lockfileVersion: 3,
    requires: true,
    packages: {
      "": {
        name: "@domainspec-v2/cli",
        version: "1.0.0",
        bin: { "domainspec-v2": "dist/cli/main.js" },
        engines: { node: "26.8.1", npm: "11.19.0" },
      },
    },
  });
  fs.writeFileSync(path.join(root, "README.md"), "# Synthetic DomainSpec release candidate\n");
  fs.writeFileSync(path.join(root, "product-value.txt"), "one\n");
  fs.writeFileSync(path.join(root, "synthetic-build.mjs"), "import fs from 'node:fs';\nimport path from 'node:path';\nconst value = fs.readFileSync('product-value.txt', 'utf8').trim();\nfs.mkdirSync(path.join('dist', 'cli'), { recursive: true });\nfs.writeFileSync(path.join('dist', 'index.js'), `export const releaseCandidateFixture = '${value}';\\n`);\nfs.writeFileSync(path.join('dist', 'cli', 'main.js'), `#!/usr/bin/env node\\nprocess.stdout.write('1.0.0\\\\n');\\n`, { mode: 0o755 });\n");
  fs.writeFileSync(path.join(root, "pnpm-lock.yaml"), "lockfileVersion: '9.0'\n");
  const commit = "1".repeat(40);
  fs.writeFileSync(path.join(root, ".release-commit"), `${commit}\n`);
  fs.writeFileSync(path.join(root, ".release-status"), "");
  fs.writeFileSync(fakeGit, `#!/bin/sh\ncase "$1 $2" in\n  "rev-parse HEAD") cat .release-commit ;;\n  "status --porcelain=v1") cat .release-status ;;\n  "config --get") printf '%s\\n' 'https://example.invalid/domainspec-core.git' ;;\n  *) exit 64 ;;\nesac\n`, { mode: 0o755 });
  return commit;
}

function createQualification(root) {
  const fixture = JSON.parse(fs.readFileSync(new URL("./fixtures/qualification.json", import.meta.url), "utf8"));
  writeJson(path.join(root, "qualification-profile.json"), fixture.profile);
  for (const run of ["run-1", "run-2"]) {
    for (const [name, value] of [["plan", fixture.plan], ["certificate", fixture.certificate], ["run-receipt", fixture.receipt]]) {
      writeJson(path.join(root, run, `qualification-${name}.json`), value);
    }
    fs.mkdirSync(path.join(root, run, "evidence"));
    for (const [name, value] of Object.entries(fixture.evidence)) fs.writeFileSync(path.join(root, run, name), value);
  }
  writeJson(path.join(root, "equivalence.json"), { ...fixture.equivalence, evidence_root: root });
}

function byteInventory(root) {
  const rows = [];
  function visit(relative) {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort((left, right) => left.name < right.name ? -1 : left.name > right.name ? 1 : 0)) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isDirectory()) visit(child);
      else {
        const bytes = fs.readFileSync(path.join(root, child));
        rows.push({ path: child, size: bytes.length, sha256: crypto.createHash("sha256").update(bytes).digest("hex") });
      }
    }
  }
  visit("");
  return rows;
}

function installAndObserve(tarball, consumer, npmEnvironment) {
  fs.mkdirSync(consumer);
  writeJson(path.join(consumer, "package.json"), { private: true, type: "module" });
  run("npm", ["install", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", tarball], consumer, npmEnvironment);
  const imported = run(process.execPath, ["--input-type=module", "-e", "const value = await import('@domainspec-v2/cli'); process.stdout.write(value.releaseCandidateFixture);"], consumer, npmEnvironment);
  const version = run(path.join(consumer, "node_modules", ".bin", "domainspec-v2"), [], consumer, npmEnvironment);
  return { imported, version };
}

function mutateJson(root, relative, mutate, digestKey = null) {
  const file = path.join(root, relative);
  let value = JSON.parse(fs.readFileSync(file, "utf8"));
  value = mutate(value) ?? value;
  if (digestKey && value && typeof value === "object" && !Array.isArray(value)) {
    delete value[digestKey]; value[digestKey] = sha256(canonicalJson(value));
  }
  writeJson(file, value);
}

// Refresh outer bindings deliberately: checksum rejection alone cannot prove
// that semantic inconsistencies inside qualification records are detected.
function refreshBundle(root) {
  const certificate = JSON.parse(fs.readFileSync(path.join(root, "qualification/run-1/qualification-certificate.json"), "utf8"));
  const rows = () => byteInventory(root).map(({ path, size, sha256 }) => ({ path, size_bytes: size, sha256 }));
  mutateJson(root, "candidate.json", (c) => {
    c.artifacts = rows().filter(({ path }) => !["candidate.json", "SHA256SUMS", "verify-release-candidate.mjs"].includes(path));
    c.qualification.evidence_inventory_sha256 = sha256(canonicalJson(c.artifacts.filter(({ path }) => path.startsWith("qualification/"))));
    c.qualification.certificate_sha256 = certificate?.certificate_sha256;
  }, "manifest_sha256");
  fs.writeFileSync(path.join(root, "SHA256SUMS"), rows().filter(({ path }) => path !== "SHA256SUMS").sort((a, b) => a.path < b.path ? -1 : 1).map(({ path, sha256 }) => `${sha256}  ${path}`).join("\n") + "\n");
}

const qualificationMutants = [
  ["C04 stale certificate digest with failed observation", "observations-pass", "certificate", (c) => { c.observations[0].result = "fail"; }, null],
  ["failed observation with refreshed self-digest", "observations-pass", "certificate", (c) => { c.observations[0].result = "fail"; }, "certificate_sha256"],
  ["not evaluable observation", "observations-pass", "certificate", (c) => { c.observations[0].result = "not_evaluable"; }, "certificate_sha256"],
  ["missing observation", "observations-pass", "certificate", (c) => { c.observations.pop(); }, "certificate_sha256"],
  ["duplicate observation", "observations-pass", "certificate", (c) => { c.observations[1] = c.observations[0]; }, "certificate_sha256"],
  ["wrong observation binding", "observations-pass", "certificate", (c) => { c.observations[0].input_sha256 = "0".repeat(64); }, "certificate_sha256"],
  ["causal blocker on pass", "observations-pass", "certificate", (c) => { c.observations[0].causal_blockers = ["terraform-init-backendless"]; }, "certificate_sha256"],
  ["unknown certificate member", "certificate", "certificate", (c) => { c.approved = true; }, "certificate_sha256"],
  ["malformed observations", "observations-pass", "certificate", (c) => { c.observations = {}; }, "certificate_sha256"],
  ["null observation", "observations-pass", "certificate", (c) => { c.observations[0] = null; }, "certificate_sha256"],
  ["wrong certificate schema", "certificate", "certificate", (c) => { c.schema_version = "unexpected"; }, "certificate_sha256"],
  ["certificate plan link", "certificate", "certificate", (c) => { c.plan_sha256 = "0".repeat(64); }, "certificate_sha256"],
  ["certificate subject link", "certificate", "certificate", (c) => { c.subject.project_id = "wrong-project"; }, "certificate_sha256"],
  ["certificate profile link", "certificate", "certificate", (c) => { c.profile_id = "wrong-profile"; }, "certificate_sha256"],
  ["authority ceiling", "certificate", "certificate", (c) => { c.authority_effect = "release"; }, "certificate_sha256"],
  ["missing tools", "toolchain", "certificate", (c) => { c.toolchain = []; }, "certificate_sha256"],
  ["stale tool identity", "toolchain", "certificate", (c) => { c.toolchain[0].executable_sha256 = "0".repeat(64); }, "certificate_sha256"],
  ["tool reference", "observations-pass", "certificate", (c) => { c.observations[1].tool_identity_sha256 = "0".repeat(64); }, "certificate_sha256"],
  ["provider lock reference", "observations-pass", "certificate", (c) => { c.observations[3].provider_lock_sha256 = "0".repeat(64); }, "certificate_sha256"],
  ["stale plan digest", "plan", "plan", (p) => { p.subject.project_id = "wrong-project"; }, null],
  ["weakened required check", "plan", "plan", (p) => { p.checks[0].required = false; }, "plan_sha256"],
  ["stale receipt digest", "receipt", "run-receipt", (r) => { r.evidence[0].exit_code = 1; }, null],
  ["failed process with pass receipt", "evidence", "run-receipt", (r) => { r.evidence[0].exit_code = 1; }, "receipt_sha256"],
  ["blocked process with pass receipt", "evidence", "run-receipt", (r) => { r.evidence[0].termination = "blocked"; }, "receipt_sha256"],
  ["receipt certificate link", "receipt", "run-receipt", (r) => { r.certificate_sha256 = "0".repeat(64); }, "receipt_sha256"],
  ["receipt evidence digest", "evidence", "run-receipt", (r) => { r.evidence[0].stdout_sha256 = "0".repeat(64); }, "receipt_sha256"],
  ["receipt evidence path traversal", "evidence", "run-receipt", (r) => { r.evidence[0].stdout_path = "../../outside.txt"; }, "receipt_sha256"],
  ["malformed receipt evidence", "evidence", "run-receipt", (r) => { r.evidence = {}; }, "receipt_sha256"],
];

test("release candidate is deterministic, independently verifiable, installable, hostile-sensitive, and source-sensitive", async (t) => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-release-candidate-test-"));
  try {
    const npmUserConfig = path.join(temporary, "npm-user.conf"), npmGlobalConfig = path.join(temporary, "npm-global.conf");
    fs.writeFileSync(npmUserConfig, ""); fs.writeFileSync(npmGlobalConfig, "");
    const npmEnvironment = {npm_config_cache: path.join(temporary, "npm-cache"), npm_config_userconfig: npmUserConfig, npm_config_globalconfig: npmGlobalConfig};
    const source = path.join(temporary, "source");
    const qualification = path.join(temporary, "qualification");
    fs.mkdirSync(source);
    fs.mkdirSync(qualification);
    const fakeGit = path.join(temporary, "fake-git");
    const firstCommit = createSource(source, fakeGit);
    createQualification(qualification);
    const first = path.join(temporary, "candidate-one");
    const second = path.join(temporary, "candidate-two");
    const firstBuild = buildReleaseCandidate({ repositoryRoot: source, packageRoot: source, qualificationEvidenceRoot: qualification, outputRoot: first, sourceCommit: firstCommit, gitExecutable: fakeGit, sourceSnapshotRoot: source });
    const secondBuild = buildReleaseCandidate({ repositoryRoot: source, packageRoot: source, qualificationEvidenceRoot: qualification, outputRoot: second, sourceCommit: firstCommit, gitExecutable: fakeGit, sourceSnapshotRoot: source });
    assert.equal(firstBuild.result, "pass");
    assert.equal(firstBuild.authority_effect, "none");
    assert.deepEqual(byteInventory(first), byteInventory(second));
    const firstVerification = verifyReleaseCandidate(first, firstCommit);
    assert.equal(firstVerification.result, "pass", JSON.stringify(firstVerification, null, 2));
    const command = spawnSync(process.execPath, [path.join(first, "verify-release-candidate.mjs"), "--bundle-root", first, "--expected-source-commit", firstCommit], { encoding: "utf8" });
    assert.equal(command.status, 0, command.stderr);
    assert.equal(JSON.parse(command.stdout).result, "pass");

    for (const [index, [name, expectedCheck, record, mutate, digestKey]] of qualificationMutants.entries()) {
      await t.test(name, () => {
        const mutant = path.join(temporary, `internal-mutant-${index}`);
        fs.cpSync(first, mutant, { recursive: true });
        for (const run of ["run-1", "run-2"]) mutateJson(mutant, `qualification/${run}/qualification-${record}.json`, mutate, digestKey);
        refreshBundle(mutant);
        const verification = verifyReleaseCandidate(mutant, firstCommit);
        assert.equal(verification.result, "fail");
        assert.equal(verification.checks.find(({ id }) => id === "checksums-current").result, "pass");
        assert.equal(verification.checks.find(({ id }) => id === "candidate-self-digest").result, "pass");
        assert.equal(verification.checks.find(({ id }) => id === `run-1:${expectedCheck}`).result, "fail");
        const rejectedOutput = path.join(temporary, `rejected-${index}`);
        assert.throws(() => buildReleaseCandidate({ repositoryRoot: source, packageRoot: source, qualificationEvidenceRoot: path.join(mutant, "qualification"), outputRoot: rejectedOutput, sourceCommit: firstCommit, gitExecutable: fakeGit, sourceSnapshotRoot: source }), /qualification evidence is inconsistent/);
        assert.equal(fs.existsSync(rejectedOutput), false);
      });
    }
    await t.test("profile, equivalence and raw evidence cannot contradict the passing summary", () => {
      const cases = [
        ["profile", (root) => mutateJson(root, "qualification-profile.json", (p) => { p.required_checks = []; }, "profile_sha256")],
        ["equivalence", (root) => mutateJson(root, "equivalence.json", (e) => { e.checks[0].result = "fail"; })],
        ["evidence", (root) => fs.appendFileSync(path.join(root, "run-1/evidence/recipe-byte-verify.stdout.txt"), "changed")],
        ["extra", (root) => fs.writeFileSync(path.join(root, "unexpected.txt"), "extra")],
        ["symlink", (root) => { const file = path.join(root, "run-1/evidence/recipe-byte-verify.stdout.txt"); fs.unlinkSync(file); fs.symlinkSync("/unreadable-outside", file); }],
      ];
      for (const [name, mutate] of cases) {
        const root = path.join(temporary, `bad-${name}`);
        fs.cpSync(qualification, root, { recursive: true }); mutate(root);
        assert.equal(verifyQualificationEvidence(root).result, "fail", name);
      }
    });

    const tarball = path.join(first, "package", "domainspec-v2-cli-1.0.0.tgz");
    assert.deepEqual(installAndObserve(tarball, path.join(temporary, "consumer-one"), npmEnvironment), { imported: "one", version: "1.0.0" });
    assert.deepEqual(installAndObserve(tarball, path.join(temporary, "consumer-two"), npmEnvironment), { imported: "one", version: "1.0.0" });

    const tamperedPackage = path.join(temporary, "tampered-package");
    fs.cpSync(first, tamperedPackage, { recursive: true });
    fs.appendFileSync(path.join(tamperedPackage, "package", "domainspec-v2-cli-1.0.0.tgz"), "tamper");
    assert.equal(verifyReleaseCandidate(tamperedPackage, firstCommit).result, "fail");
    const missingEvidence = path.join(temporary, "missing-evidence");
    fs.cpSync(first, missingEvidence, { recursive: true });
    fs.rmSync(path.join(missingEvidence, "qualification", "run-2", "qualification-certificate.json"));
    assert.equal(verifyReleaseCandidate(missingEvidence, firstCommit).result, "fail");

    fs.writeFileSync(path.join(source, "product-value.txt"), "two\n");
    fs.writeFileSync(path.join(source, ".release-status"), " M product-value.txt\n");
    assert.throws(() => buildReleaseCandidate({ repositoryRoot: source, packageRoot: source, qualificationEvidenceRoot: qualification, outputRoot: path.join(temporary, "dirty-candidate"), sourceCommit: firstCommit, gitExecutable: fakeGit, sourceSnapshotRoot: source }), /clean source tree/);
    const secondCommit = "2".repeat(40);
    fs.writeFileSync(path.join(source, ".release-commit"), `${secondCommit}\n`);
    fs.writeFileSync(path.join(source, ".release-status"), "");
    const changed = path.join(temporary, "candidate-changed");
    const changedBuild = buildReleaseCandidate({ repositoryRoot: source, packageRoot: source, qualificationEvidenceRoot: qualification, outputRoot: changed, sourceCommit: secondCommit, gitExecutable: fakeGit, sourceSnapshotRoot: source });
    assert.notEqual(changedBuild.package_sha256, firstBuild.package_sha256);
    assert.notEqual(changedBuild.manifest_sha256, firstBuild.manifest_sha256);
    assert.notEqual(canonicalJson(JSON.parse(fs.readFileSync(path.join(changed, "candidate.json")))), canonicalJson(JSON.parse(fs.readFileSync(path.join(first, "candidate.json")))));
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
});
