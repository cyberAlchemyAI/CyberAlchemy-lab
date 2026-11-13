# Shared Lab definitions and records runtime

Run shared operations through the central Lab entry point in WSL.

    node implementation/lab-runtime/lab.mjs shared help

The entry point selects the pinned Node release. Existing native commands remain available through the same entry point. Workspace configuration selects the shared host. Each workspace has its own identity and data namespace inside the stores.

The maintained base business source is contracts.alch, semantics.alch and design.alch in this directory. The maintained directory, handoff, evolution, custody and view contracts are in implementation/lab-workflows/records-workflow/workflow.alch. Compilation uses the imported Craft and AlchLang package. The original creation operations remain in their existing modules and are captured by creation-source.alch. The public creation adapter evaluates those original operations before publishing a draft.

## Commands

| Command | Behavior |
| --- | --- |
| context | Resolve the workspace/runtime model; retain a nullable semantic Project and verify the explicit shared native execution host |
| create | Prepare a native-validated Definition, Record or Artifact Type through its compiled AlchLang guard |
| attest | Validate exact original artifact bytes against a qualified schema and sign an original receipt with an explicitly provided key |
| observe-native | Verify the original native transaction and sign its observation |
| issue | Authenticate original receipts, verify complete artifact bytes, project approved members, reject conflicts, validate the input and seal it |
| evaluate | Authenticate the sealed artifact and evaluate the selected AlchLang decision |
| join-init | Persist a scoped run with stable run/operation identity |
| join-transition | Verify the artifact and actual stored revision, evaluate the transition, then atomically persist phase, event and command receipt |
| join-inspect | Inspect the run and verify retained event/command integrity |
| native-review | Delegate exact proposal review to the native owner |
| native-apply | Require verified workspace context, construction entry, source cut and original approval bytes, then invoke the signed native engine |
| native-recover | Delegate original-operation recovery to the native engine |
| stage | Store immutable snapshot blobs and a complete manifest |
| publish | Validate registry, index, source selection, native transaction and registry contract admission, then atomically move one selector |
| inspect-publication | Reconcile an original publication after a lost response |
| catalog | Read the selected mixed-version Definition catalog with original body bindings |
| read | Read exact material through the selected snapshot |
| impact | Verify a declared consumer universe and compute reverse-dependency closure, rejecting unresolved references |
| assess | Execute qualified independent check code from captured bytes and retain per-spec outcomes |

Commands consume --file REQUEST.json. Signature-bearing operations consume --trust TRUST.json. Persistent commands consume --db DATABASE. Attestation and issuance take --issuer PRINCIPAL --key PRIVATE-KEY.pem. --out FILE writes a new output exclusively.

## Operator trust

Trust configuration supplies these fields.

- principals maps issuers to Ed25519 public keys and explicit predicate, operation, scope and cut grants. Grants may expire. Keys support PEM and native hexadecimal format.
- schemas and selections map IDs to qualified absolute paths and SHA-256 values.
- workspaces optionally maps workspace references to their authority scope.
- carriers binds Definition carriers to descriptor, schema, generator and admission bytes.
- registry_contract supplies the exact Registry/v2 descriptor and signed current admission statement.
- initial_registry pins the predecessor registry for a new snapshot namespace.
- required_readers identifies the declared consumers qualified for the snapshot selector protocol.
- materials qualifies files for impact observation.
- executors qualifies independent code, interpreter and timeout.

An issuance selection declares version, operation, scope, input_schema and an exact set of required predicates. Each requirement names its source schema and JSON-pointer member mappings. The approved selection digest comes from operator trust.

A signed packet contains exact statement bytes as base64 in body, issuer and an Ed25519 hexadecimal signature. Original statements contain version 1, predicate, operation, scope, cut and the original artifact SHA-256 and byte count. Attestation validates the artifact before signing. Issuance retains all original receipt/artifact digests, member paths and its selection digest.

## Native effects and publication

A shared native apply request supplies workspace profile, catalog, selected Project, native store, proposal, approval and a verified construction packet. approval_artifact retains original approval bytes as base64. Construction permission binds those exact bytes. The native engine independently verifies its owner signature and exact proposal, scope and HEAD.

Publication consumes a verified PlanPublication packet, original snapshot files and native store path. The snapshot includes registry, deterministic index, source descriptor, proposal, approval and all native target bodies. The source descriptor includes declared readers, approved exact registry changes and the native transaction digest and target set.

The runtime validates retained registry versions, carrier/schema/generator selections, projections and current lookup. It checks the native target and consequence set against the snapshot. Lifecycle changes require verified PlanLifecycleImpact packets in the signed source descriptor.

Snapshot exposure and the publication receipt commit in one SQLite transaction under the expected selector. A local native commit remains inspectable while canonical publication is pending. Exact retries replay the original receipt. Changed bytes under the same operation conflict. Readers observe a complete snapshot through the selector API.

Design qualification originally required owner dispositions and Registry/v2 admission. Decision 0076 now supplies those decisions and activates the canonical repository workflow. The isolated regression suites continue to use temporary fixture authority.

## Verification

Run these scripts with the pinned Node selected by the central entry point.

    node implementation/lab-runtime/alchlang/shared-records/verify-decisions.mjs
    node implementation/lab-runtime/alchlang/shared-records/verify-integration.mjs
    node implementation/lab-runtime/alchlang/shared-records/verify-publication.mjs
    node implementation/lab-runtime/alchlang/shared-records/verify-registry.mjs
    node implementation/lab-runtime/alchlang/verify.mjs

Decision checks exercise all revision 4 cases against maintained source. Integration checks use actual Ed25519 authentication, schema validation, SQLite restart/replay and independent subprocesses. Publication uses a real native transaction and original Lab Definition material in an isolated namespace. Registry checks validate all 189 retained versions and 183 current identities. Existing native qualification covers creation, signatures, concurrency, interruption, recovery and event replay.


## Request shapes and readers

Attest requests provide artifact (an original file path), schema, predicate, operation, scope and cut. Observe-native requests provide native store, original_operation, schema, consuming operation, scope and cut. Both return an original receipt packet and base64 artifact bytes for the originals array of issue.

Issue requests provide selection_id, operation, scope, cut and originals. Each original has artifact bytes as base64 and its detached receipt packet. Evaluate requests provide operation, scope, cut, artifact bytes as base64 and the sealed receipt packet.

Join initialization uses operation InitializeJoin with an input value containing workspace, run_ref, original_operation and source_cut. Inspect the run to obtain its stable numeric ID. Join transitions use AssessJoinTransition and a stable command identifier. The SQL adapter checks that the ID, operation key, source cut, phase and revision match the actual persisted run before evaluating the AlchLang guards.

Snapshot files use registry.json, index.json and source.json for their protocol roles. The source descriptor declares snapshot-selector/v1 and its qualified reader IDs. The built-in catalog reader is lab.catalog-reader. Define's optional catalog reader is define.catalog-reader. A reader rejects snapshots whose declared universe excludes it.

Define can select a published catalog directly.

    ./define/define discover --work SESSION --snapshot-db DATABASE --workspace WORKSPACE --query EXACT_ID --actor ACTOR

File-catalog discovery remains available through --catalog. The optional Lab connection loads only for a snapshot request. Definition search and preparation decisions remain in Define's existing AlchLang operations.

The public apply request includes original approval bytes in approval_artifact. A read-only construction claim cannot authorize a native effect. Signed Registry/v2 admission is required by the publisher even when a planning input declares the contract current.

## Active repository selection

Decision 0076 accepts the five exact definitions, admits Registry/v2 and activates this shared workflow. The earlier design and qualification records retain their original pending-authority scope; current standing is in authority/definitions/current.json and docs/decisions/0076-shared-definitions-records-activation/.

    node implementation/lab-runtime/lab.mjs shared status
    node implementation/lab-runtime/lab.mjs shared catalog
    node implementation/lab-runtime/lab.mjs catalog --category definition --current

The central workspace catalog now selects implementation/lab-runtime/lab.mjs. The active configuration supplies the workspace, snapshot database, join journal and qualified trust by default. Explicit requests and isolated stores remain supported. Define discover uses the active snapshot when neither --catalog nor --snapshot-db is given.

The canonical selected registry contains 194 versions and 188 current identities. The frozen v1 registry retains 189 versions and 183 current identities for historical native compatibility. New original receipt issuance selections are qualified for the root Lab workspace and the activation source cut. A later workspace, source cut or signer requires an explicit trusted configuration.

## Maintained definitions and records workflow

The current canonical catalog contains 188 current Definition/v2 identities and 377 admitted versions after decision 0077. These numbers describe the migration snapshot, not limits built into the maintained workflow. Current selection is authority/definitions/current.json; original decisions and pinned design selections remain historical inputs. Shared directory verification, view reconciliation and lifecycle orchestration live once under implementation/lab-workflows/records-workflow. Define prepares and verifies candidate packages; shared Lab construction, owner authority, native admission and publication stay outside Define.

The candidate standing annotation retained in sources.json is an original design as-of annotation. Current execution selection and its authorization are authority/profiles/shared-records/current.json; current operational selection is implementation/lab-runtime/shared-workflow.json. Historical selection bytes are preserved rather than relabelled.
