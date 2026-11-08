# API53 v5 cold fixture refusal

Selected inputs: API53 Source manifest SHA-256
`872df282f400a8ee814d1fdb7751aa5074250b3b073c4c63cf16567775ab436c`,
profile SHA-256
`fb8741bc5148f9002281dfd3a251d6b20706752a61efaaadf89e22feccf8213e`,
signed ce4 family. Nine normal and nine optimized focused tests passed.

Command: `TMPDIR=/home/vlad_/projects/CyberAlchemy-lab/.local/t31-api53-source-cold-0005 python3 implementation/lab-runtime/local-host/t31-api53-original-output-0005/cold_prepare.py`.
The task-owned `.local` scratch was mode 0700 on the main filesystem; the
private fixture used `/tmp` explicitly. Both task-owned temporary contents
were removed after the failure.

The ce4 Source replay and private-plan schema material selection passed.
Before the fixture yielded, host `ReaderChannel` refused the signed ce4
Principal at `auth.py:262` with `ValueError: metadata grant cannot claim
original Agent participation or owner authority`. The `context.get` producer
requires that signed Principal through Reader eligibility and the fixed
Assignment owner. The selected workflow producer guard requires the producer
and workflow host Principals to match. No producer dispatch, WorkflowRun
append, or later consumer occurred; original transition count remains 4/28.

No wider exception to the workflow metadata authority rule was made. A
positive same-source route needs an independently signed scoped Principal and
matching participation facts, or a different original output producer that
uses a workflow-local Principal. This receipt proves the current conflict,
not workflow completion.
