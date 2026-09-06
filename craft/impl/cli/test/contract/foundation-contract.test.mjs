import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

import {
  DEFAULT_CONTRACT_PATH,
  DEFAULT_SCHEMA_PATH,
  FoundationContractError,
  canonicalJson,
  sealFoundationContract,
  validateFoundationContract
} from "../../tools/validate-foundation-contract.mjs";

const accepted = JSON.parse(fs.readFileSync(DEFAULT_CONTRACT_PATH, "utf8"));
const schema = JSON.parse(fs.readFileSync(DEFAULT_SCHEMA_PATH, "utf8"));

function expectCode(mutant, code) {
  assert.throws(
    () => validateFoundationContract(mutant),
    (error) => error instanceof FoundationContractError && error.code === code
  );
}

test("superseding Node 26 SF-01 through SF-21 foundation contract passes", () => {
  const result = validateFoundationContract(accepted);
  assert.equal(result.result, "pass");
  assert.equal(result.selection_count, 21);
  assert.equal(result.authority_effect, "none");
});

test("schema independently locks the exact accepted nested contract", () => {
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(schema.properties.decision_bindings, { const: accepted.decision_bindings });
  assert.deepEqual(schema.properties.selections, { const: accepted.selections });
  assert.deepEqual(schema.properties.supported_surface, { const: accepted.supported_surface });
  assert.deepEqual(schema.properties.invariants, { const: accepted.invariants });
});

test("canonical digest is independent of object insertion order", () => {
  const reordered = Object.fromEntries(Object.entries(accepted).reverse());
  assert.equal(canonicalJson(reordered), canonicalJson(accepted));
  assert.equal(validateFoundationContract(reordered).contract_digest, accepted.contract_digest);
});

test("one changed selected branch fails even with refreshed self-digests", () => {
  const mutant = structuredClone(accepted);
  mutant.selections[1].option = "P1";
  expectCode(sealFoundationContract(mutant), "SFC_CONTRACT_SELECTION");
});

test("missing and extra top-level members fail closed", () => {
  const missing = structuredClone(accepted);
  delete missing.supported_surface;
  expectCode(missing, "SFC_CONTRACT_SCHEMA");
  const extra = { ...accepted, extension_bag: {} };
  expectCode(extra, "SFC_CONTRACT_SCHEMA");
});

test("stale decision source identity fails even with refreshed self-digests", () => {
  const mutant = structuredClone(accepted);
  mutant.decision_bindings.owner_decision.sha256 = "f".repeat(64);
  expectCode(sealFoundationContract(mutant), "SFC_CONTRACT_SOURCE_STALE");
});

test("stale input and contract digests fail", () => {
  const staleInput = { ...accepted, input_digest: "0".repeat(64) };
  expectCode(staleInput, "SFC_CONTRACT_INPUT_DIGEST");
  const staleContract = { ...accepted, contract_digest: "0".repeat(64) };
  expectCode(staleContract, "SFC_CONTRACT_DIGEST");
});

test("authority growth and claim growth fail even when resealed", () => {
  const authority = sealFoundationContract({ ...accepted, authority_effect: "profile-admission" });
  expectCode(authority, "SFC_CONTRACT_AUTHORITY");
  const claim = structuredClone(accepted);
  claim.claim_ceiling.release = true;
  expectCode(sealFoundationContract(claim), "SFC_CONTRACT_CLAIM_CEILING");
});
