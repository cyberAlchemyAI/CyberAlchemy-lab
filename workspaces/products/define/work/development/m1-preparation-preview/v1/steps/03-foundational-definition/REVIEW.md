# Step 3 — foundational Definition

`cal.definition.definition@1.0.0-candidate.3` — proposed successor; admission pending.

## Governing meaning

A Definition is a versioned, owner-scoped semantic artifact that assigns a term one normative meaning within an exact authority scope. It is structurally complete only when stable identity, applicability, exclusions, a scientific/formal normative voice, explicitly non-normative plain-language and domain-context voices, boundaries, admitted source posture, primary consumers, a synchronized registry postimage, generated index, and a current drift route are declared. Only an exact owner promotion decision can make one exact Definition version canonical authority.

The admitted normative statement and formal expression are preserved exactly. The revised verification condition requires the exact applicable Definition carrier and evaluation profile, with explicit version and compatibility dispositions. The old condition required Definition/v1 specifically. Definition/v2 is already an admitted carrier, while its compatible evaluation/lifecycle successor package remains pending.

## A real repository candidate, applied to the same incident

The [complete example Definition](EXAMPLE-DEFINITION.md) is generated from a byte-for-byte copy of the existing [machine candidate](example-definition.json). It is an actual repository record for **Export identifier completeness**; INC-1042 and its counts remain illustrative.

### Scientific/formal voice

For a fixed source snapshot S, declared account A, declared filters F and saved output E, export identifier completeness holds exactly when every identifier required by S, A and F appears in E.

```text
CompleteIds(S,A,F,E) iff RequiredIds(S,A,F) subseteq ExportedIds(E).
```

S identifies the fixed source snapshot; A the account; F the filters; E the saved export. RequiredIds is the established required population. ExportedIds is the set present in the output. The predicate checks inclusion of all required IDs; it does not exclude extra records.

### Plain-language voice

Every required row identifier for the chosen account, filters and snapshot must appear in the saved output.

### Domain-context voice

The agent investigates INC-1042 using saved S-1042, the Northstar account, status=active filters and E-1042. The synthetic missing-ID case has 12,000 required identifiers and 11,800 unique exported identifiers, leaving 200 missing. This applies the proposed criterion and does not establish an actual production finding.

These voices explain one meaning. The explanations cannot add accuracy, account exclusivity or permission requirements to the governing criterion.

## What turns the statement into a reviewable Lab record

| Part | What it contributes |
| --- | --- |
| Stable identity and version | Names the exact proposed meaning. |
| Scope and boundaries | Declares fixed S/A/F/E and exclusions. |
| Three aligned voices | Governing meaning plus readable and domain explanations. |
| Owner and sources | Declares accountability and exact supporting authority standing. |
| Carrier and projection | Binds exact Definition/v2 schema and generator; JSON is canonical. |
| Consumers, registry/index and drift route | Makes use, discovery and future challenges explicit. |
| Evidence and open obligations | Shows what is supported and what still blocks admission. |

For the fixture's Northstar account, status=active filter, S-1042 and E-1042, 12,000 required IDs and 11,800 matched required IDs imply 200 are missing. That would fail the proposed coverage predicate. It does not mean the Definition artifact is malformed. Conversely, a schema-valid Definition does not establish that the export passed or that the owner admitted the meaning.

## Compatibility still required before admission

- Preserve exact admitted predecessor bytes and current lookup.
- Prepare applicable v2 evaluation/lifecycle profiles and current consumer dispositions.
- Resolve two historical embedded references: governed-by currently does not permit a Definition-to-Role pair, and originates-from needs a resolved Source endpoint rather than an inferred Source Admission-to-Source conversion. Neither is silently copied into a new global connection.
- Prepare exact registry/index/drift postimages, formal distinction evidence and owner fidelity review.

## Review materials

- [Complete revised foundational Definition](DEFINITION.md)
- [Machine candidate](definition.json)
- [Interpretation](interpretation.json)
- [Compatibility and historical connection dispositions](compatibility-review.json)
- [Source capture](source-selection.json)
- [Distinction review](distinction-review.json)
- [Example walkthrough](example-walkthrough.json)
- [Structural checks](review-checks.json)
- [Review queue](../../DEFINITIONS-INDEX.md)

The three sequential meanings are now presented for review. Their admission remains pending. Next is source disposition and the exact Definition/v2 evaluation/lifecycle preparation, followed by the working M1 exporter/preview.
