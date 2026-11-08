# Generic business source: generate and run a decision

## Start with the installed tools

The public core package includes a complete claim-free Rule example under
`examples/generic-rule`. After installing both downloaded CLI archives into a
new npm project, copy and run it:

```sh
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-rule/. .
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --rule ReviewDesk.IsVerified --out generated --accept-local-review my-rule
node exercise.mjs
```

Use Linux x64 and Node 26.8.1 for the currently tested path. Generation requires
a new output directory. `exercise.mjs` imports the actual generated module,
checks true and false results and confirms that malformed input rejects. Its
business condition is declared entirely in `business.alch`; no formal claim is
required. The example README explains installation and the three input files.

The full Craft guide ships at
`node_modules/@domainspec-v2/cli/docs/GENERIC-APPLICATIONS.md`. It describes the
cumulative syntax, checked HTTP profile selection and public Workflow startup.
For the separate declarative application-profile commands, see
[profile generation](PROFILE-GENERATION.md). Each path requires a profile that
explicitly admits its capabilities.

## Continue with calculations and collections

The bundled `examples/generic-decision` project combines a Rule, pure Operation,
Mapping, Calculations, Policy, validated values, bounded collections and a State
Machine proposal. In a separate consumer project with both tools installed:

```sh
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-decision/. .
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --operation ReviewDesk.ApproveRequest --out generated --accept-local-review my-decision > generation.json
node exercise.mjs
```

The exercise checks filter/map/fold results, stable multi-key natural sorting,
priority selection, state proposals, explicit rejection and arithmetic failure.
All calculations are declared in the source. Its README explains how the concepts
compose and how to regenerate into a new directory. This pure profile returns
computed data; persistent effects require their separate admitted profiles.

## Continue with a protected API and SQLite

The bundled `examples/generic-http` project extends the decision with protected
Entries, a real SQLite transaction, checked GET/POST profiles and command replay.
In a separate project with both tools installed:

```sh
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-http/. .
npx --no-install alchlang-generic generate --source business.alch --profile contracts/selected-profile.json --http-profile contracts/http-profile.json --entry ReviewDesk.CommitRequestApprovalEntry --out generated --accept-local-review my-api > generation.json
node exercise.mjs
```

The driver invokes the generated handler directly. It checks unauthenticated
rejection, authorized approval, persistent state and replay without starting a
server. Its README distinguishes generated business behavior from isolated Auth
fixtures and host configuration. Permissions remain declared with each Entry.

## Export a formal model when useful

For the small `generic-rule` project, optional export uses the same source and
bounded-values profile as code generation. No claim is needed:

```sh
npx --no-install alchlang-generic formal-export --model smtlib2 --source business.alch --profile profile.json --rule ReviewDesk.IsVerified --out formal-smt --accept-local-review my-rule
```

Inspect `formal-smt/model.smt2` and its manifest. This produces established-language
model text; it does not run a solver, TDE or EVF. Unsupported model/profile
combinations reject explicitly. Ordinary generation remains available without
claims or a model export.

## Historical construction notes

The C01–C08 notes below retain their original source-development commands,
repository paths and historical test results. They do not describe the current
archive contents or establish completion of the complete application matrix.
Use the installed starter above for the first Rule example.

The source CLI has a cumulative development path for business-only `.alch` input, explicit authored `contracts/bounds.json`, and a checked Node ESM profile. C01 generates a Rule; C02 composes that Rule inside a pure Operation. The compiler creates the technical application root and delegates to the actual Core source, semantic and native owners. Formal claims are not required.

The full example and commands live in the Core guide: `craft/projects/domainspec-v2/impl/cli/docs/GENERIC-APPLICATIONS.md`. The ready-to-copy input project is `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C01/`. All paths are repository-relative.

Run `src/generic-composition-cli.ts generate --source FILE --profile FILE --rule MODULE.RULE --out NEW_DIRECTORY --accept-local-review OWNER` through the pinned development tsx loader. Explicit local acceptance is recorded against the captured review digest; the owner string is not an authenticated approval. Generated `rule.mjs` executes outside the checkout using Node builtins, with JSON byte input/output and separate Boolean results versus typed failures. This is source-CLI qualification, not installed archive qualification.

## Add the Operation

For C02, copy `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C02/`, select the profile's explicit `Operation` capability, and replace `--rule MODULE.RULE` with `--operation MODULE.OPERATION`. Select exactly one target. Generated `operation.mjs` has the same byte-oriented `evaluate` API. Its decoded business outcome is `Returned`, `Rejected` or `Failed`; evaluator errors remain `ok:false`. The Core guide explains the wire shape and includes a complete command. C02 supports guards, conditionals and explicit return/reject/fail with Rule calls; local let, Operation calls, callee error handlers and effects reject before output.

## Add the Mapping

The C03 tutorial at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C03/` extends the same Operation with an authored Mapping. The explicit `Mapping` and `record-uint64` profile capabilities add flat Bool/UInt64 projections and constants. Field assignments run in source order; preserve copies precede explicit fields. UInt64 wire values are decimal strings. Select `--mapping MODULE.MAPPING` for standalone `mapping.mjs`, or keep the Operation selector for the complete Rule → Operation → Mapping example. See the Core guide for syntax, ordering semantics and error boundaries.

The generated graph separates executable behavior from source provenance: `mapping_semantics_sha256` covers lowered pure semantics, `executable_semantics_sha256` adds the checked Operation behavior, and `projection_sha256` records source and assignment trace. Use the generic executable identity when comparing this profile's ordered execution; the legacy semantic identity retains its original meaning.

## Add Calculations and a Policy

The qualified C04 tutorial adds an amount and score to the same request and decision. `PriorityScore` calculates amount plus ten, `BaseScore` returns the amount, and the declared `SelectScore` Policy chooses between them. The Mapping calls that Policy for its score field. With amount `"30"`, a flagged verified request produces score `"40"`; an unflagged request produces `"30"`. The Rule still controls the Operation's rejection.

Copy `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C04/` and retain the Operation selector. Its profile adds Calculation and Policy explicitly. For standalone generation, use `--calculation MODULE.CALCULATION` or `--policy MODULE.POLICY`, selecting exactly one target. The Core guide owns supported arithmetic, ordering and error boundaries. C04 passed its 162-case cumulative independent run and review; see the implementation PROGRESS.json for exact receipts.

## Add collections and validated values

The qualified C05 tutorial at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C05/` extends the same source chain with validated items, filtering, mapped scores, a folded total and stable sorting. It includes the actual business.alch, profile.json, contracts/bounds.json and input.json. Keep `--operation ReviewDesk.ApproveRequest` to generate the complete example; the source declares every Calculation and Policy that it calls.

This profile adds `bounded-values` and `bounded-collections` with the separate generic computation/bounds versions documented in the Core guide. The Core guide also defines append capacity and evaluation order, invariant rounding, structural uniqueness, Optional restrictions and the distinction between Unicode bounds and finite patterns. C05 passed 261 cumulative independent tests on source freeze002, and its generated Operation executes outside the checkout. Qualification covers the source SDK/CLI and portable generated output; installed archives and later stateful capabilities retain their own stages. Exact receipts are linked from the implementation PROGRESS.json.

## Add a state proposal

The qualified C06 tutorial at `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C06/` adds a declared StateMachine to the same source chain. Its Mapping includes the proposal returned by `ProposeApproval`; the earlier collections and Policy remain in the result. The exact profile adds `StateMachine`. Use `--operation ReviewDesk.ApproveRequest` for the complete chain or `--calculation ReviewDesk.ProposeApproval` for its proposal Calculation.

The Core guide explains first-match guards, explicit fallback, terminal self-transitions and the zero-intent proposal wire. A proposal does not store a new state, and `initial` does not reset supplied state. C06 has 52 passing independent checks on source freeze001, composed with 261 predecessor passes from the preserved cumulative run on that same source. The sole first-run failure was an async assertion around a synchronous rejection; its reviewed correction changed no product source. The tutorial's generated Operation also passed five outcomes outside the checkout. Direct Calculation and otherwise-reject coverage comes from the independent suite. Installed C06 archives remain unqualified.

## Select a protected stored-read entry

C07 adds `Entity`, keyed `Query` and entry-local permission declarations to the same business model. Its read-only wrapper calls a protected Query and passes the returned Request into the existing approval Operation. The current source CLI accepts `--entry ReviewDesk.ApproveStoredRequestEntry` with the exact keyed-query profile. The Core guide contains the declarations and their meaning; the full candidate is in `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C07-005/`.

Generation produces an application adapter, captured model, storage description, business graph, system graph and bridge. The adapter uses the installed Core SDK and requires fresh source reconstruction and explicit local review. Each invocation must also satisfy actual entry permissions. Test setup uses the separate testing API; it does not provision production access.

C07 has a fresh 462/462 cumulative source pass, a separate 34/34 installed package pass for epoch-C07-003, and an accepted installed tutorial result. The complete tutorial project retains those exact executable inputs with updated prose. Invocation took about 383 seconds in the selected environment; correctness qualification does not establish practical latency. This read milestone does not yet supply HTTP transport or business writes. Local hosting, TDE, EVF and publication remain deferred.

## Commit through the same entry model (C08 candidate)

The C08 candidate extends the C07 stored-read application with an authored transaction. `CommitRequestApproval` reads the complete Entity through its protected Query entry, invokes the existing approval Operation and uses `ApplyDecision` to write the proposed state. Permissions remain beside each entry declaration. The Core guide shows the complete transaction declaration and explains conflict, rollback and command replay behavior.

The complete candidate project is `implementation/craft-alchlang-generic-applications-2026-10-18-r5/tutorials/C08-candidate-003/`. Select its exact transaction profile and generate with:

```bash
alchlang-generic generate \
  --source business.alch \
  --profile profile.json \
  --entry ReviewDesk.CommitRequestApprovalEntry \
  --out generated \
  --accept-local-review C08-local-tutorial
```

This invocation has passed against the source CLI. It is the intended installed command after C08 archives are qualified; the current C07 archives do not support this transaction profile. Generation emits the application adapter, captured model, storage schema and business/system/bridge graphs. The host later supplies real authentication and a stable `client_key` to the generated command API; local generation review does not grant runtime access.

The profile supplies hidden revision and journal structure. Repeating the same subject/entry/key/payload returns the recorded decision after current permission checks. Reusing that identity with a different payload is a conflict. Authored business requirements, types, Mappings, entry permissions and optional formal claims remain user inputs; the generated runtime owns transaction execution. The tutorial scripts provide test setup and assertions rather than a handwritten business simulator.

## Export optional formal models from the source CLI

`formal-export` is an optional command on the development source CLI. It takes the same original `.alch` source and selected profile as generation, requires a fresh `--out` directory, and records its local review decision inside that directory. It does not run a solver, and ordinary `generate` still works without formal claims. From the Core CLI package directory, use its installed `tsx` loader:

```bash
ALCHLANG_DOMAINSPEC_PACKAGE_ROOT="$PWD" node --import tsx ../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts \
  formal-export --model smtlib2 --source /absolute/project/business.alch --profile /absolute/project/profile.json \
  --rule Logic.IsVerified --out /absolute/project/formal-smt --accept-local-review local-reviewer
```

Select `--model smtlib2` and `--rule` for a bounded pure Boolean Rule; `--model tla+` and `--workflow` for a checked Event Workflow; or `--model alloy` and one or more `--artifact-entry` values for selected emitted service Entries in a checked stateful application. Stateful sources may also need `--additional-source`, `--external-profile`, and `--external-write-selection`. The output contains `model.smt2`, `model.tla`, or `model.als`, plus `model.json`, `manifest.json`, and `decision.json`. Alloy output also contains the original emitted service artifact inventory under `artifacts/`. Unsupported model/profile combinations fail explicitly. These are bounded model exports tied to the selected source and profile; they are not solver results or a proof that generated code meets every authored claim.

C08 source/SDK/CLI/type checks have bounded independent acceptance. Runtime smoke outcomes are implementation evidence only; independent concurrency/fault/recovery tests, joined archives and installed tutorial execution remain pending. Performance is also unresolved. See the Core guide and implementation progress for the exact current qualification.

## Checked HTTP profile selection and public Workflow startup

The current CLI supports --profile contracts/selected-profile.json together with
--http-profile contracts/http-profile.json for Entry generation. Both profiles
are independently recaptured by Craft. The earlier --profile HTTP form follows
only its exact declared application_profile reference; selecting both forms
rejects. formal-export accepts the same HTTP option for admitted stateful models.
Ordinary code generation does not require formal claims or model checking.

Accepted generated application owners now expose openWorkflow. Hosts supply
original producer/receiver runtimes, Entry actors and a private journal directory
with create or reopen mode. Craft derives the journal binding and compatibility
from the checked Workflow. Users do not import private journal classes or write
semantic binding hashes. UTF-8 JSON bytes enter scheduleStart; current Entry
authorization and generated business operations still control effects. Closing
the driver releases its journal before the host closes its runtimes/Auth.

Current construction checks cover genuine process termination at provider and
post-ACK windows using this public API, including clean-installed archives.
These checks do not close the full C01-C15 matrix or qualify distributed hosting.
See the Craft generic guide for the full openWorkflow example and limits.

## Open Questions

See the Core guide and the reviewed r5 cumulative plan. The full cumulative and independent-application matrix remains unfinished; general performance and platform qualification remain open. Current completion evidence is in the r5 implementation PROGRESS.json. Local hosting, TDE, EVF and publication remain deferred.

Ordinary `generate` and optional `formal-export` now use bounded physical intake followed by Core semantic admission for selected transaction and Event profiles, including checked external-read `on-malformed` handlers. The older AlchLang frontend parser remains in the pure and keyed paths; grammar parity across all profile modes remains open.
