# T10 local W08 workflow-design routes

`route.py` cold-replays the reviewed 29-row semantic matrix and constructs ten
read-only routes for members 04–13, the W08 workflow transition designs. Each
route checks the original refused GovernedModel body and disposition, exact
review-choice bytes, W08 postimage and its selected parent, original workflow
definition, all 139 input/output schema bindings and 13 closed relation
signatures. It preserves the original 28 ordered transitions and does not
invent a relation or turn a transition design into an admitted Workflow.

For members 06 (engineering) and 12 (research), the route additionally runs
the pinned T31-0001 and T31-0002 cold producer/consumer verifiers. Their four
distinct observed output transitions have exact original candidate output
bytes and later consumers. Two transitions in those workflows and all 22
transitions in the other eight W08 workflows remain unobserved here. These
candidate runs are separate from current signed native Source8 output
journaling and from original T10 semantic selection.

The retained `RESULT-0002.json` is the selected technical receipt; it also
binds this route source and the exact T31 verifier/producer code. The earlier
`RESULT.json` is a superseded local precursor, retained for byte history.
The selected receipt reports ten design
routes, two members with isolated original candidate run evidence, four
observed transitions, zero selected GovernedModel representations, no
authority effect and `T10_complete: false`. It changes no original model,
authority, W08 or T31 file. The other 19 T10 members and native semantic
selection remain open.

From the repository root:

```bash
python3 -B implementation/lab-runtime/local-host/t10-workflow-route-0001/route.py --verify
python3 -B implementation/lab-runtime/local-host/t10-workflow-route-0001/test_route.py
python3 -O -B implementation/lab-runtime/local-host/t10-workflow-route-0001/test_route.py
```

The nine focused tests cover exact replay, ten-design/28-transition closure,
changed original bytes, wrong member kind, reversed transition direction,
wrong output kind, wrong relation counterpart, changed actual producer output,
and a symlinked selected parent.
