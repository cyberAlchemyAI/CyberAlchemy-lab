# Inspect the Lab candidate

This local CLI reads three exact saved candidate cuts: engineering, research and product. It verifies original signed transactions before presenting results. Inspection creates an owned temporary read copy and removes it when done. The output is private candidate evidence.

## Start here

```bash
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py status
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py definitions --limit 20
```

Each answer starts with the selected source, scope, source digest, signed HEAD and currentness. Definitions have independent effective admission and authored lifecycle labels. A candidate directory or version suffix does not establish unadmitted status.

Use `definitions --state admitted-historical` for previous revisions, or `definitions --state candidate-unadmitted` for the selected cut's unadmitted entries. This cut currently contains 183 current and six historical admitted Definition revisions; external candidate queues are outside its coverage. An empty unadmitted page does not prove that the whole repository has no proposals.

## Inspect exact content and authority

```bash
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py inspect cal.definition.artifact-surface-classification@1.0.0-candidate.2
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py inspect cal.definition.artifact-surface-classification@1.0.0-candidate.1
```

An exact revision selects its source binding, parsed content, contract, effective admission, recorded residue and Decision evidence. Multiple revisions require an exact `version_ref`; the CLI does not silently select one. `--without-body` omits content. Missing implementation, runtime or outcome evidence remains null.

## Trace the Project and Product

```bash
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py connections project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py --source product inspect product:cyberalchemy-lab@2.0.0-foundation.1
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py --source product connections product:cyberalchemy-lab@2.0.0-foundation.1
```

Connections retain their declared direction, exact revisions, qualifiers, carrier kinds and endpoint interpretations. Historical endpoints are validated only for inspection of existing connections. Unresolved connections carry an explicit gap. A connection grants no action permission.

## Understand a review and its result

```bash
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py review
python3 product/lab/release-candidates/v1/interface/inspection/lab_operator.py receipt
```

The review shows the saved targets before their isolated local application: exact before/after bindings, structural diff, independent Decision cores and declared effects. The receipt explains the original source, proposal, Decision cores, verified local signature, consequences and selected signed HEAD. Original file hashes, canonical record encoding hashes and structural digests are reported separately.

These are recorded candidate episodes. Final S02 review assembly and actual R08 owner judgment remain pending.

## Structured output and limits

Put `--json` before the command for the exact structured report. Definitions support `--offset` and `--limit`; the response supplies `next_offset` and the exact source cut. Reuse that cut only after checking currentness. This offset is a CLI page selector, not the proposed API's authenticated cursor.

The CLI buffers output up to its bounded ceiling and rejects an oversized report without emitting a partial body. Default output ceiling is 1 MiB; `--max-output-bytes` selects 4 KiB through 4 MiB. Invalid source selection, substituted pins, malformed original archives and ambiguous/unknown revisions fail without executing a transaction.

## Remaining product work

This step implements six operator read commands. The 34 proposed API operations, authenticated stdio adapter, SQLite query parity, complete Session/Agent continuity journey and human owner value pilot remain unfinished. CLI evidence does not satisfy those requirements. R03 stays in progress.
