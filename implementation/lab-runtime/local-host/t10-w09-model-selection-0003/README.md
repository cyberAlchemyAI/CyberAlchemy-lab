# T10 member 28: local W09 evidence model

`select_model.py` executes the hash-selected W09 retained-evidence route, which cold joins the exact Engineering, Research and Learning case bodies to the audit and later review selection. The output schema requires Engineering `FLAG`, Research `FLAG`, and Learning `PASS`. It then validates a distinct local Model, Implementation and `relation.instance-of` TypedRelation against the pinned authority schemas and kind endpoint rule. The implementation's declared output schema is itself validated against the route result.

`RESULT.json` records the corrected v3 local representation and its selected source bytes. Six focused tests pass, including the `-O` execution, source change, incorrect relation/contract, suppressed counterevidence and seven schema-valid relation/identity misbindings found by independent review. Reproduce with `python3 -B select_model.py` from this directory or run `python3 -B -m unittest discover -s . -p 'test*.py' -q`.

The original member 28 remains refused. This is a local classification of retained evidence; it does not rerun W09, grant Lesson permission, decide an owner outcome, or finish the other T10 members.
