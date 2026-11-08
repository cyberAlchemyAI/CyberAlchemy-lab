# T10 member 21: local three-lens query-contract model

`select_model.py` checks the exact original member-21 GovernedModel, refusal, choice, four target files, six evidence files, and two prepared postimages. The original GovernedModel has empty `relation_refs` and remains refused. The selected local candidate is a separate schema-valid GovernedModel, Implementation and `relation.instance-of` TypedRelation. The Implementation points to the real `t10-query-residue-route-0001/route.py` consumer, and the relation binds its pinned executable bytes to this exact local model.

The consumer runs in an isolated Python child from its captured, hash-verified bytes and recomputes five producer-to-consumer query links over distinct historical D73, current D75 and native O05 source cuts. The recomputed links are compared with the retained receipt. A second isolated child executes the captured byte-backed O03 verifier and runner to cold-validate two retained current/historical answer receipts. This verifier does not call the O03 query engine's `execute()` method. The local model represents the exact query-contract consumer and its request/response schemas; it does not change the original member, admit any artifact, grant authority, establish whole-repository coverage, or complete T10.

Run:

```sh
python3 -B implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001 -p 'test*.py' -q
```

Twelve tests passed in each mode. Negatives reject changed consumer or cold-result pins, prove captured code buffers rather than path rereads are executed, and reject conflated source cuts, wrong contract and Implementation schema, wrong relation endpoint/qualifier/direction, and false admission. `RESULT-0001-diagnostic.json` retains the initial path-execution receipt, which did not close execution substitution windows. The corrected v2 `RESULT.json` is the candidate receipt. It selects one **local** relation-backed representation for member 21. Alongside four earlier local selections, 24 members still lack a local representation; all 29 historical original bodies remain refused. The [independent review](../working/t10-query-contract-model-selection-independent-review-0001/REVIEW.md) confirmed the narrower cold-validation claim.
