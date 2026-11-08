# Preview consequences of a change

## Purpose

Show when a small graph edit changes many conclusions about existing terms.

## Layer and recognition

Ontology change analysis. conservativity, closure_diff and optional logic/conservativity plan checks.

## Contract and dependencies

Observed: compare closure under a selected rule table and restrict new consequences to existing vocabulary, alongside structural and logical reports.

Observed dependencies: before/after graphs, exact rule table and evidence helpers. Application policy is separate from the report.

## Testing obligations

Add only a domain/range axiom and observe new types; no-change control; unsupported rule; timeout; stale reviewed base.

## Observable evidence

New consequences, profile and omissions, structural changes, logical unknowns and risk reasons as separate fields.

## Source and limits

[consequence-change analysis](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/conservativity.rs#L1); [plan application](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L571).

The upstream report is relative to its rule table. Its apply path does not reject an intervening base change or enforce every risk warning.
