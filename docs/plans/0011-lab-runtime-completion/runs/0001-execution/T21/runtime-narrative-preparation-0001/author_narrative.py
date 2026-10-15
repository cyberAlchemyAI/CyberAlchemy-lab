"""Owned narrative authoring; no Lab imports, runtime, installer or site mutation."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
RUN = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API = 'product/lab/release-candidates/v1/interface/api-integration-v16'
SOURCE_PATHS = {
 'admission':'implementation/lab-runtime/ADMISSION.md',
 'decision75':'docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md',
 'v1-readme':'implementation/lab-runtime/v1/README.md',
 'v1-contract':'implementation/lab-runtime/v1/CONTRACT.md',
 'v1-cli':'implementation/lab-runtime/v1/lab_runtime/cli.py',
 'v1-entry':'implementation/lab-runtime/v1/lab.py',
 'v1-store':'implementation/lab-runtime/v1/lab_runtime/store.py',
 'v1-session':'implementation/lab-runtime/v1/lab_runtime/session.py',
 'v1-source':'implementation/lab-runtime/v1/lab_runtime/sources.py',
 'v1-profile':'implementation/lab-runtime/v1/profile.json',
 'v1-requirements':'implementation/lab-runtime/v1/requirements.txt',
 'v2-review':'implementation/lab-runtime/v2/REVIEW.md',
 'v2-profile':'implementation/lab-runtime/v2/profile.json',
 'first-witness':RUN+'/T21/first-inspection-walkthrough-0001/receipt.json',
 'first-terminal':RUN+'/T21/first-inspection-walkthrough-0001/initial-terminal.json',
 'first-corrected':RUN+'/T21/first-inspection-walkthrough-0001/corrected-inspect-terminal.json',
 'deps':RUN+'/T07/revision-0002/dependency-selection-0002.json',
 'provision':'implementation/lab-provisioning/candidates/v1/provision.py',
 'bootstrap':'implementation/lab-bootstrap/candidates/v1/bootstrap.py',
 'integration':'implementation/lab-integration/candidates/v1/validate.py',
 'review':'implementation/lab-review/candidates/v1/review.py',
 'context':'implementation/lab-context/candidates/v1/context.py',
 'native-reader':'implementation/lab-context/candidates/v1/native_reader.py',
 'ontology':'implementation/lab-ontology/candidates/v1/adapters/native/src/lib.rs',
 'continuity':'implementation/lab-continuity/candidates/v2/custody.py',
 'work':'implementation/lab-work/candidates/v1/episode.py',
 'workflow-review':'implementation/lab-workflows/candidates/v1/REVIEW.md',
 'engineering':'implementation/lab-workflows/candidates/v1/workflows/engineering.py',
 'research':'implementation/lab-workflows/candidates/v1/workflows/research.py',
 'host-authority':'implementation/lab-workflows/candidates/v1/authority/evaluator.py',
 'dispatch':'implementation/lab-workflows/candidates/v1/authority/dispatch.py',
 'api-catalog':'docs/proposals/0008-lab-api-contracts/api-contracts.json',
 'api-dispatch':API+'/integration_dispatch.py',
 'api-service':API+'/service.py',
 'api-auth':API+'/auth.py',
 'api-schema':API+'/protocol.py',
 'api-source':API+'/source_bridge.py',
 'api-workspace':API+'/workspace.py',
 'api-session':API+'/source8_context_sessions.py',
 'api-machine':API+'/machine_transport.py',
 'api-attachment':API+'/session_attachment.py',
 'api-journal':API+'/application_journal.py',
 'api-projection':API+'/projection.py',
 'api-package-import':API+'/package_import.py',
 'api-package-export':API+'/package_export.py',
 'api-installer':API+'/r02_installer.py',
 'api-release':API+'/release_readiness.py',
 'sdk':'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/README.md',
 'overlay':RUN+'/T02/composite-merge-preparation-0004/independent-review-0001.json',
 'cycle':RUN+'/T02/family4-dependency-cycle-review-0001.json',
 'capture-flag':RUN+'/T07/api17-task-local-capture-0004/independent-review-0001.json',
 'measurement':RUN+'/T35/measurement-review-0002.json',
 'driver':RUN+'/T35/full-learning-driver-0004/independent-review-0001.json',
 'margin':RUN+'/T03/observed-margin-adapter-0003/independent-review-0001.json',
 'api-docs':RUN+'/T21/api-reference-preparation-0003/reference-0001/README.md',
 'api-docs-review':RUN+'/T21/api-reference-preparation-0003/independent-review-0001.json',
 'paperclip-runner':'product/lab/release-candidates/v1/interface/paperclip-runner-v3/README.md',
 'paperclip-probe':'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/Paperclip-process-adapter-probe-0140.json',
 'paperclip-witness':'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/paperclip-local-pilot-0270/closure.json',
 'publisher':RUN+'/T14/mixed-target-publisher-0002/README.md',
 'contents':'docs/proposals/0009-lab-runtime-documentation/CONTENTS.md',
 'doc-audit':'docs/proposals/0009-lab-runtime-documentation/research/documentation-system.md',
 'site-shell':'website/source/governance-lab-series/templates/start-here.html.in',
 'site-practical':'website/source/governance-lab-series/practical_docs.py',
 'site-renderer':'website/source/governance-lab-series/render_article.py',
 'site-build':'website/build.py',
 'site-maintenance':'website/source/governance-lab-series/SITE-MAINTENANCE.md',
 'site-editorial':'website/editorial_style.py',
 'site-search':'website/source/governance-lab-series/build_site_search.py',
 'site-search-js':'website/source/governance-lab-series/assets/site-search.js',
 'importer':'tooling/docs/import_site_docs.py',
 'docs-maintenance':'docs/lab/MAINTENANCE.md',
}

CONCEPTS = {
 'authority':('website/source/governance-lab-series/governance-lab-reference.html#governance','docs/lab/guide/authority.md'),
 'provenance':('website/source/governance-lab-series/governance-lab-reference.html#evidence','docs/lab/guide/provenance.md'),
 'lifecycle':('website/source/governance-lab-series/governance-lab-reference.html#change','docs/lab/guide/lifecycle.md'),
 'agent':('website/source/governance-lab-series/governance-lab-reference.html#agent','docs/lab/guide/agents-and-memory.md'),
 'learning':('website/source/governance-lab-series/governance-lab-reference.html#learning','docs/lab/guide/operational-learning.md'),
 'records':('website/source/governance-lab-series/governance-lab-reference.html#records','docs/lab/guide/records-and-connections.md'),
 'work':('website/source/governance-lab-series/lab-reference-library.html#def-cal-definition-work','docs/lab/reference/records/def-cal-definition-work.md'),
 'memory':('website/source/governance-lab-series/lab-reference-library.html#def-cal-definition-session-memory','docs/lab/reference/records/def-cal-definition-session-memory.md'),
 'context':('website/source/governance-lab-series/lab-reference-library.html#def-cal-definition-context-view','docs/lab/reference/records/def-cal-definition-context-view.md'),
 'state':('website/source/governance-lab-series/lab-reference-library.html#def-cal-definition-project-state','docs/lab/reference/records/def-cal-definition-project-state.md'),
}

PAGES=[]
def section(title,body,diagram=None):
 return {'title':title,'body':body.strip(),'diagram':diagram}
def page(key,title,description,route,sections):
 PAGES.append({'key':key,'title':title,'description':description,'markdown_route':route,
               'site_file':'runtime-'+key+'.html','article_id':'runtime-'+key,'sections':sections})
def diagram(name,code,alternative,evidence):
 return {'id':name,'language':'mermaid','code':code.strip(),'alternative':alternative,'evidence':evidence,
         'meaning':'Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.'}

READ_COMMAND = '''# Run from the repository root, with the already selected installation0004.
lab_repository="$PWD"
lab_dependencies="$lab_repository/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004"
lab_read_store="/tmp/cal-T21-read-$$"
lab_v1_read() {
  LC_ALL=C "$lab_dependencies/lib/abi/ld-linux-x86-64.so.2" \\
    --inhibit-cache --library-path "$lab_dependencies/lib/abi" \\
    "$lab_dependencies/bin/python" -I -X utf8 -B -S -c \\
    'import sys,runpy;from pathlib import Path;assert not Path(sys.argv[3]).exists();sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2]);sys.argv=sys.argv[4:];runpy.run_path(sys.argv[0],run_name="__main__")' \\
    "$lab_dependencies/deps" "$lab_repository/implementation/lab-runtime/v1" \\
    "$lab_read_store" "$lab_repository/implementation/lab-runtime/v1/lab.py" \\
    --store "$lab_read_store" "$@"
}
lab_v1_read verify
lab_v1_read status
lab_v1_read inspect product-capability:cyberalchemy-lab:governed-knowledge-lifecycle --record'''

page('overview','Operate the Lab','Choose the implementation and the next task before relying on a runtime result.','README.md',[
 section('Start with the admitted inspection path',"""For a first inspection, use the admitted local v1 executable and its frozen Decision 0074 source profile. Decision 0075 admits that exact executable for local inspection, authorized local transactions, replay/recovery and ephemeral context. The admission is an external overlay: its original README can still say candidate without undoing the later decision. Read the [[source:admission|admission scope]], then follow [[page:first-inspection|first inspection]].

The three-command walkthrough checks public source files and selects a deliberately nonexistent store. It creates no store, key or transaction. Its observed output is D74 with 698 verified sources and 468 subjects. This is a useful working entrypoint; it is separate from a permanent service, a new installation and the expanded API."""),
 section('Choose a surface',"""| Surface | What you can rely on | What remains separate |
| --- | --- | --- |
| Admitted runtime v1 | Exact local executable admitted by D75, reading its D74 profile | Current repository D75, permanent service and external consumers |
| Runtime v2 | Separate D75 source-profile candidate | Its candidate review does not replace v1 admission |
| API16 / composite catalog | Code and declared contracts for 28 Base, 3 Action and 3 Governance operations | Full current three-branch qualification and actual permission |
| Changed API17 | Reviewed overlay code exists | Old e417/5c capture is ineligible after changes; new family/selector/capture work is incomplete |
| Paperclip 2026.1005.0 | Recorded bounded process-reader episode | Live availability, a fresh grant, autonomous Work and human usefulness |

These surfaces have different stores, channels and evidence. A filename, result envelope or catalog count cannot select an authority boundary for you. The [[page:status|dated status page]] identifies the evidence cut."""),
 section('Choose your next task',"""| Your task | Reading route |
| --- | --- |
| Inspect a public record and explain its standing | [[page:first-inspection|First inspection]] |
| Prepare a disposable local Work proposal | [[page:local-work|Local Work]] and [[page:provision|provision and review]] |
| Understand agents and their limits | [[page:sessions|Agent sessions]] |
| Deal with a timeout or pending effect | [[page:recovery|Recover and retry]] |
| Connect Paperclip to a selected reader | [[page:paperclip|Paperclip]] |
| Export, import or install a package | [[page:packages|Packages and installation]] |
| Trace the code and state ownership | [[page:architecture|Architecture]] |

For meanings, use the existing [[concept:records|record and definition library]] rather than treating these operational pages as replacement definitions."""),
 section('What a result establishes',"""Record the selected executable/profile, source cut, current permission, exact input and observed output. Then read the result posture. A prepared candidate, an admitted record, an actual action and an assessed benefit are distinct facts.

The full integrated learning path is not yet a supported successful tutorial. The measured episode expired, and the later family4 build exposed a dependency cycle before final runtime qualification. Those failures remain in [[page:status|status]] and [[page:maintenance|maintenance]]. This handbook preparation does not close T21 or publish a release."""),
])

page('status','Runtime status and evidence','Read implementation, admission, source selection and qualification as separate facts.','status.md',[
 section('Selected evidence cut',"""This draft selects public evidence available on 14 October 2026. It does not probe a live service. A later correction needs a new reviewed evidence selection, not an updated date attached to old proof.

The [[source:admission|admission overlay]] identifies v1 as admitted by D75 while its executable remains bound to D74. The [[source:v2-review|v2 review]] selects D75 as a candidate. The [[source:first-witness|fresh read-only walkthrough]] verifies the v1 path with an absent store. Code existence, effective admission and observed behavior are reported independently."""),
 section('Current facts',"""| Fact | Evidence and ceiling |
| --- | --- |
| v1 read-only inspection succeeds | [[source:first-witness|Three positive commands]], 698 sources, 468 subjects, no key/store/transaction |
| The v1 source cut is decision:0074 | D75 repository admission does not silently update the executable |
| The inspected capability has admitted-current effective standing | Its raw record also retains candidate-unadmitted authoring status, draft domain lifecycle and not-observed runtime realization |
| API17 has eight reviewed overlay leaves | [[source:overlay|Exact applied-byte review]]; three preimages retained, five new files, no runtime verdict |
| Old API17 e417/5c metadata is unchanged but ineligible | Changed code no longer matches that execution capture |
| Family4 is ineligible for final runtime | [[source:cycle|Dependency-cycle diagnosis]] and [[source:capture-flag|flagged capture review]] |
| Paperclip reader execution was observed on 13 October | [[source:paperclip-witness|Public technical closure]]; human pilot incomplete and old grant expired |

The evidence details retain hashes and original artifacts. These facts do not combine into full34 operation qualification."""),
 section('Failures that must stay visible',"""The first walkthrough attempted to inspect implementation:cyberalchemy-lab:operational-runtime:v1. It returned unknown subject at D74 because the later D75 implementation admission is outside that cut. The corrected positive example inspects the governed-knowledge-lifecycle capability; both terminals are retained.

The measured learning episode reached lesson selection but expired at its original Session/Context boundary. The [[source:measurement|measurement review]] records the actual failure, cleanup and coverage limits; it contains no successful apply/assess or empirical tail calibration.

Family4's Source table inherited the old API manifest and five selector files as current technical inputs. Final API publication would change those bytes. The build was stopped as an ineligible owned diagnostic; its artifacts and period remain preserved. A distinct successor must select exact historical snapshots without changing original history or weakening guards."""),
 section('What would justify changing this page',"""An updated claim needs its exact selected source/profile and component bytes, actual terminal and cleanup observations, original positive/security/retry/recovery/native coverage, and an independent review. A timing-margin claim additionally needs matched real load, full-tail, instrumentation and uncertainty evidence.

Permanent installation, release readiness, service activation, repository admission and a human usefulness outcome each need their own evidence. Neither a pure component PASS nor a documentation build can supply them. The [[source:api-docs|34-operation reference]] is a historical draft from the prior capture and remains useful for declared contracts, with its qualification limits intact."""),
])

page('first-inspection','First inspection without a store','Check the admitted v1 foundation and read one exact capability record.','tutorials/first-inspection.md',[
 section('Result and prerequisites',"""You will verify the public v1 source selection, read its Project State and inspect one capability record. Use the existing selected installation0004 and repository root. This example does not install dependencies, initialize a store, create a key or call the integrated API.

The [[source:v1-cli|actual parser]] has global options before its subcommand. The shell function below is defined in this page; it is a convenience around that parser, not an installed Lab SDK command. Its assertion refuses an existing store path before each invocation. Choose a fresh path rather than inspecting someone's existing local store."""),
 section('Run the three reads',"""{{CODE:read-command}}

The independently selected interpreter/dependency closure is recorded in [[source:deps|dependency selection]]. Do not replace installation0004 with the newest-looking folder. The isolated flags avoid site-package and bytecode substitutions; the two explicit import roots are the selected dependency directory and v1's own directory."""),
 section('Read the observed output',"""The [[source:first-witness|14 October walkthrough]] used the same parser/interpreter/import arrangement and a different deliberately absent path. verify returned PASS, 698 sources, 468 subjects and zero replayed transactions. status returned store_initialized: false, current freshness and repository_admission_as_of: decision:0074. The source snapshot digest was 3b7c0aa920c195d82b5c1dcc3652b28cd67554b5289f40cf546aa85a7ce3648e.

The capability inspection returned its exact record and separate axes. Effective status was admitted-current; the raw authoring status remained candidate-unadmitted, its domain lifecycle draft, and runtime realization not-observed. Explain each track separately. An admitted capability record does not establish that every implementation or consumer is currently running."""),
 section('If a read refuses',"""Stop on source drift, unresolved references or a dependency mismatch and preserve the selected command and public error. Do not initialize a store to hide drift. Read v1's [[source:v1-profile|frozen profile]] and [[source:v1-source|source capture]].

The retained failed subject implementation:cyberalchemy-lab:operational-runtime:v1 is not a positive example. Its D75 admission is outside the selected D74 envelope. Read that admission through its original decision evidence or select a separately reviewed successor profile; do not edit the v1 profile in place.

No store should exist at the selected read path afterward. The [[source:first-terminal|initial terminal]] and [[source:first-corrected|corrected inspection terminal]] retain this scoped result. This is not a fresh-install or integrated-session walkthrough."""),
 section('Record a useful reading note',"""Write the executable version, cut, inspected identity, effective standing, raw authoring/domain fields, source digest and allowed conclusion. Link unresolved questions rather than guessing an implementation outcome. Continue with [[page:architecture|architecture]] or the existing [[concept:provenance|provenance explanation]]."""),
])

page('local-work','Prepare local Work in an isolated branch','Understand a local proposal, approval, commit and replay without claiming repository admission.','tutorials/local-work.md',[
 section('Standing of this journey',"""The admitted v1 implementation supports authorized local transactions, but this handbook has not replayed a fresh effectful Work journey. Treat this page as the parser-backed preparation and acceptance checklist for that future witness. The [[page:first-inspection|read-only walkthrough]] is the currently observed tutorial.

Use a new owned branch and a separately selected operator key outside the repository. Obtain explicit authority for that local scope before authorization/application. A local owner string and public key define that branch's approval boundary; they do not prove an organizational role or authorize a repository Decision."""),
 section('Select the inputs before creating anything',"""| Input | Required decision |
| --- | --- |
| Runtime/profile | Choose exact v1/D74 or a separately reviewed v2/D75 candidate; never rebase an existing store |
| Store path and ID | New exclusive path, selected local scope and current HEAD |
| Operator identity and key | Actual independently provisioned local approver, private bytes outside Git |
| Work proposal | Exact inputs, planned outputs, carrier, version, scope and expected source snapshot |
| Approval | Complete proposal/Decision cores/time/owner/store/policy/challenge/HEAD binding |

The [[source:v1-cli|example subcommand]] produces planned candidate Work, not a completed task. The [[source:v1-contract|contract]] defines the fields that review must assess."""),
 section('Follow the original transaction boundary',"""The parser route is keygen, init, example, review, authorize, apply, then verify/status. Global --store selects the owned branch for every command. keygen rejects private paths inside the repository; init refuses an existing store. review calculates proposed consequences without approving them; authorize signs exact bytes; apply verifies that signature and current HEAD before commit.

One supported transaction can carry independent targets and Decision cores. It records local histories and consequences together. Its receipt and local Project State identify their store scope. A later repository adoption or activated service needs a separate exact governing decision.

Do not use placeholders as working credentials or treat the command names as permission. Have the exact path/identity/body selected and reviewed before execution. The complete command grammar remains in [[source:v1-readme|the preserved v1 operator guide]].""",diagram('review-commit',"""flowchart LR
  P[Exact candidate proposal] --> R[Review consequences]
  R --> A[Local owner's exact signed approval]
  A --> T[Validated staged transaction]
  T --> H[Atomic HEAD commit]
  H --> C[Cold replay and receipt]
  H -. separate .-> D[Derived graph or files]
  R -. different authority .-> O[Repository owner decision]""","An exact local proposal is reviewed, independently authorized, staged and committed at HEAD. Cold replay checks the committed chain. Derived outputs and repository admission have separate boundaries.",['v1-store','v1-contract','decision75'])),
 section('Observe completion and residue',"""For a future witness, retain the actual proposal/approval hashes, expected and resulting HEAD, independent Decision cores, terminal, cold replay and current-source checks. Record whether Work remains planned, was performed, or has a separately assessed outcome. A successful local admission receipt is not Work satisfaction.

If interrupted, inspect the owned store before deleting anything. Committed history survives; recognized uncommitted staging may be reconciled under expected HEAD. Unknown residue is retained. Do not recycle a proposal ID with different material, or overwrite earlier evidence after a failure."""),
 section('Review and cleanup criteria',"""The tutorial is eligible for a successful walkthrough only after a fresh isolated execution, exact authority selection, receipt, replay/recovery and cleanup have been observed. Dispose only its own known disposable roots/keys under the accepted retention policy; preserve committed public evidence and any uncertainty. Link [[page:recovery|recovery]] and [[concept:work|the canonical Work definition]] when reviewing the result."""),
])

page('provision','Provision a branch and review its authority','Separate environment selection, store creation, key custody and approval.','how-to/provision-and-review.md',[
 section('Choose the kind of provisioning',"""Local v1 init creates a new operational branch. Candidate provisioning constructs a separately scoped branch from pinned runtime/configuration/baseline/HEAD. Composite operator preparation additionally selects three independent branch workspaces, policies and authentication proofs. These actions are not interchangeable.

Read [[source:provision|CandidateScope and CandidateBranch]] for controlled branch construction, [[source:bootstrap|bootstrap composition]] for seed packaging, and [[source:admission|v1 admission]] for its local scope. A package, key, store and admitted implementation each answer a different question."""),
 section('Check the environment before the branch',"""Select the exact executable, parser, profile, dependency closure and supported filesystem assumptions. T07's [[source:deps|1010-file selected dependency declaration]] identifies installation0004; its existence is not a new-install witness or a blanket compatibility result for every package.

Confirm the source cut and current byte checks before selecting a new store. A historical profile may be useful for inspection while lacking current records. Installing Python/native dependencies does not initialize a branch, provision authority or activate a service. The [[page:cli|CLI/environment reference]] keeps those interfaces separate."""),
 section('Keep credential custody explicit',"""A local approver key remains outside Git and outside public artifacts. A reader policy selects a bounded Principal, source, scope, operations, budgets, expiry and nonce channel. Private signing bytes, credential paths with real secrets and live private policy bodies do not belong in task text, replies, exports or tutorial logs.

For the composite candidate, Base, Action and Governance need independent current branch selectors and three proofs. The [[source:sdk|operator contract]] explicitly selects the outer policy custody root separately from Base's actual nested Vault and its original workspace/workspace.json. Copying an outer manifest cannot stand in for the real Vault."""),
 section('Review before authorizing',"""| Stage | What it establishes |
| --- | --- |
| Environment/source inspection | The selected inputs are available and match declared bytes |
| Branch initialization | A new scoped store/configuration exists |
| Candidate review | Consequences, contracts, source cut and unresolved obligations are visible |
| Exact signed authorization | This local approver approved these bytes within this boundary |
| Application and cold replay | The observed scoped effect and its committed chain |
| Repository admission or service activation | Separate governing and operational evidence |

Review failures stay attached to their exact input version. A technical provisioning receipt cannot become Action/Governance or genuine owner authority merely by being passed to another component."""),
 section('When provisioning refuses',"""An existing path, changed baseline/HEAD, unsafe root, missing public key, expired/revoked policy or unknown execution origin should refuse. Preserve the actual error and owned partial state. Choose a separately authorized new branch or correct a new candidate version; do not silently overwrite, restore old Session RAM or extend a historical period.

Fresh setup and full three-branch operation remain pending for the changed API17 composition. Follow [[page:status|status]] and [[page:recovery|recovery]] before interpreting a refusal as a reason to rerun."""),
])

page('sessions','Context and agent sessions','Open only a current bounded resource; dispose it and reconstruct a fresh one.','how-to/agent-sessions.md',[
 section('Select the session implementation',"""Admitted v1 has a local source/HEAD-bound Session. Candidate Context consumers additionally bind native event/projection and generator inputs. The composite API selects distinct original/custody/Source8/legacy Session hosts and a Machine transport. A v1 local session is not an all34 Action grant.

Use the [[source:v1-session|local Session]], [[source:context|ContextSession]] and [[source:api-session|captured API session source]] as version-specific responsibilities. The integrated current learning journey is unqualified; this page explains its prerequisites rather than advertising a successful end-to-end example."""),
 section('Obtain a usable context',"""A Context View binds selected sources, exact cuts/cursors, exclusions, intended use, validity and current policy. The native reader checks original event/executable/request/projection pins before and after a separate native process. Semantic and governance event cursors stay distinct from Project transaction history.

Assignment identifies the task. Permission still needs the real current Principal, allowed operation, scope, policy, nonce, budget and expiry. An opaque context locator, message Actor or copied view supplies no grant. Link [[concept:context|the canonical Context View]] and [[concept:authority|authority]] when those meanings need explanation."""),
 section('Keep the lifetime boundaries',"""A live Session holds a real resource and short memory. Its caller can use only the strictest current call/policy/Session/Context/source/reader bounds. Scope revocation, changed HEAD/source, expired context or exhausted budget stops use. Refreshing a view does not renew the grant or source period.

An API Machine peer binds to the actual still-live parent Session. An application Operator borrows an exact [[source:api-attachment|SessionAttachment]]; closing that borrower must not dispose the parent's credential/custody. A host restart cannot turn a public receipt into the original in-memory resource or signer.""",diagram('session-lifetime',"""flowchart LR
  S[Durable state and assignment] --> C[Fresh checked Context]
  P[Current policy and grant] --> L[Live Session resource]
  C --> L
  L --> U[Allowed bounded use]
  U --> X[Expiry / revocation / close]
  X --> E[Erase short memory and release signer]
  E --> N[New Session with fresh context]
  S --> N""","Durable Project State can support a new checked context. Current permission and context are both needed for the live resource. Close, expiry or revocation disposes short memory; a later session reconstructs knowledge rather than restoring that resource.",['v1-session','api-session','api-machine','api-attachment'])),
 section('Local v1 grammar and expected disposition',"""The admitted parser has session SUBJECT --ttl SECONDS, with interactive context, note TEXT, memory and close commands. EOF also closes it. --context-only exports a candidate packet and immediately closes the resource: that packet is historical preparation output, not an active credential. The v1 parser's default TTL is 900 seconds.

Use this route only with the independently selected source/store and current local authorization. The fresh inspection witness did not open a Session. A separate Session walkthrough, expiry/disposal observation and fresh reconstruction remain required for this handbook's successful session recipe."""),
 section('Understand the current failure',"""The [[source:measurement|actual learning measurement]] expired during lesson selection. It retained valid outer source/reader/call budgets, but the stricter Session/Context boundary had already ended. That is not permission to enlarge the period or replay the old resource.

The new margin adapter can refuse a tail before claim when empirical bounds are unknown or cannot fit. [[source:margin|Pure margin checks]] do not establish a real safe tail. Start a separately authorized fresh episode only after its selected implementation and current inputs qualify."""),
])

page('recovery','Recover and retry safely','Distinguish an absent effect, a committed outcome and uncertainty before repeating work.','how-to/recover-and-retry.md',[
 section('Select the state you are recovering',"""A v1 store recovers staged local transactions around an atomic HEAD commit. The API Vault journals candidate operation claims/material/results. Action has its own tool-effect/reconciliation boundary; Governance owns separate native commits. SQLite projections, exports and managed files are derived or external publications with their own guards.

Keep each store identity, owner, source cut, exact request and effect boundary. A timeout or missing final response does not prove no effect. Source/profile mismatches and expired permission do not authorize inspection of foreign private state."""),
 section('Follow v1 HEAD recovery',"""Read the selected store's status under current scope, then verify its committed chain. recover requires --expected-head with the exact digest from that store; do not substitute this handbook's D74 repository-inspection digest. The [[source:v1-store|original Store recovery]] preserves committed transactions and removes only recognized pending/staging material or an immediate uncommitted next transaction.

Unknown future transactions remain for inspection. Controlled process interruption on the observed local filesystem is the supported verification scope. Power-loss durability and multi-host consensus are not established. Rebuild a disposable graph only after source/HEAD freshness; a graph file cannot become replay authority."""),
 section('Handle API idempotency and pending effects',"""The exact key belongs to an authenticated Principal/authority/scope/operation namespace. Keep the original control-input fingerprint. Same-key changed bytes conflict. Completed retries return or locate their guarded historical result; pending or uncertain keys request inspection/reconciliation and do not automatically redispatch.

The [[source:api-workspace|captured Vault claim code]] looks up prior state under the original writer lock before fresh allocation. The reviewed margin gate belongs only to a new fresh application/assessment claim; it must not make an old recorded outcome depend on a new Session. Original source, authorization, cut, deadline and journal guards still apply.""",diagram('recover-effect',"""flowchart TD
  Q[Exact request and key] --> J[Inspect owned journal]
  J -->|Completed| R[Read guarded recorded result]
  J -->|Pending / uncertain| I[Operation inspection]
  I --> A[Authorized reconciliation]
  A --> C[Cold replay / exact observed outcome]
  J -->|Fresh and authorized| G[Current pre-effect guards]
  G --> E[Effect and durable evidence]
  E --> C""","Completed outcomes are read as history. Pending or uncertain outcomes require current owned inspection and authorized reconciliation before a new effect. A fresh request follows current guards, then records observed effects. The diagram does not authorize redispatch.",['v1-store','api-workspace','dispatch','api-dispatch'])),
 section('Preserve committed work when derived output fails',"""A committed native transaction stays committed if a later projection/export/file generation fails. Reconcile the selected output boundary instead of applying the transaction again. The [[source:publisher|mixed-target publisher successor]] stages ordinary filesystem/receipt behavior; its scoped controls are not proof of every native mixed-target admission.

The capture4 writer also replaces several metadata files source-last without a cross-file transaction. An interrupted replacement can leave mixed generations. Its reviewer flags that standing; Root must inspect and use exact retained preimages through a separately reviewed recovery. Do not call source-last publication atomic across files."""),
 section('What to retain',"""Retain permitted public request/result digests, exact selected version, observed phase/terminal, pending/committed posture, current authority scope and uncertainty. Never log private proof/key bodies or Session notes. Preserve unknown residue and failed candidates. Cleanup removes only exactly owned disposable objects whose retention decision is established.

The integrated full positive/security/recovery/native qualification is still pending. Use [[page:status|the dated evidence]] to tell an implemented recovery path from a current successful witness."""),
])

page('paperclip','Use Paperclip as a bounded Lab reader','Configure the pinned process adapter without confusing orchestration with Lab authority.','how-to/paperclip.md',[
 section('What has actually been observed',"""The pinned published Paperclip version is 2026.1005.0. A local process-reader episode was observed on 13 October 2026 through the independently selected wrapper/runner configuration. Its [[source:paperclip-witness|public closure]] records process success, zero Lab mutations and zero Lab Sessions. It read a historical genuine-W09 engineering source.

The earlier [[source:paperclip-runner|runner README]] says Paperclip was not installed when that package was authored. The later receipt records setup; neither statement establishes current server health. The recorded local endpoint was 127.0.0.1:3100, the old reader grant expired, and the human pilot/usefulness outcome remains unobserved."""),
 section('Keep the two authority boundaries',"""Paperclip company/agent/task IDs and its API token provide orchestration and correlation. Lab access comes from an independently provisioned current Lab policy, reader key, source/profile/plan pins and signed nonce proof. Do not put real private credentials or policy bodies into Paperclip task text, repository files or stdout.

The recorded agent could not create agents/skills or assign tasks, and used manual/on-demand scheduling. A process-adapter success is not a Work completion, an engineering tool effect, a research conclusion or repository admission. A future autonomous Work integration needs its actual workflow/tool/output/authority evidence."""),
 section('Configure only the inspected adapter contract',"""The [[source:paperclip-probe|published adapter probe]] selects an executable command with separate args, cwd and timeout, using direct process spawning. Do not paste a newer upstream shell-command example into this pinned version. A version upgrade needs its own compatibility review.

| Selected runner argument | Requirement |
| --- | --- |
| --api-root | Exact qualified API directory, not the currently changed/ineligible API17 |
| --source-sha256 / --profile-sha256 | Independently verified selected source and protocol profile |
| --policy / --policy-sha256 | Fresh isolated reader policy and exact digest |
| --reader-key / --reader-key-sha256 | Matching protected credential selected outside task text |
| --plan / --plan-sha256 | Exact bounded read plan |
| --timeout-seconds | Whole-episode bound, at most 900 seconds |

These are real runner flags, not a fabricated working configuration. The historic plan was limited to Lab status/catalog reads; the runner code supports additional bounded artifact reads only when its selected plan/policy permits them."""),
 section('Follow a fresh operator setup',"""First choose a qualified Lab reader and obtain a fresh scope/key/nonce channel. Run its exact approved command directly; preserve public observations and cleanup. Then configure Paperclip's process agent to run that same executable/argument selection from the selected repository cwd and compare results. Start a local server only under the accepted installation/service scope.

The current preparation provides no new credential, runnable server config or qualified integrated API. Old public config hashes and receipts cannot regenerate an expired grant. Keep persistent server/company state separate from temporary Lab credential roots; health, setup and Lab authentication need separate current checks."""),
 section('Assess usefulness with the pilot owner',"""The owner's question is how to use Paperclip to run the Lab; the agreed research question asks which evidence verifies that ability and what remains unproven. After a fresh technical setup, show the actual read output and ask the owner whether it answered those questions. Record time/failures and their own assessment without claiming improvement against an unattempted baseline.

Do not convert read-only process execution into autonomous engineering/research success. [[page:work-learning|Work and evidence]] explains the missing output/assessment boundaries; [[page:status|status]] retains the dated pilot limits."""),
])

page('packages','Packages, installation and rollback','Select exact public bytes and protect host dependencies before changing an installation.','how-to/packages-and-installation.md',[
 section('Choose the package boundary',"""A source package, a public export, an installed dependency/runtime and an activated consumer are different artifacts. The [[source:api-package-export|captured export]] and [[source:api-package-import|import]] implementations bind selected records/files and prepare bounded plans; they do not grant access to every source file or admit imported candidates.

Private credentials, policy/proof bodies, Session notes and protected host dependencies are not ordinary export material. Keep selected public source bytes, manifest/digest closure, original refs and intended scope explicit."""),
 section('Check exact bytes and current effects',"""Before export/import, resolve the declared record revisions, source/ontology cuts, permitted targets, request/envelope keys, byte bounds and current channel. A valid package envelope without its exact payload/hash/reference closure is insufficient.

Materialization and installation must compare actual preimages and refuse unsafe paths, foreign files and changed selectors. Preserve the original signed/native source trail separately from generated files. A changed publisher destination or dependency family requires a reviewed successor selection; do not rename a stale manifest to make it current."""),
 section('Separate install from activate',"""| Stage | Result and limit |
| --- | --- |
| Dependency package selection | Exact executable/library/wheel/environment input pins |
| Installation | Files exist in the selected owned layout and match expected modes/bytes |
| Verification/replay | Selected code can check the declared public/current inputs |
| Release preparation | Candidate package and readiness obligations recorded |
| Activation/publication | Separate authority and actual operational outcome |

The [[source:api-installer|R02 installer]] and [[source:api-release|release-readiness code]] own bounded development paths. The existing installation0004 supports this preparation's selected environment; its prior tests do not replace a fresh setup/upgrade/rollback witness for the final runtime."""),
 section('Rollback and interruption',"""Keep the prior installation and exact rollback dependencies until the new version has its own readiness and end-to-end acceptance. Inspect uncertainty after interruption before cleanup. Remove only retained-approved owned temporary files; foreign/unknown residue is preserved.

For local state, cold replay verifies original commits and current source bytes. For derived files, verify their source cut, manifest, selected attachment and complete receipt rather than trusting a directory name. The [[source:publisher|publisher successor]] illustrates ordinary filesystem no-replace and receipt boundaries, with native mixed-target integration still separate."""),
 section('Current blocker and next review',"""Changed API17 remains ineligible until new family/selector/software/source/profile closure is accepted. Its old metadata cannot qualify modified code. Family4's inherited mutable preparation inputs exposed a cycle; the [[source:cycle|retained diagnosis]] requires a distinct successor, not suppressed guards.

A later installation tutorial must select that final version, execute setup/recovery/rollback in fresh owned paths and record original effects/cleanup. None of those actions is run by this documentation generator. Read [[page:maintenance|maintenance]] for the full integration sequence."""),
])

page('architecture','Runtime architecture and ownership','Follow the executable paths and the independent stores they own.','explanation/architecture.md',[
 section('Two entrypaths',"""The admitted local CLI enters lab.py, then cli.main. With no selected store, read_data captures the frozen repository envelope; explicit init constructs a local store. Review/sign/apply/replay/recover and ephemeral Session are local store operations.

The captured Base stdio API enters serve.main and constructs a Base service after independent source/profile/policy/nonce checks. IntegrationService composes Base28, Action3 and Governance3 with the same Schemas object and independent authenticated branch contexts. A Base connection cannot advertise full34 readiness. The [[source:sdk|maintained composite candidate]] supplies a separately selected serialized launcher contract.""",diagram('components',"""flowchart LR
  CLI[Admitted local CLI] --> LS[Local transaction store / HEAD]
  CALL[Exact stdio envelope] --> F[Composite IntegrationService]
  F --> B[Base Service 28]
  F --> A[Action Service 3]
  F --> G[Governance Service 3]
  B --> W[Owned workspace journal]
  B --> R[Signed readers / native replay]
  R --> C[Context / ephemeral Session]
  A --> AJ[Action grant / effect journal]
  G --> GS[Selected native governance store]
  R -. derive .-> Q[SQLite / graph views]""","The CLI owns a separate local transaction store. The composite routes unchanged calls to three independently authenticated branches. Base workspace, Action effects and native Governance state are distinct; readers derive Context and disposable query representations.",['v1-cli','api-dispatch','api-service','host-authority','ontology'])),
 section('Ten implementation areas',"""| Area | Concrete responsibility |
| --- | --- |
| lab-runtime | [[source:v1-cli|CLI]], source selection, local transaction/replay/recovery, graph, Session |
| lab-provisioning | [[source:provision|Pinned scoped branch]] and configuration/HEAD selection |
| lab-bootstrap | [[source:bootstrap|Seed/package composition]] and controlled candidate changes |
| lab-integration | [[source:integration|Composition verification]], distinct from component admission |
| lab-review | [[source:review|Bounded review material]], not an actual owner decision |
| lab-context | [[source:native-reader|Native reader]] and [[source:context|generator/consumer]] |
| lab-ontology | [[source:ontology|Semantic/governance event replay]] and represented views |
| lab-continuity | [[source:continuity|Durable custody evidence]] without restoring live memory |
| lab-work | [[source:work|Bounded episode]] and public evidence/archive verification |
| lab-workflows | [[source:engineering|Engineering]], [[source:research|research]], [[source:host-authority|authority]], [[source:dispatch|dispatch]] and learning |

These are implementation responsibilities. Candidate carriers, actual effects and effective admission retain their own records."""),
 section('The call chain',"""The Base service verifies channel, byte/envelope/profile bounds, allowed operation, call ID, actor, strictest deadline, budgets, cut, domain schema and actual selected code. An effectful request claims an exact fingerprint/key in the owned Vault. Prior outcomes return before fresh allocation; pending outcomes are not redispatched.

Source selection names the actual source, reader, mapper, Context producer, package, Principal and period. Native replay verifies original histories; a mapper produces a source-bound projection; Context is generated under current policy; a live Session/Machine borrows only what its actual resource permits. No internal adapter nickname can replace those public identities."""),
 section('State ownership and dependencies',"""Local immutable transactions/HEAD, native event histories, private API journal material, derived SQLite/graph files and ephemeral Session RAM have separate owners and recovery contracts. The [[page:state-memory|state/authority/memory page]] follows those stores without drawing them as one database.

The selected interpreter/native/library closure is independent of code/source/profile selection. Full historical provenance and the narrower schema execution dependency table remain explicit; unavailable historical inputs are not silently aliased to current files. Fresh original guards remain required even when pure preparation reuses a scoped snapshot."""),
 section('Current integration standing',"""The eight API17 overlay leaves are reviewed code, not current all34 qualification. The old execution capture is ineligible. Family4's Source table bound future-changing API preparation files, so final publication would invalidate the family. The capture guard rejects that cycle.

A successor needs exact historical snapshot technical bindings and complete preserved native history/role/code proof. The driver4 private loader and margin component have scoped peer checks; no successful complete learning/empirical margin follows. See [[source:capture-flag|the capture flag]] and [[page:status|dated status]]."""),
])

page('work-learning','Work, evidence and operational learning','Trace the attempt, output, review, lesson use and assessed result.','explanation/work-evidence-learning.md',[
 section('Begin with the actual Work scope',"""Use the existing [[concept:work|Work definition]] and [[concept:learning|learning explanation]]. Operationally, select exact assignment, sources, expected outputs, permitted action kinds, budgets, tool/workflow contract and assessment criteria. Work is not satisfied merely because an agent ran or an artifact exists.

Engineering and research share source/current authority boundaries but produce different evidence. The [[source:engineering|engineering workflow]] binds implementation/output/action/Work postimages. The [[source:research|research workflow]] binds its predeclared method, inputs, observations and evaluation. A negative result or an open cause remains a valid bounded observation."""),
 section('Keep output and admission separate',"""| Observation | What it does not establish |
| --- | --- |
| Planned Work or WorkflowRun | An actual attempt or permitted Tool dispatch |
| Tool/process exit | Correct output, Work satisfaction or human usefulness |
| Exact output carrier | Repository admission or causal benefit |
| Local signed transaction | Organizational adoption or deployment |
| Proposed implementation/represented-subject mapping | An admitted carrier alias |
| Assessment evidence | A positive hypothesis or universal conclusion |

The [[source:workflow-review|preserved workflow review]] explicitly records kind/represented-subject coupling gaps and candidate boundaries. Later implementations need their own output-bearing transitions and actual native/consumer witnesses; coverage from different versions cannot be merged by count."""),
 section('Follow failure and challenge',"""Preserve the exact failed inputs/output, expected criterion, method, observed occurrence, manifestation/cause/impact/containment/recovery and uncertainty. A classification is not causal proof. A challenge refers to exact material and route; an agent's controlled contest is not the governing owner's response.

Candidate handlers can prepare linked observations, failure assessments and challenge records. Their returned posture and journal show the selected bounded effect. Canonical admission needs the actual independent governing transaction and source/cut proof."""),
 section('Select, apply and assess a lesson',"""A reviewed Lesson has applicability, exclusions, evidence, instruction precedence and an exact producer/implementation scope. Selection examines that inventory for the current assignment. Application records actual use or deliberate non-use of an exact lesson version. Assessment compares its prediction with later observed evidence.

The current Source8 route selects a conditional Lesson host and application implementation; the [[source:api-docs|historical API reference]] now documents both general and conditional routes. A completed candidate Application can be read through an independently scoped ApplicationJournal. That correspondence does not prove that the lesson caused improvement.

The original 900-second integrated path has no current complete apply/assess witness. Failed selection timing cannot supply an empirical full-tail reserve. Human satisfaction, product benefit and genuine governing acceptance remain separate from technical fixtures."""),
 section('What continuity preserves',"""Persist permitted public outputs and their exact provenance through the applicable recording route. Later Sessions obtain newly checked Context/Ontology Views and current permission; they do not recover the old private signer or notes. [[source:continuity|Continuity code]] verifies archives/replay rather than transferring lost live resource authority.

For the Paperclip pilot, the successful bounded read episode is evidence of reading/orchestration only. The owner's usefulness assessment and autonomous engineering/research Work are still missing. A reusable Lab needs those actual inputs and outcomes, not a larger catalog count."""),
])

page('state-memory','State, authority and short memory','Know which records endure and what a later process must recheck.','explanation/state-authority-and-memory.md',[
 section('Use the canonical meanings',"""This chapter applies existing [[concept:state|Project State]], [[concept:memory|Session Memory]], [[concept:authority|authority]] and [[concept:provenance|provenance]] definitions. It does not introduce another semantic model.

Runtime admission, a record's lifecycle, committed history, accepted meaning, action permission and an observed outcome remain independent. A message Actor may claim an identity; only the actual selected channel/grant/source checks can support that requested operation."""),
 section('Five storage boundaries',"""| Surface | What persists | Currentness/recovery |
| --- | --- | --- |
| Local runtime store | Config, baseline, immutable transactions and HEAD | Cold signed/semantic replay, expected HEAD and source freshness |
| Native ontology/governance inputs | Original event bytes and separate cursors | Native replay/projection joins and independently supplied pins |
| Private API workspace/journal | Owned request material, claim/result/effect evidence | Current owner/scope, exact fingerprints and guarded inspection |
| Derived SQLite/graph/files | Disposable source-bound representations | Rebuild/verify at exact source cut; no replay authority |
| Session resource/notes/signer | Process-bound temporary state | Expiry/revocation/close disposes it; no public receipt restores RAM |

The [[source:api-projection|SQLite generation]] checks its row/content/source bindings. It is an optimization of selected queries, not a replacement canonical database."""),
 section('Cuts and histories',"""Project semantic/governance event histories, native ontology cursors, source transaction HEAD and representation revisions use their selected namespaces. Joining them requires actual contracts and exact inputs, not a common-looking timestamp.

The admitted v1 executable reads D74 while repository admission is D75. An independently initialized local store begins from its chosen baseline and records its own subsequent scope. No store or executable is silently rebased when the repository adds a decision."""),
 section('Authority at every boundary',"""A policy/key/nonce channel identifies a current Principal and permitted operations. Views, graph nodes, source hashes, receipts and instruction advice supply information; they grant no effect authority. Before an effect, recheck source cut, expiry/revocation, gates, allowed scope and budget under the original lock where required.

Three composite branches authenticate independently. Catalog membership and a common Principal across policies do not merge permissions. Session opening does not create Action rights; a custody signature does not issue a new grant. [[source:sdk|The operator contract]] retains these independent boundaries."""),
 section('What happens when a process ends',"""Closing a borrower releases its own resources, not the parent's custody. Closing/expiring the Session erases its bounded notes and signer. Durable Work/evidence/history remains at its own posture and can seed a new checked context.

A public Session export is historical metadata. Source period, old signed grant and expired policy remain immutable history; a fresh instance needs a distinct current selection and permission. Host restart/replayed receipts cannot reconstruct the old live resource. The [[page:sessions|Session how-to]] and [[page:recovery|recovery route]] keep knowledge reconstruction separate from authority."""),
])

page('cli','CLI and environment reference','Look up exact parser surfaces and their selected source/environment limits.','reference/cli-and-environment.md',[
 section('Admitted v1 syntax',"""The entrypoint is implementation/lab-runtime/v1/lab.py; it imports that package's cli.main. Global --repo PATH and --store PATH precede the subcommand. Its default store is .local/lab-runtime/store, so public inspection examples explicitly choose a nonexistent store to avoid an existing operator branch.

| Command | Actual parser arguments |
| --- | --- |
| verify / status | No additional positional arguments |
| inspect | SUBJECT and optional --record |
| catalog | Optional --category definition/artifact-type/relation-kind/artifact-instance/typed-relation and --current |
| query | Optional ROOT, --direction both/incoming/outgoing, --depth, --max-nodes, --max-edges, repeatable --predicate |
| rebuild | Required --out; writes disposable derived output |
| keygen | Required --private and --public; private file must be outside repository |
| init | Required --id, --owner, --public-key; new store only |
| example / review | example --id/--out; review PROPOSAL |
| authorize / apply | authorize PROPOSAL --private-key/--out; apply PROPOSAL APPROVAL |
| recover | Required --expected-head |
| session | SUBJECT, optional --ttl and --context-only |

This table comes from [[source:v1-cli|the selected parser]]. Command existence is not permission to perform its effects."""),
 section('Environment and source selection',"""The v1 requirements are jsonschema >=4.23,<5 and cryptography >=43,<49. The first walkthrough selected existing isolated Python 3.14.4/dependencies0004 with explicit dependency/v1 import roots. Its proof does not establish a fresh installation. Select the whole [[source:deps|dependency declaration]] independently rather than trusting the interpreter filename alone.

v1's [[source:v1-profile|source profile]] selects D74. v2's [[source:v2-profile|separate candidate profile]] selects D75 and a distinct default store. Never use a v2 profile to relabel an existing v1 branch. The [[page:first-inspection|first tutorial]] defines its local shell convenience and three actual reads."""),
 section('API and SDK are different interfaces',"""The captured API has LF-terminated UTF-8 JSON envelopes, request/result/error schemas, exact selected profile/source, independent challenge/proof and live context. It does not accept CLI subcommands like init or a fabricated universal lab run command.

The candidate [[source:sdk|composite launcher]] takes independently selected launcher/config hashes and a protected canonical configuration. It is serialized stdio, not a network service. All Base/Action/Governance branch inputs/proofs and a same-process fresh Action lease/handoff are prerequisites. Its focused controls do not prove full34 readiness.

The [[source:api-docs|34-operation reference draft]] looks up declared effects/errors/deadlines/keys/readiness and exact conditional implementation sources. It is historical and unqualified for changed API17.""",diagram('read-sequence',"""sequenceDiagram
  participant U as Selected caller
  participant C as ReaderChannel
  participant S as Selected service
  U->>C: Current policy and independent credential selection
  C->>U: Fresh nonce challenge
  U->>C: Exact signed proof
  C->>S: Trusted current context
  U->>S: Bounded exact envelope and source cut
  S->>S: Current source/schema/permission/deadline checks
  S-->>U: Bound reply and domain posture""","This is the API candidate read sequence, not the key-free v1 repository-inspection tutorial. Policy/key/nonce establish the trusted context; the service checks exact source/cut/bounds before replying. A reply still needs posture assessment.",['api-auth','api-schema','api-service','api-dispatch'])),
 section('Limits and safe failures',"""Input/output/line/frame/call budgets belong to the selected interface/policy. Composite startup is independently bounded from 1 to 300 seconds; it does not extend a grant. The pinned Paperclip runner's whole episode limit is at most 900 seconds. Source fixture 24-hour periods, reader grants and 900-second Session limits are independent clocks, not interchangeable defaults.

Distinguish malformed contract, unauthorized context, source integrity/stale cut, deadline/budget exhaustion, ambiguous/unresolved reference and pending/recovery-required outcomes. Preserve exact input/result hashes and public class/code location; private args/locals/proofs stay out of diagnostic output."""),
])

page('maintenance','Develop and maintain the runtime documentation','Keep implementation, evidence and the rendered edition synchronized without rewriting history.','development-and-maintenance.md',[
 section('Maintain one narrative source',"""This owned preparation uses narrative.json as the editable prose and source-map.json as its exact public evidence selection. A standard-library generator supplies HTML fragments, shared-shell preview pages and a Markdown mirror from those same section bodies.

The proposed maintained destination is website/source/governance-lab-series/runtime; the shared article renderer supplies the existing documentation shell. Imported docs/lab/runtime pages remain a projection. Directly maintained indexes link to them. Do not edit generated HTML/Markdown as competing prose sources."""),
 section('Follow the actual pipeline',"""The [[source:site-build|website builder]] stages maintained sources, renders examples/essays/reference/articles, applies presentation and approved editorial wording, finishes the site, generates final search, runs checks and packages the closure. It does not silently refresh source capture or import Markdown.

The [[source:importer|stdlib importer]] selects explicit source HTML/article/anchor routes, rewrites links, copies permitted assets and writes an import manifest. Root must add the14 explicit runtime routes, actual source-note packaging and navigation/search judgments. The [[source:site-maintenance|site instructions]] and [[source:docs-maintenance|Markdown maintenance]] retain that ownership.

The proposed fragments have section IDs/h2 headings and the start-content/start-masthead/source-notes conventions. Preview uses the existing local assets and canonical concept destinations; it is not a separately published website."""),
 section('Review source and behavior together',"""| Changed input | Required review |
| --- | --- |
| CLI argument/default | Exact parser/README/profile selection and isolated example |
| API schema/resource/remapping | Actual registry precedence and contract/source fields |
| Source/reader/mapper/Context implementation | True origin/period/history/role/full byte closure |
| Authentication/expiry/idempotency | Current channel, exact key/fingerprint, refusal/recovery |
| Installation/publisher | Owned paths/preimages/receipts/uncertainty and meaningful replay |
| Evidence/status | Exact dated receipt, actual terminal/cleanup and claim ceiling |
| Narrative/navigation | Same-source HTML/Markdown, links/fragments/portability/editorial/search |

Frozen implementation notices, unsuccessful attempts and historical receipts remain byte-preserved. A prose update does not supply a new admission, source epoch or runtime qualification."""),
 section('Do not hide the current composition gap',"""Family4's code exists and its partial Source diagnostic remains preserved, but it is ineligible for final runtime. The [[source:cycle|causal review]] shows six inherited preparation-only API inputs in its current role table. Final publication would change the manifest and four selector leaves; current_machine_context_scope is byte-preserved, but that does not remove the cycle.

A reviewed immutable successor must conserve all349 original declarations, select exact historical snapshot technical bindings for those preparation inputs, preserve all original Source/history/signature/guard/period checks and prove closure before another Source build. The [[source:capture-flag|capture review]] preserves its passing preparation checks without suppressing the blocker."""),
 section('Acceptance still required',"""This generator can check14 names, five diagram/text equivalents, exact public evidence hashes, command grammar, body identity and owned local links. It cannot prove user comprehension, fresh installation, effectful Work, Session disposal, integrated full34 behavior or empirical margin.

T21 completion still depends on T15/current qualification, final setup/recovery walkthroughs, actual website/editorial/render/search/import integration, final link/body-preservation checks and review of the exact resulting edition. No shared renderer/build/importer, website/dist, live service or private state is changed by this preparation."""),
])

def main():
 assert len(PAGES)==14 and len({p['markdown_route'] for p in PAGES})==14
 bindings={}
 for key,name in SOURCE_PATHS.items():
  source=ROOT/name
  assert source.is_file() and not source.is_symlink() and not any(p.is_symlink() for p in source.parents),(key,name)
  raw=source.read_bytes();target=HERE/'evidence'/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write(raw)
  bindings[key]={'original_path':name,'snapshot_path':target.relative_to(ROOT).as_posix(),
                 'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),
                 'scope':'Exact public source/evidence snapshot for documentation only; no identity, authority or qualification transfer.'}
 assert bindings['first-witness']['sha256']=='555ad9970fcd382f54dbe354d3996523cc613524f9f71f5e1f966c34e3a38e51'
 assert bindings['cycle']['sha256']=='b9b282170bb00e2c0a105c16add8596444e69b9a84a51fefb80b36144269df14'
 value={'schema_version':'lab-T21-runtime-narrative/v1-candidate','authority_effect':'none',
        'captured_on':'2026-10-14','task_complete':False,'pages':PAGES,'code_blocks':{'read-command':READ_COMMAND}}
 source_map={'schema_version':'lab-T21-runtime-public-source-map/v1-candidate','authority_effect':'none',
             'source_bindings':bindings,'canonical_concepts':CONCEPTS,
             'claim_ceiling':'Public selected code and scoped observations; no live probe or final T21/runtime/release qualification.'}
 for name,data in [('narrative.json',value),('source-map.json',source_map)]:
  with (HERE/name).open('x') as f:json.dump(data,f,indent=2,ensure_ascii=False,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'AUTHORED-owned-narrative','pages':len(PAGES),'public_snapshots':len(bindings),'runtime_executed':False}))
if __name__=='__main__':main()
