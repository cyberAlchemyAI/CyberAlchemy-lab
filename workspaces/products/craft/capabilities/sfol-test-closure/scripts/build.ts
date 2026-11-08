import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { compileMintedProject } from "../../../impl/tools/minted-project/compiler.ts";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const domainspecRoot = resolve(capabilityRoot, "domainspec");
const repositoryProjectsRoot = resolve(capabilityRoot, "../..");
const generatedRoot = resolve(capabilityRoot, "generated");
const profilePath = resolve(domainspecRoot, "development-profile.json");
const definitionPath = resolve(capabilityRoot, "definition-candidates.json");
const definitionSelectionPath = resolve(capabilityRoot, "decisions/definition-admission-selection.json");
const productCapabilityPath = resolve(capabilityRoot, "product-capability.json");
const productCapabilitySelectionPath = resolve(capabilityRoot, "decisions/product-capability-adoption-selection.json");
const businessOntologyPath = resolve(capabilityRoot, "business-ontology.json");
const propertyDenominatorPath = resolve(capabilityRoot, "property-denominator.json");
const businessOntologySelectionPath = resolve(capabilityRoot, "decisions/business-ontology-admission-selection.json");

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function stable(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function json(path: string): any {
  return JSON.parse(readFileSync(path, "utf8"));
}

function write(path: string, value: unknown): string {
  const bytes = stable(value);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, bytes);
  return sha256(bytes);
}

const first = compileMintedProject(domainspecRoot, {
  developmentProfileRegistry: {
    path: profilePath,
    handle: "sfol-test-closure-development-explicit-v0.1",
  },
});
const second = compileMintedProject(domainspecRoot, {
  developmentProfileRegistry: {
    path: profilePath,
    handle: "sfol-test-closure-development-explicit-v0.1",
  },
});
if (first.graphBytes !== second.graphBytes || first.sourceManifestBytes !== second.sourceManifestBytes) {
  throw new Error("SFOL_TEST_CLOSURE_NONDETERMINISTIC_COMPILE");
}

const graphDigest = sha256(first.graphBytes);
const manifestDigest = sha256(first.sourceManifestBytes);
const implementationMap = json(resolve(capabilityRoot, "implementation-map.json"));
const graphNodeIds = new Set(first.graph.nodes.map(({ node_id }) => node_id));
const components = implementationMap.components.map((component: any) => {
  for (const nodeId of component.operation_node_ids) {
    if (!graphNodeIds.has(nodeId)) throw new Error(`SFOL_IMPLEMENTATION_OPERATION_MISSING:${nodeId}`);
  }
  const bindings = component.implementation_paths.map((path: string) => {
    const absolute = resolve(repositoryProjectsRoot, path);
    return { path, sha256: sha256(readFileSync(absolute)) };
  });
  return { ...component, bindings };
}).sort((left: any, right: any) => left.component_id.localeCompare(right.component_id));

const systemOntology = {
  schema_version: "domainspec-compiled-system-ontology/v1",
  ontology_id: "DSV2-SYSTEM-ONTOLOGY-SFOL-TEST-CLOSURE",
  authority: "generated-candidate-read-model",
  source_graph_digest: graphDigest,
  source_manifest_digest: manifestDigest,
  development_profile_digest: sha256(readFileSync(profilePath)),
  components,
  admission: "not-granted",
};
const systemOntologyBytes = stable(systemOntology);
const systemOntologyDigest = sha256(systemOntologyBytes);
const graphPath = resolve(generatedRoot, "compiled-graph.json");
const manifestPath = resolve(generatedRoot, "source-manifest.json");
const ontologyPath = resolve(generatedRoot, "system-ontology.json");
mkdirSync(generatedRoot, { recursive: true });
writeFileSync(graphPath, first.graphBytes);
writeFileSync(manifestPath, first.sourceManifestBytes);
writeFileSync(ontologyPath, systemOntologyBytes);

const buildReceipt = {
  schema_version: "domainspec-sfol-test-closure-build-receipt/v1",
  result: "pass",
  compile_runs: 2,
  byte_identical: true,
  source_set_digest: first.graph.source_set_digest,
  compiled_graph_sha256: graphDigest,
  source_manifest_sha256: manifestDigest,
  system_ontology_sha256: systemOntologyDigest,
  development_profile_sha256: sha256(readFileSync(profilePath)),
  authority_effect: "none",
};
const buildReceiptDigest = write(resolve(generatedRoot, "build-receipt.json"), buildReceipt);

const definitionDigest = sha256(readFileSync(definitionPath));
const definitionSelectionDigest = sha256(readFileSync(definitionSelectionPath));
const definitionSelection = json(definitionSelectionPath);
if (
  definitionDigest !== "9ae36dd69ecbf89054d1e4e1b50359dbb9639d5ea3d987a85a66694c8a0e1e11" ||
  definitionSelectionDigest !== "fb7a58b7762a8955b75cb01455248230e4e04be67227a254f07a3dc620f2c082" ||
  definitionSelection.decision_id !== "DSV2-DEC-SFOL-DEFINITIONS-001" ||
  definitionSelection.candidate_digest !== "6a159ccf30b6c05654b72bbbfd10117266aaa0bcf498c7e5a30af3300331a335" ||
  definitionSelection.subject_sha256 !== definitionDigest ||
  definitionSelection.selected_option !== "ADMIT-EXACT"
) {
  throw new Error("SFOL_DEFINITION_ADMISSION_SELECTION_INVALID");
}
const productCapabilityDigest = sha256(readFileSync(productCapabilityPath));
const productCapabilitySelectionDigest = sha256(readFileSync(productCapabilitySelectionPath));
const productCapabilitySelection = json(productCapabilitySelectionPath);
if (
  productCapabilityDigest !== "3d1854ad37b1fb9dc568fa1c75a6a2f82520edbff97eba35a0a280ccc572a57c" ||
  productCapabilitySelectionDigest !== "f574a4f9a0b69a7782650a8bc77aa3d56669ba8cbd016556b4d371fac502cdc0" ||
  productCapabilitySelection.decision_id !== "DSV2-DEC-SFOL-CAPABILITY-001" ||
  productCapabilitySelection.candidate_digest !== "26221d25523cb4fe9d92b0e9c473cc5bf290b93c45dfa529b01198a8839e238b" ||
  productCapabilitySelection.subject_sha256 !== productCapabilityDigest ||
  productCapabilitySelection.selected_option !== "ADOPT-EXACT" ||
  JSON.stringify(productCapabilitySelection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest])
) {
  throw new Error("SFOL_PRODUCT_CAPABILITY_ADOPTION_SELECTION_INVALID");
}
const businessOntologyDigest = sha256(readFileSync(businessOntologyPath));
const propertyDenominatorDigest = sha256(readFileSync(propertyDenominatorPath));
const businessOntologySelectionDigest = sha256(readFileSync(businessOntologySelectionPath));
const businessOntologySelection = json(businessOntologySelectionPath);
if (
  businessOntologyDigest !== "769d3b364d6a0954689383f8bb7cb92cdaf60cbef76ff7ba5a88e09342e8c426" ||
  propertyDenominatorDigest !== "db481764813e3f61398d89683b497855ee504173b1cffdfa7ee30450be3cb68d" ||
  businessOntologySelectionDigest !== "92a46fada72bb17d1923158fee6ea5a7d9bce27d38a53362acb45074010d3ab4" ||
  businessOntologySelection.decision_id !== "DSV2-DEC-SFOL-BUSINESS-ONTOLOGY-001" ||
  businessOntologySelection.candidate_digest !== "33a0947ff5b8009466fa1bf9b95ada4a3fb0246b46261900507b283af95bd0c1" ||
  businessOntologySelection.subject_sha256 !== businessOntologyDigest ||
  businessOntologySelection.selected_option !== "ADMIT-EXACT" ||
  JSON.stringify(businessOntologySelection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest, productCapabilitySelection.selection_digest]) ||
  JSON.stringify(businessOntologySelection.additional_source_bindings) !== JSON.stringify([{ path: "property-denominator.json", sha256: propertyDenominatorDigest }])
) {
  throw new Error("SFOL_BUSINESS_ONTOLOGY_ADMISSION_SELECTION_INVALID");
}

write(resolve(capabilityRoot, "construction-binding.json"), {
  schema_version: "cyberalchemy-construction-binding/v1",
  binding_id: "CAV2-D65-SFOL-TEST-CLOSURE-001",
  chain: {
    definitions: {
      path: "definition-candidates.json",
      sha256: definitionDigest,
      status: "admitted-exact",
      admission_selection: {
        path: "decisions/definition-admission-selection.json",
        sha256: definitionSelectionDigest,
        selected_option: definitionSelection.selected_option
      }
    },
    product_capability: {
      path: "product-capability.json",
      sha256: productCapabilityDigest,
      status: "adopted-exact",
      adoption_selection: {
        path: "decisions/product-capability-adoption-selection.json",
        sha256: productCapabilitySelectionDigest,
        selected_option: productCapabilitySelection.selected_option
      }
    },
    business_ontology: {
      path: "business-ontology.json",
      sha256: businessOntologyDigest,
      status: "admitted-exact",
      property_denominator: { path: "property-denominator.json", sha256: propertyDenominatorDigest },
      admission_selection: {
        path: "decisions/business-ontology-admission-selection.json",
        sha256: businessOntologySelectionDigest,
        selected_option: businessOntologySelection.selected_option
      }
    },
    domainspec_source: { path: "domainspec/project.json", source_set_digest: first.graph.source_set_digest, status: "compiled-development-candidate" },
    system_ontology: { path: "generated/system-ontology.json", sha256: systemOntologyDigest, status: "generated-candidate-not-admitted" },
    implementation_binding: { path: "implementation-map.json", sha256: sha256(readFileSync(resolve(capabilityRoot, "implementation-map.json"))), status: "exact-byte-bound" },
    conformance_evidence: { path: "conformance/evidence.json", status: "pending-validation-run" }
  },
  build_receipt: { path: "generated/build-receipt.json", sha256: buildReceiptDigest },
  result: "not_evaluable",
  blockers: ["DomainSpec source acceptance", "development profile eligibility decision", "system ontology admission", "conformance evidence"],
  claim_limit: "Development candidate compilation and exact implementation binding only; no admission, publication, deployment, or production-security authority."
});

process.stdout.write(`${stable({ result: "pass", nodes: first.graph.nodes.length, edges: first.graph.edges.length, graph_sha256: graphDigest, system_ontology_sha256: systemOntologyDigest })}`);
