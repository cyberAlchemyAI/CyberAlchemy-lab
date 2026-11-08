# Product candidate 0006: event-runtime realization

This is the first frozen CyberAlchemy Ontology Product candidate that turns the
admitted cohesive Lab ontology projection into canonical D65 event histories
and calculates its current node, relation, and Context views through the Rust
lifecycle engine.

```text
14 ontology nodes + 15 ontology relations
                    |
                    v
      29 semantic + 29 governance events
                    |
                    v
       canonical D65 EventStore history
                    |
          +---------+----------+
          |                    |
          v                    v
  29 latest snapshots    Context projection
          +---------+----------+
                    |
                    v
        deterministic observation
```

Run the complete Product validation from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  product/products/ontology/v1/candidates/0006-event-runtime-realization/validate.py
```

Run only the validator's five hostile document tests:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  product/products/ontology/v1/candidates/0006-event-runtime-realization/test_validate.py
```

The validator checks every frozen source digest, runs the 15 Rust tests twice,
materializes two independent event trees, reloads one tree, and proves equal
observations and byte-equivalent canonical event files.

The Product candidate is not an active runtime. Product approval, binding
admission, runtime adoption, activation, migration, cutover, publication,
release, and deployment remain separate decisions.
