# T10 local 29-member mapping aggregate

`CATALOG.json` selects 14 disjoint local candidate packages over all 29 original T10 member indices. `aggregate.py` rechecks the frozen original matrix, reads each selected runner and result at its exact SHA-256, executes the captured runner bytes in an isolated Python child, and requires byte-for-byte agreement with the retained result. It checks unique indices and model identities, schema-valid candidate document kinds, zero authority effect, and zero original admissions. The individual package tests and independent reviews provide the deeper source, schema, relation, and behavior checks; this aggregate verifies that the package results compose without omissions or duplicate members.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t10-all29-aggregate-0001/aggregate.py > /tmp/t10-all29-result.json
cmp /tmp/t10-all29-result.json implementation/lab-runtime/local-host/t10-all29-aggregate-0001/RESULT.json
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-all29-aggregate-0001 -p 'test_aggregate.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-all29-aggregate-0001 -p 'test_aggregate.py' -q
```

The local engineering mapping covers all 29 indices. The original GovernedModel bodies remain refused and unadmitted. This package does not assign owner meaning, run private source effects, or establish original T10 admission.
