# T10 members 24–26: local source-retention models

`select_models.py` executes the hash-selected, reviewed O05→O06 source-retention route and checks its retained result receipt. That route cold-reads the selected original bodies and refusals, verifies all 140 source dispositions against the O05 core, pins the native archive digest and manifest, and checks the later private-use proposal. The owner and access authority remain unverified. Body import, semantic admission, execution, public export, service activation, source retirement and use of secrets or Session memory remain denied.

This v2 package validates the route summary against `source-route.schema.json` and builds three **distinct local candidate** GovernedModel–Implementation–`relation.instance-of` TypedRelation classifications: source dispositions, private metadata use, and original native archive retention. Each Implementation points to the same executable cold route but has its own original contract/evidence and relation qualifier. The selector checks the exact implementation kind and the TypedRelation's empty reciprocal relation list. The three original GovernedModels retain empty `relation_refs` and remain refused.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t10-source-retention-models-0002/select_models.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-source-retention-models-0002 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-source-retention-models-0002 -p 'test*.py' -q
```

The focused tests cover the three positive classifications, changed executable and receipt pins, changed original refusal or owner outcome, matching-receipt attempts to permit public export or archive replay, wrong archive and disposition bindings, direct private-use denial mutations, relation misbindings, schema-valid wrong implementation kind and extra TypedRelation link, false authority and optimized output. The result does not replay or expose archive content, grant private use, apply source effects, admit original models or complete T10.
