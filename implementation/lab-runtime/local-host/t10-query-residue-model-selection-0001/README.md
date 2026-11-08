# T10 member 27: local query-residue model

`select_model.py` checks the original member-27 refusal, choice, exact proposal and evidence bindings. It executes the pinned member-21 three-cut query consumer from captured bytes; that consumer cold-recomputes five source-pinned producer/consumer links over retained responses and cold-validates separate O03 answer receipts. This selector then joins all five links one-to-one to the original O06 residue proposal's historical D73, current D75 and native O05 partitions, including exact source-cut digest, response binding, result status and gap count. A duplicated route question cannot hide a missing proposal question. It does not rerun any query engine.

The separate local GovernedModel, Implementation and `relation.instance-of` TypedRelation validate against the selected schemas. The Implementation points to the actual pinned query route and its request/response schemas. This is one candidate representation of retained query-gap evidence. It does not select or admit original member 27, generalize coverage, resolve named gaps, grant authority or complete T10.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t10-query-residue-model-selection-0001/select_model.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-query-residue-model-selection-0001 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-query-residue-model-selection-0001 -p 'test*.py' -q
```

The result records only selected bindings, five joins and candidate documents. No protected query body, owner decision or original authority effect is produced.
