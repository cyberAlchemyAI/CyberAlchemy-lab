# T11 exact W06 native fixture route

This package extends the T11 local fixture route from one exact member to the six
W06 candidates that share `scope:lab-runtime-local:w06-learning-0002-560605b8`.
The selected T11 matrix remains SHA-pinned and its 230 members remain unchanged.
The scoped reader verifies a short-lived signed fixture grant, exact route,
carrier descriptor, JSON schema, and original body bytes before delivery. The
native adapter accepts only the six exact member/version/carrier/body-digest
tuples. A valid member in any other T11 scope receives an explicit missing
native-consumer refusal.

`build.py` produced an isolated 45-file runtime from the previously tested
one-member fixture runtime. Only `store.py`, `operations.py`, and `profile.json`
changed. The runtime provisions precisely the W06 fixture scope and requires
one original-byte `artifact-instance/admit` target at a time. Its exact-member
guard runs during both prepare and committed replay. `run.py` extracts the
historical D75 source snapshot into this package's task-owned `working/`
directory, copies the pinned runtime there, and uses a disposable signed local
store. It checks prepare, apply, replay, and fresh-process original-byte
readback for every candidate. All temporary source, key, and store contents are
removed at completion. No live `authority/` files are changed.

Cold validation: `python3 -B -m unittest
implementation/lab-runtime/local-host/t11-native-w06-six-0001/test_run.py`
and the same command with `-O -B` each pass five tests. The full native runner
has not yet been executed while the T03 and T16 native workers occupy the WSL
host; run it with `python3 -B
implementation/lab-runtime/local-host/t11-native-w06-six-0001/run.py` after
those workers finish. Its output is an effect receipt only if it exits zero and
all six native operations and cold readback pass.

This is a local fixture effect under ephemeral fixture signatures and a
historical source snapshot. It does not establish original producer execution,
current source/custodian grants, owner admission, or the 224 other native
routes. Original T11 operational completion stays 0/230 until those original
conditions are separately demonstrated. The technical local count remains one
previously demonstrated native member and six additional members pending this
runner's terminal result.
