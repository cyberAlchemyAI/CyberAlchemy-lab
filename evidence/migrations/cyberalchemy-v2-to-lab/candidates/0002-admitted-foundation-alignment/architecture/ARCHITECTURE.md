<!-- GENERATED FILE: canonical data is architecture/architecture.json. -->

# CyberAlchemy-lab Migration Architecture

## Decision

Separate active Lab packages from source-preserving imports at every plane.

## Planes

| Plane | Responsibility | Import boundary |
| --- | --- | --- |
| `authority/` | Lab definitions, Artifact Types, constitutions, decisions, schemas, and source admissions | `authority/imports/cyberalchemy-v2/` |
| `product/` | Products, Product Capabilities, product ontologies, and product-construction candidates | `product/imports/cyberalchemy-v2/` |
| `contexts/` | Explicit Bounded Context identities, languages, maps, lineages, migrations, and capability instances | `contexts/imports/cyberalchemy-v2/` |
| `coordination/` | Projects, Goals, handoffs, owner coordination, and non-authoritative work ledgers | `coordination/imports/cyberalchemy-v2/` |
| `implementation/` | Components and explicit Product/runtime bindings | `implementation/imports/cyberalchemy-v2/` |
| `evidence/` | Research, inventory read models, validation, conformance, receipts, observations, and migration evidence | `evidence/imports/cyberalchemy-v2/` |
| `platform/` | Languages, toolchains, runtimes, tools, profiles, locks, and environment declarations | `platform/imports/cyberalchemy-v2/` |
| `tooling/` | Repository generators, validators, schemas, and migration tooling | `None` |
| `tests/` | Cross-package fixtures and conformance suites | `None` |
| `docs/` | Architecture, proposals, plans, and historical source documentation | `docs/imports/cyberalchemy-v2/` |

## Recursive bounded-context form

A Bounded Context may contain its own language, maps, instances, specification/authored/generated, implementation/components/bindings, evidence, tests, construction, and handoff surfaces; those nested surfaces retain the same authority distinctions as root planes.

## Import rule

An imports/cyberalchemy-v2 package is source evidence. Promotion into an active package requires an exact owner decision and does not mutate the imported bytes.

## Runtime rule

Installed dependencies, compiler output, caches, activation state, and host bindings are reconstructed through platform profiles and locks, never migrated as canonical bytes.

## Claim ceiling

This candidate selects migration architecture and dependency rules only. It does not make imported material canonical, execute copies, delete sources, or activate runtimes.
