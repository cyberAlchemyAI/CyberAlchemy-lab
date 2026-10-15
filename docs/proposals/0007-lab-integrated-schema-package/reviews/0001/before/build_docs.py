#!/usr/bin/env python3
"""Render candidate package documentation and explicit runtime obligations."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAT=json.loads((HERE/'schema-catalog.json').read_text())
WORKFLOWS=json.loads((HERE/'workflow-catalog.json').read_text())

def write(name,text):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def dump(name,value):write(name,json.dumps(value,indent=2,sort_keys=True))

# These are responsibilities to implement and evidence, not implemented validators.
checks={
'O-EXACT':('Exact binding','Verify selected bytes, scope, identity, version, schema, selector and predecessor; reject ambiguous or altered references.'),
'O-HASH':('Stable hashing','Define encoding and digest boundaries; keep Decision cores independent of generated consequences and their receipts; detect all altered reviewed inputs.'),
'O-CUT':('Source cut','Verify every selected stream head and watermark, compatibility and freshness; reject stale write preconditions and disclose stale reads.'),
'O-CARRIER':('Domain carrier','Select the exact schema and selector; enforce current-write versus historical-read posture; verify identity and discriminators, body/header agreement and extension rules.'),
'O-CANDIDATE-CARRIER':('Prospective carrier','Resolve exact candidate descriptor/schema closure before validation; maintain separate candidate dispatch until a complete owner-authorized admission permits the new carrier.'),
'O-REFERENCE':('Reference closure','Resolve transitive dependencies, selectors, cross-artifact equality, ownership and admissibility; preserve unresolved, ambiguous, excluded and historical states.'),
'O-RELATION':('Typed connection','Verify declared endpoint pair, explicit carrier/endpoint mappings, qualifier value domains, pair-specific constraints, semantic direction and the canonical writable authority.'),
'O-EXTENSION':('Typed extension','Require the unique semantic question, orthogonal axis, exact pairs, qualifiers, semantic noncollapse analysis, affected carrier successors and owner review before new connections are writable.'),
'O-AUTHORITY':('Authority evaluation','Verify real principal/role/delegation/owner authority, action and effect scope, time, revocation, redelegation, all gates and exact authorization provenance; schema validity grants no authority.'),
'O-VIEW':('Bounded view','Apply selectors, exclusions, depth, privacy and byte budgets; attribute every included result to exact source evidence and expose freshness/gaps; context grants no authority.'),
'O-MEMORY':('Ephemeral memory','Keep machine Agent identity/session short memory ephemeral, expire it on close/failure/cancellation and prevent exports or persistence; durable continuity comes from governed Project State via Context and Ontology Views.'),
'O-PRIVACY':('Custody and disclosure','Enforce source and export scope, owner review, exclusions and private custody; keep credentials and session memory out of repository packages and query caches.'),
'O-PROFILE':('Profile compatibility','Pin source and executable independently; require explicit successor/branch and selective revalidation rather than changing old source cuts or silently rebasing history.'),
'O-ACTION':('Action dispatch','Evaluate exact inputs and bounds before tools run; observe real outputs and effects, attribution and budget; record success, failure or uncertainty without inferred completion.'),
'O-RECOVERY':('Recovery and retry','Observe uncertain effects before retry; enforce idempotency, expected heads and recovery contracts; reconcile allowed residue without deleting committed history.'),
'O-EVIDENCE':('Evidence and claim ceiling','Bind validator, observations, methods, sample/environment and results; distinguish authoring checks, implementation verification, operational success and assessed outcomes.'),
'O-COMMIT':('Canonical publication','Preflight exact authority, dependency closure and expected head; stage immutable packages/records, serialize competing writers, publish one canonical head and verify crash recovery/idempotency.'),
'O-BYTES':('Original content','Verify byte count, media type, digest and encoding against original bytes; include the complete dependencies needed for portable replay; JSON normalization is not exact reconstruction.'),
'O-PROJECTION':('Disposable SQLite generation','Enforce SQL/SQLite compatibility, foreign keys, complete input generation and watermarks; switch the active generation only after checks; rebuild from canonical sources and reject invalid or undisclosed stale results.'),
'O-FILE':('File generation','Verify the selected output scope and safe paths including symlinks; preserve unmanaged files, stage and publish a complete generation, pin rendering and distinguish exact exports from rendered views.'),
'O-WORKFLOW':('Workflow transition','Bind carrier lifecycle mappings, actor routes, exact checks and decision profile; validate current state, required inputs, transitions, satisfaction, concurrency and recoverability; assessed outcomes remain separate from tool completion.'),
'O-CLASSIFICATION':('Classification axes','Verify scheme/value/axis agreement, applicability and independent classification dimensions; classification assignment does not establish causality or authority.'),
'O-FAILURE':('Failure analysis','Separate occurrence, mode, cause hypothesis, impact, incident threshold and control/recovery assessment; bind evidence and preserve uncertainty.'),
'O-CHALLENGE':('Contestability','Verify the exact Challenge Contract, challenger eligibility, grounds, response and resolution routes and evidence; retain the challenged subject and distinguish semantic from governance consequences.'),
'O-LESSON':('Operational learning','Select lessons by evidenced applicability and exclusions; preserve observation/reflection/lesson/application/outcome distinctions; assess applications and counterevidence before broader effectiveness claims.'),
'O-ONTOLOGY':('Ontology representation','Maintain represented-subject identity, source revisions and independent Lab/ontology stream heads; global relation projections are read-only, local ontology edges obey their own profile and authority.'),
'O-MIGRATION':('Migration accounting','Account for all selected source items and their dependencies with import/adaptation/reference/defer/exclude/block disposition; preserve source custody and do not infer broad cutover or source retirement.'),
'O-ADOPTION':('Capability adoption','Verify capability realization binding, implementation conformance, owner-local scope, observation contract and actual authorization; admission and operational adoption have distinct evidence.'),
'O-RELEASE':('Release acceptance','Verify exact package closure, product/thesis/capability bindings, acceptance contracts, pilot observations, compatibility and release Decision; candidate evidence is not production acceptance.'),
'O-INSTALL':('Local installation','Verify exact release, target, authority, preimage, private custody and rollback; observe installed postimage and uncertain residue without inferring service activation.'),
'O-TRANSPORT':('Service boundary','Resolve exact operation and request/result schemas, authenticate the actual caller, evaluate policy and bounds, verify request/result correspondence and avoid interpreting caller_requirement text as permission.'),
}
used={o for p in CAT['protocols'] for o in p['runtime_obligations']}
assert used==set(checks),(used-set(checks),set(checks)-used)
obligations=[{'obligation_ref':k,'name':v[0],'required_behavior':v[1],'implementation_posture':'required-for-selected-use-not-established-by-this-package','failed_behavior':'Block the affected write/effect; for an eligible read disclose the gap and bounded claim ceiling.','schema_validity_satisfies_obligation':False} for k,v in checks.items()]
dump('obligations.json',{'schema_version':'lab-runtime-obligations/v1-candidate','authority_effect':'none','obligations':obligations})
write('RUNTIME-OBLIGATIONS.md','''# Runtime obligations

Status: proposed. These 31 responsibilities describe what runtime code and observed evidence must establish. A JSON Schema validates message shape; it cannot verify a signature, a hash, a live owner, causal evidence, a path on disk or a committed transaction.

The [machine-readable catalog](obligations.json) is linked from every protocol in [schema-catalog.json](schema-catalog.json). No responsibility is certified implemented by this package. Existing bounded runtime behavior retains its existing evidence and scope.

'''+ '\n\n'.join(f'## {k}: {v[0]}\n\n{v[1]}\n\nFailure: block the affected write or effect; disclose gaps and claim limits in eligible reads.' for k,v in checks.items()))

write('PROPOSAL.md','''# Integrated Lab schema package

Status: **candidate; no admission or runtime effect**. Scope: the selected local Agent–Lab model and its future implementation boundary.

This package produces the message contracts needed to connect the existing Lab artifact model with ephemeral Agents, local services, review/admission, workflows, ontology representations, SQLite queries and generated files. It reuses current domain contracts and the prior storage proposal.

## What is included

| Surface | Coverage |
|---|---:|
| New candidate protocol schemas | 72 |
| Registered domain contract versions bound exactly | 143 |
| Current domain carriers eligible for current-write evaluation | 121 |
| Historical carrier versions retained for reading | 22 |
| Existing Relation Kinds / exact declared endpoint pairs | 41 / 550 |
| Reused candidate storage JSON schemas | 4 |
| Reused SQLite DDL tables | 12 |
| Candidate service operations | 27 |
| Candidate workflow models | 10 |
| Runtime obligations | 31 |
| Illustrative protocol messages | 71 |

The shared `common` schema defines reusable structures and has no standalone message example. New protocols are implementation messages, not newly admitted Artifact Types. Actual domain bodies continue to use their selected registered contracts.

## Read the design

1. [Architecture and Agent interaction](ARCHITECTURE.md).
2. [Every protocol schema, its purpose and example](SCHEMAS.md).
3. [All bound domain contract versions and their current/historical posture](DOMAIN-CONTRACTS.md).
4. [Ten workflow models and completion requirements](WORKFLOWS.md).
5. [Runtime obligations](RUNTIME-OBLIGATIONS.md).
6. [Contract fit and unresolved integration decisions](FIT-REPORT.md).
7. [Review and authoring evidence](REVIEW.md).

The [package manifest](package-manifest.json), [source baseline](SOURCE-BASELINE.json) and [authoring receipt](receipts/schema-authoring.json) bind exact files. Receipt generation does not authorize an effect.

## Storage choice represented here

Existing canonical files retain their current source/admission role. Future exact-byte packages and immutable commit records can capture selected new operational content. SQLite is a rebuildable query projection. File generation exports selected original bytes or renders a view with a pinned renderer. Lab and ontology retain explicit, separate source cuts and authorities.

The underlying candidates are [storage proposal 0006](../0006-lab-artifact-storage/PROPOSAL.md) and [the integrated roadmap](../../plans/0009-lab-integrated-roadmap/PLAN.md). This package adds no performance or storage-saving measurement.

## Admission boundary

A future complete review package can present independent exact Decision cores in one final owner checkpoint. All required owners must authorize their exact members. Deterministic canonical consequences and derived generations retain provenance to that authorization. Local action effects, repository admission and release acceptance keep their own scopes.

This package does not authorize unknown future Work, lessons, signatures, installations, external effects or service activation. Selected protocols forbid network scopes and external effects; admission transactions permit zero runtime activations. The owner review will occur after the exact implementation package and its required evidence exist.
''')

write('ARCHITECTURE.md','''# Architecture and Agent interaction

Status: proposed integration design. The new service names are responsibilities; transport and implementation remain to be selected.

```mermaid
flowchart TD
    P[Project State and canonical sources] --> V[Context and Ontology Views at exact cuts]
    V --> S[Ephemeral Agent session]
    S --> R[Lab read and proposal services]
    S --> A[Authority evaluation and bounded local actions]
    A --> E[Observed outputs and evidence]
    E --> R
    R --> C[Exact candidates and validation]
    C --> H[One final checkpoint with independent owner Decision cores]
    H --> T[Authorized canonical commit]
    T --> P
    T --> Q[Disposable SQLite generation]
    T --> O[Ontology representations with independent watermark]
    T --> F[Selected byte exports or rendered files]
    S --> M[Session short memory expires on close]
```

## 1. Prepare an assignment

The governed Project, Goal, Work, Coordination Context and Intent Resolution identify the objective and method route. Agent Profile, capabilities and Implementation describe the available realization. Principal, role, responsibility, Authority Boundary and Delegation determine what the actual actor may do. Capability existence alone grants no permission.

A Coordination Context retains one Goal. Work can be partitioned into multiple bounded assignments without turning that context into a multi-goal object.

## 2. Deliver bounded context

`context.get` binds the assignment, Work and exact source cut. Delivery names Context View and Ontology View plus included sources, exclusions, lessons, freshness, expiration and gaps. `artifact.inspect` shows original body, contract and separate status facets. `artifact.query` returns references with projection generation and paging/depth/byte limits.

Admission status, domain lifecycle, implementation state, runtime observation and outcome assessment remain separate facets. Historical body labels are preserved; effective admission is explained through exact authority evidence.

## 3. Open an ephemeral session

`session.open` binds the assignment, capability/profile realization, delivered context, authority references and budget. Session memory is process-local, cannot be exported or written durably and expires with the session. A new session reconstructs continuity from Project State through views.

Eligible observed outputs may become separately governed observations, action evidence, lessons or other artifacts. Persisting one of those artifacts requires its contract, attribution and applicable authority. A session dump is not Project State. `session.close` requests termination; its separate receipt records whether termination and memory disposal actually occurred and names unresolved action residue.

## 4. Act and propose

A tool adapter pins input/output schemas, implementation, effect scope, retry semantics and recovery contract. `action.evaluate` checks actual authority. `action.dispatch` observes real results; indeterminate actions require reconciliation before retry. A valid request cannot substitute for this evaluation.

`change.prepare` and `change.validate` produce exact candidate effects. Existing domain schemas validate body shapes; runtime checks resolve identity, reference closure, current carrier posture, typed pair/qualifier semantics and evidence. Candidate new contracts use a separate binding and require owner review before becoming writable.

## 5. Review and apply

The review includes exact diffs, examples, declared consequences, validation, exclusions and private/public review. Stable Decision cores bind independently governed members. The reviewed package binds those cores, real materialized targets and the applicable Workflow Decision Profile. Actual owner conversation provenance, a verified signature or existing exact authority can supply authorization evidence; the chosen channel requires its own verified contract.

`admission.apply` checks the expected cut, exact authorization and immutable package closure. It stages content and records, serializes canonical writers and publishes a canonical head only after the selected transaction protocol is satisfied. Replay and recovery must verify the full chain and preserve committed history. The schema package describes these obligations; it does not implement them.

## 6. Derive and inspect

The commit receipt distinguishes canonical commit from projection and file status. SQLite receives a complete generation with source verification and watermarks. Queries never infer a new admission from cached rows. Ontology projection binds represented source revisions and its independent stream/cut; ontology representation does not confer Lab authority.

A byte-exact file export reproduces verified stored original bytes. A rendered view binds renderer/version and inputs. Both are managed generations with safe paths, scope/privacy review and no overwrite of unmanaged files. Portable packages include required dependencies and exclude credentials and session memory.

## Selected components

| Component | Responsibility | Binding |
|---|---|---|
| Existing domain contracts | Govern artifact bodies and their versioned semantics | [Domain bindings](domain-bindings.json) |
| Candidate protocol contracts | Type messages, configurations and receipts | [Schema catalog](schema-catalog.json) |
| Service adapter | Authenticate caller, resolve operation, evaluate bounds and policy | [Service contracts](service-contracts.json) |
| Workflow engine | Apply bound transitions and record assessed satisfaction | [Workflow models](WORKFLOWS.md) |
| Canonical publisher | Exact authority, immutable package, ordered records and head | [Commit obligations](RUNTIME-OBLIGATIONS.md) |
| SQLite projector | Disposable complete read generations | [SQL DDL](../0006-lab-artifact-storage/schemas/sqlite-read-model.sql) |
| Ontology adapter | Explicit representation mapping and separate authority/cut | [Ontology mapping schema](schemas/ontology-mapping.schema.json) |
| File/package adapter | Verified byte exports and pinned rendered generations | [File generation schema](../0006-lab-artifact-storage/schemas/file-generation.schema.json) |

No persistent database, runtime directory, transaction or installation is created by authoring this package.
''')

parts=['# Protocol schemas\n\nStatus: candidate. All new JSON schemas use Draft 2020-12 and explicit `v1-candidate` resource identifiers. Cross-field semantic checks are assigned to [runtime obligations](RUNTIME-OBLIGATIONS.md). The [offline resolver](resources.py) loads pinned local resources without network access.\n\nExisting bodies and selectors are retained in [domain bindings](domain-bindings.json). Their schemas are not rewritten into a universal body shape.']
for group in dict.fromkeys(p['group'] for p in CAT['protocols']):
    parts.append(f'## {group.title()}\n\n| Schema | Purpose | Example | Obligations |\n|---|---|---|---|')
    for p in CAT['protocols']:
        if p['group']!=group:continue
        example='Shared definitions' if p['name']=='common' else f'[Message](examples/{p["name"]}.json)'
        parts.append(f'| [{p["name"]}]({p["path"]}) | {p["purpose"]} | {example} | '+', '.join(p['runtime_obligations'])+' |')
parts.append('''## Reused storage schemas

These four candidate schemas and the 12-table SQL DDL retain their exact source bindings. They are owned by [storage proposal 0006](../0006-lab-artifact-storage/SCHEMAS.md).

| Schema | Responsibility |
|---|---|
| [artifact-content-entry](../0006-lab-artifact-storage/schemas/artifact-content-entry.schema.json) | Original bytes, digest, byte count, media type and content identity |
| [artifact-package-manifest](../0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json) | Exact input source cut, immutable entries and dependencies |
| [projection-generation](../0006-lab-artifact-storage/schemas/projection-generation.schema.json) | Complete verified disposable projection inputs and watermarks |
| [file-generation](../0006-lab-artifact-storage/schemas/file-generation.schema.json) | Managed exact or rendered files and output digests |
| [SQLite read model](../0006-lab-artifact-storage/schemas/sqlite-read-model.sql) | Query indexes, revisions, typed relations, reference resolution, authority facts, ontology links and gaps |

## Domain and compatibility resources

[DOMAIN-CONTRACTS.md](DOMAIN-CONTRACTS.md) links every one of the 143 bound versions and marks the 121 current carriers. Read/write eligibility still requires runtime authority and compatibility checks. Six existing v2 local-runtime message schemas and the Session Memory schema are pinned in [schema-catalog.json](schema-catalog.json); they do not become general admission authority.

Nine historical wrapper references select two repository schema dependencies. [schema-dependencies.json](schema-dependencies.json) declares each exact compatibility mapping. The offline resolver substitutes those declared file resource references in memory, retaining the original files and their hashes. This explicit adapter must be reviewed for runtime use; no network URL is dereferenced.

## Services

[service-contracts.json](service-contracts.json) binds 27 candidate operations to exact request, success and error schemas. `tool-service-request` and `tool-service-result` close dispatch to those operations. Helpers such as carrier mappings, authority proofs, extension reviews and release manifests are inputs to those services; they are not additional public endpoints. A declared caller requirement is not authorization.
''')
write('SCHEMAS.md','\n\n'.join(parts))

bindings=json.loads((HERE/'domain-bindings.json').read_text())['bindings']
rows=['# Bound domain contracts\n\nStatus: exact source bindings for this candidate integration package. Current means selected by the bound Artifact Type Registry; it does not establish instance admission, actor authority or end-to-end runtime compatibility. Historical versions remain available for reading.\n\n| Exact carrier | Write posture | Semantic kind | Original schema | Selector |\n|---|---|---|---|---|']
for b in sorted(bindings,key=lambda x:x['carrier_ref']):
    rows.append(f'| {b["carrier_ref"]} | {b["write_posture"]} | {b["semantic_kind"]} | [Schema](../../../{b["schema_path"]}) | {b["schema_selector"] or "root"} |')
write('DOMAIN-CONTRACTS.md','\n'.join(rows))

completion={
'intent-framing':'Resolve intent into explicit Goal/Work/method scope and implementation route; retain the one-Goal Coordination Context.',
'agent-context':'Verify assignment/authority and bounded Context/Ontology Views before opening the ephemeral session.',
'engineering':'Bind reviewed design, implemented outputs and required observations; assess Work outcome against its satisfaction contract.',
'research':'Bind inquiry/hypothesis/design, method/measurements and run evidence; assess findings with stated uncertainty.',
'failure-assessment':'Keep occurrence, classification, cause assessment and response/control evidence distinct; evaluate recovery and incident criteria.',
'challenge-handling':'Establish eligibility, response and actual owner Decision under the bound Challenge Contract; preserve contestability and history.',
'operational-learning':'Prepare an evidenced lesson, record a scoped application and assess its outcome/counterevidence before declaring effectiveness.',
'review-admission':'Materialize the whole review package, record exact authorized member outcomes and verify canonical application independently of projections.',
'ontology-migration':'Map selected source items and representations, validate candidates and account for every selected disposition; no global migration completion inferred.',
'product-adoption-release':'Assess capability realization/conformance, actual scoped pilot observations and owner release Decision; no service activation implied.',
}
rows=['''# Workflow model candidates

Status: ten proposed coordination models. They are schema-valid model instances with stage-specific outputs. They are not admitted Workflow Profiles or executable lifecycle mappings. Input/output carrier declarations identify permissible contracts, not fabricated artifact instances or automatically satisfied requirements.

Each model requires an exact Workflow Decision Profile, actor/authority routes, domain lifecycle mappings, concrete preconditions, declared connections and satisfaction checks. [domain-lifecycle-mapping](schemas/domain-lifecycle-mapping.schema.json) provides the schema for this binding. The current templates intentionally retain unbound authoring references and empty mapping bindings; execution must block until they are resolved. Blocked and indeterminate states require a bound recovery disposition; this package does not invent automatic retry transitions.

| Model | Proposed coordination path | Required completion evidence |
|---|---|---|''']
for w in WORKFLOWS['workflows']:
    m=json.loads((HERE/w['path']).read_text());states=[s for s in m['states'] if s not in ('blocked','indeterminate','cancelled')]
    rows.append(f'| [{w["name"]}]({w["path"]}) | '+ ' → '.join(states)+f' | {completion[w["name"]]} |')
rows.append('''## A realistic future Work example

Suppose a Project needs a capability that shows all definitions and their current status.

1. The owner prepares an Intent, Goal and Work: “show definition content, effective admission, version, evidence and unresolved gaps.” A Coordination Context binds that one Goal. Intent Resolution selects an engineering method and implementation route.
2. An assignment selects an Agent Profile, Implementation and capabilities. Existing Delegation and Authority Boundary permit repository inspection and candidate authoring. They do not imply permission to admit every future output.
3. The Agent requests exact Context and Ontology Views. The Lab returns current Definition contracts, registry references, predecessor decisions and relevant lessons. Missing references are visible gaps.
4. The Agent inspects definitions through `artifact.inspect`/`artifact.query`, prepares interface and query candidates, and uses bounded tool actions where permitted. Action receipts attribute actual outputs and uncertainty.
5. Generated Output, Evidence Set and Work Outcome Assessment bind the observed implementation and its required checks. If a failure occurs, classification and failure assessment feed a scoped lesson candidate rather than a hidden session-memory dump.
6. Once the complete selected package and required observations exist, one owner checkpoint reviews independent exact Decision cores. Each member binds its actual scope, bytes and evidence.
7. The authorized application adapter verifies current heads and commits the selected artifact effects. Project State/history consequences follow that exact transaction. SQLite and ontology projections expose their independent freshness.
8. A requested file generation exports original definition bytes or renders an explanatory index from pinned inputs. The session closes and short memory expires. The next Agent reconstructs continuity from updated Project State and views.

This walkthrough is a proposed execution path. The [example messages](examples/README.md) demonstrate structures; they contain placeholders and provide no evidence that this Work was executed or authorized.

## One final checkpoint

The review/admission model separates preparation, owner resolution and application. Challenge and product-release models also identify owner decisions. A single final interaction is possible for an exact package only when its Workflow Decision Profile permits composition and all required owners can authorize their members. Evidence-producing local actions before that checkpoint require existing exact authority or isolated candidate operation; an end-of-work checkpoint cannot retrospectively authorize their execution.

Future unknown Work, findings, lessons and release bytes cannot be pre-admitted. External provisioning, deployment, network operations and service activation need separately declared scopes and extensions beyond this selected local protocol package.
''')
write('WORKFLOWS.md','\n'.join(rows))

write('FIT-REPORT.md','''# Contract fit and integration gaps

Status: authoring analysis. All current source contracts are retained and bound. Schema-valid messages cannot establish semantic compatibility or execution readiness.

## Exact domain bodies

There are 143 bound versions across 121 current identities. Domain bodies have different identity/discriminator/lifecycle structures; `domain-artifact` dispatches to the exact original schema and selector. `artifact-envelope` adds transport metadata without mutating those bodies. Runtime code must check body/header agreement and effective current-write eligibility. A historical candidate label inside immutable content does not determine present admission authority.

## Endpoint mappings requiring explicit review

Current relation signatures declare semantic endpoints `project`, `product` and `method`. Current carriers do not have exact same-named semantic kinds for these three endpoints. Project Identity and Product Identity are plausible representations of the first two, but mapping them is a semantic decision. A same-named Method carrier is absent.

[carrier-endpoint-binding](schemas/carrier-endpoint-binding.schema.json) declares exact carrier/endpoint, identity selector, permitted relation roles, evidence and semantic owner review. Selected connections remain blocked until those mappings or a reviewed contract extension exist. The illustrative Work `member-of` Project message uses a Project Identity header solely to show the shape; it is not proof of an admitted alias or valid runtime connection. No alias is applied to canonical contracts.

The typed dispatcher closes the 41 existing Relation Kinds and 550 declared pairs and preserves their qualifier property shapes. Some qualifier domains remain string-shaped in the source contract. Runtime validation must apply exact value domains, pair-specific constraints and cross-artifact checks. Schema dispatch is not a semantic noncollapse verdict. [typed-extension-request](schemas/typed-extension-request.schema.json) records the unique question, orthogonal axis, pair and qualifier contracts, writable authority, affected successors and explicit review evidence.

## Workflow and actor bindings

The ten workflow models use proposed coordination states. Those states must be mapped to each selected carrier's lifecycle and observed satisfaction. Actor routes and check references are unresolved template names. Bind the exact lifecycle/profile contracts, ownership, checks and recovery dispositions before running them. A model's final coordination state does not automatically admit its outputs or demonstrate outcome satisfaction.

## Candidate contracts

New carrier candidates have exact candidate schema/descriptor closure and explicit bindings. They remain separate from the 143 registered-version dispatcher until a complete governed admission establishes their current write posture. Structural validation of a prospective schema does not authorize it. Runtime code must resolve the referenced schema bytes and complete dependencies; no unrestricted schema fallback is allowed.

## Canonical store and SQLite

The existing ontology event store uses immutable transaction files, a digest chain and an atomic HEAD; it is not a SQLite event store. Existing Lab source capture is parsed JSON plus hashes, so it cannot by itself reproduce original bytes for all content. Proposed byte packages supply that missing content closure. Storage proposal 0006 provides the exact content/package/generation schemas and 12-table read model.

The publisher, full byte closure, concurrent-writer protocol, query services and file generator remain future implementation work. SQLite DDL authoring checks cannot establish crash behavior, stale-read handling, semantic query results, file safety or performance. The package creates no persistent database or runtime state.

## Authority and the final checkpoint

Existing Admission Transaction/v1 admits repository effects with zero runtime activations and no external effect references. Decision Bundle/v1 requires materialized targets and all-or-nothing application. The proposed protocol preserves independent Decision cores and exact outcomes. A conversation provenance record, operator signature or existing authority must be verified under the chosen channel; no signature is generated by these examples.

One final review can authorize the exact complete selected members. It cannot authorize unknown future artifact bytes, substitute one owner for another, turn local authority into repository admission, or infer operational effects from a transaction. Future external deployment or activation is outside the selected local scope.

## Legacy schema dependencies

Historical wrapper schemas use repository-relative references, including wrappers with URL `$id` values. Nine exact mappings to two local schema dependencies are declared in [schema-dependencies.json](schema-dependencies.json) and pinned in the source baseline. The offline authoring resolver normalizes only these declared reference locations in memory. Original source files and hashes remain intact. A future runtime adapter must bind this compatibility interpretation explicitly; URL resolution is never delegated to the network here.

## Evidence ceiling

The authoring receipt covers schema meta-validation, offline reference resolution, illustrative instance validation, workflow structure, exact source/catalog/signature comparisons, SQL DDL compilation in memory and frozen-runtime file hashes. It does not establish live authority, actual signatures, semantic noncollapse, lifecycle compatibility, implementation conformance, operational pilot success, repository admission, migration or release acceptance.
''')
write('examples/README.md','''# Illustrative messages

There are 71 shape examples, one for each candidate message schema except the shared `common` definitions. They use `example:*` references, placeholder hashes and generally blocked/candidate/denied dispositions. They are not connected operational records, materialized review targets, authorization proofs or actual runtime receipts.

The `domain-artifact` and embedded artifact-envelope body reuse the first governed Work's original parsed body. Its byte digest is copied from the original file; all unrelated header, source-cut and authority placeholders remain illustrative. Original historical body labels are preserved.

The typed Work `member-of` Project connection illustrates a declared endpoint pair. Its Project Identity header still requires an explicitly reviewed carrier/endpoint mapping; see [contract fit](../FIT-REPORT.md). No implicit semantic alias is established.

A schema-valid `authorization-proof` message demonstrates fields only. The sample uses owner-conversation placeholders and contains no real owner provenance or signature. A schema-valid review-package example does not establish that actual targets or evidence exist.

For a coherent human-readable example, see [the workflow walkthrough](../WORKFLOWS.md). For actual package bytes and checks, use the [package manifest](../package-manifest.json) and [authoring receipt](../receipts/schema-authoring.json).
''')
write('REVIEW.md','''# Authoring review

Status: candidate package prepared for design inspection. This is the author's scope and evidence review, not an independent audit or owner admission.

## Produced

72 candidate protocol schemas, four reused storage schemas, the reused 12-table SQL read model, 143 exact domain version bindings, 41 Relation Kind dispatches covering 550 declared pairs, 27 service responsibilities, ten workflow model candidates, 31 runtime obligations and 71 illustrative messages.

## Reproduction

From the repository root:

```bash
python3 docs/proposals/0007-lab-integrated-schema-package/build_package.py
python3 docs/proposals/0007-lab-integrated-schema-package/build_examples.py
python3 docs/proposals/0007-lab-integrated-schema-package/build_docs.py
python3 docs/proposals/0007-lab-integrated-schema-package/check_package.py
```

Builders author only this candidate package. The checker resolves local resources offline, validates authoring, compiles the reused SQL in an in-memory database and writes one authoring receipt. It does not dispatch tools, mutate canonical state, run runtime test suites, install software or change frozen implementation packages.

The [authoring receipt](receipts/schema-authoring.json) reports the concrete checks and binds every package file except itself and ignored Python cache files. The [package manifest](package-manifest.json) has a null authoring-receipt binding so the manifest and receipt do not create a digest cycle; the receipt binds the manifest after generation.

## Remaining requirements before execution or admission

Resolve the [contract-fit gaps](FIT-REPORT.md), select exact lifecycle/actor/authority/channel/transport mappings and implement the [runtime obligations](RUNTIME-OBLIGATIONS.md). Prepare actual target artifacts and the exact implementation package. Obtain the evidence required by each selected contract and scope, then present the complete review package for the final owner checkpoint.

No current artifact contracts, frozen runtime sources, admitted decisions or canonical heads are altered by this proposal. Unrelated working-tree content is retained.
''')

# One-way binding: manifest covers inputs, later authoring receipt binds manifest.
def binding(path):return {'ref':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
dump('package-manifest.json',{'schema_version':'lab-protocol-package-manifest/v1-candidate','authority_effect':'none','package_ref':'lab-integrated-schema-package/0007','status':'candidate',
 'schema_bindings':[binding(HERE/p['path']) for p in CAT['protocols']]+[binding(ROOT/p['path']) for p in CAT['reused_storage_schemas']],
 'domain_catalog_binding':binding(HERE/'domain-bindings.json'),'workflow_model_bindings':[binding(HERE/w['path']) for w in WORKFLOWS['workflows']],
 'obligation_catalog_binding':binding(HERE/'obligations.json'),'source_baseline_binding':binding(HERE/'SOURCE-BASELINE.json'),'authoring_receipt_binding':None,
 'claim_ceiling':'Candidate local protocol schema and model authoring only; no admission, authority verification, runtime execution or operational acceptance.'})
print(json.dumps({'documentation_files':9,'obligations':len(obligations),'package_manifest':'candidate-exact-file-bindings'}))
