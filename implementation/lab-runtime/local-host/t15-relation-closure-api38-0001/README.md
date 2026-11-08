# API38 fixture relation closure supplement

An independent review of the 20 inherited method edits found that two changed tests filter by membership in ten expected relation versions. That can ignore an additional same-family relation. `closure.py` therefore rechecks the frozen API38 AST/source inventory, pins the selected fixture mapping and relation constant bytes, and requires the mapping's full same-family relation set to equal the ten expected versions with the typed-relation/v3 carrier. Four normal and optimized tests pass, including extra-relation, missing-relation and wrong-carrier negatives.

This closes the **static fixture mapping** gap only. It does not execute `model.connections`, inspect native relation bodies, or qualify T16/T17. The final selected cut needs an equivalent exact closure assertion over actual runtime connections.

Run `python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t15-relation-closure-api38-0001 -p 'test_closure.py' -q` and repeat with `python3 -O -B`.
