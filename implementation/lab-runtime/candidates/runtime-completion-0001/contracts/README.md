# LC-U01-02 closed contract candidate

This unit implements selection/schema/metadata primitives and a bounded selected
case runner. It supplies no host activation, enrolled actual issuer, protected
read permission, original task acceptance, genuine production graph or timing
qualification. Original API and historical proof files remain unchanged.

`lab_contracts.codec` defines UTF-8 JSON, sorted Unicode scalar keys, compact
separators, exact unnormalized strings, no duplicate fields, no floats/nonfinite
numbers, signed64-bit integers and a64-level bound. Lexical negative zero refuses
in both Python and Rust. A signing record requires its schema-version domain.
Legacy baseline metadata is hashed/read as original bytes; existing floats are
not recoded or passed through the new signing codec.

`closed-contracts.schema.json` exports the same closed definitions used by
`schema_catalog.py` and `dispatch_schema.py`. Every field is explicit; nullable
values are not implicit defaults. Diagnostic/qualification budget combinations,
terminal slots, intervals and finite limits have additional semantic checks.
The first broker frame ceiling is65536bytes; no public API limit is enlarged.

`lab_selectors.anchors` takes an independently supplied root identity and exact
allowed member bindings, rejects traversal/symlinks/FIFOs, checks original bytes
and attachment continuity and checks bounds before calling a protected reader.
Protected reads require an independently selected provider; metadata inventory
never dereferences its member rows. The17 historical tables remain ordered
occurrences, including repeated identities and public/protected classifications.
The real public projection includes API30 source, full profile and schema-execution
tables: 22 tables and 241598 original row occurrences in total.
`public_projection.build(reader, expected_policy_binding)` requires the externally
pinned `public-source-role-policy.json`, reads only its reviewed public metadata
and provenance inputs, retains every ordered row and selector, and materializes
actual document/schema-reference joins. Its policy derives table roles from
selected original schema identities and verifier symbols. Referenced member
bytes, protected-body semantic closure and genuine Artifact-instance relations
remain explicitly unresolved/gated. No kind rotation supplies real-source roles.

`graphs.validate_graph` requires an externally pinned edge policy binding exact
original node/body selectors, roles, edge kinds/endpoints and row provenance.
Semantic dependencies undergo semantic cycle checks. Execution and host-custody
cycles use separately declared policies; evidence backreferences remain
references. No `{path,sha256}` shape automatically becomes an Artifact edge.
Small synthetic graph fixtures exercise cycle/role failures separately from the
real public projection; they do not assert production meanings.

`chains` joins Code→Family→Execution and Core→Review→Activation. Structural
joins do not prove deployed custody. Whole-attempt timing reads the exact budget
selected by the permit and independent expected binding. Late lesson data must
match explicitly selected source/profile schema fragments and policy while the
family's lesson remains unchanged; missing support requires a new family.

## Host dispatch contract

The trusted coordinator first checks exact runner/helper/interpreter/dependency
bytes against independently retained review pins. It supplies
`LAB_DISPATCH_ENDORSEMENT` (an absolute path) and
`LAB_DISPATCH_ENDORSEMENT_SHA256` (its externally retained literal digest), then
invokes the plan's exact `tools/run_case.py` argv. The runner never computes a
digest from the endorsement and accepts it as its own expected value. This is
the same explicit trusted host boundary as the predecessor's guard-v2; it does
not claim hostile same-UID protection.

`-B` disables bytecode writes but still permits loading existing caches. The
coordinator therefore also verifies the selected owned regular-file cache-prefix
sentinel (bytes, type and identity) before Python starts, and supplies its exact
path as `PYTHONPYCACHEPREFIX` for the runner and every selected Python test
command. Guarded launches also use `-S` and a sanitized explicit environment,
excluding ambient site/.pth, PYTHONPATH and user startup injection. The selected
entrypoints insert the audited installation0004 dependency path themselves.
The installed interpreter/standard library remains the stated host trust base. A regular-file ancestor cannot contain cache descendants. Selected
commands must not use `-E` or `-I`, which ignore that environment input. The owned
cache-policy probe demonstrates stale timestamp-cache execution without this
prefix and exact source execution with it on the selected interpreter. Existing
cache trees remain untouched; this is a reviewed host-launch boundary, not a
claim of resistance to a hostile process with the same UID.

The closed `DispatchEndorsement` binds baseline/acceptance, roots, original plan,
selection and optional final freeze, entire reviewed source closure, case
manifest, exact executable/script/argv/environment, bounded commands, exact
write envelope, provider enrollment and gate inputs. Source→endorsement→receipt
is acyclic. The case manifest contains only command IDs plus exact case/step
gate/effect declarations. Unit gates are a minimum; every nested command adds
its actual gates/envelope. Understatement or unselected effects refuse.

Inert/fixture stages use only independently reviewed local authoring commands.
They cannot carry actual gates/effects. Pipes bound the total retained stdout
and stderr; deadline/output limit kills and reaps the owned process group.
Timeout, source drift or unknown outcome fences all later positive commands;
only separately selected cleanup runs. Every attempt is exclusive and records
the command, before/after source bindings, each command's terminal, cleanup and
aggregate. FAIL/ERROR/NOT_RUN/UNKNOWN never becomes a positive aggregate.

Actual stages additionally require an independently reviewed `provider_binding`,
`provider_command_id` and `issuer_enrollment_binding`. The provider command is a
bounded **coordinator-side** adapter process, never an arbitrary Python import
or executable inside the privileged broker. No such actual adapter is shipped
here. The adapter receives the closed
`lab-actual-authority-provider-request/v1` envelope on stdin (request, command,
issuer enrollment and provider bindings). It verifies genuine current issuer
proof and exact phase permission, rechecks at every effect, executes only
through the fixed broker/selected supervision boundary, and emits exactly
`lab-actual-authority-provider-result/v1` with `gate_verification` and
`command_result` and `effect_evidence`. A boolean gate claim or self-enrolled fixture key is not an
actual provider. The caller separately reviews/enrolls the adapter before it can
be selected. The parent bounds stdin, aggregate output and elapsed time; no
arbitrary raw adapter output is persisted. Only validated closed public receipt metadata is retained as exact original bytes. Nonzero/malformed/timeout means UNKNOWN after
transport launch, even when the child has been reaped. Store/effect cleanup and
reconciliation remain actual receipt obligations. Transport dispatch count is
distinct from observed effects.

Every actual selected command explicitly binds an `EffectEvidenceContract` with
reviewed public receipt roles, locators, allowed public subject locators, finite
count/byte limits and exact-original-byte retention. Required provider-produced
public receipts cover gate verification, currentness, prestate, poststate,
effect and cleanup; each declared output receipt is also required. The runner
checks closed schemas, original-byte hashes, all request/selection/command and
enrollment joins, known outcomes and disclosure scope before writing the exact
UTF-8 originals into exclusive fsynced attempt files. Valid closed and scoped
negative receipts are retained too and force FAIL/UNKNOWN; malformed, private
or unbound bytes are never exported. After transport launch, unverified scope
keeps the effect state unknown. Only fully scoped evidence can preserve a known
effect state if subsequent durable storage fails. The command record keeps
both provider-original and retained bindings. It does not dereference arbitrary
provider-original locators or claim they are independently retained there.

The independently reviewed and enrolled provider MUST verify and retain the
underlying native original grant/proof/output/state records in their permitted
custody. Public subject bindings are only explicitly authorized exact references;
wrapper counts and digests cannot qualify native gates. Public receipt schemas
and slot subject locators must themselves receive disclosure review. No private
body or unreviewed private locator/digest may be exported through this interface.
This unit tests receipt plumbing with isolated fixtures; no actual provider,
native proof qualification or protected access is supplied here.

Admission proofs enumerate start inputs, current before-effect checks and
consumed predecessor outputs. They cannot include this unit's future terminal
outputs. Selected commands declare `produced_terminal_checks`; their exact
union must cover the unit and nested-command terminal obligations once. Setup
and cleanup commands need not produce another command's future output. The
runner accumulates their retained terminal receipt bindings and requires full
coverage before aggregate PASS. Every nested command also has closed phase
`gate_checks`; conflicting or understated case/unit phase declarations refuse.
Positive command results require nonzero checks and known effect/cleanup states.
Cleanup aggregation preserves unknown, then retained-owned, then clean. A first
failure retains its command reference; later finalization/cleanup failures are
secondary and do not erase it.

The original plan's semantic-review/authority-review units may use code selection
with actual review inputs only when the independently pinned original unit has
that verification kind. Their effects are restricted to protected reads and
owned evidence authoring. They still require an enrolled selected provider and
complete gate/receipt checks; baseline bytes do not activate a runtime family,
namespace, candidate producer or governed effect.

Provider ownership is bounded by the accepted plan: LC-U02-04 authors the
namespace qualification adapter within `deployment/verify-host.py` (and its
owned tests), before that unit's actual G01 transaction. Its selected input is
proposed NamespaceCore; Activation is a produced terminal, never admission.
LC-U06-01 authors the provisioner phase adapter under `provisioner/`, initially
as inert code; LC-U07-02 consumes it only after LC-U06-02, which depends on
LC-U06-01. LC-U04-02 follows LC-U07-02, so the first protected diagnostic does
not precede its adapter. U10 semantic/authority review adapters belong to each
unit's exact owned test scope; real decision makers, issuers and access remain
external prerequisites. These are implementation ownership mappings, not
completed providers or expanded write authority.

Downstream units add independently reviewed versioned endorsements; no unit
rewrites this baseline or silently changes a final selection. Final dispatch
requires the exact freeze→ExecutionSelection binding. Changed family/code inputs
retain prior selections and require the original invalidation/requalification.

## Verification

The direct tests are the bootstrap oracle; the new runner cannot establish its
own acceptance. `test_contracts.py` requires an actually built Rust executable
through `LAB_CODEC_RUST_BINARY`; missing Rust is a failure, not a skipped PASS.
The Rust fixture signs the exact canonical bytes with a deterministic fixture
key solely for cross-language tests. It grants no actual authority. Cargo is
pinned by Cargo.lock, built offline, and writes target files only under unit E.
`test_graph_inventory.py` checks the full original public metadata without
reading protected members. `test_runner.py` exercises bounded real child
processes, failure fencing and dispatch substitution/refusal.
`test_public_projection.py` checks the real 241598-occurrence projection and
original selectors; `test_effect_evidence.py` tests durable exact public receipt
retention, negative evidence, phase separation and uncertainty preservation.
