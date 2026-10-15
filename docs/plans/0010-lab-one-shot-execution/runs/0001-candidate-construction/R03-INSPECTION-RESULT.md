# R03 operator inspection: current result

Status: **PASS for this scoped CLI step; R03 remains in progress**. Full plan: **28/46 criteria closed**. Actual R08 owner outcome: absent.

## Try the interface

From the repository root:

```bash
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py status
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py definitions --limit 20
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py inspect cal.definition.artifact-surface-classification@1.0.0-candidate.2
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py review
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py receipt
```

The selected private signed cut contains **183 current and six historical admitted Definition revisions**. The CLI shows effective admission separately from authored lifecycle, implementation, runtime observation and outcome. A `candidate` version suffix or directory does not make a record unadmitted. An empty unadmitted selection reports its selected-cut coverage; external candidate queues remain outside it.

Six commands now work: status, Definitions, exact revision inspection, typed connections, recorded review and receipt. Every response shows scope, original source cut, signed HEAD and currentness. Ambiguous identities require an exact revision. Existing historical connections remain inspectable through an explicit historical read path; unresolved connections carry a gap. Connections grant no action permission.

Review shows exact before/after bindings, structural changes, independent Decision cores and local effects before the recorded application. Receipt shows the original proposal, Decision cores, verified signature, deterministic consequences and selected signed chain. Original transaction file SHA, encoded record byte SHA and compact structural digest remain distinct. Same-body revisions can have an empty structural diff while retaining distinct source/revision bindings.

## What was verified

The complete **49-check suite passed**. It includes fresh-process CLI behavior, exact source content, status separation, source/engine pins, unknown and ambiguous revisions, output ceilings without partial bodies, preserved historical connections, explicit unresolved connections, changed/missing-source currentness, unchanged read copies and cleanup.

Twelve independent CLI executions retained original structured output and readable explanations. They cover status, current/historical/unadmitted Definition selections, two exact Definition revisions, Project/Product content and connections, recorded review and receipt. All six closed CLI report branches validate against the new candidate report schema. The proof compares Definition lists against the independently captured canonical registry and compares review/receipt content directly with original signed transaction bytes.

[Exact receipt](../../../../../product/lab/release-candidates/v1/interface/inspection/receipts/R03-0002.json) pins **1,416 files**, including the previous signed coupling proof. Total measured time for the twelve executions was about **102 seconds** in this environment; no SLA is established. Inspection applied no transaction, reexecuted no original domain case, exported no key/Session memory and changed no original/canonical source file.

Initial CLI import failed because `operator.py` shadowed Python's standard module; the entrypoint was renamed. The first suite found record encoding/structural hash confusion, a missing explicit historical-read flag and a wrong test selector for Decision cores. Original failed observations and source snapshots remain retained. The complete corrected successor suite passed.

## Work still required

This step supplies a usable bounded read interface, with technical examples. It implements **zero of the 34 proposed API handlers**. Actual authenticated API/stdio, all exact request/result/error contracts, required SQLite/query parity and the remaining catalog/candidate queue joins stay in scope.

Some canonical Decision references are reference-only in this selected source cut. The CLI states that gap; complete authority evidence and external candidate coverage must be integrated. Project State, Context/Ontology Views, Sessions, failures, lessons and later outcomes still need the complete third owner journey.

W07 integration, remaining roadmap tasks, S02 final review closure, actual human owner pilot and the exact R08 owner response remain pending. These twelve Agent-executed examples prove technical behavior; they do not prove human usefulness or admitted operation.

See [CLI guide](../../../../../product/lab/release-candidates/v1/interface/inspection/README.md), [saved examples](../../../../../product/lab/release-candidates/v1/examples/operator-journeys/inspection/0001/execution.json), [active task board](WORK-PACK.md) and [previous signed coupling result](R03-COUPLING-RESULT.md).
