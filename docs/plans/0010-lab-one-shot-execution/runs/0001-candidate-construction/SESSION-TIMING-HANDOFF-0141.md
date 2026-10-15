# Session verification diagnosis and live continuation

The unmodified original expiry test completed under `cProfile`: FAIL, one actual
method, full source exit guard completed. The observation contains function
timings, test failures and public reply metadata. It inspects no function locals,
private keys or Session RAM. The profiled run returned `integrity-failed`; the
earlier unprofiled regression returned `indeterminate`. Instrumentation changes
runtime cost, so these results establish distinct observations.

The largest measured costs included 364,552 original-file reads, 266 source
verification calls, 70 producer package checks and 31 policy-guard calls. The
two actual public Service calls consumed about 386 seconds of the profiled run.
These counts support investigation of redundant checks within synchronous pure
read scopes. They do not justify changing the original 70-second test, bypassing
actual current permission/expiry checks, replacing callbacks or retaining source
and authority facts across calls or effects.

The next successor should consolidate repeated immutable source verification
only inside explicitly sealed read scopes. It must preserve full original
source checks at scope entry/exit, independent live policy and clock checks,
original record/schema/revision witnesses, source/model callback identity, and
the prohibition on effects inside a pure scope. Requalify the original failure
and affected source-corruption, expiry, termination and mutation refusals.

API96 worker 0 completed PASS: all 43 original Preparation methods, no failures or
errors, full source exit guard completed. The sequential first-class observation
is FAIL: 33 passes and the real expiry failure. Other class workers remain live;
the aggregate cannot be PASS with that known failure.

R03 progress receipt `api-integration-v2/receipts/R03-0140.json` is linked to the
run as partial construction evidence. Currentness recheck completed PASS: 36/46
tasks, 38 active receipts, 77 original preparation files, 887 original sources,
no mismatches. The goal and R03 remain incomplete.

An additional actual Paperclip adapter-to-Lab runner qualification is now running
in tool session **61115**, PID obtainable from its command line. It invokes the
published `process` adapter in the temporary package inspection directory with
an owned metadata-only Lab policy and an ephemeral private credential. No server,
company or external API is selected. Its log is
`Paperclip-adapter-Lab-qualification-0141.log`; its derived terminal report is
`Paperclip-runner-qualification-0141.json`. Resume this same process and preserve
its result, whether passing or failing. The package inspection source and npm
dependency directory remain under `/tmp/cal-paperclip-package-inspection-0140`.

Workflow qualification session **25258** and the seven other regression workers
listed in `FINISHING-AUDIT-0140.md` were still running at this handoff. Do not
duplicate those runs. Session timing diagnosis **67678** and worker 0 **43550**
are terminal. The correct ARE continuation input is saved in the tool-session
store as `continue_request_0140`; its non-authorizing gate is consistent with
the existing candidate-development authorization.

The nine missing API operations, positive current Lesson/Context/Machine
qualification, human R05 journeys, R06 privacy, R07 acceptance, S02 exact final
assembly and actual R08 owner response remain required. The original reader
profile has no tool authority. Preserve all frozen histories, private/live state
and unrelated tracked changes. No new permission or fabricated owner outcome
has been inferred from the Paperclip setup response.
