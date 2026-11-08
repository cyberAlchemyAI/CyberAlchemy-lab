# Interactive Define wizard

This is a derived product and implementation note. The canonical flow is
[`authoring/define-wizard.json`](../authoring/define-wizard.json), and persisted
state follows
[`schemas/authoring-session.schema.json`](../schemas/authoring-session.schema.json).

## Product behavior

Define should ask one concrete question at a time. The current question,
previous questions, answers, decisions, unresolved items, and draft artifacts
remain visible in both CLI and chat. A user can resume with the session ID.

The first wizard covers only S0 through S3:

1. choose the business question and owner;
2. write BusinessMeaning;
3. build the InterpretationModel;
4. draft and review the FormalClaim source.

TDE and EVF run after this authoring boundary. The wizard may show their later
state, but it does not claim their results.

## Why no IPC socket is required for the first version

CLI and chat do not need to talk directly to each other. Both views read and
append to one schema-valid authoring-session JSON document. The document is the
canonical state; CLI and chat are projections of it. This is easier to replay,
review, and resume than an always-running socket process.

IPC may be added later for live notifications or concurrent writers, but only
after there is evidence that file-backed session state is insufficient. Adding
IPC must not change artifact bytes or semantic identity.

## Candidate CLI shape

```text
define formalize start --project projects/auth-foundation
define formalize answer <session-id>
define formalize show <session-id>
define formalize resume <session-id>
define formalize export <session-id>
```

These commands are a product target, not an implemented runtime claim. The
first implementation should use create-only or append-safe writes, validate the
session after each answer, and show the exact artifact changed.
