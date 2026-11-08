# T15 current API40 inherited-method comparison

`verify.py` rehashes all 207 selected source rows on each of the pinned API38 and API40 cuts, checks profile bindings and the closed top-level Python inventory, then compares the AST of all 345 inherited `test_*` methods. `RESULT.json` records zero missing, added or changed methods. Three focused tests passed in normal and optimized Python, including changed method body, duplicate method and linked-origin refusals.

Run `python3 -B implementation/lab-runtime/local-host/t15-api40-method-equivalence-0001/verify.py` and compare the output byte for byte with `RESULT.json`. This is a source-method equivalence check. Module helpers, fixtures, environment and actual inherited test execution remain separate; `t15_complete` is false.
