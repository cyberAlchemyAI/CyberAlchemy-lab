"""Render a candidate completion plan; does not import or execute the Lab."""
from pathlib import Path
import json
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
API = 'product/lab/release-candidates/v1/interface/api-integration-v16/'
RUN = 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/'
OLD = 'docs/plans/0010-lab-one-shot-execution/'
TASKS = []

def task(ident, title, layer, deps, owner, sources, modules, inputs, rules, acceptance, failures, check, original, conditions):
    TASKS.append(dict(id=ident, title=title, layer=layer, depends_on=deps.split(), owner=owner,
        source_anchors=sources, prospective_modules=modules, inputs=inputs, ordered_rules=rules,
        acceptance_evidence=acceptance, failure_modes=failures, reviewable_check=check,
        original_tasks=original.split(), acceptance_conditions=conditions.split(),
        status='not-started', authority_effect='none',
        contract_path=f'work-pack/tasks/{ident}.md', swu_ids=[f'SWU-{ident}-01']))

task('T00','Select and lock the successor execution baseline','L0','','coordinator',
 [API+'source-manifest.json', API+'contract-profile.json', OLD+'dag.json'], ['successor-selection.json','run ledger'],
 ['SOURCE-BASELINE.json','all three implementation audits','current dirty-state and live-job inspection'],
 ['Recheck source/profile digests and original task/SWU inventories; record changed inputs explicitly.',
  'Reserve an unused successor directory and private scratch run root; never edit API16 or v1/v2.',
  'Resolve every symbolic write scope to exact paths before dispatch; assign one merge coordinator and one freeze writer.',
  'Record Python, SQLite, Rust/native executable/platform versions, available resource budget and scoped execution authority.'],
 ['Exact source/profile/base cut selection','private cleanup ownership and rollback retention','disjoint worker scopes and merge order'],
 ['Unrelated concurrent mutation','predecessor overwrite','test authorization absent','source selection changes'],
 'Review digest/identity inventory and source diff; proceed only for the exact selected candidate and authorized effects.', 'B00 B01 C01 C04','AC13')

task('T01','Capture the exact causal Machine read refusal','L0','T00','Machine diagnostician',
 [API+'test_machine_transport.py', API+'machine_transport.py', RUN+'common-all34-0275/units/member--Source8-lifecycle.json'],
 ['successor diagnostics','new owned diagnostic receipts'],
 ['Actual Machine context.get failure','Source8 phase timings','selected transport and parent Session'],
 ['Capture operation name, redacted raw reply, strictest deadline, source/profile/cut and branch identity for the failed call.',
  'Instrument selected phases with a monotonic duration and actual UTC time; correlate CPU, hashing, native replay, schema validation and caller work.',
  'Keep production clocks, proof callbacks, expiry and original negative cases intact; compare serial versus admitted parallel load in owned scratch.',
  'Classify the primary refusal separately from subsequent caller exceptions; retain failed receipts.'],
 ['Causally bound raw Machine refusal','phase-by-phase Source8 latency ledger','root-cause disposition or explicit unresolved hypothesis'],
 ['Tracing leaks credential/proof secrets','instrumentation changes semantics','different-run reply mistaken for worker9 evidence'],
 'Focused reproduction of MachineTransport.test_02 and one real Source8 lifetime with raw reply/time/guard bindings; no inferred PASS.', 'R03 R07 W06','AC01 AC04 AC09')

task('T02','Correct successor fixture identity and constructor selection','L0','T00','fixture maintainer',
 [API+'test_custody_sessions.py', API+'run_session_checks.py', API+'test_termination_boundaries.py', API+'service.py'],
 ['successor test_custody_sessions.py','successor run_session_checks.py','successor test_termination_boundaries.py','successor fixture/AST map','new independently signed current Source8-equivalent reader/Context/Lesson/applicability family'],
 ['Original timestamp refusal','original constructor-origin refusal','selected distinct legacy fixture'],
 ['Bind each test to the actual source identity, selected runtime and independent period.',
  'Create a separately authorized and signed current successor source branch, native reader/mapper/Context/runtime route and Lesson/applicability family with new identities and exact scopes; keep expired original Source8/legacy records unchanged as negative evidence.',
  'Use the original declared lease duration/budget rules for the current family, with actual UTC and no backdating, larger artificial window or silent renewal of an old grant.',
  'Route both metadata resurrection test variants through the selected legacy constructor; retain the original custody adapter-origin refusal as a separate negative case.',
  'Update only explicitly documented fixture selection/assertion bindings; retain historical AST/source comparison and all original negative semantics.'],
 ['Previously failing fixture cases pass for their intended source','old source period stays unchanged','wrong class/module still refused'],
 ['Renewing old grant','loosening class guard','changing expected refusal into success','dropping inherited tests'],
 'Run the two affected whole fixture classes in isolated scratch and inspect declared fixture/AST changes.', 'R03 R07','AC01 AC04')

task('T03','Make the real Session learning sequence fit its lease','L0','T01 T02','runtime performance maintainer',
 [API+'service.py', API+'guarded_candidate.py', API+'lesson_selection.py', API+'machine_auth_scope.py'],
 ['successor scoped proof/replay/schema execution modules'],
 ['Measured T01 bottlenecks','unchanged original full history verifier','actual Source8 Context and lease'],
 ['Remove only measured redundant pure work inside a single exact guarded invocation.',
  'Scope reuse to immutable captured facts; recheck current source, policy, nonce, schema, credentials, cut and real deadline at every required boundary.',
  'Do not persist trust caches, restore Session RAM, renew an old permission period or replace full history verification.',
  'Set an observed timing margin from the remaining real lease; fail before effects when the budget cannot fit.',
  'Measure complete context/open/select/apply/assess/inspect/close under realistic declared load.'],
 ['Complete real current Source8-equivalent successor sequence inside its independently authorized live lease using preserved duration/budget rules','unchanged original expired-source and corruption/revocation refusals','phase timings and load configuration'],
 ['Unsafe cache survives mutation','deadline bypass','parallel load consumes lease','partial lesson result mislabeled complete'],
 'Real Source8 single-process lifetime plus causal mutation/expiry probes on the exact successor; report duration and remaining lease.', 'C03 C06 C08 W06 W07 R03 R07','AC01 AC04 AC09')

task('T04','Handle transport refusal and uncertainty in callers','L0','T00','caller maintainer',
 [RUN+'common-all34-0277/caller.py', API+'service.py', API+'application_journal.py'],
 ['successor common caller','operator/Paperclip caller adapter'],
 ['Transport error envelope','domain result/error contracts','effect_may_have_started/recovery_policy fields'],
 ['Branch on envelope kind before indexing message/domain data.',
  'Record refused/no-effect, pending/uncertain and completed states independently.',
  'Honor no-retry; when effects may have started inspect the exact owned operation and reconcile before any further action.',
  'Return bounded actionable diagnostics and retain ownership-scoped cleanup without disposing another Session owner.'],
 ['Expired lesson.select produces a recorded transport failure without KeyError','uncertain effect never blindly redispatched','stable caller error contract'],
 ['Exception hides primary refusal','retry duplicates effect','cleanup removes foreign/private evidence'],
 'Feed actual expired/refused and uncertain operation receipts through the caller; inspect journal count and retained failure evidence.', 'R03 R07','AC01 AC05')

task('T05','Repair the diagnosed Machine read path','L0','T01 T02','Machine transport maintainer',
 [API+'machine_transport.py', API+'session_attachment.py', API+'test_machine_transport.py', API+'legacy_context_sessions.py', 'product/lab/release-candidates/v1/interface/machine-context-scope-v1/generation.py'],
 ['successor Machine/borrowed guard modules only as causally required','new versioned exact runtime-class generation selector and binding when diagnosed'],
 ['T01 raw reply and causally established refusal','parent Session currentness','seven public read contracts'],
 ['Locate the exact failing guard and its selected producer/caller bindings.',
  'Apply the smallest causal correction in a successor; if intended refusal is correct, repair only the declared fixture/source binding.',
  'Inspect legacy_context_sessions.view_get -> machine-context-scope-v1.generation.selected exact legacy-versus-custody class mismatch. If causal, select a separately versioned origin-specific helper with explicit trusted class/module bindings; preserve original helper and wrong-origin refusal, never accept arbitrary classes.',
  'Preserve raw-byte signature, nonce replay, live policy revocation, independent Actor membership, parent ownership and original expiry.',
  'Capture before/after replies and post-call resource state.'],
 ['All seven Machine reads pass on a genuinely live permitted parent','negative transport/security cases remain refused','source and fixture changes explicitly classified'],
 ['Assuming expiry without evidence','bypassing integrity guard','borrowing becomes authority','peer close disposes parent'],
 'Run complete MachineTransport class and selected parent/borrower lifecycle tests after T01 diagnosis.', 'R03 R07','AC01 AC04')

task('T06','Provide a maintained composite operator entrypoint','L1','T00','integration maintainer',
 [API+'serve.py', API+'integration_dispatch.py', API+'integration-members.json'],
 ['successor composite stdio launcher','versioned operator configuration contract'],
 ['Base28 and Action3/Governance3 services','same Schemas instance','independent branch channels and grants'],
 ['Define explicit source/profile/policy/public key/workspace/dependency inputs and validate before startup.',
  'Construct all three actual branches using their independent authenticated policies and shared exact schema instance.',
  'Route unchanged received bytes through IntegrationService, including branch-owned operation.inspect.',
  'Keep public catalog visibility distinct from available permission; refuse unavailable configured branches honestly.',
  'Keep stdio request handling serialized per channel, including nonce/call-ID/budget consumption. Specify bounded framing, EOF/partial-frame/error behavior and deterministic owned-resource shutdown; no concurrent dispatch is introduced by this launcher.',
  'Close only owned resources on exit; startup cannot imply canonical admission or network service activation.'],
 ['One documented executable selects the full34 composition','all branches receive actual raw bytes','missing branch credentials fail closed before effects'],
 ['Base-only launcher advertised as full34','shared identity widens permissions','secret printed or persisted publicly'],
 'Launch the maintained entrypoint in a fresh isolated process and inspect catalog, branch identity, auth failures and clean shutdown.', 'R03 C11 W02','AC01 AC04')

task('T07','Package native and host dependencies reproducibly','L1','T00','packaging maintainer',
 ['implementation/lab-context/candidates/v1/native_reader.py', API+'source_bridge.py', API+'r02_installer.py'],
 ['successor environment/dependency manifest','owned installer staging'],
 ['Exact native executable ABI/build identity','Python/SQLite modules','full public/protected provenance rows'],
 ['Classify execution dependencies, immutable provenance, public install bytes and protected host-only inputs explicitly.',
  'Record supported OS/architecture/runtime/ABI and independently expected digests; define fail-closed discovery/preflight.',
  'Replace disposable /tmp assumptions with explicit owned provisioning instructions or durable protected external selections.',
  'Preserve all full proof rows while selecting bounded execution closure; never ship keys, grant secrets or live databases.',
  'Keep previous generations and rollback until verified replacement operation.'],
 ['Fresh environment can resolve every declared dependency','unsupported/missing ABI fails before execution','public/private bundle membership and provenance accounted'],
 ['Flattening protected proof into public artifact','host path quietly replaced','missing dynamic library','unreviewed background service'],
 'Reproduce install/start in an empty owned local environment with exact pins and separately provisioned protected inputs.', 'R02 R03 R06 R07','AC02 AC11 AC13')

task('T08','Separate artifact graphs from proof and host bindings','L1','T00','release graph maintainer',
 [API+'release_readiness.py', API+'installation_release.py', API+'workspace.py'],
 ['successor typed graph traversal','successor versioned protected proof reader/control schema'],
 ['Artifact schema-declared dependency roles','full source/profile proof tables','protected host input selections'],
 ['Define closed versioned binding kinds for semantic Artifact dependencies, evidence/provenance, public package bytes and protected host dependencies.',
  'Traverse only schema-declared semantic dependency edges; separately verify all exact proof rows without treating proof files as admitted Artifacts.',
  'Read protected inputs through independently selected host custody, ownership, no-follow path and digest checks; expose only bounded public evidence.',
  'Enforce existing frame/Vault limits; process the large proof table through its selected reader rather than raising limits or truncating rows.',
  'Reject unknown binding kinds, missing original rows, cycles, substituted bytes and public/private boundary violations.'],
 ['Complete approximately27MB proof closure verifies without artificial Artifact graph edges','typed semantic graph closes exactly','protected bytes remain protected'],
 ['Every path/hash treated as Artifact','dropped full provenance','generic bypass reader','private proof leaks through privacy scanner'],
 'Review schema selectors then exercise exact proof closure, a true semantic cycle, protected substitution and private-path refusal.', 'S02 R02 R06 R07','AC02 AC10 AC13')

task('T09','Define composite installation environment compatibility','L1','T00','installation maintainer',
 [API+'installation_release.py', API+'r02_installer.py'],
 ['successor installation environment adapter/schema'],
 ['Composite supported environment descriptor','R02 package environment descriptor','exact native/runtime dependencies'],
 ['Introduce an explicitly versioned selection of the R02 environment subdocument from the composite contract.',
  'Compare the selected exact subdocument and independently check remaining composite host/native requirements.',
  'Do not equate incompatible shapes, ignore unknown requirements, or silently alter the old environment contract.',
  'Carry environment selection into installation receipt and upgrade/rollback preconditions.'],
 ['Real final composite environment installs against matching R02 selection','incompatible ABI/runtime/unknown fields refused','old fixture semantics retained'],
 ['Whole-document shape mismatch','partial match hides unsupported host','rollback selects different environment'],
 'Focused real installation/upgrade/rollback cases using composite descriptor plus causal environment mismatch.', 'R02 R07 S02','AC11 AC13')

task('T10','Ground each selected model representation','L1','T00','semantic representation author',
 ['product/lab/release-candidates/v1/release-validation/0001/S02-package-specific-gaps-0276.md', 'authority/artifact-types/governed-model/v1/schema.json'],
 ['new package-specific candidate model postimages and disposition ledger'],
 ['29 refused GovernedModel proposals','original mapping members','declared directional relationship roles'],
 ['For every refused model, identify an independently supported relation with exact endpoint, direction, kind and original evidence.',
  'If no relation exists, record a supported alternate carrier or explicit unresolved design decision; do not create an arbitrary predecessor or Decision.',
  'Keep original descriptor semantics and bytes attributable; validate selected representation and dependency closure.',
  'Require accountable disposition for a meaning-changing alternative before its use.'],
 ['All29 original members individually dispositioned','each selected representation valid and semantically grounded','no invented meaning'],
 ['Schema-valid arbitrary relation','wrong direction/counterpart','silent removal of a member'],
 'Independent per-member relationship/carrier review against original descriptor and native schema; preserve actual refusal counterevidence.', 'C02 C10 C14 O01 O06 S02','AC02 AC03 AC10 AC13')

task('T11','Resolve original producer and consumer scopes','L1','T00','scope integration author',
 ['product/lab/release-candidates/v1/release-validation/0001/S02-package-specific-gaps-0276.md', 'product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/operations.py'],
 ['new scope/consumer routing selection','new independently authorized correction routes if required'],
 ['230 original domain-scoped bodies','original O.prepare rules','Project/Source8 granted scope'],
 ['Map each body to its original producer, intended consumer, exact domain scope and eligible authorization.',
  'Preserve body bytes; select the existing compatible route or a separately represented reviewed correction.',
  'Keep Project grant boundaries; refuse domains without current authority rather than widening the grant.',
  'Verify current cut/preimage, carrier schema and independently grounded domain scope before any claim.'],
 ['All230 original bodies accounted','each selected route succeeds under its exact granted scope','wrong-domain negative refused before mutation'],
 ['Project grant silently covers all domains','rewritten body scope changes meaning','scoped correction presumed authorized'],
 'Per-body routing matrix and causal native prepare/consumer checks on authorized isolated copies.', 'C02 C10 W08 O05 O06 S02','AC02 AC03 AC10 AC13')

task('T12','Resolve current governing owner prerequisites','L2','T00','actual accountable owners',
 [OLD+'work-pack/tasks/R08.md', 'product/lab/release-candidates/v1/release-validation/0001/S02-package-specific-gaps-0276.md'],
 ['candidate owner-effect matrix','actual authority records only through their authorized owner route'],
 ['Current authoritative base State and history','four required owner roles','actual principals and assignments'],
 ['Resolve repository, definition, artifact-type and identity-graph owners against actual governing Role/RoleAssignment records, interval and scope.',
  'If the selected candidate base has no assignments, locate a valid admitted authority source or expose a separate prerequisite owner route; candidate role drafts confer no authority.',
  'Record authentic operator versus accountable owner identities separately.',
  'Do not fabricate responses or create role authority from a principal name or custody signature.'],
 ['Every exact member/effect has a currently eligible accountable owner','authority source/history and assignment interval independently verified','unresolved bootstrap prerequisite explicitly blocked'],
 ['Principal name treated as RoleAssignment','candidate roles treated as governing','expired assignment','owner response invented'],
 'Manual/current-state owner-role verification; only the actual owner can supply or approve missing prerequisite authority.', 'R08 S02','AC13')

task('T13','Resolve native event targets and owner-response closure','L1','T10 T11','ontology materializer maintainer',
 [OLD+'work-pack/tasks/S02.md', 'product/lab/release-candidates/v1/release-validation/0001/S02-package-specific-gaps-0276.md'],
 ['new native event materializer selection','candidate pre-decision cores/target templates'],
 ['88 original O06 event intents','native predecessor tuples and event rules','actual owner-provenance requirements'],
 ['Materialize exact semantic target/effect bytes and independently stable unsigned cores from original native event tuples.',
  'Prove a deterministic post-response envelope/provenance binding only if the original schema permits keeping unknown owner response outside the fixed target core.',
  'If actual Decision bytes participate in the semantic target digest, stop the single-checkpoint closure and propose an explicit representation/design correction for accountable review.',
  'Keep actual decision/outcome absent until R08; append final events only after exact positive authority exists.',
  'Check all88 event targets plus semantic/governance predecessor alignment and full original intent accounting.'],
 ['All88 targets individually materialized or explicitly blocked','no fabricated owner core/Decision','formal disposition of unknown response/digest dependency'],
 ['Intent wrapped as Artifact admission','circular event/Decision digest','post-approval target changes','single-checkpoint promise hides extra review'],
 'Compare original native event schema/materializer and acceptance against pre-decision core and post-response envelope; formal causal/digest review.', 'O06 S02','AC03 AC05 AC10 AC13')

task('T14','Implement and rehearse the mixed-target publisher contract','L1','T08 T09','publisher maintainer',
 [OLD+'work-pack/tasks/S02.md', OLD+'work-pack/tasks/A01.md'],
 ['successor publisher/typed target adapters','new owned crash/recovery rehearsal'],
 ['Original Artifact/native event/registry/State carrier schemas and valid selected technical examples','original publisher and recovery rules','preimages and owner/effect matrix draft'],
 ['Prepare all targets, original-byte postimages and independently stable cores before any commit.',
  'Validate exact preimages, native history and scope under an exclusive owned lock; stage and fsync before commit point.',
  'Preserve foreign files and unknown residue; commit once or report uncertain state.',
  'Recover from each recognized interruption by cold verification without duplicate semantic/governance events or index drift.',
  'Use scratch signatures only as technical test credentials; actual owner outcomes remain separate.',
  'Freeze only executable/adapter code closure here;29/230/88 package target dispositions and D01 gate final T25, not technical T15 qualification.'],
 ['Heterogeneous target adapters support the actual selected member families','atomic failure/recovery invariants','realistic full-package rehearsal contract ready for T25'],
 ['Three small fixture cases generalized to363 members','partial publication','competing preimage overwritten','uncertainty triggers duplicate effect'],
 'Owned heterogeneous rehearsal with boundary crashes and cold replay; final exact package instance proof is additionally required at T25.', 'C07 S02 A01','AC05 AC10 AC13')

task('T15','Freeze the corrected execution candidate and fixtures','L1','T02 T03 T04 T05 T06 T07 T08 T09 T14','single freeze coordinator',
 [API+'guard.py', RUN+'final-api-regression-map-0270.py', RUN+'API16-freeze-inputs-0272.json'],
 ['new successor source/profile/schema/input manifests','new method accounting and selected evidence driver plans'],
 ['Merged corrected code','complete original input rows and schema closure','separately selected unsigned package target inputs'],
 ['Merge disjoint task postimages through one writer; preserve every declared predecessor row and classify every new/changed row.',
  'Freeze independently supplied source/profile/runtime/schema/native/fixture digests and exact current method inventory.',
  'Select separate execution closure, package target core and later evidence/owner envelope identities; prohibit self-referential digest binding.',
  'Bind new worker and all34 plans to the exact frozen successor; later byte changes invalidate affected qualification and require a new freeze.'],
 ['Independently checked frozen input manifests','original323 and current345 inherited methods retained plus deliberate new cases','no qualification transferred from API14/16'],
 ['Freeze during active writer','new code checked against old hashes','private fixture byte publication','self-referential evidence core'],
 'Independent hash/source/AST/schema closure verification before any qualifying worker starts.', 'C01 C04 C09 R07 S02','AC01 AC02 AC13')

task('T16','Qualify the complete regression inventory','L2','T15','qualification coordinator',
 [RUN+'final-api-regression-0270.py', RUN+'final-api-regression-map-0270.py'],
 ['new run regression worker/terminal/aggregate evidence only'],
 ['Exact frozen T15 method plan','original323/current345 methods and selected new cases','isolated class buckets'],
 ['Run exact whole-class buckets with original clocks/callbacks and current actual SOURCE/PROFILE injected only at declared fixture inputs.',
  'Serialize source-corrupting/exclusive classes; limit parallelism by measured lease/resource budget.',
  'Verify entry/exit full-history guards, worker identities, every declared case and terminal event with no skips or duplicated methods.',
  'Aggregate only complete bound reports; preserve failure as failure and fix through a newly frozen successor if code changes.'],
 ['Full exact regression aggregate PASS','every original and added method accounted','all source guards and terminal bindings verified'],
 ['342/345 called qualified','missing aggregate','SKIP/expected failure counted PASS','mixed source families'],
 'Existing final-api-regression-0270.py worker/aggregate CLI, with newly generated successor plan and independently supplied digests/output prefix.', 'C09 W07 R07','AC01 AC04 AC11')

task('T17','Qualify all34 operations through the maintained composition','L2','T15','API qualification maintainer',
 [RUN+'common-all34-0277/caller.py', RUN+'common-all34-selection-0278/selection-plan.json', API+'integration_dispatch.py'],
 ['new all34 caller unit, terminal and aggregate evidence'],
 ['Exact final composite entrypoint','all34 contract/Actor/schema profiles','real single-process Source8 resource'],
 ['Use the maintained composite constructor/launcher rather than a divergent test-only assembly.',
  'For all34 operations collect actual positive semantics, schema-valid causal Actor/Agent refusal and unchanged owned effect state where refusal requires it.',
  'Complete all seven Session/lesson operations in the same real permitted lifetime, without restoring RAM or replacing expiry.',
  'Treat a correctly blocked release.prepare as conformance only; actual release readiness remains T25/T30.',
  'Verify raw message bytes, branch ownership, exact source/profile/cut and complete positive/negative accounting before aggregate PASS.'],
 ['All34 same-family positive/negative aggregate PASS','complete seven-operation lifetime','no missing unit, substituted source or domain-status shortcut'],
 ['27/34 partial proof transferred','base28 mistaken for34','blocked release result considered release approval','causal negative invalid schema'],
 'Fresh versioned common-all34 unit/collector plans derived from current caller and binding all34 contracts, including complete Source8 lifetime.', 'R03 R07 W07','AC01 AC04 AC09')

task('T18','Close transport/security and recovery boundary qualification','L2','T15','security/lifecycle reviewer',
 [API+'test_machine_transport.py', API+'test_termination_boundaries.py', API+'workspace.py'],
 ['new exact security/recovery evidence selection and aggregate'],
 ['Actual signed channel/session/Actor resources','immutable raw request bytes','pending/completed private journals'],
 ['For Base Reader, Action, Governance and Machine separately collect causally bound wrong signature, connection nonce replay, live revocation, expiry, foreign owner, profile/code/schema/source substitution, actual Actor mismatch and malformed frame outcomes.',
  'Refuse cross-branch proof/context/signature reuse and context-ref collisions; bind each observed refusal to the branch identity and exact unchanged effect state.',
  'Verify close/revoke/expire clears live RAM/credentials while durable metadata cannot reconstruct the resource.',
  'Interrupt an actual owned effect and inspect/reconcile its pending key; ensure no duplicate dispatch and preserved foreign bytes.',
  'Do not claim a static audit or merely missing signer is a signature/revocation test.'],
 ['Same-family Base/Action/Governance/Machine security matrix and aggregate with actual causal mutations','cross-branch proof refusal','journal and parent/borrower ownership invariants','recovery outcomes tied to real effects'],
 ['Negative causality not established','real-time expiry hidden','global mutable nonce fixture','blind pending retry'],
 'Selected current Machine/auth/session/owned-journal crash cases and their actual terminal aggregate, not historical source8-machine-auth-0276 absence.', 'W02 W07 R03 R07','AC01 AC04 AC05')

task('T19','Verify the corrected candidate in a fresh installation','L2','T15','installation qualifier',
 [API+'test_installation_release.py', API+'r02_installer.py', OLD+'work-pack/tasks/R02.md'],
 ['new owned installation/replay/upgrade/rollback observations'],
 ['Frozen successor package','explicit composite environment/protected host inputs','independent package/scope/preimage approval'],
 ['Perform two independent fresh installations under separately owned private roots using exact package and independent original byte closure.',
  'Launch the composite operator, perform permitted reads and check native replay/query parity.',
  'Upgrade to a separately identified generation, export the permitted full package/evidence, restore into a third owned empty destination and cold replay; rollback to the retained verified predecessor without restoring live Sessions or secrets.',
  'Exercise source/environment/preimage mismatch and interrupted installation; leave uncertain keys inspect-only.',
  'Declare service health separately; no background service is implied by successful file installation.'],
 ['Two independent fresh installation and composite launch proofs','upgrade/export/restore/cold replay/rollback with retained history and original private exclusions','explicit supported environment and residue'],
 ['Scratch fixture install called complete platform support','installed files mistaken for running service','protected /tmp dependency gone'],
 'Complete installation fixture class plus real final-package fresh-host/environment rehearsal and composite startup.', 'R02 R07','AC06 AC11 AC13')

task('T20','Close runtime privacy prerequisites before the pilot','L2','T15','privacy reviewer',
 [OLD+'work-pack/tasks/R06.md', 'product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md'],
 ['new final-family boundary selection/report','protected custody evidence outside repository'],
 ['Exact public package inventory','complete protected proof/host dependencies','original R06 obligations'],
 ['Enumerate every selected public and protected member including API, native resources, packaging, private host state, fixture archives and pilot outputs.',
  'Review originals for key material, credentials, live DB/operator state and path disclosure; publish only eligible bounded postimages.',
  'Bind checks to the exact frozen successor and full member list; prior API14 checks and staged API16 boundary are historical.',
  'Record pre-pilot runtime boundary conformance; final R06 closure over later docs, Work, pilot and materialized package bytes occurs at T25. Any payload change invalidates affected proof.'],
 ['Actual same-family pre-pilot runtime privacy conformance','every currently selected runtime member dispositioned','no protected input copied into public package; late artifacts explicitly pending T25'],
 ['Prepared448 inventory treated as conformance','privacy filter corrupts proof graph','keys in original snapshot archive'],
 'Independent full selected boundary review and bounded public payload inspection against exact final-family source/profile.', 'R06 R07 S02','AC13')

task('T21','Implement and verify operator/developer documentation','L2','T15 T06 T07','documentation maintainer',
 ['docs/proposals/0009-lab-runtime-documentation/PROPOSAL.md', 'docs/proposals/0009-lab-runtime-documentation/CONTENTS.md'],
 ['selected maintained docs/lab source pages','generated exact operation reference','website staging'],
 ['Approved local documentation convention','frozen entrypoint/configuration contracts','actual qualification status'],
 ['Follow the existing website pipeline and proposal page map for startup, source/state, sessions, API, domain work, recovery, dependencies and extension.',
  'Generate operation reference from all34 exact contracts with effect/permission/error explanations.',
  'Verify copyable setup in an empty owned environment and link failures to actual diagnostics.',
  'Label admitted v1, v2 candidate and successor integration status; update evidence status at T25 without modifying frozen runtime bytes.'],
 ['Operator can follow startup and recovery instructions','all34 reference has exact sources','docs links/rendering and currentness checked'],
 ['Stale DESIGN v14 labels copied','reader pilot presented as autonomous task runner','docs install outside declared environment'],
 'Existing website documentation build/link/import checks discovered in documentation-system audit; fresh operator recipe walkthrough.', 'R03 R05 R07','AC01 AC11 AC12')

task('T22','Observe genuine engineering, research and later learning work','L2','T16 T17 T18 T19','bounded work owners',
 ['product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md', OLD+'work-pack/tasks/W09.md', OLD+'work-pack/tasks/R05.md'],
 ['new candidate Work/evidence/failure/Lesson/Application records and observations'],
 ['Real engineering and evidence questions','selected actual work authority/Tool/Session','observed failure and reviewed candidate lesson'],
 ['Perform one bounded genuine engineering task and one research/evidence task using the same selected candidate; record outcome satisfaction independently from schema validity.',
  'Derive an evidence-bound candidate lesson from an actual observed failure with explicit generator, applicability and scope.',
  'Perform a later genuine task, apply the eligible reviewed lesson and assess outcome/counterevidence.',
  'Retain actual attempts, incorrect results, cuts, timings and exclusions; candidate success cannot close admitted-operation obligations.'],
 ['Real engineering and research satisfaction observations','causal later lesson application/assessment','technical fixtures distinguished from genuine Work'],
 ['Controlled fixture called genuine task','correspondence treated as causal benefit','synthetic human observation'],
 'Independent review of real task inputs, actual tool/evidence outputs, failure lineage and later observed outcome.', 'C12 W03 W04 W05 W06 W09 R04 R05','AC08 AC09')

task('T23','Run the real owner pilot with the scoped Paperclip bridge','L2','T17 T18 T19 T20 T21 T22','human pilot owner',
 ['product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md', RUN+'paperclip-local-pilot-0270/qualification.json'],
 ['new final-family pilot protocol/attempt receipts','existing private Paperclip pilot state only when authorized'],
 ['Human owner confirmed in conversation','two agreed Paperclip questions','three declared owner journeys','fresh independently authorized current grants'],
 ['Explain setup using the maintained launcher and docs; distinguish limited reader integration from scoped task execution.',
  'Require a currently live newly authorized grant where necessary; never renew an expired original proof by editing its bytes.',
  'Have the actual human perform all three journeys, including fresh Agent/Session continuity and correct independently sourced answers.',
  'Record inputs, attempts, incorrect answers, elapsed time, findings and source cut; record baseline not attempted without claiming improvement.',
  'Use Paperclip only for the exact demonstrated/authorized capability; general automatic task creation/updates require a separately bounded extension.'],
 ['Authentic human usefulness observations','all three journeys independently checked','final-family technical bridge receipt and honest capability limits'],
 ['API14 reader result transferred','expired grant treated as live','agent answer relabeled human pilot','broad task automation presumed'],
 'Human walkthrough and separately verified technical run, on the same final source/profile; no usability claim before actual response.', 'R05 W09 R07','AC04 AC08 AC09 AC12')

task('T24','Audit all original acceptance and operational residue','L2','T16 T17 T18 T19 T20 T22 T23','independent acceptance reviewer',
 ['product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md', OLD+'dag.json', OLD+'swu-manifest.json'],
 ['new AC01-AC13 matrix','original46/63 obligation crosswalk and selected evidence'],
 ['Same-family regression/API/security/install/privacy/work/human proofs','all original task/SWU acceptance texts'],
 ['Map every original task, unit and acceptance clause to exact current evidence or an explicit remaining obligation.',
  'Inspect schema/byte/dependency closure, typed endpoints, query parity/stale cuts, managed-file escapes/overwrite, selected migration and archive restoration.',
  'Separate pre-admission candidate acceptance from actual C13/W09/O07/A02-A04 operation.',
  'Require PASS for every candidate-stage clause ready at this point; classify final package/privacy/recovery AC05/AC13 clauses as T25 obligations and admitted-operation clauses as T27-T30 obligations, with explicit PENDING evidence.',
  'Do not mark all13 fully satisfied at T24; validity, admission, catalog membership or result envelope alone cannot substitute. T25 closes candidate package clauses and T29/T30 close later operational ones.',
  'Keep an honest blocked result for absent owner-dependent evidence; do not relax acceptance.'],
 ['All13 conditions fully dispositioned with stage-specific PASS/FAIL/PENDING and exact downstream owner','all46 tasks and63 source SWUs preserved','clear candidate versus admitted obligation ledger'],
 ['Only red regression cases audited','old completed status considered current proof','post-admission obligation dropped'],
 'Independent clause-by-clause evidence audit using original texts and exact new bindings; record PASS/FAIL/PENDING separately.', 'R01 R04 R07 C13 W09 O07 A03','AC01 AC02 AC03 AC04 AC05 AC06 AC07 AC08 AC09 AC10 AC11 AC12 AC13')

task('T25','Freeze the exact final review bundle and rehearse it','L2','T12 T13 T14 T24','final-package coordinator',
 [OLD+'work-pack/tasks/S02.md', 'product/lab/release-candidates/v1/release-validation/0001/S02-package-specific-gaps-0276.md'],
 ['new final package/owner-effect/base-State/digest manifests','exact mixed-target rehearsal evidence','acyclic stable unsigned cores'],
 ['All selected original363 members and explicit additional member disposition','qualified execution family','real current owner-role prerequisites'],
 ['Account for original363 and every additional target such as Method revision/environment; explicitly resolve whether total is363/365 or another exact selection.',
  'Materialize target postimages, scopes, original dependencies, independent stable cores and authoritative base State/history before review.',
  'Rehearse the final heterogeneous instance under proven publisher/recovery using scoped scratch credentials; retain actual full-package cold proof.',
  'Build a layered acyclic manifest: target/code cores, then observed evidence attestations, then owner-response envelope; no core embeds its own future digest.',
  'Verify actual owner assignments, all supported/environment/public/protected carriers and separate operational authorization fit.',
  'Close final R06 delta conformance over all late documentation, genuine Work/learning, human observations and package materializations. Bind final candidate AC05/AC13 evidence; retain admitted-operation PENDING until T29/T30.',
  'Keep actual owner decisions absent; if unknown future Decision bytes alter semantic targets, record D01 blocked and seek the specific representation disposition.'],
 ['Closed exact source/profile/member/target/evidence/owner/effect matrix','final instance publication/recovery rehearsal PASS','final full-payload R06 conformance including late artifacts','candidate acceptance complete with admitted-operation obligations explicitly retained','S02 ready with no unknown semantic targets or digest cycle'],
 ['Owner keys or decision fabricated','unmaterialized future target','all-or-nothing bundle partially ready','late manifest self-reference'],
 'Independent whole-bundle byte/digest/cut/owner/carrier/privacy check plus final-instance scratch publication and crash/cold verification.', 'C10 W08 O06 R07 S02','AC05 AC13')

task('T26','Collect the actual exact final owner disposition','L3','T25','actual accountable owners',
 [OLD+'work-pack/tasks/R08.md'], ['actual Decision/envelope through authorized owner route'],
 ['Exact frozen T25 bundle','current role assignments','independently scoped admission and operational/release targets'],
 ['Present exact targets, byte/core/evidence digests, effects, base cut and remaining post-admission conditions to each accountable owner.',
  'Record authentic approve/reject/defer/stop outcomes per exact member and scope.',
  'Do not treat plan review or user instruction to plan as an admission/release Decision.',
  'On revision invalidate changed targets and affected proofs; do not force one checkpoint if new semantic judgment is required.'],
 ['Actual positive dispositions for every applicable exact target or explicit blocked/rejected route','no blanket assumed owner authority'],
 ['Synthetic approve outcome','owner scope missing','changed bundle after signature'],
 'Owner verification of exact signed/disposed bundle against current base/cut and authoritative role assignment.', 'R08','AC13')

task('T27','Apply exact authorized repository admission','L3','T26','authorized repository publisher',
 [OLD+'work-pack/tasks/A01.md'], ['exact owner-approved canonical postimages only'],
 ['Actual T26 positive authority','unchanged target/base/preimage','T25 tested publisher'],
 ['Recheck every owner response, scope, source/base and preimage immediately before effect.',
  'Apply admissions and deterministic semantic/governance consequences atomically; zero activations/external effects inside admission.',
  'Verify State/history and registry/index/mirror convergence by cold replay.',
  'On uncertainty inspect/reconcile the exact transaction; preserve foreign state and rollback dependencies.'],
 ['Actual admission receipt and exact output bindings','atomic recovery and successor State','zero hidden activation'],
 ['Admission treated as activation','positive response expired or scope mismatch','partial bundle applied'],
 'Actual authorized publisher transaction and independent cold verification, with each original A01 acceptance clause.', 'A01','AC05 AC10 AC13')

task('T28','Execute separately authorized local operational setup','L3','T27','authorized local operator',
 [OLD+'work-pack/tasks/A02.md'], ['exact independently authorized private operator/store/scope only'],
 ['Represented current operational authorization','post-admission compatible profile','retained private custody/branches/rollback'],
 ['Select and validate actual operator, key custody, store, Project scope and explicit local instructions.',
  'Execute only provisioning/adoption/branch transitions actually authorized by the exact governing records.',
  'Record observed operational outcomes and retain old stores/generations for rollback.',
  'Do not start public/network/background services under the local runtime release scope.'],
 ['Actual independently selected operating scope/store/operator','post-admission compatible profile','local operation receipts and residue'],
 ['CandidateScope treated as durable operational authority','A01 embeds activation','private state lost'],
 'Actual authorized local setup followed by health/identity/profile/read/write checks within represented scope.', 'A02 C11','AC04 AC11 AC13')

task('T29','Verify original admitted-operation obligations','L3','T28','independent operational reviewer',
 [OLD+'work-pack/tasks/A03.md'], ['new admitted operational observations and residue ledger'],
 ['Actual admitted state and authorized Work','original C13/W09/O07/R04 obligations'],
 ['Assess real admitted continuity, Work satisfaction, workflow/lesson outcome, ontology/import coherence and capability adoption against original criteria.',
  'Verify recovery and final gap/failure dispositions using actual current state.',
  'Treat new observations/lessons/semantic targets as candidates until independently admitted.',
  'If new effects/authority or evidence are required, report partial/blocked and identify the exact next gate.'],
 ['Original admitted operational milestones fully assessed','candidate evidence separated from operation','no unreported remaining obligation'],
 ['Candidate Work used as admitted proof','new lesson auto-admitted','scope silently expanded'],
 'Original A03/C13/W09/O07 clause-by-clause verification against actual admitted operation and authentic observed outcomes.', 'A03 C13 W09 O07 R04','AC04 AC08 AC09 AC10 AC12')

task('T30','Complete only represented release effects','L3','T29','actual release owner/operator',
 [OLD+'work-pack/tasks/A04.md', API+'release_readiness.py'], ['exact currently authorized selected local release records/effects only'],
 ['Actual T29 operational closure','fulfilled acceptance conditions','current represented release authority'],
 ['Recheck exact release targets, supporting evidence, owner authority and explicit effect conditions.',
  'Execute only already represented authorized actions; additional evidence-dependent semantic decisions require their actual owner disposition.',
  'Produce actual release/action receipt or explicit blocked disposition.',
  'Keep public push/deployment/service activation outside default local scope unless separately explicitly authorized.'],
 ['All selected release conditions fulfilled','actual release receipt and stable/usefulness claims supported','otherwise honest blocked release'],
 ['release.prepare blocked domain result counted release','missing actual operation','unapproved external effect'],
 'Independent exact A04 release-condition/authority/effect verification; readiness test PASS cannot close this task.', 'A04 R08','AC13')

task('T31','Resolve workflow output-bearing transition support','L1','T00','workflow integration maintainer',
 [API+'workflow_transition.py', 'implementation/lab-workflows/candidates/v1/workflows/engineering.py'],
 ['successor WorkflowTransition output integration and selected workflow bindings'],
 ['Original selected WorkflowDefinition allowed_output_carriers','real engineering/research candidate outputs','WorkflowRun/transition result contracts'],
 ['Inventory the ten selected workflow templates and identify output-bearing steps required by original bindings.',
  'Implement original output carrier validation and linkage for required supported transitions, retaining independently governed admission/effect handling.',
  'Reject wrong carrier, missing original bytes, unresolved dependency, incompatible scope or unauthorized output before effect.',
  'If an output transition is explicitly outside the selected capability, document its exact contract exclusion; do not narrow original acceptance merely to pass.',
  'Record actual output-bearing candidate WorkRun transition with independently verified outcome lineage.'],
 ['Each selected output-bearing transition is implemented and proved or explicitly disposed under original scope','no implicit artifact admission','positive/negative carrier and scope evidence'],
 ['Zero-output guard mislabeled full Workflow support','output fields invented','schema validity treated as Work satisfaction'],
 'Exercise one genuine selected output-bearing transition and wrong-carrier/scope negatives; compare all original required template bindings.', 'W01 W03 W04 W07 W08 W09 R07','AC01 AC02 AC08')

task('T32','Establish native batch interruption and recovery guarantees','L1','T00','native persistence maintainer',
 ['implementation/lab-ontology/candidates/v1/adapters/native/src/lib.rs', OLD+'work-pack/tasks/S02.md'],
 ['successor native batch adapter or explicitly selected publisher recovery wrapper','owned native interruption observations'],
 ['persist_batch sentinel/per-file hardlink implementation','selected operation call chains','actual declared transaction/recovery guarantee'],
 ['Map which selected calls expose persist_batch and whether a proven outer publisher supplies atomic commit/recovery.',
  'In owned copies interrupt between file links, after sentinel creation and before cleanup; cold replay and inspect recognized versus foreign residue.',
  'If selected acceptance is not met, implement durable commit/rollback or an exact existing recovery wrapper in a successor, with the real commit point explicit.',
  'Never delete an unknown lock or foreign bytes on stale-lock guess; uncertain work remains inspect/reconcile.',
  'Publish measured guarantees and limits; static suspicion alone is not an observed crash defect.'],
 ['Selected native batch boundary has causal interruption/recovery evidence','atomic/recoverable declared behavior holds or exact gap blocks affected scope','no foreign-state loss'],
 ['Per-file atomicity called batch atomicity','stale sentinel guessed safe','partial event history after kill','unselected risk generalized to whole runtime'],
 'Owned process-interruption probes and fresh cold native replay at each persisted batch boundary; no live store mutation.', 'O02 O05 O06 R07 S02','AC05 AC10')

# Newly discovered implementation boundaries must be resolved before freezing
# the corrected executable; task order in this file is not execution order.
task('T33','Implement authentic owner-response ingestion for publication','L1','T00','owner-response adapter maintainer',
 ['implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/publisher.py', OLD+'work-pack/tasks/R08.md'],
 ['successor versioned authenticated conversation adapter','publisher response verification contract'],
 ['Current helper and verifier accept key-adapter with human_conversation_outcome=None','exact stable review/member cores','independent actual host conversation evidence and role authority source'],
 ['Define the exact trusted host/issuer provenance for actual human owner message and signed response, including principal, governing role/scope/period, bundle/core digests and selected outcome.',
  'Implement a separately versioned response ingress/verifier; preserve old fixture key-adapter behavior as technical rehearsal only.',
  'Bind actual message content/identity to exact independently selected host evidence; caller-declared human flags or an agent-generated approve payload confer nothing.',
  'Reject wrong owner, forged/absent host proof, changed target, replay, expired authority and missing governing role before publication.',
  'Keep actual approving outcome absent until T26. If no trusted host evidence mechanism exists, expose that concrete external prerequisite rather than accepting a synthetic response.'],
 ['Executable versioned actual-owner adapter and explicit trusted provenance contract','causal forged/stale/wrong-scope negatives','original fixture helper cannot authorize actual R08'],
 ['None human outcome accepted as real review','copying user plan request as admission approval','untrusted conversation evidence accepted','owner key custody treated as governing authority'],
 'Independent response-verifier contract review and technical positive/negative adapter fixtures; actual human disposition and fresh positive authority only at T26.', 'C07 C10 S02 R08 A01','AC05 AC13')

task('T34','Implement the explicit operational provisioner successor','L1','T00 T07','operator provisioning maintainer',
 ['implementation/lab-provisioning/candidates/v1/provision.py', 'implementation/lab-provisioning/candidates/v1/OPERATOR.md', API+'auth.py'],
 ['successor versioned operational provisioning plan/controller','protected custody and per-run channel staging rules'],
 ['Candidate-only TemporaryDirectory provisioner','selected compatible runtime/source/profile','independent operator custody/authority and persistent owned store paths','ReaderChannel current /tmp policy constraints'],
 ['Define an explicit plan selecting owner/operator principal, scope, compatible engine/profile/base HEAD, permanent owned store path, private key/policy custody and rollback retention.',
  'Implement separate operational construction/preflight and owned rehearsal; do not mutate CandidateScope to silently confer permanent or admitted authority.',
  'Provision current ephemeral per-run channel inputs from durable protected custody to the independently owned staging boundary required by the selected auth contract, or implement an explicitly versioned constrained locator contract.',
  'Validate origin, ownership/mode/no-follow path, inode/preimage, exact source/profile, current policy/period and revocation before and after relevant effects.',
  'On restart rebuild a fresh authenticated channel; never restore Session RAM or reuse consumed nonce. Reconcile uncertain provisioning from exact durable operation evidence.',
  'Actual admitted provisioning happens only at T28 under separately represented current authority; technical rehearsal uses clearly scoped owned candidate credentials.'],
 ['Maintained versioned provisioner supports exact intended operator/store/custody selections','current channel staging and fresh restart/revocation evidence','old candidate-only boundary and rollback preserved'],
 ['Temporary branch mislabeled permanent setup','arbitrary home-policy path bypasses auth','silent grant renewal','keys in Git','candidate role creates admitted authority'],
 'Two independently owned provisioning rehearsals, fresh channel/restart/nonce/revocation checks and preimage/permission/path negatives; inspect exact prospective operational instructions.', 'C11 R02 R03 R07 A02','AC04 AC11 AC13')

next(t for t in TASKS if t['id']=='T06')['depends_on'] += ['T34']
next(t for t in TASKS if t['id']=='T14')['depends_on'] += ['T33']
next(t for t in TASKS if t['id']=='T09')['depends_on'] += ['T08']
next(t for t in TASKS if t['id']=='T15')['depends_on'] += ['T31','T32']
task('T35','Measure the independently current Source8 lifetime','L0','T00 T02','Session performance diagnostician',
 [RUN+'common-all34-0275/units/member--Source8-lifecycle.json', API+'source8_context_sessions.py', 'product/lab/release-candidates/v1/interface/lesson-host-composition-v45-action-0148/host.py'],
 ['owned task-local Source8 diagnostics and phase ledger'],
 ['T02 independently signed current source/reader/mapper/Context/runtime family','actual parent resource and strictest source/reader/Session deadline','original expired refusal'],
 ['Cold-verify current native source/mapper/Context bindings and independently authorized custody before positive instrumentation.',
  'Record sanitized operation/reply/source/profile/cut/branch identity and actual strictest expiry at each phase.',
  'Measure source guard, native replay, schema validation, locks/CPU, Session open, Machine setup, lesson selection, caller handling and negative-case cost with real UTC and monotonic durations.',
  'Count exact trusted callbacks and nested pure-scope boundaries without replacing production callbacks or clocks.',
  'Retain primary expiry/refusal separately from secondary caller exception; do not extend the positive resource after expensive negative probes.'],
 ['Actual current-family phase attribution ledger','source period and ephemeral lease separately accounted','causal refusal and sanitized exact inputs/outputs'],
 ['Expired original reused positively','measurement changes callback or clock','negative probe consumes positive lease','credentials in trace'],
 'One owned instrumented current Source8 lifetime on task-local immutable pins, with full entry/exit guards; diagnostics are not final qualification.', 'C03 C06 C08 W06 R03 R07','AC01 AC04 AC09')
machine_diag=next(t for t in TASKS if t['id']=='T01')
machine_diag['source_anchors']=[API+'test_machine_transport.py', API+'machine_transport.py', API+'receipts/per-call-observations/0cb8537fd64e4bdea5ec9b18a9e64a89.json']
machine_diag['inputs']=['Same-case raw integrity-failed reply and static legacy/custody helper mismatch','a genuinely live permitted legacy parent with separately current channel proof','selected source/profile/cut and seven read contracts']
machine_diag['ordered_rules']=['Capture sanitized exact context.get reply, source/profile/cut, actual runtime class and parent/channel identity.', 'Record the precise throwing file/function/line and selected helper origins under task-local immutable diagnostic pins; do not infer causality from generic integrity-failed.', 'Recheck original signatures, permission, callbacks, current policy and actual expiry without substituting clocks or methods.', 'Machine diagnosis can proceed independently of T02 Source8 construction when its legacy parent inputs are genuinely live; otherwise explicitly select a new current legacy diagnostic family.']
machine_diag['acceptance_evidence']=['Exact causal Machine refusal trace or honestly unresolved boundary','correct same-case raw-reply/source binding','diagnostic variant distinguished from qualifying implementation']
machine_diag['reviewable_check']='Focused MachineTransport.test_02 reproduction with independently current legacy inputs and sanitized exact guard trace; no Source8 construction dependency.'
next(t for t in TASKS if t['id']=='T03')['depends_on']=['T35','T02']
next(t for t in TASKS if t['id']=='T03')['inputs'][0]='Measured T35 Source8 bottlenecks'
next(t for t in TASKS if t['id']=='T03')['ordered_rules'].append('T35 attributes the actual host/producer/preparation call chain; include causally affected successor modules rather than assuming wrapper-only changes. Scope ends before derived evidence writes or Tool/journal claims, with fresh effect preclaim/posteffect checks.')
next(t for t in TASKS if t['id']=='T22')['acceptance_evidence'][1]='Attributable actual later use and independent outcome assessment within its declared causal ceiling; metadata correspondence alone proves no benefit'
next(t for t in TASKS if t['id']=='T03')['ordered_rules'].insert(2,
    'Specify exact input/output/scope invariants for each optimized pure helper. Qualify callback/method substitution, code/schema/profile/source/input tamper inside the scope, nested scopes, exceptions, live revocation/expiry between entry and exit, and an effect attempted inside a read-only scope. Preserve original full fresh entry/exit verifier and effect preclaim/posteffect checks; prove each causal refusal without monkeypatching original callbacks.')
next(t for t in TASKS if t['id']=='T31')['ordered_rules'].insert(4,
    'Where actual later learning is claimed, wire the selected eligible Lesson/Application into the relevant producer/tool/workflow input through its original supported mechanism. Application metadata attribution alone is not influence; identify and qualify the actual consuming path before the final freeze.')
next(t for t in TASKS if t['id']=='T22')['ordered_rules'].insert(3,
    'Show actual consuming dataflow or a specific observed behavior from the applied Lesson to the later task input/action/result, with a falsifiable expected outcome and counterevidence. Keep attribution-only metadata and human testimony separately labeled; if the consumer requires new code, return to successor construction/freeze and requalify affected descendants rather than modifying frozen code or claiming causality.')
next(t for t in TASKS if t['id']=='T00')['ordered_rules'].append(
    'Budget absolute source validity separately from ephemeral credentials and live resource leases: the original Source8 source period is24h, reader grant at most30min, Session at most900s. Select the actual minimum with clock/currentness checks; reserve independent fresh credentials immediately before each permitted attempt, never extend an original interval.')
next(t for t in TASKS if t['id']=='T02')['ordered_rules'].append(
    'Early diagnostic source instances are disposable independently signed development selections. Before final T15, construct a distinct just-in-time final source family only after code assembly and measured qualification duration/human availability are known. Retain every older period and refusal. If current contracts cannot bind the fresh family independently without changing frozen rows, construct a new fully pinned successor and requalify; never mutate a frozen fixture or silently renew it.')
next(t for t in TASKS if t['id']=='T15')['ordered_rules'].insert(1,
    'Check remaining absolute source window against measured regression/all34/install/work/pilot time plus declared margin. Select and sign the just-in-time final source family with its own exact source/cut/binding before freezing, after coordinating actual pilot availability. Issue separately authorized fresh reader grants and Sessions immediately before each attempt within original30min/900s maxima. If the source/selected grant lapses, stop positives; new immutable source or contract bytes require a new freeze and all affected source-bound qualification. Freeze code and source only when the execution window is credible; no speculative long grant or backdating.')
next(t for t in TASKS if t['id']=='T08')['ordered_rules'].insert(1,
    'Complete two ordered implementation checkpoints: first the closed protected-reader/binding-kind contract with positive and no-follow/current-boundary negatives; then the semantic graph selector consuming that accepted contract. T09 consumes the complete accepted T08 contract; shared installation hooks are merged serially.')
next(t for t in TASKS if t['id']=='T19')['ordered_rules'].insert(3,
    'Compare independently rebuilt package manifests and restored original bytes at the same source/cut for deterministic equality; record both fresh-install environment identities and every private exclusion.')
next(t for t in TASKS if t['id']=='T25')['ordered_rules'].insert(4,
    'Keep named digest domains separate: immutable execution code/source/profile; semantic target/unsigned Decision cores; exact-target rehearsal input; observed terminal/Work/pilot/privacy evidence; review envelope selecting prior domains; later owner-response envelope. Receipts must bind the fixed rehearsal input/core, never the final manifest that includes those receipt hashes. Evidence attestation can select a fixed manifest core while its enclosing review envelope selects the attestation; no mutual full-manifest hash dependency is allowed. Validate original schemas for every boundary, especially D01.')

def write_json(path, value):
    (HERE/path).parent.mkdir(parents=True, exist_ok=True)
    (HERE/path).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def link(path):
    return f'[{Path(path).name}]({ROOT/path})'

def main():
    edges=[{'from':dep,'to':t['id'],'meaning':'accepted upstream output; no authority inherited'} for t in TASKS for dep in t['depends_on']]
    dag={'schema_version':'lab-runtime-completion-dag/v1-candidate','status':'candidate','authority_effect':'none','node_count':len(TASKS),'edge_count':len(edges),'nodes':TASKS,'edges':edges,'execution_authorized_by_this_artifact':False,'source_baseline':'SOURCE-BASELINE.json','parallelism_policy':'At most three workers plus coordinator; disjoint exact resolved write scopes; one merge and one freeze writer. High-latency lifetime qualification serialized or load-budgeted.'}
    write_json('dag.json',dag)
    units=[]
    for t in TASKS:
        scope='Exact owner-approved targets only after T26; resolve at effect boundary.' if 26 <= int(t['id'][1:]) <= 30 else 'New successor staging modules listed below plus uniquely owned new evidence paths; resolve exact paths at T00. No existing frozen code/private state mutation.'
        unit={'id':t['swu_ids'][0],'parent_task':t['id'],'depends_on':[f'SWU-{x}-01' for x in t['depends_on']],'source_anchors':t['source_anchors'],'related_context':['analysis/core-workflows.md','analysis/integration-operations.md','analysis/qualification-release.md','SOURCE-BASELINE.json'],'write_scope':t['prospective_modules'],'write_scope_rule':scope,'inputs':t['inputs'],'ordered_rules':t['ordered_rules'],'outputs':t['acceptance_evidence'],'done_criteria':t['acceptance_evidence'],'failure_modes':t['failure_modes'],'validation_surface':t['reviewable_check'],'execution_owner':t['owner'],'handoff_status':'not-executed; exact scope/authority/evidence preflight required'}
        units.append(unit)
        lines=[f'# {t["id"]} — {t["title"]}', '',f'Layer: {t["layer"]}. Status: not-started. Owner recommendation: {t["owner"]}. Authority effect: none.', '', '## Dependencies', '', ', '.join(t['depends_on']) or 'None; execution baseline selection starts here.', '', '## Inputs and source selectors', '']
        lines += ['- '+x for x in t['inputs']]+['']+['- '+link(x) for x in t['source_anchors']]
        lines += ['', '## Implementation detail / ordered rules', '']+[f'{i}. {x}' for i,x in enumerate(t['ordered_rules'],1)]
        lines += ['', f'## Smallest working unit {unit["id"]}', '', f'Parent: {t["id"]}. Dependencies: '+(', '.join(unit['depends_on']) or 'none')+'.', '', 'Write scope rule: '+scope, '', 'Prospective modules/outputs:', '']+['- `'+x+'`' for x in t['prospective_modules']]
        lines += ['', 'Related context: the three implementation audit reports and SOURCE-BASELINE.json; select exact symbol/line excerpts at execution handoff. This plan creates no credentials, approved runtime effects or governing roles.', '', '## Done criteria and acceptance evidence', '']+['- '+x for x in t['acceptance_evidence']]
        lines += ['', '## Edge cases and failure modes', '']+['- '+x for x in t['failure_modes']]
        lines += ['', '## Validation / reviewable check', '', t['reviewable_check'], '', 'Focused development checks before T15 require their own exact task-local candidate pins, saved selection and owned outputs; they do not claim final qualification. T15 supplies the independently frozen shared pins for T16 onward. Reusing frozen API16 source pins for changed code is prohibited. No runtime checks were executed during plan authoring.', '', '## Original obligation mapping', '', 'Tasks: '+', '.join(t['original_tasks'])+'. Acceptance: '+', '.join(t['acceptance_conditions'])+'. Preserve their full source criteria in obligation-crosswalk.json.', '', '## Synchronization and handoff', '', 'Before execution resolve one exact SWU, paths, scoped authority and independently selected inputs. After execution record actual output hashes, command/terminal observations, counterevidence and source/profile/cut in a new run ledger. The coordinator updates status only from accepted evidence. Any code/input change invalidates affected descendants; retain old evidence. No plan-only task closure implies native goal completion.','']
        path=HERE/t['contract_path'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines))
    write_json('swu-manifest.json',{'schema_version':'lab-runtime-completion-swu/v1-candidate','authority_effect':'none','units':units})
    old=json.loads((ROOT/OLD/'dag.json').read_text());old_units=json.loads((ROOT/OLD/'swu-manifest.json').read_text())['units'];cross=[]
    for n in old['nodes']:
        selected=[t['id'] for t in TASKS if n['id'] in t['original_tasks']]
        # Every original obligation remains covered by the independent complete audit,
        # even where current evidence may already satisfy its implementation portion.
        if 'T24' not in selected: selected.append('T24')
        if n.get('post_approval_obligation_ref'):
            route={'A01':'T27','A02':'T28','A03':'T29','A04':'T30'}.get(n['post_approval_obligation_ref'])
            if route and route not in selected:selected.append(route)
        cross.append({'original_id':n['id'],'original_contract':OLD+n['contract_path'],'original_status_historical':n['status'],'completion_tasks':selected,'full_original_node':n,'original_swu_ids':[u['id'] for u in old_units if u['parent_task']==n['id']],'rule':'Retain all original acceptance; reuse only exact eligible evidence. Historical status is not a new proof.'})
    write_json('obligation-crosswalk.json',{'schema_version':'lab-runtime-original-obligations/v1-candidate','original_task_count':len(cross),'original_swu_count':len(old_units),'tasks':cross,'original_units':old_units,'authority_effect':'none'})
    mermaid=['flowchart TD']+[f'  {t["id"]}["{t["id"]}: {t["title"]}"]' for t in TASKS]+[f'  {e["from"]} --> {e["to"]}' for e in edges]
    (HERE/'DAG.md').write_text('# Lab runtime completion dependency graph\n\nCandidate plan; no execution or authority. Edges require accepted upstream evidence. [dag.json](dag.json) is the machine source. [Task contracts](WORK-PACK.md) define each node.\n\n```mermaid\n'+'\n'.join(mermaid)+'\n```\n\nT00 starts the technical lanes. T12 can be resolved in parallel, but it gates final package readiness. T13 has an explicit design stop if unknown owner Decision bytes change semantic target digests. T26–T30 require actual owner authority and operational observations.\n')
    lines=['# Lab runtime completion work-pack','','Status: candidate, not executed. Complexity: high. Output mode: split. Authority effect: none.','','This is a completion overlay for plan0010, not a replacement of its acceptance or evidence. Implementation details and one explicit smallest working unit per task are in the linked task contracts.','','Execution-pack: [EXECUTION-PACK.md](EXECUTION-PACK.md). Layering: [IMPLEMENTATION-LAYERING.md](IMPLEMENTATION-LAYERING.md). Sources: [SOURCE-BASELINE.json](SOURCE-BASELINE.json). Original obligations: [obligation-crosswalk.json](obligation-crosswalk.json).','','Global mutation gate: not requested in this planning turn. Task-local execution can proceed only with its exact authority, upstream evidence, resolved write scope and selected current inputs. Owner/semantic stops gate only affected descendants. The blocked Goals registration does not prevent producing this local candidate plan.','','| Task | Layer | Dependencies | Owner recommendation | Status |','| --- | --- | --- | --- | --- |']
    lines += [f'| [{t["id"]}]({t["contract_path"]}) {t["title"]} | {t["layer"]} | {", ".join(t["depends_on"]) or "—"} | {t["owner"]} | not-started |' for t in TASKS]
    lines += ['', 'Each task-local SWU is also recorded in [swu-manifest.json](swu-manifest.json). No completion is inferred from this plan or its validation. Actual implementation, qualification, pilot and owner approval remain work.','']
    (HERE/'WORK-PACK.md').write_text('\n'.join(lines))

if __name__=='__main__':main()
