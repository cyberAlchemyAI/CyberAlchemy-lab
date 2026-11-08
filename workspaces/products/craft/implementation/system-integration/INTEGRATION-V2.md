# DomainSpec integration generation v2 candidate

DomainSpec describes integration meaning independently of provider code, then emits native project artifacts for TypeScript, Python, or Rust. The input is one closed `domainspec.integration-generation-source/v2-candidate` document containing the persistence, messaging, external API, disclosure, and one-way ORODI observation compositions.

Applications consume the package API:

```ts
import {
  planIntegrationProjectV2,
  type IntegrationGenerationSourceV2,
} from "@domainspec-v2/cli";

const source: IntegrationGenerationSourceV2 = {
  schema_version: "domainspec.integration-generation-source/v2-candidate",
  source_id: "integration-source:commerce-v2",
  persistence,
  messaging,
  external_api,
  disclosure_policy,
  orodi_binding,
};

const plan = planIntegrationProjectV2(source, "typescript");
```

The plan contains deterministic artifacts, their hashes, a cross-language semantic manifest, and an exact plan digest. Generated application contracts use TypeScript interfaces, Python protocols, or Rust traits. Provider bindings, mappings, configuration, migrations, observation descriptors, and the semantic manifest are kept in responsibility-specific project paths; no generic `runtime/` directory is generated.

The generator validates every composition before rendering. It rejects extra aggregate fields, unsupported schema versions and languages, definition-pack drift, disclosure-policy mismatches, and invalid provider or mapping relationships.

This surface is a candidate. Generation and native compilation demonstrate deterministic structure and compile validity. They do not establish provider selection, deployment, production behavior, admission, publication, or runtime guarantees. ORODI receives only disclosure-bounded observations and has no return or control edge.
