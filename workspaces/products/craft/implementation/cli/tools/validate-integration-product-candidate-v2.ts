import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson } from "../src/input/source-manifest.js";
import { buildIntegrationProductCandidateV2, repositoryRoot } from "./freeze-integration-product-candidate-v2.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const candidatePath = path.resolve(process.argv[2] ?? path.join(here, "../../development/integration-reconciliation/v1/candidate/INTEGRATION-PRODUCT-CANDIDATE.v2.json"));
const candidate = JSON.parse(fs.readFileSync(candidatePath, "utf8"));
const expected = buildIntegrationProductCandidateV2(candidate.environment);
assert.equal(canonicalJson(candidate), canonicalJson(expected), "candidate bytes or bound source/generated artifacts drifted");
assert.equal(candidate.status, "exact-candidate");
assert.equal(candidate.validation.result, "pass");
assert.equal(candidate.authority_effect, "none");
assert.equal(path.isAbsolute(repositoryRoot), true);
process.stdout.write(`${JSON.stringify({ schema_version: "domainspec.integration-product-candidate-validation/v2", candidate_id: candidate.candidate_id, candidate_digest: candidate.candidate_digest, source_files: candidate.frozen_source.files.length, generated_artifacts: candidate.generated_artifacts.reduce((total: number, row: { artifacts: unknown[] }) => total + row.artifacts.length, 0), result: "pass", authority_effect: "none" })}\n`);
