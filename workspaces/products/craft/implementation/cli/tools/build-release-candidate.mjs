#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { canonicalJson, sha256, verifyReleaseCandidate, verifyQualificationEvidence } from "./verify-release-candidate.mjs";

const EXPECTED_NODE = "26.8.1";
const EXPECTED_NPM = "11.19.0";
const EXPECTED_PACKAGE = "@domainspec-v2/cli";
const EXPECTED_VERSION = "1.0.0";
const COMMIT = /^[a-f0-9]{40}$/;
const gitExecutable = process.env.DOMAINSPEC_RELEASE_GIT ?? "/usr/bin/git";
const tarExecutable = process.env.DOMAINSPEC_RELEASE_TAR ?? "/usr/bin/tar";
const toolRoot = path.dirname(fileURLToPath(import.meta.url));
const defaultPackageRoot = path.resolve(toolRoot, "..");
const defaultRepositoryRoot = path.resolve(defaultPackageRoot, "../../../..");
const verifierSource = path.join(toolRoot, "verify-release-candidate.mjs");

function run(command, args, cwd, extraEnvironment = {}) {
  const result = spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
    env: {
      ...process.env,
      npm_config_audit: "false",
      npm_config_fund: "false",
      npm_config_update_notifier: "false",
      ...extraEnvironment,
    },
  });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout ?? ""}\n${result.stderr ?? ""}`);
  return result.stdout.trim();
}

function exactSystemTool(executable, label) {
  if (!path.isAbsolute(executable) || path.resolve(executable) !== executable) throw new Error(`${label} must be one normalized absolute path`);
  const stats = fs.statSync(executable);
  if (!stats.isFile() || (stats.mode & 0o111) === 0) throw new Error(`${label} must be one executable regular file`);
  return executable;
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
  fs.writeFileSync(file, `${canonicalJson(value)}\n`, { flag: "wx", mode: 0o600 });
}

function fileRow(root, relative) {
  const absolute = path.join(root, relative);
  const bytes = fs.readFileSync(absolute);
  return Object.freeze({ path: relative, size_bytes: bytes.length, sha256: sha256(bytes) });
}

function compareRows(left, right) {
  return left.path < right.path ? -1 : left.path > right.path ? 1 : 0;
}

function compareNames(left, right) {
  return left.name < right.name ? -1 : left.name > right.name ? 1 : 0;
}

function walk(root) {
  const rows = [];
  function visit(relative) {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort(compareNames)) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      const absolute = path.join(root, child);
      if (entry.isSymbolicLink()) throw new Error(`release inputs cannot contain symlinks:${child}`);
      if (entry.isDirectory()) visit(child);
      else if (entry.isFile()) rows.push(fileRow(root, child));
      else throw new Error(`release inputs must be regular files:${child}`);
    }
  }
  visit("");
  return rows;
}

function copyDirectory(source, target, transform = null) {
  const sourceStats = fs.lstatSync(source);
  if (!sourceStats.isDirectory() || sourceStats.isSymbolicLink() || fs.realpathSync(source) !== path.resolve(source)) throw new Error(`source must be one real directory:${source}`);
  fs.mkdirSync(target, { recursive: true, mode: 0o700 });
  for (const entry of fs.readdirSync(source, { withFileTypes: true }).sort(compareNames)) {
    const from = path.join(source, entry.name);
    const to = path.join(target, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`release inputs cannot contain symlinks:${from}`);
    if (entry.isDirectory()) copyDirectory(from, to, transform);
    else if (entry.isFile()) {
      const replacement = transform?.(from);
      if (replacement === undefined || replacement === null) fs.copyFileSync(from, to, fs.constants.COPYFILE_EXCL);
      else fs.writeFileSync(to, replacement, { flag: "wx", mode: 0o600 });
    } else throw new Error(`release inputs must be regular files:${from}`);
  }
}

function exactPackage(packageJson) {
  if (packageJson.name !== EXPECTED_PACKAGE || packageJson.version !== EXPECTED_VERSION || packageJson.private !== false) throw new Error("release candidate requires the exact public Stable 1.0 package identity");
  if (canonicalJson(packageJson.engines) !== canonicalJson({ node: EXPECTED_NODE, npm: EXPECTED_NPM })) throw new Error("release candidate requires the exact Node/npm engine contract");
  if (packageJson.packageManager !== `npm@${EXPECTED_NPM}`) throw new Error("release candidate requires the exact npm package-manager contract");
  if ("dependencies" in packageJson || "devDependencies" in packageJson) throw new Error("release candidate package must remain dependency-free");
}

function checkedGitIdentity(repositoryRoot, sourceCommit, selectedGitExecutable) {
  if (!COMMIT.test(sourceCommit)) throw new Error("source commit must be one lowercase 40-character git SHA");
  const git = exactSystemTool(selectedGitExecutable, "release git binding");
  const observed = run(git, ["rev-parse", "HEAD"], repositoryRoot);
  if (observed !== sourceCommit) throw new Error(`source commit mismatch:expected=${sourceCommit}:observed=${observed}`);
  const status = run(git, ["status", "--porcelain=v1", "--untracked-files=all"], repositoryRoot);
  if (status !== "") throw new Error(`release candidate requires a clean source tree\n${status}`);
  const repository = run(git, ["config", "--get", "remote.origin.url"], repositoryRoot);
  if (repository === "" || /https?:\/\/[^/@]+@/.test(repository)) throw new Error("source repository identity is absent or contains credentials");
  return Object.freeze({ repository, commit_sha: sourceCommit, tree_state: "clean" });
}

function qualificationBinding(evidenceRoot, targetRoot) {
  const verification = verifyQualificationEvidence(evidenceRoot);
  if (verification.result !== "pass") throw new Error(`qualification evidence is inconsistent\n${JSON.stringify(verification, null, 2)}`);
  const equivalencePath = path.join(evidenceRoot, "equivalence.json");
  const leftPath = path.join(evidenceRoot, "run-1", "qualification-certificate.json");
  const rightPath = path.join(evidenceRoot, "run-2", "qualification-certificate.json");
  const equivalence = JSON.parse(fs.readFileSync(equivalencePath, "utf8"));
  const left = JSON.parse(fs.readFileSync(leftPath, "utf8"));
  const right = JSON.parse(fs.readFileSync(rightPath, "utf8"));
  if (equivalence.schema_version !== "domainspec.recipe-qualification-l1-equivalence/v1" || equivalence.result !== "pass") throw new Error("qualification equivalence did not pass");
  if (left.result !== "pass" || right.result !== "pass" || canonicalJson(left) !== canonicalJson(right)) throw new Error("qualification certificates are not byte-equivalent passes");
  if (!/^[a-f0-9]{64}$/.test(left.certificate_sha256 ?? "") || equivalence.observed?.certificate_sha256 !== left.certificate_sha256) throw new Error("qualification certificate binding is invalid");
  copyDirectory(evidenceRoot, targetRoot, (file) => {
    if (file !== equivalencePath) return null;
    return `${canonicalJson({ ...equivalence, evidence_root: "qualification" })}\n`;
  });
  const rows = walk(targetRoot).map((row) => Object.freeze({ ...row, path: `qualification/${row.path}` }));
  return Object.freeze({
    level: "recipe-executable-v1",
    result: "pass",
    certificate_sha256: left.certificate_sha256,
    evidence_inventory_sha256: sha256(canonicalJson(rows)),
    normalization: "equivalence-evidence-root-relative-v1",
  });
}

function packageInventory(packageRoot, packageOutputRoot, scratchRoot) {
  const packedOutput = JSON.parse(run("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", packageOutputRoot], packageRoot, { npm_config_cache: path.join(scratchRoot, "npm-cache") }));
  if (!Array.isArray(packedOutput) || packedOutput.length !== 1 || packedOutput[0].filename !== "domainspec-v2-cli-1.0.0.tgz") throw new Error("npm produced an unexpected package subject");
  const filename = packedOutput[0].filename;
  const tarball = path.join(packageOutputRoot, filename);
  const packageBytes = fs.readFileSync(tarball);
  const extraction = path.join(scratchRoot, "extracted");
  fs.mkdirSync(extraction, { mode: 0o700 });
  run(exactSystemTool(tarExecutable, "release tar binding"), ["-xzf", tarball, "-C", extraction], packageRoot);
  const files = walk(extraction).sort(compareRows);
  if (!files.some(({ path: relative }) => relative === "package/package.json") || !files.some(({ path: relative }) => relative === "package/dist/cli/main.js")) throw new Error("packed release is missing required product files");
  const packageSubject = Object.freeze({ filename, sha256: sha256(packageBytes), size_bytes: packageBytes.length });
  const body = Object.freeze({ schema_version: "domainspec.release-package-inventory/v1", package: packageSubject, files: Object.freeze(files) });
  return Object.freeze({ ...body, inventory_sha256: sha256(canonicalJson(body)) });
}

function sourceSnapshot(repositoryRoot, packageRoot, sourceCommit, scratchRoot, selectedGitExecutable, injectedSourceRoot = null) {
  const snapshotRoot = path.join(scratchRoot, "source");
  if (injectedSourceRoot !== null) {
    copyDirectory(normalizedAbsolute(injectedSourceRoot, "injected source root"), snapshotRoot);
  } else {
    const archive = path.join(scratchRoot, "source.tar");
    const git = exactSystemTool(selectedGitExecutable, "release git binding");
    run(git, [
      "archive",
      "--format=tar",
      `--output=${archive}`,
      sourceCommit,
      "--",
      "projects/domainspec-v2",
      "toolchains/node-typescript/tsconfig",
      "pnpm-lock.yaml",
    ], repositoryRoot);
    fs.mkdirSync(snapshotRoot, { mode: 0o700 });
    run(exactSystemTool(tarExecutable, "release tar binding"), ["-xf", archive, "-C", snapshotRoot], repositoryRoot);

    const dependencyRoot = path.join(repositoryRoot, "projects", "domainspec-v2", "impl", "node_modules");
    const snapshotDependencyRoot = path.join(snapshotRoot, "projects", "domainspec-v2", "impl", "node_modules");
    const dependencyStats = fs.lstatSync(dependencyRoot);
    if (!dependencyStats.isDirectory() || dependencyStats.isSymbolicLink()) throw new Error("installed build dependencies must be one real directory");
    fs.symlinkSync(dependencyRoot, snapshotDependencyRoot, "dir");
  }

  const packageRelative = path.relative(repositoryRoot, packageRoot);
  if (packageRelative.startsWith("..") || path.isAbsolute(packageRelative)) throw new Error("package root must be inside repository root");
  const snapshotPackageRoot = path.join(snapshotRoot, packageRelative);
  const snapshotPackageStats = fs.lstatSync(snapshotPackageRoot);
  if (!snapshotPackageStats.isDirectory() || snapshotPackageStats.isSymbolicLink()) throw new Error("snapshotted package root must be one real directory");
  fs.rmSync(path.join(snapshotPackageRoot, "dist"), { recursive: true, force: true });
  run("npm", ["run", "build"], snapshotPackageRoot, { SOURCE_DATE_EPOCH: "0" });
  if (!fs.existsSync(path.join(snapshotPackageRoot, "dist", "cli", "main.js"))) throw new Error("isolated source build did not produce the Stable 1.0 CLI");
  return snapshotPackageRoot;
}

function spdx(packageBinding, inventory) {
  const files = inventory.files.map((item) => Object.freeze({
    fileName: `./${item.path}`,
    SPDXID: `SPDXRef-File-${sha256(item.path).slice(0, 24)}`,
    checksums: Object.freeze([{ algorithm: "SHA256", checksumValue: item.sha256 }]),
    licenseConcluded: "NOASSERTION",
    copyrightText: "NOASSERTION",
  }));
  return Object.freeze({
    spdxVersion: "SPDX-2.3",
    dataLicense: "CC0-1.0",
    SPDXID: "SPDXRef-DOCUMENT",
    name: "domainspec-v2-cli-1.0.0-release-candidate",
    documentNamespace: `https://domainspec.local/spdx/domainspec-v2-cli/${packageBinding.sha256}`,
    creationInfo: Object.freeze({ created: "1970-01-01T00:00:00Z", creators: Object.freeze(["Tool: domainspec-v2-release-candidate-builder/1"]) }),
    packages: Object.freeze([Object.freeze({
      name: EXPECTED_PACKAGE,
      SPDXID: "SPDXRef-Package-domainspec-v2-cli",
      versionInfo: EXPECTED_VERSION,
      packageFileName: packageBinding.filename,
      downloadLocation: "NOASSERTION",
      filesAnalyzed: true,
      checksums: Object.freeze([{ algorithm: "SHA256", checksumValue: packageBinding.sha256 }]),
      licenseConcluded: "NOASSERTION",
      licenseDeclared: "NOASSERTION",
      copyrightText: "NOASSERTION",
      primaryPackagePurpose: "APPLICATION",
    })]),
    files: Object.freeze(files),
    relationships: Object.freeze([
      Object.freeze({ spdxElementId: "SPDXRef-DOCUMENT", relationshipType: "DESCRIBES", relatedSpdxElement: "SPDXRef-Package-domainspec-v2-cli" }),
      ...files.map((file) => Object.freeze({ spdxElementId: "SPDXRef-Package-domainspec-v2-cli", relationshipType: "CONTAINS", relatedSpdxElement: file.SPDXID })),
    ]),
  });
}

function provenance(source, packageBinding, packageRoot, repositoryRoot, qualification) {
  const packageJson = fs.readFileSync(path.join(packageRoot, "package.json"));
  const packageLock = fs.readFileSync(path.join(packageRoot, "package-lock.json"));
  const workspaceLock = fs.readFileSync(path.join(repositoryRoot, "pnpm-lock.yaml"));
  return Object.freeze({
    _type: "https://in-toto.io/Statement/v1",
    subject: Object.freeze([Object.freeze({ name: packageBinding.filename, digest: Object.freeze({ sha256: packageBinding.sha256 }) })]),
    predicateType: "https://slsa.dev/provenance/v1",
    predicate: Object.freeze({
      buildDefinition: Object.freeze({
        buildType: "https://domainspec.local/build-types/npm-release-candidate/v1",
        externalParameters: Object.freeze({ package: EXPECTED_PACKAGE, version: EXPECTED_VERSION, sourceCommit: source.commit_sha, qualificationCertificateSha256: qualification.certificate_sha256 }),
        internalParameters: Object.freeze({ node: EXPECTED_NODE, npm: EXPECTED_NPM, sourceSnapshot: "git archive selected build closure", command: "npm run build && npm pack --json --ignore-scripts" }),
        resolvedDependencies: Object.freeze([
          Object.freeze({ uri: source.repository, digest: Object.freeze({ gitCommit: source.commit_sha }) }),
          Object.freeze({ uri: "file:projects/domainspec-v2/impl/cli/package.json", digest: Object.freeze({ sha256: sha256(packageJson) }) }),
          Object.freeze({ uri: "file:projects/domainspec-v2/impl/cli/package-lock.json", digest: Object.freeze({ sha256: sha256(packageLock) }) }),
          Object.freeze({ uri: "file:pnpm-lock.yaml", digest: Object.freeze({ sha256: sha256(workspaceLock) }) }),
          Object.freeze({ uri: "domainspec:recipe-qualification-certificate", digest: Object.freeze({ sha256: qualification.certificate_sha256 }) }),
        ]),
      }),
      runDetails: Object.freeze({
        builder: Object.freeze({ id: "https://domainspec.local/builders/release-candidate/v1" }),
        metadata: Object.freeze({ invocationId: `domainspec-v2-cli-${source.commit_sha}`, sourceTree: "clean" }),
        byproducts: Object.freeze([]),
      }),
    }),
  });
}

function manifestDigest(candidate) {
  const body = { ...candidate };
  delete body.manifest_sha256;
  return sha256(canonicalJson(body));
}

function normalizedAbsolute(value, label) {
  if (typeof value !== "string" || !path.isAbsolute(value) || path.resolve(value) !== value) throw new Error(`${label} requires one normalized absolute path`);
  return value;
}

export function buildReleaseCandidate(options) {
  const repositoryRoot = normalizedAbsolute(options.repositoryRoot ?? defaultRepositoryRoot, "repository root");
  const packageRoot = normalizedAbsolute(options.packageRoot ?? defaultPackageRoot, "package root");
  const qualificationEvidenceRoot = normalizedAbsolute(options.qualificationEvidenceRoot, "qualification evidence root");
  const outputRoot = normalizedAbsolute(options.outputRoot, "output root");
  if (fs.existsSync(outputRoot)) throw new Error("output root must not already exist");
  const outputParent = path.dirname(outputRoot);
  const outputParentStats = fs.lstatSync(outputParent);
  if (!outputParentStats.isDirectory() || outputParentStats.isSymbolicLink() || fs.realpathSync(outputParent) !== outputParent) throw new Error("output parent must be one real directory");
  if (process.version !== `v${EXPECTED_NODE}`) throw new Error(`release candidate requires Node ${EXPECTED_NODE}; observed ${process.version}`);
  const npmVersion = run("npm", ["--version"], packageRoot);
  if (npmVersion !== EXPECTED_NPM) throw new Error(`release candidate requires npm ${EXPECTED_NPM}; observed ${npmVersion}`);
  const packageJson = JSON.parse(fs.readFileSync(path.join(packageRoot, "package.json"), "utf8"));
  exactPackage(packageJson);
  const source = checkedGitIdentity(repositoryRoot, options.sourceCommit, options.gitExecutable ?? gitExecutable);

  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-release-candidate-"));
  const stage = path.join(outputParent, `.domainspec-release-candidate-${process.pid}-${crypto.randomUUID()}`);
  try {
    fs.mkdirSync(path.join(stage, "package"), { recursive: true, mode: 0o700 });
    fs.mkdirSync(path.join(stage, "evidence"), { recursive: true, mode: 0o700 });
    const qualification = qualificationBinding(qualificationEvidenceRoot, path.join(stage, "qualification"));
    const snapshotPackageRoot = sourceSnapshot(repositoryRoot, packageRoot, source.commit_sha, scratch, options.gitExecutable ?? gitExecutable, options.sourceSnapshotRoot ?? null);
    const inventory = packageInventory(snapshotPackageRoot, path.join(stage, "package"), scratch);
    writeJson(path.join(stage, "evidence", "package-inventory.json"), inventory);
    const packageBinding = Object.freeze({
      name: EXPECTED_PACKAGE,
      version: EXPECTED_VERSION,
      filename: inventory.package.filename,
      sha256: inventory.package.sha256,
      size_bytes: inventory.package.size_bytes,
      inventory_sha256: inventory.inventory_sha256,
      node_version: EXPECTED_NODE,
      npm_version: EXPECTED_NPM,
    });
    writeJson(path.join(stage, "evidence", "sbom.spdx.json"), spdx(packageBinding, inventory));
    writeJson(path.join(stage, "evidence", "provenance.intoto.json"), provenance(source, packageBinding, packageRoot, repositoryRoot, qualification));

    const artifacts = Object.freeze(walk(stage));
    const candidateBody = Object.freeze({
      schema_version: "domainspec.release-candidate-manifest/v1",
      candidate_id: `domainspec-v2-cli-1.0.0-${source.commit_sha.slice(0, 12)}`,
      source,
      package: packageBinding,
      qualification,
      artifacts,
      claim_ceiling: Object.freeze({ release_candidate_evidence: true, publisher_identity: false, publication: false, release: false, deployment: false, production: false }),
      authority_effect: "none",
    });
    const candidate = Object.freeze({ ...candidateBody, manifest_sha256: manifestDigest(candidateBody) });
    writeJson(path.join(stage, "candidate.json"), candidate);
    fs.copyFileSync(verifierSource, path.join(stage, "verify-release-candidate.mjs"), fs.constants.COPYFILE_EXCL);
    fs.chmodSync(path.join(stage, "verify-release-candidate.mjs"), 0o700);
    const checksumRows = walk(stage).sort(compareRows);
    fs.writeFileSync(path.join(stage, "SHA256SUMS"), `${checksumRows.map((row) => `${row.sha256}  ${row.path}`).join("\n")}\n`, { flag: "wx", mode: 0o600 });
    fs.renameSync(stage, outputRoot);
    const verification = verifyReleaseCandidate(outputRoot, source.commit_sha);
    if (verification.result !== "pass") throw new Error(`generated release candidate did not verify\n${JSON.stringify(verification, null, 2)}`);
    return Object.freeze({
      schema_version: "domainspec.release-candidate-build/v1",
      result: "pass",
      candidate_id: candidate.candidate_id,
      source_commit: source.commit_sha,
      package_sha256: packageBinding.sha256,
      manifest_sha256: candidate.manifest_sha256,
      output_root: outputRoot,
      denied_effects: Object.freeze(["publication", "release", "deployment", "production"]),
      authority_effect: "none",
    });
  } catch (error) {
    fs.rmSync(stage, { recursive: true, force: true });
    if (fs.existsSync(outputRoot)) fs.rmSync(outputRoot, { recursive: true, force: true });
    throw error;
  } finally {
    fs.rmSync(scratch, { recursive: true, force: true });
  }
}

function option(name, required) {
  const index = process.argv.indexOf(name);
  if (index < 0) {
    if (required) throw new Error(`missing required option:${name}`);
    return null;
  }
  const value = process.argv[index + 1];
  if (!value) throw new Error(`missing value:${name}`);
  return value;
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  const receipt = buildReleaseCandidate({
    repositoryRoot: defaultRepositoryRoot,
    packageRoot: defaultPackageRoot,
    qualificationEvidenceRoot: option("--qualification-evidence-root", true),
    outputRoot: option("--output-root", true),
    sourceCommit: option("--source-commit", true),
  });
  process.stdout.write(`${JSON.stringify(receipt, null, 2)}\n`);
}
