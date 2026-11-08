# Native Lab source audit and model boundary

Audited 2026-11-05 against the exact files in `native-source.json`. The selected
executable is the local **Lab operational runtime v2 candidate**, with the
specialist-owner-bootstrap-0003 Project State and both history cursors at **7**.
Qualification reads the actual baseline and observes cursors at 8 after one
local transaction; it does not infer this from a directory name or old receipt.

The v2 README describes this selected successor. Some older paragraphs in
`v2/CONTRACT.md` still describe the earlier D75 cursor at 5; the model and fixture
use the actual selected source and native replay. No native documentation was
edited during this modeling task.

| Native source/function | Modeled responsibility | Original owner retained |
| --- | --- | --- |
| `sources.py:capture`, `freshness`; `store.py:roots`, `replay` | SourceEnvelope, Branch, SourcesCurrent, SelectContext | Capture, schema/material hashing, exact profile equality, full signature/history replay |
| `store.py:initialize` | Explicit provisioned Branch contract; actual initialization in the native fixture port | Provision public key and local trust boundary; publish genesis atomically; refuse an existing store |
| `operations.py:prepare` | ReviewEligibility, ApplyEligibility, permitted target effects and exact source/scope/HEAD checks | Closed protocol, whole proposed type/relation closure, immutable revisions and Decision identity validation |
| `store.py:review` | ReviewProposal returns an inert review plan | Build exact native Decision cores and consequence plan |
| `store.py:authorize`, `approval_core`, `verify_approval` | AcknowledgeApproval from NativeChecks and raw-byte approval binding | Private-key custody, exact core/header agreement and Ed25519 signatures |
| `store.py:apply` | PrepareDispatch, recoverable LocalAdmission Workflow and native outcome observation | Exclusive writer, pending/transaction staging, second source check and atomic HEAD visibility point |
| `operations.py:consequences`; `governance.py:records` | NativeResult binds receipt, transaction and both observed cursors | Generate schema-backed semantic/governance consequences and exact receipt; prevent circular hash dependencies |
| `store.py:recover` | RecoveryContinuation and native fixture recovery exercise | Inspect frozen committed chain and exact HEAD; validate pending/next-sequence files; remove only recognized leftovers |
| `sources.py:resolve` | ResolveSubject preserves exact version vs current identity behavior | Original catalog reconstruction and native subject facets |
| `graph.py:query` | TraversalBounded, PlanTraversal, stale-path suppression | Direction-preserving BFS, edge evidence, unresolved references and coverage diagnostics |
| `session.py:Session` | SessionView, SessionLifecycle, ContextAccess, open/use/note/close/expiry Operations | Reconstruct schema-backed context records, hold ephemeral state and actually close/erase on expiry |

## Observed commit/recovery contract

`Store.apply` first replays current exact sources. It recognizes an exact
committed proposal/approval pair **before** checking a fresh proposal's expected
HEAD or leftovers. ApplyEligibility preserves that order: exact replay remains
possible after HEAD advances, while conflicting reuse of a proposal ID is refused.

The visibility point is the atomic replacement of `HEAD.json`. A process exit
before that point leaves staged files and an unchanged committed chain. A process
exit after it can leave pending cleanup even though the transaction committed.
The fixture port never translates either process failure into inferred rollback.
It inspects the original chain; the workflow does not redispatch an uncertain
operation. After exact native recovery proves no commitment, continuation returns
to review/fresh permission. A committed result preserves its receipt.

`NativeOutcomeObserved` and its audit inbox are derivative model records. They
cannot act as a replay source for the original native store or as new owner
permission. Generic fixture Auth acceptance of the modeled API does not replace
an original native owner signature.

## Qualification evidence versus product journeys

The qualification prepares a Work and the actual User Journey candidate, obtains
one real native local owner signature, and observes the native transaction in a
fresh disposable store. It does not mutate the repository's User Journey standing
or mark any of the six product journeys observed end to end.

The fixed current native profile still governs the migration Project. There is
no independent Project bootstrap, membership issuer or general delegation adapter
in this model package. Those are explicit future product joins, not omitted
fields to fill with test identities.

## Creation handling

`ports/creation.py` calls the original `common.identity` using the carrier's
`artifact.instance_contract.identity_field` where present, then the native
fallback resolver. Frozen registry carriers do not all have a top-level
`identity_field`; this path does not invent one.

It uses original `current_contract`, `validate_record` and `operations.prepare`
for the body and whole unsigned proposal. Definition/v2 schema/self-binding,
new-identity checks and explicit project/Work draft scope are retained in the
creation observations. All input bodies remain unchanged. `CreateDefinition`
and `CreateRecord` own the corresponding modeled creation Policies; the
`PrepareCreation` use case constructs typed unsigned proposal metadata.

The new draft command writes only the explicitly selected candidate directory.
Its integrity receipt is not an owner signature, source admission or replay
source. The fixture tests compare compiled model output with native validation,
then pass created targets through the original signed native transaction path.

## Artifact Type registration and inline schemas

`CreateArtifactType` follows the same module/use-case organization. The draft
command validates the native v3 descriptor slot, its declared Definition
references, closed contract and native JSON schema digest using the unchanged
native runtime. The public command retains all three original inputs and emits
an unsigned proposal with the inline schema document.

`CreateRecord` uses `current_contract` and reconstructs schema material from the
verified native transaction chain before considering a frozen repository schema.
Registered schema documents carry `native-json-sha256` and the registration
transaction digest, not a fabricated original-file binding. The original schema
file need not survive on the drafting host. Record identity and discriminator
come from the current registered contract. Native validation and admission still
recheck the complete closure; modeled boolean observations grant no authority.

Qualification exercises public Artifact Type and record commands in separate
processes, exact-byte tampering, registration refusals, owner-signed type/record
admissions, custom identity resolution, committed replay and withdrawal refusal.
The original 19 selected native sources and source profile remain unchanged.
