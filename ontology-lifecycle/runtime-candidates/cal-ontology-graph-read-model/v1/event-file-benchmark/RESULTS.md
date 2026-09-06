# Generated canonical-format event-file recovery result

Status: **PASS** for two fresh-process attempts in both declared profiles.

The fixture generator created one canonical-format semantic event and one exact
governance event for every governed subject. It independently calculated the
expected source envelope and graph index before the recovery processes read the
files. Compilation and generation were excluded from recovery timing.

| Profile | Subjects | Semantic files | Governance files | Event bytes | Generation |
| --- | ---: | ---: | ---: | ---: | ---: |
| Medium | 5,000 | 5,000 | 5,000 | 13.14 MiB | 0.880 s |
| Large | 50,000 | 50,000 | 50,000 | 131.57 MiB | 9.864 s |

| Profile | Attempt | Load and validate | Calculate and rebuild | Process total | Objective |
| --- | ---: | ---: | ---: | ---: | ---: |
| Medium | 1 | 0.198 s | 0.125 s | 0.345 s | 10.000 s |
| Medium | 2 | 0.205 s | 0.135 s | 0.370 s | 10.000 s |
| Large | 1 | 2.265 s | 1.444 s | 3.886 s | 60.000 s |
| Large | 2 | 1.982 s | 1.381 s | 3.564 s | 60.000 s |

Both attempts in each profile reproduced the same normalized recovery receipt,
source-event-set digest, and rebuilt index digest. Adding leading whitespace to
a semantic event caused the separate integrity control to fail with
`NON_CANONICAL_JSON`.

The first large run exposed a quadratic exact-governance join: graph rebuild
took 118–123 seconds even though event loading took about 3.4 seconds. Replacing
the per-subject full scan with one indexed governance pass reduced the same
50,000-subject profile to 1.37–2.05 seconds for calculation and rebuild. The
failed report remains preserved as historical diagnostic evidence; it is not
part of the current passing epoch.

The source-bound validation receipt is [`validation.json`](validation.json);
its implementation envelope includes the transitive event-store runtime source.
The generated files were temporary and are not CyberAlchemy ontology source
records. A separate resource-bounded experiment establishes synthetic
250,000-subject event-file parity and RSS bounds. This result does not establish
persistence, crash consistency, durability, product approval, ontology
admission, activation, publication, or cutover. The disposable
checkpoint-plus-canonical-tail strategy is measured separately.
