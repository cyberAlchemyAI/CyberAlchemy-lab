# Current Source8 API30 successor

`prepare_successor.py` creates the disjoint `api-integration-v33-current-0001`
package from frozen API30 only after one native Source8 family has completed
source, cold replay, Reader, Mapper, and Context phases. It reads the new
manifests, current period, and Reader implementation binding, then replaces the
old legacy and optimized fixture selections with exact current pins. The
historical API30 files and prior expired-period chain stay intact.

Run:

```sh
python3 -B implementation/lab-runtime/local-host/source8-api30-rebind-0001/prepare_successor.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/source8-api30-rebind-0001 -p 'test_*.py' -q
python3 -B implementation/lab-runtime/local-host/source8-api30-rebind-0001/profile_first_test.py
python3 -B implementation/lab-runtime/local-host/source8-api30-rebind-0001/run_successor.py
```

The builder refuses an incomplete family or an existing successor. The
successor records changed source files in `rebind-receipt.json`; `PREPARED`
means only that exact bindings were generated. The two whole API Session
classes, whole Machine transport class, current Source8 Machine read, and
expired/wrong-origin negatives must pass before it can be called a working
local API30 Source8 integration. Its versioned guard checks the exact current
API and helper bytes, environment, family manifests, and profile on each
read. It explicitly leaves historical input accounting unqualified.

The native Context package's construction delivery has its own historical
expiry. The API issues a fresh bounded Context view under each new test-owned
Reader permission; the package's expired construction receipt is not treated
as a live view or used to infer a new permission. The optional
`--context-path` selector can bind a disjoint Context successor, and its exact
path and bytes are recorded in the generated manifest. The whole-suite runner
requires 99 exact test methods, no skips, a separate current Source8 Machine
read, and unchanged package and harness bytes through completion. It records
case timing and observed lease expiries without private policy contents.
