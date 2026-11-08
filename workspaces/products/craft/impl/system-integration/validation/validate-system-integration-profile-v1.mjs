#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { compileBindingManifest, LANGUAGES, loadProfilePackage, PACKAGE_ROOT, readBindingSetFile, renderLanguageContract, verifyLanguageContract } from "../compiler/system-integration-v1.mjs";

const packageState = loadProfilePackage();
const schemaNames = ["integration-reference-v1.schema.json", "dependency-contract-v1.schema.json", "persistence-binding-v1.schema.json", "transaction-guarantee-binding-v1.schema.json", "failure-outcome-binding-v1.schema.json", "durable-workflow-runtime-binding-v1.schema.json", "binding-set-v1.schema.json", "binding-manifest-v1.schema.json"];
for (const name of schemaNames) {
  const value = JSON.parse(fs.readFileSync(path.join(PACKAGE_ROOT, "contracts", name), "utf8"));
  if (name !== "integration-reference-v1.schema.json" && value.additionalProperties !== false) throw new Error(`schema is not closed:${name}`);
}
const fixture = readBindingSetFile(path.join(PACKAGE_ROOT, "fixtures/provider-neutral-v1/settlement-runtime.json"));
const digests = [];
for (const language of LANGUAGES) {
  const manifest = compileBindingManifest(fixture, language, packageState);
  const generated = renderLanguageContract(manifest);
  verifyLanguageContract(generated, manifest);
  digests.push({ language, language_profile_digest: packageState.language_profiles[language].digest, binding_digest: manifest.binding_digest, generated_bytes: Buffer.byteLength(generated) });
}
process.stdout.write(`${JSON.stringify({ status: "pass", profile_id: packageState.profile.profile_id, profile_digest: packageState.profile_digest, definitions: 5, languages: 3, obligation_rows: 15, schemas: schemaNames.length, digests, runtime_guarantees_observed: false, authority_effect: "none" })}\n`);
