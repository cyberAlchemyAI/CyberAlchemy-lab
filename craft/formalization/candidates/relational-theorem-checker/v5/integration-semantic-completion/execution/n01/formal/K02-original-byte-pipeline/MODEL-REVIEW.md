Original relation byte-entrypoint review

The new entrypoint reads the original Intent Resolution record and its relation
qualifiers from captured bytes. It no longer accepts an unrelated caller-supplied
JSON tree. It preserves the complete original record, exact frame, metadata joins,
payload roles, resolution and addressing-role checks. It also refuses a source
revision whose digest differs from the verified source capture digest.

For example, the existing 1208-byte Intent Resolution fixture selects a project
and a goal, retains an excluded subject and two satisfaction tests. The new path
parses those original bytes and runs the original full pipeline. A coherent
synthetic metadata/claim/world context using the actual source hash succeeds.
The old fixture context with its placeholder revision digest is refused. This
success does not establish real ownership or authenticate those synthetic roots.

The main theorem `CandidateOriginalBytePipeline.run_exact` states an equivalence:

    run(original captures, original typed contexts) = ok(output)
      iff
    combined supplied-capture budget holds
      AND every supplied capture passes independent preflight meaning
      AND exact source bytes parse to the source AST
      AND exact qualifier bytes parse to the qualifier AST
      AND original IntentSourcePipeline.Meaning holds
      AND output resolution digest equals the verified original source digest.

Independent scalar-byte parsing uniquely determines the ASTs. The meaning above
does not call the new executable. Batch certificates preserve the entire ordered
capture list, including every duplicate occurrence. Budget refusal and successful
batch preparation are also characterized exactly.

The policy bridge changes only `parses` in the original nineteen-slot source-policy
record. It proves that supplying the other eighteen actual premises produces the
original full SourceInterpretation. It separately proves that this parser bridge
cannot supply authentic metadata. It is a conditional theorem, not a realization
of those ownership, lifecycle, evidence or other provider policies.

| Gap | Result here | Remaining requirement |
| --- | --- | --- |
| Caller AST unrelated to original bytes | Closed on this entrypoint | Enforce its use at consumers |
| Source revision placeholder digest | Refused; exact digest join required | Authenticate ownership of the revision/profile |
| Source and qualifier omitted from resource budget | Closed for supplied batch | Complete manifest of every consumed capture |
| Supplied unused/duplicate catalog captures bypassed | Every occurrence checked and retained | Decode captures into exact typed catalogs |
| Original policy requirements lost during composition | All eighteen remaining slots preserved | Real evidence for those premises |

Four new source modules were compiled and replayed in separate build directories:
eight fresh new-module calls, twenty-eight declaration axiom inspections, eight
exact import audits and twelve runtime controls per phase. The 121 unchanged
dependency modules were verified against exact registered source/output bindings
and their matching phase outputs reused. They were not rebuilt. The replay uses
the same Lean kernel and is not independent checking. Build durations are not a
measured operational time or memory envelope.

The twelve runtime cases cover original success, duplicate supplied catalogs,
count and combined-byte budget refusal, invalid source length, malformed qualifier
digest, invalid catalog JSON, excessive unused catalog numeric exponent, malformed
qualifier shape, placeholder source digest, changed source shape and changed frame.
No caller-controlled authenticity flag is introduced.

Still missing: complete catalog manifest coverage, exact raw-to-typed adapters for
metadata/payload/owned qualifier catalogs, binding the chosen digest profile to the
verified profile-selection result, real authentic-root/source policies, mandatory
consumer integration, whole-theory countermodels, independent checking and measured
limits. The full seven-extension and twenty-task plan remains incomplete. K04/global
reviews remain pending, all 263 inherited IDs remain open and 90 original discharges
keep their original scope. This package contributes no inherited discharge.
