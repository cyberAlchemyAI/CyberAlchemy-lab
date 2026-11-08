# T10 members 00–03: bounded local routes

The [RESULT.json](RESULT.json) binds four original refused GovernedModel members, their exact dispositions and review choices, target controls, and constructed unselected postimages. Members 00–02 exercise their proposed identity selectors on SHA-pinned example carriers under the exact target schemas: `project_id`, `product_id`, and `method_id`. This proves those fields can be extracted from those examples. It does not establish that an identity carrier is the governed Project/Product/Method endpoint, or that Method/v1 is admitted.

Member 03 checks the original D75 profile, policy, review and content-manifest byte bindings, the selection row and the constructed candidate model relation. It does not execute `profiles.select()` against current host materials or prove the shared repeatable-operation Implementation is an instance of this D75-specific model. Its relation remains a candidate with no selected representation.

The result reports four bounded technical routes, three validated identity examples, **zero** selected GovernedModel representations, no authority effect, and `T10_complete: false`. The remaining 25 members, endpoint meaning decisions, actual current D75 selection, and final semantic relation classification stay open. Original authority and release-candidate files are unchanged.

From the repository root:

```bash
python3 -B implementation/lab-runtime/local-host/t10-endpoint-control-route-0001/route.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-endpoint-control-route-0001 -p 'test_*.py' -v
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-endpoint-control-route-0001 -p 'test_*.py' -v
```

The six tests cover exact receipt replay, changed original bytes, wrong member kind, wrong selector, invalid carrier and wrong D75 candidate relation.
