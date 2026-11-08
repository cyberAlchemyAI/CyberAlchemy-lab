import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson } from "../src/input/source-manifest.ts";
import { planDeploymentRecipe } from "../src/recipe/plan.ts";
import { publishDeploymentRecipe } from "../src/recipe/publish.ts";
import { readDeploymentRecipeRequest } from "../src/recipe/contracts.ts";
import {
  RECIPE_QUALIFICATION_ADAPTER_PROTOCOL,
  RECIPE_QUALIFICATION_DOCKER_IMAGE,
  RECIPE_QUALIFICATION_TERRAFORM_IMAGE,
  createRecipeQualificationProfile,
} from "../src/qualification/contracts.ts";
import { qualifyDeploymentRecipe, verifyRecipeQualification } from "../src/qualification/execute.ts";
import { createCompleteL1Project } from "../test/helpers/l1-project.ts";

interface L1BaselineV1 {
  readonly schema_version: "domainspec.recipe-qualification-l1-baseline/v1";
  readonly profile_sha256: string;
  readonly source_manifest_sha256: string;
  readonly target_implementation_sha256: string;
  readonly plan_sha256: string;
  readonly provider_lock_sha256: string;
  readonly certificate_sha256: string;
  readonly authority_effect: "none";
}

const cliRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function option(name: string, required: boolean): string | null {
  const index = process.argv.indexOf(name);
  if (index < 0) {
    if (required) throw new Error(`missing required option:${name}`);
    return null;
  }
  const value = process.argv[index + 1];
  if (!value || !path.isAbsolute(value) || path.resolve(value) !== value) throw new Error(`${name} requires one normalized absolute path`);
  return value;
}

function readBaseline(file: string): L1BaselineV1 {
  const value = JSON.parse(fs.readFileSync(file, "utf8")) as L1BaselineV1;
  const keys = ["authority_effect", "certificate_sha256", "plan_sha256", "profile_sha256", "provider_lock_sha256", "schema_version", "source_manifest_sha256", "target_implementation_sha256"];
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson(keys) || value.schema_version !== "domainspec.recipe-qualification-l1-baseline/v1" || value.authority_effect !== "none") throw new Error("invalid L1 baseline shape");
  for (const [key, digest] of Object.entries(value)) if (key.endsWith("_sha256") && (typeof digest !== "string" || !/^[a-f0-9]{64}$/.test(digest))) throw new Error(`invalid L1 baseline digest:${key}`);
  return value;
}

const requestedOutputRoot = option("--output-root", false);
const temporaryOutputParent = requestedOutputRoot === null ? fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-l1-evidence-")) : null;
const outputRoot = requestedOutputRoot ?? path.join(temporaryOutputParent!, "evidence");
const baselinePath = option("--expected-baseline", false) ?? path.join(cliRoot, "fixtures", "qualification", "l1-baseline.json");
if (fs.existsSync(outputRoot)) throw new Error("output root must not already exist");
const outputParent = path.dirname(outputRoot);
const parentStats = fs.lstatSync(outputParent);
if (!parentStats.isDirectory() || parentStats.isSymbolicLink() || fs.realpathSync(outputParent) !== outputParent) throw new Error("output parent must be one real directory");

const fixture = createCompleteL1Project();
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-l1-"));
const consumerRoot = path.join(cliRoot, "fixtures", "qualification", "l1-consumer");
const request = readDeploymentRecipeRequest(path.join(consumerRoot, "deployment-recipe-request.json"));
const terraformAdapter = path.join(cliRoot, "tools", "recipe-qualification", "terraform");
const dockerAdapter = path.join(cliRoot, "tools", "recipe-qualification", "docker");
const profile = createRecipeQualificationProfile({
  schema_version: "domainspec.recipe-qualification-profile/v1",
  profile_id: "domainspec.recipe-qualification.l1",
  ontology_id: "domainspec.recipe-qualification-ontology@1",
  qualification_level: "recipe-executable-v1",
  recipe_target: "aws-ecs-fargate-postgres-v1",
  required_checks: ["recipe-byte-verify", "terraform-fmt-check", "terraform-init-backendless", "terraform-validate", "docker-buildx-bake-check"],
  optional_checks: [],
  toolchain: {
    terraform: { version: "1.16.0", adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_TERRAFORM_IMAGE },
    docker: { version: "28.0.1", buildx_version: "0.21.3", adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_DOCKER_IMAGE },
  },
  network_policy: "provider-registry-read-only",
  normalization_profile: "domainspec.recipe-qualification-normalization/v1",
  effect_ceiling: "no-external-effect",
  authority_effect: "none",
});

try {
  const targetRoot = path.join(scratch, "recipe");
  publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request, consumerRoot), targetRoot);
  fs.mkdirSync(outputRoot, { mode: 0o700 });
  fs.writeFileSync(path.join(outputRoot, "qualification-profile.json"), `${canonicalJson(profile)}\n`, { flag: "wx" });
  const left = qualifyDeploymentRecipe(fixture.root, request, consumerRoot, targetRoot, profile, path.join(outputRoot, "run-1"), { terraformExecutable: terraformAdapter, dockerExecutable: dockerAdapter });
  const right = qualifyDeploymentRecipe(fixture.root, request, consumerRoot, targetRoot, profile, path.join(outputRoot, "run-2"), { terraformExecutable: terraformAdapter, dockerExecutable: dockerAdapter });
  const leftVerification = verifyRecipeQualification(fixture.root, request, consumerRoot, targetRoot, profile, left.qualification_root);
  const rightVerification = verifyRecipeQualification(fixture.root, request, consumerRoot, targetRoot, profile, right.qualification_root);
  const providerLockSha = left.certificate.observations.find(({ check_id }) => check_id === "terraform-init-backendless")?.provider_lock_sha256 ?? "";
  const observed: L1BaselineV1 = Object.freeze({
    schema_version: "domainspec.recipe-qualification-l1-baseline/v1",
    profile_sha256: profile.profile_sha256,
    source_manifest_sha256: left.plan.subject.source_manifest_sha256,
    target_implementation_sha256: left.plan.subject.target_implementation_sha256,
    plan_sha256: left.plan.plan_sha256,
    provider_lock_sha256: providerLockSha,
    certificate_sha256: left.certificate.certificate_sha256,
    authority_effect: "none",
  });
  const checks = Object.freeze([
    Object.freeze({ id: "run-1-pass", result: left.certificate.result === "pass" ? "pass" as const : "fail" as const }),
    Object.freeze({ id: "run-2-pass", result: right.certificate.result === "pass" ? "pass" as const : "fail" as const }),
    Object.freeze({ id: "run-1-verifies", result: leftVerification.result }),
    Object.freeze({ id: "run-2-verifies", result: rightVerification.result }),
    Object.freeze({ id: "certificate-byte-equivalence", result: fs.readFileSync(path.join(left.qualification_root, "qualification-certificate.json")).equals(fs.readFileSync(path.join(right.qualification_root, "qualification-certificate.json"))) ? "pass" as const : "fail" as const }),
    Object.freeze({ id: "expected-baseline", result: canonicalJson(observed) === canonicalJson(readBaseline(baselinePath)) ? "pass" as const : "fail" as const }),
  ]);
  const result = checks.every((check) => check.result === "pass") ? "pass" : "fail";
  const summary = Object.freeze({ schema_version: "domainspec.recipe-qualification-l1-equivalence/v1", result, checks, observed, evidence_root: outputRoot, authority_effect: "none" as const });
  fs.writeFileSync(path.join(outputRoot, "equivalence.json"), `${canonicalJson(summary)}\n`, { flag: "wx" });
  process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
  if (result !== "pass") process.exitCode = 1;
} finally {
  fs.rmSync(fixture.parent, { recursive: true, force: true });
  fs.rmSync(scratch, { recursive: true, force: true });
}
