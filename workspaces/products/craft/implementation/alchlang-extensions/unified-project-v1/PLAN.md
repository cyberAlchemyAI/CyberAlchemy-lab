# Unified project prototype

Product construction frontier: connect the existing declarative function compiler to the DomainSpec project loader, graph, certificate and standard build/verify path. Runnable now; no operational dependency blocks this prototype.

Definitions: a composition is a declared project source containing a typed behavioral contract, core-node bindings, boundary configuration, original source and derived ontology scaffold. A compiled composition is a validated dependency graph and generated artifacts bound by the project certificate. Compiler references are not admitted ontology relationships.

Construction stages (CAV2-D65): existing language definitions and ontology scaffolds -> product prototype (one deployable pricing function) -> business prototype (bounded base-price quotation) -> DomainSpec project/v2 composition source -> compiled composition graph -> generated behavior plus transport adapter -> exact local product candidate and current tests. Product approval remains a separate owner decision after tests.

Implementation scope: DomainSpec CLI input/{project-root,source-manifest,project-model,project-composition}.ts, compilation/certificate.ts, generation/{project-build,project-instantiation}.ts, assurance/checked-interchange.ts (explicit unsupported-scope rejection), associated contract schemas, package.json and focused tests; Alch src/{domainspec-project-writer,function-builder}.ts and tests; generated dist outputs and this extension evidence. Existing candidates are unchanged.

Validation: project source identity and dependency closure; typed core bindings; schema, integration and endpoint references; ontology consistency; standard artifact verification and tamper rejection; all 20 pricing fixtures, existing language/runtime tests.

Operational support: release and deployment preparation have no affected construction stage, belong to the release/deployment owner, and are deferred. No credentials, remote services, publication or registry admission are required. Meta-type factory automation remains future development.

## Open Questions

Provider-specific deployment and governed meta-type extension remain outside this prototype. Derived ontology is source-linked scaffold evidence, not an accepted business ontology or proof of business meaning.
