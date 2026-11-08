import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { DeploymentRecipeRequestV1, PlannedDeploymentRecipeArtifactV1 } from "../recipe/contracts.js";
import { planDeploymentRecipe } from "../recipe/plan.js";
import { verifyDeploymentRecipe } from "../recipe/publish.js";
import {
  qualificationArtifactInventorySha256,
  qualificationFail,
  type RecipeQualificationAdapterId,
  type RecipeQualificationCheckId,
  type RecipeQualificationPlanV1,
  type RecipeQualificationPlannedCheckV1,
  type RecipeQualificationProfileV1,
} from "./contracts.js";

const CHECKS: readonly Readonly<{ check_id: RecipeQualificationCheckId; adapter_id: RecipeQualificationAdapterId; predicate_id: string; effect_class: RecipeQualificationPlannedCheckV1["effect_class"] }>[] = Object.freeze([
  Object.freeze({ check_id: "recipe-byte-verify", adapter_id: "recipe-byte-verify-v1", predicate_id: "exact-artifact-membership-and-digests", effect_class: "pure" }),
  Object.freeze({ check_id: "terraform-fmt-check", adapter_id: "terraform-fmt-check-v1", predicate_id: "terraform-format-current", effect_class: "pure" }),
  Object.freeze({ check_id: "terraform-init-backendless", adapter_id: "terraform-init-backendless-v1", predicate_id: "terraform-provider-resolution-closed", effect_class: "network-read-only" }),
  Object.freeze({ check_id: "terraform-validate", adapter_id: "terraform-validate-v1", predicate_id: "terraform-configuration-valid", effect_class: "bounded-local-cache" }),
  Object.freeze({ check_id: "docker-buildx-bake-check", adapter_id: "docker-buildx-bake-check-v1", predicate_id: "all-declared-build-targets-check", effect_class: "network-read-only" }),
]);

function selectedArtifacts(checkId: RecipeQualificationCheckId, artifacts: readonly PlannedDeploymentRecipeArtifactV1[]): readonly Readonly<{ relative_path: string; size_bytes: number; sha256: string }>[] {
  const selected = checkId === "recipe-byte-verify"
    ? artifacts
    : checkId.startsWith("terraform-")
      ? artifacts.filter(({ relative_path }) => relative_path.startsWith("infrastructure/terraform/"))
      : artifacts.filter(({ relative_path }) => relative_path === "images/docker-bake.hcl" || relative_path.endsWith(".Dockerfile"));
  return Object.freeze(selected.map(({ relative_path, size_bytes, sha256: artifactSha }) => Object.freeze({ relative_path, size_bytes, sha256: artifactSha })).sort((left, right) => left.relative_path.localeCompare(right.relative_path)));
}

export function recipeQualificationPlanSha256(value: Omit<RecipeQualificationPlanV1, "plan_sha256">): string {
  return sha256(canonicalJson(value));
}

export function planRecipeQualification(sourceRoot: string, request: DeploymentRecipeRequestV1, consumerRoot: string, targetRoot: string, profile: RecipeQualificationProfileV1): RecipeQualificationPlanV1 {
  if (profile.recipe_target !== request.target) qualificationFail("MTCLI_QUALIFICATION_TARGET", "/profile/recipe_target", "qualification profile and recipe target differ");
  const recipe = planDeploymentRecipe(sourceRoot, request, consumerRoot);
  const verification = verifyDeploymentRecipe(sourceRoot, request, consumerRoot, targetRoot);
  if (verification.result !== "pass") qualificationFail("MTCLI_QUALIFICATION_RECIPE_STALE", "/target-root", "recipe target is not current and exact");
  const subject = Object.freeze({
    request_id: recipe.manifest.request_id,
    target: recipe.manifest.target,
    project_id: recipe.manifest.project_id,
    source_manifest_sha256: recipe.manifest.source_manifest_sha256,
    compiled_certificate_sha256: recipe.manifest.compiled_certificate_sha256,
    checked_interchange_sha256: recipe.manifest.checked_interchange_sha256,
    request_sha256: recipe.manifest.request_sha256,
    target_implementation_sha256: recipe.manifest.target_implementation_sha256,
    manifest_sha256: recipe.manifest.manifest_sha256,
    recipe_plan_sha256: recipe.plan_sha256,
    recipe_receipt_sha256: recipe.receipt.receipt_sha256,
    artifact_inventory_sha256: qualificationArtifactInventorySha256(recipe.manifest.artifacts),
  });
  const checks = Object.freeze(CHECKS.map((definition) => Object.freeze({ ...definition, input_sha256: sha256(canonicalJson(selectedArtifacts(definition.check_id, recipe.artifacts))), required: true as const })));
  const body = Object.freeze({ schema_version: "domainspec.recipe-qualification-plan/v1" as const, subject, profile_id: profile.profile_id, profile_sha256: profile.profile_sha256, checks, authority_effect: "none" as const });
  return Object.freeze({ ...body, plan_sha256: recipeQualificationPlanSha256(body) });
}

export function recipeQualificationPlanSummary(plan: RecipeQualificationPlanV1): Readonly<Record<string, unknown>> {
  return Object.freeze({ schema_version: "domainspec.recipe-qualification-plan-summary/v1", subject: plan.subject, profile_id: plan.profile_id, profile_sha256: plan.profile_sha256, required_checks: plan.checks.map(({ check_id }) => check_id), plan_sha256: plan.plan_sha256, authority_effect: "none" });
}
