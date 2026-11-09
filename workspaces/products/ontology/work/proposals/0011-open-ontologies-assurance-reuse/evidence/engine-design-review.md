# Engine-design review

Reviewed read-only:
- docs/proposals/0011-open-ontologies-assurance-reuse/ARCHITECTURE.md
- CODE-REUSE.md
- INTERFACES.md
- VALIDATION.md
- examples/preserve-batch.json
Also checked PROOF-PROFILES.md and PROFILES.json to assess the change-profile contract.

Verdict: PASS WITH TWO CONTRACT GATES. The selected whole-source/standalone-batch approach is feasible at design level and preserves accepted Lab code. No build, install, test or implementation-readiness claim is made.

## Gate 1: Make plan temporary output part of the owned job

INTERFACES.md:67-78 says plan writes candidate metadata only to the owned SQLite directory, and specifies a private environment without naming the temporary-root variables. The unchanged upstream plan also creates certificate output under std::env::temp_dir()/oo-plan-conservativity-PID (upstream src/batch.rs:1187-1194). With normal inherited temporary settings that is outside the owned job. --data-dir does not control it.

Required design clarification:
- Resolve TMPDIR/TMP/TEMP as appropriate for the supported target to an explicitly created owned job subdirectory; fix CWD and relevant config/home paths.
- Bind that environment selection in the invocation record.
- Capture/hash the conservativity certificate subtree in addition to the JSON and SQLite outputs before publishing evidence.
- Add a control that runs a plan with a deliberately different ambient temporary root and verifies that all resulting artifacts remain under the owned job. A failure must refuse the job, not silently omit certificates.

This is a concrete output-location issue, not a request for a new filesystem sandbox. The design correctly keeps same-privilege host tampering as a stated assumption.

## Gate 2: Specify the unchanged batch plan's replacement ABI

PROOF-PROFILES.md:131-135 calls the first conservativity question additive and speaks of one selected rule profile. The actual unchanged batch plan always takes a WHOLE proposed graph and fixes ExtensionMode::Replacement, profile owl-rl, scan_rows=10000 and max_rows=1000000 (upstream src/batch.rs:1174-1203). It does not accept a delta mode, configurable rule table or configurable scan cap.

Required design clarification:
- If the public request contains additions Delta, the adapter constructs and binds full proposed G union Delta before generating the plan command. Alternatively, the request must already name the exact complete proposed graph.
- The adapter independently checks source-subset/full-target correspondence. Never hand a delta file to plan as though it were a full replacement.
- Fix RDF-CHANGE-RL1 to the actual owl-rl batch behavior and record the effective scan/render limits. Unsupported requested rule tables/caps must be refused, not forwarded as ignored flags.
- Distinguish “full graph supplied as transport” from “semantic change deletes assertions.” A full replacement file containing every old assertion can still describe an additive extension.
- Add paired controls: an additive delta normalized to a full target succeeds at the intended question; the same delta incorrectly submitted as a replacement is detected rather than analyzed as the intended extension.

This does not require changing upstream Rust code or replacing its conservativity logic. It makes the Lab adapter accurately use the reused interface.

## Verified correct boundaries

1. Cargo root and fork:
CODE-REUSE preserves the entire main Rust source/build unit as its own Cargo root, original lock, empty optional features and exact Oxigraph fork rev 37db8e1522585ed2f9aa994be6c5c716859af5c8. This avoids the dependency-level patch trap. Implementation must verify actual Cargo workspace/root metadata and lock resolution as already required.

2. Batch request:
The example JSON array shape and command/args objects match BatchRunner input. preserve flags --projection, --goals, --profile, --out, --checker and --require-checker match src/batch.rs:762-819. --no-connect --data-dir JOB --json batch - --bail matches CLI construction and keeps load plus analysis in one process. NDJSON command envelope/status/exit parsing is correctly specified separately.

3. Checker discovery:
Explicit checker paths and private OO_CERT/OO_HORN are required. This covers the conservativity helper's checker:None behavior. Binary pins are independently resolved, not submitted by the caller or accepted from self-identification. Native checked status and independent Lab verification are kept separate.

4. Source export:
The design uses per-agent owned captured exports and a distinct RDF interpretation bridge; it does not ask a shared mutable OO graph to serve as canonical Lab state. Ground named identities, no implicit blank nodes/n-ary lowering, exact reviews/source versions, closed endpoint checks and explicit unknown refusal are correct first-profile limits.

5. Lab supervisor:
The proposal recognizes that v3's run-root and E00-E06 receipt/profile constraints are fixed. A reviewed successor copy with ownership/import/schema changes is correctly required rather than modifying accepted code or reusing an old issuer.

6. Evidence strength:
The proposal distinguishes source fidelity, encoded model checking, model existence, positive derivation and fresh exact kernel proof. Existing finite witness and universal/minimum-strength checks remain in force. The required set is resolved independently. Successful native process exit is explicitly insufficient.

7. Accepted-code protection:
Old finite and E00-E06 source, receipts and cached imports remain unchanged; new sources, bridges, builds and evidence have separate owned homes. Actual source copying/building remains a future implementation gate.

## Other nonblocking implementation checks

- Preserve reports with asserted membership may have no goal-specific inference certificate; keep asserted membership distinct instead of fabricating a theorem.
- --bail stops on error or stop-the-line, not every semantic nonzero result. Check the full expected command ledger and native domain outcome, as INTERFACES already requires.
- OO closure identifier FNV remains noncryptographic; manifest and invocation integrity use external SHA-256, as PROOF-PROFILES already states.
- Keep checker missing/unreadable/rejected separate. A checker rejection cannot be downgraded into an acceptable unchecked result.
- Required hard-memory mode must fail before work when unavailable; sampled RSS stays advisory.
- Retaining broad upstream tests is not proof of their fixture closure or execution. The proposal's explicit target selection and missing-tool gates are appropriate.

No other material flaw found in the reviewed engine/copy/supervision portion.

