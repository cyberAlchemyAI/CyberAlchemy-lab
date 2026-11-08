# T10 O03 selected-origin isolation successor

This disjoint successor preserves the 0003 byte-backed query loader and adds one lifecycle repair: `selected_modules()` snapshots and restores the full `sys.path` list in `finally`. The selected nested `scope.py` inserts the coupling directory at import time; leaving it behind could let later unrelated imports resolve through that directory. The new test proves exact restoration after both normal exit and an exception.

Actual current-specialist and historical D73 reruns under `secure_query.py` produced [CURRENT-SECURE-RESULT.json](CURRENT-SECURE-RESULT.json) and [HISTORICAL-SECURE-RESULT.json](HISTORICAL-SECURE-RESULT.json), byte-identical to their frozen response digests. [VERIFIED-JOIN.json](VERIFIED-JOIN.json) cold-joins the four answers to the original receipts and pins this successor's code SHA-256 `13f889f60430ebf53818bd9e4648e184dcbb23a2f3456ed01f0af014efa21676`. Eight tests pass in normal and optimized Python. The prior 0003 files remain unchanged.

```sh
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004 -p 'test_secure_query.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004 -p 'test_secure_query.py' -q
python3 -B implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004/verify.py
```

This proves selected executable origin and response equivalence for the two named scopes. It does not select a GovernedModel, grant authority, or qualify the original O05 source archive and external observations.
