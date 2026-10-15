# Reference closure candidate review

The existing authorization covers candidate construction and isolated validation.
The final R08 checkpoint remains the owner admission decision. These rules are
scoped to the signed Source8 proposals and do not admit canonical records.

## 1. Expected output and actual output

The revised Work still contains:

```json
{
  "completion_state": "pending",
  "output_refs": ["protocol:R03-fresh-context-delivery"]
}
```

The resolver binds this expected output declaration to the exact
`context-delivery/v1-candidate` protocol schema. Its validation evidence says
`actual_output_asserted: false` and `work_satisfaction_asserted: false`.
The declaration is excluded from the report slot for artifact revisions and
resolved by its separate typed protocol check. An actual delivered Context View
or completed Work needs separate source material and validation.

## 2. Goal scope

Goal/v1 has no `scope_ref` field. The exact current signed Typed Relation supplies
the Project membership proof:

```json
{
  "relation_kind_ref": "relation.member-of",
  "source": {
    "kind": "goal",
    "ref": "goal:R03-current-episode-0005",
    "version_ref": "goal:R03-current-episode-0005@1.0.0-candidate.1"
  },
  "target": {
    "kind": "project",
    "ref": "project:cyberalchemy-v2-to-lab-migration",
    "version_ref": "project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1"
  }
}
```

The contract selects the exact membership artifact header and original byte
hash. A Goal merely being present in this repository does not establish scope.

## 3. Challenge history and resolution

The prospective Challenge revision 2 keeps its exact challenged version:

```json
{
  "subject_ref": "work:R03-current-episode-0005",
  "subject_version_ref": "work:R03-current-episode-0005@1.0.0-candidate.1",
  "response_state": "resolved-for-revision",
  "resolution_decision_ref": "decision:R03-current-episode-0005:contest@1.0.0-candidate.1",
  "residue_refs": []
}
```

Work revision 2 makes revision 1 historical in the prospective projection. The
Challenge can still identify the retained exact version it challenged. This
eligibility applies only to the independently bound Challenge role and grants no
current authority. The existing Typed Relation is not silently replaced with a
connection to a new revision.

The full resolver checks current Contract, challenger, evidence inventory,
Decision, responded predecessor, exact response and declared consequences.
The native schema/core checks, signed gate and original source guards remain
required. Other carriers or proposals cannot select these rules through public
input.

## Current package and evidence

- Candidate implementation: `api-v91` and `challenge-resolution-v6`.
- All 323 inherited test method ASTs are retained unchanged.
- Exact contract/control selection: 37 checks passed.
- Actual positive public episode and additional public refusals have separate
  qualification reports; inspect their recorded results before claiming success.
- API90's actual refusal and its 14 original evidence objects remain preserved.
- Full inherited API, new Agent context, lesson application and whole Lab
  acceptance remain separate unfinished obligations.

The public artifact header also needs a versioned candidate successor to expose
Typed Relation/v4. Its private/native use in this Goal membership proof does not
establish current public inspection coverage.
