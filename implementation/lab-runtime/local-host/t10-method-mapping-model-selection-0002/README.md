# T10 member 2: local Method mapping model

`select_model.py` checks the exact original member-2 GovernedModel, refusal, review choice, target/evidence bytes, and prepared postimage. The original has empty `relation_refs` and remains refused. The selector constructs a separate local candidate GovernedModel, Implementation, and `relation.instance-of` TypedRelation. Each validates against the pinned schema, and the relation binds the exact consumer bytes. This v2 candidate pins relation identity, reciprocal links, endpoint versions, qualifier, owner/scope, evidence, lifecycle and implementation kind after an independent v1 review found schema-valid substitutions that were accepted.

The isolated consumer executes captured, hash-verified `consumer.py` bytes. It validates the bootstrap package's candidate Method record against the original Method/v1 proposal schema. The bootstrap schema bytes must match the proposal schema exactly. It then checks that the C09 package manifest and receipt pin that record and schema, and that the retained C09 joined-inspection catalog contains the exact record, carrier digest, `/method_id`, candidate version, and unadmitted state. The receipt also pins the retained inspection result. This is a cold validation of an actual historical producer/consumer join; C09 is not rerun here.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t10-method-mapping-model-selection-0002/select_model.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-method-mapping-model-selection-0002 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-method-mapping-model-selection-0002 -p 'test*.py' -q
```

The 18 focused tests cover the positive join, source pins, captured-buffer execution, selector, Method schema and identity, manifest and receipt pins, catalog kind/version/record/admission posture, relation endpoints and direction, model contract, false authority, and eight schema-valid relation/classification mutations. The result establishes one exact local candidate mapping only. It does not establish a general Method alias, owner meaning, original admission, or T10 completion.
