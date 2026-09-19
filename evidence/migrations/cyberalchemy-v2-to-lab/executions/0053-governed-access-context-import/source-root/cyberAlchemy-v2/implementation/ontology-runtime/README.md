# CyberAlchemy Ontology Runtime

Status: candidate implementation; admission and conformance remain fail-closed.
Authority effect: none.

This is the first bounded runtime realization of the CyberAlchemy Ontology
Product. It manages explicitly registered ontology packages through local,
read-only operations:

1. `route-preflight` binds one ontology-related agent request to a current
   registered ontology snapshot before route-specific repository reads;
2. `catalog` reports whether each configured registration is exact and current;
3. `snapshot` compiles a deterministic, content-addressed read model;
4. `get-record` retrieves one record by declared kind and logical ID; and
5. `validate` / `validate-all` wrap each package's native validator without
   changing or upgrading its verdict.

The runtime does not discover packages, edit ontology sources, refresh source
digests, write validation receipts, promote or accept ontologies, infer meaning,
run agents, publish, release, deploy, or make network requests.

## Registered ontologies

The local registry currently binds five private packages:

- `cav2.ontology-product`, the Ontology Product ontology;
- `cav2.define.system-runtime.v1`, the Define Session Runtime system ontology;
- `cav2.capability`, the canonical shared Capability Ontology;
- `cav2.workspace.capability`, the Workspace capability ontology;
- `cav2.durable-storage.business`, the Durable Storage business ontology.

Registration makes exact current bytes queryable and fail-closed under digest
drift. It does not accept any ontology or upgrade its native validator result;
each registration can still report its own currentness blocker.

## Construction chain

The package follows `CAV2-D65`:

```text
CAV2-D63, CAV2-D65, and CAV2-D67 selector bindings
  -> CA2-CAP-MANAGE-ONTOLOGIES Product Capability
  -> capability-local business ontology
  -> DomainSpec v2 authored source
  -> deterministic graph and candidate system ontology
  -> exact runtime.py binding
  -> tests and static conformance assessment
```

The current Ontology Product native validator is intentionally reported as
`BLOCK` because its own whole-file source bindings have drifted. A selector-bound
runtime snapshot can still be deterministic and source-current; it does not
override that native result. The DomainSpec development profile and generated
system ontology are not admitted, so the overall construction remains
`not_evaluable` for conformance.

## Use

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py route-preflight --ontology cav2.ontology-product --intent inspect --route CA2-ROUTE-ONTOLOGY
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py catalog
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py snapshot --ontology cav2.ontology-product
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py get-record --ontology cav2.ontology-product --kind node --id CA2-PRODUCT-ONTOLOGY
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py snapshot --ontology cav2.define.system-runtime.v1
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py get-record --ontology cav2.define.system-runtime.v1 --kind node --id define-session-runtime.DefineSession
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py snapshot --ontology cav2.capability
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py get-record --ontology cav2.capability --kind capability-reference --id CAP-REF-AGENT-INVOKE-DEFINE
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/implementation/ontology-runtime/runtime.py validate-all
```

`route-preflight` does not select or replace the objective route. It records the
already selected route, proves the registered ontology snapshot is current, and
returns `effect_authorized:false`. For `validate` intent it also preserves the
native validator verdict. A mutation or publication route must still obtain its
own exact authorization, and the preflight must be repeated after any material
ontology change.

Build the deterministic DomainSpec views with:

```bash
toolchains/node-typescript/bin/node-env run --project projects/domainspec-v2/impl -- \
  node --import tsx ../../../cyberAlchemy-v2/implementation/ontology-runtime/scripts/build.ts
```

## Claim ceiling

This package demonstrates a bounded read-only ontology-management runtime and
records its blockers. It does not establish Product Capability adoption,
DomainSpec profile admission, system-ontology admission, implementation-baseline
acceptance, full D65 conformance, runtime production readiness, publication,
release, or deployment.
