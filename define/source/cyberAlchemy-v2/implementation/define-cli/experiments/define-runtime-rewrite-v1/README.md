# Define runtime rewrite — question-cycle slice

This is a parallel candidate, not a replacement of `implementation/define-cli`.
The authored `question-cycle.alch` decides whether one question-cycle command is
accepted and the next lifecycle posture. AlchLang generated the executable
under `generated/`; `runtime.mjs` applies accepted decisions to a small
in-memory state, and `run.mjs` shows the result.

From this directory:

```bash
node run.mjs
node --test test.mjs
```

To regenerate from the repository root, use the local AlchLang compiler with
the `.alch` source and a **new** output directory:

```bash
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js check \
  implementation/define-cli/experiments/define-runtime-rewrite-v1/question-cycle.alch
OUT="$(mktemp -d)/question-cycle"
node language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js build \
  implementation/define-cli/experiments/define-runtime-rewrite-v1/question-cycle.alch --out "$OUT"
```

The `generated/` directory here is the inspectable output of the current
source, not an authority or release artifact. The runner uses the generated
function directly; it does not start the generated HTTP endpoint.

The existing Define runtime already uses eleven compiled AlchLang decisions.
This experiment explores moving a still-handwritten question-cycle decision
out of `src/durable-session-runtime.mjs`; it does not yet integrate with that
runtime. A bounded happy-path sequence is compared with the existing runtime.
Host code still owns command authorization, revision/idempotency,
atomic persistence, evidence, audit, and user interaction. This slice has no
identity provider, durable store, Definition Pack creation, or migration path.

## Open Questions

- Which further state transitions should belong in authored AlchLang?
- What exact parity evidence is required before any integration proposal?
- Which owner-approved migration and rollback policy would govern a later cutover?

Authority effect: none. No adoption, activation, publication, or deployment.
