# T10 members 16, 17, 19 and 20: local O02 native-evidence models

`select_models.py` executes the hash-selected O02 representation/native route and matches its retained receipt. That route cold links the representation profile, exact native and translation source bytes, mapping witnesses, three native node states, one typed relation, checkpoint parity and the later unknown-confidence proposal. The four original GovernedModel bodies remain refused. The selector validates the shared route against `native-route.schema.json` and constructs four **distinct** local Model–Implementation–TypedRelation classifications, each bound to its own original contract and digest.

`RESULT.json` records the four schema-valid local classifications. Six focused tests pass, including optimized execution, original-selection field mutation, inflated native confidence, source change and schema-valid relation misbindings. Reproduce from the repository root with `python3 -B implementation/lab-runtime/local-host/t10-o02-native-models-0001/select_models.py` or `python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-o02-native-models-0001 -p 'test*.py' -q`.

This is a cold read of retained evidence. It does not rebuild or rerun Rust/native code, choose a global edge, raise `not-assessed` confidence, grant authority, admit any original member, or finish T10.
