# T25 API45 revision-2 portability preflight

`inventory.py` reconstructs the exact selected API45 revision-2 source manifest and schema execution dependency selection, verifies their bindings to the contract profile, hashes every selected file afresh, and records one row per path in [INVENTORY.json](INVENTORY.json). It records paths, digests, selection reasons, and current byte status; it does not copy file bodies or package authority state.

The selected source manifest has 207 rows. The schema execution selection has 5,043 rows, with no overlap; their union has 5,250 files. All 5,250 files matched their selected digests at this preflight. The schema guard's exact hash union has 5,045 rows because the selection binding and an original schema-input binding add two paths; the original operation catalog is already in the 5,043 selected rows. Those two extra bindings are also cold-hashed. Fifteen top-level guard/schema startup reads outside the 5,250 selected rows are inventoried and hashed separately. The rebind receipt has a preflight snapshot digest, because the selected API checks its fields but does not source-pin its raw bytes. This 15-path list is not a transitive startup closure. The 5,250 union includes 625 absolute host dependencies and 333 live `authority/` paths. These facts make a copied API tree or the earlier fixture ZIP insufficient as an API45 installation package. The 33,434-row contract profile is a broader input freeze. Current matching hashes are a snapshot, not a portability proof.

The inventory classifies by path location, not by a filename substring: `private_content.py` is public selected code, while an explicit `private/` or `secrets/` directory would be flagged. No protected private source or issuer body is copied. Host ABI/loader and fresh credentials remain outside this metadata-only preflight.

Run from repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t25-api45r2-package-preflight-0001/inventory.py > /tmp/api45r2-inventory.json
cmp /tmp/api45r2-inventory.json implementation/lab-runtime/local-host/t25-api45r2-package-preflight-0001/INVENTORY.json
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t25-api45r2-package-preflight-0001 -p 'test*.py' -q
```

This is a dependency inventory and package design input. It makes no installed, portable, protected, or canonical release claim; T25 remains open until a clean-root package actually replays the selected implementation and original member dispositions are resolved.
