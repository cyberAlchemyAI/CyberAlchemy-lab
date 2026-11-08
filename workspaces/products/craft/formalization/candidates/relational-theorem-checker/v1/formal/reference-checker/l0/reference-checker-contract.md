# Pure reference checker

`checkInstance` reflects four independent, constructively decidable propositions into Booleans. `checkGraph` checks the input inventories, every assertion and unique assertion IDs. `checkAddition` checks the entire graph after appending an assertion. All functions are total over arbitrary finite typed inputs and use the standard library only.

Reflection through `decide` is an implementation technique, not the meaning of validity: the propositions already exist in a separate predecessor module. P05 proves the bridges to those propositions, completeness and admission-root preservation. No Boolean is assumed as an external premise to define the intended invariant.

The reference procedure may perform nested linear scans and duplicate checks; no production performance or host parser correctness is claimed. Empty/extra field objects and unknown kind strings belong to the future decoder contract. The Lean domain cannot represent such values. Kind/qualifier mismatches, unresolved/stale references, false or misbound assessments, phantom pairs, empty strings, duplicate identities and invalid old graphs are representable and are tested here.
