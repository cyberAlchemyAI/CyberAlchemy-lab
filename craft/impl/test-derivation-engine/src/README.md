# How the derivation engine reads a DomainSpec

This folder turns a DomainSpec feature into a stable list of things that must be
checked.

In plain English:

```text
SPEC.md
  -> read the declarations
  -> organize them into a simple internal model
  -> create one check obligation for each supported declaration
  -> record what was kept, omitted, rejected, or added
```

It does not generate an application. It makes the specification inspectable and
gives later generators and test tools a precise checklist.

## What changed

The engine previously understood the older collection of aspect documents, such
as `states.md` and `operations.md`. A current DomainSpec feature can instead be
written as one normalized `SPEC.md`. The validator could read that newer form,
but the derivation engine could not, so a valid current feature produced no
obligations.

The new adapter closes that gap. It reads explicitly declared concepts,
relationships, fields, attributes, and omissions from `SPEC.md`. It does not
guess missing behavior from prose.

For the agent-execution-orchestrator feature, this produces 39 obligations:

- 13 concepts
- 9 relationships
- 6 fields
- 11 attributes

The three explicitly omitted source relationships are recorded in the receipt,
but they do not become target obligations.

## The important files

### `grammar/index.ts`

This is the reader. It recognizes the supported Markdown tables and converts
each row into a small internal record.

It also rejects important malformed inputs, such as missing required tables or a
relationship that points to an undeclared concept. This prevents an empty or
broken spec from looking successful.

### `ir/types.ts`

This defines the common vocabulary used inside the engine: declarations,
relationships, and obligations. It is the stable handoff between reading a spec
and deriving checks from it.

### `rules/index.ts`

This turns supported declarations into obligations. An obligation says that the
eventual implementation or test harness must account for a declared item.

These are structural obligations. For example, the engine can require that a
declared field be accounted for, but it cannot yet decide whether the field has
the correct business meaning.

### `keys/index.ts` and `identity/human-id.ts`

These give obligations stable machine and human identifiers. Unchanged
declarations keep their identity across repeated runs, which makes diffs and
refinements easier to inspect.

### `residue/receipt.ts`

This creates a machine-readable boundary receipt. It keeps separate lists for:

- declarations present in the target spec;
- relationships backed by explicit source evidence;
- source relationships explicitly omitted from the target;
- structures rejected by the parser; and
- choices added later by implementation bindings.

Here, residue means the visible difference around a translation boundary. It
can be something omitted, something rejected, or a new commitment added by the
next stage. The receipt records these differences; it does not judge whether
they are semantically correct.

### `provenance/index.ts`

This records exactly which input files produced an output. For a normalized
feature, `SPEC.md` is hashed as the input. This lets us detect when the source has
changed and prevents generated evidence from silently referring to an older
specification.

### `emit/spec.ts`

This renders obligations into the generated test specification and coverage
report. It labels normalized declarations as needing an implementation-specific
harness before they can become meaningful runnable tests.

### `cli.ts`

This is the command-line entry point. The two relevant commands are:

```bash
pnpm exec tsx src/cli.ts derive <feature-directory>
pnpm exec tsx src/cli.ts receipt <feature-directory>
```

Add `--out` to write the result beside the feature instead of printing it.

### `grammar/normalized-spec.test.ts`

This is the executable evidence for the adapter. It checks the exact AEO counts,
repeatability, malformed inputs, provenance, receipt separation, and a small
refinement example where adding one field preserves every old obligation and
adds exactly one new obligation.

## What this implies for DomainSpec

DomainSpec now has a working bridge from its current normalized specification
format into deterministic verification work. A specification is no longer only
validated as well-formed; its declared structure can be counted, tracked,
compared between versions, and handed to later testing or generation stages.

This gives us a practical foundation for refinement: when a supported
declaration is added, we can observe the corresponding new obligation without
losing the old ones.

It does **not** yet establish semantic refinement. DomainSpec still needs a clear
definition of a valid implementation before it can say that one spec preserves
the meaning of another, or that generated software truly satisfies the spec.
