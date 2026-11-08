# T15 API39 inherited-method equivalence

`verify.py` pins the API38 and API39 source manifests and linked profile files, rehashes all 207 source rows in each cut, rejects unlisted Python files, and compares the AST of every inherited test method. `RESULT.json` records **345 methods in each cut, with zero missing, added or changed AST bodies**. The reviewed API38 inventory already connected its 345 methods to the original API v96's 323 methods; this successor check shows API39 did not change that test surface.

Reproduce from the repository root with `python3 -B implementation/lab-runtime/local-host/t15-api39-method-equivalence-0001/verify.py` and compare its bytes to `RESULT.json`. Three focused tests pass normally and with `python3 -O -B`; they cover the exact current selection, detectable method-body change, duplicate method and linked parent refusal.

This is a static method and selected-source check. It does not execute any inherited method, check the API40 composite caller or dependency closure, resolve the remaining 20 changed methods relative to the original API v96, or complete T15/T16.
