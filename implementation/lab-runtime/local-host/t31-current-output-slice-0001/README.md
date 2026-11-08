# T31 current signed Source output slice

`run.py` executed one custom, local output-bearing WorkflowRun transition on the
current signed Source fixture. It used the original workflow kernel and durable
output journal. The producer inspected the selected current Source view, emitted
a schema-valid `generated-output/v2` body and a digest-bound report, and the
later consumer parsed both bodies and independently recomputed the current
subject list. The journal replayed sequence 1 with the exact output ArtifactRef
bound to its event. Changing the output header was refused before application;
changing the report was refused by the later consumer without a second effect.

The [run receipt](RUN-0001.json) records source, event, transaction, next Run,
output body, report, and consumer SHA-256 digests. Its SHA-256 is
`cf0205f4414cbc0d9d0572dfe1b08361feef7e8eb394d27e020bdb6e905ef773`.
`verify.py` checks its exact bounded claim and the executed code digests. Three
focused tests pass under normal and optimized Python, including altered body,
report, source binding, and false original-transition credit.

This is a custom local current-source inspection transition. It does **not**
execute the selected API49 `workflow.transition` route or any of the 28 original
W08 output transitions. The original cumulative count remains 4/28. The
disposable private workspace was removed after the run, so the receipt/code
check cannot independently replay its journal or output bytes. It proves no
Work satisfaction, admission, owner outcome, or full T31 completion.
