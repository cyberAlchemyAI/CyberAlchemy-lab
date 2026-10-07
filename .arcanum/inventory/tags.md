# Index labels

The generated path manifest uses repository paths, extensions, and Git
tracking state rather than duplicating labels into every file record. Use
these area labels when adding hand-authored inventory notes:

| Tag | Scope |
| --- | --- |
| `authority` | Canonical governance, definitions, decisions, ownership, and lineage. |
| `contexts` | Context maps and bounded contextual records. |
| `coordination` | Goals, projects, and coordination records. |
| `craft` | Architecture, capabilities, definitions, implementation, and research. |
| `docs` | Plans, proposals, decisions, packs, and explanatory documents. |
| `evidence` | Validation, conformance, and migration evidence. |
| `implementation` | Runtime and implementation bindings. |
| `ontology-lifecycle` | Ontology lifecycle artifacts and runtime materials. |
| `product` | Product definitions and prototypes. |
| `tests` | Tests and conformance fixtures. |
| `tooling` | Generators, importers, schemas, validators, and inventory tooling. |
| `repository-root` | Root-level repository contract and metadata. |
| `definition-status` | Current Definition registry state and candidate-package lineage. |
| `migration-decision` | CyberAlchemy v2 migration choices, authority effects, and execution boundaries. |
| `governance-repository-map` | Path-complete governance zones, status lookup routes, and source-linked integration. |

These labels are navigation hints. They do not change artifact status or
authority.

Content records inherit the area label from their repository path. Archive
member records inherit the area label of the containing archive.
