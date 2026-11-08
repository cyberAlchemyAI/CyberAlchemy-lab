# T14 local heterogeneous byte-publisher rehearsal

This is a disposable local engineering successor to the selected T14
`mixed-target-publisher-0002` candidate. `source_guard.py` pins its original
publisher, target adapter, seven public example rows, and their original
schema/carrier/fixture bytes. `run.py` adapts the seven different target
families without changing their original bytes, prepares one complete byte
bundle, and invokes the original descriptor-bound `OwnedBytePublisher` in
private owned `/tmp/cal-T14-publisher-*` roots.

The run observes an atomic no-replace technical commit record, whole-body
cold inspection and exact replay. A child process exits immediately after
commit; a separately constructed publisher cold-verifies its stage and
receipt and replays the same bundle. Precommit negatives cover changed plan
bytes, a foreign stage marker, and a preexisting competing receipt. A
deterministic competitor is also inserted after full staging at the original
`linkat` boundary; the competing receipt survives the no-replace refusal and
cold inspection rejects it. A controlled failure after the first fsynced
stage write exercises `recovery.py`: under the same nonblocking exclusive
publisher lock, it deletes only an independently verified, exact owned
partial stage with no commit record. Foreign, changed, locked, or committed
residue remains untouched and is refused.

The original T14 publisher deliberately preserves unknown residue. The
successor rollback adapter is scoped to this disposable private technical
root and known precommit fault. It is not a generic authority recovery tool.
The selected fixtures are public examples, not current protected targets;
there is no native semantic decision, owner outcome, canonical admission,
or authority effect. This rehearsal cannot close T14's original
admission/qualification obligations.

Validation: `python3 -m unittest -v test_recovery`,
`python3 -O -m unittest -q test_recovery`, then `python3 run.py`.
`RESULT-0002.json` is the current live observation; the earlier `RESULT.json`
is preserved as superseded evidence before the lock and at-commit race repair.
