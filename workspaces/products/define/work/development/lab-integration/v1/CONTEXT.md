# Define / Lab integration execution context

Task: complete a concrete local connector and provision the missing local operator,
then exercise it with the new User Journey candidate. The user explicitly requested
that everything required for local setup be established in this session.

## Obligations and controlling sources

| Obligation | Selected source and selector |
| --- | --- |
| Keep v1/v2 and standalone contracts distinct | standalone/README.md: How Lab integrates; v2/README.md: host qualification |
| Bind a current Project State and scoped context | lab-runtime/v2/lab_runtime/session.py: Session.context; store.py: replay |
| Map full candidate bodies into native review | lab-runtime/v2/lab_runtime/operations.py: prepare and validate_record |
| Preserve complete Definition/v2 lineage | standalone/define_core/materialize.py: materialize_members |
| Retain exact v3 bytes and reconstruct from Work | standalone/define_core/api.py: inspect/reconstruct; native Source/v1 and Work/v1 contracts |
| Keep actual local authority distinct from repository admission | lab-runtime/v2/lab_runtime/store.py: initialize, authorize, apply |
| Author and index User Journey without changing admitted lookup | authority/definitions/registry.json: Product entry; Definition/v2 schema/generator |

Mode: standard, twelve controlling files in seven obligation-linked source groups; native local execution, no
nested model/runtime delegation. The source-level findings control implementation;
older Body War assessment is historical context only.

## Decisions and write scope

- Add an explicit local connector using current standalone request/Pack v3 and the
  existing native v2 protocol. Do not disguise v3 as a v2 Pack.
- Reuse the runtime's local signed transaction boundary. Provision a new external
  operator directory and fresh key; keep all credentials and stores outside Git.
- Use declared principal `person:<vrondelli>` for the requested local provisioning.
  This is local-user-declared identity, not external identity verification or a
  claim that repository role activation transfers into the local store.
- Native category/effect grants are restricted to local definition and artifact
  instance admissions. No canonical repository admission, source-profile rewrite,
  project restructuring, public service, publication, or deployment is selected.
- Index the new candidate locally; retain the existing admitted registry and source
  baseline. Preserve prior source-profile repairs and all unrelated dirty files.

## Completion checks

1. Explicit setup; scoped grant, source and dependency integrity checks.
2. Actual Lab context -> authored v3 request -> exact Pack -> Definition/v2 materialization.
3. Independent native proposal review; separate signed local authorization/application.
4. Retained Source + Work resolvable after a fresh process, with exact member parity.
5. Refuse stale/expired context, altered material, wrong host, changed grant,
   unqualified use and existing output collisions. Confirm idempotent committed retry.
6. Run connector tests and relevant preserved-runtime regressions; record limits.

The local connector's explicit provisioning is its trust root. The legacy native
gateway's empty qualified-host catalog is not changed or treated as qualification
for this separate local scope. Independent operational release qualification remains
a separate claim; no live external issuer or protected Source8 authority is inferred.
