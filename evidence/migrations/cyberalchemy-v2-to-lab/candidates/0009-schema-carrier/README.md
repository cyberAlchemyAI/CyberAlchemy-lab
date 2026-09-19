# Schema carrier and graph conformance checker

`Declared structure + graph data -> conforms / does not conform`

**Schema** means a declaration of admissible structure: the kinds of thing that can occur, constraints on their fields, available relations and rules for forming those connections. It is separate from any particular instance and explicitly identifies the relative level it constrains.

**Why this matters:** valid fields do not guarantee valid connections. Lab must inspect both without interpreting the data as truth or executing it.

## What works

This first profile supports named kinds, optional per-kind field constraints, string/integer/boolean fields, required fields, closed or open field sets, typed relation endpoints and minimum/maximum connection counts at both endpoints. A schema may define field constraints without relations or connections without field constraints. Values are never coerced between types.

```text
Artifact title is a string -> field constraint satisfied
Artifact has exactly one owner connection -> connection rule satisfied
Valid title + missing owner connection -> does not conform
Owner connection + invalid title -> does not conform
Both valid -> structural conformance only
```

The example declares `artifact` and `owner` kinds. Every present artifact must have exactly one `owned-by` connection to an owner. An owner may have zero or more incoming connections. These are structural labels; a matching graph does not prove the named owner has any authority.

The profile checks all supplied nodes and edges, including isolated nodes and zero-edge multiplicity obligations. It does not impose a global population requirement for a kind unless represented by a connection obligation on a present node. Invalid endpoints cannot satisfy multiplicity minimums.

## Try it

From the Lab root:

```bash
cd evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier
python3 check.py artifact-types/schema/v1/fixtures/valid/schema-record.json examples/conforming.json
python3 check.py artifact-types/schema/v1/fixtures/valid/schema-record.json examples/wrong-field.json
python3 check.py artifact-types/schema/v1/fixtures/valid/schema-record.json examples/missing-connection.json
```

Exit 0 means conformance, exit 1 means the graph fails declared checks, and exit 2 means an invalid schema or malformed input. Without a graph argument, the command validates the schema record only and reports that no graph was assessed. All commands are read-only.

The generated [SCHEMA.md](artifact-types/schema/v1/fixtures/valid/SCHEMA.md) explains the complete example. Schema and occupant levels must be distinct, and the supplied graph must match the selected scope and occupant level.

## Bounds and limitations

The profile permits up to 100 declared kinds, constraint groups, fields per group, relation kinds and connection rules, and checks graphs with up to 10,000 nodes and 20,000 edges. Field constraints cover primitive value types only. Path equations are represented separately and must be empty; a nonempty request is rejected rather than silently ignored. Richer nested constraints, path composition and domain-specific semantics require successor profiles.

Passing is shape evidence only. It does not establish truth, ownership, authority, promotion or runtime behavior. Occupant strings are data, including strings that resemble executable code.

## Verification and migration state

Run `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` from this directory. Verification covers shared Artifact Type mechanics, 18 behavioral tests, eight invalid schema fixtures, independent field/connection demonstrations, source bindings, deterministic regeneration and the complete 195-target reconciliation.

Construction closes over 27 Definition candidates and 25 dependency source sections, with the Schema source selector independently checked. Eight inherited lineage residues and the earlier D53 narrow source binding remain explicit. The preceding Decision candidate is preserved.

| State | Before | After |
| --- | ---: | ---: |
| Current recorded admission | 13 | 13 |
| Constructed candidate | 82 | 83 |
| Scaffold awaiting implementation | 100 | 99 |

[Validation evidence](receipts/validation.json) and [demonstration evidence](receipts/demonstration.json) bind the exact checked material. Revalidation writes fresh candidate-local evidence; create a new review snapshot if an older `manifest.json` no longer matches. The next target in ledger order is `type.schema-change`.

## What a later Product review would accept

`A declared finite-graph schema -> independent field and connection checks -> explicit structural findings`

The reviewable capability is this exact carrier and bounded graph checker. Construction completion does not admit the type or establish broader semantic conformance.

## Open questions

- The Schema owner owns additional field and path-equation profiles.
- The domain owner owns meaning and behavioral interpretation beyond shape.
- Source Definition owners retain inherited lineage residue and the D53 layout issue.
