# T20 selected public Machine-reply privacy check

`scan.py` cold-pins the local T05 result, all seven actual retained public Machine observation files, and the established T20 public-byte scanner. It checks 540,382 selected bytes for populated credential-like fields, authorization schemes, key blocks, secret assignments and owned private locators. It joins each observation request hash to the public reply binding and each reply profile to the exact pinned API33 profile, then verifies the named operation, test origin and bounded claim. The [result](RESULT.json) is `PASS-BOUNDED` for these recognizable classes. Eight normal and eight optimized tests pass, including synthetic alternate credential key, private key, locator, Bearer, request-digest and profile-digest negatives. The initial independent review found that the request/profile joins were absent; this revision adds them.

This is the exact T05 API33 output cut. It does not inspect transient private Session state, arbitrary encoded secrets, protected Source8 originals or the later final shared family; T20 remains open. No private input body is copied into this package.

From the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t20-seven-machine-replies-0001/scan.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t20-seven-machine-replies-0001 -p 'test*.py' -q
```
