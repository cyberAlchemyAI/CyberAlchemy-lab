# T10 member 1: local Product mapping model

`select_model.py` checks the exact original member-1 GovernedModel, refusal, choice, target/evidence bytes and prepared postimages. The original model has empty `relation_refs` and remains refused. It selects a separate **local candidate** GovernedModel, an Implementation for the pinned `consumer.py`, and one `relation.instance-of` TypedRelation with an exact consumer-byte qualifier. This v2 candidate pins relation identity, reciprocal links, endpoint versions, qualifier, owner/scope, evidence, lifecycle and implementation kind after an independent follow-up found schema-valid substitutions accepted by v1.

The consumer runs from captured, hash-verified bytes in an isolated child. It validates the actual candidate reference-slice Product Identity/v2 record against the original member's selected schema; joins its `/product_id`, carrier digest and candidate version to the retained producer pack's `semantic_kind=product` endpoint; checks the retained validation receipt's pack digest and Product row; and keeps the Project identity separate. The producer pack and receipt are cold-checked, not rebuilt or revalidated in this run. This proves one exact candidate reference-slice mapping, not a general Identity-to-Product alias, an owner meaning decision, an admitted instance or T10 completion.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t10-product-mapping-model-selection-0002/select_model.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-product-mapping-model-selection-0002 -p 'test*.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-product-mapping-model-selection-0002 -p 'test*.py' -q
```

The 13 focused tests exercise the positive join, source-pin and captured-buffer substitution, wrong selector, Product identity/kind/version, retained validation digest, relation endpoint/direction, model contract, false authority and eight schema-valid classification substitutions. The selected relation is only a local classification of the executable consumer under the local model; it does not establish instance conformance or authority.
