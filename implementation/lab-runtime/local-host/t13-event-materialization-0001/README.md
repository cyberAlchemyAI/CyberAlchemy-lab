# T13 exact predecessor, inert native materialization

`materialize.py` resolves its checkout root from its own installed path. It
pins the original 88-intent public accounting, reopens and byte-checks all 88
original O06 proposal bodies, the original private candidate native archive,
and an installed native executable with its
installation receipt and byte-identical source executable. It reads the archive
in memory, validates all 176 original native event bodies and their native
zero-digest preimages, and joins every O06 intent to its exact semantic and
governance predecessor tuple. The 88 original streams are distinct and each
has one predecessor at the selected frozen archive.

The code constructs 88 **inert technical successors**. Each keeps its original
semantic reference and candidate-unadmitted/authority-none state, adds a
`fixture:T13:` provenance marker, and sets the new event's predecessor digest
to the original stream head. The selected native Rust executable seals the
drafts. The receipt records every member, predecessor, native event digest,
and exact Rust canonical event-byte SHA-256. Each returned Rust canonical
body also reproduces its native event digest when its digest field is zeroed.
Complete event bodies exist only
inside the process and an owned temporary input file, which is removed on
exit. No append, Decision, owner response, original semantic rewrite, or
repository effect occurs. Earlier receipts are retained as superseded
technical runs; `RESULT-0005.json` is the current result.

This proves native **sealing mechanics and frozen predecessor joins**, not
the 88 original adoption targets. Their required owner Decision provenance
remains unknown. The proposed `fixture:T13:` marker has no selected adoption
meaning; it cannot substitute for an actual D01 Decision, accountable owner,
current T10/T11 scope, or native append authority. The original snapshot is
frozen, so the receipt does not establish a current live predecessor head.
Original T13 completion remains open.

The focused tests exercise all 88 native seals and refuse one changed
predecessor digest, one changed semantic tuple, one changed original intent
pin, one changed original archive-body hash, and a relocated checkout without
its selected inputs, an escaping locator, and a symlinked parent that points
outside the selected checkout while holding matching bytes. All seven pass normally and under
`-O`.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -q test_materialize
PYTHONDONTWRITEBYTECODE=1 python3 -O -B -m unittest -q test_materialize
python3 -B materialize.py --output /absolute/new/task-local/RESULT.json
```
