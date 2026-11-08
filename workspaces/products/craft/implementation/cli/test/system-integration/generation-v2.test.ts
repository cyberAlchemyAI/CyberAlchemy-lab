import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { canonicalJson } from "../../src/input/source-manifest.ts";
import { planIntegrationProjectV2 } from "../../src/system-integration/generation-v2.ts";
import { nodeExecutable, repositoryToolchain, typeScriptToolchain } from "../helpers/local-toolchain.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(here, "../../../system-integration/fixtures");
const generationSchemaPath = path.resolve(here, "../../../system-integration/contracts/integration-generation-source-v2.schema.json");
const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(fixtureRoot, relative), "utf8"));
const source: any = {
  schema_version: "domainspec.integration-generation-source/v2-candidate",
  source_id: "integration-source:commerce-v2",
  persistence: read("persistence-composition-v2/commerce-postgresql.json"),
  messaging: read("messaging-composition-v2/order-submitted-topic.json"),
  external_api: read("external-api-composition-v2/payments-http.json"),
  disclosure_policy: { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["provider", "statusCode"], max_attribute_count: 2, max_string_length: 64, forbidden_key_fragments: ["authorization", "credential", "secret", "token"], authority_effect: "none" },
  orodi_binding: { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "observation-input-only-no-admission", authority_effect: "none" },
};

function materialize(plan: ReturnType<typeof planIntegrationProjectV2>, root: string): void {
  for (const artifact of plan.artifacts) {
    const target = path.join(root, artifact.relative_path);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, artifact.content);
  }
}

function run(command: string, args: readonly string[], cwd: string, env: NodeJS.ProcessEnv = process.env): void {
  const result = spawnSync(command, args, { cwd, env, encoding: "utf8" });
  assert.equal(result.status, 0, `${command} ${args.join(" ")}\n${result.stdout}\n${result.stderr}`);
}

function declarationLines(content: string, declaration: RegExp, separator = "\n"): string[] {
  const body = content.match(declaration)?.[1];
  assert.ok(body !== undefined, `Missing declaration: ${declaration}`);
  return body.trim().split(separator).map(line => line.replace(/\s+/g, "")).filter(Boolean);
}

test("R7 generates semantically equivalent responsibility layouts for all three languages", () => {
  const plans = (["typescript", "python", "rust"] as const).map(language => planIntegrationProjectV2(source, language));
  assert.equal(new Set(plans.map(plan => canonicalJson(plan.semantic_manifest))).size, 1);
  for (const plan of plans) {
    assert.match(plan.plan_digest, /^[a-f0-9]{64}$/);
    assert.equal(plan.runtime_guarantees_observed, false);
    assert.equal(plan.authority_effect, "none");
    const paths = plan.artifacts.map(item => item.relative_path);
    for (const prefix of ["src/features/integration/application/", "src/integrations/providers/", "src/integrations/mappings/", "src/config/integrations/", "migrations/", "src/observability/integrations/"]) assert.equal(paths.some(item => item.startsWith(prefix)), true, `${plan.language}:${prefix}`);
    assert.equal(paths.some(item => item === "runtime" || item.startsWith("runtime/")), false);
    assert.equal(paths.includes(".domainspec/integrations/semantic-manifest.json"), true);
  }
  const typescriptContracts = plans.find(plan => plan.language === "typescript")!.artifacts.find(item => item.relative_path.endsWith("contracts.ts"))!.content;
  const pythonContracts = plans.find(plan => plan.language === "python")!.artifacts.find(item => item.relative_path.endsWith("contracts.py"))!.content;
  const rustContracts = plans.find(plan => plan.language === "rust")!.artifacts.find(item => item.relative_path.endsWith("contracts.rs"))!.content;
  assert.doesNotMatch(pythonContracts, /\n    def /);
  assert.match(pythonContracts, /\n    async def publish\(/);
  assert.match(rustContracts, /pub type ContractFuture<'a>/);
  assert.deepEqual(declarationLines(typescriptContracts, /export interface ProviderAcceptanceReceipt \{([\s\S]*?)\n\}/), [
    "readonlyacceptance_boundary_ref:string;", "readonlyprovider_acknowledgement_ref:string;",
    'readonlyclaim_ceiling:"provider-accepted";', "readonlydelivery_observed:false;", "readonlyconsumer_completion_observed:false;",
  ]);
  assert.deepEqual(declarationLines(pythonContracts, /class ProviderAcceptanceReceipt\(TypedDict\):\n([\s\S]*?)(?:\n\n|$)/), [
    "acceptance_boundary_ref:str", "provider_acknowledgement_ref:str", 'claim_ceiling:Literal["provider-accepted"]',
    "delivery_observed:Literal[False]", "consumer_completion_observed:Literal[False]",
  ]);
  assert.deepEqual(declarationLines(rustContracts, /pub struct ProviderAcceptanceReceipt \{([^}]*)\}/, ","), [
    "pubacceptance_boundary_ref:&'staticstr", "pubprovider_acknowledgement_ref:String", "pubclaim_ceiling:&'staticstr",
    "pubdelivery_observed:bool", "pubconsumer_completion_observed:bool",
  ]);
  assert.match(rustContracts, /pub type ContractFuture<'a>=Pin<Box<dyn Future<Output=Result<String,String>>\+Send\+'a>>;/);
  assert.match(rustContracts, /pub type ProviderAcceptanceFuture<'a>=Pin<Box<dyn Future<Output=Result<ProviderAcceptanceReceipt,String>>\+Send\+'a>>;/);

  // Independent fixture identities anchor named contracts, not global signature matches.
  assert.deepEqual(source.messaging.publication_bindings.map((binding: any) => binding.producer_contract_ref), ["contract:order-event-publisher"]);
  assert.deepEqual(source.persistence.persistence_bindings.map((binding: any) => binding.dependency_contract_ref), ["contract:order-store"]);
  assert.deepEqual(source.external_api.external_api_contracts.map((contract: any) => [contract.contract_id, contract.operations.map((operation: any) => operation.operation_id)]), [["contract:payment-gateway", ["authorize"]]]);
  for (const [name, operations, publisher] of [
    ["ContractOrderEventPublisher", ["publish"], true],
    ["ContractOrderStore", ["load", "save"], false],
    ["ContractPaymentGateway", ["authorize"], false],
  ] as const) {
    assert.deepEqual(declarationLines(typescriptContracts, new RegExp(`export interface ${name} \\{([\\s\\S]*?)\\n\\}`)), operations.map(operation =>
      `readonly"${operation}":(input:Readonly<Record<string,unknown>>)=>Promise<${publisher ? "ProviderAcceptanceReceipt" : "unknown"}>;`));
    assert.deepEqual(declarationLines(pythonContracts, new RegExp(`class ${name}\\(Protocol\\):\\n([\\s\\S]*?)(?:\\n\\n|$)`)), operations.map(operation =>
      `asyncdef${operation}(self,input:Mapping[str,object])->${publisher ? "ProviderAcceptanceReceipt" : "object"}:...`));
    assert.deepEqual(declarationLines(rustContracts, new RegExp(`pub trait ${name} \\{([\\s\\S]*?)\\n\\}`)), operations.map(operation =>
      `fn${operation}<'a>(&'aself,input:&'astr)->${publisher ? "ProviderAcceptanceFuture" : "ContractFuture"}<'a>;`));
  }
});

test("R7 generated TypeScript, Python and Rust compile; Rust has a closed Cargo module tree", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-integration-r7-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  for (const language of ["typescript", "python", "rust"] as const) {
    const root = path.join(temporary, language); materialize(planIntegrationProjectV2(source, language), root);
    if (language === "typescript") run(nodeExecutable(), [typeScriptToolchain().compiler, "-p", "tsconfig.json"], root);
    if (language === "python") {
      const files = fs.readdirSync(root, { recursive: true }).filter(item => typeof item === "string" && item.endsWith(".py")) as string[];
      run("python3", ["-m", "py_compile", ...files], root);
    }
    if (language === "rust") {
      assert.equal(fs.existsSync(path.join(root, "Cargo.toml")), true);
      for (const module of ["src/lib.rs", "src/features/mod.rs", "src/features/integration/application/mod.rs", "src/integrations/providers/mod.rs", "src/integrations/mappings/mod.rs", "src/config/integrations/mod.rs", "src/observability/integrations/mod.rs"]) assert.equal(fs.existsSync(path.join(root, module)), true, module);
      run(repositoryToolchain(), ["cargo", "check", "--offline"], root);
    }
  }
});

test("R7 generation is deterministic and rejects cross-definition drift", () => {
  for (const language of ["typescript", "python", "rust"] as const) assert.deepEqual(planIntegrationProjectV2(source, language), planIntegrationProjectV2(structuredClone(source), language));
  const drifted = structuredClone(source); drifted.messaging.integration_kernel.definition_pack_sha256 = "0".repeat(64);
  assert.throws(() => planIntegrationProjectV2(drifted, "typescript"));
});

test("R7 generation rejects open or unsupported source envelopes", () => {
  assert.throws(() => planIntegrationProjectV2({ ...source, accidental_authority: true }, "typescript"), { code: "INTEGRATION_GENERATION_SCHEMA" });
  assert.throws(() => planIntegrationProjectV2({ ...source, schema_version: "domainspec.integration-generation-source/v1" }, "typescript"), { code: "INTEGRATION_GENERATION_SCHEMA" });
  assert.throws(() => planIntegrationProjectV2(source, "kotlin" as never), { code: "INTEGRATION_GENERATION_LANGUAGE" });
});

test("R7 aggregate generation schema is closed and delegates each composition", () => {
  const schema = JSON.parse(fs.readFileSync(generationSchemaPath, "utf8"));
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(Object.keys(schema.properties).sort(), ["disclosure_policy", "external_api", "messaging", "orodi_binding", "persistence", "schema_version", "source_id"]);
  assert.equal(schema.properties.persistence.$ref, "persistence-composition-v2.schema.json");
  assert.equal(schema.properties.messaging.$ref, "messaging-composition-v2.schema.json");
  assert.equal(schema.properties.external_api.$ref, "external-api-composition-v2.schema.json");
  assert.equal(schema.properties.disclosure_policy.$ref, "integration-observation-v1.schema.json#/$defs/disclosurePolicy");
  assert.equal(schema.properties.orodi_binding.$ref, "integration-observation-v1.schema.json#/$defs/orodiBinding");
});
