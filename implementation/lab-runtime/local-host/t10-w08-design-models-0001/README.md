# T10 members 4–13: W08 design model selections

`select_models.py` executes the hash-selected W08 design route and checks the retained result receipt. That route cold-verifies ten exact candidate workflow designs, their original definitions, 139 schema bindings, 13 relation signatures and 28 transition declarations. This selector validates each design route against `design-route.schema.json`, then constructs a separate local GovernedModel, Implementation and `relation.instance-of` TypedRelation for each member. The implementation is the **design reader**, not the workflow engine.

`RESULT.json` contains ten schema-valid local representations. Five tests pass in the normal runner, including an optimized subprocess, source-change refusal, false-executable route refusal and relation misbinding negatives. Reproduce with `python3 -B select_models.py` or `python3 -B -m unittest discover -s . -p 'test*.py' -q` from this directory.

All ten original GovernedModels retain their historical refusal. None of the 28 transitions is executed by this selector, and no workflow, role, permission or owner decision is activated. T10 remains open for other members and native output execution is a separate T31 requirement.
