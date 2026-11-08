import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BUSINESS_CONTRACT_RESOURCES_V2 } from '../src/profile-engine/business-authoring-contract-registry-v2.ts';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const canonicalRoot = path.resolve(root, "../system-integration/contracts");
const mirrored = [
  "provider-pack-selection-v1.schema.json",
  "integration-generation-source-v2.schema.json",
  "application-integration-binding-v1.schema.json",
  "compiled-application-graph-v1.schema.json",
  "persistence-composition-v2.schema.json",
  "messaging-composition-v2.schema.json",
  "external-api-composition-v2.schema.json",
  "integration-observation-v1.schema.json",
  "integration-kernel-v2.schema.json",
];

const results = mirrored.map(name => {
  const sourceBytes = fs.readFileSync(path.join(canonicalRoot, name));
  const packagedBytes = fs.readFileSync(path.join(root, "contracts", name));
  assert.deepEqual(packagedBytes, sourceBytes, `packaged schema drifted from its canonical source:${name}`);
  JSON.parse(packagedBytes.toString("utf8"));
  return { schema: `contracts/${name}`, bytes: packagedBytes.length, authority: `system-integration/contracts/${name}` };
});

const wholeApplicationPath = path.join(root, "contracts/whole-application-plan-v1.schema.json");
const wholeApplicationBytes = fs.readFileSync(wholeApplicationPath);
const wholeApplication = JSON.parse(wholeApplicationBytes.toString("utf8"));
assert.equal(wholeApplication.$schema, "https://json-schema.org/draft/2020-12/schema");
assert.equal(wholeApplication.$id, "https://domainspec.dev/contracts/whole-application-plan-v1.schema.json");
assert.equal(wholeApplication.properties?.schema_version?.const, "domainspec.whole-application-plan/v1-candidate");
assert.equal(wholeApplication.properties?.runtime_guarantees_observed?.const, false);
assert.equal(wholeApplication.properties?.claim_ceiling?.const, "formation-and-static-compilation-only");
assert.equal(wholeApplication.properties?.authority_effect?.const, "none");
assert.equal(wholeApplication.additionalProperties, false);
results.push({ schema: "contracts/whole-application-plan-v1.schema.json", bytes: wholeApplicationBytes.length, authority: "cli/src/generation/whole-application-v1.ts" });

const runtimeEvidencePath = path.join(root, "contracts/provider-application-runtime-evidence-v1.schema.json");
const runtimeEvidenceBytes = fs.readFileSync(runtimeEvidencePath);
const runtimeEvidence = JSON.parse(runtimeEvidenceBytes.toString("utf8"));
assert.equal(runtimeEvidence.$schema, "https://json-schema.org/draft/2020-12/schema");
assert.equal(runtimeEvidence.$id, "https://domainspec.dev/contracts/provider-application-runtime-evidence-v1.schema.json");
assert.equal(runtimeEvidence.properties?.schema_version?.const, "domainspec.provider-application-runtime-evidence/v1-candidate");
assert.equal(runtimeEvidence.properties?.production_runtime_guarantees_observed?.const, false);
assert.equal(runtimeEvidence.properties?.authority_effect?.const, "none");
assert.equal(runtimeEvidence.additionalProperties, false);
results.push({ schema: "contracts/provider-application-runtime-evidence-v1.schema.json", bytes: runtimeEvidenceBytes.length, authority: "cli/src/generation/provider-application-runtime-evidence-v1.ts" });

// Candidate business/request contracts are owned here, rather than legacy mirror sources.
const businessSchemas = {
  "business-spec-v1.schema.json":"alchlang.business-spec/v1-candidate",
  "business-authoring-project-v1.schema.json":"craft.business-authoring-project/v1-candidate",
  "business-review-v1.schema.json":"craft.business-review/v1-candidate",
  "business-decision-v1.schema.json":"craft.business-decision/v1-candidate",
  "business-authoring-lock-v1.schema.json":"craft.business-authoring-lock/v1-candidate",
  "business-lowering-v1.schema.json":"craft.business-lowering/v1-candidate",
  "operation-json-post-v1.schema.json":"craft.operation-json-post/v1-candidate",
  "profile-package-v3.schema.json":"craft.profile-package/v3-candidate",
  "profile-package-v4.schema.json":"craft.profile-package/v4-candidate",
  "profile-project-v2.schema.json":"craft.profile-project/v2-candidate",
  "profile-package-v2.schema.json":"craft.profile-package/v2-candidate",
  "business-application-v1.schema.json":"craft.business-application/v1-candidate",
  "request-application-source-v1.schema.json":"domainspec.request-application-source/v1-candidate",
  "request-application-binding-v1.schema.json":"domainspec.request-application-binding/v1-candidate",
  "compiled-request-application-graph-v1.schema.json":"domainspec.compiled-request-application-graph/v1-candidate",
  "request-application-plan-v1.schema.json":"domainspec.request-application-plan/v1-candidate"
};
for (const [name,version] of Object.entries(businessSchemas)) {
  const bytes=fs.readFileSync(path.join(root,"contracts",name)),schema=JSON.parse(bytes);
  assert.equal(schema.additionalProperties,false);
  assert.equal(schema.properties.schema_version.const,version);
  results.push({schema:"contracts/"+name,bytes:bytes.length,authority:"cli/contracts/"+name});
}

// Additive closed U0 successor resources; v1 schemas and their checks remain unchanged.
const packageFiles=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8')).files;
// The technical source envelope is owned here and ships with its runtime
// validator. Its preserved design spelling is an explicit compatibility alias.
const technicalSourceName='technical-profile-source-v1.schema.json';
const technicalSourceBytes=fs.readFileSync(path.join(root,'contracts',technicalSourceName));
const technicalSourceSchema=JSON.parse(technicalSourceBytes);
assert.equal(technicalSourceSchema.$schema,'https://json-schema.org/draft/2020-12/schema');
assert.equal(technicalSourceSchema.$id,'urn:craft:technical-profile-source:v1');
assert.equal(technicalSourceSchema.additionalProperties,false);
assert.deepEqual(technicalSourceSchema.properties.schema_version.enum,['craft.technical-profile-source/v1','craft.technical-profile-source/v1-design']);
assert(packageFiles.includes('contracts/'+technicalSourceName),'unpackaged technical source schema');
results.push({schema:'contracts/'+technicalSourceName,bytes:technicalSourceBytes.length,authority:'cli/contracts/'+technicalSourceName});
for(const resource of BUSINESS_CONTRACT_RESOURCES_V2){
  const bytes=fs.readFileSync(path.join(root,'contracts',resource.file));
  const schema=JSON.parse(bytes.toString('utf8'));
  assert.equal(schema.$schema,'https://json-schema.org/draft/2020-12/schema');
  assert.equal(schema.$id,resource.version);
  assert.equal(schema.properties.schema_version.const,resource.version);
  assert.equal(schema.additionalProperties,false);
  assert(packageFiles.includes('contracts/'+resource.file),'unpackaged successor schema:'+resource.file);
  results.push({schema:'contracts/'+resource.file,bytes:bytes.length,authority:'cli/contracts/'+resource.file});
}

const packagedSchemaNames = results.map(row => path.basename(row.schema));
const resolvedReferences = [];
const visitReferences = (value, owner) => {
  if (Array.isArray(value)) return value.forEach(child => visitReferences(child, owner));
  if (value === null || typeof value !== "object") return;
  if (typeof value.$ref === "string" && !value.$ref.startsWith("#") && !/^[a-z]+:/i.test(value.$ref)) {
    const referenced = value.$ref.split("#", 1)[0];
    assert.equal(fs.existsSync(path.join(root, "contracts", referenced)), true, `unresolved packaged schema reference:${owner}:${value.$ref}`);
    resolvedReferences.push({ owner, reference: value.$ref });
  }
  for (const child of Object.values(value)) visitReferences(child, owner);
};
for (const name of packagedSchemaNames) visitReferences(JSON.parse(fs.readFileSync(path.join(root, "contracts", name), "utf8")), name);

process.stdout.write(`${JSON.stringify({ result: "pass", schemas: results, resolved_references: resolvedReferences })}\n`);
